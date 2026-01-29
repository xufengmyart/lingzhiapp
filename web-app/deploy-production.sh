#!/bin/bash

# 灵值生态园APP - 生产环境部署脚本

set -e

# 配置变量
APP_NAME="lingzhi-ecosystem"
DEPLOY_DIR="/var/www/lingzhi-ecosystem"
BACKUP_DIR="/var/backups/lingzhi-ecosystem"
NGINX_CONF="/etc/nginx/sites-available/lingzhi-ecosystem"
DOMAIN="${DOMAIN:-yourdomain.com}"

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo "========================================="
echo "灵值生态园APP - 生产环境部署"
echo "========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}请使用root用户或sudo运行此脚本${NC}"
    exit 1
fi

# 步骤1: 安装必要软件
echo -e "${YELLOW}[1/7] 安装必要软件...${NC}"
apt-get update
apt-get install -y nginx nodejs npm certbot python3-certbot-nginx

# 步骤2: 创建目录
echo -e "${YELLOW}[2/7] 创建部署目录...${NC}"
mkdir -p "$DEPLOY_DIR"
mkdir -p "$BACKUP_DIR"
mkdir -p /var/log/nginx

# 步骤3: 备份现有部署（如果存在）
echo -e "${YELLOW}[3/7] 备份现有部署...${NC}"
if [ -d "$DEPLOY_DIR" ]; then
    BACKUP_FILE="$BACKUP_DIR/backup-$(date +%Y%m%d-%H%M%S).tar.gz"
    tar -czf "$BACKUP_FILE" -C "$(dirname $DEPLOY_DIR)" "$(basename $DEPLOY_DIR)"
    echo -e "${GREEN}备份已保存到: $BACKUP_FILE${NC}"
fi

# 步骤4: 复制构建产物
echo -e "${YELLOW}[4/7] 部署应用文件...${NC}"
rm -rf "$DEPLOY_DIR"/*
cp -r dist/* "$DEPLOY_DIR/"

# 设置权限
chown -R www-data:www-data "$DEPLOY_DIR"
chmod -R 755 "$DEPLOY_DIR"

# 步骤5: 配置Nginx
echo -e "${YELLOW}[5/7] 配置Nginx...${NC}"
cp nginx-production.conf "$NGINX_CONF"

# 替换域名
sed -i "s/yourdomain.com/$DOMAIN/g" "$NGINX_CONF"

# 启用站点
ln -sf "$NGINX_CONF" /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# 测试Nginx配置
nginx -t
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Nginx配置测试通过${NC}"
else
    echo -e "${RED}Nginx配置测试失败${NC}"
    exit 1
fi

# 步骤6: 获取SSL证书（可选）
echo -e "${YELLOW}[6/7] 配置SSL证书...${NC}"
read -p "是否配置SSL证书？(需要域名已解析) [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    certbot --nginx -d "$DOMAIN" -d "www.$DOMAIN" --non-interactive --agree-tos --email admin@$DOMAIN
fi

# 步骤7: 重启服务
echo -e "${YELLOW}[7/7] 重启服务...${NC}"
systemctl restart nginx
systemctl enable nginx

echo ""
echo -e "${GREEN}========================================="
echo "部署完成！"
echo "========================================="
echo ""
echo "访问地址:"
echo "  HTTP:  http://$DOMAIN"
echo "  HTTPS: https://$DOMAIN"
echo ""
echo "管理命令:"
echo "  查看日志: tail -f /var/log/nginx/lingzhi-ecosystem-access.log"
echo "  重启Nginx: systemctl restart nginx"
echo "  重载Nginx: systemctl reload nginx"
echo ""
echo "备份位置: $BACKUP_DIR"
echo ""
