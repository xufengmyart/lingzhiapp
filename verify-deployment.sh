#!/bin/bash

# 验证部署结果

set -e

# 配置
DOMAIN="meiyueart.com"
SERVER_HOST="123.56.142.143"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "验证部署结果 - $DOMAIN"
echo "=========================================="
echo ""

# 1. 检查服务器文件
echo -e "${BLUE}[1/4]${NC} 检查服务器文件..."
export SSHPASS="Meiyue@root123"
FILES=$(sshpass -e ssh -o StrictHostKeyChecking=no root@123.56.142.143 "ls -la /var/www/html/ | grep -E '(index.html|assets)' | wc -l")

if [ "$FILES" -ge 2 ]; then
    echo -e "${GREEN}✓${NC} 服务器文件存在"
else
    echo -e "${RED}✗${NC} 服务器文件不完整"
fi
unset SSHPASS
echo ""

# 2. 测试 HTTP 访问
echo -e "${BLUE}[2/4]${NC} 测试 HTTP 访问..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" "http://$DOMAIN" 2>/dev/null || echo "000")

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} HTTP 访问正常 (状态码: $HTTP_CODE)"
elif [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    echo -e "${YELLOW}⚠${NC} HTTP 重定向 (状态码: $HTTP_CODE)"
    FINAL_URL=$(curl -s -I "http://$DOMAIN" | grep -i location | head -1 | awk '{print $2}' | tr -d '\r')
    echo "  重定向到: $FINAL_URL"
else
    echo -e "${RED}✗${NC} HTTP 访问失败 (状态码: $HTTP_CODE)"
fi
echo ""

# 3. 测试 HTTPS 访问
echo -e "${BLUE}[3/4]${NC} 测试 HTTPS 访问..."
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "https://$DOMAIN" 2>/dev/null || echo "000")

if [ "$HTTPS_CODE" = "200" ]; then
    echo -e "${GREEN}✓${NC} HTTPS 访问正常 (状态码: $HTTPS_CODE)"
elif [ "$HTTPS_CODE" = "301" ] || [ "$HTTPS_CODE" = "302" ]; then
    echo -e "${YELLOW}⚠${NC} HTTPS 重定向 (状态码: $HTTPS_CODE)"
    FINAL_URL=$(curl -s -I "https://$DOMAIN" | grep -i location | head -1 | awk '{print $2}' | tr -d '\r')
    echo "  重定向到: $FINAL_URL"
elif [ "$HTTPS_CODE" = "000" ]; then
    echo -e "${YELLOW}⚠${NC} HTTPS 证书可能未配置"
    echo "  可以使用 HTTP 访问: http://$DOMAIN"
else
    echo -e "${RED}✗${NC} HTTPS 访问失败 (状态码: $HTTPS_CODE)"
fi
echo ""

# 4. 显示 Nginx 配置
echo -e "${BLUE}[4/4]${NC} 显示 Nginx 配置..."
export SSHPASS="Meiyue@root123"
NGINX_CONF=$(sshpass -e ssh -o StrictHostKeyChecking=no root@123.56.142.143 "cat /etc/nginx/sites-enabled/default 2>/dev/null | head -30 || cat /etc/nginx/nginx.conf 2>/dev/null | head -20")
echo "$NGINX_CONF"
unset SSHPASS
echo ""

# 完成
echo "=========================================="
echo "验证完成"
echo "=========================================="
echo ""
echo "📝 访问信息:"
echo ""
echo "   域名: $DOMAIN"
echo "   IP:   $SERVER_HOST"
echo ""
echo "🌐 访问地址:"
echo "   - http://$DOMAIN"
echo "   - http://$SERVER_HOST"
echo ""
if [ "$HTTPS_CODE" = "200" ] || [ "$HTTPS_CODE" = "301" ] || [ "$HTTPS_CODE" = "302" ]; then
    echo "   - https://$DOMAIN"
fi
echo ""
echo "📱 移动端:"
echo "   - 在手机浏览器中访问 $DOMAIN"
echo "   - 添加到主屏幕以获得 PWA 体验"
echo ""
echo "🔧 管理入口:"
echo "   - 后台管理: http://$DOMAIN/admin"
echo "   - 用户指南: http://$DOMAIN/guide"
echo "   - 项目入口: http://$DOMAIN/medium-video"
echo ""
echo "✨ 开始使用吧！"
echo ""
