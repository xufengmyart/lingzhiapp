#!/usr/bin/env python3
"""检查 experts 表的数据"""

import sqlite3

OLD_DATABASE = '../灵值生态园智能体移植包/src/auth/auth.db'
NEW_DATABASE = 'lingzhi_ecosystem.db'

conn_old = sqlite3.connect(OLD_DATABASE)
cursor_old = conn_old.cursor()

# 检查 experts 表是否存在
cursor_old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='experts'")
table_exists = cursor_old.fetchone()

if table_exists:
    print("✅ experts 表存在")
    
    # 获取表结构
    cursor_old.execute("PRAGMA table_info(experts)")
    columns = cursor_old.fetchall()
    print("\n表结构:")
    for col in columns:
        print(f"  - {col[1]} ({col[2]})")
    
    # 获取数据
    cursor_old.execute("SELECT * FROM experts")
    data = cursor_old.fetchall()
    print(f"\n数据量: {len(data)} 条")
    
    if data:
        print("\n前 5 条数据:")
        for i, row in enumerate(data[:5]):
            print(f"  {i+1}. {row}")
else:
    print("❌ experts 表不存在")

conn_old.close()

# 检查新数据库的 experts 表
print("\n" + "=" * 80)
print("检查新数据库的 experts 表...")
print("=" * 80)

conn_new = sqlite3.connect(NEW_DATABASE)
cursor_new = conn_new.cursor()

# 获取表结构
cursor_new.execute("PRAGMA table_info(experts)")
columns = cursor_new.fetchall()
print("\n表结构:")
for col in columns:
    print(f"  - {col[1]} ({col[2]})")

# 获取数据
cursor_new.execute("SELECT * FROM experts")
data = cursor_new.fetchall()
print(f"\n数据量: {len(data)} 条")

if data:
    print("\n数据:")
    for i, row in enumerate(data):
        print(f"  {i+1}. {row}")
else:
    print("  无数据")

conn_new.close()
