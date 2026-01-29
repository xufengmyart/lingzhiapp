#!/bin/bash

#############################################
# 灵值生态园智能体 - 一键部署脚本
# 版本：v5.0
# 日期：2025-01-24
#############################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目配置
PROJECT_NAME="灵值生态园智能体"
VERSION="v5.0"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUTH_DIR="${SCRIPT_DIR}/src/auth"
LOG_FILE="/tmp/deploy_$(date +%Y%m%d_%H%M%S).log"

# 函数：打印信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1" | tee -a "$LOG_FILE"
}

# 函数：打印成功
print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

# 函数：打印警告
print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

# 函数：打印错误
print_error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

# 函数：打印标题
print_title() {
    echo "" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
    echo "$1" | tee -a "$LOG_FILE"
    echo "========================================" | tee -a "$LOG_FILE"
}

# 函数：检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 未安装"
        return 1
    fi
    return 0
}

# 函数：检查 Python 版本
check_python_version() {
    print_title "检查 Python 版本"
    
    if ! check_command python3; then
        print_error "Python 3 未安装"
        return 1
    fi
    
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    print_info "Python 版本：${PYTHON_VERSION}"
    
    if [[ $(echo "$PYTHON_VERSION < 3.10" | bc) -eq 1 ]]; then
        print_error "Python 版本过低，需要 Python 3.10 或更高版本"
        return 1
    fi
    
    print_success "Python 版本检查通过"
    return 0
}

# 函数：安装依赖
install_dependencies() {
    print_title "安装 Python 依赖"
    
    if [ ! -f "${AUTH_DIR}/requirements.txt" ]; then
        print_error "requirements.txt 文件不存在"
        return 1
    fi
    
    print_info "正在安装依赖..."
    cd "${AUTH_DIR}"
    
    if pip3 install -r requirements.txt >> "$LOG_FILE" 2>&1; then
        print_success "依赖安装成功"
        return 0
    else
        print_error "依赖安装失败，请查看日志：$LOG_FILE"
        return 1
    fi
}

# 函数：初始化数据库
init_database() {
    print_title "初始化数据库"
    
    print_info "正在初始化权限管理数据..."
    cd "${AUTH_DIR}"
    if python3 init_data.py >> "$LOG_FILE" 2>&1; then
        print_success "权限管理数据初始化成功"
    else
        print_error "权限管理数据初始化失败"
        return 1
    fi
    
    print_info "正在初始化生态机制数据..."
    if python3 init_ecosystem.py >> "$LOG_FILE" 2>&1; then
        print_success "生态机制数据初始化成功"
    else
        print_error "生态机制数据初始化失败"
        return 1
    fi
    
    print_info "正在初始化项目参与和团队组建数据..."
    if python3 init_project.py >> "$LOG_FILE" 2>&1; then
        print_success "项目参与和团队组建数据初始化成功"
    else
        print_error "项目参与和团队组建数据初始化失败"
        return 1
    fi
    
    print_success "数据库初始化完成"
    return 0
}

# 函数：停止旧服务
stop_service() {
    print_title "停止旧服务"
    
    PID=$(ps aux | grep "uvicorn api:app" | grep -v grep | awk '{print $2}')
    if [ -n "$PID" ]; then
        print_info "正在停止旧服务 (PID: $PID)..."
        kill "$PID" >> "$LOG_FILE" 2>&1
        sleep 2
        print_success "旧服务已停止"
    else
        print_info "未发现运行中的服务"
    fi
}

# 函数：启动服务
start_service() {
    print_title "启动服务"
    
    cd "${AUTH_DIR}"
    
    print_info "正在启动 FastAPI 服务..."
    nohup python3 -m uvicorn api:app --host 0.0.0.0 --port 8000 > /tmp/api.log 2>&1 &
    
    sleep 5
    
    PID=$(ps aux | grep "uvicorn api:app" | grep -v grep | awk '{print $2}')
    if [ -n "$PID" ]; then
        print_success "服务启动成功 (PID: $PID)"
        return 0
    else
        print_error "服务启动失败，请查看日志：/tmp/api.log"
        return 1
    fi
}

# 函数：验证服务
verify_service() {
    print_title "验证服务"
    
    print_info "正在检查服务状态..."
    
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        print_success "服务响应正常"
    else
        print_error "服务无响应"
        return 1
    fi
    
    print_info "正在测试登录功能..."
    LOGIN_RESULT=$(curl -s -X POST http://localhost:8000/api/auth/login \
        -H "Content-Type: application/x-www-form-urlencoded" \
        -d "username=xufeng@meiyueart.cn&password=Xf@071214")
    
    if echo "$LOGIN_RESULT" | grep -q "access_token"; then
        print_success "登录功能正常"
    else
        print_warning "登录功能可能存在问题，请手动测试"
    fi
    
    print_info "正在检查 API 文档..."
    if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
        print_success "API 文档可访问"
    else
        print_warning "API 文档访问可能存在问题"
    fi
    
    return 0
}

# 函数：显示部署信息
show_deploy_info() {
    print_title "部署信息"
    
    echo -e "${GREEN}项目名称：${NC}${PROJECT_NAME}" | tee -a "$LOG_FILE"
    echo -e "${GREEN}版本：${NC}${VERSION}" | tee -a "$LOG_FILE"
    echo -e "${GREEN}部署时间：${NC}$(date '+%Y-%m-%d %H:%M:%S')" | tee -a "$LOG_FILE"
    echo -e "${GREEN}日志文件：${NC}${LOG_FILE}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo -e "${GREEN}服务地址：${NC}http://localhost:8000" | tee -a "$LOG_FILE"
    echo -e "${GREEN}API 文档：${NC}http://localhost:8000/docs" | tee -a "$LOG_FILE"
    echo -e "${GREEN}健康检查：${NC}http://localhost:8000/" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo -e "${GREEN}管理员账号：${NC}xufeng@meiyueart.cn" | tee -a "$LOG_FILE"
    echo -e "${GREEN}管理员密码：${NC}Xf@071214" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo -e "${YELLOW}⚠️  请妥善保管管理员账号密码！${NC}" | tee -a "$LOG_FILE"
}

# 函数：主函数
main() {
    print_title "${PROJECT_NAME} 一键部署脚本"
    echo "版本：${VERSION}" | tee -a "$LOG_FILE"
    echo "日期：$(date '+%Y-%m-%d')" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    # 检查环境
    if ! check_python_version; then
        exit 1
    fi
    
    # 安装依赖
    if ! install_dependencies; then
        exit 1
    fi
    
    # 初始化数据库
    if ! init_database; then
        exit 1
    fi
    
    # 停止旧服务
    stop_service
    
    # 启动服务
    if ! start_service; then
        exit 1
    fi
    
    # 验证服务
    if ! verify_service; then
        print_warning "服务验证失败，但服务可能仍在运行"
    fi
    
    # 显示部署信息
    show_deploy_info
    
    print_success "部署完成！"
}

# 执行主函数
main "$@"
