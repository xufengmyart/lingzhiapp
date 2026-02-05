#!/bin/bash

echo "========================================"
echo "🚀 快速修复500错误"
echo "========================================"
echo ""

# 1. 停止可能冲突的进程
echo "步骤1：清理冲突进程..."
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "gunicorn" 2>/dev/null || true
sleep 2
echo "✅ 进程已清理"
echo ""

# 2. 启动后端服务
echo "步骤2：启动后端服务..."
cd /root/admin-backend
if [ -f app.py ]; then
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    sleep 5

    # 检查进程是否启动
    if ps aux | grep -v grep | grep -q "python.*app.py"; then
        echo "✅ 后端服务已启动"
        PID=$(ps aux | grep "python.*app.py" | grep -v grep | awk '{print $2}')
        echo "   进程ID: $PID"
    else
        echo "❌ 后端服务启动失败"
        echo "查看日志："
        tail -50 /tmp/backend.log
        exit 1
    fi
else
    echo "❌ app.py 不存在于 /root/admin-backend"
    exit 1
fi
echo ""

# 3. 测试后端API
echo "步骤3：测试后端API..."
sleep 2
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8001/api/status)
if [ "$API_STATUS" = "200" ]; then
    echo "✅ 后端API正常（HTTP 200）"
    curl -s http://127.0.0.1:8001/api/status | head -3
else
    echo "❌ 后端API异常（HTTP $API_STATUS）"
    echo "查看后端日志："
    tail -50 /tmp/backend.log
fi
echo ""

# 4. 重启Nginx
echo "步骤4：重启Nginx..."
systemctl reload nginx
if [ $? -eq 0 ]; then
    echo "✅ Nginx已重启"
else
    echo "⚠️  Nginx重启失败，尝试强制重启"
    systemctl restart nginx
fi
echo ""

# 5. 完整测试
echo "========================================"
echo "步骤5：完整测试"
echo "========================================"
echo ""

echo "测试1：后端健康检查"
curl -s http://127.0.0.1:8001/api/health
echo ""

echo ""
echo "测试2：前端主页"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://meiyueart.com/)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试3：登录页面"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://meiyueart.com/login)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "测试4：API登录接口"
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST -H "Content-Type: application/json" -d '{"username":"test","password":"test"}' http://127.0.0.1:8001/api/login)
echo "HTTP状态码: $HTTP_CODE"

echo ""
echo "========================================"
echo "✅ 快速修复完成"
echo "========================================"
echo ""
echo "📱 现在请重新访问："
echo "   - 主页: https://meiyueart.com"
echo "   - 登录: https://meiyueart.com/login"
echo ""
echo "💡 如果问题仍然存在，请运行诊断命令："
echo "   curl -fsSL \"https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/diagnose_500_error_bfc59b58.sh?sign=1770415796-ec04c3158f-0-ef3ea7d816b9ac735740180f2594256e130743e43fc75e8f4b4ee91b204c7326\" | bash"
echo ""
