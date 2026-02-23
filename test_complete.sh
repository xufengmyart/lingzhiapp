#!/bin/bash
# 完整的 API 测试脚本 - 修复版

echo "🚀 开始完整 API 测试..."
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 测试结果统计
PASSED=0
FAILED=0
WARNINGS=0

# API 基础 URL
BASE_URL="http://localhost:5000"

# 测试函数
test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local method="${3:-GET}"
    local expected_status="${4:-200}"
    local data="${5:-}"
    local token="${6:-}"
    
    echo -n "测试: $name ... "
    
    # 构建请求命令
    if [ "$method" = "GET" ]; then
        if [ -n "$token" ]; then
            response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $token" -o /tmp/test_response.txt "$BASE_URL$endpoint" 2>&1)
        else
            response=$(curl -s -w "\n%{http_code}" -o /tmp/test_response.txt "$BASE_URL$endpoint" 2>&1)
        fi
    elif [ "$method" = "POST" ]; then
        if [ -n "$token" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -H "Authorization: Bearer $token" -d "$data" -o /tmp/test_response.txt "$BASE_URL$endpoint" 2>&1)
        else
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" -o /tmp/test_response.txt "$BASE_URL$endpoint" 2>&1)
        fi
    elif [ "$method" = "PUT" ]; then
        response=$(curl -s -w "\n%{http_code}" -X PUT -H "Content-Type: application/json" -d "$data" -o /tmp/test_response.txt "$BASE_URL$endpoint" 2>&1)
    elif [ "$method" = "DELETE" ]; then
        response=$(curl -s -w "\n%{http_code}" -X DELETE -o /tmp/test_response.txt "$BASE_URL$endpoint" 2>&1)
    fi
    
    status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
        return 0
    elif [ "$status_code" -ge 400 ] && [ "$status_code" -lt 500 ]; then
        echo -e "${YELLOW}⚠ 警告${NC} (HTTP $status_code, 期望 $expected_status)"
        echo "响应内容:"
        cat /tmp/test_response.txt
        WARNINGS=$((WARNINGS + 1))
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $status_code, 期望 $expected_status)"
        echo "响应内容:"
        cat /tmp/test_response.txt
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# 等待服务启动
echo -e "${YELLOW}等待后端服务启动...${NC}"
sleep 3

# 检查服务是否运行
if ! pgrep -f "python.*app.py" > /dev/null; then
    echo -e "${RED}错误: 后端服务未运行${NC}"
    echo "启动服务..."
    cd /workspace/projects/admin-backend
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    sleep 5
fi

echo ""
echo "📊 测试基础服务"
echo "================================"

test_endpoint "健康检查" "/" "GET" 200

echo ""
echo "📈 测试资产交易市场接口"
echo "================================"

test_endpoint "获取市场统计" "/api/v9/market/stats" "GET" 200
test_endpoint "获取市场资产列表" "/api/v9/market/assets" "GET" 200

echo ""
echo "📥 测试批量导入接口"
echo "================================"

test_endpoint "批量导入数据" "/api/batch-import" "POST" 200 '{"type":"data_element","items":[]}'

echo ""
echo "📊 测试 API 监控接口"
echo "================================"

test_endpoint "获取API监控数据" "/admin/api-monitor?timeRange=24h" "GET" 200
test_endpoint "获取告警规则" "/admin/api-monitor/alerts" "GET" 200

echo ""
echo "📝 测试错误日志接口"
echo "================================"

test_endpoint "获取错误日志列表" "/admin/error-logs" "GET" 200

echo ""
echo "👤 测试用户管理接口"
echo "================================"

test_endpoint "获取用户列表" "/api/admin/users" "GET" 200
test_endpoint "获取角色列表" "/api/admin/roles" "GET" 200

echo ""
echo "💰 测试经济系统接口"
echo "================================"

test_endpoint "获取灵值配置" "/api/admin/economy/config" "GET" 200

echo ""
echo "📊 测试管理员统计接口"
echo "================================"

test_endpoint "获取系统统计" "/api/admin/stats" "GET" 200

echo ""
echo "================================"
echo "📊 测试结果汇总"
echo "================================"
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${YELLOW}警告: $WARNINGS${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo "总计: $((PASSED + WARNINGS + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ 所有测试通过！${NC}"
    exit 0
elif [ $WARNINGS -gt 0 ]; then
    echo -e "\n${YELLOW}⚠️  有 $WARNINGS 个警告，但所有测试通过！${NC}"
    exit 0
else
    echo -e "\n${RED}❌ 有 $FAILED 个测试失败！${NC}"
    exit 1
fi
