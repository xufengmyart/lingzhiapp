#!/bin/bash

# ============================================
# 智能体自动化系统
# 功能：监控代码变化，自动部署
# 使用方法：./auto-deploy.sh &
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置
WATCH_DIR="/workspace/projects"
SERVER_HOST="123.56.142.143"
LOG_FILE="/workspace/projects/auto-deploy.log"
PID_FILE="/workspace/projects/auto-deploy.pid"

# 监控间隔（秒）
WATCH_INTERVAL=30
# 部署冷却时间（秒）
DEPLOY_COOLDOWN=300

# 部署冷却时间戳
LAST_DEPLOY_TIME=0

# ============================================
# 函数定义
# ============================================

log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    echo -e "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

log_info() {
    log "INFO" "$1"
}

log_success() {
    log -e "${GREEN}SUCCESS${NC}" "$1"
}

log_error() {
    log -e "${RED}ERROR${NC}" "$1"
}

log_warning() {
    log -e "${YELLOW}WARN${NC}" "$1"
}

# 获取文件的哈希值
get_file_hash() {
    find "$WATCH_DIR" -type f \( -name "*.tsx" -o -name "*.ts" -o -name "*.jsx" -o -name "*.js" -o -name "*.json" \) -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/dist/*" -not -path "*/build/*" -exec md5sum {} \; | md5sum | cut -d' ' -f1
}

# 执行快速部署
perform_deploy() {
    local current_time=$(date +%s)

    # 检查冷却时间
    if [ $((current_time - LAST_DEPLOY_TIME)) -lt $DEPLOY_COOLDOWN ]; then
        local remaining=$((DEPLOY_COOLDOWN - (current_time - LAST_DEPLOY_TIME)))
        log_warning "部署冷却中，还需等待 ${remaining} 秒"
        return 1
    fi

    log_info "检测到代码变化，开始自动部署..."

    cd "$WATCH_DIR"

    # 1. 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        log_info "发现未提交的更改，自动提交..."

        git add -A
        local commit_message="auto-deploy: $(date '+%Y-%m-%d %H:%M:%S')"
        git commit -m "$commit_message" --no-verify

        log_success "代码已自动提交"
    fi

    # 2. 推送到 GitHub
    log_info "推送到 GitHub..."
    if git push origin main 2>&1 | tee -a "$LOG_FILE"; then
        log_success "已推送到 GitHub"
    else
        log_error "推送到 GitHub 失败"
        return 1
    fi

    # 3. 同步到服务器
    log_info "同步到服务器..."
    if ssh root@"$SERVER_HOST" "
        set -e
        cd /var/www/lingzhiapp
        git pull origin main
        sudo systemctl restart nginx
    " 2>&1 | tee -a "$LOG_FILE"; then
        log_success "已同步到服务器"
    else
        log_error "同步到服务器失败"
        return 1
    fi

    # 4. 验证部署
    log_info "验证部署..."
    if ssh root@"$SERVER_HOST" "systemctl is-active nginx" > /dev/null 2>&1; then
        log_success "部署验证通过"
    else
        log_error "部署验证失败"
        return 1
    fi

    # 更新最后部署时间
    LAST_DEPLOY_TIME=$(date +%s)

    log_success "自动部署完成！"

    return 0
}

# 监控循环
watch_loop() {
    log_info "智能体自动化系统启动"
    log_info "监控目录: $WATCH_DIR"
    log_info "监控间隔: ${WATCH_INTERVAL} 秒"
    log_info "部署冷却时间: ${DEPLOY_COOLDOWN} 秒"
    log_info "日志文件: $LOG_FILE"

    local last_hash=""

    while true; do
        # 获取当前文件哈希
        local current_hash=$(get_file_hash)

        # 比较哈希值
        if [ "$last_hash" != "" ] && [ "$last_hash" != "$current_hash" ]; then
            log_warning "检测到文件变化"
            perform_deploy
        fi

        # 更新哈希值
        last_hash=$current_hash

        # 等待
        sleep $WATCH_INTERVAL
    done
}

# 信号处理
cleanup() {
    log_info "收到退出信号，正在清理..."
    if [ -f "$PID_FILE" ]; then
        rm -f "$PID_FILE"
    fi
    log_info "智能体自动化系统已停止"
    exit 0
}

# 显示帮助
show_help() {
    echo "智能体自动化系统"
    echo ""
    echo "使用方法:"
    echo "  ./auto-deploy.sh start    - 启动自动化系统"
    echo "  ./auto-deploy.sh stop     - 停止自动化系统"
    echo "  ./auto-deploy.sh status   - 查看系统状态"
    echo "  ./auto-deploy.sh logs     - 查看日志"
    echo "  ./auto-deploy.sh deploy   - 手动触发部署"
    echo "  ./auto-deploy.sh help     - 显示帮助信息"
    echo ""
    echo "功能说明:"
    echo "  - 自动监控代码变化"
    echo "  - 检测到变化后自动提交并推送"
    echo "  - 自动同步到服务器"
    echo "  - 支持部署冷却时间"
}

# 查看状态
show_status() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${GREEN}✓ 智能体自动化系统正在运行${NC}"
            echo "  PID: $pid"
            echo "  日志: $LOG_FILE"
            echo ""
            echo "最近日志："
            tail -n 10 "$LOG_FILE"
        else
            echo -e "${RED}✗ PID 文件存在但进程未运行${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}✗ 智能体自动化系统未运行${NC}"
    fi
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -n 50 -f "$LOG_FILE"
    else
        echo "日志文件不存在"
    fi
}

# 启动系统
start_system() {
    # 检查是否已经在运行
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}⚠ 智能体自动化系统已经在运行 (PID: $pid)${NC}"
            exit 1
        else
            rm -f "$PID_FILE"
        fi
    fi

    # 后台运行监控循环
    echo "启动智能体自动化系统..."
    watch_loop &
    local pid=$!

    # 保存 PID
    echo $pid > "$PID_FILE"

    echo -e "${GREEN}✓ 智能体自动化系统已启动 (PID: $pid)${NC}"
    echo "  日志文件: $LOG_FILE"
    echo ""
    echo "使用以下命令查看状态:"
    echo "  ./auto-deploy.sh status"
    echo ""
    echo "使用以下命令查看日志:"
    echo "  ./auto-deploy.sh logs"
    echo ""
    echo "使用以下命令停止系统:"
    echo "  ./auto-deploy.sh stop"
}

# 停止系统
stop_system() {
    if [ -f "$PID_FILE" ]; then
        local pid=$(cat "$PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            echo "停止智能体自动化系统..."
            kill "$pid"
            rm -f "$PID_FILE"
            echo -e "${GREEN}✓ 智能体自动化系统已停止${NC}"
        else
            echo -e "${YELLOW}⚠ 进程未运行${NC}"
            rm -f "$PID_FILE"
        fi
    else
        echo -e "${YELLOW}⚠ 智能体自动化系统未运行${NC}"
    fi
}

# ============================================
# 主流程
# ============================================

# 注册信号处理
trap cleanup SIGINT SIGTERM

# 处理命令行参数
case "${1:-start}" in
    start)
        start_system
        ;;
    stop)
        stop_system
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    deploy)
        perform_deploy
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}✗ 未知选项: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
