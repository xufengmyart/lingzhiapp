#!/usr/bin/env python3
"""
详细检查用户信息和登录状态
"""

import sqlite3
import bcrypt

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

print("=" * 100)
print("用户详细信息")
print("=" * 100)
print()

# 查询所有用户的基本信息
cursor.execute("SELECT id, username, email, phone, password_hash, total_lingzhi, is_verified, status FROM users")
users = cursor.fetchall()

print(f"总用户数: {len(users)}")
print()

for user in users:
    user_id, username, email, phone, password_hash, total_lingzhi, is_verified, status = user

    print(f"用户ID: {user_id}")
    print(f"用户名: {username}")
    print(f"邮箱: {email}")
    print(f"手机: {phone}")
    print(f"灵值: {total_lingzhi}")
    print(f"已验证: {'是' if is_verified else '否'}")
    print(f"状态: {status if status else '正常'}")

    # 检查密码
    if password_hash:
        print(f"密码哈希: {password_hash[:50]}...")
        print(f"密码已设置: 是")

        # 尝试用常见密码测试
        test_passwords = ['123456', 'password', 'admin123', 'xufeng123', 'Meiyue@root123']
        print("测试常见密码:")
        for test_pwd in test_passwords:
            try:
                if bcrypt.checkpw(test_pwd.encode('utf-8'), password_hash.encode('utf-8')):
                    print(f"  ✓ 密码是: {test_pwd}")
                    break
            except:
                continue
        else:
            print(f"  ✗ 常见密码都不匹配")
    else:
        print("密码哈希: None")
        print("密码已设置: 否 - 这是无法登录的原因！")

    print("-" * 100)

print()
print("=" * 100)
print("检查'许锋'用户详情")
print("=" * 100)

cursor.execute("SELECT * FROM users WHERE username = '许锋' OR email LIKE '%xufeng%'")
xufeng_user = cursor.fetchone()

if xufeng_user:
    print("找到'许锋'用户:")
    print(f"  ID: {xufeng_user[0]}")
    print(f"  用户名: {xufeng_user[1]}")
    print(f"  邮箱: {xufeng_user[2]}")
    print(f"  手机: {xufeng_user[3]}")
    print(f"  密码哈希: {xufeng_user[4] if xufeng_user[4] else 'NULL - 无法登录！'}")
    print(f"  灵值: {xufeng_user[5]}")
    print(f"  已验证: {xufeng_user[6]}")
    print(f"  状态: {xufeng_user[7]}")
    print(f"  创建时间: {xufeng_user[8]}")
else:
    print("未找到'许锋'用户")

conn.close()
