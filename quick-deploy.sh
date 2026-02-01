#!/bin/bash

# 快速部署脚本 - 不备份，快速同步
# 用途：开发过程中的快速预览

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

# GitHub 配置
GITHUB_USERNAME="${GITHUB_USERNAME:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
GITHUB_REPO="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/xufengmyart/lingzhiapp.git"

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

log "开始快速部署..."

# 进入项目目录
cd "$PROJECT_PATH"

# 检查是否有变更
if [ -n "$(git status --porcelain)" ]; then
    log "检测到代码变更"

    # 提交变更
    git add .
    git commit -m "Quick deploy: $(date '+%Y-%m-%d %H:%M:%S')" || true

    # 推送
    if git push "$GITHUB_REPO" 2>&1; then
        success "代码已推送到远程仓库"
    else
        error "推送失败"
        exit 1
    fi
else
    log "没有代码变更，跳过提交"
fi

# 构建前端
log "构建前端应用..."
cd "$PROJECT_PATH/web-app"

if npm run build; then
    success "前端构建成功"
else
    error "前端构建失败"
    exit 1
fi

# 同步到服务器
if [ -n "$SERVER_HOST" ] && [ "$SERVER_HOST" != "your-server-ip" ]; then
    log "同步文件到服务器..."

    # 设置 SSHPASS 环境变量
    export SSHPASS="$SERVER_PASSWORD"

    if rsync -avz --delete -e "sshpass -e ssh -o StrictHostKeyChecking=no" "$BUILD_DIR/" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"; then
        success "文件同步成功"

        # 重启 Nginx
        sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "systemctl reload nginx"
        success "Nginx 已重新加载"

        # 清除环境变量
        unset SSHPASS
    else
        error "文件同步失败"
        unset SSHPASS
        exit 1
    fi
else
    log "未配置服务器，跳过同步"
fi

success "快速部署完成！"
