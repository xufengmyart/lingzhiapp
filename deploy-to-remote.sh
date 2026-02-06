#!/bin/bash

# ============================================
# 灵值生态园 - 自动部署脚本
# 用途：自动构建并部署到远程服务器
# ============================================

set -e

# 加载环境变量
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "错误：找不到 .env 文件"
    exit 1
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 配置变量
PROJECT_DIR="/workspace/projects"
FRONTEND_DIR="$PROJECT_DIR/web-app"
BUILD_DIR="$PROJECT_DIR/public"
REMOTE_HOST="${SERVER_HOST}"
REMOTE_USER="${SERVER_USER}"
REMOTE_PASSWORD="${SERVER_PASSWORD}"
REMOTE_PATH="${SERVER_PATH}"
BACKUP_DIR="$REMOTE_PATH.backup.$(date +%Y%m%d_%H%M%S)"

# 日志函数
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 开始
clear
echo "=========================================="
echo -e "${PURPLE}灵值生态园 - 自动部署脚本${NC}"
echo "=========================================="
echo ""
echo "项目目录: $PROJECT_DIR"
echo "前端目录: $FRONTEND_DIR"
echo "远程主机: $REMOTE_HOST"
echo "远程用户: $REMOTE_USER"
echo "远程路径: $REMOTE_PATH"
echo "备份路径: $BACKUP_DIR"
echo ""
echo "=========================================="
echo ""

# 安装sshpass（如果未安装）
if ! command -v sshpass &> /dev/null; then
    log "安装 sshpass..."
    apt-get update -qq
    apt-get install -y sshpass > /dev/null 2>&1
    success "✓ sshpass 安装完成"
fi

# ============================================
# 步骤1: 构建前端
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 1/5: 构建前端${NC}"
echo "=========================================="

cd "$FRONTEND_DIR"

log "检查 node_modules..."
if [ ! -d "node_modules" ]; then
    log "安装依赖..."
    npm install --silent --no-audit --no-fund
    success "✓ 依赖安装完成"
else
    log "✓ node_modules 已存在"
fi

log "构建前端..."
npm run build

if [ ! -d "$BUILD_DIR" ]; then
    error "构建失败：找不到构建目录 $BUILD_DIR"
    exit 1
fi

success "✓ 前端构建完成"

# 检查构建产物
if [ ! -f "$BUILD_DIR/index.html" ]; then
    error "构建失败：找不到 $BUILD_DIR/index.html"
    exit 1
fi

echo ""
log "构建产物："
ls -lh "$BUILD_DIR/" | head -20

cd "$PROJECT_DIR"

# ============================================
# 步骤2: 备份远程服务器现有文件
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 2/5: 备份远程服务器文件${NC}"
echo "=========================================="

log "检查远程目录..."
sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no \
    ${REMOTE_USER}@${REMOTE_HOST} \
    "if [ -d '$REMOTE_PATH' ] && [ \"\$(ls -A $REMOTE_PATH 2>/dev/null)\" ]; then mkdir -p $BACKUP_DIR && cp -r $REMOTE_PATH/* $BACKUP_DIR/ && echo '备份完成'; else echo '目录为空或不存在，跳过备份'; fi"

success "✓ 远程备份完成"

# ============================================
# 步骤3: 上传构建产物
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 3/5: 上传构建产物${NC}"
echo "=========================================="

log "清空远程目录..."
sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no \
    ${REMOTE_USER}@${REMOTE_HOST} \
    "rm -rf ${REMOTE_PATH}/*"

log "上传文件..."
# 使用scp上传文件
sshpass -p "$REMOTE_PASSWORD" scp -o StrictHostKeyChecking=no -r \
    "$BUILD_DIR"/* \
    ${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_PATH}/

success "✓ 文件上传完成"

# ============================================
# 步骤4: 设置远程文件权限
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 4/5: 设置文件权限${NC}"
echo "=========================================="

sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no \
    ${REMOTE_USER}@${REMOTE_HOST} \
    "chown -R www-data:www-data ${REMOTE_PATH} && chmod -R 755 ${REMOTE_PATH}"

success "✓ 权限设置完成"

# ============================================
# 步骤5: 验证部署
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 5/5: 验证部署${NC}"
echo "=========================================="

log "检查关键文件..."
RESULT=$(sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no \
    ${REMOTE_USER}@${REMOTE_HOST} \
    "if [ -f '${REMOTE_PATH}/index.html' ]; then echo 'OK'; else echo 'FAIL'; fi")

if [ "$RESULT" = "OK" ]; then
    success "✓ index.html 存在"
else
    error "✗ index.html 不存在"
    exit 1
fi

log "检查 assets 目录..."
ASSETS_COUNT=$(sshpass -p "$REMOTE_PASSWORD" ssh -o StrictHostKeyChecking=no \
    ${REMOTE_USER}@${REMOTE_HOST} \
    "ls ${REMOTE_PATH}/assets 2>/dev/null | wc -l")

log "✓ 找到 $ASSETS_COUNT 个资源文件"

# ============================================
# 部署完成
# ============================================
echo ""
echo "=========================================="
echo -e "${GREEN}✅ 部署成功！${NC}"
echo "=========================================="
echo ""
echo "部署信息："
echo "  远程主机: $REMOTE_HOST"
echo "  远程路径: $REMOTE_PATH"
echo "  备份位置: $BACKUP_DIR"
echo ""
echo "访问地址："
echo -e "  主页: ${GREEN}https://meiyueart.com${NC}"
echo -e "  登录: ${GREEN}https://meiyueart.com/login-full${NC}"
echo -e "  注册: ${GREEN}https://meiyueart.com/register-full${NC}"
echo ""
echo "提示："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 使用无痕模式测试"
echo "  3. 如有问题，恢复备份："
echo "     ssh root@${REMOTE_HOST}"
echo "     cp -r ${BACKUP_DIR}/* ${REMOTE_PATH}/"
echo ""
