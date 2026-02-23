#!/bin/bash

# 小程序一键部署脚本
# 使用方法: ./deploy.sh [version] [description]

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="${SCRIPT_DIR}"

# 获取版本号
VERSION=${1:-$(date +'%Y.%m.%d')-${git rev-parse --short HEAD 2>/dev/null || echo 'dev'}}
DESCRIPTION=${2:-"自动化部署 $(date +'%Y-%m-%d %H:%M:%S')"}

# 打印信息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# 检查环境
check_env() {
    print_info "检查部署环境..."

    # 检查 Node.js
    if ! command -v node &> /dev/null; then
        print_error "未安装 Node.js，请先安装"
        exit 1
    fi

    # 检查 npm
    if ! command -v npm &> /dev/null; then
        print_error "未安装 npm，请先安装"
        exit 1
    fi

    # 检查密钥文件
    if [ ! -d "${PROJECT_DIR}/keys" ]; then
        print_error "keys 目录不存在"
        exit 1
    fi

    KEY_FILE=$(find "${PROJECT_DIR}/keys" -name "*.key" | head -n 1)
    if [ -z "$KEY_FILE" ]; then
        print_error "密钥文件不存在，请将微信私钥文件放置在 keys/ 目录"
        exit 1
    fi

    print_info "环境检查通过 ✓"
}

# 安装依赖
install_deps() {
    print_info "检查并安装依赖..."

    cd "${PROJECT_DIR}"

    if [ ! -d "node_modules" ]; then
        print_info "首次安装，正在安装依赖..."
        npm install
    else
        print_info "依赖已存在 ✓"
    fi
}

# 更新配置文件
update_config() {
    print_info "检查配置文件..."

    # 检查是否需要更新 AppID
    APPID=$(grep -oP '(?<="appid": ")[^"]*' "${PROJECT_DIR}/project.config.json" 2>/dev/null || echo "")

    if [ "$APPID" = "请填写你的小程序AppID" ] || [ -z "$APPID" ]; then
        print_error "请在 project.config.json 中配置正确的小程序 AppID"
        exit 1
    fi

    print_info "AppID: $APPID ✓"
}

# 执行上传
upload_code() {
    print_info "开始上传代码..."
    print_info "版本号: $VERSION"
    print_info "描述: $DESCRIPTION"

    cd "${PROJECT_DIR}"

    # 设置环境变量
    export VERSION="$VERSION"
    export DESC="$DESCRIPTION"

    # 执行上传
    npm run upload

    if [ $? -eq 0 ]; then
        print_info "上传成功！"
        print_info "请在微信公众平台的「版本管理」中查看上传的版本"
    else
        print_error "上传失败"
        exit 1
    fi
}

# 主流程
main() {
    print_info "======================================"
    print_info "  小程序一键部署"
    print_info "======================================"
    print_info ""

    check_env
    install_deps
    update_config
    upload_code

    print_info ""
    print_info "======================================"
    print_info "  部署完成"
    print_info "======================================"
}

# 执行主流程
main "$@"
