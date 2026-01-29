"""
检查数据库当前表结构
"""

import sqlite3
import os

db_path = "auth.db"

if not os.path.exists(db_path):
    print(f"数据库文件不存在：{db_path}")
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("="*60)
    print("数据库表结构检查")
    print("="*60)
    print(f"\n数据库路径: {db_path}")
    print(f"\n共有 {len(tables)} 个表：\n")
    
    for table in tables:
        table_name = table[0]
        print(f"📋 {table_name}")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        
        print("   列信息：")
        for col in columns:
            col_id, name, type_name, not_null, default, pk = col
            pk_str = " [PK]" if pk else ""
            null_str = " NOT NULL" if not_null else ""
            default_str = f" DEFAULT {default}" if default else ""
            print(f"      - {name}: {type_name}{null_str}{default_str}{pk_str}")
        print()
    
    conn.close()
