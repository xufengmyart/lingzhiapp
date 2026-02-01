#!/bin/bash
# 在服务器上执行此脚本来更新前端文件

echo "=========================================="
echo "灵值生态园 - 前端更新脚本"
echo "=========================================="

# 检查是否以root用户运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用root用户运行此脚本"
    exit 1
fi

# 备份现有文件
echo ""
echo "步骤 1: 备份现有文件..."
BACKUP_DIR="/var/www/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /var/www/html/* "$BACKUP_DIR/"
echo "✅ 备份完成: $BACKUP_DIR"

# 停止服务
echo ""
echo "步骤 2: 停止服务..."
systemctl stop nginx
echo "✅ Nginx 已停止"

# 更新文件（这里需要你手动上传文件到/tmp/public目录）
echo ""
echo "步骤 3: 更新前端文件..."
echo ""
echo "请先执行以下操作："
echo "1. 在本地将 /workspace/projects/public/ 目录打包"
echo "2. 上传到服务器的 /tmp/ 目录（使用 FTP、SFTP 或其他方式）"
echo ""
read -p "文件已上传完成吗？(y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "请先上传文件，然后重新运行此脚本"
    exit 1
fi

# 检查上传的文件
if [ ! -d "/tmp/public" ]; then
    echo "❌ 错误：未找到 /tmp/public 目录"
    echo "请确保已将 public 目录上传到 /tmp/"
    exit 1
fi

# 复制文件
echo ""
echo "正在复制文件..."
rm -rf /var/www/html/*
cp -r /tmp/public/* /var/www/html/
echo "✅ 文件复制完成"

# 设置权限
echo ""
echo "步骤 4: 设置文件权限..."
chown -R www-data:www-data /var/www/html
chmod -R 755 /var/www/html
echo "✅ 权限设置完成"

# 配置Nginx
echo ""
echo "步骤 5: 配置Nginx..."
cat > /etc/nginx/sites-available/meiyueart.com << 'EOF'
server {
    listen 80;
    server_name 123.56.142.143;

    # 前端静态文件
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
EOF

echo "✅ Nginx 配置已更新"

# 测试配置
echo ""
echo "步骤 6: 测试Nginx配置..."
nginx -t
if [ $? -eq 0 ]; then
    echo "✅ Nginx 配置测试通过"
else
    echo "❌ Nginx 配置测试失败"
    echo "正在恢复备份..."
    rm -rf /var/www/html/*
    cp -r "$BACKUP_DIR"/* /var/www/html/
    systemctl start nginx
    echo "已恢复备份"
    exit 1
fi

# 启动服务
echo ""
echo "步骤 7: 启动服务..."
systemctl start nginx
systemctl restart lingzhi-api
echo "✅ 服务已启动"

# 验证
echo ""
echo "步骤 8: 验证服务..."
sleep 2

# 检查Nginx
systemctl status nginx --no-pager -l | grep "Active:"
# 检查后端API
systemctl status lingzhi-api --no-pager -l | grep "Active:"

echo ""
echo "=========================================="
echo "✅ 更新完成！"
echo "=========================================="
echo ""
echo "请访问 http://123.56.142.143 测试"
echo "用户名: 许锋"
echo "密码: 123456"
echo ""
echo "如果还有问题，请查看日志："
echo "  Nginx: tail -f /var/log/nginx/error.log"
echo "  API: tail -f /app/work/logs/bypass/app.log"
