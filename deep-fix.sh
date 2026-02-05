#!/bin/bash
# ==========================================
#  深度诊断和修复脚本
#  在服务器上执行此脚本
# ==========================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  深度诊断和修复${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

FRONTEND_DIR="/var/www/frontend"
NGINX_CONF="/etc/nginx/sites-enabled/meiyueart"

# ========== 诊断阶段 ==========
echo -e "${BLUE}【阶段1: 深度诊断】${NC}"
echo "----------------------------------------"

# 检查1: index.html内容
echo "检查1: index.html内容"
if [ -f "$FRONTEND_DIR/index.html" ]; then
    HAS_ROOT=$(grep -c '<div id="root">' "$FRONTEND_DIR/index.html" || echo 0)
    HAS_JS=$(grep -c 'src="assets/index-.*\.js"' "$FRONTEND_DIR/index.html" || echo 0)
    HAS_CSS=$(grep -c 'href="assets/index-.*\.css"' "$FRONTEND_DIR/index.html" || echo 0)

    echo "  - root元素: $HAS_ROOT"
    echo "  - JS引用: $HAS_JS"
    echo "  - CSS引用: $HAS_CSS"

    if [ "$HAS_ROOT" -eq 0 ]; then
        echo -e "  ${RED}✗${NC} index.html不包含root元素"
        HAS_ISSUE=1
    fi
    if [ "$HAS_JS" -eq 0 ]; then
        echo -e "  ${RED}✗${NC} index.html不包含JS引用"
        HAS_ISSUE=1
    fi
else
    echo -e "  ${RED}✗${NC} index.html不存在"
    HAS_ISSUE=1
fi

# 检查2: JS文件
echo ""
echo "检查2: JS文件"
if [ -f "$FRONTEND_DIR/assets/index-CkydMeua.js" ]; then
    JS_SIZE=$(ls -lh "$FRONTEND_DIR/assets/index-CkydMeua.js" | awk '{print $5}')
    echo -e "  ${GREEN}✓${NC} index-CkydMeua.js存在 ($JS_SIZE)"
else
    echo -e "  ${RED}✗${NC} index-CkydMeua.js不存在"
    HAS_ISSUE=1
fi

# 检查3: Nginx配置
echo ""
echo "检查3: Nginx配置"
if grep -q "try_files.*index.html" "$NGINX_CONF" 2>/dev/null; then
    echo -e "  ${GREEN}✓${NC} Nginx配置包含try_files"
else
    echo -e "  ${RED}✗${NC} Nginx配置缺少try_files"
    HAS_ISSUE=1
fi

# ========== 修复阶段 ==========
echo ""
echo -e "${BLUE}【阶段2: 自动修复】${NC}"
echo "----------------------------------------"

if [ -n "$HAS_ISSUE" ]; then
    echo "发现${RED}问题${NC}，开始修复..."
else
    echo -e "${GREEN}未发现问题，进行验证性修复...${NC}"
fi

# 修复1: 强制重新部署
echo ""
echo "修复1: 强制重新部署前端文件"

# 下载
mkdir -p /root
cd /root
rm -f dream.tar.gz

echo "  下载构建产物..."
wget -q --show-progress https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38 -O dream.tar.gz

if [ -f "/root/dream.tar.gz" ]; then
    SIZE=$(ls -lh /root/dream.tar.gz | awk '{print $5}')
    echo -e "  ${GREEN}✓${NC} 下载完成 ($SIZE)"
else
    echo -e "  ${RED}✗${NC} 下载失败"
    exit 1
fi

# 部署
echo "  部署到目标目录..."
rm -rf "$FRONTEND_DIR"/*
mkdir -p /tmp/dream-final
tar -xzf /root/dream.tar.gz -C /tmp/dream-final

# 检查解压结果
if [ ! -d "/tmp/dream-final" ] || [ -z "$(ls -A /tmp/dream-final)" ]; then
    echo -e "  ${RED}✗${NC} 解压失败或文件为空"
    exit 1
fi

cp -r /tmp/dream-final/* "$FRONTEND_DIR"/
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
rm -rf /tmp/dream-final

# 检查关键文件
if [ -f "$FRONTEND_DIR/index.html" ]; then
    echo -e "  ${GREEN}✓${NC} index.html已部署"
else
    echo -e "  ${RED}✗${NC} index.html部署失败"
    exit 1
fi

# 修复2: 强制更新Nginx配置
echo ""
echo "修复2: 强制更新Nginx配置"

cat > "$NGINX_CONF" << 'EOF'
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

echo -e "  ${GREEN}✓${NC} Nginx配置已更新"

# 测试Nginx配置
if nginx -t 2>&1; then
    echo -e "  ${GREEN}✓${NC} Nginx配置测试通过"
else
    echo -e "  ${RED}✗${NC} Nginx配置测试失败"
    exit 1
fi

# 修复3: 重启Nginx
echo ""
echo "修复3: 重启Nginx"
systemctl reload nginx
if systemctl is-active --quiet nginx; then
    echo -e "  ${GREEN}✓${NC} Nginx已重启"
else
    echo -e "  ${RED}✗${NC} Nginx重启失败"
    exit 1
fi

# 修复4: 检查文件权限
echo ""
echo "修复4: 检查文件权限"
chmod -R 755 "$FRONTEND_DIR"
chown -R root:root "$FRONTEND_DIR"
echo -e "  ${GREEN}✓${NC} 权限已设置"

# ========== 最终验证 ==========
echo ""
echo -e "${BLUE}【阶段3: 最终验证】${NC}"
echo "----------------------------------------"

echo ""
echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$' | awk '{print "  " $9 " (" $5 ")"}' || echo "  未找到JS/CSS文件"

echo ""
echo "index.html详细检查："

# 检查root元素
if grep -q '<div id="root">' "$FRONTEND_DIR/index.html"; then
    echo -e "  ${GREEN}✓${NC} <div id=\"root\"> 存在"
else
    echo -e "  ${RED}✗${NC} <div id=\"root\"> 不存在"
fi

# 检查JS引用
JS_LINE=$(grep -o 'src="assets/index-[^"]*\.js"' "$FRONTEND_DIR/index.html" | head -1)
if [ -n "$JS_LINE" ]; then
    echo -e "  ${GREEN}✓${NC} JS引用: $JS_LINE"
    # 检查文件是否存在
    JS_FILE=$(echo $JS_LINE | sed 's/src="//;s/"//')
    if [ -f "$FRONTEND_DIR/$JS_FILE" ]; then
        JS_SIZE=$(ls -lh "$FRONTEND_DIR/$JS_FILE" | awk '{print $5}')
        echo -e "    ${GREEN}✓${NC} 文件存在 ($JS_SIZE)"
    else
        echo -e "    ${RED}✗${NC} 文件不存在"
    fi
else
    echo -e "  ${RED}✗${NC} JS引用未找到"
fi

# 检查CSS引用
CSS_LINE=$(grep -o 'href="assets/index-[^"]*\.css"' "$FRONTEND_DIR/index.html" | head -1)
if [ -n "$CSS_LINE" ]; then
    echo -e "  ${GREEN}✓${NC} CSS引用: $CSS_LINE"
    # 检查文件是否存在
    CSS_FILE=$(echo $CSS_LINE | sed 's/href="//;s/"//')
    if [ -f "$FRONTEND_DIR/$CSS_FILE" ]; then
        CSS_SIZE=$(ls -lh "$FRONTEND_DIR/$CSS_FILE" | awk '{print $5}')
        echo -e "    ${GREEN}✓${NC} 文件存在 ($CSS_SIZE)"
    else
        echo -e "    ${RED}✗${NC} 文件不存在"
    fi
else
    echo -e "  ${RED}✗${NC} CSS引用未找到"
fi

# 检查是否有开发模式引用
if grep -q 'src="/src/main.tsx"' "$FRONTEND_DIR/index.html"; then
    echo -e "  ${RED}✗${NC} 警告：包含开发模式引用 /src/main.tsx"
    echo -e "  ${YELLOW}⚠${NC} 这会导致页面空白，需要修复"
fi

echo ""
echo "=========================================="
echo "  修复完成"
echo "=========================================="
echo ""

echo "如果页面仍然空白，请检查浏览器控制台（F12）："
echo "  1. 打开开发者工具（F12）"
echo "  2. 查看 Console 标签页的错误信息"
echo "  3. 查看 Network 标签页的文件加载状态"
echo ""

echo "访问地址："
echo -e "  🎨 ${GREEN}https://meiyueart.com/dream-selector${NC}"
echo ""
