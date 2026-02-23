#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
灵值生态园 - 导入所有用户到生产数据库
用途：从 admin-backend 数据库导入所有用户到生产数据库
作者：Coze Coding
版本：v1.0
日期：2026-02-11
"""

import sqlite3
import hashlib
import shutil
from datetime import datetime

# 数据库路径
SOURCE_DB = '/workspace/projects/admin-backend/lingzhi_ecosystem.db'
TARGET_DB = '/workspace/projects/lingzhi_ecosystem.db'
DEFAULT_PASSWORD = '123456'

def hash_password(password):
    """密码哈希（SHA256）"""
    return hashlib.sha256(password.encode()).hexdigest()

def get_db_connection(db_path):
    """获取数据库连接"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def export_users_from_source():
    """从源数据库导出所有用户"""
    print("=" * 70)
    print("从源数据库导出用户")
    print("=" * 70)
    
    conn = get_db_connection(SOURCE_DB)
    cursor = conn.cursor()
    
    # 查询所有用户
    cursor.execute('''
        SELECT id, username, phone, email, password_hash, status, 
               real_name, is_verified, login_type, 
               wechat_openid, wechat_unionid, wechat_nickname, wechat_avatar,
               referrer_id, created_at, updated_at
        FROM users
        ORDER BY id
    ''')
    
    users = cursor.fetchall()
    
    print(f"找到 {len(users)} 个用户")
    print()
    
    # 显示前10个用户
    print("前 10 个用户：")
    print("-" * 70)
    print(f"{'ID':<6} {'用户名':<20} {'手机号':<15} {'邮箱':<30} {'状态':<10}")
    print("-" * 70)
    for user in users[:10]:
        print(f"{user['id']:<6} {user['username']:<20} {str(user['phone']):<15} {str(user['email']):<30} {user['status']:<10}")
    
    if len(users) > 10:
        print(f"... 还有 {len(users) - 10} 个用户")
    
    conn.close()
    
    return users

def import_users_to_target(users):
    """导入用户到目标数据库"""
    print()
    print("=" * 70)
    print("导入用户到生产数据库")
    print("=" * 70)
    print()
    
    # 备份目标数据库
    backup_file = f"{TARGET_DB}.backup.before_import.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(TARGET_DB, backup_file)
    print(f"✅ 生产数据库已备份到: {backup_file}")
    print()
    
    conn = get_db_connection(TARGET_DB)
    cursor = conn.cursor()
    
    # 初始化数据库表（如果需要）
    init_db(cursor)
    
    imported = 0
    skipped = 0
    updated = 0
    
    password_hash = hash_password(DEFAULT_PASSWORD)
    
    for user in users:
        # 检查用户是否已存在（按用户名或手机号）
        cursor.execute('''
            SELECT id FROM users 
            WHERE username = ? OR phone = ? OR email = ?
        ''', (user['username'], user['phone'], user['email']))
        
        existing = cursor.fetchone()
        
        user_data = (
            user['username'],
            user['email'],
            user['phone'],
            password_hash,  # 使用统一密码
            user['status'],
            user['real_name'],
            1 if user['is_verified'] else 0,
            user['login_type'],
            user['wechat_openid'],
            user['wechat_unionid'],
            user['wechat_nickname'],
            user['wechat_avatar'],
            user['referrer_id']
        )
        
        if existing:
            # 更新现有用户
            cursor.execute('''
                UPDATE users SET
                    email = ?,
                    phone = ?,
                    password_hash = ?,
                    status = ?,
                    real_name = ?,
                    is_verified = ?,
                    login_type = ?,
                    wechat_openid = ?,
                    wechat_unionid = ?,
                    wechat_nickname = ?,
                    wechat_avatar = ?,
                    referrer_id = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (user_data[1], user_data[2], user_data[3], user_data[4], 
                  user_data[5], user_data[6], user_data[7], user_data[8],
                  user_data[9], user_data[10], user_data[11], user_data[12],
                  existing['id']))
            updated += 1
        else:
            # 插入新用户
            cursor.execute('''
                INSERT INTO users (
                    username, email, phone, password_hash, status, real_name, 
                    is_verified, login_type, wechat_openid, wechat_unionid, 
                    wechat_nickname, wechat_avatar, referrer_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', user_data)
            imported += 1
    
    conn.commit()
    
    # 查询最终用户数量
    cursor.execute('SELECT COUNT(*) FROM users')
    final_count = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"✅ 导入完成！")
    print(f"   新增用户: {imported}")
    print(f"   更新用户: {updated}")
    print(f"   跳过用户: {skipped}")
    print(f"   最终用户数: {final_count}")
    print()
    
    return final_count

def init_db(cursor):
    """初始化数据库表"""
    # 用户表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT,
            phone TEXT,
            password_hash TEXT NOT NULL,
            total_lingzhi INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            last_login_at TIMESTAMP,
            avatar_url TEXT,
            real_name TEXT,
            is_verified BOOLEAN DEFAULT 0,
            login_type TEXT DEFAULT 'phone',
            wechat_openid TEXT,
            wechat_unionid TEXT,
            wechat_nickname TEXT,
            wechat_avatar TEXT,
            referrer_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

def main():
    print("=" * 70)
    print("灵值生态园 - 用户导入工具")
    print("=" * 70)
    print()
    print(f"源数据库: {SOURCE_DB}")
    print(f"目标数据库: {TARGET_DB}")
    print(f"默认密码: {DEFAULT_PASSWORD}")
    print()
    
    # 检查源数据库
    if not sqlite3.connect(SOURCE_DB):
        print(f"❌ 错误：源数据库不存在: {SOURCE_DB}")
        return 1
    
    # 导出用户
    users = export_users_from_source()
    
    if not users:
        print("❌ 源数据库中没有用户")
        return 1
    
    print()
    print(f"⚠️  即将导入 {len(users)} 个用户")
    print(f"⚠️  所有用户密码将被设置为: {DEFAULT_PASSWORD}")
    print()
    
    # 确认
    confirm = input("确认要继续吗？(yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print("操作已取消")
        return 0
    
    # 导入用户
    import_users_to_target(users)
    
    print("=" * 70)
    print("操作完成！")
    print("=" * 70)
    print()
    print("📝 提示：")
    print(f"  - 所有用户的密码为: {DEFAULT_PASSWORD}")
    print("  - 建议用户首次登录后立即修改密码")
    print()
    
    return 0

if __name__ == '__main__':
    import sys
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
