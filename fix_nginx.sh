#!/bin/bash

echo "🚀 开始完整修复..."

# 备份当前Nginx配置
echo "1. 备份当前Nginx配置..."
cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup.$(date +%Y%m%d_%H%M%S)

# 创建新的Nginx配置
echo "2. 创建新Nginx配置..."
cat > /etc/nginx/sites-enabled/default << 'NGINX_CONFIG'
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 前端静态文件
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
        index index.html;
        
        # 禁用缓存，确保加载新文件
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
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

    # WebSocket支持
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源（强制刷新）
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        root /var/www/frontend;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
NGINX_CONFIG

# 测试Nginx配置
echo "3. 测试Nginx配置..."
nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx配置测试失败"
    exit 1
fi

# 重启Nginx
echo "4. 重启Nginx..."
systemctl restart nginx
if [ $? -ne 0 ]; then
    echo "❌ Nginx重启失败"
    exit 1
fi

# 验证Nginx状态
echo "5. 验证Nginx状态..."
systemctl status nginx --no-pager -l

echo ""
echo "✅ Nginx配置修复完成！"
