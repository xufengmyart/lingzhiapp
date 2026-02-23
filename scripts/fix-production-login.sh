#!/bin/bash
#
# 生产环境一键修复脚本
# 在生产服务器上执行此脚本即可修复登录问题
#

set -e

echo "========================================="
echo "  灵值生态园 - 生产环境一键修复"
echo "========================================="
echo ""

# 进入后端目录
cd /root/lingzhi-ecosystem/admin-backend

echo "1. 备份数据库..."
cp lingzhi_ecosystem.db lingzhi_ecosystem.db.backup_$(date +%Y%m%d_%H%M%S)
echo "   ✓ 备份完成"

echo ""
echo "2. 修复 admin 用户密码..."
python3 << 'EOF'
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

# 连接数据库
conn = sqlite3.connect("./lingzhi_ecosystem.db")
cursor = conn.cursor()

# 生成新的密码哈希
password = "admin123"
password_hash = generate_password_hash(password)
print(f"   新密码哈希: {password_hash[:30]}...")

# 验证哈希
is_valid = check_password_hash(password_hash, password)
print(f"   密码验证: {'✓ 成功' if is_valid else '✗ 失败'}")

if not is_valid:
    print("   错误: 密码哈希生成失败")
    exit(1)

# 删除旧的 admin 用户
cursor.execute("DELETE FROM users WHERE username = 'admin'")

# 创建新的 admin 用户
cursor.execute(
    """INSERT INTO users (username, password_hash, email, phone, status, is_verified)
       VALUES (?, ?, ?, ?, ?, ?)""",
    ('admin', password_hash, 'admin@meiyueart.com', '', 'active', 1)
)

conn.commit()
print("   ✓ admin 用户重建完成")

# 验证
cursor.execute("SELECT id, username, password_hash FROM users WHERE username = 'admin'")
admin = cursor.fetchone()
if admin:
    print(f"   ✓ 验证成功: ID={admin[0]}, Username={admin[1]}")
else:
    print("   ✗ 验证失败: admin 用户不存在")
    exit(1)

conn.close()
EOF

echo ""
echo "3. 重启服务..."
pkill -f "python.*app.py" || true
sleep 3

nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &

sleep 5

if pgrep -f "python.*app.py" > /dev/null; then
    echo "   ✓ 服务重启成功"
else
    echo "   ✗ 服务启动失败"
    tail -n 20 /var/log/meiyueart-backend/app.log
    exit 1
fi

echo ""
echo "4. 验证登录..."
sleep 3

LOGIN_RESPONSE=$(curl -s -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' 2>/dev/null)

if echo "$LOGIN_RESPONSE" | grep -q "success.*true"; then
    echo "   ✓ 登录测试成功"
else
    echo "   ✗ 登录测试失败"
    echo "   响应: $LOGIN_RESPONSE"
fi

echo ""
echo "========================================="
echo "  ✅ 修复完成！"
echo "========================================="
echo ""
echo "登录信息:"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "访问地址:"
echo "  https://meiyueart.com"
echo ""
