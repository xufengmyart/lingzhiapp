#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵值生态园 - 新闻数据表初始化脚本
News Database Initialization Script

Author: Coze Coding
Version: 1.0.0
Date: 2026-02-21
"""

import os
import sys
from datetime import datetime
import logging

# 添加项目路径到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

from database import get_db

def init_news_tables():
    """初始化新闻相关数据表"""
    logger.info("开始初始化新闻数据表...")

    try:
        conn = get_db()
        cursor = conn.cursor()

        # 1. 创建新闻分类表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                slug VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                icon VARCHAR(100),
                sort_order INTEGER DEFAULT 0,
                status VARCHAR(20) DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ 新闻分类表创建成功")

        # 2. 创建新闻文章表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(255) NOT NULL,
                slug VARCHAR(255) NOT NULL UNIQUE,
                content TEXT NOT NULL,
                summary TEXT,
                category_id INTEGER,
                author_id INTEGER DEFAULT 1,
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
        """)
        logger.info("✅ 新闻文章表创建成功")

        # 3. 创建用户通知表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                title VARCHAR(255) NOT NULL,
                content TEXT,
                type VARCHAR(50) DEFAULT 'system',
                is_read BOOLEAN DEFAULT 0,
                link VARCHAR(500),
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                read_at TIMESTAMP
            )
        """)
        logger.info("✅ 用户通知表创建成功")

        # 4. 创建系统新闻日志表（记录升级新闻）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_news_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                version VARCHAR(50) NOT NULL,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                category VARCHAR(50) DEFAULT 'update',
                is_published BOOLEAN DEFAULT 0,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        logger.info("✅ 系统新闻日志表创建成功")

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_articles_category ON news_articles(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_articles_status ON news_articles(status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_articles_published ON news_articles(published_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_notifications_user ON user_notifications(user_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_notifications_read ON user_notifications(is_read)")
        logger.info("✅ 索引创建成功")

        # 初始化默认新闻分类
        init_default_categories(cursor)

        conn.commit()
        conn.close()

        logger.info("🎉 新闻数据表初始化完成！")
        return True

    except Exception as e:
        logger.error(f"❌ 初始化新闻数据表失败: {str(e)}")
        return False


def init_default_categories(cursor):
    """初始化默认新闻分类"""
    logger.info("初始化默认新闻分类...")

    categories = [
        {
            'name': '系统更新',
            'slug': 'system-update',
            'description': '系统版本更新和功能升级公告',
            'icon': '🔄',
            'sort_order': 1
        },
        {
            'name': '新功能发布',
            'slug': 'new-feature',
            'description': '新功能上线和使用指南',
            'icon': '✨',
            'sort_order': 2
        },
        {
            'name': '平台公告',
            'slug': 'announcement',
            'description': '平台重要通知和活动信息',
            'icon': '📢',
            'sort_order': 3
        },
        {
            'name': '使用指南',
            'slug': 'tutorial',
            'description': '功能使用教程和最佳实践',
            'icon': '📚',
            'sort_order': 4
        },
        {
            'name': '活动资讯',
            'slug': 'event',
            'description': '线上活动和社区动态',
            'icon': '🎉',
            'sort_order': 5
        }
    ]

    for cat in categories:
        try:
            cursor.execute(
                """INSERT INTO news_categories (name, slug, description, icon, sort_order, status)
                   VALUES (?, ?, ?, ?, ?, 'active')""",
                (cat['name'], cat['slug'], cat['description'], cat['icon'], cat['sort_order'])
            )
            logger.info(f"✅ 创建分类: {cat['name']}")
        except sqlite3.IntegrityError:
            logger.info(f"ℹ️  分类已存在: {cat['name']}")
            continue


def create_system_update_news(version, title, content):
    """
    创建系统升级新闻
    Args:
        version: 版本号（如 V9.24.0）
        title: 新闻标题
        content: 新闻内容
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 获取系统更新分类ID
        cursor.execute("SELECT id FROM news_categories WHERE slug = 'system-update'")
        category_row = cursor.fetchone()
        category_id = category_row['id'] if category_row else 1

        # 创建slug
        slug = f"update-{version.replace('.', '-').lower()}"

        # 创建新闻文章
        cursor.execute("""
            INSERT INTO news_articles (
                title, slug, content, summary,
                category_id, author_name, status,
                is_featured, is_pinned, published_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'published', 1, 1, ?)
        """, (
            title,
            slug,
            content,
            f"{title} - {datetime.now().strftime('%Y-%m-%d')}",
            category_id,
            '系统管理员',
            datetime.now()
        ))

        # 记录到系统新闻日志
        cursor.execute("""
            INSERT INTO system_news_log (version, title, content, is_published, published_at)
            VALUES (?, ?, ?, 1, ?)
        """, (version, title, content, datetime.now()))

        # 为所有活跃用户创建通知
        cursor.execute("""
            INSERT INTO user_notifications (user_id, title, content, type, link)
            SELECT id, ?, ?, 'system', '/news/' || ?
            FROM users WHERE status = 'active'
        """, (title, f"{title} - {version}", slug))

        conn.commit()
        conn.close()

        logger.info(f"✅ 系统升级新闻创建成功: {version}")
        return True

    except Exception as e:
        logger.error(f"❌ 创建系统升级新闻失败: {str(e)}")
        return False


def generate_version_news(version, features=None):
    """
    自动生成版本升级新闻
    Args:
        version: 版本号
        features: 功能列表
    """
    features = features or []

    title = f"灵值生态园智能体系统升级至 {version}"

    content = f"""# 灵值生态园智能体系统 - {version} 版本更新

## 升级时间
{datetime.now().strftime('%Y年%m月%d日 %H:%M')}

## 版本概述
本次升级为系统带来多项重要更新和优化，进一步提升用户体验和系统性能。

## 新增功能
"""

    if features:
        for i, feature in enumerate(features, 1):
            content += f"\n{i}. **{feature}**\n"
    else:
        content += "\n1. 系统性能优化\n2. 用户体验提升\n3. 安全性增强\n"

    content += """
## 系统优化
- 性能优化：提升系统响应速度
- 安全增强：加强数据保护机制
- 用户体验：优化界面交互流程

## 技术升级
- 后端服务稳定性优化
- 数据库性能提升
- API接口优化

## 注意事项
- 请及时更新客户端以获得最佳体验
- 如遇问题，请联系客服支持

感谢您的使用与支持！
"""

    return create_system_update_news(version, title, content)


if __name__ == '__main__':
    import sqlite3

    # 初始化数据表
    if init_news_tables():
        print("\n🎉 新闻系统初始化完成！")

        # 创建V9.24.0版本升级新闻
        version = "V9.24.0"
        features = [
            "自动平台信息新闻功能",
            "批量导入数据优化",
            "经济系统功能增强",
            "区块链集成测试",
            "邮件/短信告警集成",
            "性能监控与优化",
            "用户培训文档完善"
        ]

        print(f"\n📝 生成版本 {version} 升级新闻...")
        if generate_version_news(version, features):
            print("✅ 版本升级新闻创建成功！")
        else:
            print("❌ 版本升级新闻创建失败！")
    else:
        print("❌ 新闻系统初始化失败！")
        sys.exit(1)
