#!/usr/bin/env python3
"""迁移专家和推荐关系数据"""

import sqlite3

OLD_DATABASE = '../灵值生态园智能体移植包/src/auth/auth.db'
NEW_DATABASE = 'lingzhi_ecosystem.db'

def migrate_experts():
    """迁移专家数据"""
    print("=" * 80)
    print("迁移专家数据")
    print("=" * 80)
    
    conn_old = sqlite3.connect(OLD_DATABASE)
    conn_new = sqlite3.connect(NEW_DATABASE)
    
    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()
    
    # 检查 experts 表是否存在
    cursor_old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='experts'")
    if not cursor_old.fetchone():
        print("❌ 旧数据库中 experts 表不存在")
        conn_old.close()
        conn_new.close()
        return
    
    # 获取旧数据
    cursor_old.execute('SELECT * FROM experts')
    experts = cursor_old.fetchall()
    experts_columns = [description[0] for description in cursor_old.description]
    
    print(f"旧数据库中有 {len(experts)} 条专家数据")
    
    # 检查新数据库中是否已有数据
    cursor_new.execute("SELECT COUNT(*) FROM experts")
    count = cursor_new.fetchone()[0]
    
    if count > 0:
        print(f"新数据库中已有 {count} 条专家数据，清空后重新迁移")
        cursor_new.execute("DELETE FROM experts")
    
    # 迁移数据
    migrated = 0
    for expert in experts:
        expert_data = dict(zip(experts_columns, expert))
        
        try:
            # 尝试转换数据格式
            cursor_new.execute('''
                INSERT INTO experts (
                    id, user_id, specialty, bio, rating, total_projects, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                expert_data.get('id'),
                None,  # user_id 临时设为 None
                expert_data.get('expertise', expert_data.get('specialty', '')),
                expert_data.get('description', expert_data.get('bio', '')),
                expert_data.get('rating', 0),
                expert_data.get('review_count', 0),
                expert_data.get('status', 'active'),
                expert_data.get('created_at'),
                expert_data.get('updated_at')
            ))
            migrated += 1
        except Exception as e:
            print(f"  ❌ 迁移失败 (ID: {expert_data.get('id')}): {e}")
    
    conn_new.commit()
    conn_old.close()
    conn_new.close()
    
    print(f"✅ 专家数据迁移完成，共迁移 {migrated} 条记录")

def migrate_referrals():
    """迁移推荐关系数据"""
    print("\n" + "=" * 80)
    print("迁移推荐关系数据")
    print("=" * 80)
    
    conn_old = sqlite3.connect(OLD_DATABASE)
    conn_new = sqlite3.connect(NEW_DATABASE)
    
    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()
    
    # 检查 referrals 表是否存在
    cursor_old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='referrals'")
    if not cursor_old.fetchone():
        print("❌ 旧数据库中 referrals 表不存在")
        conn_old.close()
        conn_new.close()
        return
    
    # 获取旧数据
    cursor_old.execute('SELECT * FROM referrals')
    referrals = cursor_old.fetchall()
    referrals_columns = [description[0] for description in cursor_old.description]
    
    print(f"旧数据库中有 {len(referrals)} 条推荐关系数据")
    
    # 检查新数据库中是否已有数据
    cursor_new.execute("SELECT COUNT(*) FROM referrals")
    count = cursor_new.fetchone()[0]
    
    if count > 0:
        print(f"新数据库中已有 {count} 条推荐关系数据，清空后重新迁移")
        cursor_new.execute("DELETE FROM referrals")
    
    # 迁移数据
    migrated = 0
    for referral in referrals:
        referral_data = dict(zip(referrals_columns, referral))
        
        try:
            cursor_new.execute('''
                INSERT INTO referrals (
                    id, referrer_id, referred_id, referral_code, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                referral_data.get('id'),
                referral_data.get('referrer_id'),
                referral_data.get('referred_id'),
                referral_data.get('referral_code'),
                referral_data.get('status', 'active'),
                referral_data.get('created_at'),
                referral_data.get('updated_at')
            ))
            migrated += 1
        except Exception as e:
            print(f"  ❌ 迁移失败 (ID: {referral_data.get('id')}): {e}")
    
    conn_new.commit()
    conn_old.close()
    conn_new.close()
    
    print(f"✅ 推荐关系数据迁移完成，共迁移 {migrated} 条记录")

if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("专家和推荐关系数据迁移")
    print("=" * 80 + "\n")
    
    migrate_experts()
    migrate_referrals()
    
    print("\n" + "=" * 80)
    print("✅ 所有迁移完成！")
    print("=" * 80)
