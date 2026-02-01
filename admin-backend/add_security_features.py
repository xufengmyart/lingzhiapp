#!/usr/bin/env python3
"""
添加设备管理和单点登录功能的数据库迁移脚本
"""

import sqlite3
import os

DATABASE = 'lingzhi_ecosystem.db'

def migrate():
    """执行数据库迁移"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    print("=" * 80)
    print("添加设备管理和单点登录功能")
    print("=" * 80)

    # 1. 添加设备管理表
    print("\n[1/5] 创建设备管理表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            device_id TEXT NOT NULL,
            device_name TEXT,
            device_type TEXT,
            user_agent TEXT,
            ip_address TEXT,
            location TEXT,
            is_current BOOLEAN DEFAULT 0,
            last_active_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, device_id)
        )
    ''')
    print("✅ 设备管理表创建成功")

    # 2. 添加登录会话表
    print("\n[2/5] 创建登录会话表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS login_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT NOT NULL UNIQUE,
            device_id TEXT,
            ip_address TEXT,
            user_agent TEXT,
            expires_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ 登录会话表创建成功")

    # 3. 为 users 表添加安全设置字段
    print("\n[3/5] 添加用户安全设置字段...")
    try:
        cursor.execute("ALTER TABLE users ADD COLUMN require_phone_verification BOOLEAN DEFAULT 1")
        print("✅ 手机验证要求字段添加成功")
    except:
        print("⚠️  手机验证要求字段已存在")

    try:
        cursor.execute("ALTER TABLE users ADD COLUMN single_login_enabled BOOLEAN DEFAULT 1")
        print("✅ 单点登录设置字段添加成功")
    except:
        print("⚠️  单点登录设置字段已存在")

    # 4. 创建安全日志表
    print("\n[4/5] 创建安全日志表...")
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS security_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            event_type TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            details TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("✅ 安全日志表创建成功")

    # 5. 创建索引
    print("\n[5/5] 创建索引...")
    try:
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_devices_user_id ON user_devices(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_sessions_user_id ON login_sessions(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_login_sessions_token ON login_sessions(token)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_security_logs_user_id ON security_logs(user_id)")
        print("✅ 索引创建成功")
    except Exception as e:
        print(f"⚠️  索引创建警告: {e}")

    conn.commit()
    conn.close()

    print("\n==========================================")
    print("✅ 数据库迁移完成！")
    print("==========================================")

if __name__ == '__main__':
    # 切换到数据库目录
    os.chdir('/workspace/projects/admin-backend')
    migrate()
