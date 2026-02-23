#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户恢复脚本
用于恢复丢失的用户数据
"""

import sqlite3
import sys
from datetime import datetime

DATABASE = 'admin-backend/data/lingzhi_ecosystem.db'

# 常用用户列表（用于恢复）
USERS_TO_RESTORE = [
    {
        'username': '许韩玲',
        'password': '123',
        'total_lingzhi': 100,
        'real_name': '许韩玲',
        'phone': '13800000030',
        'email': 'xuhanling@example.com'
    },
    {
        'username': '许韩冰',
        'password': '123',
        'total_lingzhi': 50,
        'real_name': '许韩冰',
        'phone': '13800000031',
        'email': 'xuhanbing@example.com'
    },
    {
        'username': '许韩美',
        'password': '123',
        'total_lingzhi': 30,
        'real_name': '许韩美',
        'phone': '13800000032',
        'email': 'xuhanmei@example.com'
    }
]

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """哈希密码 - 使用scrypt格式"""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password, method='scrypt')

def restore_user(user_data):
    """恢复用户"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # 检查用户是否已存在
        cursor.execute(
            "SELECT id, username FROM users WHERE username = ? OR phone = ?",
            (user_data['username'], user_data['phone'])
        )
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"⚠️  用户已存在: {existing_user['username']} (ID: {existing_user['id']})")
            print(f"   更新用户数据...")

            # 更新用户信息
            cursor.execute(
                """
                UPDATE users SET
                    real_name = ?,
                    phone = ?,
                    email = ?,
                    total_lingzhi = ?
                WHERE id = ?
                """,
                (
                    user_data['real_name'],
                    user_data['phone'],
                    user_data['email'],
                    user_data['total_lingzhi'],
                    existing_user['id']
                )
            )
            conn.commit()
            print(f"✅ 用户信息已更新: {user_data['username']}")
        else:
            # 创建新用户
            cursor.execute(
                """
                INSERT INTO users (
                    username, password_hash, phone, email,
                    total_lingzhi, real_name, status, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, 'active', ?)
                """,
                (
                    user_data['username'],
                    hash_password(user_data['password']),
                    user_data['phone'],
                    user_data['email'],
                    user_data['total_lingzhi'],
                    user_data['real_name'],
                    datetime.now().isoformat()
                )
            )
            user_id = cursor.lastrowid
            conn.commit()
            print(f"✅ 用户已创建: {user_data['username']} (ID: {user_id})")

        return True

    except Exception as e:
        print(f"❌ 恢复用户失败: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def restore_all_users():
    """恢复所有用户"""
    print("=" * 80)
    print("用户恢复脚本")
    print("=" * 80)

    restored_count = 0
    failed_count = 0

    for user_data in USERS_TO_RESTORE:
        print(f"\n正在恢复用户: {user_data['username']}")
        print("-" * 80)

        if restore_user(user_data):
            restored_count += 1
        else:
            failed_count += 1

    print("\n" + "=" * 80)
    print("恢复完成")
    print("=" * 80)
    print(f"✅ 成功恢复: {restored_count} 个用户")
    print(f"❌ 恢复失败: {failed_count} 个用户")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        # 恢复指定用户
        username = sys.argv[1]
        for user_data in USERS_TO_RESTORE:
            if user_data['username'] == username:
                restore_user(user_data)
                break
        else:
            print(f"❌ 未找到用户: {username}")
    else:
        # 恢复所有用户
        restore_all_users()
