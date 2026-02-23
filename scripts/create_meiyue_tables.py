#!/usr/bin/env python3
"""
创建媄月商业艺术系统所需的数据库表
"""

import sqlite3
import sys

# 数据库路径
DATABASE = 'lingzhi_ecosystem.db'

def create_tables():
    """创建所有缺失的数据库表"""

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # ==================== 圣地管理系统 ====================

    # 圣地表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sacred_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            cultural_theme TEXT,
            location TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'planning',
            image_url TEXT,
            total_investment REAL DEFAULT 0,
            expected_returns REAL DEFAULT 0,
            current_value REAL DEFAULT 0,
            creator_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
    ''')

    # 圣地资源表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sacred_site_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            site_id INTEGER NOT NULL,
            resource_type TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            value REAL DEFAULT 0,
            status TEXT DEFAULT 'available',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (site_id) REFERENCES sacred_sites(id)
        )
    ''')

    # ==================== 文化项目管理系统 ====================

    # 文化项目表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cultural_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            site_id INTEGER,
            project_type TEXT,
            status TEXT DEFAULT 'planning',
            progress INTEGER DEFAULT 0,
            budget REAL DEFAULT 0,
            actual_cost REAL DEFAULT 0,
            start_date DATE,
            end_date DATE,
            manager_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (site_id) REFERENCES sacred_sites(id),
            FOREIGN KEY (manager_id) REFERENCES users(id)
        )
    ''')

    # 项目参与者表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS project_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            role TEXT NOT NULL,
            contribution TEXT,
            reward REAL DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES cultural_projects(id),
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # ==================== 用户修行记录系统 ====================

    # 用户学习记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_learning_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            knowledge_id INTEGER,
            knowledge_title TEXT,
            learning_type TEXT,
            duration INTEGER DEFAULT 0,
            notes TEXT,
            realization TEXT,
            reward INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 用户旅程阶段表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_journey_stages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            stage_name TEXT NOT NULL,
            stage_level INTEGER NOT NULL,
            description TEXT,
            requirements TEXT,
            progress INTEGER DEFAULT 0,
            is_completed BOOLEAN DEFAULT 0,
            completed_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(user_id, stage_name)
        )
    ''')

    # ==================== 用户贡献系统 ====================

    # 用户贡献记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_id INTEGER,
            contribution_type TEXT NOT NULL,
            description TEXT NOT NULL,
            attachments TEXT,
            status TEXT DEFAULT 'pending',
            review_comment TEXT,
            reward REAL DEFAULT 0,
            reviewer_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            reviewed_at TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES cultural_projects(id),
            FOREIGN KEY (reviewer_id) REFERENCES users(id)
        )
    ''')

    # ==================== 通证管理系统 ====================

    # 通证类型表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            symbol TEXT NOT NULL UNIQUE,
            description TEXT,
            token_type TEXT NOT NULL,
            total_supply INTEGER DEFAULT 0,
            circulated_supply INTEGER DEFAULT 0,
            unit_price REAL DEFAULT 0,
            is_transferrable BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 用户通证余额表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_token_balances (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token_type_id INTEGER NOT NULL,
            balance REAL DEFAULT 0,
            frozen_balance REAL DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (token_type_id) REFERENCES token_types(id),
            UNIQUE(user_id, token_type_id)
        )
    ''')

    # 通证交易记录表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS token_transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user_id INTEGER,
            to_user_id INTEGER NOT NULL,
            token_type_id INTEGER NOT NULL,
            amount REAL NOT NULL,
            transaction_type TEXT NOT NULL,
            related_id INTEGER,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (from_user_id) REFERENCES users(id),
            FOREIGN KEY (to_user_id) REFERENCES users(id),
            FOREIGN KEY (token_type_id) REFERENCES token_types(id)
        )
    ''')

    # ==================== SBT 管理系统 ====================

    # SBT 类型表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sbt_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            category TEXT NOT NULL,
            rarity TEXT DEFAULT 'common',
            image_url TEXT,
            attributes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # 用户 SBT 持有表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_sbts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            sbt_type_id INTEGER NOT NULL,
            metadata TEXT,
            issued_by INTEGER,
            issued_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (sbt_type_id) REFERENCES sbt_types(id),
            FOREIGN KEY (issued_by) REFERENCES users(id),
            UNIQUE(user_id, sbt_type_id)
        )
    ''')

    # ==================== 社群活动系统 ====================

    # 社群活动表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS community_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            activity_type TEXT NOT NULL,
            location TEXT,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            max_participants INTEGER,
            current_participants INTEGER DEFAULT 0,
            status TEXT DEFAULT 'upcoming',
            organizer_id INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (organizer_id) REFERENCES users(id)
        )
    ''')

    # 活动参与者表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            status TEXT DEFAULT 'registered',
            check_in_time TIMESTAMP,
            feedback TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (activity_id) REFERENCES community_activities(id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            UNIQUE(activity_id, user_id)
        )
    ''')

    # ==================== 公司动态系统 ====================

    # 公司动态表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS company_news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            image_url TEXT,
            author_id INTEGER,
            is_published BOOLEAN DEFAULT 0,
            published_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    ''')

    # ==================== 其他补充表 ====================

    # 数字资产表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS digital_assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            asset_type TEXT NOT NULL,
            token_id TEXT,
            contract_address TEXT,
            owner_id INTEGER NOT NULL,
            related_project_id INTEGER,
            metadata TEXT,
            value REAL DEFAULT 0,
            is_frozen BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (owner_id) REFERENCES users(id)
        )
    ''')

    # 用户资源表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            resource_type TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            file_url TEXT,
            file_size INTEGER,
            mime_type TEXT,
            is_public BOOLEAN DEFAULT 0,
            download_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # 知识库项目表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            category TEXT,
            tags TEXT,
            author_id INTEGER,
            view_count INTEGER DEFAULT 0,
            like_count INTEGER DEFAULT 0,
            is_published BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author_id) REFERENCES users(id)
        )
    ''')

    # 提交更改
    conn.commit()

    # 显示所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    print("✅ 数据库表创建成功！")
    print("\n当前数据库中的所有表：")
    for table in tables:
        print(f"  - {table[0]}")

    conn.close()


if __name__ == '__main__':
    try:
        create_tables()
    except Exception as e:
        print(f"❌ 创建数据库表失败: {str(e)}")
        sys.exit(1)
