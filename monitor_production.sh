#!/bin/bash
################################################################################
# 生产环境监控脚本
# 用途: 监控生产环境状态，发现异常自动告警
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
PRODUCTION_URL="https://meiyueart.com"
API_BASE="$PRODUCTION_URL/api"
ALERT_EMAIL="ops@meiyueart.com"
LOG_FILE="/var/log/production_monitor.log"
ERROR_LOG_FILE="/var/log/production_alerts.log"

# 告警阈值
MAX_RESPONSE_TIME=5000  # 5秒
MAX_CPU_USAGE=80        # 80%
MAX_MEMORY_USAGE=80     # 80%
MAX_DISK_USAGE=90       # 90%

# 日志函数
log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} [INFO] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} [ERROR] $1" | tee -a "$ERROR_LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} [WARNING] $1" | tee -a "$LOG_FILE"
}

# 发送告警
send_alert() {
    local subject="[ALERT] $1"
    local body="时间: $(date '+%Y-%m-%d %H:%M:%S')\n告警信息: $2\n服务器: $PRODUCTION_URL"
    
    log_error "$1: $2"
    
    # 发送邮件（需要配置sendmail或使用其他方式）
    echo -e "Subject: $subject\n\n$body" | sendmail -t "$ALERT_EMAIL" 2>/dev/null || \
        log_warning "邮件发送失败"
}

# 检查API健康状态
check_api_health() {
    log_info "检查API健康状态"
    
    local response=$(curl -sf "$API_BASE/health")
    local exit_code=$?
    
    if [ $exit_code -ne 0 ]; then
        send_alert "API健康检查失败" "API无法访问，请立即检查！"
        return 1
    fi
    
    if echo "$response" | grep -q '"status":"healthy"'; then
        log_info "API健康状态正常"
        return 0
    else
        send_alert "API健康状态异常" "API响应异常: $response"
        return 1
    fi
}

# 检查API响应时间
check_response_time() {
    log_info "检查API响应时间"
    
    local start_time=$(date +%s%N)
    curl -sf "$API_BASE/health" > /dev/null
    local exit_code=$?
    local end_time=$(date +%s%N)
    
    if [ $exit_code -ne 0 ]; then
        return 1
    fi
    
    local duration=$(( (end_time - start_time) / 1000000 ))
    
    if [ $duration -gt $MAX_RESPONSE_TIME ]; then
        send_alert "API响应时间过长" "响应时间: ${duration}ms (阈值: ${MAX_RESPONSE_TIME}ms)"
        return 1
    else
        log_info "API响应时间: ${duration}ms (正常)"
        return 0
    fi
}

# 检查服务状态
check_service_status() {
    log_info "检查服务状态"
    
    local status=$(sudo supervisorctl status lingzhi_admin_backend | awk '{print $2}')
    
    if [ "$status" == "RUNNING" ]; then
        log_info "服务状态: 运行中"
        return 0
    else
        send_alert "服务状态异常" "服务状态: $status"
        return 1
    fi
}

# 检查CPU使用率
check_cpu_usage() {
    log_info "检查CPU使用率"
    
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    cpu_usage=${cpu_usage%.*}  # 取整数部分
    
    if [ $cpu_usage -gt $MAX_CPU_USAGE ]; then
        send_alert "CPU使用率过高" "CPU使用率: ${cpu_usage}% (阈值: ${MAX_CPU_USAGE}%)"
        return 1
    else
        log_info "CPU使用率: ${cpu_usage}% (正常)"
        return 0
    fi
}

# 检查内存使用率
check_memory_usage() {
    log_info "检查内存使用率"
    
    local memory_usage=$(free | grep Mem | awk '{printf("%.0f"), $3/$2 * 100.0}')
    memory_usage=${memory_usage%.*}
    
    if [ $memory_usage -gt $MAX_MEMORY_USAGE ]; then
        send_alert "内存使用率过高" "内存使用率: ${memory_usage}% (阈值: ${MAX_MEMORY_USAGE}%)"
        return 1
    else
        log_info "内存使用率: ${memory_usage}% (正常)"
        return 0
    fi
}

# 检查磁盘空间
check_disk_usage() {
    log_info "检查磁盘空间"
    
    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    if [ $disk_usage -gt $MAX_DISK_USAGE ]; then
        send_alert "磁盘空间不足" "磁盘使用率: ${disk_usage}% (阈值: ${MAX_DISK_USAGE}%)"
        return 1
    else
        log_info "磁盘使用率: ${disk_usage}% (正常)"
        return 0
    fi
}

# 检查错误日志
check_error_logs() {
    log_info "检查错误日志"
    
    local error_count=$(sudo grep -c "ERROR" /var/log/flask_backend.log 2>/dev/null || echo "0")
    
    if [ $error_count -gt 10 ]; then
        send_alert "错误日志过多" "发现 $error_count 条ERROR日志"
        return 1
    else
        log_info "错误日志数量: $error_count (正常)"
        return 0
    fi
}

# 检查数据库状态
check_database_status() {
    log_info "检查数据库状态"
    
    local db_path="/path/to/app/admin-backend/data/lingzhi_ecosystem.db"
    
    if [ ! -f "$db_path" ]; then
        send_alert "数据库文件不存在" "数据库路径: $db_path"
        return 1
    fi
    
    local db_size=$(du -h "$db_path" | awk '{print $1}')
    log_info "数据库大小: $db_size (正常)"
    return 0
}

# 生成监控报告
generate_report() {
    echo ""
    echo "========================================="
    echo "  监控报告"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================="
    echo ""
    echo "检查项目:"
    echo "  - API健康状态: $(check_api_health 2>&1 | tail -1)"
    echo "  - API响应时间: $(check_response_time 2>&1 | tail -1)"
    echo "  - 服务状态: $(check_service_status 2>&1 | tail -1)"
    echo "  - CPU使用率: $(check_cpu_usage 2>&1 | tail -1)"
    echo "  - 内存使用率: $(check_memory_usage 2>&1 | tail -1)"
    echo "  - 磁盘空间: $(check_disk_usage 2>&1 | tail -1)"
    echo "  - 错误日志: $(check_error_logs 2>&1 | tail -1)"
    echo "  - 数据库状态: $(check_database_status 2>&1 | tail -1)"
    echo ""
}

# 主函数
main() {
    log_info "开始监控检查"
    
    local error_count=0
    
    # 执行所有检查
    check_api_health || ((error_count++))
    check_response_time || ((error_count++))
    check_service_status || ((error_count++))
    check_cpu_usage || ((error_count++))
    check_memory_usage || ((error_count++))
    check_disk_usage || ((error_count++))
    check_error_logs || ((error_count++))
    check_database_status || ((error_count++))
    
    log_info "监控检查完成，发现 $error_count 个问题"
    
    # 生成报告
    generate_report
    
    return $error_count
}

# 执行主函数
main "$@"
