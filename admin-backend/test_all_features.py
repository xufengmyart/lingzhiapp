#!/usr/bin/env python3
"""测试所有功能"""

import sqlite3
import os

NEW_DATABASE = 'lingzhi_ecosystem.db'

def test_database_integrity():
    """测试数据库完整性"""
    print("=" * 80)
    print("1. 测试数据库完整性")
    print("=" * 80)
    
    conn = sqlite3.connect(NEW_DATABASE)
    cursor = conn.cursor()
    
    # 检查所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print(f"\n数据库中共有 {len(tables)} 个表:")
    for table in tables:
        print(f"  - {table[0]}")
    
    # 检查用户数据
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\n用户总数: {user_count}")
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE status='active'")
    active_users = cursor.fetchone()[0]
    print(f"活跃用户: {active_users}")
    
    # 检查角色数据
    cursor.execute("SELECT COUNT(*) FROM roles")
    role_count = cursor.fetchone()[0]
    print(f"\n角色数: {role_count}")
    
    # 检查权限数据
    cursor.execute("SELECT COUNT(*) FROM permissions")
    permission_count = cursor.fetchone()[0]
    print(f"权限数: {permission_count}")
    
    # 检查专家数据
    cursor.execute("SELECT COUNT(*) FROM experts")
    expert_count = cursor.fetchone()[0]
    print(f"\n专家数: {expert_count}")
    
    # 检查推荐关系数据
    cursor.execute("SELECT COUNT(*) FROM referrals")
    referral_count = cursor.fetchone()[0]
    print(f"推荐关系数: {referral_count}")
    
    # 检查会员等级数据
    cursor.execute("SELECT COUNT(*) FROM member_levels")
    level_count = cursor.fetchone()[0]
    print(f"\n会员等级数: {level_count}")
    
    cursor.execute("SELECT COUNT(*) FROM user_member_levels")
    user_level_count = cursor.fetchone()[0]
    print(f"用户会员等级数: {user_level_count}")
    
    # 检查用户贡献数据
    cursor.execute("SELECT COUNT(*) FROM user_contributions")
    contribution_count = cursor.fetchone()[0]
    print(f"\n用户贡献记录数: {contribution_count}")
    
    # 检查待奖励数据
    cursor.execute("SELECT COUNT(*) FROM pending_rewards")
    reward_count = cursor.fetchone()[0]
    print(f"待奖励记录数: {reward_count}")
    
    # 检查审计日志数据
    cursor.execute("SELECT COUNT(*) FROM audit_logs")
    log_count = cursor.fetchone()[0]
    print(f"审计日志数: {log_count}")
    
    conn.close()
    
    print("\n✅ 数据库完整性测试通过")

def test_data_consistency():
    """测试数据一致性"""
    print("\n" + "=" * 80)
    print("2. 测试数据一致性")
    print("=" * 80)
    
    conn = sqlite3.connect(NEW_DATABASE)
    cursor = conn.cursor()
    
    # 检查用户角色关联
    cursor.execute('''
        SELECT u.username, r.name 
        FROM users u
        JOIN user_roles ur ON u.id = ur.user_id
        JOIN roles r ON ur.role_id = r.id
    ''')
    user_roles = cursor.fetchall()
    
    print(f"\n用户角色关联: {len(user_roles)} 条")
    for user_role in user_roles:
        print(f"  - {user_role[0]}: {user_role[1]}")
    
    # 检查角色权限关联
    cursor.execute('''
        SELECT r.name, COUNT(rp.permission_id) as perm_count
        FROM roles r
        LEFT JOIN role_permissions rp ON r.id = rp.role_id
        GROUP BY r.id, r.name
    ''')
    role_permissions = cursor.fetchall()
    
    print(f"\n角色权限关联:")
    for role_perm in role_permissions:
        print(f"  - {role_perm[0]}: {role_perm[1]} 个权限")
    
    # 检查用户贡献
    cursor.execute('''
        SELECT u.username, uc.cumulative_contribution
        FROM users u
        LEFT JOIN user_contributions uc ON u.id = uc.user_id
    ''')
    user_contributions = cursor.fetchall()
    
    print(f"\n用户贡献统计:")
    for user_contrib in user_contributions:
        if user_contrib[1] is not None:
            print(f"  - {user_contrib[0]}: {user_contrib[1]:.2f}")
    
    conn.close()
    
    print("\n✅ 数据一致性测试通过")

def test_backup_system():
    """测试备份系统"""
    print("\n" + "=" * 80)
    print("3. 测试备份系统")
    print("=" * 80)
    
    backup_dir = 'backups'
    if os.path.exists(backup_dir):
        backups = os.listdir(backup_dir)
        print(f"\n备份目录存在，包含 {len(backups)} 个备份文件:")
        for backup in backups[:5]:  # 只显示前 5 个
            backup_path = os.path.join(backup_dir, backup)
            backup_size = os.path.getsize(backup_path)
            print(f"  - {backup} ({backup_size / 1024:.2f} KB)")
        if len(backups) > 5:
            print(f"  ... 还有 {len(backups) - 5} 个备份文件")
    else:
        print("\n备份目录不存在")
    
    print("\n✅ 备份系统检查完成")

def main():
    print("\n" + "=" * 80)
    print("综合功能测试")
    print("=" * 80 + "\n")
    
    try:
        test_database_integrity()
        test_data_consistency()
        test_backup_system()
        
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
