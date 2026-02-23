#!/usr/bin/env python3
"""
补充测试数据
"""

import sqlite3
import os
from datetime import datetime, timedelta
import random

# 配置
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lingzhi_ecosystem.db')

def add_test_data():
    """补充测试数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 1. 补充用户资源测试数据
        cursor.execute('SELECT COUNT(*) FROM user_resources')
        count = cursor.fetchone()[0]

        if count < 10:
            print("正在添加用户资源测试数据...")
            resource_types = ['土地', '房产', '知识产权', '古董', '书画', '玉器', '陶瓷', '非遗']
            for i in range(count, 15):
                cursor.execute('''
                    INSERT INTO user_resources (user_id, resource_type, resource_name, description, availability, estimated_value, status, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    i % 11 + 1,  # user_id (1-11)
                    random.choice(resource_types),
                    f'测试资源 {i+1}',
                    f'这是测试资源 {i+1} 的描述',
                    'available',
                    random.randint(1000, 100000),
                    'approved',
                    datetime.now().isoformat()
                ))
            print(f"✅ 添加了 {15-count} 条用户资源数据")

        # 2. 补充数字资产测试数据
        cursor.execute('SELECT COUNT(*) FROM digital_assets')
        count = cursor.fetchone()[0]

        if count < 10:
            print("正在添加数字资产测试数据...")
            asset_types = ['image', 'video', '3d_model', 'audio', 'document']
            rarities = ['common', 'rare', 'epic', 'legendary']
            for i in range(count, 15):
                cursor.execute('''
                    INSERT INTO digital_assets (user_id, asset_type, asset_name, description, image_url, value, rarity, is_transferable, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    i % 11 + 1,  # user_id
                    random.choice(asset_types),
                    f'数字资产 {i+1}',
                    f'这是数字资产 {i+1} 的描述',
                    f'https://example.com/asset_{i+1}.png',
                    random.randint(50, 500),
                    random.choice(rarities),
                    True,
                    datetime.now().isoformat()
                ))
            print(f"✅ 添加了 {15-count} 条数字资产数据")

        # 3. 补充签到记录测试数据
        cursor.execute('SELECT COUNT(*) FROM checkin_records')
        count = cursor.fetchone()[0]

        if count < 10:
            print("正在添加签到记录测试数据...")
            for i in range(count, 15):
                # 生成过去几天的签到记录
                days_ago = i % 7
                checkin_date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')
                cursor.execute('''
                    INSERT OR IGNORE INTO checkin_records (user_id, checkin_date, lingzhi_earned, created_at)
                    VALUES (?, ?, ?, ?)
                ''', (
                    i % 11 + 1,  # user_id
                    checkin_date,
                    10,  # 灵值奖励
                    datetime.now().isoformat()
                ))
            print(f"✅ 添加了签到记录测试数据")

        # 4. 补充公司项目测试数据
        cursor.execute('SELECT COUNT(*) FROM company_projects')
        count = cursor.fetchone()[0]

        if count < 5:
            print("正在添加公司项目测试数据...")
            projects = [
                ('西安文化数字化', '将西安文化进行数字化保护和传播', 'culture', 100000),
                ('古城墙VR体验', '开发古城墙VR虚拟现实体验项目', 'technology', 150000),
                ('汉文化博物馆', '建设汉文化主题博物馆', 'heritage', 500000),
                ('唐文化主题公园', '开发唐文化主题公园', 'entertainment', 800000),
                ('非遗传承计划', '非物质文化遗产传承保护计划', 'heritage', 200000),
            ]
            
            for i, (name, description, category, budget) in enumerate(projects):
                cursor.execute('''
                    INSERT OR IGNORE INTO company_projects (name, description, category, budget, status)
                    VALUES (?, ?, ?, ?, 'planning')
                ''', (name, description, category, budget))
            
            print(f"✅ 添加了公司项目测试数据")

        # 5. 补充转译项目测试数据
        cursor.execute('SELECT COUNT(*) FROM translation_projects')
        count = cursor.fetchone()[0]

        if count < 10:
            print("正在添加转译项目测试数据...")
            additional_projects = [
                ('folk_art', '民间艺术', '传承民间艺术，保护非遗文化', 'folklore', 'medium', 80),
                ('architecture', '古建筑保护', '保护古建筑，传承建筑文化', 'architecture', 'hard', 200),
                ('festivals', '节日文化', '记录传统节日，传承节日文化', 'heritage', 'easy', 60),
                ('crafts', '手工艺品', '传统手工艺数字化', 'art', 'medium', 90),
                ('legends', '传说故事', '收集整理传说故事', 'heritage', 'easy', 70),
            ]
            
            for project_code, title, description, category, difficulty, reward in additional_projects:
                cursor.execute('''
                    INSERT OR IGNORE INTO translation_projects (project_code, title, description, project_type, category, difficulty_level, base_reward, status)
                    VALUES (?, ?, ?, 'text', ?, ?, ?, 'active')
                ''', (project_code, title, description, category, difficulty, reward))
            
            print(f"✅ 添加了转译项目测试数据")

        conn.commit()
        print("\n✅ 所有测试数据补充完成")

    except Exception as e:
        print(f"❌ 补充测试数据失败: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    print("=== 补充测试数据 ===\n")
    add_test_data()
