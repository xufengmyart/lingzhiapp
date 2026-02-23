#!/usr/bin/env python3
"""
数据初始化脚本
为数据库添加初始数据
"""

import sqlite3
import json
from datetime import datetime, timedelta

DATABASE = 'lingzhi_ecosystem.db'

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_sacred_sites():
    """初始化圣地数据"""
    print("初始化圣地数据...")

    sites = [
        {
            "name": "灵山圣地",
            "description": "灵山圣地是中国传统文化的重要象征，承载着千年的文化底蕴和精神传承。",
            "cultural_theme": "唐风精神",
            "location": "中国江苏无锡",
            "latitude": 31.4908,
            "longitude": 120.3446,
            "status": "operating",
            "image_url": "https://via.placeholder.com/400x300",
            "total_investment": 5000000,
            "expected_returns": 7500000,
            "current_value": 5500000,
            "creator_id": 1
        },
        {
            "name": "文化古村",
            "description": "文化古村是传统文化与现代文明交融的典范，展现了乡村文化的独特魅力。",
            "cultural_theme": "江南水乡",
            "location": "中国浙江绍兴",
            "latitude": 30.0142,
            "longitude": 120.5845,
            "status": "building",
            "image_url": "https://via.placeholder.com/400x300",
            "total_investment": 3000000,
            "expected_returns": 4500000,
            "current_value": 2000000,
            "creator_id": 1
        },
        {
            "name": "艺术工坊",
            "description": "艺术工坊是传承和发展传统艺术的重要基地，培养新一代艺术人才。",
            "cultural_theme": "传统工艺",
            "location": "中国苏州",
            "latitude": 31.2989,
            "longitude": 120.5853,
            "status": "planning",
            "image_url": "https://via.placeholder.com/400x300",
            "total_investment": 2000000,
            "expected_returns": 3000000,
            "current_value": 0,
            "creator_id": 1
        }
    ]

    conn = get_db()
    cursor = conn.cursor()

    for site in sites:
        cursor.execute('''
            INSERT OR IGNORE INTO sacred_sites
            (name, description, cultural_theme, location, latitude, longitude, status, image_url, total_investment, expected_returns, current_value, creator_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            site["name"], site["description"], site["cultural_theme"],
            site["location"], site["latitude"], site["longitude"],
            site["status"], site["image_url"], site["total_investment"],
            site["expected_returns"], site["current_value"], site["creator_id"]
        ))

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(sites)} 个圣地")

def initialize_cultural_projects():
    """初始化文化项目数据"""
    print("初始化文化项目数据...")

    conn = get_db()
    cursor = conn.cursor()

    # 获取第一个圣地ID
    cursor.execute('SELECT id FROM sacred_sites LIMIT 1')
    result = cursor.fetchone()
    if not result:
        print("⚠️ 没有找到圣地，跳过项目初始化")
        conn.close()
        return

    site_id = result['id']

    projects = [
        {
            "name": "古建筑修缮工程",
            "description": "对灵山圣地内的古建筑进行全面修缮，保护文化遗产。",
            "site_id": site_id,
            "project_type": "renovation",
            "status": "ongoing",
            "progress": 60,
            "budget": 800000,
            "actual_cost": 480000,
            "start_date": "2026-01-01",
            "end_date": "2026-06-30",
            "manager_id": 1
        },
        {
            "name": "文化展览策划",
            "description": "策划并实施灵山圣地文化展览活动，传播传统文化。",
            "site_id": site_id,
            "project_type": "creation",
            "status": "planning",
            "progress": 20,
            "budget": 200000,
            "actual_cost": 40000,
            "start_date": "2026-03-01",
            "end_date": "2026-05-31",
            "manager_id": 1
        }
    ]

    for project in projects:
        cursor.execute('''
            INSERT OR IGNORE INTO cultural_projects
            (name, description, site_id, project_type, status, progress, budget, actual_cost, start_date, end_date, manager_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            project["name"], project["description"], project["site_id"],
            project["project_type"], project["status"], project["progress"],
            project["budget"], project["actual_cost"], project["start_date"],
            project["end_date"], project["manager_id"]
        ))

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(projects)} 个文化项目")

def initialize_token_types():
    """初始化通证类型"""
    print("初始化通证类型...")

    token_types = [
        {
            "name": "灵值通证",
            "symbol": "LING",
            "description": "灵值生态园权益通证，代表用户在生态中的权益和贡献",
            "token_type": "equity",
            "total_supply": 10000000,
            "circulated_supply": 5000000,
            "unit_price": 1.0,
            "is_transferrable": 1
        },
        {
            "name": "治理通证",
            "symbol": "GOV",
            "description": "灵值生态园治理通证，持有者可参与生态治理决策",
            "token_type": "governance",
            "total_supply": 1000000,
            "circulated_supply": 300000,
            "unit_price": 10.0,
            "is_transferrable": 1
        },
        {
            "name": "奖励通证",
            "symbol": "REWARD",
            "description": "灵值生态园奖励通证，用于奖励优秀贡献者",
            "token_type": "reward",
            "total_supply": 5000000,
            "circulated_supply": 1000000,
            "unit_price": 0.5,
            "is_transferrable": 0
        }
    ]

    conn = get_db()
    cursor = conn.cursor()

    for token_type in token_types:
        cursor.execute('''
            INSERT OR IGNORE INTO token_types
            (name, symbol, description, token_type, total_supply, circulated_supply, unit_price, is_transferrable)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            token_type["name"], token_type["symbol"], token_type["description"],
            token_type["token_type"], token_type["total_supply"],
            token_type["circulated_supply"], token_type["unit_price"],
            token_type["is_transferrable"]
        ))

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(token_types)} 种通证类型")

def initialize_user_token_balances():
    """初始化用户通证余额"""
    print("初始化用户通证余额...")

    conn = get_db()
    cursor = conn.cursor()

    # 获取所有用户和通证类型
    cursor.execute('SELECT id FROM users')
    users = cursor.fetchall()

    cursor.execute('SELECT id FROM token_types')
    token_types = cursor.fetchall()

    # 为每个用户分配初始通证
    for user in users:
        for token_type in token_types:
            cursor.execute('''
                INSERT OR IGNORE INTO user_token_balances
                (user_id, token_type_id, balance)
                VALUES (?, ?, ?)
            ''', (user['id'], token_type['id'], 1000))

    conn.commit()
    conn.close()
    print(f"✓ 初始化了用户通证余额")

def initialize_sbt_types():
    """初始化 SBT 类型"""
    print("初始化 SBT 类型...")

    sbt_types = [
        {
            "name": "文化使者",
            "description": "授予为文化传播做出突出贡献的用户",
            "category": "badge",
            "rarity": "rare",
            "image_url": "https://via.placeholder.com/200",
            "attributes": json.dumps({"icon": "🎭", "color": "#FFD700"})
        },
        {
            "name": "建设先锋",
            "description": "授予为圣地建设做出重要贡献的用户",
            "category": "achievement",
            "rarity": "epic",
            "image_url": "https://via.placeholder.com/200",
            "attributes": json.dumps({"icon": "🏗️", "color": "#FF6B6B"})
        },
        {
            "name": "早期参与者",
            "description": "授予项目早期参与和贡献的用户",
            "category": "identity",
            "rarity": "legendary",
            "image_url": "https://via.placeholder.com/200",
            "attributes": json.dumps({"icon": "⭐", "color": "#9B59B6"})
        },
        {
            "name": "学习达人",
            "description": "授予积极学习并完成修行目标的用户",
            "category": "achievement",
            "rarity": "common",
            "image_url": "https://via.placeholder.com/200",
            "attributes": json.dumps({"icon": "📚", "color": "#3498DB"})
        },
        {
            "name": "文化认证师",
            "description": "授予通过文化专业认证的用户",
            "category": "certification",
            "rarity": "rare",
            "image_url": "https://via.placeholder.com/200",
            "attributes": json.dumps({"icon": "🎓", "color": "#2ECC71"})
        }
    ]

    conn = get_db()
    cursor = conn.cursor()

    for sbt_type in sbt_types:
        cursor.execute('''
            INSERT OR IGNORE INTO sbt_types
            (name, description, category, rarity, image_url, attributes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            sbt_type["name"], sbt_type["description"], sbt_type["category"],
            sbt_type["rarity"], sbt_type["image_url"], sbt_type["attributes"]
        ))

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(sbt_types)} 种 SBT 类型")

def initialize_knowledge():
    """初始化知识库"""
    print("初始化知识库...")

    knowledge_items = [
        {
            "title": "唐风文化概述",
            "content": "唐风文化是中国唐朝时期形成的文化风格，以开放包容、华丽典雅为特征，对后世产生了深远影响。唐朝文化在诗歌、绘画、音乐、舞蹈等领域都达到了巅峰，成为中华文明的重要组成部分。",
            "category": "文化",
            "tags": json.dumps(["唐朝", "文化", "历史"]),
            "author_id": 1,
            "is_published": 1
        },
        {
            "title": "传统建筑保护技术",
            "content": "传统建筑保护技术是保护古建筑的重要手段，包括结构加固、材料修复、病害防治等方面。通过科学的保护技术，可以有效延长古建筑的寿命，传承建筑文化。",
            "category": "技术",
            "tags": json.dumps(["建筑", "保护", "技术"]),
            "author_id": 1,
            "is_published": 1
        },
        {
            "title": "文化项目策划指南",
            "content": "文化项目策划需要考虑项目定位、目标受众、执行方案、预算管理等多个方面。成功的文化项目策划应该兼顾文化价值和商业价值，实现社会效益和经济效益的统一。",
            "category": "管理",
            "tags": json.dumps(["项目", "策划", "管理"]),
            "author_id": 1,
            "is_published": 1
        }
    ]

    conn = get_db()
    cursor = conn.cursor()

    for item in knowledge_items:
        cursor.execute('''
            INSERT OR IGNORE INTO knowledge
            (title, content, category, tags, author_id, is_published)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            item["title"], item["content"], item["category"],
            item["tags"], item["author_id"], item["is_published"]
        ))

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(knowledge_items)} 条知识库内容")

def initialize_company_news():
    """初始化公司动态"""
    print("初始化公司动态...")

    news_items = [
        {
            "title": "灵值生态园 v11.0 版本上线",
            "content": "灵值生态园 v11.0 版本正式上线！本次更新带来了全新的圣地管理、文化项目管理、通证系统、SBT 系统等功能，为用户提供更加完善的数字文化体验。感谢大家的支持与期待！",
            "category": "update",
            "image_url": "https://via.placeholder.com/800x400",
            "author_id": 1,
            "is_published": 1
        },
        {
            "title": "文化志愿者招募活动启动",
            "content": "灵值生态园启动文化志愿者招募活动，邀请热爱传统文化、愿意为文化传播贡献力量的用户加入。志愿者将有机会参与圣地建设、文化活动策划等工作。",
            "category": "recruitment",
            "image_url": "https://via.placeholder.com/800x400",
            "author_id": 1,
            "is_published": 1
        },
        {
            "title": "首届传统文化论坛即将举办",
            "content": "灵值生态园将于近期举办首届传统文化论坛，邀请文化学者、艺术家、传承人等共同探讨传统文化的传承与发展。论坛将设置主题演讲、圆桌讨论、文化体验等环节。",
            "category": "event",
            "image_url": "https://via.placeholder.com/800x400",
            "author_id": 1,
            "is_published": 1
        }
    ]

    conn = get_db()
    cursor = conn.cursor()

    for item in news_items:
        cursor.execute('''
            INSERT OR IGNORE INTO company_news
            (title, content, category, image_url, author_id, is_published, published_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            item["title"], item["content"], item["category"],
            item["image_url"], item["author_id"], item["is_published"],
            datetime.now()
        ))

    conn.commit()
    conn.close()
    print(f"✓ 初始化了 {len(news_items)} 条公司动态")

def initialize_all():
    """初始化所有数据"""
    print("="*60)
    print("开始初始化数据")
    print("="*60)
    print()

    try:
        initialize_sacred_sites()
        initialize_cultural_projects()
        initialize_token_types()
        initialize_user_token_balances()
        initialize_sbt_types()
        initialize_knowledge()
        initialize_company_news()

        print()
        print("="*60)
        print("✅ 数据初始化完成")
        print("="*60)

    except Exception as e:
        print()
        print("="*60)
        print(f"❌ 数据初始化失败: {str(e)}")
        print("="*60)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    initialize_all()
