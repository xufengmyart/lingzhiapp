#!/bin/bash

# 动态资讯用户显示修复 - 快速部署脚本

echo "=========================================="
echo "动态资讯用户显示修复 - 开始部署"
echo "=========================================="

# 停止后端服务
echo "\n[1/4] 停止后端服务..."
pkill -f "python app.py" || true
echo "✓ 后端服务已停止"

# 启动后端服务
echo "\n[2/4] 启动后端服务..."
cd /workspace/projects/admin-backend
nohup python app.py > /var/log/meiyueart-backend/app.log 2>&1 &
echo "✓ 后端服务已启动"

# 等待服务启动
echo "\n[3/4] 等待服务启动..."
sleep 5

# 测试API
echo "\n[4/4] 测试API..."
RESPONSE=$(curl -s http://localhost:5000/api/company/users/activities)

if echo "$RESPONSE" | grep -q '"success":true'; then
    echo "✓ API测试成功"
    TOTAL=$(echo "$RESPONSE" | python -c "import sys, json; print(json.load(sys.stdin).get('total', 0))")
    echo "  返回活动数量: $TOTAL"
else
    echo "✗ API测试失败"
    echo "$RESPONSE"
    exit 1
fi

echo "\n=========================================="
echo "部署完成！"
echo "=========================================="
echo "\n访问地址: https://meiyueart.com/company/users"
echo "\n功能说明:"
echo "  - 显示真实的用户活动数据"
echo "  - 用户名已自动脱敏（保护隐私）"
echo "  - 支持签到、充值、注册等多种活动"
echo "\n注意事项:"
echo "  - admin用户显示为'管理员'"
echo "  - 其他用户显示为前2位+***"
echo "  - 不返回任何敏感信息"
echo "=========================================="
