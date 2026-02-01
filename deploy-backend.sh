#!/bin/bash

# 在阿里云服务器上部署后端API服务

set -e

# 配置
SERVER_USER="root"
SERVER_HOST="123.56.142.143"
SERVER_PASSWORD="Meiyue@root123"
REMOTE_PATH="/var/www/backend"

# 颜色输出
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "部署后端API到阿里云服务器"
echo "=========================================="
echo ""

# 1. 创建远程目录
echo -e "${BLUE}[1/4]${NC} 创建远程目录..."
export SSHPASS="$SERVER_PASSWORD"
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "mkdir -p $REMOTE_PATH"
echo -e "${GREEN}✓${NC} 目录创建完成"
echo ""

# 2. 上传后端文件
echo -e "${BLUE}[2/4]${NC} 上传后端文件..."
rsync -avz --delete \
    -e "sshpass -e ssh -o StrictHostKeyChecking=no" \
    "admin-backend/" \
    "$SERVER_USER@$SERVER_HOST:$REMOTE_PATH/"
echo -e "${GREEN}✓${NC} 文件上传完成"
echo ""

# 3. 安装依赖
echo -e "${BLUE}[3/4]${NC} 安装依赖..."
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" \
    "cd $REMOTE_PATH && pip install -r requirements.txt"
echo -e "${GREEN}✓${NC} 依赖安装完成"
echo ""

# 4. 配置Nginx反向代理
echo -e "${BLUE}[4/4]${NC} 配置Nginx反向代理..."

# 创建Nginx配置
NGINX_CONF="/etc/nginx/sites-available/lingzhi-api.conf"

sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "cat > $NGINX_CONF << 'EOF'
# API 反向代理配置
server {
    listen 8000;
    server_name 123.56.142.143 meiyueart.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_cache_bypass \$http_upgrade;
    }
}
EOF
"

# 启用配置
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" \
    "ln -sf $NGINX_CONF /etc/nginx/sites-enabled/ 2>/dev/null || true"

# 重启Nginx
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" \
    "nginx -t && systemctl reload nginx"

echo -e "${GREEN}✓${NC} Nginx配置完成"
echo ""

# 5. 创建systemd服务
echo -e "${BLUE}[5/5]${NC} 创建systemd服务..."

sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "cat > /etc/systemd/system/lingzhi-api.service << 'EOF'
[Unit]
Description=Lingzhi Ecosystem API Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/backend
ExecStart=/usr/bin/python3 /var/www/backend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
"

echo -e "${GREEN}✓${NC} 服务配置完成"
echo ""

# 6. 启动服务
echo -e "${BLUE}[6/6]${NC} 启动API服务..."

# 重载systemd
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" \
    "systemctl daemon-reload"

# 停止旧服务（如果存在）
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" \
    "systemctl stop lingzhi-api 2>/dev/null || true"

# 启动新服务
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" \
    "systemctl start lingzhi-api"

# 启用开机自启
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" \
    "systemctl enable lingzhi-api"

# 检查服务状态
SERVICE_STATUS=$(sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" \
    "systemctl is-active lingzhi-api 2>/dev/null || echo 'unknown'")

if [ "$SERVICE_STATUS" = "active" ]; then
    echo -e "${GREEN}✓${NC} API服务已启动"
else
    echo -e "${RED}✗${NC} API服务启动失败: $SERVICE_STATUS"
    echo "查看日志: journalctl -u lingzhi-api -n 50"
fi
unset SSHPASS
echo ""

# 完成
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "🔧 API服务信息:"
echo "   - 服务名称: lingzhi-api"
echo "   - 服务状态: $SERVICE_STATUS"
echo "   - 端口: 8000"
echo ""
echo "📝 管理命令:"
echo "   查看状态: systemctl status lingzhi-api"
echo "   查看日志: journalctl -u lingzhi-api -f"
echo "   重启服务: systemctl restart lingzhi-api"
echo "   停止服务: systemctl stop lingzhi-api"
echo ""
echo "🔍 测试API:"
echo "   curl http://123.56.142.143:8000/api/health"
echo ""
