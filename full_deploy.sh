#!/bin/bash

echo "========================================"
echo "🚀 生态之梦风格 - 完整闭环部署"
echo "========================================"
echo ""

# 步骤1：修复Nginx配置
echo "步骤1：修复Nginx配置..."
cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup.$(date +%Y%m%d_%H%M%S)

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

    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
        index index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

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

    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        root /var/www/frontend;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }
}
NGINX_CONFIG

echo "✅ Nginx配置已更新"

# 步骤2：测试Nginx配置
echo "步骤2：测试Nginx配置..."
nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx配置测试失败"
    exit 1
fi
echo "✅ Nginx配置测试通过"

# 步骤3：下载并部署前端文件
echo "步骤3：下载并部署前端文件..."
cd /root

# 下载构建产物
wget -O public.tar.gz "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/public_v3.tar_3e884757.gz?sign=1770371205-4fbb370610-0-b96757292bda4487a3ad4b530db38a80f16e4c7f2f747392da7addc15d0bcd7a" -q --show-progress

if [ $? -ne 0 ]; then
    echo "❌ 下载失败"
    exit 1
fi

echo "✅ 下载完成"

# 清空并部署
rm -rf /var/www/frontend/*
tar -xzf public.tar.gz -C /var/www/frontend/

if [ $? -ne 0 ]; then
    echo "❌ 解压失败"
    exit 1
fi

echo "✅ 解压完成"

# 设置权限
chown -R root:root /var/www/frontend
chmod -R 755 /var/www/frontend

echo "✅ 权限设置完成"

# 清理临时文件
rm -f public.tar.gz

# 步骤4：重启Nginx
echo "步骤4：重启Nginx..."
systemctl restart nginx

if [ $? -ne 0 ]; then
    echo "❌ Nginx重启失败"
    exit 1
fi

echo "✅ Nginx已重启"

# 步骤5：验证部署
echo ""
echo "========================================"
echo "步骤5：验证部署"
echo "========================================"
echo ""

echo "前端目录内容："
ls -lh /var/www/frontend/
echo ""

echo "Assets目录内容："
ls -lh /var/www/frontend/assets/ 2>&1 || echo "assets目录不存在"
echo ""

echo "index.html 前20行："
head -20 /var/www/frontend/index.html
echo ""

echo "Nginx状态："
systemctl status nginx --no-pager -l | head -15
echo ""

echo "========================================"
echo "✅ 部署完成！"
echo "========================================"
echo ""
echo "📱 访问地址: https://meiyueart.com"
echo "💡 请清除浏览器缓存后访问"
echo ""
echo "清除缓存方法："
echo "  - Windows: Ctrl + Shift + R"
echo "  - Mac: Cmd + Shift + R"
echo "  - 或者使用浏览器无痕模式"
echo ""
echo "🎯 预期效果："
echo "  ✅ 绿色→琥珀金渐变背景"
echo "  ✅ 100价值确定性/T+1快速到账/0手续费（光扫动画）"
echo "  ✅ 登录和微信登录双按钮"
echo "  ✅ 忘记密码功能"
echo ""
echo "========================================"
