#!/bin/bash
#
# 服务器部署脚本 - 从对象存储下载前端文件并部署
#

set -e

echo "========================================"
echo "🚀 开始部署前端到服务器"
echo "========================================"

# 配置
FRONTEND_DIR="/var/www/frontend"
BUCKET_NAME="coze-coding-project"
STORAGE_PREFIX="frontend/"

# 对象存储文件列表（包含MD5哈希的完整key）
FILES=(
    "apple-touch-icon_a768c0be.svg"
    "icon-192x192_3c3b98e4.svg"
    "icon-512x512_147a2f69.svg"
    "index-BI24OT2H_3cc8cd1e.css"
    "index-C_quYkQi_3e38ec02.js"
    "index_e41fbf49.html"
    "manifest_7017329e.webmanifest"
    "manifest_a8e5ef9d.json"
    "mask-icon_a745323b.svg"
    "registerSW_c677cc83.js"
    "sw_a0fcf211.js"
    "workbox-3896e580_4d882448.js"
)

# 下载URL模板（使用阿里云OSS公开访问）
DOWNLOAD_URL="https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475"

echo ""
echo "步骤1：备份现有文件（如果存在）..."
if [ -d "${FRONTEND_DIR}" ]; then
    BACKUP_DIR="${FRONTEND_DIR}.backup.$(date +%Y%m%d_%H%M%S)"
    cp -r "${FRONTEND_DIR}" "${BACKUP_DIR}" || echo "备份失败，继续部署"
    echo "✅ 已备份到: ${BACKUP_DIR}"
fi

echo ""
echo "步骤2：清理并重建目录..."
rm -rf "${FRONTEND_DIR:?}"/*
mkdir -p "${FRONTEND_DIR}/assets"
echo "✅ 目录已清理"

echo ""
echo "步骤3：下载文件..."
SUCCESS_COUNT=0
TOTAL_COUNT=${#FILES[@]}

for file in "${FILES[@]}"; do
    echo -n "  📥 下载 ${file}... "

    # 确定目标路径
    if [[ $file == index_* ]]; then
        target_path="${FRONTEND_DIR}/index.html"
    elif [[ $file == manifest* ]]; then
        target_path="${FRONTEND_DIR}/$(echo $file | sed 's/_[a-f0-9]*\.\([^.]*\)$/.\1/')"
    elif [[ $file == sw_* || $file == workbox-* || $file == registerSW* ]]; then
        target_path="${FRONTEND_DIR}/$(echo $file | sed 's/_[a-f0-9]*\.\([^.]*\)$/.\1/')"
    elif [[ $file == icon-* ]]; then
        target_path="${FRONTEND_DIR}/$(echo $file | sed 's/_[a-f0-9]*\.\([^.]*\)$/.\1/')"
    else
        target_path="${FRONTEND_DIR}/${file}"
    fi

    # 下载文件
    download_url="${DOWNLOAD_URL}/${file}"
    if curl -fsSL "${download_url}" -o "${target_path}"; then
        echo "✅"
        SUCCESS_COUNT=$((SUCCESS_COUNT + 1))
    else
        echo "❌ 失败"
    fi
done

echo ""
echo "步骤4：设置文件权限..."
chmod -R 755 "${FRONTEND_DIR}"
find "${FRONTEND_DIR}" -type f -exec chmod 644 {} \;
echo "✅ 权限已设置"

echo ""
echo "步骤5：验证关键文件..."
REQUIRED_FILES=(
    "${FRONTEND_DIR}/index.html"
    "${FRONTEND_DIR}/assets/index-BI24OT2H.css"
    "${FRONTEND_DIR}/assets/index-C_quYkQi.js"
)

ALL_OK=true
for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        size=$(stat -c%s "$file" 2>/dev/null || stat -f%z "$file" 2>/dev/null)
        echo "  ✅ $(basename $file) (${size} bytes)"
    else
        echo "  ❌ $(basename $file) - 缺失！"
        ALL_OK=false
    fi
done

echo ""
echo "步骤6：测试Nginx配置..."
if nginx -t 2>&1 | grep -q "syntax is ok"; then
    echo "✅ Nginx配置正确"
else
    echo "❌ Nginx配置有误"
    nginx -t
fi

echo ""
echo "步骤7：重启Nginx..."
systemctl reload nginx
echo "✅ Nginx已重启"

echo ""
echo "========================================"
echo "📊 部署结果"
echo "========================================"
echo "成功下载: ${SUCCESS_COUNT}/${TOTAL_COUNT} 个文件"
echo "部署目录: ${FRONTEND_DIR}"

if [ "$ALL_OK" = true ]; then
    echo "✅ 所有关键文件都已部署"
else
    echo "⚠️  部分关键文件缺失"
fi

echo ""
echo "========================================"
echo "🎉 部署完成"
echo "========================================"
echo ""
echo "📱 现在请访问："
echo "   - https://meiyueart.com"
echo ""
echo "💡 清除浏览器缓存："
echo "   - Windows: Ctrl + Shift + R"
echo "   - Mac: Cmd + Shift + R"
echo ""
