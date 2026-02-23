#!/bin/bash

# Flask 应用监控脚本
# 定期执行健康检查，自动恢复故障

set -e

# 配置
SCRIPT_DIR="/workspace/projects/admin-backend"
HEALTH_CHECK_SCRIPT="${SCRIPT_DIR}/health-check.sh"
LOG_DIR="/var/log/flask"
MONITOR_LOG="${LOG_DIR}/monitor.log"

# 创建日志目录
mkdir -p "${LOG_DIR}"

# 日志函数
log() {
    local level=$1
    shift
    local message="$*"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[${timestamp}] [${level}] ${message}" | tee -a "${MONITOR_LOG}"
}

# 执行健康检查
run_health_check() {
    log "INFO" "执行健康检查..."

    if [ -x "${HEALTH_CHECK_SCRIPT}" ]; then
        "${HEALTH_CHECK_SCRIPT}" check
        local result=$?

        if [ ${result} -eq 0 ]; then
            log "INFO" "✓ 服务健康检查通过"
        else
            log "WARNING" "服务已自动重启"
        fi
    else
        log "ERROR" "健康检查脚本不存在: ${HEALTH_CHECK_SCRIPT}"
    fi
}

# 检查磁盘空间
check_disk_space() {
    local usage=$(df -h /workspace | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ ${usage} -gt 90 ]; then
        log "WARNING" "磁盘空间不足: ${usage}%"
    fi
}

# 检查内存使用
check_memory() {
    local usage=$(free | awk 'NR==2{printf "%.0f", $3/$2*100}')

    if [ ${usage} -gt 90 ]; then
        log "WARNING" "内存使用过高: ${usage}%"
    fi
}

# 主流程
main() {
    log "INFO" "=========================================="
    log "INFO" "开始监控检查"
    log "INFO" "=========================================="

    # 健康检查
    run_health_check

    # 资源检查
    check_disk_space
    check_memory

    log "INFO" "监控检查完成"
}

# 定时任务安装
install_cron() {
    log "INFO" "安装定时任务..."

    # 添加 crontab 任务
    (crontab -l 2>/dev/null | grep -v "flask-monitor"; \
     echo "* * * * * ${0} check >> /var/log/flask/monitor-cron.log 2>&1") | crontab -

    log "INFO" "定时任务已安装，每分钟执行一次"
}

# 卸载定时任务
uninstall_cron() {
    log "INFO" "卸载定时任务..."

    crontab -l 2>/dev/null | grep -v "flask-monitor" | crontab -

    log "INFO" "定时任务已卸载"
}

# 命令处理
case "${1:-check}" in
    check)
        main
        ;;
    install)
        install_cron
        ;;
    uninstall)
        uninstall_cron
        ;;
    *)
        echo "用法: $0 {check|install|uninstall}"
        echo ""
        echo "命令说明:"
        echo "  check     - 执行一次监控检查"
        echo "  install   - 安装定时任务（每分钟执行一次）"
        echo "  uninstall - 卸载定时任务"
        exit 1
        ;;
esac
