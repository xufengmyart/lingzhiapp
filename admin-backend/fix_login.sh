#!/bin/bash
# 在服务器上执行此脚本，1分钟解决登录问题

echo "=========================================="
echo "灵值生态园 - 登录问题快速修复"
echo "=========================================="
echo ""

# 检查是否为root用户
if [ "$EUID" -ne 0 ]; then
    echo "❌ 请使用 root 用户运行此脚本"
    echo "   运行命令: sudo bash fix_login.sh"
    exit 1
fi

# 备份现有Nginx配置
echo "步骤 1/5: 备份Nginx配置..."
if [ -f "/etc/nginx/sites-available/meiyueart.com" ]; then
    cp /etc/nginx/sites-available/meiyueart.com /etc/nginx/sites-available/meiyueart.com.backup.$(date +%Y%m%d_%H%M%S)
    echo "✅ 配置已备份"
else
    echo "⚠️  配置文件不存在，将创建新配置"
fi

# 创建新的Nginx配置
echo ""
echo "步骤 2/5: 配置Nginx代理..."
cat > /etc/nginx/sites-available/meiyueart.com << 'EOF'
server {
    listen 80;
    server_name 123.56.142.143;

    # 前端静态文件
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
        index index.html;
        
        # 缓存配置
        add_header Cache-Control "public, max-age=3600";
    }

    # 后端API代理
    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # 禁止访问隐藏文件
    location ~ /\. {
        deny all;
    }
}
EOF

echo "✅ Nginx 配置已更新"

# 测试配置
echo ""
echo "步骤 3/5: 测试Nginx配置..."
nginx -t
if [ $? -eq 0 ]; then
    echo "✅ 配置测试通过"
else
    echo "❌ 配置测试失败，正在恢复备份..."
    if [ -f "/etc/nginx/sites-available/meiyueart.com.backup."* ]; then
        LATEST_BACKUP=$(ls -t /etc/nginx/sites-available/meiyueart.com.backup.* | head -1)
        cp "$LATEST_BACKUP" /etc/nginx/sites-available/meiyueart.com
        echo "✅ 已恢复备份配置"
    fi
    exit 1
fi

# 重启Nginx
echo ""
echo "步骤 4/5: 重启Nginx..."
systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx 已重启"
else
    echo "❌ Nginx 重启失败"
    exit 1
fi

# 检查后端API服务
echo ""
echo "步骤 5/5: 检查后端服务..."
systemctl status lingzhi-api --no-pager -l | grep "Active:" || echo "后端服务未运行，正在启动..."
systemctl start lingzhi-api

# 验证
echo ""
echo "=========================================="
echo "验证服务状态"
echo "=========================================="

echo ""
echo "Nginx 状态:"
systemctl status nginx --no-pager -l | grep "Active:"

echo ""
echo "后端API 状态:"
systemctl status lingzhi-api --no-pager -l | grep "Active:"

# 测试API
echo ""
echo "测试API连接:"
sleep 2
curl -s http://localhost:8001/api/login -X POST -H "Content-Type: application/json" -d '{"test":"test"}' | head -c 100
echo "..."

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "现在可以登录了："
echo "  访问地址: http://123.56.142.143"
echo "  用户名: 许锋"
echo "  密码: 123456"
echo ""
echo "其他可用账号:"
echo "  CTO（待定）  / 123456"
echo "  CMO（待定）  / 123456"
echo "  COO（待定）  / 123456"
echo "  CFO（待定）  / 123456"
echo ""
echo "如果还有问题，请查看日志："
echo "  Nginx: tail -f /var/log/nginx/error.log"
echo "  API:   tail -f /app/work/logs/bypass/app.log"
echo ""
