#!/bin/bash
# 后端服务监控脚本
# 自动检测和重启停止的服务

LOG_FILE="/var/log/service-monitor.log"
BACKEND_CMD="python3 /workspace/projects/admin-backend/app.py"
BACKEND_DIR="/workspace/projects/admin-backend"
MAX_RESTART_ATTEMPTS=5
RESTART_DELAY=30

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

# 检查服务是否运行
check_backend() {
    if pgrep -f "python.*app.py" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# 启动后端服务
start_backend() {
    log "启动后端服务..."
    cd "$BACKEND_DIR"
    
    # 清理可能的僵尸进程
    pkill -9 -f "python.*app.py" 2>/dev/null || true
    sleep 2
    
    # 使用 nohup 启动服务
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    
    # 保存 PID
    echo $BACKEND_PID > /tmp/backend.pid
    
    # 等待服务启动
    sleep 10
    
    # 验证服务是否启动成功
    if pgrep -f "python.*app.py" > /dev/null; then
        log_success "后端服务启动成功 (PID: $BACKEND_PID)"
        return 0
    else
        log_error "后端服务启动失败"
        log "查看日志:"
        tail -20 /tmp/backend.log
        return 1
    fi
}

# 停止后端服务
stop_backend() {
    log "停止后端服务..."
    pkill -f "python.*app.py" || true
    sleep 3
    
    # 确保进程已停止
    if pgrep -f "python.*app.py" > /dev/null; then
        log_warning "强制终止进程..."
        pkill -9 -f "python.*app.py" || true
        sleep 2
    fi
    
    log "后端服务已停止"
}

# 重启后端服务
restart_backend() {
    log "重启后端服务..."
    stop_backend
    sleep 2
    start_backend
}

# 健康检查
health_check() {
    if curl -s -f http://localhost:5000 > /dev/null 2>&1; then
        log_success "后端服务健康检查通过"
        return 0
    else
        log_warning "后端服务健康检查失败"
        return 1
    fi
}

# 监控循环
monitor_loop() {
    local restart_count=0
    
    while true; do
        if ! check_backend; then
            log_warning "检测到后端服务未运行"
            
            if [ $restart_count -lt $MAX_RESTART_ATTEMPTS ]; then
                log "尝试重启服务 (尝试 $((restart_count + 1))/$MAX_RESTART_ATTEMPTS)"
                
                if start_backend; then
                    restart_count=0
                    health_check
                else
                    restart_count=$((restart_count + 1))
                    log_error "服务启动失败，等待 $RESTART_DELAY 秒后重试..."
                    sleep $RESTART_DELAY
                fi
            else
                log_error "达到最大重启尝试次数 ($MAX_RESTART_ATTEMPTS)，停止监控"
                exit 1
            fi
        else
            # 服务正在运行，进行健康检查
            health_check
            restart_count=0
        fi
        
        # 每 30 秒检查一次
        sleep 30
    done
}

# 主函数
main() {
    log "=========================================="
    log "服务监控脚本启动"
    log "=========================================="
    
    # 根据参数执行不同操作
    case "${1:-monitor}" in
        start)
            start_backend
            ;;
        stop)
            stop_backend
            ;;
        restart)
            restart_backend
            ;;
        status)
            if check_backend; then
                log_success "后端服务正在运行"
                ps aux | grep "python.*app.py" | grep -v grep
            else
                log_warning "后端服务未运行"
            fi
            ;;
        health)
            health_check
            ;;
        monitor)
            # 先尝试启动服务
            if ! check_backend; then
                log "服务未运行，尝试启动..."
                start_backend
            fi
            # 进入监控循环
            monitor_loop
            ;;
        *)
            echo "用法: $0 {start|stop|restart|status|health|monitor}"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
