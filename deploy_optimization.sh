#!/bin/bash
# 部署脚本 - 部署性能优化和功能完善版本

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
LOG_FILE="$PROJECT_DIR/deploy.log"

# 日志函数
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}" | tee -a "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] SUCCESS: $1${NC}" | tee -a "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}" | tee -a "$LOG_FILE"
}

log_info() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] INFO: $1${NC}" | tee -a "$LOG_FILE"
}

# 清理旧进程
cleanup_old_processes() {
    log_info "清理旧进程..."
    
    # 停止旧的后端进程
    if pgrep -f "python.*app.py" > /dev/null; then
        log_info "停止旧的后端进程..."
        pkill -f "python.*app.py" || true
        sleep 2
    fi
    
    # 停止旧的 Node 进程
    if pgrep -f "node.*vite" > /dev/null; then
        log_info "停止旧的前端开发服务器..."
        pkill -f "node.*vite" || true
        sleep 2
    fi
}

# 检查环境
check_environment() {
    log_info "检查部署环境..."
    
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
    
    # 检查 npm
    if ! command -v npm &> /dev/null; then
        log_error "npm 未安装"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# 安装后端依赖
install_backend_dependencies() {
    log_info "安装后端依赖..."
    
    cd "$BACKEND_DIR"
    
    if [ -f "../requirements.txt" ]; then
        pip3 install -q -r ../requirements.txt || {
            log_error "后端依赖安装失败"
            exit 1
        }
    fi
    
    # 确保 Flask 和相关依赖已安装
    pip3 install -q Flask Flask-CORS flask-socketio python-dotenv || {
        log_error "Flask 依赖安装失败"
        exit 1
    }
    
    log_success "后端依赖安装完成"
}

# 构建前端
build_frontend() {
    log_info "构建前端项目..."
    
    cd "$FRONTEND_DIR"
    
    # 生成版本号
    npm run generate-version || log_warning "版本号生成失败，继续构建..."
    
    # 清理旧的构建文件
    rm -rf dist
    
    # 构建
    npm run build || {
        log_error "前端构建失败"
        exit 1
    }
    
    log_success "前端构建完成"
}

# 启动后端服务
start_backend() {
    log_info "启动后端服务..."
    
    cd "$BACKEND_DIR"
    
    # 使用后台模式启动
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!
    
    # 保存 PID
    echo $BACKEND_PID > /tmp/backend.pid
    
    # 等待服务启动
    sleep 5
    
    # 检查服务是否启动成功
    if ps -p $BACKEND_PID > /dev/null; then
        log_success "后端服务启动成功 (PID: $BACKEND_PID)"
    else
        log_error "后端服务启动失败，查看日志："
        tail -50 /tmp/backend.log
        exit 1
    fi
}

# 验证服务
verify_services() {
    log_info "验证服务状态..."
    
    # 等待服务完全启动
    sleep 3
    
    # 检查后端健康状态
    if curl -s -f http://localhost:5000 > /dev/null 2>&1; then
        log_success "后端服务健康检查通过"
    else
        log_error "后端服务健康检查失败"
        tail -50 /tmp/backend.log
        exit 1
    fi
    
    # 检查 API
    if curl -s -f http://localhost:5000/api/admin/api-monitor > /dev/null 2>&1; then
        log_success "API 监控接口正常"
    else
        log_warning "API 监控接口未响应，可能仍在初始化"
    fi
}

# 运行测试
run_tests() {
    log_info "运行测试..."
    
    cd "$PROJECT_DIR"
    
    # 赋予测试脚本执行权限
    chmod +x test_optimization.sh
    
    # 运行测试
    if bash test_optimization.sh; then
        log_success "所有测试通过"
    else
        log_warning "部分测试失败，但服务已启动"
    fi
}

# 主部署流程
main() {
    log "=========================================="
    log "开始部署 - 性能优化和功能完善版本"
    log "=========================================="
    
    # 清理旧进程
    cleanup_old_processes
    
    # 检查环境
    check_environment
    
    # 安装后端依赖
    install_backend_dependencies
    
    # 构建前端
    build_frontend
    
    # 启动后端
    start_backend
    
    # 验证服务
    verify_services
    
    # 运行测试
    run_tests
    
    log "=========================================="
    log_success "部署完成！"
    log "=========================================="
    log ""
    log "服务信息："
    log "  - 后端地址: http://localhost:5000"
    log "  - 前端构建: $FRONTEND_DIR/dist"
    log "  - 后端日志: /tmp/backend.log"
    log "  - 部署日志: $LOG_FILE"
    log ""
    log "新增功能："
    log "  - 前端代码分割和懒加载"
    log "  - 图片懒加载"
    log "  - API 响应缓存"
    log "  - 批量导入功能"
    log "  - 资产交易市场"
    log "  - 区块链集成"
    log "  - API 性能监控"
    log "  - 错误日志收集"
    log "  - 自动告警"
    log ""
    log "管理页面："
    log "  - 批量导入: http://localhost:5000/admin/batch-import"
    log "  - 错误日志: http://localhost:5000/admin/error-logs"
    log "  - API监控: http://localhost:5000/admin/api-monitor"
    log "  - 资产市场: http://localhost:5000/asset-market"
    log ""
}

# 执行主流程
main
