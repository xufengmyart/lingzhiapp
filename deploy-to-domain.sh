#!/bin/bash

# 部署到 meiyueart.com 域名

set -e

# 配置
PROJECT_PATH="/workspace/projects"
BUILD_DIR="$PROJECT_PATH/public"
SERVER_USER="root"
SERVER_HOST="123.56.142.143"
SERVER_PASSWORD="Meiyue@root123"
SERVER_PATH="/var/www/html"
DOMAIN="meiyueart.com"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "=========================================="
echo "部署到 $DOMAIN"
echo "=========================================="
echo ""

# 1. 检查构建目录
echo -e "${BLUE}[1/5]${NC} 检查构建目录..."
if [ ! -d "$BUILD_DIR" ]; then
    echo -e "${RED}错误${NC}: 构建目录不存在: $BUILD_DIR"
    echo "请先运行: cd web-app && npm run build"
    exit 1
fi

if [ ! -f "$BUILD_DIR/index.html" ]; then
    echo -e "${RED}错误${NC}: index.html 不存在"
    echo "请先运行: cd web-app && npm run build"
    exit 1
fi

echo -e "${GREEN}✓${NC} 构建目录检查通过"
echo ""

# 2. 显示构建文件列表
echo -e "${BLUE}[2/5]${NC} 构建文件列表..."
echo ""
ls -lh "$BUILD_DIR"
echo ""

# 3. 测试服务器连接
echo -e "${BLUE}[3/5]${NC} 测试服务器连接..."
export SSHPASS="$SERVER_PASSWORD"
if sshpass -e ssh -o StrictHostKeyChecking=no -o ConnectTimeout=10 "$SERVER_USER@$SERVER_HOST" "echo '连接成功'" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} 服务器连接成功"
else
    echo -e "${RED}✗${NC} 服务器连接失败"
    echo "请检查网络和服务器配置"
    exit 1
fi
unset SSHPASS
echo ""

# 4. 备份当前版本
echo -e "${BLUE}[4/5]${NC} 备份当前版本..."
export SSHPASS="$SERVER_PASSWORD"
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "mkdir -p $SERVER_PATH/backup && cp -r $SERVER_PATH/* $SERVER_PATH/backup/backup-$(date +%Y%m%d-%H%M%S)/ 2>/dev/null || echo '首次部署，无需备份'"
echo -e "${GREEN}✓${NC} 备份完成"
unset SSHPASS
echo ""

# 5. 部署到服务器
echo -e "${BLUE}[5/5]${NC} 部署到服务器..."
echo "正在上传文件..."
export SSHPASS="$SERVER_PASSWORD"

# 使用 rsync 同步文件
rsync -avz --delete \
    -e "sshpass -e ssh -o StrictHostKeyChecking=no" \
    "$BUILD_DIR/" \
    "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓${NC} 文件上传成功"
else
    echo -e "${RED}✗${NC} 文件上传失败"
    exit 1
fi
unset SSHPASS
echo ""

# 6. 重启 Nginx
echo -e "${BLUE}[6/6]${NC} 重启 Nginx..."
export SSHPASS="$SERVER_PASSWORD"
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "systemctl reload nginx"
echo -e "${GREEN}✓${NC} Nginx 已重启"
unset SSHPASS
echo ""

# 完成
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "🌐 访问地址:"
echo "   - http://$DOMAIN"
echo "   - http://$SERVER_HOST"
echo ""
echo "📱 移动端访问:"
echo "   - 在手机浏览器中访问 $DOMAIN"
echo "   - 添加到主屏幕以获得更好的体验"
echo ""
echo "🔧 管理:"
echo "   - 后台管理: http://$DOMAIN/admin"
echo ""
echo "✨ 祝你使用愉快！"
echo ""
