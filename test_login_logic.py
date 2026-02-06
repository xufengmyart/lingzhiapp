#!/usr/bin/env python3
import bcrypt
import sqlite3

username = "许锋"
password = "password123"

conn = sqlite3.connect('admin-backend/lingzhi_ecosystem.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 查询用户
cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
user = cursor.fetchone()

if user:
    print(f"找到用户: {user['username']}")
    print(f"密码哈希: {user['password_hash']}")

    # 验证密码（使用后端的verify_password逻辑）
    password_hash = user['password_hash']

    if password_hash.startswith('$2b$'):
        try:
            result = bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            print(f"bcrypt验证结果: {result}")
        except Exception as e:
            print(f"bcrypt验证失败: {e}")
else:
    print("未找到用户")

conn.close()
