#!/bin/bash
# ==========================================
#  紧急修复 - 重新部署文件 + 修复Nginx冲突
#  在服务器上执行此脚本
# ==========================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  紧急修复 - 重新部署 + Nginx冲突修复${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
TAR_FILE="/root/dream.tar.gz"
DOWNLOAD_URL="https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38"

# 步骤1：检查并删除冲突的Nginx配置
echo -e "${BLUE}步骤 1/6: 修复Nginx配置冲突${NC}"
echo "  检查所有Nginx配置文件..."
find /etc/nginx/sites-enabled -name "*" -type f | while read file; do
    echo "  - $file"
done

echo "  删除所有配置文件..."
rm -f /etc/nginx/sites-enabled/*
echo -e "  ${GREEN}✓${NC} 已清空配置文件"

# 步骤2：创建新的Nginx配置
echo ""
echo -e "${BLUE}步骤 2/6: 创建Nginx配置${NC}"
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
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
echo -e "  ${GREEN}✓${NC} Nginx配置已创建"

# 步骤3：测试Nginx配置
echo ""
echo -e "${BLUE}步骤 3/6: 测试Nginx配置${NC}"
if nginx -t 2>&1; then
    echo -e "  ${GREEN}✓${NC} 配置测试通过"
else
    echo -e "  ${RED}✗${NC} 配置测试失败"
    exit 1
fi

# 步骤4：检查并下载构建产物
echo ""
echo -e "${BLUE}步骤 4/6: 检查并下载构建产物${NC}"
if [ -f "$TAR_FILE" ]; then
    SIZE=$(ls -lh "$TAR_FILE" | awk '{print $5}')
    echo -e "  ${GREEN}✓${NC} 文件已存在 ($SIZE)"
else
    echo "  正在下载..."
    cd /root
    wget -q --show-progress "$DOWNLOAD_URL" -O "$TAR_FILE"
    SIZE=$(ls -lh "$TAR_FILE" | awk '{print $5}')
    echo -e "  ${GREEN}✓${NC} 下载完成 ($SIZE)"
fi

# 步骤5：部署文件
echo ""
echo -e "${BLUE}步骤 5/6: 部署文件${NC}"
echo "  清空目标目录..."
rm -rf "$FRONTEND_DIR"/*
mkdir -p "$FRONTEND_DIR"

echo "  解压并部署..."
mkdir -p /tmp/dream-final
tar -xzf "$TAR_FILE" -C /tmp/dream-final
cp -r /tmp/dream-final/public/* "$FRONTEND_DIR"/
rm -rf /tmp/dream-final

# 设置权限
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"

# 检查文件
if [ -f "$FRONTEND_DIR/index.html" ]; then
    echo -e "  ${GREEN}✓${NC} index.html 已部署"
else
    echo -e "  ${RED}✗${NC} index.html 部署失败"
    exit 1
fi

# 检查assets目录
if [ -d "$FRONTEND_DIR/assets" ]; then
    ASSET_COUNT=$(ls -1 "$FRONTEND_DIR/assets" | wc -l)
    echo -e "  ${GREEN}✓${NC} assets 目录有 $ASSET_COUNT 个文件"
else
    echo -e "  ${RED}✗${NC} assets 目录不存在"
    exit 1
fi

# 步骤6：重启Nginx
echo ""
echo -e "${BLUE}步骤 6/6: 重启Nginx${NC}"
systemctl reload nginx
if systemctl is-active --quiet nginx; then
    echo -e "  ${GREEN}✓${NC} Nginx已重启"
else
    echo -e "  ${RED}✗${NC} Nginx重启失败"
    exit 1
fi

# 验证
echo ""
echo "=========================================="
echo "  验证部署结果"
echo "=========================================="
echo ""

echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$' | awk '{print "  " $9 " (" $5 ")"}' || echo "  未找到JS/CSS文件"

echo ""
echo "index.html引用："
if [ -f "$FRONTEND_DIR/index.html" ]; then
    JS_REF=$(grep -o 'src="/assets/index-[^"]*\.js"' "$FRONTEND_DIR/index.html" | head -1)
    CSS_REF=$(grep -o 'href="/assets/index-[^"]*\.css"' "$FRONTEND_DIR/index.html" | head -1)
    echo "  JS引用: $JS_REF"
    echo "  CSS引用: $CSS_REF"
else
    echo "  index.html 不存在"
fi

echo ""
echo "=========================================="
echo "  ✅ 修复完成"
echo "=========================================="
echo ""
echo -e "  🎨 ${GREEN}https://meiyueart.com/dream-selector${NC}"
echo ""
echo "📝 重要："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 访问页面并测试"
echo "  3. 检查浏览器Network标签，应该加载 index-CkydMeua.js"
echo ""
