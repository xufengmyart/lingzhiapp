#!/bin/bash
################################################################################
# 生产环境自动化部署脚本
# 目标环境: meiyueart.com
# 用途: 自动部署修复后的代码到生产环境
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
PRODUCTION_SERVER="user@meiyueart.com"
APP_PATH="/path/to/app"  # 需要替换为实际路径
BACKUP_DIR="/path/to/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 本地文件
LOCAL_USER_SYSTEM="admin-backend/routes/user_system.py"

# 远程文件
REMOTE_USER_SYSTEM="$APP_PATH/admin-backend/routes/user_system.py"
REMOTE_CHANGE_PASSWORD="$APP_PATH/admin-backend/routes/change_password.py"
REMOTE_DATABASE="$APP_PATH/admin-backend/database.py"
REMOTE_APP_PY="$APP_PATH/admin-backend/app.py"

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

# 打印横幅
print_banner() {
    echo -e "${BLUE}"
    echo "========================================="
    echo "  生产环境自动化部署"
    echo "  目标: meiyueart.com"
    echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "========================================="
    echo -e "${NC}"
}

# 检查本地文件
check_local_files() {
    log_info "检查本地文件..."
    
    if [ ! -f "$LOCAL_USER_SYSTEM" ]; then
        log_error "本地文件不存在: $LOCAL_USER_SYSTEM"
        exit 1
    fi
    
    log_success "本地文件检查通过"
}

# 备份生产环境
backup_production() {
    log_info "备份生产环境..."
    
    ssh "$PRODUCTION_SERVER" << EOF
        # 创建备份目录
        mkdir -p $BACKUP_DIR
        
        # 备份user_system.py
        if [ -f "$REMOTE_USER_SYSTEM" ]; then
            cp "$REMOTE_USER_SYSTEM" "$BACKUP_DIR/user_system.py.$TIMESTAMP"
            echo "✅ 已备份user_system.py"
        fi
        
        # 备份数据库
        if [ -f "$APP_PATH/admin-backend/data/lingzhi_ecosystem.db" ]; then
            cp "$APP_PATH/admin-backend/data/lingzhi_ecosystem.db" "$BACKUP_DIR/lingzhi_ecosystem.db.$TIMESTAMP"
            echo "✅ 已备份数据库"
        fi
EOF
    
    log_success "备份完成"
}

# 上传文件到生产环境
upload_files() {
    log_info "上传文件到生产环境..."
    
    # 上传user_system.py
    scp "$LOCAL_USER_SYSTEM" "$PRODUCTION_SERVER:$REMOTE_USER_SYSTEM"
    log_success "已上传user_system.py"
    
    log_success "文件上传完成"
}

# 验证远程文件存在
verify_remote_files() {
    log_info "验证远程文件..."
    
    ssh "$PRODUCTION_SERVER" << EOF
        # 检查user_system.py
        if [ ! -f "$REMOTE_USER_SYSTEM" ]; then
            echo "❌ user_system.py不存在"
            exit 1
        fi
        echo "✅ user_system.py存在"
        
        # 检查change_password.py
        if [ ! -f "$REMOTE_CHANGE_PASSWORD" ]; then
            echo "❌ change_password.py不存在"
            exit 1
        fi
        echo "✅ change_password.py存在"
        
        # 检查database.py
        if [ ! -f "$REMOTE_DATABASE" ]; then
            echo "❌ database.py不存在"
            exit 1
        fi
        echo "✅ database.py存在"
EOF
    
    log_success "远程文件验证通过"
}

# 检查依赖包
check_dependencies() {
    log_info "检查依赖包..."
    
    ssh "$PRODUCTION_SERVER" << EOF
        cd $APP_PATH/admin-backend
        
        # 检查bcrypt是否安装
        if ! pip show bcrypt > /dev/null 2>&1; then
            echo "❌ bcrypt未安装"
            echo "安装bcrypt..."
            pip install bcrypt
        fi
        echo "✅ bcrypt已安装"
EOF
    
    log_success "依赖包检查通过"
}

# 重启服务
restart_service() {
    log_info "重启服务..."
    
    ssh "$PRODUCTION_SERVER" << EOF
        # 使用supervisor重启
        sudo supervisorctl restart lingzhi_admin_backend
        
        # 等待服务启动
        sleep 5
        
        # 检查服务状态
        if sudo supervisorctl status lingzhi_admin_backend | grep -q "RUNNING"; then
            echo "✅ 服务启动成功"
        else
            echo "❌ 服务启动失败"
            sudo supervisorctl status lingzhi_admin_backend
            exit 1
        fi
EOF
    
    log_success "服务重启完成"
}

# 验证部署
verify_deployment() {
    log_info "验证部署..."
    
    # 检查健康状态
    log_info "检查健康状态..."
    if curl -sf https://meiyueart.com/api/health > /dev/null; then
        log_success "健康检查通过"
    else
        log_error "健康检查失败"
        exit 1
    fi
    
    # 测试登录
    log_info "测试登录功能..."
    LOGIN_RESPONSE=$(curl -s -X POST https://meiyueart.com/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "123"}')
    
    if echo "$LOGIN_RESPONSE" | grep -q '"success":true'; then
        TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")
        log_success "登录成功，获取到token"
    else
        log_error "登录失败"
        echo "$LOGIN_RESPONSE"
        exit 1
    fi
    
    # 测试用户信息API（验证推荐人字段）
    log_info "测试用户信息API..."
    USER_INFO=$(curl -s -X GET "https://meiyueart.com/api/user/info" \
        -H "Authorization: Bearer $TOKEN")
    
    if echo "$USER_INFO" | grep -q '"success":true'; then
        log_success "用户信息API正常"
        if echo "$USER_INFO" | grep -q '"referrer"'; then
            log_success "推荐人字段存在"
        else
            log_warning "推荐人字段可能不存在，请手动验证"
        fi
    else
        log_error "用户信息API失败"
        echo "$USER_INFO"
        exit 1
    fi
    
    # 测试密码修改功能
    log_info "测试密码修改功能..."
    PASSWORD_CHANGE=$(curl -s -X POST "https://meiyueart.com/api/user/change-password" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d '{"oldPassword": "123", "newPassword": "NewPassword123!"}')
    
    if echo "$PASSWORD_CHANGE" | grep -q '"success":true'; then
        log_success "密码修改功能正常"
        
        # 恢复原密码
        log_info "恢复原密码..."
        curl -s -X POST "https://meiyueart.com/api/user/change-password" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d '{"oldPassword": "NewPassword123!", "newPassword": "123"}' > /dev/null
        log_success "密码已恢复"
    elif echo "$PASSWORD_CHANGE" | grep -q '"NOT_FOUND"'; then
        log_error "密码修改API不存在"
        echo "$PASSWORD_CHANGE"
        exit 1
    else
        log_warning "密码修改功能可能有问题"
        echo "$PASSWORD_CHANGE"
    fi
    
    log_success "部署验证通过"
}

# 打印部署摘要
print_summary() {
    echo -e "${GREEN}"
    echo "========================================="
    echo "  部署成功！"
    echo "========================================="
    echo -e "${NC}"
    echo "部署时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo "备份位置: $BACKUP_DIR"
    echo "备份时间戳: $TIMESTAMP"
    echo ""
    echo "下一步操作:"
    echo "1. 访问 https://meiyueart.com 验证前端功能"
    echo "2. 检查应用日志: ssh $PRODUCTION_SERVER 'tail -f /var/log/flask_backend.log'"
    echo "3. 如需回滚: ssh $PRODUCTION_SERVER 'cp $BACKUP_DIR/user_system.py.$TIMESTAMP $REMOTE_USER_SYSTEM'"
}

# 主函数
main() {
    print_banner
    
    # 检查本地文件
    check_local_files
    
    # 备份生产环境
    backup_production
    
    # 上传文件
    upload_files
    
    # 验证远程文件
    verify_remote_files
    
    # 检查依赖
    check_dependencies
    
    # 重启服务
    restart_service
    
    # 验证部署
    verify_deployment
    
    # 打印摘要
    print_summary
}

# 捕获错误并回滚
trap 'log_error "部署过程中出现错误"; log_info "正在回滚..."; ssh "$PRODUCTION_SERVER" "cp $BACKUP_DIR/user_system.py.$TIMESTAMP $REMOTE_USER_SYSTEM && sudo supervisorctl restart lingzhi_admin_backend"; log_info "回滚完成"; exit 1' ERR

# 执行主函数
main "$@"
