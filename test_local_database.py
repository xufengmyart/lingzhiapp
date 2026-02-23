#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""直接在本地测试数据库"""

import sqlite3
import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin-backend'))

from werkzeug.security import check_password_hash, generate_password_hash

DB_PATH = "admin-backend/data/lingzhi_ecosystem.db"

def test_database_passwords():
    """测试数据库中的密码"""
    print("=== 测试数据库密码 ===\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 查询所有用户
    cursor.execute("SELECT id, username, password_hash FROM users")
    users = cursor.fetchall()

    print(f"找到 {len(users)} 个用户:\n")

    for user_id, username, password_hash in users:
        print(f"用户 {username} (ID: {user_id}):")
        print(f"  哈希: {password_hash[:80]}...")

        # 测试密码验证
        test_passwords = ["123", "123456"]
        for pwd in test_passwords:
            result = check_password_hash(password_hash, pwd)
            status = "✅ 通过" if result else "❌ 失败"
            print(f"  密码 '{pwd}': {status}")
        print()

    conn.close()

    # 测试生成新哈希
    print("\n=== 测试生成新哈希 ===\n")
    new_hash = generate_password_hash("123", method="scrypt")
    print(f"生成的新哈希 (密码123): {new_hash}")

    # 验证新哈希
    result = check_password_hash(new_hash, "123")
    print(f"验证密码 '123': {'✅ 通过' if result else '❌ 失败'}")

if __name__ == "__main__":
    test_database_passwords()
