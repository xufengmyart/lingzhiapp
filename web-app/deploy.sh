#!/bin/bash

###############################################################################
# 灵值生态园APP - 一键部署脚本
# 支持多种部署方案
###############################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置
APP_NAME="lingzhi-ecosystem"
DOMAIN=""
DEPLOYMENT_TYPE=""
PROJECT_DIR="/var/www/$APP_NAME"

# 打印带颜色的信息
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

# 打印Logo
print_logo() {
    echo -e "${GREEN}"
    echo "╔════════════════════════════════════════════════════════════╗"
    echo "║                                                            ║"
    echo "║          灵值生态园APP - 一键部署脚本                      ║"
    echo "║          Lingzhi Ecosystem - One-Click Deployment          ║"
    echo "║                                                            ║"
    echo "╚════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# 显示菜单
show_menu() {
    echo ""
    echo "请选择部署方案："
    echo ""
    echo "1) 本地开发服务器 (localhost:3000)"
    echo "2) Docker容器部署"
    echo "3) 生产环境部署 (Nginx)"
    echo "4) 静态文件导出 (自行部署)"
    echo "5) 移动应用打包 (Android/iOS)"
    echo "6) 仅构建项目"
    echo "0) 退出"
    echo ""
}

# 检查系统环境
check_environment() {
    print_info "检查系统环境..."

    # 检查Node.js
    if ! command -v node &> /dev/null; then
        print_error "Node.js未安装！请先安装Node.js"
        exit 1
    fi

    # 检查npm
    if ! command -v npm &> /dev/null; then
        print_error "npm未安装！请先安装npm"
        exit 1
    fi

    print_success "系统环境检查通过"
    print_info "Node.js版本: $(node -v)"
    print_info "npm版本: $(npm -v)"
}

# 安装依赖
install_dependencies() {
    print_info "安装项目依赖..."

    if [ -d "node_modules" ]; then
        print_warning "node_modules已存在，跳过安装"
    else
        npm install
        print_success "依赖安装完成"
    fi
}

# 构建项目
build_project() {
    print_info "构建项目..."
    npm run build
    print_success "项目构建完成"
}

# 方案1：本地开发服务器
deploy_local() {
    print_info "启动本地开发服务器..."
    print_warning "服务器将运行在 http://localhost:3000"
    print_warning "按 Ctrl+C 停止服务器"
    echo ""

    npm run dev
}

# 方案2：Docker容器部署
deploy_docker() {
    print_info "Docker容器部署..."

    # 检查Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker未安装！请先安装Docker"
        exit 1
    fi

    # 构建镜像
    print_info "构建Docker镜像..."
    docker build -t $APP_NAME:latest .

    # 停止旧容器
    print_info "停止旧容器（如果存在）..."
    docker stop $APP_NAME 2>/dev/null || true
    docker rm $APP_NAME 2>/dev/null || true

    # 启动新容器
    print_info "启动新容器..."
    docker run -d \
        -p 80:80 \
        -p 443:443 \
        --name $APP_NAME \
        --restart unless-stopped \
        $APP_NAME:latest

    print_success "Docker容器部署完成"
    print_info "应用已启动，访问地址: http://localhost"
    print_info "查看日志: docker logs -f $APP_NAME"
}

# 方案3：生产环境部署
deploy_production() {
    print_info "生产环境部署..."

    # 检查Nginx
    if ! command -v nginx &> /dev/null; then
        print_error "Nginx未安装！请先安装Nginx"
        print_info "安装命令: apt-get install nginx"
        exit 1
    fi

    # 获取域名
    read -p "请输入域名（例如: example.com）: " DOMAIN

    if [ -z "$DOMAIN" ]; then
        print_error "域名不能为空！"
        exit 1
    fi

    # 创建项目目录
    print_info "创建项目目录..."
    sudo mkdir -p $PROJECT_DIR

    # 构建项目
    build_project

    # 复制文件
    print_info "复制文件到Nginx目录..."
    sudo cp -r dist/* $PROJECT_DIR/

    # 配置Nginx
    print_info "配置Nginx..."
    sudo cp nginx-production.conf /etc/nginx/sites-available/$APP_NAME
    sudo ln -sf /etc/nginx/sites-available/$APP_NAME /etc/nginx/sites-enabled/

    # 替换域名
    sudo sed -i "s/yourdomain.com/$DOMAIN/g" /etc/nginx/sites-available/$APP_NAME

    # 测试Nginx配置
    print_info "测试Nginx配置..."
    sudo nginx -t

    if [ $? -eq 0 ]; then
        # 重启Nginx
        print_info "重启Nginx..."
        sudo systemctl restart nginx
        print_success "生产环境部署完成"
        print_info "应用已启动，访问地址: http://$DOMAIN"
        print_info "配置SSL证书: sudo certbot --nginx -d $DOMAIN"
    else
        print_error "Nginx配置测试失败！"
        exit 1
    fi
}

# 方案4：静态文件导出
deploy_static() {
    print_info "导出静态文件..."
    build_project

    print_info "创建压缩包..."
    tar -czf $APP_NAME-dist.tar.gz dist/

    print_success "静态文件导出完成"
    print_info "压缩包: $APP_NAME-dist.tar.gz"
    print_info "解压命令: tar -xzf $APP_NAME-dist.tar.gz"
}

# 方案5：移动应用打包
deploy_mobile() {
    print_info "移动应用打包..."

    # 检查Capacitor
    if ! npm list @capacitor/cli &> /dev/null; then
        print_error "Capacitor未安装！"
        print_info "安装命令: npm install @capacitor/core @capacitor/cli"
        exit 1
    fi

    # 构建项目
    build_project

    # 添加平台
    print_info "选择移动平台:"
    echo "1) Android"
    echo "2) iOS"
    read -p "请选择 (1/2): " PLATFORM

    case $PLATFORM in
        1)
            print_info "构建Android应用..."
            npx cap add android
            npx cap sync android
            print_success "Android应用准备完成"
            print_info "下一步: 使用Android Studio打开 android/ 目录并构建APK"
            ;;
        2)
            print_info "构建iOS应用..."
            npx cap add ios
            npx cap sync ios
            print_success "iOS应用准备完成"
            print_info "下一步: 使用Xcode打开 ios/ 目录并构建IPA"
            ;;
        *)
            print_error "无效的选择！"
            exit 1
            ;;
    esac
}

# 方案6：仅构建
deploy_build_only() {
    print_info "仅构建项目..."
    build_project
    print_success "构建完成"
    print_info "输出目录: dist/"
}

# 主函数
main() {
    print_logo
    check_environment

    # 进入项目目录
    if [ -f "package.json" ]; then
        print_info "已检测到package.json"
    else
        print_error "请在项目根目录运行此脚本！"
        exit 1
    fi

    # 显示菜单
    while true; do
        show_menu
        read -p "请选择 (0-6): " choice

        case $choice in
            1)
                install_dependencies
                deploy_local
                break
                ;;
            2)
                install_dependencies
                deploy_docker
                break
                ;;
            3)
                install_dependencies
                deploy_production
                break
                ;;
            4)
                install_dependencies
                deploy_static
                break
                ;;
            5)
                install_dependencies
                deploy_mobile
                break
                ;;
            6)
                install_dependencies
                deploy_build_only
                break
                ;;
            0)
                print_info "退出脚本"
                exit 0
                ;;
            *)
                print_error "无效的选择！"
                ;;
        esac
    done
}

# 运行主函数
main
