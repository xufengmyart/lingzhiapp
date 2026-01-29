#!/usr/bin/env python3
"""
更新 referrals 表结构
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

def update_referrals_table():
    """更新 referrals 表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("检查 referrals 表结构...")
    
    # 获取表结构
    cursor.execute("PRAGMA table_info(referrals)")
    columns = cursor.fetchall()
    
    print("\n当前列:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 检查是否缺少列
    column_names = [col[1] for col in columns]
    
    required_columns = {
        'referral_code': 'VARCHAR(50)',
        'relationship_type': 'VARCHAR(20)',
        'status': 'VARCHAR(20)'
    }
    
    print("\n添加缺失的列...")
    for col_name, col_type in required_columns.items():
        if col_name not in column_names:
            try:
                cursor.execute(f"ALTER TABLE referrals ADD COLUMN {col_name} {col_type}")
                print(f"✅ 添加列: {col_name}")
            except Exception as e:
                print(f"⚠️  添加列 {col_name} 失败: {str(e)}")
        else:
            print(f"  ✓ 列已存在: {col_name}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ referrals 表结构更新完成！")
    print("="*80)


if __name__ == "__main__":
    update_referrals_table()
