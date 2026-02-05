#!/bin/bash

echo "========================================"
echo "🚨 紧急修复403错误"
echo "========================================"
echo ""

# 步骤1：修复文件权限
echo "步骤1：修复文件权限..."
chown -R www-data:www-data /var/www/frontend 2>/dev/null || chown -R nginx:nginx /var/www/frontend 2>/dev/null || chown -R root:root /var/www/frontend
chmod -R 755 /var/www/frontend
chmod -R 644 /var/www/frontend/*.html
chmod -R 644 /var/www/frontend/assets/*
echo "✅ 文件权限已修复"
echo ""

# 步骤2：修复SELinux
echo "步骤2：修复SELinux（如果启用）..."
if command -v getenforce &> /dev/null; then
    SELINUX_STATUS=$(getenforce)
    if [ "$SELINUX_STATUS" = "Enforcing" ]; then
        echo "SELinux已启用，设置HTTP访问权限..."
        setsebool -P httpd_read_user_content 1 2>/dev/null || setsebool -P nginx_read_user_content 1 2>/dev/null
        restorecon -R /var/www/frontend 2>/dev/null
        echo "✅ SELinux已配置"
    else
        echo "✅ SELinux未启用，跳过"
    fi
else
    echo "✅ SELinux未安装，跳过"
fi
echo ""

# 步骤3：应用修复的Nginx配置
echo "步骤3：应用Nginx配置..."
cat > /etc/nginx/sites-enabled/default << 'NGINX_CONFIG'
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com;

    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    # 前端静态文件
    location / {
        root /var/www/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;

        # 安全headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # 禁用缓存
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    # API反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 静态资源
    location ~* \.(jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot|webmanifest)$ {
        root /var/www/frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # JS/CSS
    location ~* \.(js|css)$ {
        root /var/www/frontend;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
NGINX_CONFIG

echo "✅ Nginx配置已更新"
echo ""

# 步骤4：测试Nginx配置
echo "步骤4：测试Nginx配置..."
nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx配置测试失败"
    nginx -t
    exit 1
fi
echo "✅ Nginx配置测试通过"
echo ""

# 步骤5：重启Nginx
echo "步骤5：重启Nginx..."
systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx已重启"
else
    echo "❌ Nginx重启失败"
    systemctl status nginx --no-pager -l | tail -20
    exit 1
fi
echo ""

# 步骤6：启动后端服务
echo "步骤6：启动后端服务..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2

BACKEND_PATH="/root/lingzhi-ecosystem/admin-backend"
if [ -f "$BACKEND_PATH/app.py" ]; then
    cd "$BACKEND_PATH"
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    sleep 5

    if ps aux | grep -v grep | grep -q "python.*app.py"; then
        echo "✅ 后端服务已启动"
    else
        echo "⚠️  后端服务启动失败"
    fi
else
    echo "⚠️  后端文件不存在: $BACKEND_PATH/app.py"
fi
echo ""

# 步骤7：完整测试
echo ""
echo "========================================"
echo "步骤7：完整测试"
echo "========================================"
echo ""

echo "测试1：HTTP访问"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试2：HTTPS访问"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -k https://127.0.0.1/)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试3：外部访问"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://meiyueart.com/)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试4：API状态"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status)
echo "HTTP状态码: $HTTP_CODE"

# 步骤8：显示状态
echo ""
echo "========================================"
echo "步骤8：系统状态"
echo "========================================"
echo ""

echo "Nginx状态："
systemctl status nginx --no-pager -l | head -10
echo ""

echo "前端目录："
ls -ld /var/www/frontend
ls -lh /var/www/frontend/index.html
echo ""

echo "========================================"
echo "✅ 紧急修复完成"
echo "========================================"
echo ""
echo "📱 现在请重新访问："
echo "   - https://meiyueart.com"
echo ""
echo "💡 请清除浏览器缓存："
echo "   - Windows: Ctrl + Shift + R"
echo "   - Mac: Cmd + Shift + R"
echo ""
echo "🔍 如果仍然403，请查看Nginx日志："
echo "   tail -50 /var/log/nginx/error.log"
echo ""
