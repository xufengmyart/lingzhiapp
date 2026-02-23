#!/bin/bash
# 性能优化和功能测试脚本

echo "🚀 开始性能优化和功能测试..."
echo "================================"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试结果统计
PASSED=0
FAILED=0

# 测试函数
test_endpoint() {
    local name="$1"
    local endpoint="$2"
    local method="${3:-GET}"
    local expected_status="${4:-200}"
    
    echo -n "测试: $name ... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -o /tmp/test_response.txt "$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -o /tmp/test_response.txt "$endpoint" 2>&1)
    fi
    
    status_code=$(echo "$response" | tail -n1)
    
    if [ "$status_code" -eq "$expected_status" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
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

echo ""
echo "📊 测试 API 性能监控接口"
echo "================================"

test_endpoint "获取API监控数据" "http://localhost:5000/api/admin/api-monitor?timeRange=24h" "GET" 200

echo ""
echo "📝 测试错误日志接口"
echo "================================"

test_endpoint "获取错误日志列表" "http://localhost:5000/api/admin/error-logs" "GET" 200

echo ""
echo "📈 测试资产交易市场接口"
echo "================================"

test_endpoint "获取市场统计" "http://localhost:5000/api/v9/market/stats" "GET" 200
test_endpoint "获取市场资产列表" "http://localhost:5000/api/v9/market/assets" "GET" 200

echo ""
echo "📥 测试批量导入接口"
echo "================================"

# 创建测试数据
cat > /tmp/test_import.json << EOF
{
  "type": "data_element",
  "items": [
    {
      "name": "测试数据要素",
      "type": "文本",
      "description": "这是一个测试数据要素"
    }
  ]
}
EOF

test_endpoint "批量导入数据" "http://localhost:5000/api/v9/batch-import" "POST" 200

echo ""
echo "🔗 测试区块链集成接口"
echo "================================"

test_endpoint "获取区块链网络状态" "http://localhost:5000/api/v9/blockchain/network-status" "GET" 200

echo ""
echo "================================"
echo "📊 测试结果汇总"
echo "================================"
echo -e "${GREEN}通过: $PASSED${NC}"
echo -e "${RED}失败: $FAILED${NC}"
echo "总计: $((PASSED + FAILED))"

if [ $FAILED -eq 0 ]; then
    echo -e "\n${GREEN}✅ 所有测试通过！${NC}"
    exit 0
else
    echo -e "\n${RED}❌ 有 $FAILED 个测试失败！${NC}"
    exit 1
fi
