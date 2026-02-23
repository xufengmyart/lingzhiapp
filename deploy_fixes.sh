#!/bin/bash

# API修复与部署脚本

echo "========================================="
echo "🔧 灵值生态园 - API修复与部署"
echo "========================================="
echo ""

# 1. 复制修复文件到生产环境
echo "📋 步骤 1/5: 上传修复文件到生产环境..."

# 上传SQL脚本
sshpass -p "Meiyue@root123" scp -P 22 -o StrictHostKeyChecking=no \
    /workspace/projects/admin-backend/create_merchants_table.sql \
    root@meiyueart.com:/tmp/

echo "✅ 文件上传完成"

# 2. 在生产环境执行SQL
echo ""
echo "📋 步骤 2/5: 创建缺失的数据库表..."

sshpass -p "Meiyue@root123" ssh -p 22 -o StrictHostKeyChecking=no root@meiyueart.com \
    "sqlite3 /app/meiyueart-backend/data/lingzhi_ecosystem.db < /tmp/create_merchants_table.sql && echo '✅ 商家表创建成功'"

# 3. 验证表是否创建成功
echo ""
echo "📋 步骤 3/5: 验证数据库表..."

sshpass -p "Meiyue@root123" ssh -p 22 -o StrictHostKeyChecking=no root@meiyueart.com \
    "sqlite3 /app/meiyueart-backend/data/lingzhi_ecosystem.db 'SELECT COUNT(*) as count FROM merchants;'"

# 4. 重启后端服务
echo ""
echo "📋 步骤 4/5: 重启后端服务..."

sshpass -p "Meiyue@root123" ssh -p 22 -o StrictHostKeyChecking=no root@meiyueart.com \
    "cd /app/meiyueart-backend && pkill -f 'python.*app.py' && sleep 2 && FLASK_PORT=5000 python3 -u app.py > /tmp/app_restart.log 2>&1 &"

sleep 3

# 5. 验证API是否正常
echo ""
echo "📋 步骤 5/5: 验证API可用性..."

# 登录获取token
echo "   - 测试登录..."
TOKEN=$(curl -s -X POST https://meiyueart.com/api/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"123"}' | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo "   ✅ 登录成功"
    
    # 测试用户信息
    echo "   - 测试用户信息..."
    curl -s https://meiyueart.com/api/user/info \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | grep -q "success.*true" && echo "   ✅ 用户信息API正常" || echo "   ❌ 用户信息API失败"
    
    # 测试商家列表
    echo "   - 测试商家列表..."
    curl -s https://meiyueart.com/api/merchants \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | grep -q "data.*\[" && echo "   ✅ 商家列表API正常" || echo "   ❌ 商家列表API失败"
    
    # 测试文化转译
    echo "   - 测试文化转译..."
    curl -s https://meiyueart.com/api/culture/translation/projects \
        -H "Authorization: Bearer $TOKEN" | python3 -m json.tool | grep -q "count.*[0-9]" && echo "   ✅ 文化转译API正常" || echo "   ❌ 文化转译API失败"
    
else
    echo "   ❌ 登录失败"
fi

echo ""
echo "========================================="
echo "✅ 部署完成"
echo "========================================="
