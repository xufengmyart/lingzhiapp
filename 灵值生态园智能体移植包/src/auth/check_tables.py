#!/usr/bin/env python3
"""
检查数据库中是否有所有必要的表
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

def check_tables():
    """检查数据库中的表"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [t[0] for t in cursor.fetchall()]
    
    print("数据库中的表:")
    for table in tables:
        print(f"  - {table}")
    
    # 检查必要的表
    required_tables = [
        'users',
        'member_levels',
        'user_member_levels',
        'roles',
        'permissions',
        'referrals',
        'projects',
        'dividend_pools',
        'equity_holdings'
    ]
    
    print("\n必要的表检查:")
    for table in required_tables:
        exists = table in tables
        status = "✅" if exists else "❌"
        print(f"  {status} {table}")
    
    conn.close()


if __name__ == "__main__":
    check_tables()
