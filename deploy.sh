#!/bin/bash

# ============================================
# 灵值生态园自动部署脚本
# 功能：自动构建、备份、同步到服务器
# 使用方法：./deploy.sh
# ============================================

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================
# 配置项
# ============================================

# 服务器配置
SERVER_HOST="123.56.142.143"
SERVER_USER="root"
SERVER_PROJECT_PATH="/var/www/lingzhiapp"
SERVER_BACKUP_PATH="/var/backups/lingzhiapp"

# 本地配置
LOCAL_PROJECT_PATH="/workspace/projects"
BUILD_OUTPUT_PATH="$LOCAL_PROJECT_PATH/public"
LOCAL_BACKUP_PATH="/workspace/projects/backups"

# Git 配置
GITHUB_REPO="https://github.com/xufengmyart/lingzhiapp.git"

# ============================================
# 函数定义
# ============================================

# 打印消息
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}[$(date '+%Y-%m-%d %H:%M:%S')] ${message}${NC}"
}

# 打印成功消息
print_success() {
    print_message "$GREEN" "✅ $1"
}

# 打印错误消息
print_error() {
    print_message "$RED" "❌ $1"
}

# 打印警告消息
print_warning() {
    print_message "$YELLOW" "⚠️  $1"
}

# 打印信息消息
print_info() {
    print_message "$BLUE" "ℹ️  $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 命令不存在，请先安装"
        exit 1
    fi
}

# 创建备份目录
create_backup_dir() {
    if [ ! -d "$1" ]; then
        mkdir -p "$1"
        print_success "创建备份目录: $1"
    fi
}

# 本地备份
local_backup() {
    local backup_name="lingzhiapp-backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    local backup_path="$LOCAL_BACKUP_PATH/$backup_name"

    print_info "开始本地备份..."

    create_backup_dir "$LOCAL_BACKUP_PATH"

    # 排除不需要备份的文件
    tar --exclude='node_modules' \
        --exclude='.git' \
        --exclude='backups' \
        --exclude='*.log' \
        -czf "$backup_path" \
        -C "$LOCAL_PROJECT_PATH" \
        .

    print_success "本地备份完成: $backup_name"

    # 清理 7 天前的备份
    find "$LOCAL_BACKUP_PATH" -name "lingzhiapp-backup-*.tar.gz" -mtime +7 -delete
    print_info "已清理 7 天前的旧备份"
}

# 服务器备份
server_backup() {
    print_info "开始服务器备份..."

    # 在服务器上创建备份
    ssh "$SERVER_USER@$SERVER_HOST" "
        set -e

        # 创建备份目录
        sudo mkdir -p $SERVER_BACKUP_PATH

        # 备份当前部署
        if [ -d '$SERVER_PROJECT_PATH' ]; then
            backup_name='lingzhiapp-backup-\$(date +%Y%m%d-%H%M%S).tar.gz'
            backup_path='$SERVER_BACKUP_PATH/\$backup_name'

            sudo tar --exclude='node_modules' \\
                -czf \"\$backup_path\" \\
                -C '$SERVER_PROJECT_PATH' \\
                .

            echo '✅ 服务器备份完成: \$backup_name'

            # 清理 7 天前的备份
            sudo find '$SERVER_BACKUP_PATH' -name 'lingzhiapp-backup-*.tar.gz' -mtime +7 -delete
            echo '✅ 已清理 7 天前的旧备份'
        else
            echo '⚠️  服务器上还没有项目，跳过备份'
        fi
    "

    print_success "服务器备份完成"
}

# 推送到 GitHub
push_to_github() {
    print_info "推送到 GitHub..."

    cd "$LOCAL_PROJECT_PATH"

    # 检查是否有未提交的更改
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "发现未提交的更改，先提交..."

        # 添加所有更改
        git add .

        # 提交
        read -p "请输入提交信息: " commit_message
        git commit -m "$commit_message"

        print_success "代码已提交"
    fi

    # 推送到 GitHub
    print_info "推送到 GitHub..."
    git push origin main

    print_success "已推送到 GitHub"
}

# 同步到服务器
sync_to_server() {
    print_info "同步到服务器..."

    # 在服务器上拉取最新代码
    ssh "$SERVER_USER@$SERVER_HOST" "
        set -e

        # 检查项目目录是否存在
        if [ ! -d '$SERVER_PROJECT_PATH' ]; then
            echo '⚠️  项目目录不存在，创建中...'
            sudo mkdir -p '$SERVER_PROJECT_PATH'
            sudo chown -R \$USER:\$USER '$SERVER_PROJECT_PATH'
        fi

        # 拉取最新代码
        cd '$SERVER_PROJECT_PATH'
        git pull origin main

        echo '✅ 代码已同步到服务器'
    "

    print_success "同步到服务器完成"
}

# 在服务器上重新构建（如果需要）
rebuild_on_server() {
    print_info "在服务器上重新构建..."

    ssh "$SERVER_USER@$SERVER_HOST" "
        set -e

        cd '$SERVER_PROJECT_PATH/web-app'

        # 检查是否需要重新构建
        if [ 'public/index.html' -ot 'src/' ] || [ ! -d 'public' ]; then
            echo '⚠️  需要重新构建...'

            # 安装依赖
            if [ ! -d 'node_modules' ]; then
                npm install
            fi

            # 构建
            npm run build

            echo '✅ 构建完成'
        else
            echo '✅ 无需重新构建'
        fi
    "

    print_success "服务器构建完成"
}

# 重启服务器 Nginx
restart_nginx() {
    print_info "重启 Nginx..."

    ssh "$SERVER_USER@$SERVER_HOST" "
        set -e

        # 检查 Nginx 配置
        sudo nginx -t

        if [ \$? -eq 0 ]; then
            sudo systemctl restart nginx
            echo '✅ Nginx 已重启'
        else
            echo '❌ Nginx 配置错误，未重启'
            exit 1
        fi
    "

    print_success "Nginx 重启完成"
}

# 验证部署
verify_deployment() {
    print_info "验证部署..."

    # 检查本地文件
    if [ ! -f "$BUILD_OUTPUT_PATH/index.html" ]; then
        print_error "本地构建文件不存在"
        exit 1
    fi

    print_success "本地构建文件正常"

    # 检查服务器文件
    ssh "$SERVER_USER@$SERVER_HOST" "
        set -e

        if [ -f '$SERVER_PROJECT_PATH/public/index.html' ]; then
            echo '✅ 服务器文件正常'
        else
            echo '❌ 服务器文件不存在'
            exit 1
        fi
    "

    print_success "部署验证通过"
}

# 显示帮助信息
show_help() {
    echo "使用方法: ./deploy.sh [选项]"
    echo ""
    echo "选项:"
    echo "  backup      仅执行备份"
    echo "  build       仅执行构建"
    echo "  sync        仅执行同步"
    echo "  full        执行完整部署流程（默认）"
    echo "  help        显示帮助信息"
    echo ""
    echo "完整部署流程包括："
    echo "  1. 本地备份"
    echo "  2. 服务器备份"
    echo "  3. 推送到 GitHub"
    echo "  4. 同步到服务器"
    echo "  5. 重启 Nginx"
    echo "  6. 验证部署"
}

# ============================================
# 主流程
# ============================================

main() {
    echo ""
    print_info "========================================"
    print_info "  灵值生态园自动部署脚本"
    print_info "========================================"
    echo ""

    # 检查必要的命令
    print_info "检查必要的命令..."
    check_command "git"
    check_command "ssh"
    check_command "tar"

    # 处理命令行参数
    case "${1:-full}" in
        backup)
            print_info "执行备份..."
            local_backup
            server_backup
            ;;
        build)
            print_info "执行构建..."
            cd "$LOCAL_PROJECT_PATH/web-app"
            npm run build
            ;;
        sync)
            print_info "执行同步..."
            push_to_github
            sync_to_server
            restart_nginx
            ;;
        full)
            print_info "执行完整部署流程..."
            echo ""

            # 步骤 1: 本地备份
            print_info "步骤 1/6: 本地备份"
            local_backup
            echo ""

            # 步骤 2: 服务器备份
            print_info "步骤 2/6: 服务器备份"
            server_backup
            echo ""

            # 步骤 3: 推送到 GitHub
            print_info "步骤 3/6: 推送到 GitHub"
            push_to_github
            echo ""

            # 步骤 4: 同步到服务器
            print_info "步骤 4/6: 同步到服务器"
            sync_to_server
            echo ""

            # 步骤 5: 重启 Nginx
            print_info "步骤 5/6: 重启 Nginx"
            restart_nginx
            echo ""

            # 步骤 6: 验证部署
            print_info "步骤 6/6: 验证部署"
            verify_deployment
            echo ""

            print_success "========================================"
            print_success "  部署完成！"
            print_success "========================================"
            echo ""
            print_info "访问地址: https://meiyueart.com"
            echo ""
            ;;
        help)
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            show_help
            exit 1
            ;;
    esac
}

# 执行主流程
main "$@"
