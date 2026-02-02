#!/bin/bash

# 云服务器自动修复脚本
# 用于修复连接被拒绝的问题

set -e

CLOUD_SERVER="123.56.142.143"

echo "========================================="
echo "  云服务器自动修复"
echo "========================================="
echo ""

# 检查是否可以SSH连接
echo "检查SSH连接..."
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes root@${CLOUD_SERVER} "echo 'SSH连接成功'" 2>/dev/null; then
    echo "❌ SSH连接失败，请检查SSH密钥配置"
    echo "提示：使用 ssh-copy-id root@${CLOUD_SERVER} 配置密钥"
    exit 1
fi
echo "✓ SSH连接正常"
echo ""

# 在服务器上执行修复
ssh root@${CLOUD_SERVER} << 'ENDSSH'

echo "========================================="
echo "步骤 1/6: 关闭防火墙"
echo "========================================="

# 关闭firewalld
if command -v systemctl &> /dev/null; then
    systemctl stop firewalld 2>/dev/null || true
    systemctl disable firewalld 2>/dev/null || true
    echo "✓ Firewalld已关闭"
fi

# 清空iptables规则
if command -v iptables &> /dev/null; then
    iptables -F 2>/dev/null || true
    iptables -X 2>/dev/null || true
    echo "✓ Iptables规则已清空"
fi

echo ""
echo "========================================="
echo "步骤 2/6: 安装Nginx"
echo "========================================="

if ! command -v nginx &> /dev/null; then
    yum install -y nginx
    echo "✓ Nginx已安装"
else
    echo "✓ Nginx已存在"
fi

echo ""
echo "========================================="
echo "步骤 3/6: 配置Nginx"
echo "========================================="

# 创建Nginx配置
cat > /etc/nginx/conf.d/lingzhi-ecosystem.conf << 'NGINX_CONF'
server {
    listen 80;
    server_name _;

    # 前端静态文件
    location / {
        root /root/lingzhi-ecosystem/web-app-dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_CONF

echo "✓ Nginx配置已创建"

# 测试配置
nginx -t || echo "⚠️ Nginx配置测试失败"

echo ""
echo "========================================="
echo "步骤 4/6: 部署项目文件"
echo "========================================="

# 创建项目目录
mkdir -p /root/lingzhi-ecosystem
mkdir -p /root/lingzhi-ecosystem/web-app-dist
mkdir -p /root/lingzhi-ecosystem/admin-backend

# 检查是否有前端文件
if [ ! -f "/root/lingzhi-ecosystem/web-app-dist/index.html" ]; then
    echo "⚠️ 未找到前端文件，需要先上传前端构建产物"
    echo "提示：执行 ./scripts/deploy_to_cloud.sh 上传完整项目"
else
    echo "✓ 前端文件已存在"
fi

echo ""
echo "========================================="
echo "步骤 5/6: 启动后端服务"
echo "========================================="

# 检查Python后端
if [ -f "/root/lingzhi-ecosystem/admin-backend/app.py" ]; then
    # 停止旧进程
    pkill -f "python.*app.py" 2>/dev/null || true
    sleep 1

    # 启动新进程
    cd /root/lingzhi-ecosystem/admin-backend
    nohup python app.py > /tmp/backend.log 2>&1 &
    sleep 2

    # 检查服务状态
    if pgrep -f "python.*app.py" > /dev/null; then
        echo "✓ Python后端服务已启动"
    else
        echo "✗ Python后端服务启动失败"
        echo "查看日志: tail -f /tmp/backend.log"
    fi
else
    echo "⚠️ 未找到后端代码，需要先上传"
fi

echo ""
echo "========================================="
echo "步骤 6/6: 启动Nginx"
echo "========================================="

# 启动Nginx
systemctl start nginx
systemctl enable nginx

# 检查Nginx状态
if systemctl is-active --quiet nginx; then
    echo "✓ Nginx已启动"
else
    echo "✗ Nginx启动失败"
    systemctl status nginx
fi

echo ""
echo "========================================="
echo "修复完成！"
echo "========================================="
echo ""
echo "检查端口监听:"
netstat -tlnp 2>/dev/null | grep -E ":80 |:8001 " || ss -tlnp 2>/dev/null | grep -E ":80 |:8001 "

echo ""
echo "测试本地访问:"
curl -I http://127.0.0.1:80 --connect-timeout 2 2>/dev/null | head -1 || echo "80端口无法访问"
curl -I http://127.0.0.1:8001/api/login --connect-timeout 2 2>/dev/null | head -1 || echo "8001端口无法访问"

echo ""
echo "下一步："
echo "1. 在阿里云控制台开放80端口"
echo "2. 访问 http://$(hostname -I | awk '{print $1}')"
echo ""

ENDSSH

echo ""
echo "========================================="
echo "修复脚本执行完成"
echo "========================================="
