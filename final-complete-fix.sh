#!/bin/bash
# ==========================================
#  最终修复脚本 - 完整闭环
#  在服务器上执行此脚本
# ==========================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  最终修复 - 完整闭环${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
DOWNLOAD_URL="https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-final.tar_5ae1f596.gz?sign=1770361894-5d60c162c8-0-62abe83e6c040bdd75986d40961f8b4ad20415ecef63837fecc7cdbcbe2968ee"

# 步骤1：下载
echo -e "${BLUE}步骤 1/4: 下载构建产物${NC}"
cd /root
rm -f dream.tar.gz
wget -q --show-progress "$DOWNLOAD_URL" -O dream.tar.gz
SIZE=$(ls -lh dream.tar.gz | awk '{print $5}')
echo -e "  ${GREEN}✓${NC} 下载完成 ($SIZE)"

# 步骤2：部署
echo ""
echo -e "${BLUE}步骤 2/4: 部署文件${NC}"
rm -rf "$FRONTEND_DIR"/*
mkdir -p "$FRONTEND_DIR"
tar -xzf dream.tar.gz -C /tmp/
cp -r /tmp/public/* "$FRONTEND_DIR"/
rm -rf /tmp/public
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
echo -e "  ${GREEN}✓${NC} 部署完成"

# 步骤3：修复Nginx
echo ""
echo -e "${BLUE}步骤 3/4: 修复Nginx配置${NC}"
cat > /etc/nginx/sites-enabled/meiyueart.conf << 'EOF'
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

    root /var/www/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0";
    }

    location ~* \.(js|css)$ {
        add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF
echo -e "  ${GREEN}✓${NC} Nginx配置已修复"

# 步骤4：重启
echo ""
echo -e "${BLUE}步骤 4/4: 重启Nginx${NC}"
nginx -t && systemctl reload nginx
echo -e "  ${GREEN}✓${NC} Nginx已重启"

# 验证
echo ""
echo "=========================================="
echo "  验证结果"
echo "=========================================="
echo ""

echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$' | awk '{print "  " $9 " (" $5 ")"}' || echo "  未找到文件"

echo ""
echo "index.html引用："
if [ -f "$FRONTEND_DIR/index.html" ]; then
    grep -o 'src="/assets/index-[^"]*\.js"' "$FRONTEND_DIR/index.html"
    grep -o 'href="/assets/index-[^"]*\.css"' "$FRONTEND_DIR/index.html"
else
    echo "  index.html不存在"
fi

echo ""
echo "=========================================="
echo "  ✅ 修复完成"
echo "=========================================="
echo ""
echo -e "访问地址：${GREEN}https://meiyueart.com/dream-selector${NC}"
echo ""
echo "新梦幻风格："
echo "  🌈 极光之梦 - 绚丽、梦幻、多彩"
echo "  🌸 樱花之梦 - 浪漫、柔美、优雅"
echo "  🌊 海洋之梦 - 宁静、深邃、自由"
echo "  ☁️  云端之梦 - 轻盈、纯净、梦幻"
echo ""
echo "📝 重要：清除浏览器缓存 (Ctrl+Shift+R)"
echo ""
