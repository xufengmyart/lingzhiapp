#!/bin/bash
# ==========================================
#  Nginx配置修复 - 禁用缓存，确保加载新文件
#  在服务器上执行此脚本
# ==========================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Nginx配置修复 - 禁用缓存${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 配置
NGINX_CONF="/etc/nginx/sites-enabled/meiyueart"
FRONTEND_DIR="/var/www/frontend"

# 步骤1：备份Nginx配置
echo -e "${BLUE}步骤 1/5: 备份Nginx配置${NC}"
if [ -f "$NGINX_CONF" ]; then
    cp "$NGINX_CONF" "${NGINX_CONF}.cache_fix.$(date +%Y%m%d_%H%M%S)"
    echo -e "  ${GREEN}✓${NC} 已备份"
fi

# 步骤2：创建新的Nginx配置（禁用缓存）
echo ""
echo -e "${BLUE}步骤 2/5: 创建Nginx配置（禁用缓存）${NC}"
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

    # React Router支持
    location / {
        try_files $uri $uri/ /index.html;
        # 禁用所有缓存
        add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # 静态资源也禁用缓存（临时）
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        # 临时禁用缓存，确保加载新文件
        add_header Cache-Control "no-cache, no-store, must-revalidate, max-age=0";
        add_header Pragma "no-cache";
        add_header Expires "0";
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
echo -e "  ${GREEN}✓${NC} 配置已更新（禁用缓存）"

# 步骤3：测试Nginx配置
echo ""
echo -e "${BLUE}步骤 3/5: 测试Nginx配置${NC}"
if nginx -t 2>&1; then
    echo -e "  ${GREEN}✓${NC} 配置测试通过"
else
    echo -e "  ${RED}✗${NC} 配置测试失败"
    cat "$NGINX_CONF"
    exit 1
fi

# 步骤4：重启Nginx
echo ""
echo -e "${BLUE}步骤 4/5: 重启Nginx${NC}"
systemctl reload nginx
if systemctl is-active --quiet nginx; then
    echo -e "  ${GREEN}✓${NC} Nginx已重启"
else
    echo -e "  ${RED}✗${NC} Nginx重启失败"
    exit 1
fi

# 步骤5：验证服务器文件
echo ""
echo -e "${BLUE}步骤 5/5: 验证服务器文件${NC}"
echo ""
echo "服务器上的文件："
ls -lh "$FRONTEND_DIR/assets/index-*.js"
echo ""
echo "index.html引用："
grep -o 'src="/assets/index-[^"]*\.js"' "$FRONTEND_DIR/index.html"
echo ""

# 结果
echo "=========================================="
echo "  ✅ Nginx配置修复完成"
echo "=========================================="
echo ""
echo "修改内容："
echo "  ✓ 禁用所有缓存（Cache-Control: no-cache）"
echo "  ✓ 禁用所有静态资源缓存"
echo "  ✓ 确保每次都加载最新文件"
echo ""
echo "=========================================="
echo "  立即测试"
echo "=========================================="
echo ""
echo -e "  🎨 ${GREEN}https://meiyueart.com/dream-selector${NC}"
echo ""
echo "📝 重要："
echo "  1. 现在访问页面，应该加载 index-CkydMeua.js"
echo "  2. 如果还是空白，请按 F12 查看控制台错误"
echo "  3. 或者使用无痕模式测试"
echo ""
echo "🔧 如果还有问题："
echo "  1. 检查Nginx错误日志: tail -n 20 /var/log/nginx/error.log"
echo "  2. 检查Nginx访问日志: tail -n 20 /var/log/nginx/access.log | grep dream-selector"
echo ""
