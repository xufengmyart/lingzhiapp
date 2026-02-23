#!/bin/bash
################################################################################
# 版本一致性检查脚本
# 用途: 检查容器环境和生产环境的代码版本是否一致
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 配置
PRODUCTION_SERVER="user@meiyueart.com"
APP_PATH="/path/to/app"  # 需要替换为实际路径

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

# 获取文件的MD5哈希
get_file_hash() {
    local file_path=$1
    local server=$2
    
    if [ -z "$server" ]; then
        # 本地文件
        if [ -f "$file_path" ]; then
            md5sum "$file_path" | cut -d' ' -f1
        else
            echo "FILE_NOT_EXISTS"
        fi
    else
        # 远程文件
        ssh "$server" "if [ -f '$file_path' ]; then md5sum '$file_path' | cut -d' ' -f1; else echo 'FILE_NOT_EXISTS'; fi"
    fi
}

# 比较文件哈希
compare_files() {
    local local_file=$1
    local remote_file=$2
    local file_name=$3
    
    log_info "检查文件: $file_name"
    
    local_hash=$(get_file_hash "$local_file" "")
    remote_hash=$(get_file_hash "$remote_file" "$PRODUCTION_SERVER")
    
    if [ "$local_hash" == "FILE_NOT_EXISTS" ]; then
        log_error "本地文件不存在: $local_file"
        return 1
    elif [ "$remote_hash" == "FILE_NOT_EXISTS" ]; then
        log_error "远程文件不存在: $remote_file"
        return 1
    elif [ "$local_hash" == "$remote_hash" ]; then
        log_success "文件一致: $file_name"
        return 0
    else
        log_warning "文件不一致: $file_name"
        echo "  本地:  $local_hash"
        echo "  远程:  $remote_hash"
        return 1
    fi
}

# 检查Python文件
check_python_files() {
    log_info "检查Python文件..."
    
    local inconsistencies=0
    
    # 定义需要检查的文件
    declare -a files=(
        "admin-backend/routes/user_system.py"
        "admin-backend/routes/change_password.py"
        "admin-backend/database.py"
        "admin-backend/app.py"
    )
    
    for file in "${files[@]}"; do
        local filename=$(basename "$file")
        if ! compare_files "$file" "$APP_PATH/$file" "$filename"; then
            ((inconsistencies++))
        fi
    done
    
    return $inconsistencies
}

# 检查依赖包版本
check_dependencies() {
    log_info "检查依赖包版本..."
    
    log_info "检查本地依赖包..."
    local_bcrypt_version=$(pip show bcrypt 2>/dev/null | grep Version | awk '{print $2}')
    log_success "本地bcrypt版本: $local_bcrypt_version"
    
    log_info "检查远程依赖包..."
    remote_bcrypt_version=$(ssh "$PRODUCTION_SERVER" "cd $APP_PATH/admin-backend && pip show bcrypt 2>/dev/null | grep Version | awk '{print \$2}'")
    log_success "远程bcrypt版本: $remote_bcrypt_version"
    
    if [ "$local_bcrypt_version" != "$remote_bcrypt_version" ]; then
        log_warning "依赖包版本不一致"
        echo "  本地:  $local_bcrypt_version"
        echo "  远程:  $remote_bcrypt_version"
        return 1
    else
        log_success "依赖包版本一致"
        return 0
    fi
}

# 检查数据库版本
check_database_version() {
    log_info "检查数据库版本..."
    
    log_info "获取本地数据库信息..."
    if [ -f "admin-backend/data/lingzhi_ecosystem.db" ]; then
        local_db_size=$(stat -c%s "admin-backend/data/lingzhi_ecosystem.db" 2>/dev/null || echo "0")
        local_db_hash=$(md5sum "admin-backend/data/lingzhi_ecosystem.db" 2>/dev/null | cut -d' ' -f1)
        log_success "本地数据库大小: ${local_db_size} bytes"
        log_success "本地数据库哈希: ${local_db_hash:0:16}..."
    else
        log_warning "本地数据库文件不存在"
        local_db_size=0
        local_db_hash="NONE"
    fi
    
    log_info "获取远程数据库信息..."
    remote_db_size=$(ssh "$PRODUCTION_SERVER" "stat -c%s '$APP_PATH/admin-backend/data/lingzhi_ecosystem.db' 2>/dev/null || echo '0'")
    remote_db_hash=$(ssh "$PRODUCTION_SERVER" "md5sum '$APP_PATH/admin-backend/data/lingzhi_ecosystem.db' 2>/dev/null | cut -d' ' -f1" || echo "NONE")
    log_success "远程数据库大小: ${remote_db_size} bytes"
    log_success "远程数据库哈希: ${remote_db_hash:0:16}..."
    
    if [ "$local_db_hash" != "$remote_db_hash" ]; then
        log_warning "数据库文件不一致"
        echo "  本地:  $local_db_hash"
        echo "  远程:  $remote_db_hash"
        return 1
    else
        log_success "数据库文件一致"
        return 0
    fi
}

# 检查API功能
check_api_features() {
    log_info "检查API功能..."
    
    # 测试生产环境API
    log_info "测试生产环境API..."
    
    # 健康检查
    if curl -sf https://meiyueart.com/api/health > /dev/null; then
        log_success "健康检查API正常"
    else
        log_error "健康检查API失败"
        return 1
    fi
    
    # 登录
    local login_response=$(curl -s -X POST https://meiyueart.com/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username": "admin", "password": "123"}')
    
    if echo "$login_response" | grep -q '"success":true'; then
        log_success "登录API正常"
    else
        log_error "登录API失败"
        return 1
    fi
    
    # 获取token
    local token=$(echo "$login_response" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")
    
    # 用户信息API
    local user_info=$(curl -s -X GET "https://meiyueart.com/api/user/info" \
        -H "Authorization: Bearer $token")
    
    if echo "$user_info" | grep -q '"success":true'; then
        if echo "$user_info" | grep -q '"referrer"'; then
            log_success "用户信息API包含推荐人字段"
        else
            log_warning "用户信息API缺少推荐人字段"
            return 1
        fi
    else
        log_error "用户信息API失败"
        return 1
    fi
    
    # 密码修改API
    local password_change=$(curl -s -X POST "https://meiyueart.com/api/user/change-password" \
        -H "Authorization: Bearer $token" \
        -H "Content-Type: application/json" \
        -d '{"oldPassword": "123", "newPassword": "Temp123!"}')
    
    if echo "$password_change" | grep -q '"NOT_FOUND"'; then
        log_error "密码修改API不存在"
        return 1
    elif echo "$password_change" | grep -q '"success":true'; then
        log_success "密码修改API正常"
        # 恢复原密码
        curl -s -X POST "https://meiyueart.com/api/user/change-password" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d '{"oldPassword": "Temp123!", "newPassword": "123"}' > /dev/null
    else
        log_warning "密码修改API可能存在问题"
    fi
    
    return 0
}

# 生成报告
generate_report() {
    local code_status=$1
    local dep_status=$2
    local db_status=$3
    local api_status=$4
    
    echo ""
    echo "========================================="
    echo "  版本一致性检查报告"
    echo "========================================="
    echo ""
    echo "检查时间: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
    echo "检查结果:"
    
    if [ $code_status -eq 0 ]; then
        echo "  ✅ 代码文件: 一致"
    else
        echo "  ❌ 代码文件: 不一致"
    fi
    
    if [ $dep_status -eq 0 ]; then
        echo "  ✅ 依赖包: 一致"
    else
        echo "  ❌ 依赖包: 不一致"
    fi
    
    if [ $db_status -eq 0 ]; then
        echo "  ✅ 数据库: 一致"
    else
        echo "  ❌ 数据库: 不一致"
    fi
    
    if [ $api_status -eq 0 ]; then
        echo "  ✅ API功能: 正常"
    else
        echo "  ❌ API功能: 异常"
    fi
    
    echo ""
    
    if [ $code_status -eq 0 ] && [ $dep_status -eq 0 ] && [ $db_status -eq 0 ] && [ $api_status -eq 0 ]; then
        echo "🎉 所有检查通过！容器和生产环境版本一致。"
        return 0
    else
        echo "⚠️  发现不一致，需要同步。"
        echo ""
        echo "建议操作:"
        if [ $code_status -ne 0 ]; then
            echo "  - 运行部署脚本: ./deploy_to_production.sh"
        fi
        if [ $dep_status -ne 0 ]; then
            echo "  - 同步依赖包: ssh $PRODUCTION_SERVER 'cd $APP_PATH/admin-backend && pip install -r requirements.txt'"
        fi
        if [ $db_status -ne 0 ]; then
            echo "  - 同步数据库: scp admin-backend/data/lingzhi_ecosystem.db $PRODUCTION_SERVER:$APP_PATH/admin-backend/data/"
        fi
        return 1
    fi
}

# 主函数
main() {
    echo -e "${BLUE}"
    echo "========================================="
    echo "  版本一致性检查"
    echo "  对比: 容器环境 ↔ 生产环境"
    echo "========================================="
    echo -e "${NC}"
    
    # 检查代码文件
    check_python_files
    code_status=$?
    
    # 检查依赖包
    check_dependencies
    dep_status=$?
    
    # 检查数据库
    check_database_version
    db_status=$?
    
    # 检查API功能
    check_api_features
    api_status=$?
    
    # 生成报告
    generate_report $code_status $dep_status $db_status $api_status
}

# 执行主函数
main "$@"
