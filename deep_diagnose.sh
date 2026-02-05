#!/bin/bash

echo "========================================"
echo "🔍 深度诊断500错误 - 完整检查"
echo "========================================"
echo ""

echo "【1】检查前端文件"
echo "---"
if [ -f /var/www/frontend/index.html ]; then
    echo "✅ index.html 存在"
    echo "   文件大小: $(ls -lh /var/www/frontend/index.html | awk '{print $5}')"
    echo "   修改时间: $(ls -l /var/www/frontend/index.html | awk '{print $6, $7, $8}')"
else
    echo "❌ index.html 不存在"
fi

if [ -d /var/www/frontend/assets ]; then
    echo "✅ assets 目录存在"
    echo "   文件数量: $(ls -1 /var/www/frontend/assets/ | wc -l)"
    echo "   文件列表:"
    ls -lh /var/www/frontend/assets/ | tail -5
else
    echo "❌ assets 目录不存在"
fi

echo ""
echo "【2】检查Nginx配置"
echo "---"
echo "当前配置："
cat /etc/nginx/sites-enabled/default | grep -A 20 "location /"
echo ""

echo "【3】测试前端直接访问"
echo "---"
curl -s http://127.0.0.1/ 2>&1 | head -5
echo ""

echo "【4】测试后端API"
echo "---"
curl -s http://127.0.0.1:8001/api/status 2>&1 | head -5
echo ""

echo "【5】检查后端进程"
echo "---"
ps aux | grep "python.*app.py" | grep -v grep || echo "后端进程未运行"
echo ""

echo "【6】检查端口监听"
echo "---"
netstat -tlnp 2>/dev/null | grep -E ":(80|443|8001)" || ss -tlnp 2>/dev/null | grep -E ":(80|443|8001)"
echo ""

echo "【7】Nginx错误日志（最新20行）"
echo "---"
tail -20 /var/log/nginx/error.log
echo ""

echo "【8】测试所有路径"
echo "---"
echo "测试 / : HTTP $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/)"
echo "测试 /login : HTTP $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/login)"
echo "测试 /api/status : HTTP $(curl -s -o /dev/null -w '%{http_code}' http://127.0.0.1/api/status)"
echo ""

echo "========================================"
echo "✅ 诊断完成"
echo "========================================"
