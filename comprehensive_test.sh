#!/bin/bash
# 全面功能测试脚本

echo "=================================================="
echo "灵值生态园 - 全面功能测试"
echo "=================================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试结果
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# 测试函数
test_api() {
    local name=$1
    local method=$2
    local url=$3
    local data=$4
    local headers=$5
    local expected=$6

    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    echo -n "测试 $name... "

    local response
    if [ -z "$data" ]; then
        response=$(curl -s -X $method "http://127.0.0.1:8080$url" $headers 2>&1)
    else
        response=$(curl -s -X $method "http://127.0.0.1:8080$url" -H "Content-Type: application/json" -d "$data" $headers 2>&1)
    fi

    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✓ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        echo "  预期: $expected"
        echo "  响应: $response"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 测试1: 健康检查
echo -e "${BLUE}[1/10] 基础服务测试${NC}"
test_api "健康检查" "GET" "/api/health" "" "" "ok"

# 测试2: 用户登录
echo ""
echo -e "${BLUE}[2/10] 用户认证测试${NC}"
LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1:8080/api/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin123"}')
if echo "$LOGIN_RESPONSE" | grep -q "success.*true"; then
    echo -e "用户登录... ${GREEN}✓ 通过${NC}"
    PASSED_TESTS=$((PASSED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])" 2>/dev/null)
else
    echo -e "用户登录... ${RED}✗ 失败${NC}"
    FAILED_TESTS=$((FAILED_TESTS + 1))
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
fi

# 测试3: 获取用户信息
if [ -n "$TOKEN" ]; then
    test_api "获取用户信息" "GET" "/api/user/info" "" "-H \"Authorization: Bearer $TOKEN\"" "username"
else
    echo "跳过用户信息测试（未获取到token）"
fi

# 测试4: 签到状态
if [ -n "$TOKEN" ]; then
    test_api "获取签到状态" "GET" "/api/checkin/status" "" "-H \"Authorization: Bearer $TOKEN\"" "success"
else
    echo "跳过签到状态测试（未获取到token）"
fi

# 测试5: 签到
if [ -n "$TOKEN" ]; then
    echo ""
    echo -e "${BLUE}[3/10] 灵值经济测试${NC}"
    test_api "签到功能" "POST" "/api/checkin" "" "-H \"Authorization: Bearer $TOKEN\"" "success"
else
    echo "跳过签到测试（未获取到token）"
fi

# 测试6: 获取充值档位
test_api "获取充值档位" "GET" "/api/recharge/tiers" "" "" "success"

# 测试7: 中视频项目
if [ -n "$TOKEN" ]; then
    echo ""
    echo -e "${BLUE}[4/10] 核心项目测试${NC}"
    test_api "获取中视频项目" "GET" "/api/video/projects" "" "-H \"Authorization: Bearer $TOKEN\"" "success"
else
    echo "跳过中视频项目测试（未获取到token）"
fi

# 测试8: 西安美学侦探
if [ -n "$TOKEN" ]; then
    test_api "获取西安美学侦探项目" "GET" "/api/aesthetic/projects" "" "-H \"Authorization: Bearer $TOKEN\"" "success"
else
    echo "跳过西安美学侦探测试（未获取到token）"
fi

# 测试9: 合伙人项目
if [ -n "$TOKEN" ]; then
    test_api "获取合伙人项目" "GET" "/api/partner/projects" "" "-H \"Authorization: Bearer $TOKEN\"" "success"
else
    echo "跳过合伙人项目测试（未获取到token）"
fi

# 测试10: 智能对话
if [ -n "$TOKEN" ]; then
    echo ""
    echo -e "${BLUE}[5/10] 智能体测试${NC}"
    CHAT_RESPONSE=$(curl -s -X POST http://127.0.0.1:8080/api/chat \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d '{"message":"你好"}')
    if echo "$CHAT_RESPONSE" | grep -q "success\|response\|message"; then
        echo -e "智能对话... ${GREEN}✓ 通过${NC}"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    else
        echo -e "智能对话... ${RED}✗ 失败${NC}"
        FAILED_TESTS=$((FAILED_TESTS + 1))
        TOTAL_TESTS=$((TOTAL_TESTS + 1))
    fi
else
    echo "跳过智能对话测试（未获取到token）"
fi

# 测试结果汇总
echo ""
echo "=================================================="
echo "测试结果汇总"
echo "=================================================="
echo -e "总测试数: $TOTAL_TESTS"
echo -e "通过: ${GREEN}$PASSED_TESTS${NC}"
echo -e "失败: ${RED}$FAILED_TESTS${NC}"
echo ""

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}所有测试通过！✓${NC}"
    exit 0
else
    echo -e "${RED}有 $FAILED_TESTS 个测试失败！✗${NC}"
    exit 1
fi
