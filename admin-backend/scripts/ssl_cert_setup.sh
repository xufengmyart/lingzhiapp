#!/bin/bash
# ============================================
# 灵值生态园 - HTTPS 证书配置脚本
# Lingzhi Ecosystem - SSL Certificate Setup
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

# 域名配置
DOMAIN="meiyueart.com"
EMAIL="admin@meiyueart.com"

echo -e "${BLUE}"
echo "============================================"
echo "  灵值生态园 - HTTPS 证书配置"
echo "  Lingzhi Ecosystem - SSL Setup"
echo "============================================"
echo -e "${NC}"

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    log_error "请使用 root 权限运行此脚本"
    exit 1
fi

# 1. 安装 Certbot
log_info "安装 Certbot..."
if ! command -v certbot &> /dev/null; then
    apt-get update -y
    apt-get install -y certbot python3-certbot-nginx
    log_success "Certbot 安装完成"
else
    log_info "Certbot 已安装"
fi

# 2. 创建临时目录
log_info "创建临时目录..."
mkdir -p /var/www/html/.well-known/acme-challenge
log_success "临时目录创建完成"

# 3. 获取 SSL 证书
log_info "获取 SSL 证书..."
log_warning "请确保域名 $DOMAIN 已正确解析到此服务器"

# 测试配置（不实际获取证书）
log_info "测试证书配置..."
certbot certonly --dry-run --webroot -w /var/www/html -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --no-eff-email

if [ $? -eq 0 ]; then
    log_success "证书配置测试通过"
else
    log_error "证书配置测试失败，请检查域名解析"
    exit 1
fi

# 询问是否继续
echo ""
log_warning "即将正式获取 SSL 证书"
read -p "是否继续？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    log_info "已取消操作"
    exit 0
fi

# 4. 正式获取证书
log_info "正在获取 SSL 证书..."
certbot certonly --webroot -w /var/www/html -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --no-eff-email

if [ $? -eq 0 ]; then
    log_success "SSL 证书获取成功"
else
    log_error "SSL 证书获取失败"
    exit 1
fi

# 5. 配置证书自动续期
log_info "配置证书自动续期..."
(crontab -l 2>/dev/null; echo "0 0,12 * * * certbot renew --quiet --post-hook 'systemctl reload nginx'") | crontab -
log_success "证书自动续期已配置"

# 6. 重启 Nginx
log_info "重启 Nginx..."
systemctl reload nginx
log_success "Nginx 已重启"

# 7. 验证证书
log_info "验证 SSL 证书..."
cert_path="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
if [ -f "$cert_path" ]; then
    log_success "SSL 证书验证成功"
    echo ""
    echo "证书信息:"
    openssl x509 -in "$cert_path" -noout -subject -issuer -dates
else
    log_error "SSL 证书验证失败"
    exit 1
fi

# 8. 显示状态
echo ""
log_success "HTTPS 配置完成！"
echo ""
echo "证书位置:"
echo "  - 证书文件: /etc/letsencrypt/live/$DOMAIN/fullchain.pem"
echo "  - 私钥文件: /etc/letsencrypt/live/$DOMAIN/privkey.pem"
echo "  - 链证书: /etc/letsencrypt/live/$DOMAIN/chain.pem"
echo ""
echo "证书管理:"
echo "  - 查看证书: certbot certificates"
echo "  - 续期证书: certbot renew"
echo "  - 取消证书: certbot delete"
echo ""
echo "验证访问:"
echo "  - HTTP: http://$DOMAIN"
echo "  - HTTPS: https://$DOMAIN"
echo ""
log_success "HTTPS 配置完成！"
