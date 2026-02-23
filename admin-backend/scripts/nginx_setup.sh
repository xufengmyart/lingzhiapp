#!/bin/bash
# ============================================
# 灵值生态园 - Nginx 安装和配置脚本
# Lingzhi Ecosystem - Nginx Setup Script
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 日志函数
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 root 权限运行此脚本"
    exit 1
fi

echo -e "${BLUE}"
echo "============================================"
echo "  灵值生态园 - Nginx 配置"
echo "  Lingzhi Ecosystem - Nginx Setup"
echo "============================================"
echo -e "${NC}"

# 1. 更新包管理器
log_info "更新包管理器..."
apt-get update -y

# 2. 安装 Nginx
log_info "安装 Nginx..."
if ! command -v nginx &> /dev/null; then
    apt-get install -y nginx
    log_success "Nginx 安装完成"
else
    log_info "Nginx 已安装"
fi

# 3. 备份原配置
NGINX_CONF="/etc/nginx/sites-available/default"
if [ -f "$NGINX_CONF" ]; then
    cp "$NGINX_CONF" "$NGINX_CONF.backup.$(date +%Y%m%d_%H%M%S)"
    log_success "原配置已备份"
fi

# 4. 创建必要目录
log_info "创建必要目录..."
mkdir -p /var/www/html
mkdir -p /var/cache/nginx
mkdir -p /etc/letsencrypt
log_success "目录创建完成"

# 5. 复制配置文件
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
NGINX_CONFIG_FILE="$PROJECT_ROOT/nginx/nginx-http.conf"

if [ -f "$NGINX_CONFIG_FILE" ]; then
    cp "$NGINX_CONFIG_FILE" /etc/nginx/sites-available/meiyueart
    log_success "Nginx 配置文件已复制"

    # 创建符号链接
    ln -sf /etc/nginx/sites-available/meiyueart /etc/nginx/sites-enabled/

    # 删除默认配置
    rm -f /etc/nginx/sites-enabled/default
    log_success "Nginx 配置已启用"
else
    log_error "找不到配置文件: $NGINX_CONFIG_FILE"
    exit 1
fi

# 6. 测试配置
log_info "测试 Nginx 配置..."
nginx -t
if [ $? -eq 0 ]; then
    log_success "Nginx 配置测试通过"
else
    log_error "Nginx 配置测试失败"
    exit 1
fi

# 7. 启动 Nginx
log_info "启动 Nginx..."
systemctl enable nginx
systemctl start nginx
log_success "Nginx 已启动"

# 8. 检查状态
log_info "检查 Nginx 状态..."
if systemctl is-active --quiet nginx; then
    log_success "Nginx 运行正常"
else
    log_error "Nginx 启动失败"
    exit 1
fi

# 9. 显示状态
echo ""
log_info "Nginx 配置完成！"
echo ""
echo "配置文件位置:"
echo "  - 主配置: /etc/nginx/sites-available/meiyueart"
echo "  - 日志目录: /var/log/nginx/"
echo ""
echo "服务管理命令:"
echo "  - 启动: systemctl start nginx"
echo "  - 停止: systemctl stop nginx"
echo "  - 重启: systemctl restart nginx"
echo "  - 状态: systemctl status nginx"
echo "  - 重载: systemctl reload nginx"
echo ""
echo "下一步:"
echo "  1. 配置 HTTPS 证书（运行 ssl_cert_setup.sh）"
echo "  2. 修改默认管理员密码"
echo "  3. 设置定时备份"
echo ""
log_success "Nginx 配置完成！"
