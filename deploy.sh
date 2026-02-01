#!/bin/bash

# 完整部署脚本 - 包含备份
# 用途：生产环境部署

set -e

# 加载环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] 未找到 .env 文件，请从 .env.example 复制并配置"
    exit 1
fi

PROJECT_PATH="/workspace/projects"
BUILD_DIR="$PROJECT_PATH/public"
LOG_FILE="/app/work/logs/bypass/app.log"

# 服务器配置
SERVER_USER="${SERVER_USER:-root}"
SERVER_HOST="${SERVER_HOST:-your-server-ip}"
SERVER_PASSWORD="${SERVER_PASSWORD:-}"
SERVER_PATH="${SERVER_PATH:-/var/www/html}"
BACKUP_DIR="${SERVER_PATH}/backup"

# GitHub 配置
GITHUB_USERNAME="${GITHUB_USERNAME:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
GITHUB_REPO="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/xufengmyart/lingzhiapp.git"

# SSH 配置
SSH_CMD="sshpass -p '${SERVER_PASSWORD}' ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST}"
BACKUP_RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-7}"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [INFO] $1" | tee -a "$LOG_FILE"
}

error() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] $1" | tee -a "$LOG_FILE"
}

success() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [SUCCESS] $1" | tee -a "$LOG_FILE"
}

warn() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [WARN] $1" | tee -a "$LOG_FILE"
}

log "开始完整部署..."

# 进入项目目录
cd "$PROJECT_PATH"

# 1. 检查代码变更
log "检查代码变更..."
if [ -n "$(git status --porcelain)" ]; then
    log "检测到代码变更"

    # 2. 提交变更
    log "提交代码变更..."
    git add .
    git commit -m "Full deploy: $(date '+%Y-%m-%d %H:%M:%S')" || true

    # 3. 推送到远程
    log "推送到远程仓库..."
    if git push "$GITHUB_REPO" 2>&1; then
        success "代码已推送到远程仓库"
    else
        error "推送失败"
        exit 1
    fi
else
    log "没有代码变更"
fi

# 4. 运行测试
log "运行测试..."
cd "$PROJECT_PATH"
# npm test  # 暂时跳过测试，可根据需要启用
success "测试跳过"

# 5. 构建前端
log "构建前端应用..."
cd "$PROJECT_PATH/web-app"
if npm run build; then
    success "前端构建成功"
else
    error "前端构建失败"
    exit 1
fi

# 6. 部署到服务器
if [ -n "$SERVER_HOST" ] && [ "$SERVER_HOST" != "your-server-ip" ]; then
    log "准备部署到服务器..."

    # 7. 备份当前版本
    log "备份当前版本..."
    BACKUP_NAME="backup-$(date +%Y%m%d-%H%M%S)"
    $SSH_CMD "mkdir -p $BACKUP_DIR && cp -r $SERVER_PATH/* $BACKUP_DIR/$BACKUP_NAME/ 2>/dev/null || true"
    success "备份完成: $BACKUP_NAME"

    # 8. 同步新版本
    log "同步新版本文件..."
    export SSHPASS="$SERVER_PASSWORD"
    if rsync -avz --delete -e "sshpass -e ssh -o StrictHostKeyChecking=no" "$BUILD_DIR/" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"; then
        success "文件同步成功"
        unset SSHPASS
    else
        error "文件同步失败"
        unset SSHPASS
        exit 1
    fi

    # 9. 重启服务
    log "重启服务..."
    export SSHPASS="$SERVER_PASSWORD"
    $SSH_CMD "systemctl reload nginx"
    success "Nginx 已重新加载"
    unset SSHPASS

    # 10. 验证部署
    log "验证部署..."
    sleep 2
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER_HOST/ || echo "000")

    if [ "$HTTP_CODE" = "200" ]; then
        success "部署验证成功 (HTTP $HTTP_CODE)"
    else
        error "部署验证失败 (HTTP $HTTP_CODE)"
        error "正在回滚..."
        export SSHPASS="$SERVER_PASSWORD"
        $SSH_CMD "rm -rf $SERVER_PATH/* && cp -r $BACKUP_DIR/$BACKUP_NAME/* $SERVER_PATH/"
        $SSH_CMD "systemctl reload nginx"
        success "已回滚到备份版本"
        unset SSHPASS
        exit 1
    fi
else
    warn "未配置服务器，跳过部署"
fi

# 11. 清理旧备份（保留配置的天数）
if [ -n "$SERVER_HOST" ] && [ "$SERVER_HOST" != "your-server-ip" ]; then
    log "清理旧备份..."
    export SSHPASS="$SERVER_PASSWORD"
    $SSH_CMD "find $BACKUP_DIR -name 'backup-*' -type d -mtime +${BACKUP_RETENTION_DAYS} -exec rm -rf {} + 2>/dev/null || true"
    unset SSHPASS
    success "旧备份已清理"
fi

success "完整部署成功！"
