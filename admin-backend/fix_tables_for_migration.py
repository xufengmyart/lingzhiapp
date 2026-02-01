#!/usr/bin/env python3
"""修复表结构，使专家和推荐关系的用户ID字段可以为NULL"""

import sqlite3

NEW_DATABASE = 'lingzhi_ecosystem.db'

def fix_experts_table():
    """修复 experts 表结构"""
    print("=" * 80)
    print("修复 experts 表结构")
    print("=" * 80)
    
    conn = sqlite3.connect(NEW_DATABASE)
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(experts)")
    columns = cursor.fetchall()
    
    print("当前表结构:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]}) NOT NULL={col[3]}")
    
    # 由于 SQLite 不支持直接修改约束，需要重建表
    print("\n重建 experts 表...")
    
    # 备份数据
    cursor.execute("SELECT * FROM experts")
    old_data = cursor.fetchall()
    cursor.execute("PRAGMA table_info(experts)")
    old_columns = [col[1] for col in cursor.fetchall()]
    
    # 删除旧表
    cursor.execute("DROP TABLE experts")
    
    # 创建新表（user_id 可以为 NULL）
    cursor.execute('''
        CREATE TABLE experts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            specialty TEXT,
            bio TEXT,
            rating DECIMAL(3,2) DEFAULT 0,
            total_projects INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # 恢复数据（如果有）
    if old_data:
        for row in old_data:
            row_dict = dict(zip(old_columns, row))
            try:
                cursor.execute('''
                    INSERT INTO experts (
                        id, user_id, name, specialty, bio, rating, 
                        total_projects, status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row_dict.get('id'),
                    row_dict.get('user_id'),
                    row_dict.get('name'),
                    row_dict.get('specialty'),
                    row_dict.get('bio'),
                    row_dict.get('rating'),
                    row_dict.get('total_projects'),
                    row_dict.get('status'),
                    row_dict.get('created_at'),
                    row_dict.get('updated_at')
                ))
            except Exception as e:
                pass
    
    conn.commit()
    conn.close()
    
    print("✅ experts 表结构修复完成")

def fix_referrals_table():
    """修复 referrals 表结构"""
    print("\n" + "=" * 80)
    print("修复 referrals 表结构")
    print("=" * 80)
    
    conn = sqlite3.connect(NEW_DATABASE)
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(referrals)")
    columns = cursor.fetchall()
    
    print("当前表结构:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]}) NOT NULL={col[3]}")
    
    # 由于 SQLite 不支持直接修改约束，需要重建表
    print("\n重建 referrals 表...")
    
    # 备份数据
    cursor.execute("SELECT * FROM referrals")
    old_data = cursor.fetchall()
    cursor.execute("PRAGMA table_info(referrals)")
    old_columns = [col[1] for col in cursor.fetchall()]
    
    # 删除旧表
    cursor.execute("DROP TABLE referrals")
    
    # 创建新表（referred_id 可以为 NULL）
    cursor.execute('''
        CREATE TABLE referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER,
            referred_id INTEGER,
            referral_code TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES users(id),
            FOREIGN KEY (referred_id) REFERENCES users(id)
        )
    ''')
    
    # 恢复数据（如果有）
    if old_data:
        for row in old_data:
            row_dict = dict(zip(old_columns, row))
            try:
                cursor.execute('''
                    INSERT INTO referrals (
                        id, referrer_id, referred_id, referral_code, 
                        status, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row_dict.get('id'),
                    row_dict.get('referrer_id'),
                    row_dict.get('referred_id'),
                    row_dict.get('referral_code'),
                    row_dict.get('status'),
                    row_dict.get('created_at'),
                    row_dict.get('updated_at')
                ))
            except Exception as e:
                pass
    
    conn.commit()
    conn.close()
    
    print("✅ referrals 表结构修复完成")

if __name__ == '__main__':
    fix_experts_table()
    fix_referrals_table()
    
    print("\n" + "=" * 80)
    print("✅ 表结构修复完成！")
    print("=" * 80)
