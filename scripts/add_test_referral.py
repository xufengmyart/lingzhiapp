#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
添加测试推荐关系数据脚本
用于在生产环境创建测试用户的推荐关系
"""

import sqlite3
import sys
from datetime import datetime

# 数据库路径（自动检测环境）
import os
if os.path.exists('/app/meiyueart-backend/data/lingzhi_ecosystem.db'):
    DATABASE_PATH = '/app/meiyueart-backend/data/lingzhi_ecosystem.db'
else:
    # 本地开发环境
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATABASE_PATH = os.path.join(BASE_DIR, 'admin-backend', 'data', 'lingzhi_ecosystem.db')

def add_referral_relationship(referrer_id, referee_id, level=1, status='active'):
    """添加推荐关系"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute('SELECT id, username FROM users WHERE id = ?', (referrer_id,))
        referrer = cursor.fetchone()
        if not referrer:
            print(f'❌ 推荐人ID {referrer_id} 不存在')
            return False

        cursor.execute('SELECT id, username FROM users WHERE id = ?', (referee_id,))
        referee = cursor.fetchone()
        if not referee:
            print(f'❌ 被推荐人ID {referee_id} 不存在')
            return False

        # 检查是否已经存在推荐关系
        cursor.execute(
            'SELECT id FROM referral_relationships WHERE referee_id = ?',
            (referee_id,)
        )
        if cursor.fetchone():
            print(f'⚠️  被推荐人 {referee["username"]} (ID={referee_id}) 已经有推荐关系，跳过')
            return False

        # 检查不能推荐自己
        if referrer_id == referee_id:
            print(f'❌ 不能自己推荐自己')
            return False

        # 创建推荐关系
        created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute(
            """
            INSERT INTO referral_relationships (referrer_id, referee_id, level, status, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (referrer_id, referee_id, level, status, created_at)
        )

        conn.commit()
        conn.close()

        print(f'✅ 推荐关系创建成功: {referrer["username"]} (ID={referrer_id}) → {referee["username"]} (ID={referee_id})')
        return True

    except Exception as e:
        print(f'❌ 添加推荐关系失败: {e}')
        import traceback
        traceback.print_exc()
        return False

def show_referral_stats():
    """显示推荐关系统计"""
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # 统计推荐关系数量
        cursor.execute('SELECT COUNT(*) as count FROM referral_relationships')
        total = cursor.fetchone()['count']
        print(f'\n📊 推荐关系统计: 共 {total} 条记录')

        # 显示所有推荐关系
        cursor.execute("""
            SELECT
                rr.id,
                r.username as referrer_name,
                e.username as referee_name,
                rr.level,
                rr.status,
                rr.created_at
            FROM referral_relationships rr
            LEFT JOIN users r ON rr.referrer_id = r.id
            LEFT JOIN users e ON rr.referee_id = e.id
            ORDER BY rr.id
        """)
        print('\n当前推荐关系列表:')
        for row in cursor.fetchall():
            print(f'  {row["id"]}: {row["referrer_name"]} → {row["referee_name"]} (level={row["level"]}, status={row["status"]})')

        conn.close()

    except Exception as e:
        print(f'❌ 获取推荐统计失败: {e}')

def main():
    """主函数"""
    print('=' * 60)
    print('添加测试推荐关系数据')
    print('=' * 60)

    if len(sys.argv) < 2:
        print('\n用法:')
        print('  python3 add_test_referral.py <推荐人ID> <被推荐人ID> [等级] [状态]')
        print('\n示例:')
        print('  python3 add_test_referral.py 1 1037 1 active')
        print('\n可用命令:')
        print('  python3 add_test_referral.py show  # 显示推荐关系统计')
        print('  python3 add_test_referral.py demo  # 添加演示数据')
        return

    if sys.argv[1] == 'show':
        show_referral_stats()
        return

    if sys.argv[1] == 'demo':
        print('\n添加演示数据...')
        # 演示数据：许锋推荐马伟娟
        add_referral_relationship(1, 1037, 1, 'active')
        show_referral_stats()
        return

    if len(sys.argv) < 2:
        print('\n用法:')
        print('  python3 add_test_referral.py <推荐人ID> <被推荐人ID> [等级] [状态]')
        print('\n示例:')
        print('  python3 add_test_referral.py 1 1037 1 active')
        return

    referrer_id = int(sys.argv[1])
    referee_id = int(sys.argv[2])
    level = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    status = sys.argv[4] if len(sys.argv) > 4 else 'active'

    add_referral_relationship(referrer_id, referee_id, level, status)
    show_referral_stats()

if __name__ == '__main__':
    main()
