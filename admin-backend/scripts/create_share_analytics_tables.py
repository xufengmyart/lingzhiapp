#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分享系统数据库表创建脚本
"""

import sqlite3
import os

def create_share_clicks_table():
    """创建分享点击记录表"""
    db_path = os.getenv('DATABASE_PATH', 'data/lingzhi_ecosystem.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建分享点击记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS share_clicks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referral_code TEXT NOT NULL,
            article_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            clicked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referral_code) REFERENCES share_stats(referral_code),
            FOREIGN KEY (article_id) REFERENCES news_articles(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_clicks_referral_code ON share_clicks(referral_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_clicks_clicked_at ON share_clicks(clicked_at)')
    
    print("✅ share_clicks 表创建成功")
    
    conn.commit()
    conn.close()

def create_reward_logs_table():
    """创建奖励日志表"""
    db_path = os.getenv('DATABASE_PATH', 'data/lingzhi_ecosystem.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建奖励日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reward_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referee_id INTEGER NOT NULL,
            reward_type TEXT NOT NULL,
            amount INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reason TEXT,
            FOREIGN KEY (referrer_id) REFERENCES users(id),
            FOREIGN KEY (referee_id) REFERENCES users(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reward_logs_referrer_id ON reward_logs(referrer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reward_logs_created_at ON reward_logs(created_at)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reward_logs_reward_type ON reward_logs(reward_type)')
    
    print("✅ reward_logs 表创建成功")
    
    conn.commit()
    conn.close()

def update_users_table():
    """更新用户表，添加积分字段"""
    db_path = os.getenv('DATABASE_PATH', 'data/lingzhi_ecosystem.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查并添加字段
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if 'points' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN points INTEGER DEFAULT 0')
        print("✅ users 表添加 points 字段")
    
    if 'referrer_id' not in columns:
        cursor.execute('ALTER TABLE users ADD COLUMN referrer_id INTEGER')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_referrer_id ON users(referrer_id)')
        print("✅ users 表添加 referrer_id 字段")
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    print("开始创建分享系统数据库表...")
    
    create_share_clicks_table()
    create_reward_logs_table()
    update_users_table()
    
    print("\n🎉 所有数据库表创建完成！")
