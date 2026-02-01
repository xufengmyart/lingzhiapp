#!/usr/bin/env python3
"""
检查旧密码格式的验证方式
"""

import sqlite3
import hashlib
import bcrypt

OLD_DATABASE = '../灵值生态园智能体移植包/src/auth/auth.db'

conn = sqlite3.connect(OLD_DATABASE)
cursor = conn.cursor()

# 查询所有用户
cursor.execute("SELECT id, name, password_hash FROM users")
users = cursor.fetchall()

print("检查旧密码格式...")
print("=" * 80)

for user in users:
    user_id, name, password_hash = user
    
    print(f"\n用户: {name}")
    print(f"密码哈希: {password_hash}")
    print(f"长度: {len(password_hash)}")
    print(f"前缀: {password_hash[:10]}")
    
    # 尝试各种验证方式
    
    # 1. SHA256
    test_password = "123456"  # 常见测试密码
    sha256_hash = hashlib.sha256(test_password.encode()).hexdigest()
    print(f"  SHA256 ({test_password}): {sha256_hash[:10]}... - 匹配: {'✅' if password_hash == sha256_hash else '❌'}")
    
    # 2. MD5
    md5_hash = hashlib.md5(test_password.encode()).hexdigest()
    print(f"  MD5 ({test_password}): {md5_hash[:10]}... - 匹配: {'✅' if password_hash == md5_hash else '❌'}")
    
    # 3. bcrypt
    if password_hash.startswith('$2b$'):
        try:
            result = bcrypt.checkpw(test_password.encode(), password_hash.encode())
            print(f"  bcrypt ({test_password}): 匹配: {'✅' if result else '❌'}")
        except:
            print(f"  bcrypt: 错误")
    else:
        print(f"  bcrypt: 不是 bcrypt 格式")
    
    # 4. 简单的字符串比较
    if password_hash == "hashed_password":
        print(f"  简单字符串: 匹配: {'✅' if password_hash == 'hashed_password' else '❌'}")

conn.close()
