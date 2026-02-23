#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紧急修复：清空并重新设置所有用户密码
修复密码哈希重复问题
"""

import sqlite3
import sys
import os
from werkzeug.security import generate_password_hash, check_password_hash

# 添加项目路径
sys.path.append(os.path.dirname(__file__))
from config import config

def emergency_fix_passwords():
    """紧急修复所有用户密码"""
    print("=== 紧急修复用户密码 ===\n")

    try:
        # 连接数据库
        conn = sqlite3.connect(config.DATABASE_PATH, timeout=30)
        cursor = conn.cursor()

        # 禁用WAL模式
        cursor.execute('PRAGMA journal_mode=DELETE')
        cursor.execute('PRAGMA synchronous=FULL')

        print("步骤 1: 查询所有用户...")
        cursor.execute('SELECT id, username FROM users ORDER BY id')
        users = cursor.fetchall()

        print(f"找到 {len(users)} 个用户\n")

        # 步骤 2: 生成正确的密码哈希
        print("步骤 2: 生成密码123的哈希...")
        new_password_hash = generate_password_hash("123", method='scrypt')
        print(f"密码哈希: {new_password_hash[:50]}...")
        print(f"哈希长度: {len(new_password_hash)}\n")

        # 步骤 3: 为每个用户生成独立的密码哈希
        print("步骤 3: 重置所有用户密码为123...")
        updated_count = 0
        for user_id, username in users:
            # 为每个用户生成独立的哈希（每次生成的哈希都有随机salt）
            user_hash = generate_password_hash("123", method='scrypt')
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (user_hash, user_id)
            )
            updated_count += 1
            print(f"  ✓ 重置用户 {username} (ID: {user_id})")

        conn.commit()

        print(f"\n已重置 {updated_count} 个用户的密码\n")

        # 步骤 4: 验证密码哈希
        print("步骤 4: 验证密码哈希...")
        cursor.execute('SELECT id, username, password_hash FROM users ORDER BY id')
        users = cursor.fetchall()

        print("\n修复后的用户列表:")
        print("-" * 60)
        print(f"{'ID':<6}{'用户名':<15}{'哈希长度':<10}")
        print("-" * 60)

        for user_id, username, password_hash in users:
            print(f"{user_id:<6}{username:<15}{len(password_hash) if password_hash else 0:<10}")

        print("-" * 60)

        # 验证每个用户的密码
        print("\n验证密码哈希:")
        for user_id, username, password_hash in users:
            if password_hash:
                # 测试密码验证
                test_password = "123"
                is_valid = check_password_hash(password_hash, test_password)
                status = "✅ 正确" if is_valid else "❌ 错误"
                print(f"  {username}: {status} (哈希长度: {len(password_hash)})")

                if not is_valid:
                    print(f"    ⚠️  密码验证失败，哈希: {password_hash[:80]}...")

        # 检查重复哈希
        print("\n检查重复哈希:")
        duplicate_count = 0
        for user_id, username, password_hash in users:
            if password_hash and len(password_hash) > 200:  # 正常的scrypt哈希大约162字符
                print(f"  ⚠️  用户 {username} (ID: {user_id}) 的哈希可能重复！长度: {len(password_hash)}")
                duplicate_count += 1

        if duplicate_count == 0:
            print("  ✓ 所有用户密码哈希正常")
        else:
            print(f"  ❌ 发现 {duplicate_count} 个用户可能有重复哈希")

        conn.close()

        print("\n✅ 紧急修复完成！")
        print("\n测试账号:")
        print("  - 所有用户密码: 123")
        print(f"  - 总用户数: {len(users)}")

        return True

    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = emergency_fix_passwords()
    sys.exit(0 if success else 1)
