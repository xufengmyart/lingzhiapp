#!/bin/bash
################################################################################
# 部署验证脚本
# 用途: 验证生产环境部署后的功能是否正常
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 加载配置
if [ -f "deploy_config.sh" ]; then
    source deploy_config.sh
else
    PRODUCTION_URL="https://meiyueart.com"
    API_BASE="$PRODUCTION_URL/api"
fi

# 测试计数
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 测试函数
test_start() {
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -e "\n${YELLOW}[测试 $TOTAL_TESTS]${NC} $1"
}

test_pass() {
    PASSED_TESTS=$((PASSED_TESTS + 1))
    echo -e "${GREEN}✅ 通过${NC} $1"
    return 0
}

test_fail() {
    FAILED_TESTS=$((FAILED_TESTS + 1))
    echo -e "${RED}❌ 失败${NC} $1"
    return 1
}

# 测试1: 健康检查
test_health_check() {
    test_start "健康检查API"

    local response=$(curl -sf "$API_BASE/health")

    if [ $? -eq 0 ]; then
        if echo "$response" | grep -q '"status":"healthy"'; then
            test_pass "健康检查正常"
            return 0
        else
            test_fail "健康状态异常"
            echo "$response"
            return 1
        fi
    else
        test_fail "API不可访问"
        return 1
    fi
}

# 测试2: 用户登录
test_user_login() {
    test_start "用户登录"

    local response=$(curl -s -X POST "$API_BASE/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "123"}')

    if echo "$response" | grep -q '"success":true'; then
        TOKEN=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])" 2>/dev/null || echo "")
        USER_ID=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['user']['id'])" 2>/dev/null || echo "")
        test_pass "登录成功"
        return 0
    else
        test_fail "登录失败"
        echo "$response"
        return 1
    fi
}

# 测试3: 用户信息API（验证推荐人字段）
test_user_info() {
    test_start "用户信息API（验证推荐人字段）"

    if [ -z "$TOKEN" ]; then
        test_fail "未获取到Token，跳过测试"
        return 1
    fi

    local response=$(curl -s -X GET "$API_BASE/user/info" \
        -H "Authorization: Bearer $TOKEN")

    if echo "$response" | grep -q '"success":true'; then
        if echo "$response" | grep -q '"referrer"'; then
            test_pass "推荐人字段存在"
            echo "$response" | python3 -m json.tool 2>/dev/null || echo "$response"
            return 0
        else
            test_fail "推荐人字段不存在"
            echo "$response"
            return 1
        fi
    else
        test_fail "API调用失败"
        echo "$response"
        return 1
    fi
}

# 测试4: 密码修改功能
test_change_password() {
    test_start "密码修改功能"

    if [ -z "$TOKEN" ]; then
        test_fail "未获取到Token，跳过测试"
        return 1
    fi

    local response=$(curl -s -X POST "$API_BASE/user/change-password" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"oldPassword": "123", "newPassword": "TempPassword123!"}')

    if echo "$response" | grep -q '"NOT_FOUND"' || echo "$response" | grep -q '"404"'; then
        test_fail "密码修改API不存在"
        echo "$response"
        return 1
    elif echo "$response" | grep -q '"success":true'; then
        test_pass "密码修改功能正常"

        # 恢复原密码
        log_info "恢复原密码..."
        local restore_response=$(curl -s -X POST "$API_BASE/user/change-password" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"oldPassword": "TempPassword123!", "newPassword": "123"}')

        if echo "$restore_response" | grep -q '"success":true'; then
            log_success "密码已恢复"
        else
            log_warning "密码恢复失败，请手动检查"
        fi
        return 0
    else
        test_fail "密码修改失败"
        echo "$response"
        return 1
    fi
}

# 测试5: API响应时间
test_api_response_time() {
    test_start "API响应时间"

    local start_time=$(date +%s%N)
    curl -sf "$API_BASE/health" > /dev/null
    local end_time=$(date +%s%N)

    local duration=$(( (end_time - start_time) / 1000000 ))

    if [ $duration -lt 1000 ]; then
        test_pass "响应时间: ${duration}ms (优秀)"
    elif [ $duration -lt 2000 ]; then
        test_pass "响应时间: ${duration}ms (良好)"
    elif [ $duration -lt 5000 ]; then
        log_warning "响应时间: ${duration}ms (一般)"
        return 0
    else
        test_fail "响应时间: ${duration}ms (缓慢)"
        return 1
    fi
}

# 打印测试摘要
print_summary() {
    echo -e "\n${BLUE}"
    echo "========================================="
    echo "  测试摘要"
    echo "========================================="
    echo -e "${NC}"
    echo "总测试数: $TOTAL_TESTS"
    echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
    echo -e "${RED}失败: $FAILED_TESTS${NC}"
    echo ""

    if [ $FAILED_TESTS -eq 0 ]; then
        echo -e "${GREEN}🎉 所有测试通过！部署成功！${NC}"
        echo ""
        echo "下一步操作:"
        echo "1. 访问 $PRODUCTION_URL 在浏览器中验证前端功能"
        echo "2. 检查应用日志: ssh user@meiyueart.com 'tail -50 /var/log/flask_backend.log'"
        echo "3. 监控API性能和错误率"
        return 0
    else
        echo -e "${RED}⚠️  部分测试失败，请检查并修复${NC}"
        echo ""
        echo "建议操作:"
        echo "1. 查看服务日志"
        echo "2. 检查错误信息"
        echo "3. 如需回滚，查看备份目录"
        return 1
    fi
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "========================================="
    echo "  生产环境部署验证"
    echo "  目标: $PRODUCTION_URL"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================="
    echo -e "${NC}"

    # 执行测试
    test_health_check || true
    test_user_login || true
    test_user_info || true
    test_change_password || true
    test_api_response_time || true

    # 打印摘要
    print_summary
}

# 执行主函数
main "$@"
