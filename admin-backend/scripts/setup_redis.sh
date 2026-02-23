#!/bin/bash
# ============================================
# 灵值生态园 - Redis 缓存配置脚本
# Lingzhi Ecosystem - Redis Setup Script
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

# Redis 配置
REDIS_HOST="127.0.0.1"
REDIS_PORT="6379"
REDIS_PASSWORD=""
REDIS_MAX_MEMORY="256mb"

echo -e "${BLUE}"
echo "============================================"
echo "  灵值生态园 - Redis 缓存配置"
echo "  Lingzhi Ecosystem - Redis Setup"
echo "============================================"
echo -e "${NC}"

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 root 权限运行此脚本"
    exit 1
fi

# 1. 安装 Redis
log_info "安装 Redis..."
if ! command -v redis-server &> /dev/null; then
    apt-get update -y
    apt-get install -y redis-server
    log_success "Redis 安装完成"
else
    log_info "Redis 已安装"
fi

# 2. 配置 Redis
log_info "配置 Redis..."
REDIS_CONF="/etc/redis/redis.conf"

# 备份原配置
if [ -f "$REDIS_CONF" ]; then
    cp "$REDIS_CONF" "$REDIS_CONF.backup.$(date +%Y%m%d_%H%M%S)"
    log_success "原配置已备份"
fi

# 更新配置
sed -i "s/^bind 127.0.0.1 ::1/bind 127.0.0.1/" "$REDIS_CONF"
sed -i "s/^# maxmemory <bytes>/maxmemory $REDIS_MAX_MEMORY/" "$REDIS_CONF"
sed -i "s/^# maxmemory-policy noeviction/maxmemory-policy allkeys-lru/" "$REDIS_CONF"
sed -i "s/^save 900 1/# save 900 1/" "$REDIS_CONF"
sed -i "s/^save 300 10/# save 300 10/" "$REDIS_CONF"
sed -i "s/^save 60 10000/# save 60 10000/" "$REDIS_CONF"

log_success "Redis 配置已更新"

# 3. 启动 Redis
log_info "启动 Redis..."
systemctl enable redis-server
systemctl start redis-server

if [ $? -eq 0 ]; then
    log_success "Redis 已启动"
else
    log_error "Redis 启动失败"
    exit 1
fi

# 4. 验证 Redis
log_info "验证 Redis..."
if redis-cli ping > /dev/null 2>&1; then
    log_success "Redis 运行正常"
    redis-cli INFO | head -20
else
    log_error "Redis 运行异常"
    exit 1
fi

# 5. 更新应用配置
log_info "更新应用配置..."
PROJECT_DIR="/workspace/projects/admin-backend"
ENV_FILE="$PROJECT_DIR/.env"

if [ -f "$ENV_FILE" ]; then
    # 添加或更新 Redis 配置
    if grep -q "REDIS_HOST=" "$ENV_FILE"; then
        sed -i "s/^REDIS_HOST=.*/REDIS_HOST=$REDIS_HOST/" "$ENV_FILE"
    else
        echo "REDIS_HOST=$REDIS_HOST" >> "$ENV_FILE"
    fi

    if grep -q "REDIS_PORT=" "$ENV_FILE"; then
        sed -i "s/^REDIS_PORT=.*/REDIS_PORT=$REDIS_PORT/" "$ENV_FILE"
    else
        echo "REDIS_PORT=$REDIS_PORT" >> "$ENV_FILE"
    fi

    if grep -q "REDIS_PASSWORD=" "$ENV_FILE"; then
        sed -i "s/^REDIS_PASSWORD=.*/REDIS_PASSWORD=$REDIS_PASSWORD/" "$ENV_FILE"
    else
        echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> "$ENV_FILE"
    fi

    log_success "应用配置已更新"
else
    log_warning "环境变量文件不存在: $ENV_FILE"
fi

# 6. 重启应用
log_info "重启应用服务..."
PROJECT_PID_FILE="$PROJECT_DIR/tmp/app.pid"

if [ -f "$PROJECT_PID_FILE" ]; then
    PID=$(cat "$PROJECT_PID_FILE")
    if ps -p $PID > /dev/null 2>&1; then
        kill $PID
        log_success "应用已停止 (PID: $PID)"
        sleep 3
    fi
fi

# 重新启动应用
cd "$PROJECT_DIR"
nohup gunicorn -w 4 -b 0.0.0.0:8080 "app:create_app()" > logs/app.log 2>&1 &
NEW_PID=$!
echo $NEW_PID > "$PROJECT_DIR/tmp/app.pid"
log_success "应用已重启 (PID: $NEW_PID)"

# 7. 完成
echo ""
log_success "Redis 缓存配置完成！"
echo ""
echo "Redis 配置:"
echo "  - 地址: $REDIS_HOST:$REDIS_PORT"
echo "  - 密码: ${REDIS_PASSWORD:-无}"
echo "  - 最大内存: $REDIS_MAX_MEMORY"
echo "  - 淘汰策略: allkeys-lru"
echo ""
echo "管理命令:"
echo "  - 启动: systemctl start redis-server"
echo "  - 停止: systemctl stop redis-server"
echo "  - 重启: systemctl restart redis-server"
echo "  - 状态: systemctl status redis-server"
echo "  - 连接: redis-cli"
echo "  - 监控: redis-cli monitor"
echo ""
log_success "配置完成！"
