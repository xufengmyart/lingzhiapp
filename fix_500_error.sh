#!/bin/bash

echo "========================================"
echo "🔧 修复500错误 - 完整方案"
echo "========================================"
echo ""

# 步骤1：检查并启动后端服务
echo "步骤1：检查后端服务..."
cd /root/admin-backend

# 检查是否有后端服务在运行
if ps aux | grep -v grep | grep -q "python.*app.py"; then
    echo "✅ 后端服务正在运行"
    # 获取进程ID
    PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
    echo "   进程ID: $PID"
else
    echo "⚠️  后端服务未运行，正在启动..."
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    sleep 3
    if ps aux | grep -v grep | grep -q "python.*app.py"; then
        echo "✅ 后端服务已启动"
    else
        echo "❌ 后端服务启动失败"
        echo "查看日志："
        tail -50 /tmp/backend.log
    fi
fi

echo ""

# 步骤2：检查后端API
echo "步骤2：测试后端API..."
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ 后端API正常（HTTP 200）"
else
    echo "❌ 后端API异常（HTTP $API_STATUS）"
    echo "尝试重启后端服务..."
    pkill -f "python.*app.py"
    sleep 2
    cd /root/admin-backend
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    sleep 3
    API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status)
    if [ "$API_STATUS" = "200" ]; then
        echo "✅ 后端API已恢复"
    else
        echo "❌ 后端API仍然异常"
        tail -50 /tmp/backend.log
    fi
fi

echo ""

# 步骤3：检查前端文件
echo "步骤3：检查前端文件..."
if [ -f /var/www/frontend/index.html ]; then
    echo "✅ index.html 存在"
else
    echo "❌ index.html 不存在"
fi

if [ -d /var/www/frontend/assets ]; then
    echo "✅ assets 目录存在"
    echo "   文件数量: $(ls -1 /var/www/frontend/assets/ | wc -l)"
else
    echo "❌ assets 目录不存在"
fi

echo ""

# 步骤4：检查Nginx配置
echo "步骤4：检查Nginx配置..."
nginx -t 2>&1 | grep "successful" > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Nginx配置正确"
else
    echo "❌ Nginx配置有误"
    nginx -t
fi

echo ""

# 步骤5：重启Nginx
echo "步骤5：重启Nginx..."
systemctl reload nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx已重启"
else
    echo "❌ Nginx重启失败"
fi

echo ""

# 步骤6：完整测试
echo "========================================"
echo "步骤6：完整测试"
echo "========================================"
echo ""

echo "测试1：后端API"
curl -s http://127.0.0.1:8001/api/status | head -5
echo ""

echo "测试2：前端页面"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" https://meiyueart.com/
echo ""

echo "测试3：登录页面"
curl -s -o /dev/null -w "HTTP状态码: %{http_code}\n" https://meiyueart.com/login
echo ""

# 步骤7：显示日志
echo "========================================"
echo "步骤7：最新日志"
echo "========================================"
echo ""

echo "Nginx错误日志（最近10行）："
tail -10 /var/log/nginx/error.log
echo ""

echo "后端日志（最近10行）："
if [ -f /tmp/backend.log ]; then
    tail -10 /tmp/backend.log
else
    echo "后端日志文件不存在"
fi

echo ""
echo "========================================"
echo "✅ 修复完成"
echo "========================================"
echo ""
echo "📱 请重新访问 https://meiyueart.com/login"
echo "💡 如果问题仍然存在，请检查上述日志"
echo ""
