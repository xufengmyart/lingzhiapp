#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为 users 表添加 referral_code 和 referral_code_expires_at 字段
"""

import sqlite3
import os
from datetime import datetime, timedelta
import uuid

# 数据库路径
DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/meiyueart-backend/data/lingzhi_ecosystem.db')

def main():
    print("开始添加 referral_code 字段...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 检查字段是否存在
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'referral_code' in columns:
        print("✅ referral_code 字段已存在")
    else:
        print("📝 添加 referral_code 字段...")
        cursor.execute("ALTER TABLE users ADD COLUMN referral_code VARCHAR(20)")
        print("✅ referral_code 字段添加成功")
    
    if 'referral_code_expires_at' in columns:
        print("✅ referral_code_expires_at 字段已存在")
    else:
        print("📝 添加 referral_code_expires_at 字段...")
        cursor.execute("ALTER TABLE users ADD COLUMN referral_code_expires_at DATETIME")
        print("✅ referral_code_expires_at 字段添加成功")
    
    # 为现有用户生成推荐码
    print("📝 为现有用户生成推荐码...")
    cursor.execute("SELECT id FROM users WHERE referral_code IS NULL")
    users = cursor.fetchall()
    
    for user in users:
        user_id = user[0]
        referral_code = uuid.uuid4().hex[:8].upper()
        expires_at = (datetime.now() + timedelta(days=365)).isoformat()
        
        cursor.execute(
            "UPDATE users SET referral_code = ?, referral_code_expires_at = ? WHERE id = ?",
            (referral_code, expires_at, user_id)
        )
    
    conn.commit()
    
    print(f"✅ 已为 {len(users)} 个用户生成推荐码")
    
    # 显示一些示例
    cursor.execute("SELECT username, referral_code FROM users LIMIT 5")
    sample_users = cursor.fetchall()
    print("\n示例用户推荐码：")
    for user in sample_users:
        print(f"  {user[0]}: {user[1]}")
    
    conn.close()
    print("\n完成！")

if __name__ == '__main__':
    main()
