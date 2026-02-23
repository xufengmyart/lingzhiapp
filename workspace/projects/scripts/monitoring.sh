#!/bin/bash
# 监控告警脚本 - 集成邮件告警

# 配置
LOG_DIR="/var/log/monitoring"
ALERT_LOG="$LOG_DIR/alerts.log"
BACKEND_LOG="/tmp/backend.log"

# 告警配置
CPU_THRESHOLD=80
MEMORY_THRESHOLD=80
DISK_THRESHOLD=85
API_ERROR_RATE_THRESHOLD=10  # 百分比

# 邮件配置（从环境变量读取）
SMTP_HOST="${SMTP_HOST:-smtp.example.com}"
SMTP_PORT="${SMTP_PORT:-587}"
SMTP_USER="${SMTP_USER:-}"
SMTP_PASSWORD="${SMTP_PASSWORD:-}"
SMTP_FROM="${SMTP_FROM:-noreply@meiyueart.com}"
ALERT_EMAILS="${ALERT_EMAILS:-admin@meiyueart.com}"

# 创建日志目录
mkdir -p "$LOG_DIR"

# 发送邮件函数
send_email() {
    local subject="$1"
    local body="$2"
    
    if [ -z "$SMTP_USER" ]; then
        echo "$(date) [邮件] 未配置SMTP，跳过发送" >> "$ALERT_LOG"
        return 1
    fi
    
    # 使用sendmail或mail命令发送邮件
    if command -v sendmail &> /dev/null; then
        echo "Subject: $subject\n\n$body" | sendmail -t "$ALERT_EMAILS"
    elif command -v mail &> /dev/null; then
        echo "$body" | mail -s "$subject" "$ALERT_EMAILS"
    else
        echo "$(date) [邮件] 未找到sendmail或mail命令" >> "$ALERT_LOG"
        return 1
    fi
    
    echo "$(date) [邮件] 已发送: $subject" >> "$ALERT_LOG"
}

# 检查CPU使用率
check_cpu() {
    local cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
    cpu_usage=${cpu_usage%.*}  # 取整数部分
    
    if [ "$cpu_usage" -gt "$CPU_THRESHOLD" ]; then
        local message="CPU使用率过高: ${cpu_usage}% (阈值: ${CPU_THRESHOLD}%)"
        echo "$(date) [警告] $message" >> "$ALERT_LOG"
        send_email "[警告] CPU使用率过高" "$message"
        return 1
    fi
    return 0
}

# 检查内存使用率
check_memory() {
    local memory_usage=$(free | grep Mem | awk '{printf("%.0f", ($3/$2)*100)}')
    
    if [ "$memory_usage" -gt "$MEMORY_THRESHOLD" ]; then
        local message="内存使用率过高: ${memory_usage}% (阈值: ${MEMORY_THRESHOLD}%)"
        echo "$(date) [警告] $message" >> "$ALERT_LOG"
        send_email "[警告] 内存使用率过高" "$message"
        return 1
    fi
    return 0
}

# 检查磁盘使用率
check_disk() {
    local disk_usage=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)
    
    if [ "$disk_usage" -gt "$DISK_THRESHOLD" ]; then
        local message="磁盘使用率过高: ${disk_usage}% (阈值: ${DISK_THRESHOLD}%)"
        echo "$(date) [警告] $message" >> "$ALERT_LOG"
        send_email "[警告] 磁盘使用率过高" "$message"
        return 1
    fi
    return 0
}

# 检查API错误率
check_api_error_rate() {
    if [ ! -f "$BACKEND_LOG" ]; then
        return 0
    fi
    
    # 统计最近1小时的API请求和错误
    local total=$(grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" "$BACKEND_LOG" | wc -l)
    local errors=$(grep "$(date -d '1 hour ago' '+%Y-%m-%d %H')" "$BACKEND_LOG" | grep -i "error\|exception" | wc -l)
    
    if [ "$total" -gt 0 ]; then
        local error_rate=$((errors * 100 / total))
        
        if [ "$error_rate" -gt "$API_ERROR_RATE_THRESHOLD" ]; then
            local message="API错误率过高: ${error_rate}% (错误: ${errors}, 总请求: ${total})"
            echo "$(date) [警告] $message" >> "$ALERT_LOG"
            send_email "[警告] API错误率过高" "$message"
            return 1
        fi
    fi
    return 0
}

# 检查后端服务状态
check_backend_service() {
    if ! pgrep -f "python.*app.py" > /dev/null; then
        local message="后端服务未运行，请检查！"
        echo "$(date) [严重] $message" >> "$ALERT_LOG"
        send_email "[严重] 后端服务停止" "$message"
        return 1
    fi
    return 0
}

# 生成监控报告
generate_report() {
    local report_file="$LOG_DIR/report_$(date +%Y%m%d_%H%M%S).txt"
    
    {
        echo "========================================="
        echo "系统监控报告"
        echo "========================================="
        echo "时间: $(date)"
        echo ""
        echo "系统状态:"
        echo "  CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}')"
        echo "  内存: $(free -h | grep Mem | awk '{print $3 "/" $2}')"
        echo "  磁盘: $(df -h / | tail -1 | awk '{print $3 "/" $2 " (" $5 ")"}')"
        echo "  负载: $(uptime | awk -F'load average:' '{print $2}')"
        echo ""
        echo "服务状态:"
        if pgrep -f "python.*app.py" > /dev/null; then
            echo "  后端服务: 运行中 (PID: $(pgrep -f "python.*app.py" | head -1))"
        else
            echo "  后端服务: 未运行"
        fi
        echo ""
        echo "最近告警 (最近10条):"
        tail -10 "$ALERT_LOG" 2>/dev/null || echo "  无告警记录"
    } > "$report_file"
    
    echo "报告已生成: $report_file"
}

# 主监控函数
monitor() {
    echo "$(date) [监控] 开始监控..." >> "$ALERT_LOG"
    
    check_cpu
    check_memory
    check_disk
    check_api_error_rate
    check_backend_service
    
    echo "$(date) [监控] 监控周期完成" >> "$ALERT_LOG"
}

# 使用方法
case "$1" in
    monitor)
        # 启动持续监控（每5分钟）
        echo "启动持续监控..."
        while true; do
            monitor
            sleep 300
        done
        ;;
    once)
        # 单次检查
        monitor
        ;;
    report)
        # 生成报告
        generate_report
        ;;
    *)
        echo "使用方法:"
        echo "  $0 monitor   - 持续监控"
        echo "  $0 once      - 单次检查"
        echo "  $0 report    - 生成报告"
        exit 1
        ;;
esac
