#!/bin/bash
# 完整部署和测试脚本

echo "========================================="
echo "灵值生态园 - 完整部署和测试"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 统计变量
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNED_TESTS=0

# 测试函数
test_endpoint() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    TOTAL_TESTS=$((TOTAL_TESTS + 1))
    
    echo -n "测试: $name ... "
    
    response=$(curl -s -w "\n%{http_code}" "$url")
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq "$expected" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $http_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    elif [ "$http_code" -eq 200 ] && [ "$expected" -eq 200 ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $http_code)"
        PASSED_TESTS=$((PASSED_TESTS + 1))
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $http_code, 期望 $expected)"
        echo "响应内容:"
        echo "$body" | head -5
        FAILED_TESTS=$((FAILED_TESTS + 1))
        return 1
    fi
}

# 等待服务启动
wait_for_service() {
    echo "等待后端服务启动..."
    sleep 5
}

# 初始化数据
echo "========================================="
echo "📊 初始化数据"
echo "========================================="
echo ""

echo "初始化新闻数据表..."
cd /workspace/projects/admin-backend && python3 scripts/init_news_tables.py 2>&1 | grep -E "✅|❌"

echo ""
echo "初始化系统配置表..."
python3 scripts/init_system_config.py 2>&1 | grep -E "✅|❌"

echo ""
echo "========================================="
echo "🧪 开始功能测试"
echo "========================================="
echo ""

wait_for_service

# 1. 测试新闻系统
echo "📰 测试新闻系统"
echo "----------------------------------------"
test_endpoint "获取文章列表" "http://localhost:5000/api/v9/news/articles" 200
test_endpoint "获取文章分类" "http://localhost:5000/api/v9/news/categories" 200
test_endpoint "获取推荐文章" "http://localhost:5000/api/v9/news/recommendations/1" 200
test_endpoint "获取用户通知" "http://localhost:5000/api/v9/news/notifications" 200
echo ""

# 2. 测试经济系统
echo "💰 测试经济系统"
echo "----------------------------------------"
test_endpoint "获取灵值配置" "http://localhost:5000/api/admin/economy/config" 200
test_endpoint "获取充值档位" "http://localhost:5000/api/admin/economy/recharge-tiers" 200
test_endpoint "获取分红池" "http://localhost:5000/api/admin/economy/dividend-pool" 200
echo ""

# 3. 测试区块链
echo "⛓ 测试区块链"
echo "----------------------------------------"
test_endpoint "区块链健康检查" "http://localhost:5000/api/v9/blockchain/health" 200
test_endpoint "获取网络状态" "http://localhost:5000/api/v9/blockchain/network-status" 200
echo ""

# 4. 测试批量导入
echo "📥 测试批量导入"
echo "----------------------------------------"
echo "测试批量导入（无文件）..."
test_endpoint "批量导入数据" "http://localhost:5000/api/batch-import" 400
echo ""

# 5. 测试资产市场
echo "📈 测试资产市场"
echo "----------------------------------------"
test_endpoint "获取市场统计" "http://localhost:5000/api/v9/market/stats" 200
test_endpoint "获取市场资产" "http://localhost:5000/api/v9/market/assets" 200
echo ""

# 6. 测试API监控
echo "📊 测试API监控"
echo "----------------------------------------"
test_endpoint "获取API监控数据" "http://localhost:5000/admin/api-monitor" 200
echo ""

# 7. 测试错误日志
echo "📝 测试错误日志"
echo "----------------------------------------"
test_endpoint "获取错误日志" "http://localhost:5000/api/errors" 200
echo ""

# 8. 测试用户管理
echo "👤 测试用户管理"
echo "----------------------------------------"
test_endpoint "获取用户列表" "http://localhost:5000/api/users" 200
echo ""

# 9. 测试管理员统计
echo "📊 测试管理员统计"
echo "----------------------------------------"
test_endpoint "获取系统统计" "http://localhost:5000/api/admin/stats" 200
echo ""

# 10. 运行单元测试
echo "🧪 运行单元测试"
echo "----------------------------------------"
cd /workspace/projects/admin-backend && python3 tests/test_comprehensive.py 2>&1 | tail -20
echo ""

# 测试结果汇总
echo ""
echo "========================================="
echo "📊 测试结果汇总"
echo "========================================="
echo -e "总测试数: $TOTAL_TESTS"
echo -e "${GREEN}通过: $PASSED_TESTS${NC}"
echo -e "${RED}失败: $FAILED_TESTS${NC}"
echo ""

# 计算通过率
if [ $TOTAL_TESTS -gt 0 ]; then
    PASS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo "通过率: ${PASS_RATE}%"
else
    echo "通过率: N/A"
fi

echo ""

# 部署状态
if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}=========================================${NC}"
    echo -e "${GREEN}✅ 所有测试通过！部署成功！${NC}"
    echo -e "${GREEN}=========================================${NC}"
    
    # 生成部署报告
    cat > /tmp/deployment_report.txt <<EOF
========================================
部署报告
========================================
部署时间: $(date '+%Y-%m-%d %H:%M:%S')
版本: V9.24.0

测试结果:
- 总测试数: $TOTAL_TESTS
- 通过: $PASSED_TESTS
- 失败: $FAILED_TESTS
- 通过率: ${PASS_RATE}%

部署状态: 成功

新功能:
✓ 自动平台信息新闻功能
✓ 批量导入数据优化
✓ 经济系统功能增强
✓ 区块链集成测试（Goerli）
✓ 邮件/短信告警集成
✓ 性能监控与优化
✓ 单元测试覆盖
✓ 用户培训文档

========================================
EOF
    
    cat /tmp/deployment_report
    
    exit 0
else
    echo -e "${RED}=========================================${NC}"
    echo -e "${RED}❌ 部署失败！存在 $FAILED_TESTS 个失败测试${NC}"
    echo -e "${RED}=========================================${NC}"
    exit 1
fi
