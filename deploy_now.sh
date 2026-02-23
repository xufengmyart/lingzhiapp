#!/bin/bash
################################################################################
# 生产环境部署执行脚本
# 用途: 执行部署到生产环境的完整流程
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 加载配置
if [ -f "deploy_config.sh" ]; then
    source deploy_config.sh
else
    log_error "配置文件不存在: deploy_config.sh"
    exit 1
fi

# 检查SSH连接
check_ssh_connection() {
    log_info "检查SSH连接..."
    if ssh -o ConnectTimeout=10 $PRODUCTION_SERVER "echo 'SSH连接成功'" > /dev/null 2>&1; then
        log_success "SSH连接正常"
        return 0
    else
        log_error "SSH连接失败，请检查配置和网络"
        exit 1
    fi
}

# 备份生产环境
backup_production() {
    log_info "备份生产环境..."

    BACKUP_DIR="$HOME/backups/$(date +%Y%m%d_%H%M%S)"
    ssh $PRODUCTION_SERVER << ENDSSH
        mkdir -p $BACKUP_DIR
        cp $APP_PATH/routes/user_system.py $BACKUP_DIR/ 2>/dev/null || true
        cp $APP_PATH/routes/change_password.py $BACKUP_DIR/ 2>/dev/null || true
        cp $DB_PATH $BACKUP_DIR/ 2>/dev/null || true
        echo "备份完成: $BACKUP_DIR"
        echo "$BACKUP_DIR" > $HOME/.last_backup_path
ENDSSH

    log_success "生产环境备份完成"
}

# 上传修复文件
upload_files() {
    log_info "上传修复文件..."

    # 检查本地文件是否存在
    if [ ! -f "admin-backend/routes/user_system.py" ]; then
        log_error "本地文件不存在: admin-backend/routes/user_system.py"
        exit 1
    fi

    if [ ! -f "admin-backend/routes/change_password.py" ]; then
        log_error "本地文件不存在: admin-backend/routes/change_password.py"
        exit 1
    fi

    # 上传文件
    scp admin-backend/routes/user_system.py $PRODUCTION_SERVER:$APP_PATH/routes/
    scp admin-backend/routes/change_password.py $PRODUCTION_SERVER:$APP_PATH/routes/

    log_success "文件上传完成"
}

# 安装依赖
install_dependencies() {
    log_info "安装依赖..."

    ssh $PRODUCTION_SERVER << ENDSSH
        cd $APP_PATH
        pip3 list | grep bcrypt || pip3 install bcrypt
        echo "依赖安装完成"
ENDSSH

    log_success "依赖安装完成"
}

# 重启服务
restart_service() {
    log_info "重启后端服务..."

    ssh $PRODUCTION_SERVER << ENDSSH
        sudo supervisorctl restart $SERVICE_NAME
        sleep 5
        sudo supervisorctl status $SERVICE_NAME
ENDSSH

    log_success "服务重启完成"
}

# 等待服务启动
wait_for_service() {
    log_info "等待服务启动..."

    local max_attempts=30
    local attempt=0

    while [ $attempt -lt $max_attempts ]; do
        if curl -sf $HEALTH_CHECK_URL > /dev/null 2>&1; then
            log_success "服务已启动并正常运行"
            return 0
        fi
        attempt=$((attempt + 1))
        echo -n "."
        sleep 2
    done

    echo ""
    log_error "服务启动超时"
    return 1
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "========================================="
    echo "  生产环境部署"
    echo "  目标: $PRODUCTION_URL"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================="
    echo -e "${NC}"

    # 执行部署步骤
    check_ssh_connection
    backup_production
    upload_files
    install_dependencies
    restart_service
    wait_for_service

    echo ""
    log_success "部署完成！"
    echo ""
    echo "下一步操作:"
    echo "1. 运行验证脚本: ./verify_deployment.sh"
    echo "2. 查看服务日志: ssh $PRODUCTION_SERVER 'sudo tail -50 $LOG_FILE'"
    echo ""
}

# 执行主函数
main "$@"
