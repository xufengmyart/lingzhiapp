#!/bin/bash
# 生产环境自动化测试脚本
# 用于验证所有修复的功能是否正常工作

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
API_BASE="http://localhost:5000"
TEST_USER="prod_test_$(date +%s)"
TEST_EMAIL="${TEST_USER}@example.com"
TEST_PASSWORD="Test123456!"

# 测试结果统计
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 打印函数
print_header() {
    echo -e "\n${YELLOW}========================================${NC}"
    echo -e "${YELLOW}$1${NC}"
    echo -e "${YELLOW}========================================${NC}"
}

print_test() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${YELLOW}[测试 $TOTAL_TESTS]${NC} $1"
}

print_pass() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${GREEN}✅ 通过${NC} $1"
}

print_fail() {
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "${RED}❌ 失败${NC} $1"
}

# 测试1: 用户登录
test_login() {
    print_test "用户登录测试"

    response=$(curl -s -X POST "${API_BASE}/api/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "123"}')

    success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")

    if [ "$success" = "True" ]; then
        TOKEN=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('token', ''))")
        print_pass "登录成功，获取到token"
        return 0
    else
        print_fail "登录失败"
        return 1
    fi
}

# 测试2: Token验证（模拟页面刷新）
test_token_validation() {
    print_test "Token验证测试（模拟页面刷新）"

    if [ -z "$TOKEN" ]; then
        print_fail "Token未获取，无法测试"
        return 1
    fi

    success_count=0
    for i in {1..3}; do
        response=$(curl -s -X GET "${API_BASE}/api/user/info" \
            -H "Authorization: Bearer $TOKEN")
        success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")
        if [ "$success" = "True" ]; then
            success_count=$((success_count + 1))
        fi
    done

    if [ $success_count -eq 3 ]; then
        print_pass "Token验证成功（3/3次请求成功）"
        return 0
    else
        print_fail "Token验证失败（成功${success_count}/3次）"
        return 1
    fi
}

# 测试3: 用户注册
test_register() {
    print_test "用户注册测试"

    response=$(curl -s -X POST "${API_BASE}/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"${TEST_USER}\", \"email\": \"${TEST_EMAIL}\", \"password\": \"${TEST_PASSWORD}\"}")

    success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")

    if [ "$success" = "True" ]; then
        USER_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('userId', 0))")
        print_pass "注册成功，用户ID: ${USER_ID}"
        return 0
    else
        print_fail "注册失败"
        return 1
    fi
}

# 测试4: 测试用户登录
test_new_user_login() {
    print_test "测试用户登录"

    response=$(curl -s -X POST "${API_BASE}/api/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"username\": \"${TEST_USER}\", \"password\": \"${TEST_PASSWORD}\"}")

    success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")

    if [ "$success" = "True" ]; then
        TEST_TOKEN=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('token', ''))")
        TEST_USER_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('user', {}).get('id', 0))")
        print_pass "测试用户登录成功，用户ID: ${TEST_USER_ID}"
        return 0
    else
        print_fail "测试用户登录失败"
        return 1
    fi
}

# 测试5: 更新用户资料（包含user_profiles字段）
test_update_profile() {
    print_test "更新用户资料测试"

    if [ -z "$TEST_TOKEN" ]; then
        print_fail "测试用户Token未获取，无法测试"
        return 1
    fi

    response=$(curl -s -X PUT "${API_BASE}/api/user/profile" \
        -H "Authorization: Bearer ${TEST_TOKEN}" \
        -H "Content-Type: application/json" \
        -d '{
            "idCard": "310101199001011234",
            "bankAccount": "6222021234567890123",
            "bankName": "中国建设银行",
            "realName": "测试用户",
            "phone": "13900139000"
        }')

    success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")

    if [ "$success" = "True" ]; then
        print_pass "用户资料更新成功"
        return 0
    else
        print_fail "用户资料更新失败"
        return 1
    fi
}

# 测试6: 数据库验证（user_profiles表）
test_database_profiles() {
    print_test "数据库验证（user_profiles表）"

    if [ -z "$TEST_USER_ID" ]; then
        print_fail "测试用户ID未获取，无法测试"
        return 1
    fi

    result=$(cd /workspace/projects/admin-backend && python3 -c "
import sqlite3
conn = sqlite3.connect('data/lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute('SELECT user_id, id_card, bank_account, bank_name FROM user_profiles WHERE user_id = ?', (${TEST_USER_ID},))
row = cursor.fetchone()
conn.close()
if row:
    print(f'{row[0]}|{row[1]}|{row[2]}|{row[3]}')
else:
    print('NOT_FOUND')
")

    if [ "$result" != "NOT_FOUND" ]; then
        print_pass "user_profiles表数据正确"
        return 0
    else
        print_fail "user_profiles表数据不存在"
        return 1
    fi
}

# 测试7: 充值订单创建
test_recharge_order() {
    print_test "充值订单创建测试"

    if [ -z "$TEST_TOKEN" ]; then
        print_fail "测试用户Token未获取，无法测试"
        return 1
    fi

    response=$(curl -s -X POST "${API_BASE}/api/recharge/create-order" \
        -H "Authorization: Bearer ${TEST_TOKEN}" \
        -H "Content-Type: application/json" \
        -d "{
            \"user_id\": ${TEST_USER_ID},
            \"tier_id\": 1,
            \"payment_method\": \"alipay\"
        }")

    success=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('success', False))")

    if [ "$success" = "True" ]; then
        ORDER_NO=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('orderNo', ''))")
        print_pass "充值订单创建成功，订单号: ${ORDER_NO}"
        return 0
    else
        print_fail "充值订单创建失败"
        return 1
    fi
}

# 主测试流程
main() {
    print_header "开始生产环境测试"

    # 检查服务是否运行
    if ! curl -s -f "${API_BASE}/api/health" > /dev/null 2>&1; then
        echo -e "${RED}❌ 错误: 后端服务未运行${NC}"
        echo "请先启动后端服务: cd admin-backend && python3 app.py"
        exit 1
    fi

    # 执行测试
    test_login || true
    test_token_validation || true
    test_register || true
    test_new_user_login || true
    test_update_profile || true
    test_database_profiles || true
    test_recharge_order || true

    # 打印测试结果
    print_header "测试结果汇总"

    echo -e "总测试数: ${TOTAL_TESTS}"
    echo -e "${GREEN}通过: ${PASSED_TESTS}${NC}"
    echo -e "${RED}失败: ${FAILED_TESTS}${NC}"

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "\n${GREEN}🎉 所有测试通过！${NC}"
        exit 0
    else
        echo -e "\n${RED}⚠️  部分测试失败，请检查日志${NC}"
        exit 1
    fi
}

# 运行主函数
main "$@"
