#!/bin/bash
# 生产环境一键部署脚本

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/workspace/projects"
BACKEND_DIR="$PROJECT_DIR/admin-backend"
FRONTEND_DIR="$PROJECT_DIR/web-app"
LOG_FILE="$PROJECT_DIR/deploy_production.log"

# 日志函数
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

# 检查环境
check_environment() {
    log_info "检查生产环境..."
    
    # 检查 Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    
    # 检查 Gunicorn
    if ! command -v gunicorn &> /dev/null; then
        log_warning "Gunicorn 未安装，开始安装..."
        pip3 install -q gunicorn
    fi
    
    # 检查 Nginx
    if ! command -v nginx &> /dev/null; then
        log_warning "Nginx 未安装，跳过 Nginx 配置"
    fi
    
    log_success "环境检查通过"
}

# 停止旧服务
stop_services() {
    log_info "停止旧服务..."
    
    # 停止旧的后端进程
    pkill -f "python.*app.py" || true
    pkill -f "gunicorn" || true
    sleep 3
    
    log_success "旧服务已停止"
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖..."
    
    # 安装后端依赖
    cd "$PROJECT_DIR"
    if [ -f "requirements.txt" ]; then
        pip3 install -q -r requirements.txt
    fi
    
    # 确保关键依赖已安装
    pip3 install -q gunicorn flask flask-cors flask-socketio python-dotenv bcrypt supervisor
    
    # 安装前端依赖
    cd "$FRONTEND_DIR"
    if [ -f "package.json" ]; then
        npm install
    fi
    
    log_success "依赖安装完成"
}

# 构建前端
build_frontend() {
    log_info "构建前端..."
    
    cd "$FRONTEND_DIR"
    
    # 生成版本号
    npm run generate-version || log_warning "版本号生成失败，继续构建..."
    
    # 清理旧构建
    rm -rf dist
    
    # 构建
    npm run build
    
    # 验证构建
    if [ ! -d "dist" ]; then
        log_error "前端构建失败"
        exit 1
    fi
    
    log_success "前端构建完成"
}

# 配置生产环境
configure_production() {
    log_info "配置生产环境..."
    
    # 复制生产环境配置
    cd "$BACKEND_DIR"
    if [ -f ".env.production" ]; then
        cp .env.production .env
        log_success "生产环境配置已加载"
    else
        log_warning "未找到生产环境配置文件，使用默认配置"
    fi
    
    # 创建必要的目录
    mkdir -p /var/log/lingzhi
    mkdir -p /var/log/gunicorn
    mkdir -p /var/log/supervisor
    mkdir -p /workspace/backups
    
    log_success "生产环境配置完成"
}

# 启动服务 (使用 Gunicorn)
start_gunicorn() {
    log_info "使用 Gunicorn 启动后端服务..."
    
    cd "$BACKEND_DIR"
    
    # 使用 Gunicorn 启动
    nohup gunicorn -c "$PROJECT_DIR/gunicorn_config.py" app:app > /var/log/gunicorn/gunicorn.log 2>&1 &
    GUNICORN_PID=$!
    
    # 保存 PID
    echo $GUNICORN_PID > /tmp/gunicorn.pid
    
    # 等待服务启动
    sleep 5
    
    # 验证服务是否启动成功
    if ps -p $GUNICORN_PID > /dev/null; then
        log_success "Gunicorn 服务启动成功 (PID: $GUNICORN_PID)"
    else
        log_error "Gunicorn 服务启动失败"
        tail -50 /var/log/gunicorn/gunicorn.log
        exit 1
    fi
}

# 配置 Nginx
configure_nginx() {
    log_info "配置 Nginx..."
    
    if ! command -v nginx &> /dev/null; then
        log_warning "Nginx 未安装，跳过 Nginx 配置"
        return
    fi
    
    # 创建 Nginx 配置文件
    NGINX_CONF="/etc/nginx/sites-available/lingzhi-backend"
    
    cat > "$NGINX_CONF" << EOF
# 灵值生态园后端服务 Nginx 配置
upstream lingzhi_backend {
    server 127.0.0.1:5000;
    keepalive 64;
}

server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;
    
    # 日志
    access_log /var/log/nginx/lingzhi-backend-access.log;
    error_log /var/log/nginx/lingzhi-backend-error.log;
    
    # 请求体大小限制
    client_max_body_size 50M;
    
    # 静态文件
    location /uploads/ {
        alias /workspace/projects/admin-backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /dist/ {
        alias /workspace/projects/web-app/dist/;
        expires 7d;
        add_header Cache-Control "public";
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://lingzhi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # WebSocket 支持
    location /socket.io/ {
        proxy_pass http://lingzhi_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
    
    # 前端路由
    location / {
        root /workspace/projects/web-app/dist;
        try_files $uri $uri/ /index.html;
    }
}
EOF
    
    # 启用站点
    ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
    
    # 测试配置
    if nginx -t; then
        systemctl reload nginx
        log_success "Nginx 配置已更新"
    else
        log_error "Nginx 配置测试失败"
    fi
}

# 配置日志轮转
configure_logrotate() {
    log_info "配置日志轮转..."
    
    cat > /etc/logrotate.d/lingzhi << EOF
/var/log/lingzhi/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload lingzhi-backend.service
    endscript
}

/var/log/gunicorn/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 root root
    sharedscripts
    postrotate
        systemctl reload gunicorn
    endscript
}
EOF
    
    log_success "日志轮转配置完成"
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    cd "$PROJECT_DIR"
    if [ -f "test_complete.sh" ]; then
        if bash test_complete.sh; then
            log_success "所有测试通过"
        else
            log_warning "部分测试失败，但继续部署"
        fi
    else
        log_warning "测试脚本不存在，跳过测试"
    fi
}

# 配置监控
configure_monitoring() {
    log_info "配置监控..."
    
    # 设置进程监控
    cd "$PROJECT_DIR"
    chmod +x scripts/service-monitor.sh
    
    log_success "监控配置完成"
}

# 创建备份
create_backup() {
    log_info "创建备份..."
    
    BACKUP_DIR="/workspace/backups"
    BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    
    mkdir -p "$BACKUP_DIR"
    
    tar -czf "$BACKUP_FILE" \
        "$BACKEND_DIR/data" \
        "$BACKEND_DIR/uploads" \
        "$FRONTEND_DIR/dist" \
        2>/dev/null || true
    
    # 保留最近 7 天的备份
    find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete
    
    log_success "备份已创建: $BACKUP_FILE"
}

# 主部署流程
main() {
    log "=========================================="
    log "开始生产环境部署"
    log "=========================================="
    
    # 检查环境
    check_environment
    
    # 停止旧服务
    stop_services
    
    # 安装依赖
    install_dependencies
    
    # 构建前端
    build_frontend
    
    # 配置生产环境
    configure_production
    
    # 启动服务
    start_gunicorn
    
    # 配置 Nginx
    configure_nginx
    
    # 配置日志轮转
    configure_logrotate
    
    # 运行测试
    run_tests
    
    # 配置监控
    configure_monitoring
    
    # 创建备份
    create_backup
    
    log "=========================================="
    log_success "生产环境部署完成！"
    log "=========================================="
    log ""
    log "服务信息："
    log "  - 后端地址: http://localhost:5000"
    log "  - Gunicorn 进程: $(cat /tmp/gunicorn.pid 2>/dev/null || echo 'N/A')"
    log "  - 前端构建: $FRONTEND_DIR/dist"
    log "  - 后端日志: /var/log/gunicorn/gunicorn.log"
    log "  - 部署日志: $LOG_FILE"
    log ""
    log "管理命令："
    log "  - 查看服务状态: bash $PROJECT_DIR/scripts/service-monitor.sh status"
    log "  - 重启服务: bash $PROJECT_DIR/scripts/service-monitor.sh restart"
    log "  - 停止服务: bash $PROJECT_DIR/scripts/service-monitor.sh stop"
    log "  - 查看日志: tail -f /var/log/gunicorn/gunicorn.log"
    log ""
    log "监控命令："
    log "  - 启动监控: nohup bash $PROJECT_DIR/scripts/service-monitor.sh monitor > /var/log/service-monitor.log 2>&1 &"
    log ""
}

# 执行主流程
main
