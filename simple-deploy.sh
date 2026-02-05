#!/bin/bash

# ==========================================
#  梦幻版页面 - 简易部署脚本
#  直接在服务器上运行
# ==========================================

echo "=========================================="
echo "  梦幻版页面部署"
echo "=========================================="
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"

# 1. 备份
if [ -d "$FRONTEND_DIR" ] && [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ]; then
    echo "备份现有文件..."
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR"
    echo "✓ 备份完成"
fi

# 2. 清空
echo "清空目标目录..."
rm -rf "$FRONTEND_DIR"/*
echo "✓ 清空完成"

# 3. 复制新文件
echo "复制新构建产物..."
if [ -d "/root/public" ]; then
    cp -r /root/public/* "$FRONTEND_DIR/"
elif [ -f "/root/dream-frontend-deploy.tar.gz" ]; then
    mkdir -p /tmp/dream
    tar -xzf /root/dream-frontend-deploy.tar.gz -C /tmp/dream
    cp -r /tmp/dream/* "$FRONTEND_DIR/"
else
    echo "错误：找不到构建产物"
    echo "请上传 dream-frontend-deploy.tar.gz 到 /root/ 目录"
    exit 1
fi

# 4. 设置权限
echo "设置权限..."
chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"

# 5. 重启Nginx
echo "重启Nginx..."
systemctl restart nginx

# 6. 验证
echo ""
echo "=========================================="
echo "  部署结果"
echo "=========================================="
echo ""
echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" 2>/dev/null | grep -E '\.(js|css)$'
echo ""
echo "访问：https://meiyueart.com/dream-selector"
echo "提示：清除浏览器缓存 (Ctrl+Shift+R)"
