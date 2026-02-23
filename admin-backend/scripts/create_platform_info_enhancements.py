#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建平台信息增强功能表
包括：阅读记录、订阅记录、评论记录
"""

import sqlite3
import os

def create_enhancement_tables():
    """创建平台信息增强功能表"""
    db_path = os.getenv('DATABASE_PATH', 'data/lingzhi_ecosystem.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🔨 创建平台信息增强功能表...")
    
    # 1. 创建阅读记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_info_reads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform_info_id INTEGER NOT NULL,
            read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (platform_info_id) REFERENCES news_articles(id),
            UNIQUE(user_id, platform_info_id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reads_user ON platform_info_reads(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reads_info ON platform_info_reads(platform_info_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_reads_user_info ON platform_info_reads(user_id, platform_info_id)')
    
    print("✅ platform_info_reads 表创建成功")
    
    # 2. 创建订阅记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_info_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            info_type TEXT NOT NULL,
            importance_level INTEGER,
            subscribed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, info_type)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_user ON platform_info_subscriptions(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_type ON platform_info_subscriptions(info_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_subscriptions_active ON platform_info_subscriptions(is_active)')
    
    print("✅ platform_info_subscriptions 表创建成功")
    
    # 3. 创建评论记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_info_comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_info_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            parent_id INTEGER,
            like_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            is_deleted BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (platform_info_id) REFERENCES news_articles(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (parent_id) REFERENCES platform_info_comments(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_info ON platform_info_comments(platform_info_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_user ON platform_info_comments(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_parent ON platform_info_comments(parent_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_comments_created ON platform_info_comments(created_at DESC)')
    
    print("✅ platform_info_comments 表创建成功")
    
    # 4. 创建推送消息表（用于记录推送历史）
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_info_pushes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_info_id INTEGER NOT NULL,
            push_type TEXT NOT NULL,
            target_type TEXT NOT NULL,
            target_ids TEXT,
            title TEXT,
            content TEXT,
            status TEXT DEFAULT 'pending',
            sent_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (platform_info_id) REFERENCES news_articles(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pushes_info ON platform_info_pushes(platform_info_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pushes_status ON platform_info_pushes(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_pushes_created ON platform_info_pushes(created_at DESC)')
    
    print("✅ platform_info_pushes 表创建成功")
    
    # 5. 创建点赞记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_info_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            platform_info_id INTEGER NOT NULL,
            liked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (platform_info_id) REFERENCES news_articles(id),
            UNIQUE(user_id, platform_info_id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_likes_user ON platform_info_likes(user_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_likes_info ON platform_info_likes(platform_info_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_likes_user_info ON platform_info_likes(user_id, platform_info_id)')
    
    print("✅ platform_info_likes 表创建成功")
    
    # 6. 创建分享记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS platform_info_shares (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            platform_info_id INTEGER NOT NULL,
            platform TEXT NOT NULL,
            share_url TEXT,
            referral_code TEXT,
            share_count INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (platform_info_id) REFERENCES news_articles(id)
        )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_shares_info ON platform_info_shares(platform_info_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_shares_referral_code ON platform_info_shares(referral_code)')
    
    print("✅ platform_info_shares 表创建成功")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 所有增强功能表创建完成！")
    print("\n📋 创建的表：")
    print("  1. platform_info_reads - 阅读记录")
    print("  2. platform_info_subscriptions - 订阅记录")
    print("  3. platform_info_comments - 评论记录")
    print("  4. platform_info_pushes - 推送记录")
    print("  5. platform_info_likes - 点赞记录")
    print("  6. platform_info_shares - 分享记录")

if __name__ == '__main__':
    create_enhancement_tables()
