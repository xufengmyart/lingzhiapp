#!/bin/bash

# 灵值生态园 - 访问测试脚本
# 用于验证系统服务状态

echo "======================================"
echo "灵值生态园 - 服务状态测试"
echo "======================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local name="$1"
    local url="$2"

    echo -n "测试 $name ... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>&1)

    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ 正常 ($response)${NC}"
        return 0
    else
        echo -e "${RED}✗ 失败 ($response)${NC}"
        return 1
    fi
}

# 1. 检查 Flask 服务进程
echo "1. 检查 Flask 服务进程"
if ps aux | grep -v grep | grep "python.*app.py" > /dev/null; then
    pid=$(ps aux | grep -v grep | grep "python.*app.py" | awk '{print $2}')
    echo -e "   ${GREEN}✓ Flask 服务运行中 (PID: $pid)${NC}"
else
    echo -e "   ${RED}✗ Flask 服务未运行${NC}"
fi
echo ""

# 2. 检查端口监听
echo "2. 检查端口监听状态"
if lsof -i :8080 > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓ 端口 8080 已监听${NC}"
else
    echo -e "   ${RED}✗ 端口 8080 未监听${NC}"
fi

if lsof -i :9000 > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓ 端口 9000 已监听 (Coze 运行时)${NC}"
else
    echo -e "   ${RED}✗ 端口 9000 未监听${NC}"
fi
echo ""

# 3. 本地 API 测试
echo "3. 本地 API 测试"
test_endpoint "健康检查" "http://127.0.0.1:8080/api/health"
test_endpoint "登录接口" "http://127.0.0.1:8080/api/login" || echo -e "   ${YELLOW}⚠ 可能需要 POST 请求${NC}"
test_endpoint "项目列表" "http://127.0.0.1:8080/api/projects"
test_endpoint "商家列表" "http://127.0.0.1:8080/api/merchants"
echo ""

# 4. 数据库检查
echo "4. 数据库状态检查"
db_path="/workspace/projects/admin-backend/lingzhi_ecosystem.db"
if [ -f "$db_path" ]; then
    size=$(du -h "$db_path" | cut -f1)
    echo -e "   ${GREEN}✓ 数据库文件存在 (大小: $size)${NC}"

    # 统计数据
    user_count=$(sqlite3 "$db_path" "SELECT COUNT(*) FROM users;" 2>/dev/null || echo "0")
    project_count=$(sqlite3 "$db_path" "SELECT COUNT(*) FROM projects;" 2>/dev/null || echo "0")
    merchant_count=$(sqlite3 "$db_path" "SELECT COUNT(*) FROM merchants;" 2>/dev/null || echo "0")

    echo "   - 用户数: $user_count"
    echo "   - 项目数: $project_count"
    echo "   - 商家数: $merchant_count"
else
    echo -e "   ${RED}✗ 数据库文件不存在${NC}"
fi
echo ""

# 5. 访问信息
echo "======================================"
echo "📋 访问信息"
echo "======================================"
echo ""
echo "Coze 平台临时域名:"
echo -e "   ${GREEN}https://f8ab8c28-f515-4fa3-9fb4-0ca0c3a0d34f.dev.coze.site${NC}"
echo ""
echo "本地测试地址:"
echo -e "   ${GREEN}http://127.0.0.1:8080${NC}"
echo ""
echo "默认登录账号:"
echo -e "   用户名: ${YELLOW}admin${NC}"
echo -e "   密码: ${YELLOW}admin123${NC}"
echo ""
echo "======================================"

# 6. 问题诊断
echo ""
echo "6. 常见问题诊断"
echo "======================================"

# 检查域名解析
echo "域名解析检查:"
dns_ip=$(nslookup meiyueart.com 2>/dev/null | grep -A 1 "Name:" | tail -1 | awk '{print $2}')
if [ -n "$dns_ip" ]; then
    echo -e "   meiyueart.com → ${YELLOW}$dns_ip${NC}"
    echo -e "   ${RED}✗ 与服务器 IP 不匹配 (服务器: 9.128.106.115)${NC}"
    echo "   解决方案: 使用 Coze 临时域名访问"
else
    echo -e "   ${YELLOW}⚠ 无法查询域名解析${NC}"
fi
echo ""

# 7. 访问引导
echo "======================================"
echo "🚀 快速访问"
echo "======================================"
echo ""
echo "方式 1: 点击下方链接直接访问"
echo "   https://f8ab8c28-f515-4fa3-9fb4-0ca0c3a0d34f.dev.coze.site"
echo ""
echo "方式 2: 查看访问引导页面"
echo "   file:///workspace/projects/public/access-guide.html"
echo ""
echo "======================================"
echo ""
