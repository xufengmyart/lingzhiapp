#!/usr/bin/env python3
"""检查用户会员等级数据"""

import sqlite3

OLD_DATABASE = '../灵值生态园智能体移植包/src/auth/auth.db'
NEW_DATABASE = 'lingzhi_ecosystem.db'

print("=" * 80)
print("检查用户会员等级数据")
print("=" * 80)

conn_old = sqlite3.connect(OLD_DATABASE)
conn_new = sqlite3.connect(NEW_DATABASE)

cursor_old = conn_old.cursor()
cursor_new = conn_new.cursor()

# 获取旧数据
cursor_old.execute("SELECT * FROM user_member_levels")
old_data = cursor_old.fetchall()
cursor_old.execute("PRAGMA table_info(user_member_levels)")
old_columns = [col[1] for col in cursor_old.fetchall()]

print(f"\n旧数据库: {len(old_data)} 条记录")
if old_data:
    print("\n旧数据:")
    for i, row in enumerate(old_data):
        row_dict = dict(zip(old_columns, row))
        print(f"  {i+1}. ID: {row_dict.get('id')}, User ID: {row_dict.get('user_id')}, Level ID: {row_dict.get('level_id')}")

# 获取新数据
cursor_new.execute("SELECT * FROM user_member_levels")
new_data = cursor_new.fetchall()
cursor_new.execute("PRAGMA table_info(user_member_levels)")
new_columns = [col[1] for col in cursor_new.fetchall()]

print(f"\n新数据库: {len(new_data)} 条记录")
if new_data:
    print("\n新数据:")
    for i, row in enumerate(new_data):
        row_dict = dict(zip(new_columns, row))
        print(f"  {i+1}. ID: {row_dict.get('id')}, User ID: {row_dict.get('user_id')}, Level ID: {row_dict.get('level_id')}")

# 检查旧数据库的用户列表
cursor_old.execute("SELECT id, name, email FROM users")
old_users = cursor_old.fetchall()
print(f"\n旧数据库用户: {len(old_users)} 个")
for user in old_users:
    print(f"  - ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")

# 检查新数据库的用户列表
cursor_new.execute("SELECT id, username, email FROM users")
new_users = cursor_new.fetchall()
print(f"\n新数据库用户: {len(new_users)} 个")
for user in new_users:
    print(f"  - ID: {user[0]}, Name: {user[1]}, Email: {user[2]}")

conn_old.close()
conn_new.close()

print("\n" + "=" * 80)
