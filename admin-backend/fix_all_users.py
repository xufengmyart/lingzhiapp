#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量修复用户密码和灵值
- 将所有用户密码重置为123
- 为灵值少于100的用户补齐到100
- 添加相应的灵值消费记录
"""

import sqlite3
import sys
import os
from datetime import datetime
from werkzeug.security import generate_password_hash

# 添加项目路径
sys.path.append(os.path.dirname(__file__))
from config import config

def hash_password(password):
    """哈希密码 - 使用scrypt格式"""
    return generate_password_hash(password, method='scrypt')

def fix_users():
    """修复用户密码和灵值"""
    print("=== 批量修复用户密码和灵值 ===\n")

    try:
        # 连接数据库
        conn = sqlite3.connect(config.DATABASE_PATH, timeout=30)
        cursor = conn.cursor()

        # 禁用WAL模式
        cursor.execute('PRAGMA journal_mode=DELETE')
        cursor.execute('PRAGMA synchronous=FULL')

        print("步骤 1: 查询所有用户...")
        cursor.execute('SELECT id, username, total_lingzhi FROM users ORDER BY id')
        users = cursor.fetchall()

        print(f"找到 {len(users)} 个用户\n")

        # 步骤 2: 重置所有用户密码为123
        print("步骤 2: 重置所有用户密码为123...")
        new_password_hash = hash_password("123")

        updated_count = 0
        for user_id, username, total_lingzhi in users:
            cursor.execute(
                "UPDATE users SET password_hash = ? WHERE id = ?",
                (new_password_hash, user_id)
            )
            updated_count += 1
            print(f"  ✓ 重置用户 {username} (ID: {user_id}) 的密码为 123")

        print(f"\n已重置 {updated_count} 个用户的密码\n")

        # 步骤 3: 为灵值少于100的用户补齐到100
        print("步骤 3: 为灵值少于100的用户补齐到100...")
        cursor.execute('SELECT id, username, total_lingzhi FROM users WHERE total_lingzhi < 100')
        low_lingzhi_users = cursor.fetchall()

        if low_lingzhi_users:
            for user_id, username, current_lingzhi in low_lingzhi_users:
                bonus = 100 - current_lingzhi
                cursor.execute(
                    "UPDATE users SET total_lingzhi = ? WHERE id = ?",
                    (100, user_id)
                )
                print(f"  ✓ 用户 {username} (ID: {user_id}): {current_lingzhi} → 100 (+{bonus})")
        else:
            print("  所有用户灵值都已 >= 100")

        print()

        # 步骤 4: 为用户添加灵值消费记录
        print("步骤 4: 添加灵值消费记录...")
        cursor.execute('''
            SELECT u.id, u.username, u.total_lingzhi
            FROM users u
            WHERE u.total_lingzhi = 100
            AND u.id NOT IN (
                SELECT user_id FROM lingzhi_consumption_records
                WHERE consumption_type = 'new_user_bonus'
            )
        ''')
        users_need_record = cursor.fetchall()

        if users_need_record:
            for user_id, username, total_lingzhi in users_need_record:
                cursor.execute('''
                    INSERT INTO lingzhi_consumption_records
                    (user_id, consumption_type, consumption_item, lingzhi_amount, description)
                    VALUES (?, 'new_user_bonus', 'new_user_bonus', 100, '新用户注册赠送（系统修复）')
                ''', (user_id,))
                print(f"  ✓ 为用户 {username} (ID: {user_id}) 添加灵值消费记录: +100")
        else:
            print("  所有用户都有灵值消费记录")

        print()

        # 步骤 5: 验证修复结果
        print("步骤 5: 验证修复结果...")
        cursor.execute('SELECT id, username, total_lingzhi FROM users ORDER BY id')
        fixed_users = cursor.fetchall()

        print("\n修复后的用户列表:")
        print("-" * 60)
        print(f"{'ID':<6}{'用户名':<15}{'灵值':<10}")
        print("-" * 60)

        for user_id, username, total_lingzhi in fixed_users:
            print(f"{user_id:<6}{username:<15}{total_lingzhi:<10}")

        print("-" * 60)

        # 检查灵值消费记录
        cursor.execute('SELECT COUNT(*) FROM lingzhi_consumption_records WHERE consumption_type = "new_user_bonus"')
        record_count = cursor.fetchone()[0]
        print(f"\n灵值消费记录数: {record_count}")

        # 提交更改
        conn.commit()
        conn.close()

        print("\n✅ 所有修复已完成！")
        print("\n测试账号:")
        print("  - 所有用户密码已重置为: 123")
        print(f"  - 总用户数: {len(users)}")
        print(f"  - 灵值 >= 100 的用户数: {len(users)}")

        return True

    except Exception as e:
        print(f"\n❌ 修复失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = fix_users()
    sys.exit(0 if success else 1)
