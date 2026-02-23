#!/bin/bash

echo "==============================================="
echo "服务全面诊断脚本"
echo "==============================================="

# 1. 停止所有 Python 进程
echo ""
echo "[1] 停止所有 Python 进程..."
pkill -9 -f "python.*app.py"
sleep 2
echo "✅ 进程已停止"

# 2. 检查是否有残留进程
echo ""
echo "[2] 检查残留进程..."
ps aux | grep app.py | grep -v grep || echo "✅ 无残留进程"

# 3. 检查端口占用
echo ""
echo "[3] 检查 8001 端口占用..."
netstat -tlnp 2>/dev/null | grep 8001 || echo "✅ 端口 8001 未被占用"

# 4. 前台运行服务以查看实时输出
echo ""
echo "[4] 前台运行服务（30秒后自动停止）..."
cd /var/www/backend
timeout 30 python3 app.py 2>&1 | head -100 &
SERVER_PID=$!
sleep 30
kill $SERVER_PID 2>/dev/null || true

echo ""
echo "==============================================="
echo "诊断完成"
echo "==============================================="
