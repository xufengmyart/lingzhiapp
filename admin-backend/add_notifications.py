#!/usr/bin/env python3
"""
添加系统通知功能
"""

import sqlite3
from datetime import datetime

DATABASE = 'lingzhi_ecosystem.db'

def add_notification_tables():
    """添加通知表"""
    print("=" * 80)
    print("添加系统通知表...")
    print("=" * 80)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建系统通知表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            notification_type TEXT DEFAULT 'info',
            is_read BOOLEAN DEFAULT 0,
            target_user_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (target_user_id) REFERENCES users(id)
        )
    ''')
    
    print("  ✅ 系统通知表创建成功")
    
    # 创建用户已读通知记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_read_notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_id INTEGER NOT NULL,
            read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(user_id, notification_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (notification_id) REFERENCES system_notifications(id)
        )
    ''')
    
    print("  ✅ 用户已读通知表创建成功")
    
    conn.commit()
    conn.close()
    
    print("\n通知表添加完成！")

def create_sample_notification():
    """创建示例通知"""
    print("\n" + "=" * 80)
    print("创建系统更新通知...")
    print("=" * 80)
    
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    
    # 创建系统更新通知
    notification = {
        'title': '系统更新通知',
        'content': '''亲爱的用户：

系统已于 2026-02-01 完成重要更新，本次更新包含以下内容：

1. 新增微信登录功能
2. 优化用户注册流程
3. 完善用户信息管理
4. 增强系统安全性

您的账号信息已成功迁移，可以使用原有的登录方式继续使用本系统。
如遇到任何问题，请联系客服。

感谢您的支持！

灵值生态园团队''',
        'notification_type': 'info',
        'target_user_id': None  # 全局通知
    }
    
    cursor.execute(
        '''INSERT INTO system_notifications (title, content, notification_type, target_user_id)
           VALUES (?, ?, ?, ?)''',
        (notification['title'], notification['content'], notification['notification_type'], notification['target_user_id'])
    )
    
    conn.commit()
    conn.close()
    
    print("  ✅ 系统更新通知创建成功")

if __name__ == '__main__':
    add_notification_tables()
    create_sample_notification()
    
    print("\n" + "=" * 80)
    print("系统通知功能添加完成！")
    print("=" * 80)
