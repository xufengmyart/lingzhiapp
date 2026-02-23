#!/bin/bash

# ================================================================
# 紧急修复脚本 - 快速恢复 502 错误
# ================================================================

set -e

echo "=================================================="
echo "🚨 紧急修复 - 恢复 502 错误"
echo "=================================================="

PROJECT_ROOT="/workspace/projects"
BACKEND_DIR="$PROJECT_ROOT/admin-backend"
LOG_DIR="/tmp"

# 1. 检查并启动 Flask 服务
echo ""
echo "[步骤 1] 检查并启动 Flask 服务..."
cd "$BACKEND_DIR"

if pgrep -f "python3 app.py" > /dev/null; then
    echo "⚠️  Flask 服务正在运行，检查健康状态..."
    if curl -s -m 5 http://localhost:8080/api/health > /dev/null; then
        echo "✅ Flask 服务正常"
    else
        echo "❌ Flask 服务异常，重启..."
        pkill -f "python3 app.py" || true
        sleep 2
        nohup python3 app.py > "$LOG_DIR/flask_server.log" 2>&1 &
        sleep 3
    fi
else
    echo "🔄 启动 Flask 服务..."
    nohup python3 app.py > "$LOG_DIR/flask_server.log" 2>&1 &
    sleep 3
fi

# 验证 Flask 服务
if curl -s -m 5 http://localhost:8080/api/health > /dev/null; then
    echo "✅ Flask 服务启动成功（端口 8080）"
else
    echo "❌ Flask 服务启动失败"
    echo "查看日志：tail -f $LOG_DIR/flask_server.log"
    exit 1
fi

# 2. 检查并启动 Nginx
echo ""
echo "[步骤 2] 检查并启动 Nginx..."
if ! command -v nginx &> /dev/null; then
    echo "📦 安装 Nginx..."
    apt-get update -qq
    apt-get install -y nginx -qq
fi

if pgrep nginx > /dev/null; then
    echo "⚠️  Nginx 正在运行，重新加载配置..."
    nginx -s reload 2>&1 || true
else
    echo "🔄 启动 Nginx..."
    nginx
fi

# 检查 Nginx 端口
if netstat -tlnp 2>&1 | grep -q ":80 "; then
    echo "✅ Nginx 端口 80 正在监听"
else
    echo "❌ Nginx 端口 80 未监听"
    exit 1
fi

# 3. 验证反向代理
echo ""
echo "[步骤 3] 验证反向代理..."
if curl -s -m 5 http://localhost/api/health > /dev/null; then
    echo "✅ 反向代理正常"
else
    echo "❌ 反向代理失败，尝试修复配置..."

    # 检查配置文件
    if [ ! -f /etc/nginx/sites-enabled/meiyueart.com ]; then
        echo "⚠️  Nginx 配置文件不存在，创建配置..."
        ln -sf /etc/nginx/sites-available/meiyueart.com /etc/nginx/sites-enabled/ 2>&1 || true
        rm -f /etc/nginx/sites-enabled/default 2>&1 || true
        nginx -s reload
        sleep 2
    fi

    # 再次验证
    if curl -s -m 5 http://localhost/api/health > /dev/null; then
        echo "✅ 反向代理修复成功"
    else
        echo "❌ 反向代理仍然失败"
        exit 1
    fi
fi

# 4. 运行完整测试
echo ""
echo "[步骤 4] 运行完整 API 测试..."
echo "  - 健康检查: $(curl -s -m 5 http://localhost/api/health | grep -o '"status":"[^"]*"' || echo '❌')"
echo "  - 商家列表: $(curl -s -m 5 http://localhost/api/merchants 2>&1 | python3 -c 'import sys, json; print(f"{len(json.load(sys.stdin))} 条记录")' 2>&1 || echo '❌')"
echo "  - 项目列表: $(curl -s -m 5 http://localhost/api/projects 2>&1 | python3 -c 'import sys, json; print(f"{len(json.load(sys.stdin))} 条记录")' 2>&1 || echo '❌')"

echo ""
echo "=================================================="
echo "✅ 紧急修复完成！"
echo "=================================================="
echo ""
echo "现在可以通过以下地址访问："
echo "  - 前端: http://meiyueart.com"
echo "  - 后端: http://meiyueart.com/api"
echo ""
echo "如果问题仍然存在，请检查日志："
echo "  - Flask: tail -f $LOG_DIR/flask_server.log"
echo "  - Nginx: tail -f /var/log/nginx/error.log"
echo ""
