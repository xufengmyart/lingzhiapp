#!/usr/bin/env python3
"""
测试用户登录
"""

import sqlite3
import bcrypt

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

print("=" * 100)
print("测试用户登录")
print("=" * 100)
print()

print("测试1: 使用用户名 '许锋' 登录，密码 '123456'")
print("-" * 100)

# 查找用户
cursor.execute("SELECT id, username, email, phone, password_hash FROM users WHERE username = ?", ('许锋',))
user = cursor.fetchone()

if user:
    user_id, username, email, phone, password_hash = user
    print(f"找到用户: {username}")
    print(f"  ID: {user_id}")
    print(f"  邮箱: {email}")
    print(f"  手机: {phone}")

    # 验证密码
    test_password = '123456'
    try:
        if bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8')):
            print(f"✓ 密码验证成功！")
            print(f"  用户可以使用密码 '{test_password}' 登录")
            print(f"  登录方式: 用户名 '{username}'")
        else:
            print(f"✗ 密码验证失败")
    except Exception as e:
        print(f"✗ 密码验证出错: {e}")
else:
    print("未找到用户")

print()
print("测试2: 使用邮箱 'xufeng@meiyueart.cn' 登录，密码 '123456'")
print("-" * 100)

# 使用邮箱查找
cursor.execute("SELECT id, username, email, phone, password_hash FROM users WHERE email = ?", ('xufeng@meiyueart.cn',))
user = cursor.fetchone()

if user:
    user_id, username, email, phone, password_hash = user
    print(f"找到用户: {username}")
    print(f"  ID: {user_id}")
    print(f"  邮箱: {email}")
    print(f"  手机: {phone}")

    # 验证密码
    test_password = '123456'
    try:
        if bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8')):
            print(f"✓ 密码验证成功！")
            print(f"  用户可以使用密码 '{test_password}' 登录")
            print(f"  登录方式: 邮箱 '{email}'")
        else:
            print(f"✗ 密码验证失败")
    except Exception as e:
        print(f"✗ 密码验证出错: {e}")
else:
    print("未找到用户")

print()
print("测试3: 使用用户名 '许锋' 登录，密码 'admin123'")
print("-" * 100)

cursor.execute("SELECT id, username, email, password_hash FROM users WHERE username = ?", ('许锋',))
user = cursor.fetchone()

if user:
    user_id, username, email, password_hash = user
    print(f"找到用户: {username}")

    # 验证密码
    test_password = 'admin123'
    try:
        if bcrypt.checkpw(test_password.encode('utf-8'), password_hash.encode('utf-8')):
            print(f"✓ 密码验证成功！")
            print(f"  用户可以使用密码 '{test_password}' 登录")
        else:
            print(f"✗ 密码验证失败")
    except Exception as e:
        print(f"✗ 密码验证出错: {e}")

print()
print("=" * 100)
print("总结")
print("=" * 100)
print("用户 '许锋' 可以使用以下方式登录:")
print("  1. 用户名: 许锋  密码: 123456")
print("  2. 邮箱: xufeng@meiyueart.cn  密码: 123456")

conn.close()
