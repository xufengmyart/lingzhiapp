#!/usr/bin/env python3
import sqlite3
import os

# 数据库路径
DATABASE = 'lingzhi_ecosystem.db'

# 连接数据库
conn = sqlite3.connect(DATABASE)
cursor = conn.cursor()

# 查询所有用户及其密码哈希格式
cursor.execute("SELECT id, username, SUBSTR(password_hash, 1, 10) as prefix, LENGTH(password_hash) as length FROM users")
users = cursor.fetchall()

print("数据库中的用户密码格式：")
print("=" * 80)
print(f"{'ID':<5} {'用户名':<20} {'密码前缀':<15} {'长度':<10} {'类型':<20}")
print("-" * 80)

for user in users:
    user_id, username, prefix, length = user
    # 判断密码类型
    if prefix.startswith('$2b$'):
        pwd_type = 'bcrypt'
    elif len(prefix) == 10 and all(c in '0123456789abcdef' for c in prefix):
        pwd_type = 'SHA256'
    else:
        pwd_type = '未知格式'
    
    print(f"{user_id:<5} {username:<20} {prefix:<15} {length:<10} {pwd_type:<20}")

print("=" * 80)
print(f"\n总用户数：{len(users)}")

# 统计各类型密码数量
cursor.execute("SELECT SUBSTR(password_hash, 1, 10) as prefix, COUNT(*) as count FROM users GROUP BY prefix")
stats = cursor.fetchall()

print("\n密码格式统计：")
for prefix, count in stats:
    if prefix.startswith('$2b$'):
        pwd_type = 'bcrypt'
    elif len(prefix) == 10 and all(c in '0123456789abcdef' for c in prefix):
        pwd_type = 'SHA256'
    else:
        pwd_type = '未知格式'
    print(f"  {pwd_type}: {count} 个用户")

conn.close()
