#!/usr/bin/env python3
"""
检查所有用户信息
"""

import sqlite3

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 查询所有用户
cursor.execute("SELECT id, username, email, phone, total_lingzhi, is_verified, status FROM users")
users = cursor.fetchall()

print("=" * 100)
print("所有用户信息")
print("=" * 100)
print()
print(f"总用户数: {len(users)}")
print()

print(f"{'ID':<5} {'用户名':<15} {'邮箱':<30} {'手机':<15} {'灵值':<10} {'已验证':<8} {'状态':<10}")
print("-" * 100)

for user in users:
    print(f"{user[0]:<5} {user[1]:<15} {user[2]:<30} {user[3]:<15} {user[4]:<10} {'是' if user[5] else '否':<8} {user[6] if user[6] else '正常':<10}")

print()
print("=" * 100)
print("检查'许锋'用户")
print("=" * 100)

# 查找'许锋'用户
cursor.execute("SELECT * FROM users WHERE username LIKE '%许锋%' OR email LIKE '%许锋%'")
xufeng_users = cursor.fetchall()

if xufeng_users:
    for user in xufeng_users:
        print(f"找到用户: {user}")
        print(f"ID: {user[0]}")
        print(f"用户名: {user[1]}")
        print(f"邮箱: {user[2]}")
        print(f"手机: {user[3]}")
        print(f"密码哈希: {user[4]}")
        print(f"灵值: {user[5]}")
        print(f"已验证: {user[6]}")
        print(f"状态: {user[7]}")
        print(f"创建时间: {user[8]}")
        print()
else:
    print("未找到'许锋'用户")

conn.close()
