#!/bin/bash

# ================================================================
# 灵值生态园服务启动脚本
# ================================================================

set -e

PROJECT_ROOT="/workspace/projects"
BACKEND_DIR="$PROJECT_ROOT/admin-backend"
LOG_DIR="/tmp"

echo "=================================================="
echo "灵值生态园服务启动中..."
echo "=================================================="

# 1. 启动后端 Flask 服务
echo ""
echo "[1/3] 启动后端 Flask 服务..."
cd "$BACKEND_DIR"

# 检查是否已有 Flask 进程运行
if pgrep -f "python3 app.py" > /dev/null; then
    echo "⚠️  Flask 服务已在运行，跳过启动"
else
    echo "✅ 启动 Flask 服务..."
    nohup python3 app.py > "$LOG_DIR/flask_server.log" 2>&1 &
    sleep 3
    echo "✅ Flask 服务已启动（端口 8080）"
fi

# 2. 启动 Nginx 服务
echo ""
echo "[2/3] 启动 Nginx 服务..."
if pgrep nginx > /dev/null; then
    echo "⚠️  Nginx 服务已在运行，重新加载配置..."
    nginx -s reload
else
    echo "✅ 启动 Nginx 服务..."
    nginx
fi
echo "✅ Nginx 服务已启动（端口 80）"

# 3. 验证服务状态
echo ""
echo "[3/3] 验证服务状态..."

# 检查端口
if netstat -tlnp 2>&1 | grep -q ":80 "; then
    echo "✅ Nginx 端口 80 正在监听"
else
    echo "❌ Nginx 端口 80 未监听"
    exit 1
fi

if netstat -tlnp 2>&1 | grep -q ":8080 "; then
    echo "✅ Flask 端口 8080 正在监听"
else
    echo "❌ Flask 端口 8080 未监听"
    exit 1
fi

# 测试 API
if curl -s -m 5 http://localhost/api/health > /dev/null; then
    echo "✅ API 健康检查通过"
else
    echo "❌ API 健康检查失败"
    exit 1
fi

echo ""
echo "=================================================="
echo "✅ 所有服务启动成功！"
echo "=================================================="
echo ""
echo "服务地址："
echo "  - 前端: http://meiyueart.com"
echo "  - 后端: http://meiyueart.com/api"
echo ""
echo "日志位置："
echo "  - Flask: $LOG_DIR/flask_server.log"
echo "  - Nginx: /var/log/nginx/"
echo ""
