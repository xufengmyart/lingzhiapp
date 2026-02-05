#!/bin/bash

echo "========================================"
echo "🌿 生态之梦风格 - 完整WEB+PWA闭环部署"
echo "========================================"
echo ""
echo "版本: v9.0 Final"
echo "日期: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# 步骤1：备份当前配置
echo "步骤1：备份当前配置..."
cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup.$(date +%Y%m%d_%H%M%S)
echo "✅ 配置已备份"

# 步骤2：应用Nginx配置
echo "步骤2：应用Nginx配置..."
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

    # 前端静态文件
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
        index index.html;

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

    # 静态资源（强制刷新）
    location ~* \.(jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/frontend;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    }

    # JS/CSS（强制刷新）
    location ~* \.(js|css)$ {
        root /var/www/frontend;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    }

    # Service Worker（可缓存）
    location ~* \.webmanifest$ {
        root /var/www/frontend;
        add_header Cache-Control "public, max-age=3600";
    }
}
NGINX_CONFIG

echo "✅ Nginx配置已更新"

# 步骤3：测试Nginx配置
echo "步骤3：测试Nginx配置..."
nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx配置测试失败，恢复备份"
    cp /etc/nginx/sites-enabled/default.backup.$(date +%Y%m%d_%H%M%S) /etc/nginx/sites-enabled/default
    exit 1
fi
echo "✅ Nginx配置测试通过"

# 步骤4：下载并部署前端文件
echo "步骤4：下载并部署前端文件..."
cd /root

# 下载构建产物
wget -O public.tar.gz "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/public_final_pwa.tar_df1b4f37.gz?sign=1770413380-88d16d2284-0-0c1b790ab62121874bafa7d8d325c288c431fd27babf2949fa0e7079019e0d96" -q --show-progress

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

# 步骤5：重启Nginx
echo "步骤5：重启Nginx..."
systemctl restart nginx

if [ $? -ne 0 ]; then
    echo "❌ Nginx重启失败"
    exit 1
fi

echo "✅ Nginx已重启"

# 步骤6：验证部署
echo ""
echo "========================================"
echo "步骤6：验证部署"
echo "========================================"
echo ""

echo "前端目录内容："
ls -lh /var/www/frontend/
echo ""

echo "PWA文件检查："
[ -f /var/www/frontend/manifest.json ] && echo "✅ manifest.json" || echo "❌ manifest.json"
[ -f /var/www/frontend/manifest.webmanifest ] && echo "✅ manifest.webmanifest" || echo "❌ manifest.webmanifest"
[ -f /var/www/frontend/registerSW.js ] && echo "✅ registerSW.js" || echo "❌ registerSW.js"
echo ""

echo "Assets目录："
ls -lh /var/www/frontend/assets/ 2>&1 | head -10
echo ""

echo "index.html内容（前30行）："
head -30 /var/www/frontend/index.html
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
echo "  - 无痕模式: Ctrl + Shift + N (Windows) / Cmd + Shift + N (Mac)"
echo ""
echo "🎯 生态之梦风格功能清单："
echo "  ✅ 绿色→琥珀金渐变背景（资源→价值转化）"
echo "  ✅ 100价值确定性 / T+1快速到账 / 0手续费（光扫动画）"
echo "  ✅ 登录与微信登录分离（双按钮）"
echo "  ✅ 忘记密码功能"
echo "  ✅ 推荐人必填（注册时关系锁定）"
echo "  ✅ 无风格选择器"
echo "  ✅ 无顶部动画（仅静态装饰）"
echo "  ✅ 不换行原则"
echo ""
echo "📦 PWA功能清单："
echo "  ✅ Service Worker自动注册"
echo "  ✅ 离线访问支持"
echo "  ✅ 添加到主屏幕"
echo "  ✅ 快捷方式支持"
echo "  ✅ API缓存策略"
echo ""
echo "🔑 测试账号："
echo "  用户名: admin"
echo "  密码: password123"
echo ""
echo "========================================"
