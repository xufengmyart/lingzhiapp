#!/bin/bash
# ==========================================
#  完整部署脚本 - 一键执行所有操作
#  在服务器上执行此脚本
# ==========================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  完整部署 - 一键执行${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
TAR_FILE="/root/dream.tar.gz"
DOWNLOAD_URL="https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38"

# 步骤1：下载构建产物
echo -e "${BLUE}步骤 1/6: 下载构建产物${NC}"
cd /root
if [ -f "$TAR_FILE" ]; then
    SIZE=$(ls -lh "$TAR_FILE" | awk '{print $5}')
    echo -e "  ${GREEN}✓${NC} 文件已存在 ($SIZE)"
else
    echo "  正在下载..."
    wget -q --show-progress "$DOWNLOAD_URL" -O "$TAR_FILE"
    SIZE=$(ls -lh "$TAR_FILE" | awk '{print $5}')
    echo -e "  ${GREEN}✓${NC} 下载完成 ($SIZE)"
fi

# 步骤2：备份现有文件
echo ""
echo -e "${BLUE}步骤 2/6: 备份现有文件${NC}"
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"
if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ]; then
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR"
    echo -e "  ${GREEN}✓${NC} 已备份到: $BACKUP_DIR"
else
    mkdir -p "$FRONTEND_DIR"
    echo -e "  ${YELLOW}⚠${NC} 目录为空，跳过备份"
fi

# 步骤3：解压并部署
echo ""
echo -e "${BLUE}步骤 3/6: 解压并部署${NC}"
echo "  清空目标目录..."
rm -rf "$FRONTEND_DIR"/*
echo "  解压文件..."
mkdir -p /tmp/dream-final
tar -xzf "$TAR_FILE" -C /tmp/dream-final
echo "  复制文件..."
cp -r /tmp/dream-final/public/* "$FRONTEND_DIR"/
rm -rf /tmp/dream-final
echo -e "  ${GREEN}✓${NC} 部署完成"

# 步骤4：设置权限
echo ""
echo -e "${BLUE}步骤 4/6: 设置权限${NC}"
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
echo -e "  ${GREEN}✓${NC} 权限已设置"

# 步骤5：重启Nginx
echo ""
echo -e "${BLUE}步骤 5/6: 重启Nginx${NC}"
systemctl reload nginx
if systemctl is-active --quiet nginx; then
    echo -e "  ${GREEN}✓${NC} Nginx已重启"
else
    echo -e "  ${RED}✗${NC} Nginx重启失败"
    exit 1
fi

# 步骤6：验证部署
echo ""
echo -e "${BLUE}步骤 6/6: 验证部署${NC}"
echo ""
echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$' | awk '{print "  " $9 " (" $5 ")"}'

echo ""
echo "index.html检查："

# 检查root元素
if grep -q '<div id="root">' "$FRONTEND_DIR/index.html"; then
    echo -e "  ${GREEN}✓${NC} <div id=\"root\"> 存在"
else
    echo -e "  ${RED}✗${NC} <div id=\"root\"> 不存在"
fi

# 检查JS引用
JS_REF=$(grep -o 'src="/assets/index-[^"]*\.js"' "$FRONTEND_DIR/index.html" | head -1)
if [ -n "$JS_REF" ]; then
    echo -e "  ${GREEN}✓${NC} JS引用: $JS_REF"
    JS_FILE=$(echo $JS_REF | sed 's/src="//;s/"//')
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
CSS_REF=$(grep -o 'href="/assets/index-[^"]*\.css"' "$FRONTEND_DIR/index.html" | head -1)
if [ -n "$CSS_REF" ]; then
    echo -e "  ${GREEN}✓${NC} CSS引用: $CSS_REF"
    CSS_FILE=$(echo $CSS_REF | sed 's/href="//;s/"//')
    if [ -f "$FRONTEND_DIR/$CSS_FILE" ]; then
        CSS_SIZE=$(ls -lh "$FRONTEND_DIR/$CSS_FILE" | awk '{print $5}')
        echo -e "    ${GREEN}✓${NC} 文件存在 ($CSS_SIZE)"
    else
        echo -e "    ${RED}✗${NC} 文件不存在"
    fi
else
    echo -e "  ${RED}✗${NC} CSS引用未找到"
fi

# 结果
echo ""
echo "=========================================="
echo "  ✅ 部署完成"
echo "=========================================="
echo ""
echo "备份位置: $BACKUP_DIR"
echo ""
echo "=========================================="
echo "  访问地址（清除缓存后访问）"
echo "=========================================="
echo ""
echo -e "  🎨 ${GREEN}https://meiyueart.com/dream-selector${NC}"
echo -e "  🔐 ${GREEN}https://meiyueart.com/login-full${NC}"
echo -e "  📝 ${GREEN}https://meiyueart.com/register-full${NC}"
echo ""
echo "📝 重要提示："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 或使用无痕模式测试"
echo "  3. 访问页面并检查功能"
echo ""
