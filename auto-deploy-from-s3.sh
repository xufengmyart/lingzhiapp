#!/bin/bash
# ==========================================
# 梦幻版页面 - 自动部署脚本
# 从对象存储下载并部署
# ==========================================

set -e

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  梦幻版页面 - 自动部署${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"
DOWNLOAD_URL="${1:-https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-deploy.tar_7a6617f3.gz?sign=1770273524-245076a2ff-0-561bd59a69ac1a9cd6cb1c2c1cf230ab25b33fcaf79bf754a78d93f32f21de38}"

# 步骤1：下载
echo -e "${BLUE}步骤 1/5: 下载构建产物${NC}"
echo "----------------------------"

if [ ! -d "/root" ]; then
    mkdir -p /root
fi

cd /root
echo "正在从对象存储下载..."

if command -v wget &> /dev/null; then
    wget -O dream-frontend-deploy.tar.gz "$DOWNLOAD_URL"
elif command -v curl &> /dev/null; then
    curl -o dream-frontend-deploy.tar.gz "$DOWNLOAD_URL"
else
    echo -e "${RED}✗${NC} 错误：找不到wget或curl"
    exit 1
fi

if [ -f "/root/dream-frontend-deploy.tar.gz" ]; then
    SIZE=$(ls -lh /root/dream-frontend-deploy.tar.gz | awk '{print $5}')
    echo -e "${GREEN}✓${NC} 下载完成 (大小: $SIZE)"
else
    echo -e "${RED}✗${NC} 下载失败"
    exit 1
fi
echo ""

# 步骤2：备份
echo -e "${BLUE}步骤 2/5: 备份现有文件${NC}"
echo "----------------------------"

if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ]; then
    echo "备份到: $BACKUP_DIR"
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓${NC} 备份完成"
else
    echo -e "${YELLOW}⚠${NC} 前端目录为空，跳过备份"
fi
echo ""

# 步骤3：解压
echo -e "${BLUE}步骤 3/5: 解压构建产物${NC}"
echo "----------------------------"

mkdir -p "$FRONTEND_DIR"
rm -rf "$FRONTEND_DIR"/*

mkdir -p /tmp/dream-deploy
tar -xzf /root/dream-frontend-deploy.tar.gz -C /tmp/dream-deploy

if [ -f "/tmp/dream-deploy/index.html" ]; then
    echo -e "${GREEN}✓${NC} 解压成功"
else
    echo -e "${RED}✗${NC} 解压失败或文件损坏"
    exit 1
fi
echo ""

# 步骤4：复制
echo -e "${BLUE}步骤 4/5: 部署文件${NC}"
echo "----------------------------"

cp -r /tmp/dream-deploy/* "$FRONTEND_DIR"/
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"

echo -e "${GREEN}✓${NC} 文件部署完成"
rm -rf /tmp/dream-deploy
echo ""

# 步骤5：重启Nginx
echo -e "${BLUE}步骤 5/5: 重启Nginx${NC}"
echo "----------------------------"

if systemctl restart nginx 2>&1; then
    echo -e "${GREEN}✓${NC} Nginx已重启"
else
    echo -e "${YELLOW}⚠${NC} Nginx重启警告"
fi
echo ""

# 验证
echo "=========================================="
echo "  部署结果"
echo "=========================================="
echo ""

if [ -f "$FRONTEND_DIR/index.html" ]; then
    echo -e "${GREEN}✓${NC} index.html 存在"
else
    echo -e "${RED}✗${NC} index.html 不存在"
fi

echo ""
echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$' || echo "未找到JS/CSS文件"

echo ""
echo "备份位置: $BACKUP_DIR"
echo ""

echo "=========================================="
echo "  访问地址"
echo "=========================================="
echo ""
echo -e "  梦幻风格选择器: ${GREEN}https://meiyueart.com/dream-selector${NC}"
echo -e "  梦幻版登录: ${GREEN}https://meiyueart.com/login-full${NC}"
echo -e "  梦幻版注册: ${GREEN}https://meiyueart.com/register-full${NC}"
echo ""

echo "提示："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 使用无痕模式测试"
echo "  3. 如有问题，恢复备份: cp -r $BACKUP_DIR/* $FRONTEND_DIR/"
echo ""
