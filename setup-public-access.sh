#!/bin/bash

# 公网部署快速配置脚本

set -e

echo "======================================"
echo "灵值生态园 - 公网部署配置"
echo "======================================"

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用root用户或sudo运行此脚本"
    exit 1
fi

# 获取公网IP
echo ""
echo "正在获取服务器公网IP..."
PUBLIC_IP=$(curl -s ifconfig.me || curl -s icanhazip.com || echo "")

if [ -z "$PUBLIC_IP" ]; then
    echo "警告: 无法自动获取公网IP"
    read -p "请输入您的公网IP地址: " PUBLIC_IP
else
    echo "检测到公网IP: $PUBLIC_IP"
    read -p "是否使用此IP? (y/n): " confirm
    if [ "$confirm" != "y" ]; then
        read -p "请输入您的公网IP地址: " PUBLIC_IP
    fi
fi

if [ -z "$PUBLIC_IP" ]; then
    echo "错误: 必须提供公网IP地址"
    exit 1
fi

# 配置后端
echo ""
echo "======================================"
echo "配置后端服务..."
echo "======================================"

cd "$(dirname "$0")/admin-backend"

# 确保后端监听所有接口
if ! grep -q "host='0.0.0.0'" app.py; then
    echo "警告: 后端可能未配置监听所有接口"
fi

# 启动后端服务
echo "启动后端服务..."
nohup python app.py > ../logs/app_backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
sleep 5

# 检查后端是否启动成功
if ps -p $BACKEND_PID > /dev/null; then
    echo "✓ 后端服务启动成功 (PID: $BACKEND_PID)"
else
    echo "✗ 后端服务启动失败，请查看日志: logs/app_backend.log"
    exit 1
fi

# 配置前端
echo ""
echo "======================================"
echo "配置前端..."
echo "======================================"

cd "$(dirname "$0")/web-app"

# 更新环境变量
echo "配置API地址: http://$PUBLIC_IP:8001"
cat > .env.production <<EOF
VITE_API_BASE_URL=http://$PUBLIC_IP:8001
EOF

# 重新构建前端
echo "重新构建前端..."
npm run build

if [ $? -eq 0 ]; then
    echo "✓ 前端构建成功"
else
    echo "✗ 前端构建失败"
    exit 1
fi

# 检查防火墙
echo ""
echo "======================================"
echo "检查防火墙配置..."
echo "======================================"

if command -v ufw &> /dev/null; then
    echo "检测到UFW防火墙"
    echo "开放必要端口..."

    ufw allow 8001/tcp comment "Backend API"
    ufw allow 80/tcp comment "HTTP"
    ufw allow 443/tcp comment "HTTPS"

    echo "✓ 防火墙规则已更新"
elif command -v firewall-cmd &> /dev/null; then
    echo "检测到firewalld"
    echo "开放必要端口..."

    firewall-cmd --permanent --add-port=8001/tcp 2>/dev/null
    firewall-cmd --permanent --add-port=80/tcp 2>/dev/null
    firewall-cmd --permanent --add-port=443/tcp 2>/dev/null
    firewall-cmd --reload 2>/dev/null

    echo "✓ 防火墙规则已更新"
else
    echo "⚠ 未检测到防火墙，请手动开放端口: 80, 443, 8001"
fi

# 测试服务
echo ""
echo "======================================"
echo "测试服务..."
echo "======================================"

echo "测试后端健康检查..."
HEALTH_CHECK=$(curl -s http://localhost:8001/api/health)

if [ "$HEALTH_CHECK" = '{"status": "ok"}' ]; then
    echo "✓ 后端服务正常"
else
    echo "⚠ 后端服务可能有问题"
    echo "响应: $HEALTH_CHECK"
fi

echo ""
echo "======================================"
echo "配置完成！"
echo "======================================"

echo ""
echo "部署信息:"
echo "  后端API地址: http://$PUBLIC_IP:8001"
echo "  前端文件位置: $(pwd)/dist"
echo "  后端日志: $(dirname "$0")/logs/app_backend.log"
echo ""
echo "后续步骤:"
echo "  1. 部署前端文件到您的Web服务器 (dist目录)"
echo "  2. 如果使用云服务器，请在控制台开放端口: 80, 443, 8001"
echo "  3. 访问 http://$PUBLIC_IP 测试"
echo ""
echo "推荐: 使用Nginx作为Web服务器和反向代理"
echo "  详见: docs/PUBLIC_DEPLOYMENT.md"
echo ""

read -p "是否安装Nginx并配置反向代理? (y/n): " install_nginx

if [ "$install_nginx" = "y" ]; then
    echo "正在安装Nginx..."

    # 根据系统选择安装命令
    if command -v apt-get &> /dev/null; then
        apt-get update
        apt-get install -y nginx
    elif command -v yum &> /dev/null; then
        yum install -y nginx
    else
        echo "⚠ 无法自动安装Nginx，请手动安装"
        exit 0
    fi

    # 创建Nginx配置
    NGINX_CONF="/etc/nginx/sites-available/lingzhi-ecosystem"
    DIST_PATH="$(pwd)/dist"

    cat > $NGINX_CONF <<EOF
server {
    listen 80;
    server_name $PUBLIC_IP;

    # 前端静态文件
    location / {
        root $DIST_PATH;
        try_files \$uri \$uri/ /index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    # 日志
    access_log /var/log/nginx/lingzhi-ecosystem-access.log;
    error_log /var/log/nginx/lingzhi-ecosystem-error.log;
}
EOF

    # 启用配置
    ln -sf $NGINX_CONF /etc/nginx/sites-enabled/

    # 删除默认配置（可选）
    rm -f /etc/nginx/sites-enabled/default

    # 测试配置
    nginx -t

    if [ $? -eq 0 ]; then
        # 重启Nginx
        systemctl restart nginx

        # 开机自启
        systemctl enable nginx

        echo "✓ Nginx已配置并启动"
        echo ""
        echo "现在访问 http://$PUBLIC_IP 即可使用应用"
    else
        echo "✗ Nginx配置测试失败"
        exit 1
    fi
fi

echo ""
echo "======================================"
echo "配置完成！"
echo "======================================"
