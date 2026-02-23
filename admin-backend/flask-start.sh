#!/bin/bash

# Flask 应用启动脚本
# 支持自动重启、日志管理、健康检查

set -e

# 配置
APP_DIR="/workspace/projects/admin-backend"
APP_USER="root"
WORKERS=4
BIND_ADDR="0.0.0.0:8080"
LOG_DIR="/var/log/flask"
PID_FILE="/var/run/flask-app.pid"
ACCESS_LOG="${LOG_DIR}/access.log"
ERROR_LOG="${LOG_DIR}/error.log"
GUNICORN_BIN="/usr/local/bin/gunicorn"

# 创建日志目录
mkdir -p "${LOG_DIR}"
chmod 755 "${LOG_DIR}"

# 停止旧进程
stop_old_process() {
    echo "停止旧进程..."

    # 停止旧的 gunicorn 进程
    pkill -f "gunicorn.*app:app" || true

    # 等待进程完全停止
    sleep 2

    # 检查是否还有残留进程
    if pgrep -f "gunicorn.*app:app" > /dev/null; then
        echo "强制停止残留进程..."
        pkill -9 -f "gunicorn.*app:app" || true
        sleep 1
    fi

    echo "旧进程已停止"
}

# 启动新进程
start_new_process() {
    echo "启动新进程..."

    cd "${APP_DIR}"

    # 启动 gunicorn
    nohup "${GUNICORN_BIN}" \
        --workers "${WORKERS}" \
        --worker-class sync \
        --worker-connections 1000 \
        --max-requests 1000 \
        --max-requests-jitter 50 \
        --timeout 120 \
        --keep-alive 5 \
        --bind "${BIND_ADDR}" \
        --access-logfile "${ACCESS_LOG}" \
        --error-logfile "${ERROR_LOG}" \
        --log-level info \
        --capture-output \
        --daemon \
        --pid "${PID_FILE}" \
        app:app

    echo "新进程已启动"
}

# 检查进程状态
check_process() {
    if [ -f "${PID_FILE}" ]; then
        pid=$(cat "${PID_FILE}")
        if ps -p "${pid}" > /dev/null 2>&1; then
            return 0
        else
            echo "PID 文件存在但进程不存在"
            return 1
        fi
    else
        echo "PID 文件不存在"
        return 1
    fi
}

# 健康检查
health_check() {
    local max_attempts=10
    local attempt=0

    while [ ${attempt} -lt ${max_attempts} ]; do
        attempt=$((attempt + 1))

        if curl -f -s http://localhost:8080/health > /dev/null 2>&1; then
            echo "健康检查通过"
            return 0
        else
            echo "健康检查失败，第 ${attempt}/${max_attempts} 次"
            sleep 2
        fi
    done

    echo "健康检查失败"
    return 1
}

# 主流程
main() {
    echo "=========================================="
    echo "Flask 应用启动脚本"
    echo "=========================================="
    echo ""

    # 停止旧进程
    stop_old_process

    # 启动新进程
    start_new_process

    # 等待进程启动
    echo "等待进程启动..."
    sleep 3

    # 检查进程状态
    if check_process; then
        echo "进程运行正常"
    else
        echo "进程启动失败"
        exit 1
    fi

    # 健康检查
    if health_check; then
        echo ""
        echo "=========================================="
        echo "✓ Flask 应用启动成功"
        echo "=========================================="
        echo ""
        echo "服务信息:"
        echo "  工作目录: ${APP_DIR}"
        echo "  监听地址: ${BIND_ADDR}"
        echo "  Worker 数量: ${WORKERS}"
        echo "  访问日志: ${ACCESS_LOG}"
        echo "  错误日志: ${ERROR_LOG}"
        echo "  PID 文件: ${PID_FILE}"
        echo ""
        echo "管理命令:"
        echo "  查看状态: ps aux | grep gunicorn"
        echo "  查看日志: tail -f ${ERROR_LOG}"
        echo "  停止服务: ${0} stop"
        echo "  重启服务: ${0} restart"
        echo ""
    else
        echo "健康检查失败，服务启动失败"
        exit 1
    fi
}

# 停止命令
stop() {
    stop_old_process
    [ -f "${PID_FILE}" ] && rm -f "${PID_FILE}"
    echo "服务已停止"
}

# 重启命令
restart() {
    stop
    sleep 2
    main
}

# 命令处理
case "${1:-start}" in
    start)
        main
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    status)
        if check_process; then
            echo "服务运行中"
            ps aux | grep gunicorn | grep -v grep
        else
            echo "服务未运行"
            exit 1
        fi
        ;;
    *)
        echo "用法: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac
