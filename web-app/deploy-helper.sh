#!/bin/bash

# 灵值生态园APP - 部署辅助脚本
# 此脚本帮助用户快速完成一些可以自动化的操作

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# 打印横幅
print_banner() {
    echo ""
    echo "=========================================="
    echo "  灵值生态园APP - 部署辅助脚本"
    echo "=========================================="
    echo ""
}

# 检查Git状态
check_git_status() {
    print_info "检查Git状态..."

    if ! command_exists git; then
        print_error "Git未安装，请先安装Git"
        exit 1
    fi

    if [ ! -d ".git" ]; then
        print_warning "Git仓库未初始化"
        print_info "正在初始化Git仓库..."
        git init
        print_success "Git仓库已初始化"
    else
        print_success "Git仓库已存在"
    fi
}

# 检查远程仓库
check_remote() {
    print_info "检查Git远程仓库..."

    if git remote get-url origin >/dev/null 2>&1; then
        REMOTE_URL=$(git remote get-url origin)
        print_success "远程仓库已配置: $REMOTE_URL"
        return 0
    else
        print_warning "远程仓库未配置"
        return 1
    fi
}

# 添加远程仓库
add_remote() {
    print_info "请输入GitHub仓库URL（格式：https://github.com/用户名/仓库名.git）"
    read -p "> " REPO_URL

    if [ -z "$REPO_URL" ]; then
        print_error "仓库URL不能为空"
        return 1
    fi

    print_info "正在添加远程仓库..."
    git remote add origin "$REPO_URL"
    print_success "远程仓库已添加: $REPO_URL"
}

# 推送到GitHub
push_to_github() {
    print_info "正在推送到GitHub..."

    # 检查是否在main分支
    CURRENT_BRANCH=$(git branch --show-current)
    if [ "$CURRENT_BRANCH" != "main" ]; then
        print_info "切换到main分支..."
        git checkout -b main || git branch -M main
    fi

    # 尝试推送
    if git push -u origin main 2>&1; then
        print_success "代码已成功推送到GitHub"
        return 0
    else
        print_error "推送失败"
        print_info "可能的原因："
        print_info "  1. 仓库URL不正确"
        print_info "  2. 需要GitHub认证（用户名和Personal Access Token）"
        print_info "  3. 仓库不存在或没有权限"
        print_info ""
        print_info "请检查以上问题后重试"
        return 1
    fi
}

# 构建项目
build_project() {
    print_info "正在构建项目..."

    if [ ! -f "package.json" ]; then
        print_error "package.json不存在，无法构建"
        return 1
    fi

    if ! command_exists npm; then
        print_error "npm未安装，请先安装Node.js和npm"
        return 1
    fi

    # 检查node_modules
    if [ ! -d "node_modules" ]; then
        print_info "正在安装依赖..."
        npm install
    fi

    # 构建
    npm run build

    if [ -d "dist" ]; then
        print_success "项目构建成功"
        return 0
    else
        print_error "项目构建失败"
        return 1
    fi
}

# 显示Git状态
show_git_status() {
    print_info "Git状态："
    git status
}

# 显示最近的提交
show_recent_commits() {
    print_info "最近的提交："
    git log --oneline -5
}

# 显示帮助信息
show_help() {
    cat << EOF
使用方法: ./deploy-helper.sh [选项]

选项:
    status      显示当前状态
    remote      检查/配置远程仓库
    push        推送代码到GitHub
    build       构建项目
    all         执行完整部署流程（检查→远程→推送）
    help        显示帮助信息

示例:
    ./deploy-helper.sh status     # 查看状态
    ./deploy-helper.sh remote     # 配置远程仓库
    ./deploy-helper.sh push       # 推送代码
    ./deploy-helper.sh all        # 完整流程

EOF
}

# 显示当前状态
show_status() {
    print_banner
    check_git_status

    echo ""
    print_info "远程仓库状态："
    if check_remote; then
        echo "  ✓ 远程仓库已配置"
    else
        echo "  ✗ 远程仓库未配置"
    fi

    echo ""
    print_info "文件状态："
    show_git_status

    echo ""
    print_info "最近提交："
    show_recent_commits

    echo ""
    print_info "构建状态："
    if [ -d "dist" ]; then
        echo "  ✓ 项目已构建"
    else
        echo "  ✗ 项目未构建"
    fi

    echo ""
    print_info "下一步操作："
    if ! check_remote; then
        echo "  1. 运行: ./deploy-helper.sh remote"
    fi
    echo "  2. 运行: ./deploy-helper.sh push"
    echo "  3. 访问Vercel并导入仓库"
}

# 完整流程
full_process() {
    print_banner
    print_info "开始完整部署流程..."
    echo ""

    # 步骤1：检查Git
    check_git_status

    # 步骤2：配置远程仓库
    if ! check_remote; then
        echo ""
        print_info "===== 步骤1/3: 配置远程仓库 ====="
        add_remote
    fi

    # 步骤3：推送代码
    echo ""
    print_info "===== 步骤2/3: 推送代码到GitHub ====="
    push_to_github || exit 1

    # 步骤4：构建项目（可选）
    echo ""
    print_info "===== 步骤3/3: 构建项目（可选）====="
    read -p "是否构建项目？(y/n) [n]: " BUILD_CHOICE
    if [ "$BUILD_CHOICE" = "y" ] || [ "$BUILD_CHOICE" = "Y" ]; then
        build_project || exit 1
    fi

    # 完成
    echo ""
    print_banner
    print_success "准备工作已完成！"
    echo ""
    print_info "下一步操作："
    echo "  1. 访问 https://vercel.com"
    echo "  2. 登录并创建新项目"
    echo "  3. 导入GitHub仓库: $(git remote get-url origin 2>/dev/null || echo '未配置')"
    echo "  4. 点击Deploy按钮"
    echo "  5. 等待部署完成（约2-3分钟）"
    echo ""
    print_info "详细步骤请参考: USER_ACTION_GUIDE.md"
}

# 主函数
main() {
    case "${1:-status}" in
        status)
            show_status
            ;;
        remote)
            print_banner
            check_git_status
            add_remote
            ;;
        push)
            print_banner
            check_git_status
            if ! check_remote; then
                print_warning "远程仓库未配置，请先运行: ./deploy-helper.sh remote"
                exit 1
            fi
            push_to_github
            ;;
        build)
            print_banner
            build_project
            ;;
        all)
            full_process
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "未知选项: $1"
            echo ""
            show_help
            exit 1
            ;;
    esac
}

# 执行主函数
main "$@"
