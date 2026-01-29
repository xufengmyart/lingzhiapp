#!/usr/bin/env python3
"""
初始化会员级别数据
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

def init_member_levels():
    """初始化会员级别数据"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    print("初始化会员级别数据...")
    
    # 检查是否已有数据
    cursor.execute("SELECT COUNT(*) FROM member_levels")
    count = cursor.fetchone()[0]
    
    if count > 0:
        print(f"\n⚠️  member_levels 表中已有 {count} 条数据")
        print("如需重新初始化，请先清空数据")
        conn.close()
        return
    
    # 定义会员级别
    member_levels = [
        {
            'level': 'T',
            'level_code': 'TRIAL',
            'level_name': '试用会员',
            'level_type': 'trial',
            'min_contribution_value': 0,
            'min_team_members': 0,
            'referral_commission_rate': 0.05,
            'dividend_percentage': 0.0,
            'benefits': '免费体验7天，获得100贡献值启动资金',
            'status': 'active'
        },
        {
            'level': 'B',
            'level_code': 'BASIC',
            'level_name': '基础会员',
            'level_type': 'basic',
            'min_contribution_value': 1000,
            'min_team_members': 5,
            'referral_commission_rate': 0.10,
            'dividend_percentage': 0.0,
            'benefits': '基础服务，10%推荐佣金',
            'status': 'active'
        },
        {
            'level': 'S',
            'level_code': 'STANDARD',
            'level_name': '标准会员',
            'level_type': 'standard',
            'min_contribution_value': 5000,
            'min_team_members': 20,
            'referral_commission_rate': 0.15,
            'dividend_percentage': 0.0,
            'benefits': '标准服务，15%推荐佣金',
            'status': 'active'
        },
        {
            'level': 'A',
            'level_code': 'ADVANCED',
            'level_name': '高级会员',
            'level_type': 'advanced',
            'min_contribution_value': 20000,
            'min_team_members': 50,
            'referral_commission_rate': 0.20,
            'dividend_percentage': 0.0,
            'benefits': '高级服务，20%推荐佣金',
            'status': 'active'
        },
        {
            'level': 'E',
            'level_code': 'EXPERT',
            'level_name': '专家会员',
            'level_type': 'expert',
            'min_contribution_value': 100000,
            'min_team_members': 100,
            'referral_commission_rate': 0.25,
            'dividend_percentage': 0.1,
            'benefits': '专家服务，25%推荐佣金，0.1%股权',
            'status': 'active'
        }
    ]
    
    print("\n插入会员级别数据...")
    for level_data in member_levels:
        try:
            cursor.execute("""
                INSERT INTO member_levels (
                    level, name, level_code, level_name, level_type,
                    min_contribution_value, min_team_members,
                    referral_commission_rate, dividend_percentage,
                    benefits, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                level_data['level'],
                level_data['level_name'],  # name
                level_data['level_code'],
                level_data['level_name'],
                level_data['level_type'],
                level_data['min_contribution_value'],
                level_data['min_team_members'],
                level_data['referral_commission_rate'],
                level_data['dividend_percentage'],
                level_data['benefits'],
                level_data['status']
            ))
            print(f"✅ 插入: {level_data['level_name']}")
        except Exception as e:
            print(f"❌ 插入失败 {level_data['level_name']}: {str(e)}")
    
    conn.commit()
    conn.close()
    
    print("\n" + "="*80)
    print("✅ 会员级别数据初始化完成！")
    print("="*80)


if __name__ == "__main__":
    init_member_levels()
