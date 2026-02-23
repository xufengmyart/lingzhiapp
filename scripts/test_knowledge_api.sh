#!/bin/bash
# 灵值生态园 - 知识库API测试脚本
# 用于验证知识库侧边栏API是否正常工作

echo "============================================================"
echo "灵值生态园 - 知识库API测试"
echo "============================================================"
echo ""

# 测试地址
BASE_URL="http://meiyueart.com"
API_BASE="$BASE_URL/api"

echo "测试地址: $BASE_URL"
echo "API地址: $API_BASE"
echo ""

# 测试1: 获取知识库条目
echo "[测试 1/3] 获取知识库条目..."
echo "请求: GET $API_BASE/v9/knowledge/items"
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE/v9/knowledge/items")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "✓ HTTP状态: $HTTP_STATUS"
    echo "✓ 响应内容:"
    echo "$BODY" | head -n 20
else
    echo -e "✗ HTTP状态: $HTTP_STATUS"
    echo "✗ 响应内容:"
    echo "$BODY"
fi
echo ""

# 测试2: 搜索知识库
echo "[测试 2/3] 搜索知识库（关键词：签到）..."
echo "请求: GET $API_BASE/v9/knowledge/search?q=签到"
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE/v9/knowledge/search?q=签到")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "✓ HTTP状态: $HTTP_STATUS"
    echo "✓ 响应内容:"
    echo "$BODY" | head -n 20
else
    echo -e "✗ HTTP状态: $HTTP_STATUS"
    echo "✗ 响应内容:"
    echo "$BODY"
fi
echo ""

# 测试3: 健康检查
echo "[测试 3/3] 后端健康检查..."
echo "请求: GET $API_BASE/health"
RESPONSE=$(curl -s -w "\nHTTP_STATUS:%{http_code}" "$API_BASE/health")
HTTP_STATUS=$(echo "$RESPONSE" | grep "HTTP_STATUS" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_STATUS")

if [ "$HTTP_STATUS" = "200" ]; then
    echo -e "✓ HTTP状态: $HTTP_STATUS"
    echo "✓ 响应内容: $BODY"
else
    echo -e "✗ HTTP状态: $HTTP_STATUS"
    echo "✗ 响应内容: $BODY"
fi
echo ""

echo "============================================================"
echo "测试完成"
echo "============================================================"
echo ""
echo "如果所有测试都通过（HTTP状态200），说明知识库API正常工作。"
echo "如果出现404错误，请执行以下操作："
echo "  1. 运行 Nginx配置更新: ./scripts/update_nginx.sh"
echo "  2. 或者运行完整部署: ./scripts/deploy.sh"
echo ""
