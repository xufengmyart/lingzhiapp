#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建 share_stats 表
"""

import sqlite3
import os

def create_share_stats_table():
    """创建分享统计表"""
    db_path = os.getenv('DATABASE_PATH', 'data/lingzhi_ecosystem.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 创建分享统计表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS share_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            article_id INTEGER NOT NULL,
            share_type TEXT NOT NULL,
            share_url TEXT NOT NULL,
            referral_code TEXT UNIQUE,
            platform TEXT NOT NULL,
            share_count INTEGER DEFAULT 1,
            click_count INTEGER DEFAULT 0,
            registration_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (article_id) REFERENCES news_articles(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_user_id ON share_stats(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_article_id ON share_stats(article_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_referral_code ON share_stats(referral_code)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_user_time ON share_stats(user_id, created_at DESC)')
    
    conn.commit()
    conn.close()
    
    print("✅ share_stats 表创建成功")

if __name__ == '__main__':
    create_share_stats_table()
