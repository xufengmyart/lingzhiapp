#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

print("数据库表列表:")
print("=" * 50)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"- {table[0]}")

print()
print("知识库相关表:")
print("=" * 50)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%kb%' OR name LIKE '%knowledge%')")
kb_tables = cursor.fetchall()
if kb_tables:
    for table in kb_tables:
        print(f"- {table[0]}")
        cursor.execute(f"PRAGMA table_info({table[0]})")
        cols = cursor.fetchall()
        print("  字段:")
        for col in cols:
            print(f"    {col[1]} ({col[2]})")
else:
    print("未找到知识库相关表")

print()
print("公司动态相关表:")
print("=" * 50)
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND (name LIKE '%company%' OR name LIKE '%news%' OR name LIKE '%dynamic%')")
news_tables = cursor.fetchall()
if news_tables:
    for table in news_tables:
        print(f"- {table[0]}")
else:
    print("未找到公司动态相关表")

print()
print("用户统计:")
print("=" * 50)
cursor.execute("SELECT COUNT(*) FROM users")
total_users = cursor.fetchone()[0]
print(f"总用户数: {total_users}")

conn.close()
