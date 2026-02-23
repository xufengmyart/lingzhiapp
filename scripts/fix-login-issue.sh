#!/bin/bash

################################################################################
# 灵值生态园 - 登录问题修复脚本
# 用途：专门修复登录 502 错误问题
# 问题：登录 API 返回 502 Bad Gateway
# 根因：Flask 后端服务未运行
# 作者：Coze Coding
# 版本：v1.0
# 日期：2026-02-11
################################################################################

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# 配置变量
DOMAIN="meiyueart.com"
FLASK_PORT=8080
NGINX_HTTP_PORT=80
NGINX_HTTPS_PORT=443
SERVICE_NAME="flask-app"
APP_DIR="/var/www/meiyueart"

# 打印横幅
print_banner() {
    echo ""
    echo "================================================================================"
    echo "  灵值生态园 - 登录问题修复工具 v1.0"
    echo "  问题: 登录 API 返回 502 Bad Gateway"
    echo "  根因: Flask 后端服务未运行"
    echo "================================================================================"
    echo ""
}

# 日志函数
log_info() {
    echo -e "${CYAN}[INFO]${NC} $1"
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

# 诊断函数
diagnose_login_issue() {
    echo ""
    echo "========================================="
    echo "诊断登录问题"
    echo "========================================="
    echo ""
    
    local issues=0
    
    # 1. 检查 Flask 服务状态
    echo -n "检查 Flask 服务状态... "
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}[运行中]${NC}"
    else
        echo -e "${RED}[未运行]${NC} ⚠️ 这是登录失败的根因！"
        issues=$((issues + 1))
    fi
    
    # 2. 检查 Flask 端口监听
    echo -n "检查 Flask 端口 ($FLASK_PORT)... "
    if lsof -Pi :$FLASK_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}[监听中]${NC}"
    else
        echo -e "${RED}[未监听]${NC} ⚠️ Flask 服务未启动！"
        issues=$((issues + 1))
    fi
    
    # 3. 检查登录 API
    echo -n "检查登录 API (/api/login)... "
    if curl -f -s -o /dev/null http://localhost:$FLASK_PORT/api/login --max-time 5 -X POST -H "Content-Type: application/json" -d '{}' 2>/dev/null; then
        echo -e "${GREEN}[正常]${NC}"
    else
        echo -e "${RED}[异常]${NC} ⚠️ 登录 API 无法访问！"
        issues=$((issues + 1))
    fi
    
    # 4. 检查 Nginx 服务
    echo -n "检查 Nginx 服务... "
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}[运行中]${NC}"
    else
        echo -e "${RED}[未运行]${NC}"
        issues=$((issues + 1))
    fi
    
    # 5. 检查 Nginx 配置
    echo -n "检查 Nginx 配置... "
    if nginx -t >/dev/null 2>&1; then
        echo -e "${GREEN}[正常]${NC}"
    else
        echo -e "${RED}[异常]${NC}"
        issues=$((issues + 1))
    fi
    
    echo ""
    echo "诊断结果：发现 $issues 个问题"
    echo ""
    
    return $issues
}

# 修复函数
fix_login_issue() {
    echo "========================================="
    echo "修复登录问题"
    echo "========================================="
    echo ""
    
    # 1. 检查服务是否正在运行，如果未运行则启动
    log_info "检查 Flask 服务..."
    if ! systemctl is-active --quiet $SERVICE_NAME; then
        log_warning "Flask 服务未运行，正在启动..."
        systemctl start $SERVICE_NAME
        sleep 3
    else
        log_info "Flask 服务正在运行，尝试重启..."
        systemctl restart $SERVICE_NAME
        sleep 3
    fi
    
    # 2. 验证服务是否启动成功
    if systemctl is-active --quiet $SERVICE_NAME; then
        log_success "Flask 服务启动成功"
    else
        log_error "Flask 服务启动失败"
        echo ""
        echo "查看详细错误信息："
        systemctl status $SERVICE_NAME --no-pager -l
        echo ""
        log_error "服务启动失败，请检查日志："
        echo "  journalctl -u $SERVICE_NAME -n 50"
        return 1
    fi
    
    # 3. 检查端口监听
    log_info "检查端口监听..."
    if lsof -Pi :$FLASK_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        log_success "Flask 端口 $FLASK_PORT 正常监听"
    else
        log_error "Flask 端口 $FLASK_PORT 未监听"
        return 1
    fi
    
    # 4. 测试登录 API
    log_info "测试登录 API..."
    if curl -f -s -o /dev/null http://localhost:$FLASK_PORT/api/login --max-time 5 -X POST -H "Content-Type: application/json" -d '{}' 2>/dev/null; then
        log_success "登录 API 正常"
    else
        log_warning "登录 API 返回异常（可能需要认证参数）"
    fi
    
    # 5. 重启 Nginx（如果需要）
    if ! systemctl is-active --quiet nginx; then
        log_warning "Nginx 服务未运行，正在启动..."
        systemctl start nginx
        sleep 2
    fi
    
    if systemctl is-active --quiet nginx; then
        log_success "Nginx 服务正常"
    else
        log_error "Nginx 服务异常"
        return 1
    fi
    
    echo ""
    log_success "所有服务已修复完成！"
    return 0
}

# 验证函数
verify_fix() {
    echo ""
    echo "========================================="
    echo "验证修复结果"
    echo "========================================="
    echo ""
    
    local passed=0
    local total=5
    
    # 1. 检查 Flask 服务
    echo -n "1. Flask 服务状态... "
    if systemctl is-active --quiet $SERVICE_NAME; then
        echo -e "${GREEN}✓ 通过${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ 失败${NC}"
    fi
    
    # 2. 检查 Flask 端口
    echo -n "2. Flask 端口监听... "
    if lsof -Pi :$FLASK_PORT -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ 失败${NC}"
    fi
    
    # 3. 检查 Nginx 服务
    echo -n "3. Nginx 服务状态... "
    if systemctl is-active --quiet nginx; then
        echo -e "${GREEN}✓ 通过${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ 失败${NC}"
    fi
    
    # 4. 检查 HTTP 访问
    echo -n "4. HTTP 访问测试... "
    if curl -f -s -o /dev/null http://localhost/ --max-time 5 2>/dev/null; then
        echo -e "${GREEN}✓ 通过${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ 失败${NC}"
    fi
    
    # 5. 检查 HTTPS 访问
    echo -n "5. HTTPS 访问测试... "
    if curl -kf -s -o /dev/null https://localhost/ --max-time 5 2>/dev/null; then
        echo -e "${GREEN}✓ 通过${NC}"
        passed=$((passed + 1))
    else
        echo -e "${RED}✗ 失败${NC}"
    fi
    
    echo ""
    echo "验证结果：$passed/$total 通过"
    
    if [ $passed -eq $total ]; then
        echo -e "${GREEN}✓ 所有验证通过！登录功能已恢复正常${NC}"
        return 0
    else
        echo -e "${YELLOW}⚠️ 部分验证未通过，请检查日志${NC}"
        return 1
    fi
}

# 显示测试指南
show_test_guide() {
    echo ""
    echo "========================================="
    echo "测试登录功能"
    echo "========================================="
    echo ""
    echo "请在浏览器中测试以下功能："
    echo ""
    echo "1. 访问网站"
    echo "   URL: https://$DOMAIN"
    echo ""
    echo "2. 尝试登录"
    echo "   - 打开浏览器开发者工具 (F12)"
    echo "   - 切换到 Network 标签"
    echo "   - 输入用户名和密码登录"
    echo "   - 检查 /api/login 请求是否返回 200 OK"
    echo ""
    echo "3. 验证登录成功"
    echo "   - 应该能成功登录"
    echo "   - 不应该出现 502 错误"
    echo ""
    echo "如果仍然出现 502 错误："
    echo "  1. 查看详细日志:"
    echo "     journalctl -u $SERVICE_NAME -f"
    echo "  2. 查看错误日志:"
    echo "     tail -f /var/log/flask-app-error.log"
    echo "  3. 运行完整诊断:"
    echo "     cd $APP_DIR && bash scripts/diagnose-and-fix.sh"
    echo ""
}

# 主函数
main() {
    print_banner
    
    # 诊断问题
    diagnose_login_issue
    
    # 修复问题
    if fix_login_issue; then
        # 验证修复
        verify_fix
        
        # 显示测试指南
        show_test_guide
        
        echo ""
        echo "================================================================================"
        echo -e "${GREEN}✓ 修复完成！登录功能应该已经恢复正常${NC}"
        echo "================================================================================"
        echo ""
        echo "查看日志命令："
        echo "  Flask 日志: journalctl -u $SERVICE_NAME -f"
        echo "  错误日志:   tail -f /var/log/flask-app-error.log"
        echo "  Nginx 日志:  tail -f /var/log/nginx/error.log"
        echo ""
    else
        echo ""
        echo "================================================================================"
        echo -e "${RED}✗ 修复失败，请查看上述错误信息${NC}"
        echo "================================================================================"
        exit 1
    fi
}

# 执行主函数
main "$@"
