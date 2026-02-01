#!/usr/bin/env python3
# 迁移旧用户数据到新数据库

import sqlite3
import os

# 数据库路径
OLD_DB = './灵值生态园智能体移植包/src/auth/auth.db'
NEW_DB = './admin-backend/lingzhi_ecosystem.db'

def migrate_users():
    """迁移用户数据"""
    if not os.path.exists(OLD_DB):
        print(f"旧数据库不存在: {OLD_DB}")
        return
    
    # 连接旧数据库
    old_conn = sqlite3.connect(OLD_DB)
    old_cursor = old_conn.cursor()
    
    # 查询旧用户
    old_cursor.execute("SELECT id, name, email, phone, password_hash, created_at FROM users")
    old_users = old_cursor.fetchall()
    
    if not old_users:
        print("旧数据库中没有用户数据")
        old_conn.close()
        return
    
    print(f"找到 {len(old_users)} 个旧用户")
    
    # 连接新数据库
    new_conn = sqlite3.connect(NEW_DB)
    new_cursor = new_conn.cursor()
    
    migrated_count = 0
    skipped_count = 0
    
    for old_user in old_users:
        old_id, name, email, phone, password_hash, created_at = old_user
        
        # 检查是否已存在（按邮箱）
        new_cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if new_cursor.fetchone():
            print(f"跳过（已存在）: {name} ({email})")
            skipped_count += 1
            continue
        
        # 插入新用户
        try:
            new_cursor.execute(
                "INSERT INTO users (username, email, phone, password_hash, total_lingzhi, created_at) VALUES (?, ?, ?, ?, 0, ?)",
                (name, email, phone or '', password_hash, created_at)
            )
            migrated_count += 1
            print(f"✓ 迁移: {name} ({email})")
        except Exception as e:
            print(f"✗ 失败 {name}: {e}")
    
    new_conn.commit()
    new_conn.close()
    old_conn.close()
    
    print(f"\n迁移完成:")
    print(f"  成功: {migrated_count}")
    print(f"  跳过: {skipped_count}")

if __name__ == '__main__':
    migrate_users()
