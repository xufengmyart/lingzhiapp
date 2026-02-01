#!/bin/bash

# ============================================
# 快速部署脚本
# 用于日常快速部署，只做必要的备份和同步
# ============================================

set -e

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}========================================"
echo -e "  快速部署脚本"
echo -e "========================================${NC}"
echo ""

# 1. 快速备份（仅备份 public 目录）
echo "📦 快速备份..."
BACKUP_NAME="quick-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -czf "backups/$BACKUP_NAME" public/
echo -e "${GREEN}✅ 备份完成${NC}"

# 2. 提交并推送
echo "📤 推送到 GitHub..."
git add -A
git commit -m "deploy: $(date '+%Y-%m-%d %H:%M:%S')" || true
git push origin main
echo -e "${GREEN}✅ 已推送到 GitHub${NC}"

# 3. 同步到服务器
echo "🔄 同步到服务器..."
ssh root@123.56.142.143 "
    cd /var/www/lingzhiapp
    git pull origin main
    sudo systemctl restart nginx
"
echo -e "${GREEN}✅ 同步完成${NC}"

echo ""
echo -e "${GREEN}========================================"
echo -e "  快速部署完成！"
echo -e "========================================${NC}"
