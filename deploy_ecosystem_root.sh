#!/bin/bash

# 生态之梦风格部署脚本 - 直接替换 meiyueart.com 根目录

echo "🌿 生态之梦风格部署中..."

# 下载最新构建
cd /root
wget -q https://coze-coding-project.tos.coze.site/public_v2.tar_df696dc0.gz -O public.tar.gz

if [ $? -ne 0 ]; then
    echo "❌ 下载失败"
    exit 1
fi

echo "✅ 下载完成"

# 备份旧版本（可选）
# cp -r /var/www/frontend /var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)

# 清空并部署新版本
rm -rf /var/www/frontend/*
tar -xzf public.tar.gz -C /var/www/frontend/

if [ $? -ne 0 ]; then
    echo "❌ 解压失败"
    exit 1
fi

# 设置权限
chown -R root:root /var/www/frontend
chmod -R 755 /var/www/frontend

# 重启 Nginx
systemctl reload nginx

if [ $? -ne 0 ]; then
    echo "❌ Nginx 重启失败"
    exit 1
fi

# 清理
rm -f public.tar.gz

echo "✅ 部署完成！"
echo "📱 访问地址: https://meiyueart.com"
echo "💡 请清除浏览器缓存后访问"
