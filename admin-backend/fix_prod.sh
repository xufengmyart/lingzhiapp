#!/bin/bash

# 生产环境修复脚本
# 用于修复用户密码和总灵值显示问题

echo "=========================================="
echo "生产环境修复脚本"
echo "=========================================="
echo ""

# 数据库路径
DATABASE_PATH="/workspace/projects/admin-backend/lingzhi_ecosystem.db"

# 检查数据库是否存在
if [ ! -f "$DATABASE_PATH" ]; then
    echo "❌ 数据库文件不存在: $DATABASE_PATH"
    exit 1
fi

echo "✅ 找到数据库: $DATABASE_PATH"
echo ""

# 创建临时Python脚本
cat > /tmp/fix_users.py << 'EOF'
import sqlite3
import bcrypt

DATABASE_PATH = "/workspace/projects/admin-backend/lingzhi_ecosystem.db"

USERS = [
    "马伟娟",
    "许锋",
    "许蓝月",
    "黄爱莉",
    "许韩玲",
    "许芳侠",
    "许武勤",
    "弓俊芳",
    "许明芳",
    "许秀芳"
]

PASSWORD = "123"

conn = sqlite3.connect(DATABASE_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("开始重置用户密码...")
print("-" * 50)

success_count = 0
failed_count = 0

for username in USERS:
    # 检查用户是否存在
    cursor.execute("SELECT id, username FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()

    if user:
        # 生成新密码hash
        password_hash = bcrypt.hashpw(PASSWORD.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 更新密码
        cursor.execute("UPDATE users SET password_hash = ? WHERE id = ?", (password_hash, user['id']))
        conn.commit()

        print(f"✅ {username} (ID={user['id']}): 密码已重置为 {PASSWORD}")
        success_count += 1
    else:
        print(f"⚠️  {username}: 用户不存在")
        failed_count += 1

conn.close()

print()
print(f"成功: {success_count} 个, 失败: {failed_count} 个")
print("=" * 50)
EOF

# 执行修复脚本
python3 /tmp/fix_users.py

# 清理临时文件
rm /tmp/fix_users.py

echo ""
echo "=========================================="
echo "✅ 修复完成！"
echo "=========================================="
echo ""
echo "下一步："
echo "1. 重启后端服务: pkill -f app.py && python app.py &"
echo "2. 测试用户登录（用户名: 马伟娟, 密码: 123）"
echo "3. 检查主页总灵值显示"
echo "=========================================="
