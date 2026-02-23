#!/usr/bin/env python3
"""初始化公司生态数据的脚本"""

import sqlite3
import random
from datetime import datetime, timedelta

# 数据库配置
DATABASE = 'lingzhi_ecosystem.db'

def init_company_data():
    """初始化公司生态数据"""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 公司动态数据
    news_categories = ['产品更新', '技术突破', '战略合作', '融资消息', '人事变动', '行业奖项']
    news_titles = [
        '灵值生态园推出智能体2.0版本，AI能力大幅提升',
        '获得A轮5000万美元融资，加速生态扩张',
        '与多家知名企业达成战略合作，共建数字生态',
        'AI核心算法取得重大突破，推理效率提升300%',
        '创始人获得年度科技企业家奖',
        '公司技术团队扩充至200人，加速产品研发'
    ]

    for i, title in enumerate(news_titles):
        cursor.execute('''
            INSERT INTO company_news (title, content, category, summary, author, status, view_count)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            title,
            f'{title}的详细内容。这是灵值生态园的重要里程碑，标志着我们在AI领域的技术实力和生态建设取得了显著进展。',
            news_categories[i % len(news_categories)],
            f'{title}的简要摘要。',
            'Admin',
            'published',
            random.randint(100, 10000)
        ))

    # 项目动态数据
    project_categories = ['AI研发', '生态建设', '市场推广', '技术支持', '人才培养']
    project_names = [
        '智能体开发平台升级',
        '多模态大模型研发',
        '生态合作伙伴计划',
        '全球市场推广活动',
        'AI人才培养计划',
        '数据安全系统建设'
    ]

    for i, name in enumerate(project_names):
        cursor.execute('''
            INSERT INTO company_projects (project_name, description, category, status, progress, priority, budget)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            name,
            f'{name}是灵值生态园的重点项目，旨在提升用户体验和产品竞争力。',
            project_categories[i % len(project_categories)],
            random.choice(['active', 'completed', 'planning']),
            random.randint(0, 100),
            random.choice(['high', 'normal', 'low']),
            random.randint(100, 1000) * 1000
        ))

    # 信息动态数据
    info_types = ['公告', '政策', '活动', '福利']
    info_titles = [
        '系统维护公告',
        '隐私政策更新通知',
        '年度开发者大会即将举办',
        '新年福利活动开始啦',
        '服务条款更新',
        '数据安全合规声明'
    ]

    for i, title in enumerate(info_titles):
        cursor.execute('''
            INSERT INTO company_info (info_type, title, content, priority, is_public)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            info_types[i % len(info_types)],
            title,
            f'{title}的详细内容，请用户关注相关信息。',
            random.choice(['high', 'normal', 'low']),
            1
        ))

    # 用户动态数据
    activity_types = ['登录', '充值', '使用智能体', '签到', '发布内容', '参与活动']
    
    # 假设有100个用户
    for user_id in range(1, 101):
        for _ in range(random.randint(1, 5)):
            cursor.execute('''
                INSERT INTO company_users (user_id, activity_type, description, metadata, device_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                user_id,
                random.choice(activity_types),
                f'用户{user_id}执行了相关活动',
                '{"details": "活动详情"}',
                random.choice(['web', 'mobile', 'app'])
            ))

    conn.commit()
    conn.close()

    print("✅ 公司生态数据初始化完成！")
    print("- 公司动态: 6条")
    print("- 项目动态: 6条")
    print("- 信息动态: 6条")
    print("- 用户动态: 约300条")

if __name__ == '__main__':
    init_company_data()
