#!/bin/bash
# ==========================================
#  新版本部署 - 3种新梦幻风格
#  在服务器上执行此脚本
# ==========================================

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  新版本部署 - 3种新梦幻风格${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
DOWNLOAD_URL="https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/dream-frontend-v2.tar_b9c91430.gz?sign=1770361288-c2002af984-0-0872739370dd35deafc29529aa8d3317cec3774128c8b544c6e96d99790c65b1"

echo "新梦幻风格："
echo "  🌈 极光之梦 - 绚丽、梦幻、多彩"
echo "  🌸 樱花之梦 - 浪漫、柔美、优雅"
echo "  🌊 海洋之梦 - 宁静、深邃、自由"
echo "  ☁️  云端之梦 - 轻盈、纯净、梦幻"
echo ""

# 步骤1：下载
echo -e "${BLUE}步骤 1/4: 下载新版本${NC}"
cd /root
wget -q --show-progress "$DOWNLOAD_URL" -O dream-v2.tar.gz
SIZE=$(ls -lh dream-v2.tar.gz | awk '{print $5}')
echo -e "  ${GREEN}✓${NC} 下载完成 ($SIZE)"

# 步骤2：备份
echo ""
echo -e "${BLUE}步骤 2/4: 备份现有文件${NC}"
BACKUP_DIR="/var/www/frontend.backup.v2.$(date +%Y%m%d_%H%M%S)"
cp -r "$FRONTEND_DIR" "$BACKUP_DIR" 2>/dev/null || true
echo -e "  ${GREEN}✓${NC} 已备份到: $BACKUP_DIR"

# 步骤3：部署
echo ""
echo -e "${BLUE}步骤 3/4: 部署新版本${NC}"
rm -rf "$FRONTEND_DIR"/*
mkdir -p /tmp/dream-v2
tar -xzf dream-v2.tar.gz -C /tmp/dream-v2
cp -r /tmp/dream-v2/* "$FRONTEND_DIR"/
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
rm -rf /tmp/dream-v2
echo -e "  ${GREEN}✓${NC} 部署完成"

# 步骤4：重启
echo ""
echo -e "${BLUE}步骤 4/4: 重启Nginx${NC}"
systemctl reload nginx
echo -e "  ${GREEN}✓${NC} Nginx已重启"

# 结果
echo ""
echo "=========================================="
echo "  ✅ 新版本部署完成"
echo "=========================================="
echo ""
echo "新增梦幻风格："
echo "  🌸 樱花之梦 - 浪漫、柔美、优雅"
echo "  🌊 海洋之梦 - 宁静、深邃、自由"
echo "  ☁️  云端之梦 - 轻盈、纯净、梦幻"
echo ""
echo "保留风格："
echo "  🌈 极光之梦 - 绚丽、梦幻、多彩"
echo ""
echo -e "访问地址：${GREEN}https://meiyueart.com/dream-selector${NC}"
echo ""
echo "📝 重要：清除浏览器缓存 (Ctrl+Shift+R)"
echo ""
