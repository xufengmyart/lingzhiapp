#!/bin/bash
# ==========================================
#  紧急修复脚本 - 强制重新部署
#  在服务器上执行此脚本（root用户）
# ==========================================

set -e

echo "=========================================="
echo "  🚨 紧急修复 - 强制重新部署"
echo "=========================================="
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
DOWNLOAD_URL="https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38"

# 步骤1：备份现有文件
echo "步骤1: 备份现有文件..."
BACKUP_DIR="/var/www/frontend.backup.emergency.$(date +%Y%m%d_%H%M%S)"
if [ -d "$FRONTEND_DIR" ]; then
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR" 2>/dev/null || true
    echo "  ✓ 已备份到: $BACKUP_DIR"
else
    mkdir -p "$FRONTEND_DIR"
    echo "  ✓ 创建目录: $FRONTEND_DIR"
fi

# 步骤2：下载构建产物
echo ""
echo "步骤2: 下载构建产物..."
cd /root
rm -f dream.tar.gz

if command -v wget &> /dev/null; then
    wget --progress=bar:force -O dream.tar.gz "$DOWNLOAD_URL" 2>&1 | tail -n 1
else
    curl --progress-bar -o dream.tar.gz "$DOWNLOAD_URL"
fi

if [ -f "/root/dream.tar.gz" ]; then
    SIZE=$(ls -lh /root/dream.tar.gz | awk '{print $5}')
    echo "  ✓ 下载完成 (大小: $SIZE)"
else
    echo "  ✗ 下载失败"
    exit 1
fi

# 步骤3：解压并检查
echo ""
echo "步骤3: 解压并检查..."
rm -rf /tmp/dream-emergency
mkdir -p /tmp/dream-emergency
tar -xzf /root/dream.tar.gz -C /tmp/dream-emergency

# 检查解压结果
if [ ! -f "/tmp/dream-emergency/public/index.html" ]; then
    echo "  ✗ 解压失败，未找到 index.html"
    exit 1
fi
echo "  ✓ 解压成功"

# 检查JS文件
EXPECTED_JS="index-CkydMeua.js"
if [ -f "/tmp/dream-emergency/public/assets/$EXPECTED_JS" ]; then
    JS_SIZE=$(ls -lh "/tmp/dream-emergency/public/assets/$EXPECTED_JS" | awk '{print $5}')
    echo "  ✓ 找到JS文件: $EXPECTED_JS ($JS_SIZE)"
else
    echo "  ✗ 未找到JS文件: $EXPECTED_JS"
    ls -la /tmp/dream-emergency/public/assets/
    exit 1
fi

# 步骤4：强制部署
echo ""
echo "步骤4: 强制部署..."
rm -rf "$FRONTEND_DIR"/*
cp -r /tmp/dream-emergency/public/* "$FRONTEND_DIR"/
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
rm -rf /tmp/dream-emergency

# 步骤5：验证部署
echo ""
echo "步骤5: 验证部署..."

# 检查index.html
if [ -f "$FRONTEND_DIR/index.html" ]; then
    echo "  ✓ index.html 存在"

    # 检查root元素
    if grep -q '<div id="root">' "$FRONTEND_DIR/index.html"; then
        echo "  ✓ root元素存在"
    else
        echo "  ✗ root元素不存在"
        exit 1
    fi

    # 检查JS引用
    JS_REF=$(grep -o 'src="/assets/index-[^"]*\.js"' "$FRONTEND_DIR/index.html" | head -1)
    if [ -n "$JS_REF" ]; then
        echo "  ✓ JS引用: $JS_REF"
    else
        echo "  ✗ JS引用未找到"
        exit 1
    fi
else
    echo "  ✗ index.html 不存在"
    exit 1
fi

# 检查JS文件
if [ -f "$FRONTEND_DIR/assets/$EXPECTED_JS" ]; then
    echo "  ✓ JS文件存在: $EXPECTED_JS"
else
    echo "  ✗ JS文件不存在: $EXPECTED_JS"
    ls -la "$FRONTEND_DIR/assets/"
    exit 1
fi

# 步骤6：重启Nginx
echo ""
echo "步骤6: 重启Nginx..."
systemctl reload nginx
if systemctl is-active --quiet nginx; then
    echo "  ✓ Nginx已重启"
else
    echo "  ✗ Nginx重启失败"
    exit 1
fi

# 最终结果
echo ""
echo "=========================================="
echo "  ✅ 紧急修复完成"
echo "=========================================="
echo ""

echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$' | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "index.html内容："
echo "  - root元素: $(grep -q '<div id="root">' "$FRONTEND_DIR/index.html" && echo '✓' || echo '✗')"
echo "  - JS引用: $(grep -o 'src="/assets/index-[^"]*\.js"' "$FRONTEND_DIR/index.html" | head -1)"
echo "  - CSS引用: $(grep -o 'href="/assets/index-[^"]*\.css"' "$FRONTEND_DIR/index.html" | head -1)"

echo ""
echo "备份位置："
echo "  - $BACKUP_DIR"
echo ""

echo "=========================================="
echo "  立即访问（强制刷新浏览器）"
echo "=========================================="
echo ""
echo "🎨 https://meiyueart.com/dream-selector"
echo ""
echo "📝 重要："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 或使用无痕模式"
echo "  3. 如果还是空白，按 F12 查看控制台错误"
echo ""
