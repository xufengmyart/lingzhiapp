#!/bin/bash

# 智能体一致性验证定时任务管理脚本

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEDULER_SCRIPT="$SCRIPT_DIR/scheduler_agent_consistency.py"
PID_FILE="$SCRIPT_DIR/.scheduler.pid"
LOG_FILE="/app/work/logs/bypass/agent_consistency_scheduler.log"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 显示帮助信息
show_help() {
    echo "智能体一致性验证定时任务管理脚本"
    echo ""
    echo "用法: $0 {start|stop|restart|status|logs|run_now}"
    echo ""
    echo "命令:"
    echo "  start    - 启动定时任务调度器"
    echo "  stop     - 停止定时任务调度器"
    echo "  restart  - 重启定时任务调度器"
    echo "  status   - 查看调度器状态"
    echo "  logs     - 查看调度器日志（最新50行）"
    echo "  run_now  - 立即执行一次验证"
    echo ""
}

# 检查调度器是否在运行
is_running() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p "$PID" > /dev/null 2>&1; then
            return 0
        else
            # PID文件存在但进程不存在，清理PID文件
            rm -f "$PID_FILE"
            return 1
        fi
    fi
    return 1
}

# 启动调度器
start_scheduler() {
    if is_running; then
        echo -e "${YELLOW}调度器已在运行中${NC}"
        return 1
    fi

    echo "启动智能体一致性验证定时任务调度器..."

    # 启动调度器
    nohup python "$SCHEDULER_SCRIPT" > /dev/null 2>&1 &
    PID=$!

    # 保存PID
    echo $PID > "$PID_FILE"

    sleep 2

    if is_running; then
        echo -e "${GREEN}✅ 调度器启动成功（PID: $PID）${NC}"
        echo "日志文件: $LOG_FILE"
        echo ""
        echo "使用以下命令查看日志:"
        echo "  $0 logs"
        echo ""
        echo "使用以下命令查看状态:"
        echo "  $0 status"
        return 0
    else
        echo -e "${RED}❌ 调度器启动失败${NC}"
        return 1
    fi
}

# 停止调度器
stop_scheduler() {
    if ! is_running; then
        echo -e "${YELLOW}调度器未在运行${NC}"
        return 1
    fi

    echo "停止智能体一致性验证定时任务调度器..."

    PID=$(cat "$PID_FILE")
    kill "$PID"

    sleep 2

    if is_running; then
        echo -e "${YELLOW}调度器未正常停止，尝试强制终止...${NC}"
        kill -9 "$PID"
        sleep 1
    fi

    rm -f "$PID_FILE"

    if is_running; then
        echo -e "${RED}❌ 调度器停止失败${NC}"
        return 1
    else
        echo -e "${GREEN}✅ 调度器已停止${NC}"
        return 0
    fi
}

# 重启调度器
restart_scheduler() {
    echo "重启智能体一致性验证定时任务调度器..."
    stop_scheduler
    sleep 1
    start_scheduler
}

# 查看状态
show_status() {
    if is_running; then
        PID=$(cat "$PID_FILE")
        echo -e "${GREEN}✅ 调度器正在运行${NC}"
        echo "PID: $PID"
        echo "启动时间: $(ps -p $PID -o lstart=)"
        echo "CPU使用: $(ps -p $PID -o %cpu=)%"
        echo "内存使用: $(ps -p $PID -o %mem=)%"
        echo "日志文件: $LOG_FILE"
        return 0
    else
        echo -e "${YELLOW}⚠️ 调度器未在运行${NC}"
        return 1
    fi
}

# 查看日志
show_logs() {
    if [ -f "$LOG_FILE" ]; then
        echo "智能体一致性验证调度器日志（最新50行）:"
        echo "========================================"
        tail -n 50 "$LOG_FILE"
        echo "========================================"
        echo ""
        echo "查看完整日志: cat $LOG_FILE"
    else
        echo -e "${YELLOW}日志文件不存在: $LOG_FILE${NC}"
    fi
}

# 立即执行验证
run_now() {
    echo "立即执行智能体一致性验证..."
    VERIFY_SCRIPT="$SCRIPT_DIR/verify_agent_consistency.py"

    if [ -f "$VERIFY_SCRIPT" ]; then
        python "$VERIFY_SCRIPT"
    else
        echo -e "${RED}❌ 验证脚本不存在: $VERIFY_SCRIPT${NC}"
        return 1
    fi
}

# 主函数
main() {
    case "$1" in
        start)
            start_scheduler
            ;;
        stop)
            stop_scheduler
            ;;
        restart)
            restart_scheduler
            ;;
        status)
            show_status
            ;;
        logs)
            show_logs
            ;;
        run_now)
            run_now
            ;;
        *)
            show_help
            exit 1
            ;;
    esac
}

main "$@"
