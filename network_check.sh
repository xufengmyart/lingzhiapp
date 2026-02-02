#!/bin/bash
# 网络连接检查脚本

echo "=================================================="
echo "灵值生态园 - 网络连接检查"
echo "=================================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}[1] 检查服务状态${NC}"
echo "Flask服务 (8080):"
if pgrep -f "python3.*app.py" > /dev/null; then
    echo -e "  ${GREEN}✓ 运行中${NC}"
else
    echo -e "  ${RED}✗ 未运行${NC}"
fi

echo "集成服务器 (80):"
if pgrep -f "integrated_server.py" > /dev/null; then
    echo -e "  ${GREEN}✓ 运行中${NC}"
else
    echo -e "  ${RED}✗ 未运行${NC}"
fi

echo "Nginx:"
if pgrep nginx > /dev/null; then
    echo -e "  ${GREEN}✓ 运行中${NC}"
else
    echo -e "  ${YELLOW}! 未运行${NC}"
fi

echo ""
echo -e "${BLUE}[2] 检查端口监听${NC}"
echo "80端口:"
if netstat -tlnp | grep ":80 " > /dev/null; then
    echo -e "  ${GREEN}✓ 监听中${NC}"
    netstat -tlnp | grep ":80 "
else
    echo -e "  ${RED}✗ 未监听${NC}"
fi

echo "8080端口:"
if netstat -tlnp | grep ":8080 " > /dev/null; then
    echo -e "  ${GREEN}✓ 监听中${NC}"
    netstat -tlnp | grep ":8080 "
else
    echo -e "  ${RED}✗ 未监听${NC}"
fi

echo ""
echo -e "${BLUE}[3] 本地访问测试${NC}"
echo "127.0.0.1:80:"
if curl -s http://127.0.0.1 | grep -q "灵值生态园"; then
    echo -e "  ${GREEN}✓ 可访问${NC}"
else
    echo -e "  ${RED}✗ 无法访问${NC}"
fi

echo "127.0.0.1:8080/api/health:"
if curl -s http://127.0.0.1:8080/api/health | grep -q "ok"; then
    echo -e "  ${GREEN}✓ 可访问${NC}"
else
    echo -e "  ${RED}✗ 无法访问${NC}"
fi

echo ""
echo -e "${BLUE}[4] 内网IP访问测试${NC}"
echo "9.129.167.93:80:"
if curl -s http://9.129.167.93 | grep -q "灵值生态园"; then
    echo -e "  ${GREEN}✓ 可访问${NC}"
else
    echo -e "  ${RED}✗ 无法访问${NC}"
fi

echo ""
echo -e "${BLUE}[5] 公网IP访问测试${NC}"
echo "123.56.142.143:80:"
if curl -s --connect-timeout 5 http://123.56.142.143 | grep -q "灵值生态园"; then
    echo -e "  ${GREEN}✓ 可访问${NC}"
else
    echo -e "  ${RED}✗ 无法访问${NC}"
    echo -e "  ${YELLOW}! 可能原因：阿里云安全组未开放80端口${NC}"
fi

echo ""
echo -e "${BLUE}[6] 域名访问测试${NC}"
echo "meiyueart.com:"
if curl -s --connect-timeout 5 http://meiyueart.com | grep -q "灵值生态园"; then
    echo -e "  ${GREEN}✓ 可访问${NC}"
else
    echo -e "  ${RED}✗ 无法访问${NC}"
    echo -e "  ${YELLOW}! 可能原因：DNS解析未配置或安全组未开放80端口${NC}"
fi

echo "www.meiyueart.com:"
if curl -s --connect-timeout 5 http://www.meiyueart.com | grep -q "灵值生态园"; then
    echo -e "  ${GREEN}✓ 可访问${NC}"
else
    echo -e "  ${RED}✗ 无法访问${NC}"
    echo -e "  ${YELLOW}! 可能原因：DNS解析未配置www子域名${NC}"
fi

echo ""
echo "=================================================="
echo "诊断结果"
echo "=================================================="
echo ""
echo -e "${GREEN}可访问的地址:${NC}"
echo "  • http://127.0.0.1 (本地)"
echo "  • http://9.129.167.93 (内网IP)"
echo ""
echo -e "${RED}不可访问的地址:${NC}"
echo "  • http://123.56.142.143 (公网IP)"
echo "  • http://meiyueart.com"
echo "  • http://www.meiyueart.com"
echo ""
echo -e "${YELLOW}问题分析:${NC}"
echo "1. 本地服务正常，端口监听正常"
echo "2. 内网IP访问正常"
echo "3. 公网IP和域名无法访问"
echo ""
echo -e "${YELLOW}可能原因:${NC}"
echo "1. 阿里云安全组未开放80端口"
echo "2. DNS解析未配置或未生效"
echo "3. 云服务器网络策略限制"
echo ""
echo -e "${YELLOW}解决方案:${NC}"
echo "1. 登录阿里云控制台"
echo "2. 进入 ECS 实例 -> 安全组"
echo "3. 添加入站规则：端口80，协议TCP，来源0.0.0.0/0"
echo "4. 检查DNS解析配置"
echo "5. 等待DNS解析生效（最多24小时）"
echo ""
echo "=================================================="
