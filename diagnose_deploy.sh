#!/bin/bash

echo "🔍 诊断部署状态..."

# 检查前端目录
echo "1. 检查 /var/www/frontend/ 目录："
ls -lh /var/www/frontend/ 2>&1 || echo "目录不存在"

# 检查index.html
echo -e "\n2. 检查 index.html："
if [ -f /var/www/frontend/index.html ]; then
    head -20 /var/www/frontend/index.html
else
    echo "index.html 不存在"
fi

# 检查assets
echo -e "\n3. 检查 assets 目录："
ls -lh /var/www/frontend/assets/ 2>&1 || echo "assets 目录不存在"

# 检查Nginx配置
echo -e "\n4. 检查 Nginx 配置："
cat /etc/nginx/sites-enabled/default 2>&1 | grep -A 10 "server {" || cat /etc/nginx/nginx.conf 2>&1 | grep -A 10 "server {"

# 检查Nginx状态
echo -e "\n5. 检查 Nginx 状态："
systemctl status nginx --no-pager -l

echo -e "\n✅ 诊断完成"
