#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户清理脚本
删除测试用户，保留正式用户
"""

import sqlite3
import sys
from datetime import datetime

DATABASE = 'admin-backend/data/lingzhi_ecosystem.db'

# 需要保留的用户（用户名列表）
USERS_TO_KEEP = [
    'admin',           # 管理员
    '许锋',             # 正式用户
    '许韩玲',           # 正式用户
    '黄爱莉',           # 正式用户（需要创建）
    '许武勤',           # 正式用户（需要创建）
    '弓俊芳',           # 正式用户（需要创建）
    '许芳侠',           # 正式用户（需要创建）
    '许明芳',           # 正式用户（需要创建）
    '许秀芳',           # 正式用户（需要创建）
    'cto',              # 系统用户
    'ceo',              # 系统用户
    '许蓝月',           # 可能是正式用户
]

# 需要创建的用户
USERS_TO_CREATE = [
    {
        'username': '黄爱莉',
        'password': '123',
        'total_lingzhi': 100,
        'real_name': '黄爱莉',
        'phone': '13800000040',
        'email': 'huangaili@example.com'
    },
    {
        'username': '许武勤',
        'password': '123',
        'total_lingzhi': 100,
        'real_name': '许武勤',
        'phone': '13800000041',
        'email': 'xuwuqin@example.com'
    },
    {
        'username': '弓俊芳',
        'password': '123',
        'total_lingzhi': 100,
        'real_name': '弓俊芳',
        'phone': '13800000042',
        'email': 'gongjunfang@example.com'
    },
    {
        'username': '许芳侠',
        'password': '123',
        'total_lingzhi': 100,
        'real_name': '许芳侠',
        'phone': '13800000043',
        'email': 'xufangxia@example.com'
    },
    {
        'username': '许明芳',
        'password': '123',
        'total_lingzhi': 100,
        'real_name': '许明芳',
        'phone': '13800000044',
        'email': 'xumingfang@example.com'
    },
    {
        'username': '许秀芳',
        'password': '123',
        'total_lingzhi': 100,
        'real_name': '许秀芳',
        'phone': '13800000045',
        'email': 'xuxiufang@example.com'
    }
]

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """哈希密码"""
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password, method='scrypt')

def create_user(user_data):
    """创建用户"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # 检查用户是否已存在
        cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (user_data['username'],)
        )
        existing_user = cursor.fetchone()

        if existing_user:
            print(f"⚠️  用户已存在: {user_data['username']} (ID: {existing_user['id']})")
            return False

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
        print(f"❌ 创建用户失败: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def delete_user(user_id, username):
    """删除用户"""
    conn = get_db()
    cursor = conn.cursor()

    try:
        # 删除用户的签到记录
        cursor.execute(
            "DELETE FROM checkin_records WHERE user_id = ?",
            (user_id,)
        )

        # 删除用户
        cursor.execute(
            "DELETE FROM users WHERE id = ?",
            (user_id,)
        )

        conn.commit()
        print(f"✅ 用户已删除: {username} (ID: {user_id})")
        return True

    except Exception as e:
        print(f"❌ 删除用户失败: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def cleanup_users():
    """清理用户"""
    print("=" * 100)
    print("用户清理脚本")
    print("=" * 100)

    conn = get_db()
    cursor = conn.cursor()

    # 查询所有用户
    cursor.execute('SELECT id, username FROM users ORDER BY id')
    all_users = cursor.fetchall()
    conn.close()

    print(f"\n总用户数: {len(all_users)}")
    print(f"需要保留的用户: {len(USERS_TO_KEEP)} 个")
    print(f"需要删除的用户: {len(all_users) - len(USERS_TO_KEEP)} 个（估计）\n")

    # 先创建缺失的用户
    print("=" * 100)
    print("创建缺失的用户")
    print("=" * 100)

    created_count = 0
    for user_data in USERS_TO_CREATE:
        if create_user(user_data):
            created_count += 1

    print(f"\n✅ 成功创建: {created_count} 个用户\n")

    # 删除测试用户
    print("=" * 100)
    print("删除测试用户")
    print("=" * 100)

    deleted_count = 0
    kept_count = 0

    for user in all_users:
        if user['username'] in USERS_TO_KEEP:
            print(f"✅ 保留用户: {user['username']} (ID: {user['id']})")
            kept_count += 1
        else:
            if delete_user(user['id'], user['username']):
                deleted_count += 1

    print("\n" + "=" * 100)
    print("清理完成")
    print("=" * 100)
    print(f"✅ 创建新用户: {created_count} 个")
    print(f"✅ 保留用户: {kept_count} 个")
    print(f"✅ 删除用户: {deleted_count} 个")

if __name__ == '__main__':
    cleanup_users()
