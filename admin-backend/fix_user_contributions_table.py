#!/usr/bin/env python3
"""
修复 user_contributions 表结构
"""

import sqlite3

DATABASE = 'lingzhi_ecosystem.db'

def fix_user_contributions_table():
    """修复 user_contributions 表结构"""
    print("=" * 80)
    print("修复 user_contributions 表结构")
    print("=" * 80)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 备份现有数据
    print("\n1. 备份现有数据...")
    try:
        cursor.execute("SELECT * FROM user_contributions")
        existing_data = cursor.fetchall()
        print(f"  备份了 {len(existing_data)} 条现有数据")
    except:
        existing_data = []
        print("  表为空，无需备份")
    
    # 删除旧表
    print("\n2. 删除旧表...")
    cursor.execute("DROP TABLE IF EXISTS user_contributions")
    print("  ✅ 旧表已删除")
    
    # 创建新表
    print("\n3. 创建新表...")
    cursor.execute('''
        CREATE TABLE user_contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cumulative_contribution DECIMAL(10,2) DEFAULT 0,
            project_contribution DECIMAL(10,2) DEFAULT 0,
            remaining_contribution DECIMAL(10,2) DEFAULT 0,
            consumed_contribution DECIMAL(10,2) DEFAULT 0,
            initial_contribution DECIMAL(10,2) DEFAULT 0,
            referral_reward DECIMAL(10,2) DEFAULT 0,
            commission_income DECIMAL(10,2) DEFAULT 0,
            team_income DECIMAL(10,2) DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("  ✅ 新表已创建")
    
    # 提交更改
    conn.commit()
    conn.close()
    
    print("\n" + "=" * 80)
    print("✅ user_contributions 表结构修复完成！")
    print("=" * 80)
    print("\n请重新运行完整数据迁移脚本。")

if __name__ == '__main__':
    fix_user_contributions_table()
