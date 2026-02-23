#!/usr/bin/env python
"""
查看数据库schema
"""
import sys
sys.path.append('admin-backend')

from database import get_db

def show_schema():
    """显示数据库schema"""
    print("数据库Schema:")
    print("=" * 80)
    
    conn = get_db()
    
    # 获取所有表
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    ).fetchall()
    
    print(f"找到 {len(tables)} 个表:\n")
    
    for table in tables:
        table_name = table[0]
        print(f"表名: {table_name}")
        print("-" * 80)
        
        # 获取表结构
        columns = conn.execute(f"PRAGMA table_info({table_name})").fetchall()
        
        print(f"{'列名':<20} {'类型':<15} {'非空':<8} {'默认值':<15} {'主键':<8}")
        print("-" * 80)
        for col in columns:
            col_name = col[1]
            col_type = col[2]
            not_null = "是" if col[3] else "否"
            default_val = str(col[4]) if col[4] else ""
            pk = "是" if col[5] else "否"
            print(f"{col_name:<20} {col_type:<15} {not_null:<8} {default_val:<15} {pk:<8}")
        
        print()
    
    conn.close()

if __name__ == '__main__':
    show_schema()
