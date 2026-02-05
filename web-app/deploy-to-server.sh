#!/bin/bash

# 一键部署脚本 - 将本地构建产物上传到服务器
# 使用方法: ./deploy-to-server.sh

set -e  # 遇到错误立即退出

echo "=========================================="
echo "  梦幻版页面一键部署脚本"
echo "=========================================="
echo ""

# 配置
SERVER_USER="root"
SERVER_IP="123.56.142.143"
SERVER_PATH="/var/www/frontend"
LOCAL_BUILD="public"

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查构建产物
echo "步骤 1/5: 检查本地构建产物..."
if [ ! -f "$LOCAL_BUILD/index.html" ]; then
    echo -e "${RED}✗${NC} 错误：找不到 index.html"
    echo "请先运行: cd web-app && npm run build"
    exit 1
fi

if [ ! -d "$LOCAL_BUILD/assets" ]; then
    echo -e "${RED}✗${NC} 错误：找不到 assets 目录"
    exit 1
fi

echo -e "${GREEN}✓${NC} 本地构建产物检查通过"
echo ""

# 检查服务器连接
echo "步骤 2/5: 检查服务器连接..."
if ! ssh -o ConnectTimeout=5 $SERVER_USER@$SERVER_IP "echo 'connected'" 2>/dev/null; then
    echo -e "${RED}✗${NC} 错误：无法连接到服务器 $SERVER_IP"
    echo ""
    echo "请检查："
    echo "  1. 服务器IP是否正确: $SERVER_IP"
    echo "  2. SSH密钥是否配置"
    echo "  3. 网络连接是否正常"
    exit 1
fi

echo -e "${GREEN}✓${NC} 服务器连接正常"
echo ""

# 备份服务器现有文件
echo "步骤 3/5: 备份服务器现有文件..."
BACKUP_NAME="frontend.backup.$(date +%Y%m%d_%H%M%S)"
ssh $SERVER_USER@$SERVER_IP "if [ -d '$SERVER_PATH' ]; then cp -r '$SERVER_PATH' '/var/www/$BACKUP_NAME'; else mkdir -p '$SERVER_PATH'; fi"
echo -e "${GREEN}✓${NC} 备份完成: $BACKUP_NAME"
echo ""

# 上传构建产物
echo "步骤 4/5: 上传构建产物到服务器..."
echo "正在上传文件..."

# 使用 tar + ssh 上传（更可靠）
tar -czf - -C "$LOCAL_BUILD" . | ssh $SERVER_USER@$SERVER_IP "tar -xzf - -C '$SERVER_PATH'"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} 上传失败"
    exit 1
fi

echo -e "${GREEN}✓${NC} 上传完成"
echo ""

# 验证上传
echo "验证上传的文件..."
FILES=$(ssh $SERVER_USER@$SERVER_IP "ls -lh '$SERVER_PATH/assets/' | grep -E 'index-.*\\.(js|css)' | wc -l")
if [ "$FILES" -lt 2 ]; then
    echo -e "${YELLOW}⚠${NC} 警告：上传的文件数量不正常（期望至少2个，实际$FILES个）"
else
    echo -e "${GREEN}✓${NC} 文件验证通过"
fi
echo ""

# 重启Nginx
echo "步骤 5/5: 重启Nginx..."
ssh $SERVER_USER@$SERVER_IP "systemctl restart nginx"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Nginx重启失败"
    echo ""
    echo "手动重启命令："
    echo "  ssh $SERVER_USER@$SERVER_IP 'systemctl restart nginx'"
    exit 1
fi

echo -e "${GREEN}✓${NC} Nginx已重启"
echo ""

# 显示结果
echo "=========================================="
echo "  ✅ 部署成功！"
echo "=========================================="
echo ""
echo "服务器上的文件："
ssh $SERVER_USER@$SERVER_IP "ls -lh '$SERVER_PATH/assets/' | grep -E 'index-.*\\.(js|css)'"
echo ""
echo "访问地址："
echo -e "  ${YELLOW}https://meiyueart.com/dream-selector${NC}"
echo -e "  ${YELLOW}https://meiyueart.com/login-full${NC}"
echo -e "  ${YELLOW}https://meiyueart.com/register-full${NC}"
echo ""
echo "提示："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 使用无痕模式测试"
echo "  3. 如果有问题，恢复备份："
echo "     ssh $SERVER_USER@$SERVER_IP 'cp -r /var/www/$BACKUP_NAME/* $SERVER_PATH/'"
echo ""
