#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化管理员账号
"""

import sqlite3
import bcrypt
import sys
import os

# 添加项目路径
sys.path.append(os.path.dirname(__file__))
from config import config

def hash_password(password):
    """哈希密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def init_admin(max_retries=5, retry_delay=2):
    """初始化管理员账号"""
    print("开始初始化管理员账号...")

    import time

    for attempt in range(max_retries):
        conn = None
        try:
            # 尝试连接数据库
            print(f"[INIT_ADMIN] 尝试连接数据库 (第{attempt + 1}次/{max_retries})...")
            conn = sqlite3.connect(config.DATABASE_PATH, timeout=30)
            cursor = conn.cursor()

            # 确保admins表存在
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT DEFAULT 'admin',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # 确保users表存在
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                phone TEXT,
                password_hash TEXT NOT NULL,
                total_lingzhi INTEGER DEFAULT 100,
                status TEXT DEFAULT 'active',
                last_login_at TIMESTAMP,
                avatar_url TEXT,
                real_name TEXT,
                is_verified BOOLEAN DEFAULT 0,
                login_type TEXT DEFAULT 'phone',
                wechat_openid TEXT,
                wechat_unionid TEXT,
                wechat_nickname TEXT,
                wechat_avatar TEXT,
                referrer_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')

            # 检查是否已存在admin用户
            cursor.execute("SELECT id, username FROM admins WHERE username = ?", ('admin',))
            existing_admin = cursor.fetchone()

            if existing_admin:
                print(f"管理员账号已存在: {existing_admin[1]} (ID: {existing_admin[0]})")
                # 更新密码
                new_password = "123"
                new_hash = hash_password(new_password)
                cursor.execute(
                    "UPDATE admins SET password_hash = ? WHERE username = ?",
                    (new_hash, 'admin')
                )
                print(f"密码已重置为: {new_password}")
            else:
                # 创建管理员账号
                username = "admin"
                password = "123"
                role = "super_admin"
                password_hash = hash_password(password)

                cursor.execute(
                    "INSERT INTO admins (username, password_hash, role) VALUES (?, ?, ?)",
                    (username, password_hash, role)
                )
                print(f"管理员账号创建成功!")
                print(f"  用户名: {username}")
                print(f"  密码: {password}")
                print(f"  角色: {role}")

            conn.commit()

            # 同时在users表中创建admin账号（用于登录）
            cursor.execute("SELECT id, username FROM users WHERE username = ?", ('admin',))
            existing_user = cursor.fetchone()

            if not existing_user:
                password_hash = hash_password("123")
                cursor.execute(
                    """
                    INSERT INTO users (username, password_hash, total_lingzhi, status, login_type)
                    VALUES ('admin', ?, 0, 'active', 'phone')
                    """,
                    (password_hash,)
                )
                print("✅ 用户表中admin账号已创建")
            else:
                # 更新密码
                new_hash = hash_password("123")
                cursor.execute(
                    "UPDATE users SET password_hash = ? WHERE username = ?",
                    (new_hash, 'admin')
                )
                print("✅ 用户表中admin密码已重置")

            conn.commit()
            conn.close()
            conn = None

            print("管理员账号初始化完成!")
            return  # 成功，退出函数

        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"[INIT_ADMIN] 数据库锁定: {e}")
                if attempt < max_retries - 1:
                    print(f"[INIT_ADMIN] 等待 {retry_delay} 秒后重试...")
                    time.sleep(retry_delay)
                else:
                    print(f"[INIT_ADMIN] 重试 {max_retries} 次后仍失败")
                    raise
            else:
                raise
        except Exception as e:
            print(f"[INIT_ADMIN] 初始化失败: {e}")
            import traceback
            traceback.print_exc()
            raise
        finally:
            if conn:
                try:
                    conn.close()
                except Exception as e:
                    print(f"[INIT_ADMIN] 关闭连接时出错: {e}")

if __name__ == '__main__':
    init_admin()
