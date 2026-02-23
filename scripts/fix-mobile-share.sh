#!/bin/bash

# 手机分享链接修复部署脚本
# 使用方法：sudo ./fix-mobile-share.sh

echo "========================================="
echo "  手机分享链接修复部署脚本"
echo "========================================="
echo ""

# 检查是否以 root 权限运行
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 权限运行此脚本"
    exit 1
fi

# 备份现有配置
echo "1. 备份现有 Nginx 配置..."
BACKUP_DIR="/etc/nginx/backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp /etc/nginx/sites-enabled/meiyueart.conf "$BACKUP_DIR/" 2>/dev/null || true
cp /etc/nginx/conf.d/meiyueart.conf "$BACKUP_DIR/" 2>/dev/null || true
echo "   ✓ 配置已备份到: $BACKUP_DIR"

# 复制新配置
echo ""
echo "2. 部署新的 Nginx 配置..."
PROJECT_DIR="/var/www"
CONFIG_FILE="$PROJECT_DIR/lingzhi-ecosystem/nginx-meiyueart-compatible.conf"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "   ✗ 配置文件不存在: $CONFIG_FILE"
    echo "   请将配置文件复制到服务器后再运行"
    exit 1
fi

# 复制配置到 Nginx 目录
cp "$CONFIG_FILE" /etc/nginx/sites-available/meiyueart.conf
if [ ! -L "/etc/nginx/sites-enabled/meiyueart.conf" ]; then
    ln -s /etc/nginx/sites-available/meiyueart.conf /etc/nginx/sites-enabled/meiyueart.conf
fi
echo "   ✓ 配置文件已部署"

# 测试配置
echo ""
echo "3. 测试 Nginx 配置..."
nginx -t
if [ $? -eq 0 ]; then
    echo "   ✓ 配置测试通过"
else
    echo "   ✗ 配置测试失败，请检查配置文件"
    exit 1
fi

# 重启 Nginx
echo ""
echo "4. 重启 Nginx..."
systemctl reload nginx
echo "   ✓ Nginx 已重新加载"

# 检查服务状态
echo ""
echo "5. 检查服务状态..."
systemctl status nginx --no-pager -l

# 测试访问
echo ""
echo "6. 测试 HTTP 和 HTTPS 访问..."
echo "   HTTP 访问: http://meiyueart.com"
echo "   HTTPS 访问: https://meiyueart.com"

# 显示日志
echo ""
echo "7. 查看 Nginx 日志..."
echo "   HTTP 访问日志: tail -f /var/log/nginx/meiyueart-http-access.log"
echo "   HTTPS 访问日志: tail -f /var/log/nginx/meiyueart-https-access.log"
echo "   HTTP 错误日志: tail -f /var/log/nginx/meiyueart-http-error.log"
echo "   HTTPS 错误日志: tail -f /var/log/nginx/meiyueart-https-error.log"

echo ""
echo "========================================="
echo "  部署完成！"
echo "========================================="
echo ""
echo "请使用手机测试以下链接："
echo "  • HTTP: http://meiyueart.com"
echo "  • HTTPS: https://meiyueart.com"
echo ""
echo "如果遇到问题，请查看日志："
echo "  tail -f /var/log/nginx/*.log"
echo ""
