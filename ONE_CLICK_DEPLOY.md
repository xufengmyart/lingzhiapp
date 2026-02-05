#!/bin/bash
# ==========================================
# 一键部署命令 - 在服务器上执行
# ==========================================

cat <<'EOF'
==========================================
  梦幻版页面 - 一键部署
==========================================

在服务器上直接执行以下命令：

------------------------------------------
方法1：完整部署脚本（推荐）
------------------------------------------

bash -c "$(cat <<'DEPLOY_SCRIPT'
#!/bin/bash
set -e

FRONTEND_DIR="/var/www/frontend"
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"
URL="https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38"

echo "📥 步骤1/4: 下载构建产物..."
mkdir -p /root
cd /root
if command -v wget &> /dev/null; then
    wget -O dream-frontend-deploy.tar.gz "$URL"
else
    curl -o dream-frontend-deploy.tar.gz "$URL"
fi

echo "💾 步骤2/4: 备份现有文件..."
[ -d "$FRONTEND_DIR" ] && [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ] && cp -r "$FRONTEND_DIR" "$BACKUP_DIR" 2>/dev/null || true

echo "📦 步骤3/4: 部署文件..."
mkdir -p "$FRONTEND_DIR"
rm -rf "$FRONTEND_DIR"/*
mkdir -p /tmp/dream
tar -xzf /root/dream-frontend-deploy.tar.gz -C /tmp/dream
cp -r /tmp/dream/* "$FRONTEND_DIR"/
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
rm -rf /tmp/dream

echo "🔄 步骤4/4: 重启Nginx..."
systemctl restart nginx

echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "📍 访问地址："
echo "   https://meiyueart.com/dream-selector"
echo ""
echo "📝 部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$'
echo ""
echo "提示：清除浏览器缓存 (Ctrl+Shift+R)"
DEPLOY_SCRIPT
)"

------------------------------------------
方法2：直接执行（一行命令）
------------------------------------------

cd /root && wget -O dream.tar.gz "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38" && tar -xzf dream.tar.gz -C /tmp/dream && rm -rf /var/www/frontend/* && cp -r /tmp/dream/* /var/www/frontend/ && chown -R root:root /var/www/frontend && chmod -R 755 /var/www/frontend && systemctl restart nginx && echo "✅ 部署完成！访问: https://meiyueart.com/dream-selector"

==========================================
EOF
