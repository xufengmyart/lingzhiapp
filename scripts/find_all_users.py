#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

# 所有数据库文件
db_files = [
    '/workspace/projects/lingzhi_ecosystem.db',
    '/workspace/projects/admin-backend/lingzhi_ecosystem.db',
    '/workspace/projects/admin-backend/lingzhi_garden.db',
]

# 备份目录
backup_dir = '/workspace/projects/admin-backend/backups'

# 收集所有数据库文件
if os.path.exists(backup_dir):
    for filename in os.listdir(backup_dir):
        if filename.endswith('.db'):
            db_files.append(os.path.join(backup_dir, filename))

print("=" * 70)
print("检查所有数据库文件中的用户")
print("=" * 70)
print()

all_users = {}

for db_path in db_files:
    if not os.path.exists(db_path):
        continue
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查是否有 users 表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        if not cursor.fetchone():
            conn.close()
            continue
        
        # 查询用户数量
        cursor.execute('SELECT COUNT(*) FROM users')
        user_count = cursor.fetchone()[0]
        
        if user_count > 0:
            print(f"📁 {db_path}")
            print(f"   用户数量: {user_count}")
            
            # 查询所有用户
            cursor.execute('''
                SELECT id, username, phone, email, status, created_at
                FROM users
                ORDER BY id
            ''')
            users = cursor.fetchall()
            
            print(f"{'ID':<6} {'用户名':<20} {'手机号':<15} {'邮箱':<30} {'状态':<10}")
            print("-" * 80)
            for user in users:
                print(f"{user[0]:<6} {user[1]:<20} {str(user[2]):<15} {str(user[3]):<30} {user[4]:<10}")
            
            print()
            
            # 收集用户
            db_name = os.path.basename(db_path)
            all_users[db_name] = users
        
        conn.close()
        
    except Exception as e:
        print(f"❌ {db_path}: {e}")
        print()

print("=" * 70)
print("汇总")
print("=" * 70)

# 找出用户最多的数据库
max_users = 0
max_db = None
for db_name, users in all_users.items():
    if len(users) > max_users:
        max_users = len(users)
        max_db = db_name

if max_db:
    print(f"用户最多的数据库: {max_db} ({max_users} 个用户)")
    print()

# 去重所有用户
unique_users = {}
for db_name, users in all_users.items():
    for user in users:
        user_id = user[0]
        username = user[1]
        key = f"{user_id}_{username}"
        if key not in unique_users:
            unique_users[key] = {
                'id': user[0],
                'username': user[1],
                'phone': user[2],
                'email': user[3],
                'status': user[4],
                'db': db_name
            }

print(f"去重后的用户总数: {len(unique_users)}")
print()

if unique_users:
    print(f"{'ID':<6} {'用户名':<20} {'手机号':<15} {'邮箱':<30} {'状态':<10} {'来源数据库':<40}")
    print("-" * 130)
    for user in sorted(unique_users.values(), key=lambda x: x['id']):
        print(f"{user['id']:<6} {user['username']:<20} {str(user['phone']):<15} {str(user['email']):<30} {user['status']:<10} {user['db']:<40}")
