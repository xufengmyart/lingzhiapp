#!/bin/bash

################################################################################
# 灵值生态园 - 健康检查和自动修复脚本
# 用途：定期检查服务状态，自动修复问题
# 建议：添加到 crontab 每分钟运行一次
# 作者：Coze Coding
# 版本：v1.0
# 日期：2026-02-11
################################################################################

set -e

# 配置变量
DOMAIN="meiyueart.com"
FLASK_PORT=8080
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
SERVICE_NAME="flask-app"
LOG_FILE="/var/log/health-check.log"
ALERT_WEBHOOK=""  # 可选：配置告警 Webhook URL

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 日志函数
log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> $LOG_FILE
}

log_info() {
    log "INFO" "$@"
    echo -e "${GREEN}[INFO]${NC} $@"
}

log_warning() {
    log "WARNING" "$@"
    echo -e "${YELLOW}[WARNING]${NC} $@"
}

log_error() {
    log "ERROR" "$@"
    echo -e "${RED}[ERROR]${NC} $@"
}

# 发送告警
send_alert() {
    local message="$@"
    log "ALERT" "$message"
    
    if [ -n "$ALERT_WEBHOOK" ]; then
        curl -X POST "$ALERT_WEBHOOK" \
            -H "Content-Type: application/json" \
            -d "{\"text\": \"$message\"}" \
            >/dev/null 2>&1
    fi
}

# 检查端口是否监听
check_port() {
    local port=$1
    local service_name=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_info "$service_name (端口 $port) 正常"
        return 0
    else
        log_error "$service_name (端口 $port) 未运行"
        return 1
    fi
}

# 检查服务状态
check_service() {
    local service_name=$1
    
    if systemctl is-active --quiet $service_name; then
        log_info "$service_name 服务正常"
        return 0
    else
        log_error "$service_name 服务未运行"
        return 1
    fi
}

# 测试 HTTP 响应
test_http() {
    local url=$1
    local service_name=$2
    
    if curl -f -s -o /dev/null "$url" --max-time 5; then
        log_info "$service_name HTTP 响应正常"
        return 0
    else
        log_error "$service_name HTTP 响应异常"
        return 1
    fi
}

# 重启服务
restart_service() {
    local service_name=$1
    
    log_warning "正在重启 $service_name..."
    systemctl restart $service_name
    
    sleep 3
    
    if systemctl is-active --quiet $service_name; then
        log_info "$service_name 重启成功"
        send_alert "$service_name 已自动重启"
        return 0
    else
        log_error "$service_name 重启失败"
        send_alert "⚠️ $service_name 重启失败，需要人工干预"
        return 1
    fi
}

# 主健康检查逻辑
main() {
    local issues=0
    
    log_info "开始健康检查..."
    
    # 1. 检查 Flask 服务
    if ! check_service $SERVICE_NAME; then
        log_warning "Flask 服务停止，尝试重启..."
        if restart_service $SERVICE_NAME; then
            log_info "Flask 服务已恢复"
        else
            issues=$((issues + 1))
        fi
    fi
    
    # 2. 检查 Flask 端口
    if ! check_port $FLASK_PORT "Flask API"; then
        log_warning "Flask 端口 $FLASK_PORT 未监听，尝试重启服务..."
        if restart_service $SERVICE_NAME; then
            log_info "Flask 端口已恢复"
        else
            issues=$((issues + 1))
        fi
    fi
    
    # 3. 检查 Flask 健康接口
    if ! test_http "http://localhost:$FLASK_PORT/api/health" "Flask 健康检查"; then
        log_warning "Flask 健康检查失败，尝试重启服务..."
        if restart_service $SERVICE_NAME; then
            log_info "Flask 健康检查已恢复"
        else
            issues=$((issues + 1))
        fi
    fi
    
    # 4. 检查 Nginx 服务
    if ! check_service nginx; then
        log_warning "Nginx 服务停止，尝试重启..."
        if restart_service nginx; then
            log_info "Nginx 服务已恢复"
        else
            issues=$((issues + 1))
        fi
    fi
    
    # 5. 检查 Nginx 端口
    if ! check_port $NGINX_HTTP_PORT "Nginx HTTP"; then
        log_warning "Nginx HTTP 端口未监听，尝试重启..."
        if restart_service nginx; then
            log_info "Nginx HTTP 端口已恢复"
        else
            issues=$((issues + 1))
        fi
    fi
    
    if ! check_port $NGINX_HTTPS_PORT "Nginx HTTPS"; then
        log_warning "Nginx HTTPS 端口未监听，尝试重启..."
        if restart_service nginx; then
            log_info "Nginx HTTPS 端口已恢复"
        else
            issues=$((issues + 1))
        fi
    fi
    
    # 6. 检查 HTTPS 访问
    if ! test_http "https://localhost/api/health" "HTTPS API"; then
        log_warning "HTTPS API 访问失败"
        issues=$((issues + 1))
    fi
    
    # 7. 检查磁盘空间
    local disk_usage=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
    if [ $disk_usage -gt 90 ]; then
        log_warning "磁盘空间不足: ${disk_usage}%"
        send_alert "⚠️ 磁盘空间不足: ${disk_usage}%"
        issues=$((issues + 1))
    fi
    
    # 8. 检查内存使用
    local mem_usage=$(free | awk 'NR==2 {printf "%.0f", $3/$2*100}')
    if [ $mem_usage -gt 90 ]; then
        log_warning "内存使用过高: ${mem_usage}%"
        issues=$((issues + 1))
    fi
    
    # 总结
    if [ $issues -eq 0 ]; then
        log_info "健康检查完成，所有服务正常"
    else
        log_error "健康检查发现 $issues 个问题"
        send_alert "⚠️ 健康检查发现 $issues 个问题，请查看日志: $LOG_FILE"
    fi
    
    return $issues
}

# 执行健康检查
main
exit $?
