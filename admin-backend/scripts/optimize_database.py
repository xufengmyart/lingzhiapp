#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库索引优化脚本
为关键表创建索引以提升查询性能
"""

import sqlite3
import os

def optimize_database():
    """优化数据库索引"""
    db_path = os.getenv('DATABASE_PATH', 'data/lingzhi_ecosystem.db')
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("🚀 开始优化数据库索引...")
    
    # ==================== users 表优化 ====================
    print("\n📊 优化 users 表...")
    
    # 登录查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)')
        print("  ✅ idx_users_username - 用于登录查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 推荐关系查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_referrer_id ON users(referrer_id)')
        print("  ✅ idx_users_referrer_id - 用于推荐关系查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # Token查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_token ON users(token)')
        print("  ✅ idx_users_token - 用于Token查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # ==================== news_articles 表优化 ====================
    print("\n📊 优化 news_articles 表...")
    
    # 文章列表查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_articles_status ON news_articles(status)')
        print("  ✅ idx_news_articles_status - 用于文章状态筛选")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 分类查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_articles_category ON news_articles(category_id)')
        print("  ✅ idx_news_articles_category - 用于分类查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 作者查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_articles_author ON news_articles(author_id)')
        print("  ✅ idx_news_articles_author - 用于作者查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 时间排序优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_news_articles_created ON news_articles(created_at)')
        print("  ✅ idx_news_articles_created - 用于时间排序")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 复合索引：状态 + 创建时间
    try:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_news_articles_status_created 
            ON news_articles(status, created_at DESC)
        ''')
        print("  ✅ idx_news_articles_status_created - 复合索引")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # ==================== notifications 表优化 ====================
    print("\n📊 优化 notifications 表...")
    
    # 用户通知查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)')
        print("  ✅ idx_notifications_user - 用于用户通知查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 未读通知查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)')
        print("  ✅ idx_notifications_read - 用于未读通知查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 复合索引：用户 + 读取状态 + 时间
    try:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_notifications_user_read 
            ON notifications(user_id, is_read, created_at DESC)
        ''')
        print("  ✅ idx_notifications_user_read - 复合索引")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # ==================== share_stats 表优化 ====================
    print("\n📊 优化 share_stats 表...")
    
    # 用户分享查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_user ON share_stats(user_id)')
        print("  ✅ idx_share_stats_user - 用于用户分享查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 推荐码查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_code ON share_stats(referral_code)')
        print("  ✅ idx_share_stats_code - 用于推荐码查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 复合索引：用户 + 时间
    try:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_share_stats_user_time 
            ON share_stats(user_id, created_at DESC)
        ''')
        print("  ✅ idx_share_stats_user_time - 复合索引")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # ==================== share_clicks 表优化 ====================
    print("\n📊 优化 share_clicks 表...")
    
    # 点击时间查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_clicks_time ON share_clicks(clicked_at)')
        print("  ✅ idx_share_clicks_time - 用于时间范围查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # ==================== reward_logs 表优化 ====================
    print("\n📊 优化 reward_logs 表...")
    
    # 推荐人查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reward_logs_referrer ON reward_logs(referrer_id)')
        print("  ✅ idx_reward_logs_referrer - 用于推荐人查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 时间查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_reward_logs_time ON reward_logs(created_at)')
        print("  ✅ idx_reward_logs_time - 用于时间范围查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 复合索引：推荐人 + 时间
    try:
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_reward_logs_referrer_time 
            ON reward_logs(referrer_id, created_at DESC)
        ''')
        print("  ✅ idx_reward_logs_referrer_time - 复合索引")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # ==================== 充值记录表优化 ====================
    print("\n📊 优化 recharge_records 表...")
    
    # 用户充值查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recharge_user ON recharge_records(user_id)')
        print("  ✅ idx_recharge_user - 用于用户充值查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 订单号查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_recharge_order ON recharge_records(order_id)')
        print("  ✅ idx_recharge_order - 用于订单号查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # ==================== 对话记录表优化 ====================
    print("\n📊 优化 conversation_history 表...")
    
    # 用户对话查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_user ON conversation_history(user_id)')
        print("  ✅ idx_conversation_user - 用于用户对话查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # 会话查询优化
    try:
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_conversation_session ON conversation_history(session_id)')
        print("  ✅ idx_conversation_session - 用于会话查询")
    except Exception as e:
        print(f"  ❌ 创建索引失败: {e}")
    
    # ==================== 分析统计信息 ====================
    print("\n📈 分析表统计信息...")
    
    tables = ['users', 'news_articles', 'notifications', 'share_stats', 
              'share_clicks', 'reward_logs', 'recharge_records', 'conversation_history']
    
    for table in tables:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  📋 {table}: {count} 条记录")
        except Exception as e:
            print(f"  ❌ 无法统计 {table}: {e}")
    
    # 提交事务
    conn.commit()
    
    # 清理数据库
    cursor.execute("VACUUM")
    print("\n✅ 数据库已清理")
    
    # 分析数据库（优化查询计划）
    cursor.execute("ANALYZE")
    print("✅ 查询计划已优化")
    
    conn.close()
    
    print("\n🎉 数据库优化完成！")
    print("\n💡 提示：")
    print("  - 已为关键表创建索引")
    print("  - 已清理数据库碎片")
    print("  - 已优化查询计划")
    print("  - 建议定期运行此脚本以保持最佳性能")

if __name__ == '__main__':
    optimize_database()
