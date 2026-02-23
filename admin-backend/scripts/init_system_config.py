#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
初始化系统配置表
"""

import sys
import os
from datetime import datetime

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from database import get_db

def init_system_config_table():
    """初始化系统配置表"""
    conn = get_db()
    cursor = conn.cursor()

    # 创建系统配置表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS system_config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key VARCHAR(100) NOT NULL,
            value TEXT,
            category VARCHAR(50),
            description TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(key, category)
        )
    """)

    # 插入默认灵值配置
    lingzhi_configs = [
        ('initial_lingzhi', '100', 'lingzhi', '新用户初始灵值'),
        ('daily_limit', '500', 'lingzhi', '每日灵值上限'),
        ('checkin_reward', '10', 'lingzhi', '每日签到奖励'),
        ('checkin_consecutive_reward', '50', 'lingzhi', '连续签到奖励'),
        ('conversation_cost', '1', 'lingzhi', '每次对话消耗'),
        ('premium_conversation_cost', '2', 'lingzhi', '高级对话消耗'),
        ('dividend_rate', '0.1', 'lingzhi', '分红比例'),
        ('dividend_threshold', '1000', 'lingzhi', '分红门槛'),
        ('referral_reward', '50', 'lingzhi', '推荐奖励'),
        ('task_completion_reward', '20', 'lingzhi', '任务完成奖励'),
    ]

    for key, value, category, description in lingzhi_configs:
        cursor.execute("""
            INSERT OR IGNORE INTO system_config (key, value, category, description)
            VALUES (?, ?, ?, ?)
        """, (key, value, category, description))

    conn.commit()
    conn.close()

    print("✅ 系统配置表初始化完成")

if __name__ == '__main__':
    init_system_config_table()
