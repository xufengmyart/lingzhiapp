#!/bin/bash

# 智能体自动化部署系统 v1.0
# 功能：监控代码变化，自动提交、推送并部署到服务器

set -e

# 加载环境变量
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] [ERROR] 未找到 .env 文件，请从 .env.example 复制并配置"
    exit 1
fi

# 配置
PROJECT_PATH="/workspace/projects"
SERVER_USER="${SERVER_USER:-root}"
SERVER_HOST="${SERVER_HOST:-your-server-ip}"
SERVER_PATH="${SERVER_PATH:-/var/www/html}"
BACKUP_PATH="${SERVER_PATH}/backup"
LOG_FILE="/app/work/logs/bypass/app.log"
MONITOR_INTERVAL="${MONITOR_INTERVAL:-30}"  # 监控间隔（秒）

# GitHub 配置
GITHUB_USERNAME="${GITHUB_USERNAME:-}"
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
GITHUB_REPO="https://${GITHUB_USERNAME}:${GITHUB_TOKEN}@github.com/xufengmyart/lingzhiapp.git"

# SSH 配置
SSH_PASSWORD="${SERVER_PASSWORD:-}"
SSH_CMD="sshpass -p '${SSH_PASSWORD}' ssh -o StrictHostKeyChecking=no ${SERVER_USER}@${SERVER_HOST}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 日志函数
log() {
    echo -e "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1${NC}" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}$(date '+%Y-%m-%d %H:%M:%S') [WARN] $1${NC}" | tee -a "$LOG_FILE"
}

# 检查 Git 状态
check_git_status() {
    cd "$PROJECT_PATH"
    git status --porcelain
}

# 提交代码
commit_changes() {
    cd "$PROJECT_PATH"

    # 检查是否有变更
    if [ -z "$(check_git_status)" ]; then
        warn "没有检测到代码变更"
        return 0
    fi

    log "检测到代码变更，准备提交..."

    # 添加所有变更
    git add .

    # 提交
    commit_msg="Auto deploy: $(date '+%Y-%m-%d %H:%M:%S')"
    git commit -m "$commit_msg"

    success "代码已提交: $commit_msg"
}

# 推送到远程仓库
push_to_remote() {
    cd "$PROJECT_PATH"

    log "推送到远程仓库..."

    if git push "$GITHUB_REPO" 2>&1; then
        success "代码已推送到远程仓库"
    else
        error "推送失败"
        return 1
    fi
}

# 部署到服务器
deploy_to_server() {
    log "部署到服务器..."

    # 备份当前版本
    $SSH_CMD "mkdir -p $BACKUP_PATH && cp -r $SERVER_PATH/* $BACKUP_PATH/backup-$(date +%Y%m%d-%H%M%S)/ 2>/dev/null || true"

    # 同步文件
    export SSHPASS="$SSH_PASSWORD"
    rsync -avz --delete -e "sshpass -e ssh -o StrictHostKeyChecking=no" "$PROJECT_PATH/public/" "$SERVER_USER@$SERVER_HOST:$SERVER_PATH/"
    unset SSHPASS

    # 重启 Nginx
    export SSHPASS="$SSH_PASSWORD"
    $SSH_CMD "systemctl reload nginx"
    unset SSHPASS

    success "部署成功！"
}

# 执行完整部署流程
full_deploy() {
    log "开始完整部署流程..."

    commit_changes
    push_to_remote
    deploy_to_server

    success "完整部署流程完成！"
}

# 监控代码变化
monitor_changes() {
    log "开始监控代码变化（间隔: ${MONITOR_INTERVAL}秒）..."

    while true; do
        if [ -n "$(check_git_status)" ]; then
            log "检测到代码变更"
            full_deploy
        fi

        sleep "$MONITOR_INTERVAL"
    done
}

# PID 文件
PID_FILE="/tmp/auto-deploy.pid"

# 启动监控
start() {
    if [ -f "$PID_FILE" ]; then
        warn "监控已在运行中 (PID: $(cat $PID_FILE))"
        exit 1
    fi

    log "启动自动化部署系统..."

    # 在后台运行监控
    monitor_changes &
    echo $! > "$PID_FILE"

    success "自动化部署系统已启动 (PID: $(cat $PID_FILE))"
    log "使用 '$0 stop' 停止监控"
}

# 停止监控
stop() {
    if [ ! -f "$PID_FILE" ]; then
        warn "监控未运行"
        exit 1
    fi

    log "停止自动化部署系统..."

    kill $(cat "$PID_FILE")
    rm "$PID_FILE"

    success "自动化部署系统已停止"
}

# 查看状态
status() {
    if [ -f "$PID_FILE" ]; then
        success "监控正在运行 (PID: $(cat $PID_FILE))"
    else
        warn "监控未运行"
    fi
}

# 快速部署（不监控）
quick_deploy() {
    log "执行快速部署..."
    full_deploy
}

# 显示帮助
show_help() {
    echo "智能体自动化部署系统 v1.0"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令:"
    echo "  start      启动自动化监控"
    echo "  stop       停止自动化监控"
    echo "  status     查看监控状态"
    echo "  deploy     执行一次完整部署"
    echo "  quick      快速部署（不备份）"
    echo "  help       显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 start          # 启动自动化监控"
    echo "  $0 deploy         # 手动触发一次部署"
    echo "  $0 stop           # 停止监控"
}

# 主函数
main() {
    case "$1" in
        start)
            start
            ;;
        stop)
            stop
            ;;
        status)
            status
            ;;
        deploy)
            full_deploy
            ;;
        quick)
            quick_deploy
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo "错误: 未知命令 '$1'"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
