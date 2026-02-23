#!/bin/bash

# 手机分享链接问题诊断脚本

echo "========================================="
echo "  手机分享链接问题诊断"
echo "========================================="
echo ""

DOMAIN="meiyueart.com"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$DOMAIN 2>/dev/null)
HTTPS_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://$DOMAIN 2>/dev/null)
HTTP_REDIRECT=$(curl -sI http://$DOMAIN 2>/dev/null | grep -i "Location:" | head -1)
HTTPS_REDIRECT=$(curl -sI https://$DOMAIN 2>/dev/null | grep -i "Location:" | head -1)

echo "1. HTTP 访问测试 ($DOMAIN)"
echo "   状态码: $HTTP_CODE"
if [ -n "$HTTP_REDIRECT" ]; then
    echo "   重定向: $HTTP_REDIRECT"
fi
if [ "$HTTP_CODE" = "200" ]; then
    echo "   ✓ HTTP 访问正常"
else
    echo "   ✗ HTTP 访问异常"
fi
echo ""

echo "2. HTTPS 访问测试 ($DOMAIN)"
echo "   状态码: $HTTPS_CODE"
if [ -n "$HTTPS_REDIRECT" ]; then
    echo "   重定向: $HTTPS_REDIRECT"
fi
if [ "$HTTPS_CODE" = "200" ]; then
    echo "   ✓ HTTPS 访问正常"
else
    echo "   ✗ HTTPS 访问异常"
fi
echo ""

echo "3. SSL 证书检查"
if command -v openssl &> /dev/null; then
    echo "   证书信息:"
    openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | grep -A 2 "subject=" | head -3 | sed 's/^/      /'
    echo ""
    echo "   证书有效期:"
    openssl s_client -connect $DOMAIN:443 -servername $DOMAIN 2>/dev/null | grep -i "notAfter" | sed 's/^/      /'
else
    echo "   ⚠ openssl 未安装，无法检查证书"
fi
echo ""

echo "4. DNS 解析检查"
if command -v nslookup &> /dev/null; then
    echo "   DNS 记录:"
    nslookup $DOMAIN 2>/dev/null | grep -A 2 "Name:" | sed 's/^/      /'
else
    echo "   ⚠ nslookup 未安装，无法检查 DNS"
fi
echo ""

echo "5. Nginx 配置检查"
if [ -f "/etc/nginx/sites-enabled/meiyueart.conf" ]; then
    echo "   ✓ Nginx 配置文件存在"
    echo "   配置内容预览:"
    grep -E "listen|server_name|return" /etc/nginx/sites-enabled/meiyueart.conf | head -10 | sed 's/^/      /'
else
    echo "   ✗ Nginx 配置文件不存在"
fi
echo ""

echo "6. 前端构建检查"
if [ -d "/var/www/frontend" ]; then
    echo "   ✓ 前端目录存在"
    if [ -f "/var/www/frontend/index.html" ]; then
        echo "   ✓ index.html 存在"
    else
        echo "   ✗ index.html 不存在"
    fi
else
    echo "   ✗ 前端目录不存在"
fi
echo ""

echo "7. 后端服务检查"
if command -v netstat &> /dev/null; then
    echo "   端口监听状态:"
    netstat -tlnp 2>/dev/null | grep -E "80|443|8001" | sed 's/^/      /' || echo "      无法获取端口信息"
else
    echo "   ⚠ netstat 未安装，无法检查端口"
fi
echo ""

echo "========================================="
echo "  诊断完成"
echo "========================================="
echo ""
echo "建议的访问链接："
if [ "$HTTP_CODE" = "200" ]; then
    echo "  ✓ HTTP: http://$DOMAIN (推荐用于分享)"
else
    echo "  ✗ HTTP: http://$DOMAIN (不可用)"
fi

if [ "$HTTPS_CODE" = "200" ]; then
    echo "  ✓ HTTPS: https://$DOMAIN"
else
    echo "  ✗ HTTPS: https://$DOMAIN (不可用)"
fi
echo ""
