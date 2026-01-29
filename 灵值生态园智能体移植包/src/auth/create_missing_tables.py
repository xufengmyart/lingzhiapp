#!/usr/bin/env python3
"""
创建缺失的数据库表
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

def create_missing_tables():
    """创建缺失的表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("创建缺失的表...")
    
    # 创建 user_member_levels 表
    print("\n[1] 创建 user_member_levels 表...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_member_levels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                level_id INTEGER NOT NULL,
                contribution_value REAL DEFAULT 0.0,
                team_member_count INTEGER DEFAULT 0,
                total_earned REAL DEFAULT 0.0,
                total_dividend_earned REAL DEFAULT 0.0,
                equity_percentage REAL DEFAULT 0.0,
                level_since DATETIME,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (level_id) REFERENCES member_levels(id)
            )
        """)
        print("✅ user_member_levels 表创建成功")
    except Exception as e:
        print(f"❌ user_member_levels 表创建失败: {str(e)}")
    
    # 创建 equity_holdings 表
    print("\n[2] 创建 equity_holdings 表...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS equity_holdings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                pool_id INTEGER NOT NULL,
                equity_percentage REAL NOT NULL,
                granted_date DATETIME,
                expires_date DATETIME,
                status VARCHAR(20) DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (pool_id) REFERENCES dividend_pools(id)
            )
        """)
        print("✅ equity_holdings 表创建成功")
    except Exception as e:
        print(f"❌ equity_holdings 表创建失败: {str(e)}")
    
    # 创建索引
    print("\n[3] 创建索引...")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_member_levels_user_id ON user_member_levels(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_member_levels_level_id ON user_member_levels(level_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equity_holdings_user_id ON equity_holdings(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_equity_holdings_pool_id ON equity_holdings(pool_id)")
        print("✅ 索引创建成功")
    except Exception as e:
        print(f"❌ 索引创建失败: {str(e)}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ 所有缺失的表创建完成！")
    print("="*80)


if __name__ == "__main__":
    create_missing_tables()
