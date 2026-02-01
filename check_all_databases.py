#!/usr/bin/env python3
import sqlite3
import os

# 旧数据库路径
OLD_DATABASE = './灵值生态园智能体移植包/src/auth/auth.db'

if os.path.exists(OLD_DATABASE):
    print(f"检查旧数据库: {OLD_DATABASE}")
    print("=" * 80)
    
    conn = sqlite3.connect(OLD_DATABASE)
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"数据库中的表: {[t[0] for t in tables]}")
    
    # 检查 users 表
    if any('users' in t for t in tables):
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"users 表中的用户数量: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, name, email, phone, SUBSTR(password_hash, 1, 10) as prefix FROM users LIMIT 10")
            users = cursor.fetchall()
            print("\n旧数据库中的用户示例：")
            print(f"{'ID':<5} {'用户名':<20} {'邮箱':<30} {'密码前缀':<15}")
            print("-" * 80)
            for user in users:
                user_id, name, email, phone, prefix = user
                print(f"{user_id:<5} {name:<20} {email:<30} {prefix:<15}")
    
    conn.close()
else:
    print(f"旧数据库不存在: {OLD_DATABASE}")

# 检查新数据库
NEW_DATABASE = './admin-backend/lingzhi_ecosystem.db'

if os.path.exists(NEW_DATABASE):
    print(f"\n检查新数据库: {NEW_DATABASE}")
    print("=" * 80)
    
    conn = sqlite3.connect(NEW_DATABASE)
    cursor = conn.cursor()
    
    # 检查表结构
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"数据库中的表: {[t[0] for t in tables]}")
    
    # 检查 users 表
    if any('users' in t for t in tables):
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        print(f"users 表中的用户数量: {user_count}")
        
        if user_count > 0:
            cursor.execute("SELECT id, username, email, phone, SUBSTR(password_hash, 1, 10) as prefix FROM users LIMIT 10")
            users = cursor.fetchall()
            print("\n新数据库中的用户示例：")
            print(f"{'ID':<5} {'用户名':<20} {'邮箱':<30} {'密码前缀':<15}")
            print("-" * 80)
            for user in users:
                user_id, username, email, phone, prefix = user
                print(f"{user_id:<5} {username:<20} {email:<30} {prefix:<15}")
    
    conn.close()
else:
    print(f"新数据库不存在: {NEW_DATABASE}")
