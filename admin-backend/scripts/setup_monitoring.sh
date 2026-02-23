#!/bin/bash
# ============================================
# 灵值生态园 - 监控告警配置脚本
# Lingzhi Ecosystem - Monitoring Setup Script
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

echo -e "${BLUE}"
echo "============================================"
echo "  灵值生态园 - 监控告警配置"
echo "  Lingzhi Ecosystem - Monitoring Setup"
echo "============================================"
echo -e "${NC}"

PROJECT_DIR="/workspace/projects/admin-backend"
MONITOR_DIR="$PROJECT_DIR/monitoring"

# 1. 创建监控目录
log_info "创建监控目录..."
mkdir -p "$MONITOR_DIR/scripts"
log_success "监控目录已创建"

# 2. 创建健康检查脚本
log_info "创建健康检查脚本..."
cat > "$MONITOR_DIR/scripts/health_check.sh" << 'EOF'
#!/bin/bash
# 健康检查脚本

PROJECT_DIR="/workspace/projects/admin-backend"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"
NOTIFICATION_WEBHOOK=""

# 记录日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# 发送通知
send_notification() {
    local message="$1"
    log "发送通知: $message"

    # 这里可以添加发送到钉钉、企业微信等的通知逻辑
    # curl -X POST "$NOTIFICATION_WEBHOOK" -d "{\"text\": \"$message\"}"
}

# 检查服务健康
check_service() {
    local service_name="$1"
    local url="$2"
    local expected_status="${3:-200}"

    log "检查 $service_name: $url"

    local status_code=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$status_code" -eq "$expected_status" ]; then
        log "✅ $service_name 正常 (HTTP $status_code)"
        return 0
    else
        log "❌ $service_name 异常 (HTTP $status_code)"
        send_notification "⚠️ 服务异常: $service_name 返回 HTTP $status_code"
        return 1
    fi
}

# 检查进程
check_process() {
    local process_name="$1"
    local service_name="$2"

    log "检查 $service_name 进程: $process_name"

    if pgrep -f "$process_name" > /dev/null; then
        log "✅ $service_name 进程运行正常"
        return 0
    else
        log "❌ $service_name 进程未运行"
        send_notification "⚠️ 进程异常: $service_name 未运行"
        return 1
    fi
}

# 检查磁盘空间
check_disk() {
    local threshold="${1:-80}"

    log "检查磁盘空间..."

    local disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')

    if [ "$disk_usage" -lt "$threshold" ]; then
        log "✅ 磁盘空间正常 (${disk_usage}%)"
        return 0
    else
        log "❌ 磁盘空间不足 (${disk_usage}%)"
        send_notification "⚠️ 磁盘空间不足: ${disk_usage}%"
        return 1
    fi
}

# 执行所有检查
log "开始健康检查..."

check_service "Flask 应用" "http://localhost:8080/api/health" "200"
check_process "gunicorn" "Gunicorn 应用"
check_process "nginx" "Nginx 服务"
check_disk 80

log "健康检查完成"
EOF

chmod +x "$MONITOR_DIR/scripts/health_check.sh"
log_success "健康检查脚本已创建"

# 3. 创建性能监控脚本
log_info "创建性能监控脚本..."
cat > "$MONITOR_DIR/scripts/performance_monitor.sh" << 'EOF'
#!/bin/bash
# 性能监控脚本

PROJECT_DIR="/workspace/projects/admin-backend"
MONITOR_LOG="$PROJECT_DIR/logs/performance.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$MONITOR_LOG"
}

# 监控系统资源
log "性能监控开始..."

# CPU 使用率
cpu_usage=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
log "CPU 使用率: ${cpu_usage}%"

# 内存使用
mem_usage=$(free | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')
log "内存使用: ${mem_usage}"

# 磁盘使用
disk_usage=$(df -h / | awk 'NR==2 {print $5}')
log "磁盘使用: ${disk_usage}"

# 应用进程数
gunicorn_count=$(pgrep -f "gunicorn" | wc -l)
log "Gunicorn 进程数: ${gunicorn_count}"

# 数据库大小
db_size=$(du -h "$PROJECT_DIR/data/lingzhi_ecosystem.db" | cut -f1)
log "数据库大小: ${db_size}"

# 日志大小
log_size=$(du -sh "$PROJECT_DIR/logs" | cut -f1)
log "日志大小: ${log_size}"

log "性能监控完成"
EOF

chmod +x "$MONITOR_DIR/scripts/performance_monitor.sh"
log_success "性能监控脚本已创建"

# 4. 配置定时监控
log_info "配置定时监控..."

# 健康检查：每 5 分钟
CRON_HEALTH="*/5 * * * * $MONITOR_DIR/scripts/health_check.sh"

# 性能监控：每 10 分钟
CRON_PERFORMANCE="*/10 * * * * $MONITOR_DIR/scripts/performance_monitor.sh"

# 添加到 crontab
(crontab -l 2>/dev/null | grep -v "$MONITOR_DIR/scripts"; echo "$CRON_HEALTH"; echo "$CRON_PERFORMANCE") | crontab -

log_success "定时监控已配置"

# 5. 创建日志轮转配置
log_info "配置日志轮转..."
cat > /etc/logrotate.d/meiyueart << EOF
$PROJECT_DIR/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        # 重启应用（可选）
        # kill -HUP $(cat $PROJECT_DIR/tmp/app.pid 2>/dev/null) || true
    endscript
}
EOF

log_success "日志轮转配置已创建"

# 6. 创建监控仪表板脚本（可选）
log_info "创建监控仪表板脚本..."
cat > "$MONITOR_DIR/scripts/monitor_dashboard.sh" << 'EOF'
#!/bin/bash
# 监控仪表板

PROJECT_DIR="/workspace/projects/admin-backend"
LOG_FILE="$PROJECT_DIR/logs/monitor.log"

clear
echo "============================================"
echo "  灵值生态园 - 监控仪表板"
echo "============================================"
echo ""

# 服务状态
echo "📊 服务状态"
echo "----------------------------------------"
if curl -s http://localhost:8080/api/health > /dev/null; then
    echo "✅ Flask 应用: 正常"
else
    echo "❌ Flask 应用: 异常"
fi

if systemctl is-active --quiet nginx; then
    echo "✅ Nginx: 正常"
else
    echo "❌ Nginx: 异常"
fi

if systemctl is-active --quiet redis-server; then
    echo "✅ Redis: 正常"
else
    echo "❌ Redis: 异常"
fi
echo ""

# 系统资源
echo "💻 系统资源"
echo "----------------------------------------"
echo "CPU 使用率: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)%"
echo "内存使用: $(free | awk 'NR==2{printf "%.2f%%", $3*100/$2 }')"
echo "磁盘使用: $(df -h / | awk 'NR==2 {print $5}')"
echo "负载: $(uptime | awk -F'load average:' '{print $2}')"
echo ""

# 应用进程
echo "🔄 应用进程"
echo "----------------------------------------"
GUNICORN_COUNT=$(pgrep -f "gunicorn" | wc -l)
echo "Gunicorn 进程: $GUNICORN_COUNT"
if [ -f "$PROJECT_DIR/tmp/app.pid" ]; then
    PID=$(cat "$PROJECT_DIR/tmp/app.pid")
    if ps -p $PID > /dev/null 2>&1; then
        echo "主进程 PID: $PID (运行中)"
    else
        echo "主进程 PID: $PID (未运行)"
    fi
fi
echo ""

# 数据库信息
echo "🗄️  数据库"
echo "----------------------------------------"
DB_SIZE=$(du -h "$PROJECT_DIR/data/lingzhi_ecosystem.db" 2>/dev/null | cut -f1)
echo "数据库大小: ${DB_SIZE:-N/A}"
BACKUP_COUNT=$(find "$PROJECT_DIR/backups" -name "*.db.gz" 2>/dev/null | wc -l)
echo "备份文件数: $BACKUP_COUNT"
echo ""

# 最近日志
echo "📝 最近日志（最后 5 行）"
echo "----------------------------------------"
tail -5 "$PROJECT_DIR/logs/app.log" 2>/dev/null || echo "无日志"
echo ""

echo "============================================"
echo "按 Ctrl+C 退出，自动刷新..."
echo "============================================"
EOF

chmod +x "$MONITOR_DIR/scripts/monitor_dashboard.sh"
log_success "监控仪表板脚本已创建"

# 7. 完成
echo ""
log_success "监控告警配置完成！"
echo ""
echo "监控配置:"
echo "  - 健康检查: 每 5 分钟"
echo "  - 性能监控: 每 10 分钟"
echo "  - 日志轮转: 每天轮转，保留 30 天"
echo ""
echo "监控脚本位置:"
echo "  - 健康检查: $MONITOR_DIR/scripts/health_check.sh"
echo "  - 性能监控: $MONITOR_DIR/scripts/performance_monitor.sh"
echo "  - 监控仪表板: $MONITOR_DIR/scripts/monitor_dashboard.sh"
echo ""
echo "管理命令:"
echo "  - 查看定时任务: crontab -l"
echo "  - 手动健康检查: $MONITOR_DIR/scripts/health_check.sh"
echo "  - 手动性能监控: $MONITOR_DIR/scripts/performance_monitor.sh"
echo "  - 启动监控仪表板: $MONITOR_DIR/scripts/monitor_dashboard.sh"
echo "  - 查看监控日志: tail -f $PROJECT_DIR/logs/monitor.log"
echo ""
log_success "配置完成！"
