#!/usr/bin/env python3
"""
统一数据库更新脚本
修复所有表结构问题
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

def update_all_tables():
    """更新所有需要的表结构"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("统一数据库更新...")
    print("="*80)
    
    # 1. 创建 referral_commissions 表
    print("\n[1] 创建 referral_commissions 表...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS referral_commissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referral_id INTEGER NOT NULL,
                project_id INTEGER NOT NULL,
                referrer_id INTEGER NOT NULL,
                transaction_amount REAL NOT NULL,
                commission_rate REAL NOT NULL,
                commission_amount REAL NOT NULL,
                dividend_pool_contribution REAL DEFAULT 0.0,
                status VARCHAR(20) DEFAULT 'pending',
                paid_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referral_id) REFERENCES referrals(id),
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (referrer_id) REFERENCES users(id)
            )
        """)
        print("✅ referral_commissions 表创建成功")
    except Exception as e:
        print(f"⚠️  referral_commissions 表创建失败: {str(e)}")
    
    # 2. 更新 projects 表
    print("\n[2] 更新 projects 表...")
    try:
        cursor.execute("PRAGMA table_info(projects)")
        project_columns = [col[1] for col in cursor.fetchall()]
        
        if 'project_name' not in project_columns:
            cursor.execute("ALTER TABLE projects ADD COLUMN project_name VARCHAR(100)")
            print("✅ 添加列: project_name")
        
        if 'current_participants' not in project_columns:
            cursor.execute("ALTER TABLE projects ADD COLUMN current_participants INTEGER DEFAULT 0")
            print("✅ 添加列: current_participants")
    except Exception as e:
        print(f"⚠️  projects 表更新失败: {str(e)}")
    
    # 3. 更新 dividend_distributions 表
    print("\n[3] 创建 dividend_distributions 表...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS dividend_distributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pool_id INTEGER NOT NULL,
                equity_holding_id INTEGER NOT NULL,
                distribution_round INTEGER,
                total_pool_amount REAL,
                user_equity_percentage REAL,
                dividend_amount REAL NOT NULL,
                status VARCHAR(20) DEFAULT 'pending',
                paid_at DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pool_id) REFERENCES dividend_pools(id),
                FOREIGN KEY (equity_holding_id) REFERENCES equity_holdings(id)
            )
        """)
        print("✅ dividend_distributions 表创建成功")
    except Exception as e:
        print(f"⚠️  dividend_distributions 表创建失败: {str(e)}")
    
    # 4. 更新 dividend_pools 表
    print("\n[4] 更新 dividend_pools 表...")
    try:
        cursor.execute("PRAGMA table_info(dividend_pools)")
        pool_columns = [col[1] for col in cursor.fetchall()]
        
        if 'last_dividend_date' not in pool_columns:
            cursor.execute("ALTER TABLE dividend_pools ADD COLUMN last_dividend_date DATETIME")
            print("✅ 添加列: last_dividend_date")
    except Exception as e:
        print(f"⚠️  dividend_pools 表更新失败: {str(e)}")
    
    # 5. 创建 project_profit_distributions 表
    print("\n[5] 创建 project_profit_distributions 表...")
    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS project_profit_distributions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER NOT NULL,
                participation_id INTEGER NOT NULL,
                distribution_round INTEGER,
                profit_amount REAL NOT NULL,
                distribution_date DATETIME,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects(id),
                FOREIGN KEY (participation_id) REFERENCES project_participations(id)
            )
        """)
        print("✅ project_profit_distributions 表创建成功")
    except Exception as e:
        print(f"⚠️  project_profit_distributions 表创建失败: {str(e)}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ 数据库更新完成！")
    print("="*80)


if __name__ == "__main__":
    update_all_tables()
