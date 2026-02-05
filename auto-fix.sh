#!/bin/bash
# ==========================================
#  自动化修复脚本 - Nginx配置 + 重新部署
#  在服务器上执行此脚本
# ==========================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  自动修复 - Nginx配置 + 重新部署${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
NGINX_CONF="/etc/nginx/sites-enabled/meiyueart"
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"

# 步骤1：备份Nginx配置
echo -e "${BLUE}步骤 1/5: 备份Nginx配置${NC}"
if [ -f "$NGINX_CONF" ]; then
    cp "$NGINX_CONF" "${NGINX_CONF}.backup.$(date +%Y%m%d_%H%M%S)"
    echo -e "${GREEN}✓${NC} Nginx配置已备份"
else
    echo -e "${YELLOW}⚠${NC} Nginx配置文件不存在，将创建新配置"
fi

# 步骤2：创建正确的Nginx配置
echo -e "${BLUE}步骤 2/5: 创建Nginx配置${NC}"
cat > "$NGINX_CONF" << 'EOF'
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
    root /var/www/frontend;
    index index.html;

    # React Router支持 - 关键配置
    location / {
        try_files $uri $uri/ /index.html;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
    }

    # 静态资源缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF
echo -e "${GREEN}✓${NC} Nginx配置已更新"

# 步骤3：测试Nginx配置
echo -e "${BLUE}步骤 3/5: 测试Nginx配置${NC}"
if nginx -t 2>&1; then
    echo -e "${GREEN}✓${NC} Nginx配置测试通过"
else
    echo -e "${RED}✗${NC} Nginx配置测试失败"
    exit 1
fi

# 步骤4：重新部署前端
echo -e "${BLUE}步骤 4/5: 重新部署前端${NC}"

# 备份现有文件
if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ]; then
    echo "备份现有文件..."
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR" 2>/dev/null || true
fi

# 下载并部署
echo "下载构建产物..."
mkdir -p /root
cd /root
rm -f dream.tar.gz
wget -q --show-progress https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38 -O dream.tar.gz

if [ -f "/root/dream.tar.gz" ]; then
    SIZE=$(ls -lh /root/dream.tar.gz | awk '{print $5}')
    echo -e "${GREEN}✓${NC} 下载完成 ($SIZE)"
else
    echo -e "${RED}✗${NC} 下载失败"
    exit 1
fi

echo "解压并部署..."
rm -rf "$FRONTEND_DIR"/*
mkdir -p /tmp/dream-deploy
tar -xzf /root/dream.tar.gz -C /tmp/dream-deploy
cp -r /tmp/dream-deploy/* "$FRONTEND_DIR"/
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
rm -rf /tmp/dream-deploy

# 检查关键文件
if [ -f "$FRONTEND_DIR/index.html" ] && grep -q '<div id="root">' "$FRONTEND_DIR/index.html"; then
    echo -e "${GREEN}✓${NC} 前端文件部署成功"
else
    echo -e "${RED}✗${NC} 前端文件部署失败"
    exit 1
fi

# 步骤5：重启服务
echo -e "${BLUE}步骤 5/5: 重启Nginx${NC}"
systemctl reload nginx
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓${NC} Nginx已重启"
else
    echo -e "${YELLOW}⚠${NC} Nginx重启警告"
fi

# 验证
echo ""
echo "=========================================="
echo "  修复结果"
echo "=========================================="
echo ""

echo -e "${GREEN}✓${NC} Nginx配置已更新（支持React Router）"
echo -e "${GREEN}✓${NC} 前端文件已重新部署"
echo -e "${GREEN}✓${NC} Nginx已重启"
echo ""

echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$' || echo "未找到JS/CSS文件"

echo ""
echo "index.html验证："
if [ -f "$FRONTEND_DIR/index.html" ]; then
    echo "  - index.html存在: $(grep -q '<div id="root">' "$FRONTEND_DIR/index.html" && echo "✓" || echo "✗")"
    JS_REF=$(grep -o 'src="assets/index-[^"]*\.js"' "$FRONTEND_DIR/index.html" | head -1)
    if [ -n "$JS_REF" ]; then
        echo "  - JS引用: $JS_REF"
    else
        echo "  - JS引用: ✗ 未找到"
    fi
    CSS_REF=$(grep -o 'href="assets/index-[^"]*\.css"' "$FRONTEND_DIR/index.html" | head -1)
    if [ -n "$CSS_REF" ]; then
        echo "  - CSS引用: $CSS_REF"
    else
        echo "  - CSS引用: ✗ 未找到"
    fi
fi

echo ""
echo "备份位置："
echo "  - Nginx配置: ${NGINX_CONF}.backup.*"
echo "  - 前端文件: $BACKUP_DIR"
echo ""

echo "=========================================="
echo "  访问地址"
echo "=========================================="
echo ""
echo -e "  🎨 梦幻风格选择器: ${GREEN}https://meiyueart.com/dream-selector${NC}"
echo -e "  🔐 梦幻版登录: ${GREEN}https://meiyueart.com/login-full${NC}"
echo -e "  📝 梦幻版注册: ${GREEN}https://meiyueart.com/register-full${NC}"
echo ""

echo "=========================================="
echo "  立即测试"
echo "=========================================="
echo ""
echo "1. 清除浏览器缓存（Ctrl+Shift+R）"
echo "2. 访问: https://meiyueart.com/dream-selector"
echo "3. 如果仍有问题，检查浏览器控制台（F12）"
echo ""
