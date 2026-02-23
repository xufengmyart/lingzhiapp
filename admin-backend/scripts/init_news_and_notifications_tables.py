#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化新闻和通知系统数据库表
在生产环境运行此脚本以创建缺失的表
"""

import sqlite3
import os
from datetime import datetime

# 数据库路径
DATABASE_PATH = os.getenv('DATABASE_PATH', '/app/meiyueart-backend/data/lingzhi_ecosystem.db')

def init_news_tables():
    """初始化新闻相关表"""
    print("🔧 初始化新闻系统表...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news_articles'")
    if cursor.fetchone():
        print("✅ news_articles 表已存在")
    else:
        print("📝 创建 news_articles 表...")
        cursor.execute('''
            CREATE TABLE news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                slug VARCHAR(255) UNIQUE,
                content TEXT,
                summary TEXT,
                category_id INTEGER,
                author_id INTEGER,
                author_name VARCHAR(100),
                cover_image VARCHAR(500),
                is_featured BOOLEAN DEFAULT 0,
                is_pinned BOOLEAN DEFAULT 0,
                view_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'published',
                tags VARCHAR(500),
                seo_title VARCHAR(255),
                seo_description TEXT,
                seo_keywords VARCHAR(255),
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES news_categories(id)
            )
        ''')
        print("✅ news_articles 表创建成功")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news_categories'")
    if cursor.fetchone():
        print("✅ news_categories 表已存在")
    else:
        print("📝 创建 news_categories 表...")
        cursor.execute('''
            CREATE TABLE news_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                slug VARCHAR(100) UNIQUE,
                description TEXT,
                icon VARCHAR(100),
                sort_order INTEGER DEFAULT 0,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        print("✅ news_categories 表创建成功")
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='news_comments'")
    if cursor.fetchone():
        print("✅ news_comments 表已存在")
    else:
        print("📝 创建 news_comments 表...")
        cursor.execute('''
            CREATE TABLE news_comments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                article_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                user_name VARCHAR(100),
                user_avatar VARCHAR(500),
                content TEXT NOT NULL,
                parent_id INTEGER,
                like_count INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'approved',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (article_id) REFERENCES news_articles(id) ON DELETE CASCADE,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("✅ news_comments 表创建成功")
    
    # 插入默认分类
    cursor.execute("SELECT COUNT(*) FROM news_categories")
    if cursor.fetchone()[0] == 0:
        print("📝 插入默认分类...")
        categories = [
            ('平台信息', 'announcements', '平台公告、系统更新和重要通知', 'megaphone', 1),
            ('功能更新', 'updates', '新功能和改进', 'zap', 2),
            ('使用教程', 'tutorials', '使用指南和教程', 'book', 3),
            ('活动资讯', 'events', '活动和促销信息', 'calendar', 4),
            ('常见问题', 'faq', '常见问题和解答', 'help-circle', 5)
        ]
        cursor.executemany('''
            INSERT INTO news_categories (name, slug, description, icon, sort_order)
            VALUES (?, ?, ?, ?, ?)
        ''', categories)
        print("✅ 默认分类插入成功")
    
    # 插入示例文章
    cursor.execute("SELECT COUNT(*) FROM news_articles")
    if cursor.fetchone()[0] == 0:
        print("📝 插入示例文章...")
        articles = [
            (
                '欢迎使用灵值生态园智能体系统',
                'welcome-to-lingzhi-ecosystem',
                '<h2>欢迎使用灵值生态园智能体系统</h2>\n<p>这是一个功能强大的智能体生态系统，为您提供全方位的服务。</p>\n<h3>主要功能</h3>\n<ul>\n<li>智能对话</li>\n<li>知识管理</li>\n<li>数据分析</li>\n<li>经济模型</li>\n</ul>',
                '欢迎使用灵值生态园智能体系统，这是一个功能强大的智能体生态系统。',
                1,
                '系统管理员',
                1,
                'published',
                datetime.now()
            ),
            (
                '灵值生态园功能更新 - v2.0',
                'lingzhi-ecosystem-update-v2',
                '<h2>🎉 灵值生态园 v2.0 版本发布</h2>\n<p>我们很高兴地宣布灵值生态园 v2.0 版本正式上线！</p>\n<h3>✨ 新增功能</h3>\n<ul>\n<li>新增智能体市场，您可以发布和使用各种智能体</li>\n<li>优化了用户界面，提供更好的用户体验</li>\n<li>新增灵值经济系统，支持贡献奖励</li>\n<li>增强的社交功能，方便用户交流和协作</li>\n</ul>\n<h3>🔧 改进内容</h3>\n<ul>\n<li>性能优化，响应速度提升 50%</li>\n<li>修复了多个已知问题</li>\n<li>增强了安全性和稳定性</li>\n</ul>',
                '灵值生态园 v2.0 版本正式上线，带来更多新功能和改进！',
                2,
                '开发团队',
                1,
                'published',
                datetime.now()
            ),
            (
                '如何快速开始使用灵值生态园',
                'how-to-start-lingzhi-ecosystem',
                '<h2>📚 如何快速开始使用灵值生态园</h2>\n<p>本文将帮助您快速上手灵值生态园智能体系统。</p>\n<h3>步骤 1：注册账号</h3>\n<p>点击页面右上角的"注册"按钮，填写必要信息完成注册。</p>\n<h3>步骤 2：完善个人信息</h3>\n<p>登录后，进入"个人中心"完善您的个人信息。</p>\n<h3>步骤 3：探索功能</h3>\n<p>您可以开始探索以下功能：</p>\n<ul>\n<li>智能对话：与 AI 智能体进行对话</li>\n<li>知识库：管理和分享您的知识</li>\n<li>项目协作：与他人协作完成项目</li>\n</ul>\n<h3>步骤 4：获取灵值</h3>\n<p>通过签到、完成任务、贡献内容等方式获取灵值奖励。</p>',
                '快速上手灵值生态园智能体系统，只需简单几步即可开始使用。',
                3,
                '客服团队',
                0,
                'published',
                datetime.now()
            ),
            (
                '灵值生态园用户福利活动',
                'lingzhi-ecosystem-promotion',
                '<h2>🎁 灵值生态园用户福利活动</h2>\n<p>为了感谢广大用户的支持，我们特别推出以下福利活动！</p>\n<h3>🔥 活动内容</h3>\n<ul>\n<li><strong>连续签到奖励</strong>：连续签到 7 天可获得 100 灵值</li>\n<li><strong>新用户专享</strong>：注册即送 50 灵值</li>\n<li><strong>邀请好友</strong>：每邀请一位好友注册，双方各得 30 灵值</li>\n<li><strong>内容贡献</strong>：发布优质内容可获得灵值奖励</li>\n</ul>\n<h3>📅 活动时间</h3>\n<p>即日起至 2026 年 12 月 31 日</p>\n<h3>📜 活动规则</h3>\n<p>每人只能参与一次新用户专享活动，邀请好友无上限。灵值可用于兑换平台内各种服务。</p>',
                '灵值生态园用户福利活动，签到、邀请好友、贡献内容均可获得灵值奖励！',
                4,
                '运营团队',
                1,
                'published',
                datetime.now()
            ),
            (
                '常见问题解答 - 灵值生态园',
                'faq-lingzhi-ecosystem',
                '<h2>❓ 常见问题解答</h2>\n<h3>Q1：灵值是什么？</h3>\n<p>A：灵值是灵值生态园的积分系统，您可以通过签到、完成任务、贡献内容等方式获得灵值，灵值可用于兑换平台内各种服务。</p>\n<h3>Q2：如何获取灵值？</h3>\n<p>A：您可以通过以下方式获取灵值：</p>\n<ul>\n<li>每日签到</li>\n<li>完成任务</li>\n<li>贡献内容</li>\n<li>邀请好友</li>\n</ul>\n<h3>Q3：如何联系客服？</h3>\n<p>A：您可以通过页面底部的"联系我们"联系客服，或发送邮件至 support@meiyueart.com。</p>\n<h3>Q4：如何修改密码？</h3>\n<p>A：登录后，进入"个人中心" > "账户安全" > "修改密码"即可修改密码。</p>',
                '灵值生态园常见问题解答，帮助您快速解决使用中的问题。',
                5,
                '客服团队',
                0,
                'published',
                datetime.now()
            )
        ]
        cursor.executemany('''
            INSERT INTO news_articles (title, slug, content, summary, category_id, author_name, is_pinned, status, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', articles)
        print("✅ 示例文章插入成功")
    else:
        # 检查是否需要补充文章（少于5篇）
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        if cursor.fetchone()[0] < 5:
            print("📝 补充文章...")
            # 只插入除第一篇外的其他文章
            articles = [
                (
                    '灵值生态园功能更新 - v2.0',
                    'lingzhi-ecosystem-update-v2',
                    '<h2>🎉 灵值生态园 v2.0 版本发布</h2><p>我们很高兴地宣布灵值生态园 v2.0 版本正式上线！</p><h3>✨ 新增功能</h3><ul><li>新增智能体市场，您可以发布和使用各种智能体</li><li>优化了用户界面，提供更好的用户体验</li><li>新增灵值经济系统，支持贡献奖励</li><li>增强的社交功能，方便用户交流和协作</li></ul><h3>🔧 改进内容</h3><ul><li>性能优化，响应速度提升 50%</li><li>修复了多个已知问题</li><li>增强了安全性和稳定性</li></ul>',
                    '灵值生态园 v2.0 版本正式上线，带来更多新功能和改进！',
                    2,
                    '开发团队',
                    1,
                    'published',
                    datetime.now()
                ),
                (
                    '如何快速开始使用灵值生态园',
                    'how-to-start-lingzhi-ecosystem',
                    '<h2>📚 如何快速开始使用灵值生态园</h2><p>本文将帮助您快速上手灵值生态园智能体系统。</p><h3>步骤 1：注册账号</h3><p>点击页面右上角的"注册"按钮，填写必要信息完成注册。</p><h3>步骤 2：完善个人信息</h3><p>登录后，进入"个人中心"完善您的个人信息。</p><h3>步骤 3：探索功能</h3><p>您可以开始探索以下功能：</p><ul><li>智能对话：与 AI 智能体进行对话</li><li>知识库：管理和分享您的知识</li><li>项目协作：与他人协作完成项目</li></ul><h3>步骤 4：获取灵值</h3><p>通过签到、完成任务、贡献内容等方式获取灵值奖励。</p>',
                    '快速上手灵值生态园智能体系统，只需简单几步即可开始使用。',
                    3,
                    '客服团队',
                    0,
                    'published',
                    datetime.now()
                ),
                (
                    '灵值生态园用户福利活动',
                    'lingzhi-ecosystem-promotion',
                    '<h2>🎁 灵值生态园用户福利活动</h2><p>为了感谢广大用户的支持，我们特别推出以下福利活动！</p><h3>🔥 活动内容</h3><ul><li><strong>连续签到奖励</strong>：连续签到 7 天可获得 100 灵值</li><li><strong>新用户专享</strong>：注册即送 50 灵值</li><li><strong>邀请好友</strong>：每邀请一位好友注册，双方各得 30 灵值</li><li><strong>内容贡献</strong>：发布优质内容可获得灵值奖励</li></ul><h3>📅 活动时间</h3><p>即日起至 2026 年 12 月 31 日</p><h3>📜 活动规则</h3><p>每人只能参与一次新用户专享活动，邀请好友无上限。灵值可用于兑换平台内各种服务。</p>',
                    '灵值生态园用户福利活动，签到、邀请好友、贡献内容均可获得灵值奖励！',
                    4,
                    '运营团队',
                    1,
                    'published',
                    datetime.now()
                ),
                (
                    '常见问题解答 - 灵值生态园',
                    'faq-lingzhi-ecosystem',
                    '<h2>❓ 常见问题解答</h2><h3>Q1：灵值是什么？</h3><p>A：灵值是灵值生态园的积分系统，您可以通过签到、完成任务、贡献内容等方式获得灵值，灵值可用于兑换平台内各种服务。</p><h3>Q2：如何获取灵值？</h3><p>A：您可以通过以下方式获取灵值：</p><ul><li>每日签到</li><li>完成任务</li><li>贡献内容</li><li>邀请好友</li></ul><h3>Q3：如何联系客服？</h3><p>A：您可以通过页面底部的"联系我们"联系客服，或发送邮件至 support@meiyueart.com。</p><h3>Q4：如何修改密码？</h3><p>A：登录后，进入"个人中心" > "账户安全" > "修改密码"即可修改密码。</p>',
                    '灵值生态园常见问题解答，帮助您快速解决使用中的问题。',
                    5,
                    '客服团队',
                    0,
                    'published',
                    datetime.now()
                )
            ]
            for article in articles:
                try:
                    cursor.execute('''
                        INSERT INTO news_articles (title, slug, content, summary, category_id, author_name, is_pinned, status, published_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', article)
                except sqlite3.IntegrityError:
                    # 如果文章已存在，跳过
                    pass
            print("✅ 文章补充成功")
    
    conn.commit()
    conn.close()
    print("✅ 新闻系统表初始化完成")

def init_notifications_tables():
    """初始化通知相关表"""
    print("\n🔧 初始化通知系统表...")
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user_notifications'")
    if cursor.fetchone():
        print("✅ user_notifications 表已存在")
    else:
        print("📝 创建 user_notifications 表...")
        cursor.execute('''
            CREATE TABLE user_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT,
                type VARCHAR(50),
                is_read BOOLEAN DEFAULT 0,
                link VARCHAR(500),
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        print("✅ user_notifications 表创建成功")
    
    # 为所有现有用户创建欢迎通知
    cursor.execute("SELECT id FROM users LIMIT 1")
    if cursor.fetchone():
        print("📝 创建用户欢迎通知...")
        # 欢迎通知
        cursor.execute('''
            INSERT OR IGNORE INTO user_notifications (user_id, title, content, type, is_read, created_at)
            SELECT id, '欢迎来到灵值生态园', '感谢您加入灵值生态园智能体系统！在这里，您可以体验智能对话、知识管理、项目协作等功能。', 'welcome', 0, CURRENT_TIMESTAMP
            FROM users
        ''')
        # 系统更新通知
        cursor.execute('''
            INSERT OR IGNORE INTO user_notifications (user_id, title, content, type, is_read, created_at)
            SELECT id, '🎉 新版本上线通知', '灵值生态园 v2.0 版本已上线！新增智能体市场、灵值经济系统等功能，快来体验吧！', 'system', 0, CURRENT_TIMESTAMP
            FROM users
        ''')
        # 签到提醒通知
        cursor.execute('''
            INSERT OR IGNORE INTO user_notifications (user_id, title, content, type, is_read, created_at)
            SELECT id, '💰 每日签到提醒', '记得每日签到获取灵值奖励哦！连续签到还有额外奖励！', 'checkin', 0, CURRENT_TIMESTAMP
            FROM users
        ''')
        # 活动通知
        cursor.execute('''
            INSERT OR IGNORE INTO user_notifications (user_id, title, content, type, is_read, created_at)
            SELECT id, '🎁 用户福利活动', '限时福利活动火热进行中！签到、邀请好友、贡献内容均可获得灵值奖励！', 'activity', 0, CURRENT_TIMESTAMP
            FROM users
        ''')
        print("✅ 用户欢迎通知创建成功")
    
    conn.commit()
    conn.close()
    print("✅ 通知系统表初始化完成")

def main():
    """主函数"""
    print("=" * 60)
    print("初始化新闻和通知系统数据库表")
    print("=" * 60)
    print(f"数据库路径: {DATABASE_PATH}")
    print()
    
    try:
        init_news_tables()
        init_notifications_tables()
        
        print("\n" + "=" * 60)
        print("✅ 所有表初始化完成")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
