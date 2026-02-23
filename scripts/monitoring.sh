#!/bin/bash
# 监控告警脚本
# 监控系统健康状态并在异常时发送告警

LOG_FILE="/var/log/monitoring.log"
ALERT_LOG="/var/log/alerts.log"
BACKEND_URL="http://localhost:5000"

# 告警阈值
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=80
ERROR_RATE_THRESHOLD=10
RESPONSE_TIME_THRESHOLD=5000

# 告警收件人
ALERT_EMAIL="admin@meiyueart.com"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_alert() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ALERT: $1${NC}" | tee -a "$ALERT_LOG"
}

# 检查 CPU 使用率
check_cpu() {
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    CPU_INT=${CPU_USAGE%.*}
    
    if [ $CPU_INT -gt $CPU_THRESHOLD ]; then
        log_alert "CPU 使用率过高: ${CPU_USAGE}%"
        send_alert "CPU 使用率过高" "当前 CPU 使用率为 ${CPU_USAGE}%，超过阈值 ${CPU_THRESHOLD}%"
        return 1
    else
        log "CPU 使用率正常: ${CPU_USAGE}%"
        return 0
    fi
}

# 检查内存使用率
check_memory() {
    MEMORY_USAGE=$(free | grep Mem | awk '{printf("%.0f"), $3/$2 * 100.0}')
    MEMORY_INT=${MEMORY_USAGE%.*}
    
    if [ $MEMORY_INT -gt $MEMORY_THRESHOLD ]; then
        log_alert "内存使用率过高: ${MEMORY_USAGE}%"
        send_alert "内存使用率过高" "当前内存使用率为 ${MEMORY_USAGE}%，超过阈值 ${MEMORY_THRESHOLD}%"
        return 1
    else
        log "内存使用率正常: ${MEMORY_USAGE}%"
        return 0
    fi
}

# 检查磁盘使用率
check_disk() {
    DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | cut -d'%' -f1)
    
    if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
        log_alert "磁盘使用率过高: ${DISK_USAGE}%"
        send_alert "磁盘使用率过高" "当前磁盘使用率为 ${DISK_USAGE}%，超过阈值 ${DISK_THRESHOLD}%"
        return 1
    else
        log "磁盘使用率正常: ${DISK_USAGE}%"
        return 0
    fi
}

# 检查后端服务
check_backend_service() {
    if pgrep -f "gunicorn\|python.*app.py" > /dev/null; then
        log "后端服务运行正常"
        
        # 检查服务健康状态
        STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" "$BACKEND_URL/api/admin/stats")
        
        if [ "$STATUS_CODE" != "200" ]; then
            log_alert "后端服务响应异常: HTTP $STATUS_CODE"
            send_alert "后端服务响应异常" "后端服务返回 HTTP $STATUS_CODE"
            return 1
        fi
        
        return 0
    else
        log_alert "后端服务未运行"
        send_alert "后端服务未运行" "检测到后端服务进程不存在"
        return 1
    fi
}

# 检查 API 错误率
check_api_error_rate() {
    RESPONSE=$(curl -s "$BACKEND_URL/admin/api-monitor?timeRange=1h" 2>/dev/null)
    ERROR_RATE=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('summary', {}).get('errorRate', 0))" 2>/dev/null || echo "0")
    ERROR_INT=${ERROR_RATE%.*}
    
    if [ $ERROR_INT -gt $ERROR_RATE_THRESHOLD ]; then
        log_alert "API 错误率过高: ${ERROR_RATE}%"
        send_alert "API 错误率过高" "当前 API 错误率为 ${ERROR_RATE}%，超过阈值 ${ERROR_RATE_THRESHOLD}%"
        return 1
    else
        log "API 错误率正常: ${ERROR_RATE}%"
        return 0
    fi
}

# 检查 API 响应时间
check_api_response_time() {
    RESPONSE=$(curl -s "$BACKEND_URL/admin/api-monitor?timeRange=1h" 2>/dev/null)
    RESPONSE_TIME=$(echo "$RESPONSE" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('data', {}).get('summary', {}).get('avgResponseTime', 0))" 2>/dev/null || echo "0")
    RESPONSE_INT=${RESPONSE_TIME%.*}
    
    if [ $RESPONSE_INT -gt $RESPONSE_TIME_THRESHOLD ]; then
        log_alert "API 响应时间过长: ${RESPONSE_TIME}ms"
        send_alert "API 响应时间过长" "当前 API 平均响应时间为 ${RESPONSE_TIME}ms，超过阈值 ${RESPONSE_TIME_THRESHOLD}ms"
        return 1
    else
        log "API 响应时间正常: ${RESPONSE_TIME}ms"
        return 0
    fi
}

# 检查数据库连接
check_database() {
    DB_PATH="/workspace/projects/admin-backend/data/lingzhi_ecosystem.db"
    
    if [ -f "$DB_PATH" ]; then
        # 检查数据库文件大小
        DB_SIZE=$(du -h "$DB_PATH" | awk '{print $1}')
        log "数据库文件大小: $DB_SIZE"
        
        # 检查数据库是否可访问
        if python3 -c "import sqlite3; conn = sqlite3.connect('$DB_PATH'); cursor = conn.cursor(); cursor.execute('SELECT 1'); conn.close()" 2>/dev/null; then
            log "数据库连接正常"
            return 0
        else
            log_alert "数据库连接失败"
            send_alert "数据库连接失败" "无法连接到数据库文件: $DB_PATH"
            return 1
        fi
    else
        log_alert "数据库文件不存在: $DB_PATH"
        send_alert "数据库文件不存在" "数据库文件未找到: $DB_PATH"
        return 1
    fi
}

# 发送告警
send_alert() {
    local subject="$1"
    local message="$2"
    
    log "发送告警: $subject"
    
    # 这里可以集成邮件、短信或钉钉告警
    # 示例：邮件告警
    if command -v mail &> /dev/null; then
        echo "$message" | mail -s "[告警] $subject" "$ALERT_EMAIL"
    fi
    
    # 示例：钉钉告警
    # curl -X POST "$DINGTALK_WEBHOOK" -H "Content-Type: application/json" -d "{\"text\": {\"content\": \"$subject: $message\"}}"
}

# 生成监控报告
generate_report() {
    log "生成监控报告..."
    
    REPORT_FILE="/var/log/monitoring_report_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
========================================
系统监控报告
========================================
时间: $(date '+%Y-%m-%d %H:%M:%S')

系统资源:
- CPU 使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')
- 内存使用率: $(free | grep Mem | awk '{printf("%.1f%%"), $3/$2 * 100.0}')
- 磁盘使用率: $(df -h / | awk 'NR==2 {print $5}')
- 负载平均值: $(uptime | awk -F'load average:' '{print $2}')

服务状态:
- 后端服务: $(pgrep -f "gunicorn\|python.*app.py" > /dev/null && echo "运行中" || echo "未运行")
- 数据库: $(python3 -c "import sqlite3; conn = sqlite3.connect('/workspace/projects/admin-backend/data/lingzhi_ecosystem.db'); conn.close()" 2>/dev/null && echo "正常" || echo "异常")

网络状态:
- 监听端口: $(netstat -tuln | grep LISTEN | wc -l)
- 活动连接: $(netstat -tuln | grep ESTABLISHED | wc -l)

最近错误日志 (5条):
$(tail -5 /var/log/gunicorn/error.log 2>/dev/null || echo "无日志")

========================================
EOF
    
    log "监控报告已生成: $REPORT_FILE"
}

# 主监控循环
monitor_loop() {
    log "=========================================="
    log "开始系统监控"
    log "=========================================="
    
    while true; do
        # 检查各项指标
        check_cpu
        check_memory
        check_disk
        check_backend_service
        check_api_error_rate
        check_api_response_time
        check_database
        
        # 每小时生成一次报告
        if [ $(date +%M) -eq 0 ]; then
            generate_report
        fi
        
        # 每 5 分钟检查一次
        sleep 300
    done
}

# 主函数
main() {
    case "${1:-monitor}" in
        cpu)
            check_cpu
            ;;
        memory)
            check_memory
            ;;
        disk)
            check_disk
            ;;
        backend)
            check_backend_service
            ;;
        api)
            check_api_error_rate
            check_api_response_time
            ;;
        database)
            check_database
            ;;
        report)
            generate_report
            ;;
        monitor)
            monitor_loop
            ;;
        once)
            log "执行一次完整监控检查"
            check_cpu
            check_memory
            check_disk
            check_backend_service
            check_api_error_rate
            check_api_response_time
            check_database
            generate_report
            ;;
        *)
            echo "用法: $0 {cpu|memory|disk|backend|api|database|report|monitor|once}"
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
