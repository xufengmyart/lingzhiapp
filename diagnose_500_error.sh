#!/bin/bash

echo "========================================"
echo "🔍 诊断500错误"
echo "========================================"
echo ""

echo "1. 检查Nginx错误日志（最近20行）："
echo "---"
tail -20 /var/log/nginx/error.log
echo ""

echo "========================================"
echo "2. 检查后端服务状态："
echo "---"
systemctl status --no-pager -l 2>&1 | grep -E "(python|flask|gunicorn|admin-backend)" | head -20
echo ""

echo "========================================"
echo "3. 检查后端进程："
echo "---"
ps aux | grep -E "python|flask|gunicorn" | grep -v grep
echo ""

echo "========================================"
echo "4. 测试后端API："
echo "---"
curl -s http://127.0.0.1:8001/api/status 2>&1 || echo "后端API无响应"
echo ""

echo "========================================"
echo "5. 检查端口占用："
echo "---"
netstat -tlnp | grep 8001 || echo "8001端口未监听"
echo ""

echo "========================================"
echo "✅ 诊断完成"
echo "========================================"
