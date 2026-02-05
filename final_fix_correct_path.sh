#!/bin/bash

echo "========================================"
echo "🔧 完整修复500错误 - 使用正确路径"
echo "========================================"
echo ""

# 步骤1：应用Nginx配置
echo "步骤1：应用Nginx配置..."
cat > /etc/nginx/sites-enabled/default << 'NGINX_CONFIG'
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com;

    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 前端静态文件（优先级最高，处理所有前端路由）
    location / {
        root /var/www/frontend;
        try_files $uri $uri/ /index.html;
        index index.html;

        # 禁用缓存
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    # API反向代理（仅处理 /api/ 开头的请求）
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 静态资源（强制刷新）
    location ~* \.(jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot)$ {
        root /var/www/frontend;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    }

    # JS/CSS（强制刷新）
    location ~* \.(js|css)$ {
        root /var/www/frontend;
        expires -1;
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
    }

    # Service Worker
    location ~* \.webmanifest$ {
        root /var/www/frontend;
        add_header Cache-Control "public, max-age=3600";
    }
}
NGINX_CONFIG

echo "✅ Nginx配置已更新"

# 步骤2：测试Nginx配置
echo "步骤2：测试Nginx配置..."
nginx -t
if [ $? -ne 0 ]; then
    echo "❌ Nginx配置测试失败"
    exit 1
fi
echo "✅ Nginx配置测试通过"

# 步骤3：清理旧进程
echo "步骤3：清理旧进程..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 2
echo "✅ 旧进程已清理"

# 步骤4：查找并启动后端服务
echo "步骤4：启动后端服务..."
BACKEND_PATH="/root/lingzhi-ecosystem/admin-backend"

if [ -f "$BACKEND_PATH/app.py" ]; then
    echo "✅ 找到后端文件: $BACKEND_PATH/app.py"
    
    cd "$BACKEND_PATH"
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    sleep 5

    if ps aux | grep -v grep | grep -q "python.*app.py"; then
        echo "✅ 后端服务已启动"
        PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
        echo "   进程ID: $PID"
        echo "   工作目录: $BACKEND_PATH"
    else
        echo "❌ 后端服务启动失败"
        echo "查看日志："
        tail -50 /tmp/backend.log
        exit 1
    fi
else
    echo "❌ app.py 不存在于 $BACKEND_PATH"
    echo "尝试查找app.py..."
    find /root -name "app.py" -type f 2>/dev/null | head -10
    exit 1
fi

# 步骤5：测试后端API
echo "步骤5：测试后端API..."
sleep 2
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ 后端API正常（HTTP 200）"
else
    echo "⚠️  后端API返回 $API_STATUS"
    curl -s http://127.0.0.1:8001/api/status | head -3
fi

# 步骤6：重启Nginx
echo "步骤6：重启Nginx..."
systemctl restart nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx已重启"
else
    echo "❌ Nginx重启失败"
    exit 1
fi

# 步骤7：完整测试
echo ""
echo "========================================"
echo "步骤7：完整测试"
echo "========================================"
echo ""

echo "测试1：前端主页"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试2：前端登录页"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/login)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试3：前端注册页"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/register-full)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试4：API状态"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/api/status)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试5：API健康检查"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1/api/health)
echo "HTTP状态码: $HTTP_CODE"

# 步骤8：显示状态
echo ""
echo "========================================"
echo "步骤8：系统状态"
echo "========================================"
echo ""

echo "Nginx状态："
systemctl status nginx --no-pager -l | head -10
echo ""

echo "后端进程："
ps aux | grep "python.*app.py" | grep -v grep || echo "未运行"
echo ""

echo "后端工作目录："
ps aux | grep "python.*app.py" | grep -v grep | awk '{for(i=11;i<=NF;i++)printf $i" ";print ""}'
echo ""

echo "端口监听："
netstat -tlnp 2>/dev/null | grep -E ":(80|443|8001)" || ss -tlnp 2>/dev/null | grep -E ":(80|443|8001)"
echo ""

echo "========================================"
echo "✅ 完整修复完成"
echo "========================================"
echo ""
echo "📱 请清除浏览器缓存后访问："
echo "   - 主页（生态之梦）: https://meiyueart.com"
echo "   - 登录页（旧版）: https://meiyueart.com/login"
echo "   - 注册页: https://meiyueart.com/register-full"
echo ""
echo "💡 清除缓存方法："
echo "   - Windows: Ctrl + Shift + R"
echo "   - Mac: Cmd + Shift + R"
echo "   - 无痕模式: Ctrl + Shift + N"
echo ""
