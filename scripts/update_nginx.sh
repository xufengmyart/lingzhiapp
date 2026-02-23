#!/bin/bash
# 灵值生态园 - Nginx配置更新脚本
# 用于更新生产环境Nginx配置，解决API 404问题

set -e

echo "============================================================"
echo "灵值生态园 - Nginx配置更新"
echo "============================================================"
echo ""

NGINX_CONF_PATH="/workspace/projects/web-app/nginx.conf"
REMOTE_HOST="123.56.142.143"
REMOTE_USER="root"
REMOTE_NGINX_CONF="/etc/nginx/sites-available/meiyueart"
REMOTE_NGINX_ENABLED="/etc/nginx/sites-enabled/meiyueart"

if [ ! -f "$NGINX_CONF_PATH" ]; then
    echo "✗ 错误: 找不到Nginx配置文件 $NGINX_CONF_PATH"
    exit 1
fi

echo "本地配置文件: $NGINX_CONF_PATH"
echo ""

# 显示配置内容
echo "配置内容预览："
echo "============================================================"
cat "$NGINX_CONF_PATH"
echo "============================================================"
echo ""

# 生成应用脚本
cat > /tmp/apply_nginx_config.sh << 'APPLY_EOF'
#!/bin/bash
set -e

echo "============================================================"
echo "应用Nginx配置"
echo "============================================================"
echo ""

# 1. 备份当前配置
echo "[1/4] 备份当前Nginx配置..."
if [ -f "/etc/nginx/sites-available/default" ]; then
    cp /etc/nginx/sites-available/default /etc/nginx/sites-available/default.backup_$(date +%Y%m%d_%H%M%S)
    echo "✓ 已备份 default 配置"
elif [ -f "/etc/nginx/conf.d/default.conf" ]; then
    cp /etc/nginx/conf.d/default.conf /etc/nginx/conf.d/default.conf.backup_$(date +%Y%m%d_%H%M%S)
    echo "✓ 已备份 default.conf 配置"
fi

# 2. 应用新配置
echo ""
echo "[2/4] 应用新Nginx配置..."
# 确保目录存在
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# 移除旧的软链接
if [ -L "$REMOTE_NGINX_ENABLED" ]; then
    rm -f "$REMOTE_NGINX_ENABLED"
fi

# 复制配置文件
cp /tmp/meiyueart_nginx.conf "$REMOTE_NGINX_CONF"
echo "✓ 配置文件已复制到 $REMOTE_NGINX_CONF"

# 创建软链接
ln -sf "$REMOTE_NGINX_CONF" "$REMOTE_NGINX_ENABLED"
echo "✓ 已创建软链接到 $REMOTE_NGINX_ENABLED"

# 3. 测试配置
echo ""
echo "[3/4] 测试Nginx配置..."
nginx -t
if [ $? -eq 0 ]; then
    echo "✓ Nginx配置测试通过"
else
    echo "✗ Nginx配置测试失败"
    exit 1
fi

# 4. 重启Nginx
echo ""
echo "[4/4] 重启Nginx..."
systemctl reload nginx 2>/dev/null || service nginx reload 2>/dev/null || nginx -s reload 2>/dev/null
echo "✓ Nginx已重新加载"

echo ""
echo "============================================================"
echo "✓ Nginx配置更新完成"
echo "============================================================"
echo ""
echo "API代理配置："
echo "  - /api -> http://127.0.0.1:9000"
echo "  - 超时时间: 600秒"
echo ""
echo "测试API访问："
echo "  curl http://localhost/api/v9/knowledge/items"
echo ""
echo "============================================================"
APPLY_EOF

chmod +x /tmp/apply_nginx_config.sh

echo "============================================================"
echo "Nginx配置更新脚本已生成"
echo "============================================================"
echo ""
echo "配置文件: $NGINX_CONF_PATH"
echo ""
echo "手动应用步骤："
echo "============================================================"
echo "1. 将配置文件上传到服务器:"
echo "   scp $NGINX_CONF_PATH $REMOTE_USER@$REMOTE_HOST:/tmp/meiyueart_nginx.conf"
echo ""
echo "2. 上传并执行应用脚本:"
echo "   scp /tmp/apply_nginx_config.sh $REMOTE_USER@$REMOTE_HOST:/tmp/"
echo "   ssh $REMOTE_USER@$REMOTE_HOST 'bash /tmp/apply_nginx_config.sh'"
echo ""
echo "或者使用完整命令:"
echo "   scp $NGINX_CONF_PATH $REMOTE_USER@$REMOTE_HOST:/tmp/meiyueart_nginx.conf && \\"
echo "   scp /tmp/apply_nginx_config.sh $REMOTE_USER@$REMOTE_HOST:/tmp/ && \\"
echo "   ssh $REMOTE_USER@$REMOTE_HOST 'bash /tmp/apply_nginx_config.sh'"
echo "============================================================"
echo ""
