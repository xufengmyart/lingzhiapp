#!/bin/bash

echo "========================================"
echo "🔍 紧急诊断403错误"
echo "========================================"
echo ""

echo "【1】检查前端目录权限"
echo "---"
ls -ld /var/www/frontend
ls -ld /var/www/frontend/assets
echo ""

echo "【2】检查index.html权限"
echo "---"
ls -lh /var/www/frontend/index.html 2>&1
echo ""

echo "【3】检查Nginx用户权限"
echo "---"
ps aux | grep nginx | head -3
echo ""
echo "Nginx配置用户："
grep "^user" /etc/nginx/nginx.conf
echo ""

echo "【4】检查SELinux状态"
echo "---"
if command -v getenforce &> /dev/null; then
    getenforce
else
    echo "SELinux未安装"
fi
echo ""

echo "【5】检查防火墙规则"
echo "---"
iptables -L -n | grep -E "80|443" | head -10 || echo "防火墙规则未显示"
echo ""

echo "【6】测试Nginx配置"
echo "---"
nginx -t 2>&1 | head -20
echo ""

echo "【7】检查Nginx错误日志（最新20行）"
echo "---"
tail -20 /var/log/nginx/error.log
echo ""

echo "【8】测试本地访问"
echo "---"
curl -I http://127.0.0.1/ 2>&1 | head -10
echo ""

echo "【9】测试HTTPS访问"
echo "---"
curl -I https://127.0.0.1/ -k 2>&1 | head -10
echo ""

echo "【10】检查SSL证书"
echo "---"
ls -lh /etc/letsencrypt/live/meiyueart.com/
echo ""

echo "========================================"
echo "✅ 诊断完成"
echo "========================================"
