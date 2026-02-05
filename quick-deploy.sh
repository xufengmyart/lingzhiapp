#!/bin/bash
# ==========================================
# 梦幻版页面 - 快速部署脚本
# 在服务器上执行此脚本
# ==========================================

set -e

# 配置
FRONTEND_DIR="/var/www/frontend"
URL="https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38"

echo "🚀 开始部署梦幻版页面..."
echo ""

# 备份
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"
if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ]; then
    echo "💾 备份现有文件..."
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR" 2>/dev/null || true
fi

# 下载
echo "📥 下载构建产物..."
mkdir -p /root
cd /root
if command -v wget &> /dev/null; then
    wget -O dream.tar.gz "$URL"
else
    curl -o dream.tar.gz "$URL"
fi

# 部署
echo "📦 部署文件..."
mkdir -p "$FRONTEND_DIR"
rm -rf "$FRONTEND_DIR"/*
mkdir -p /tmp/dream
tar -xzf dream.tar.gz -C /tmp/dream
cp -r /tmp/dream/* "$FRONTEND_DIR"/
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
rm -rf /tmp/dream

# 重启
echo "🔄 重启Nginx..."
systemctl restart nginx

# 结果
echo ""
echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "📍 访问地址："
echo "   https://meiyueart.com/dream-selector"
echo "   https://meiyueart.com/login-full"
echo "   https://meiyueart.com/register-full"
echo ""
echo "📝 部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$'
echo ""
echo "提示：清除浏览器缓存 (Ctrl+Shift+R)"
