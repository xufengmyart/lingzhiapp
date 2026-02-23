#!/usr/bin/env python3
"""
查看数据库中所有表和结构
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin-backend'))

from database import get_db

def show_tables():
    """显示所有表"""
    conn = get_db()
    
    print("数据库中的所有表:")
    print("=" * 80)
    
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    
    for table in tables:
        table_name = table[0]
        print(f"\n表名: {table_name}")
        print("-" * 80)
        
        # 获取表结构
        columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        
        print(f"{'列名':<30} {'类型':<15} {'非空':<8} {'默认值':<20} {'主键':<8}")
        print("-" * 80)
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            not_null_str = "是" if not_null else "否"
            default_val_str = str(default_val) if default_val else ""
            pk_str = "是" if pk else "否"
            print(f"{col_name:<30} {col_type:<15} {not_null_str:<8} {default_val_str:<20} {pk_str:<8}")
    
    conn.close()

if __name__ == '__main__':
    show_tables()
