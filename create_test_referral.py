#!/usr/bin/env python3
"""
创建推荐关系测试数据
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin-backend'))

from database import get_db

def create_test_referral_data():
    """创建测试推荐关系数据"""
    print("开始创建推荐关系测试数据...")
    
    conn = get_db()
    
    try:
        # 检查表是否存在
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='referral_relationships'"
        ).fetchall()
        
        if not tables:
            print("创建 referral_relationships 表...")
            conn.execute('''
                CREATE TABLE referral_relationships (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    referee_id INTEGER NOT NULL,
                    level INTEGER DEFAULT 1,
                    status VARCHAR(20) DEFAULT 'active',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(id),
                    FOREIGN KEY (referee_id) REFERENCES users(id),
                    UNIQUE(referee_id)
                )
            ''')
            conn.commit()
            print("✓ 表创建成功")
        
        # 检查 referral_codes 表是否存在
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='referral_codes'"
        ).fetchall()
        
        if not tables:
            print("创建 referral_codes 表...")
            conn.execute('''
                CREATE TABLE referral_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER NOT NULL,
                    code VARCHAR(20) UNIQUE NOT NULL,
                    status VARCHAR(20) DEFAULT 'active',
                    expires_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(id)
                )
            ''')
            conn.commit()
            print("✓ 表创建成功")
        
        # 获取现有用户
        users = conn.execute("SELECT id, username FROM users").fetchall()
        print(f"\n找到 {len(users)} 个用户:")
        for user in users:
            print(f"  ID: {user[0]}, 用户名: {user[1]}")
        
        if len(users) < 2:
            print("\n⚠️  需要至少2个用户才能创建推荐关系")
            print("请先创建更多用户")
            return
        
        # 创建推荐关系（第一个用户推荐第二个用户）
        referrer_id = users[0][0]
        referred_user_id = users[1][0]
        
        # 检查是否已存在推荐关系
        existing = conn.execute(
            "SELECT id FROM referral_relationships WHERE referee_id = ?",
            (referred_user_id,)
        ).fetchone()
        
        if existing:
            print(f"\n✓ 用户 {users[1][1]} 已有推荐人，无需重复创建")
        else:
            # 创建推荐关系
            conn.execute('''
                INSERT INTO referral_relationships (referrer_id, referee_id, level, status)
                VALUES (?, ?, 1, 'active')
            ''', (referrer_id, referred_user_id))
            
            print(f"\n✓ 创建推荐关系成功:")
            print(f"  推荐人: {users[0][1]} (ID: {referrer_id})")
            print(f"  被推荐人: {users[1][1]} (ID: {referred_user_id})")
            print(f"  推荐码: TESTCODE123")
            print(f"  奖励: 50 灵值")
        
        # 为第一个用户生成推荐码
        import random
        import string
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        existing_code = conn.execute(
            "SELECT id FROM referral_codes WHERE referrer_id = ?",
            (referrer_id,)
        ).fetchone()
        
        if existing_code:
            print(f"\n✓ 用户 {users[0][1]} 已有推荐码")
        else:
            conn.execute('''
                INSERT INTO referral_codes (referrer_id, code, expires_at)
                VALUES (?, ?, datetime('now', '+30 days'))
            ''', (referrer_id, referral_code))
            
            print(f"\n✓ 生成推荐码成功:")
            print(f"  用户: {users[0][1]} (ID: {referrer_id})")
            print(f"  推荐码: {referral_code}")
            print(f"  有效期: 30 天")
        
        conn.commit()
        print("\n" + "="*50)
        print("测试数据创建完成！")
        print("="*50)
        
    except Exception as e:
        print(f"❌ 创建测试数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == '__main__':
    create_test_referral_data()
