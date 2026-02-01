#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('../灵值生态园智能体移植包/src/auth/auth.db')
cursor = conn.cursor()

cursor.execute("PRAGMA table_info(user_contributions_v2)")
columns = cursor.fetchall()

print("user_contributions_v2 表结构：")
for col in columns:
    print(f"  {col[1]}: {col[2]}")

print("\n前 3 条数据：")
cursor.execute("SELECT * FROM user_contributions_v2 LIMIT 3")
for row in cursor.fetchall():
    print(row)

conn.close()
