#!/bin/bash
# 灵值生态园 API 自动化测试脚本
# API Automation Test Script

set -e

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
BASE_URL="${API_BASE_URL:-https://meiyueart.com}"
API_BASE="$BASE_URL/api"

# 测试统计
TESTS_TOTAL=0
TESTS_PASSED=0
TESTS_FAILED=0

# 日志函数
log_test() { echo -e "${BLUE}[TEST]${NC} $1"; }
log_pass() { echo -e "${GREEN}[PASS]${NC} $1"; ((TESTS_PASSED++)); }
log_fail() { echo -e "${RED}[FAIL]${NC} $1"; ((TESTS_FAILED++)); }
log_info() { echo -e "${YELLOW}[INFO]${NC} $1"; }

# 计数
count_test() { ((TESTS_TOTAL++)); }

# 测试函数
test_api() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local auth="$5"
    local expected="$6"

    count_test
    log_test "Testing: $name"

    local cmd="curl -s -X $method '$API_BASE$endpoint'"
    
    if [ -n "$data" ]; then
        cmd="$cmd -H 'Content-Type: application/json' -d '$data'"
    fi
    
    if [ -n "$auth" ]; then
        cmd="$cmd -H 'Authorization: Bearer $auth'"
    fi

    local response=$(eval $cmd)
    
    if echo "$response" | grep -q "$expected"; then
        log_pass "$name"
        return 0
    else
        log_fail "$name"
        log_info "Expected: $expected"
        log_info "Response: $response"
        return 1
    fi
}

# ==================== 开始测试 ====================

echo ""
echo "========================================="
echo "🧪 灵值生态园 API 自动化测试"
echo "========================================="
echo ""
echo "📊 测试环境:"
echo "  - Base URL: $BASE_URL"
echo "  - API URL: $API_BASE"
echo ""

# ========== 1. 基础测试 ==========
log_info "========== 1. 基础测试 =========="

test_api "健康检查" "GET" "/health" "" "" "success.*true"
test_api "系统状态" "GET" "/status" "" "" "success.*true"

# ========== 2. 认证测试 ==========
log_info ""
log_info "========== 2. 认证测试 =========="

# 管理员登录
ADMIN_TOKEN=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"123"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('token', ''))" 2>/dev/null || echo "")

if [ -n "$ADMIN_TOKEN" ]; then
    log_pass "管理员登录成功"
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
else
    log_fail "管理员登录失败"
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
fi

# 用户登录
USER_TOKEN=$(curl -s -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"username":"马伟娟","password":"123"}' | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('token', ''))" 2>/dev/null || echo "")

if [ -n "$USER_TOKEN" ]; then
    log_pass "用户登录成功"
    ((TESTS_PASSED++))
    ((TESTS_TOTAL++))
else
    log_fail "用户登录失败"
    ((TESTS_FAILED++))
    ((TESTS_TOTAL++))
fi

# ========== 3. 私有资源库测试 ==========
log_info ""
log_info "========== 3. 私有资源库测试 =========="

if [ -n "$ADMIN_TOKEN" ]; then
    test_api "获取资源列表" "GET" "/private-resources" "" "$ADMIN_TOKEN" "success.*true"
    
    # 创建测试资源
    CREATE_RESPONSE=$(curl -s -X POST "$API_BASE/private-resources" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $ADMIN_TOKEN" \
        -d '{
            "resourceName": "自动化测试资源",
            "resourceType": "资金",
            "description": "用于自动化测试的资源",
            "estimatedValue": 50000,
            "contactName": "测试用户",
            "contactPhone": "13900000000",
            "canSolve": "技术支持"
        }')
    
    if echo "$CREATE_RESPONSE" | grep -q "success.*true"; then
        RESOURCE_ID=$(echo "$CREATE_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin).get('data', {}).get('id', 0))" 2>/dev/null || echo "0")
        if [ "$RESOURCE_ID" != "0" ]; then
            log_pass "创建资源成功 (ID: $RESOURCE_ID)"
            ((TESTS_PASSED++))
            ((TESTS_TOTAL++))
            
            # 获取资源详情
            test_api "获取资源详情" "GET" "/private-resources/$RESOURCE_ID" "" "$ADMIN_TOKEN" "success.*true"
            
            # 更新资源
            test_api "更新资源" "PUT" "/private-resources/$RESOURCE_ID" '{"resourceName":"更新后的测试资源"}' "$ADMIN_TOKEN" "success.*true"
        else
            log_fail "创建资源失败，无法获取资源ID"
            ((TESTS_FAILED++))
            ((TESTS_TOTAL++))
        fi
    else
        log_fail "创建资源失败"
        ((TESTS_FAILED++))
        ((TESTS_TOTAL++))
    fi
else
    log_warn "跳过资源库测试（无有效Token）"
fi

# ========== 4. 通知系统测试 ==========
log_info ""
log_info "========== 4. 通知系统测试 =========="

if [ -n "$ADMIN_TOKEN" ]; then
    test_api "获取通知列表" "GET" "/notifications" "" "$ADMIN_TOKEN" "success.*true"
    test_api "获取未读通知数量" "GET" "/notifications/unread-count" "" "$ADMIN_TOKEN" "success.*true"
else
    log_warn "跳过通知系统测试（无有效Token）"
fi

# ========== 5. 报表系统测试 ==========
log_info ""
log_info "========== 5. 报表系统测试 =========="

if [ -n "$ADMIN_TOKEN" ]; then
    test_api "获取仪表盘数据" "GET" "/reports/dashboard" "" "$ADMIN_TOKEN" "success.*true"
    test_api "获取项目统计报表" "GET" "/reports/projects/summary" "" "$ADMIN_TOKEN" "success.*true"
    test_api "获取资源统计报表" "GET" "/reports/resources/summary" "" "$ADMIN_TOKEN" "success.*true"
    test_api "获取分润统计报表" "GET" "/reports/profits/summary" "" "$ADMIN_TOKEN" "success.*true"
else
    log_warn "跳过报表系统测试（无有效Token）"
fi

# ========== 6. 资源匹配测试 ==========
log_info ""
log_info "========== 6. 资源匹配测试 =========="

if [ -n "$ADMIN_TOKEN" ]; then
    test_api "获取匹配列表" "GET" "/resource-matches" "" "$ADMIN_TOKEN" "success.*true"
    test_api "自动匹配资源" "POST" "/resource-matches/auto-match" "" "$ADMIN_TOKEN" "success.*true"
else
    log_warn "跳过资源匹配测试（无有效Token）"
fi

# ========== 7. 项目参与测试 ==========
log_info ""
log_info "========== 7. 项目参与测试 =========="

if [ -n "$ADMIN_TOKEN" ]; then
    test_api "获取参与列表" "GET" "/project-participations" "" "$ADMIN_TOKEN" "success.*true"
else
    log_warn "跳过项目参与测试（无有效Token）"
fi

# ========== 8. 分润管理测试 ==========
log_info ""
log_info "========== 8. 分润管理测试 =========="

if [ -n "$ADMIN_TOKEN" ]; then
    test_api "获取分润列表" "GET" "/profit-sharing" "" "$ADMIN_TOKEN" "success.*true"
else
    log_warn "跳过分润管理测试（无有效Token）"
fi

# ========== 测试结果 ==========
echo ""
echo "========================================="
echo "📊 测试结果统计"
echo "========================================="
echo ""
echo "  总测试数: $TESTS_TOTAL"
echo -e "  ${GREEN}通过: $TESTS_PASSED${NC}"
echo -e "  ${RED}失败: $TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "${RED}❌ 有 $TESTS_FAILED 个测试失败${NC}"
    exit 1
fi
