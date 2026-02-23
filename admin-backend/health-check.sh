#!/bin/bash

# Flask 应用健康检查脚本
# 定期检查服务状态，异常时自动重启

set -e

# 配置
APP_DIR="/workspace/projects/admin-backend"
LOG_DIR="/var/log/flask"
START_SCRIPT="${APP_DIR}/flask-start.sh"
HEALTH_LOG="${LOG_DIR}/health-check.log"
PID_FILE="/var/run/flask-app.pid"
CHECK_INTERVAL=60  # 检查间隔（秒）
MAX_FAILURES=3     # 最大失败次数

# 创建日志目录
mkdir -p "${LOG_DIR}"

# 日志函数
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${HEALTH_LOG}"
}

# 检查进程是否存在
check_process() {
    if [ -f "${PID_FILE}" ]; then
        local pid=$(cat "${PID_FILE}")
        if ps -p "${pid}" > /dev/null 2>&1; then
            return 0
        fi
    fi

    # 检查是否有 gunicorn 进程
    if pgrep -f "gunicorn.*app:app" > /dev/null; then
        return 0
    fi

    return 1
}

# 检查端口是否监听
check_port() {
    if netstat -tuln 2>/dev/null | grep -q ":8080 "; then
        return 0
    fi

    if ss -tuln 2>/dev/null | grep -q ":8080 "; then
        return 0
    fi

    return 1
}

# 检查健康接口
check_health_endpoint() {
    local response
    response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/api/health 2>/dev/null || echo "000")

    if [ "${response}" = "200" ]; then
        return 0
    fi

    return 1
}

# 检查登录接口
check_login_endpoint() {
    local response
    response=$(curl -s -X POST http://localhost:8080/api/login \
        -H "Content-Type: application/json" \
        -H "Host: meiyueart.com" \
        -d '{"username":"admin","password":"admin123"}' \
        -o /dev/null \
        -w "%{http_code}" 2>/dev/null || echo "000")

    if [ "${response}" = "200" ]; then
        return 0
    fi

    return 1
}

# 记录失败次数
RESTART_NEEDED=0

# 主健康检查流程
main() {
    log "INFO" "开始健康检查..."

    local failure_count=0

    # 1. 检查进程
    if check_process; then
        log "INFO" "✓ 进程检查通过"
    else
        log "ERROR" "✗ 进程检查失败"
        failure_count=$((failure_count + 1))
    fi

    # 2. 检查端口
    if check_port; then
        log "INFO" "✓ 端口检查通过"
    else
        log "ERROR" "✗ 端口检查失败"
        failure_count=$((failure_count + 1))
    fi

    # 3. 检查健康接口
    if check_health_endpoint; then
        log "INFO" "✓ 健康接口检查通过"
    else
        log "ERROR" "✗ 健康接口检查失败"
        failure_count=$((failure_count + 1))
    fi

    # 4. 检查登录接口
    if check_login_endpoint; then
        log "INFO" "✓ 登录接口检查通过"
    else
        log "ERROR" "✗ 登录接口检查失败"
        failure_count=$((failure_count + 1))
    fi

    # 判断是否需要重启
    if [ ${failure_count} -ge ${MAX_FAILURES} ]; then
        log "ERROR" "健康检查失败 ${failure_count} 项，需要重启服务"
        RESTART_NEEDED=1
    elif [ ${failure_count} -gt 0 ]; then
        log "WARNING" "健康检查部分失败 (${failure_count}/${MAX_FAILURES})"
    else
        log "INFO" "✓ 所有检查通过，服务正常"
    fi

    return ${RESTART_NEEDED}
}

# 重启服务
restart_service() {
    log "INFO" "开始重启服务..."

    cd "${APP_DIR}"

    if [ -x "${START_SCRIPT}" ]; then
        "${START_SCRIPT}" restart
        log "INFO" "服务重启成功"
    else
        log "ERROR" "启动脚本不存在或不可执行: ${START_SCRIPT}"
        return 1
    fi
}

# 命令处理
case "${1:-check}" in
    check)
        main
        if [ $? -eq 1 ]; then
            restart_service
        fi
        ;;
    force-restart)
        log "INFO" "强制重启服务"
        restart_service
        ;;
    status)
        if check_process; then
            echo "服务运行中"
            exit 0
        else
            echo "服务未运行"
            exit 1
        fi
        ;;
    *)
        echo "用法: $0 {check|force-restart|status}"
        echo ""
        echo "命令说明:"
        echo "  check        - 执行健康检查，失败时自动重启"
        echo "  force-restart - 强制重启服务"
        echo "  status       - 检查服务状态"
        exit 1
        ;;
esac
