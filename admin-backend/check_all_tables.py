#!/usr/bin/env python3
"""
全面检查所有数据库表的数据情况
"""

import sqlite3
import os

# 数据库路径
OLD_DATABASE = '../灵值生态园智能体移植包/src/auth/auth.db'
NEW_DATABASE = 'lingzhi_ecosystem.db'

def check_all_tables(db_path, db_name):
    """检查数据库中的所有表"""
    print("\n" + "=" * 80)
    print(f"检查数据库: {db_name}")
    print("=" * 80)
    
    if not os.path.exists(db_path):
        print(f"  ❌ 数据库不存在")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = cursor.fetchall()
    
    print(f"\n表总数: {len(tables)}")
    print(f"\n{'表名':<30} {'记录数':<10}")
    print("-" * 80)
    
    table_info = {}
    
    for table in tables:
        table_name = table[0]
        if table_name == 'sqlite_sequence':
            continue
        
        # 获取记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        
        table_info[table_name] = count
        print(f"{table_name:<30} {count:<10}")
    
    conn.close()
    
    return table_info

def check_table_structure(db_path, table_name):
    """检查表结构"""
    print("\n" + "-" * 80)
    print(f"表结构: {table_name}")
    print("-" * 80)
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取表结构
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print(f"\n{'字段名':<20} {'类型':<15} {'允许空':<8} {'默认值':<15} {'主键':<6}")
    print("-" * 80)
    
    for col in columns:
        col_id, name, type_, not_null, default_val, pk = col
        print(f"{name:<20} {type_:<15} {'NO' if not_null else 'YES':<8} {str(default_val):<15} {'是' if pk else '否':<6}")
    
    # 获取前 5 条数据示例
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 5")
    rows = cursor.fetchall()
    
    if rows:
        print(f"\n数据示例（前 5 条）：")
        print("-" * 80)
        col_names = [col[1] for col in columns]
        print(" | ".join([f"{name:<20}" for name in col_names]))
        print("-" * 80)
        
        for row in rows:
            print(" | ".join([f"{str(val)[:20]:<20}" for val in row]))
    
    conn.close()

# 检查旧数据库
old_tables = check_all_tables(OLD_DATABASE, "旧数据库")

# 检查新数据库
new_tables = check_all_tables(NEW_DATABASE, "新数据库")

# 对比差异
print("\n" + "=" * 80)
print("数据对比")
print("=" * 80)

print(f"\n{'表名':<30} {'旧数据库':<10} {'新数据库':<10} {'状态':<15}")
print("-" * 80)

# 所有表的并集
all_tables = set(old_tables.keys()) | set(new_tables.keys())

for table in sorted(all_tables):
    old_count = old_tables.get(table, 0)
    new_count = new_tables.get(table, 0)
    
    if table == 'sqlite_sequence':
        continue
    
    if old_count > 0 and new_count == 0:
        status = "❌ 未迁移"
    elif old_count == new_count:
        status = "✅ 已同步"
    elif new_count > old_count:
        status = "⬆️ 新增"
    elif new_count < old_count:
        status = "⬇️ 缺失"
    else:
        status = "⚠️ 部分同步"
    
    print(f"{table:<30} {old_count:<10} {new_count:<10} {status:<15}")

# 详细检查未迁移的表
print("\n" + "=" * 80)
print("详细检查未迁移的表")
print("=" * 80)

for table in sorted(all_tables):
    old_count = old_tables.get(table, 0)
    new_count = new_tables.get(table, 0)
    
    if old_count > 0 and new_count == 0 and table != 'sqlite_sequence':
        print(f"\n❌ 表 {table} 有 {old_count} 条记录未迁移！")
        check_table_structure(OLD_DATABASE, table)
