#!/usr/bin/env python3
import bcrypt
import sqlite3

# 生成新密码的哈希
new_password = "password123"
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

print(f"新密码哈希: {password_hash.decode('utf-8')}")

# 更新许锋的密码
conn = sqlite3.connect('admin-backend/lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute("UPDATE users SET password_hash = ? WHERE username = ?", (password_hash.decode('utf-8'), '许锋'))
conn.commit()

print(f"✅ 已更新许锋的密码")

# 验证
cursor.execute("SELECT password_hash FROM users WHERE username = ?", ('许锋',))
result = cursor.fetchone()
if result:
    stored_hash = result[0]
    if bcrypt.checkpw(new_password.encode('utf-8'), stored_hash.encode('utf-8')):
        print("✅ 密码验证成功！")
    else:
        print("❌ 密码验证失败")

conn.close()
