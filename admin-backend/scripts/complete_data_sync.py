#!/usr/bin/env python3
"""
完整数据迁移和同步脚本
迁移所有重要数据，确保数据完整性
"""

import sqlite3
import os
from datetime import datetime

# 数据库路径
OLD_DATABASE = '../灵值生态园智能体移植包/src/auth/auth.db'
NEW_DATABASE = 'lingzhi_ecosystem.db'

def backup_database():
    """备份数据库"""
    try:
        import shutil
        from datetime import datetime
        
        backup_dir = 'backups'
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, f'lingzhi_ecosystem_before_sync_{timestamp}.db')
        
        shutil.copy2(NEW_DATABASE, backup_file)
        print(f"✅ 数据库已备份: {backup_file}")
        return True
    except Exception as e:
        print(f"❌ 数据库备份失败: {e}")
        return False

def create_missing_tables():
    """创建缺失的表"""
    print("\n" + "=" * 80)
    print("创建缺失的表...")
    print("=" * 80)
    
    conn = sqlite3.connect(NEW_DATABASE)
    cursor = conn.cursor()
    
    # 创建角色表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ 表 roles 创建成功")
    
    # 创建权限表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS permissions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            resource TEXT,
            action TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ 表 permissions 创建成功")
    
    # 创建角色权限关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS role_permissions (
            role_id INTEGER NOT NULL,
            permission_id INTEGER NOT NULL,
            PRIMARY KEY (role_id, permission_id),
            FOREIGN KEY (role_id) REFERENCES roles(id),
            FOREIGN KEY (permission_id) REFERENCES permissions(id)
        )
    ''')
    print("  ✅ 表 role_permissions 创建成功")
    
    # 创建用户角色关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_roles (
            user_id INTEGER NOT NULL,
            role_id INTEGER NOT NULL,
            PRIMARY KEY (user_id, role_id),
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (role_id) REFERENCES roles(id)
        )
    ''')
    print("  ✅ 表 user_roles 创建成功")
    
    # 创建会员等级表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS member_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            level_order INTEGER DEFAULT 0,
            required_lingzhi INTEGER DEFAULT 0,
            benefits TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ 表 member_levels 创建成功")
    
    # 创建用户会员等级关联表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_member_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            level_id INTEGER NOT NULL,
            contribution_value DECIMAL(10,2) DEFAULT 0,
            team_member_count INTEGER DEFAULT 0,
            total_earned DECIMAL(10,2) DEFAULT 0,
            total_dividend_earned DECIMAL(10,2) DEFAULT 0,
            equity_percentage DECIMAL(5,2) DEFAULT 0,
            level_since TIMESTAMP,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (level_id) REFERENCES member_levels(id)
        )
    ''')
    print("  ✅ 表 user_member_levels 创建成功")
    
    # 创建用户贡献表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_contributions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            cumulative_contribution DECIMAL(10,2) DEFAULT 0,
            project_contribution DECIMAL(10,2) DEFAULT 0,
            remaining_contribution DECIMAL(10,2) DEFAULT 0,
            consumed_contribution DECIMAL(10,2) DEFAULT 0,
            initial_contribution DECIMAL(10,2) DEFAULT 0,
            referral_reward DECIMAL(10,2) DEFAULT 0,
            commission_income DECIMAL(10,2) DEFAULT 0,
            team_income DECIMAL(10,2) DEFAULT 0,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("  ✅ 表 user_contributions 创建成功")
    
    # 创建待奖励表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reward_type TEXT NOT NULL,
            amount DECIMAL(10,2) NOT NULL,
            reason TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("  ✅ 表 pending_rewards 创建成功")
    
    # 创建推荐表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_id INTEGER NOT NULL,
            referral_code TEXT,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (referrer_id) REFERENCES users(id),
            FOREIGN KEY (referred_id) REFERENCES users(id)
        )
    ''')
    print("  ✅ 表 referrals 创建成功")
    
    # 创建审计日志表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            action TEXT NOT NULL,
            resource TEXT,
            resource_id INTEGER,
            details TEXT,
            ip_address TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    print("  ✅ 表 audit_logs 创建成功")
    
    # 创建专家表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            specialty TEXT,
            bio TEXT,
            rating DECIMAL(3,2) DEFAULT 0,
            total_projects INTEGER DEFAULT 0,
            status TEXT DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("  ✅ 表 experts 创建成功")
    
    conn.commit()
    conn.close()
    
    print("\n✅ 所有缺失的表创建完成！")

def migrate_simple_table(conn_old, conn_new, table_name, field_mapping=None):
    """迁移简单表（直接复制）"""
    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()
    
    # 检查新表是否已有数据
    cursor_new.execute(f"SELECT COUNT(*) FROM {table_name}")
    if cursor_new.fetchone()[0] > 0:
        print(f"  ⊘ 表 {table_name} 已有数据，跳过迁移")
        return 0
    
    # 获取旧表结构
    cursor_old.execute(f"PRAGMA table_info({table_name})")
    old_columns = cursor_old.fetchall()
    old_column_names = [col[1] for col in old_columns]
    
    # 获取新表结构
    cursor_new.execute(f"PRAGMA table_info({table_name})")
    new_columns = cursor_new.fetchall()
    new_column_names = [col[1] for col in new_columns]
    
    # 找出共有的字段
    common_columns = set(old_column_names) & set(new_column_names)
    common_column_names = [col for col in old_column_names if col in common_columns]
    
    if not common_column_names:
        print(f"  ❌ 表 {table_name} 没有共有字段")
        return 0
    
    # 获取旧数据
    cursor_old.execute(f"SELECT {','.join(common_column_names)} FROM {table_name}")
    old_data = cursor_old.fetchall()
    
    if not old_data:
        print(f"  ⊘ 表 {table_name} 无数据")
        return 0
    
    # 构建插入语句
    placeholders = ','.join(['?' for _ in common_column_names])
    insert_sql = f"INSERT INTO {table_name} ({','.join(common_column_names)}) VALUES ({placeholders})"
    
    # 插入数据
    migrated = 0
    for row in old_data:
        try:
            cursor_new.execute(insert_sql, row)
            migrated += 1
        except Exception as e:
            print(f"  ❌ 迁移失败: {e}")
    
    print(f"  ✅ 表 {table_name}: 迁移 {migrated} 条记录")
    return migrated

def migrate_with_user_mapping(conn_old, conn_new, table_name, user_id_field):
    """迁移需要用户ID映射的表"""
    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()
    
    # 获取用户ID映射（需要设置 row_factory）
    conn_new.row_factory = sqlite3.Row
    cursor_new = conn_new.cursor()
    
    cursor_new.execute("SELECT id, username, email FROM users")
    new_users = {row['username']: row['id'] for row in cursor_new.fetchall()}
    new_users_email = {row['email']: row['id'] for row in cursor_new.fetchall() if row['email']}
    
    # 恢复 row_factory
    conn_new.row_factory = None
    cursor_new = conn_new.cursor()
    
    # 获取旧表结构
    cursor_old.execute(f"PRAGMA table_info({table_name})")
    old_columns = cursor_old.fetchall()
    old_column_names = [col[1] for col in old_columns]
    
    # 获取新表结构
    cursor_new.execute(f"PRAGMA table_info({table_name})")
    new_columns = cursor_new.fetchall()
    new_column_names = [col[1] for col in new_columns]
    
    # 找出共有的字段
    common_columns = set(old_column_names) & set(new_column_names)
    common_column_names = [col for col in old_column_names if col in common_columns]
    
    if not common_columns:
        print(f"  ❌ 表 {table_name} 没有共有字段")
        return 0
    
    if user_id_field not in common_column_names:
        print(f"  ❌ 表 {table_name} 没有 {user_id_field} 字段")
        return 0
    
    # 获取旧数据
    cursor_old.execute(f"SELECT {','.join(common_column_names)} FROM {table_name}")
    old_data = cursor_old.fetchall()
    
    if not old_data:
        return 0
    
    # 获取旧用户信息
    cursor_old.execute("SELECT id, name, email FROM users")
    old_users = cursor_old.fetchall()
    old_user_map = {}
    for old_user in old_users:
        old_user_id, name, email = old_user
        old_user_map[old_user_id] = {'name': name, 'email': email}
    
    # 迁移数据
    migrated = 0
    for row in old_data:
        try:
            # 转换为字典
            row_dict = dict(zip(common_column_names, row))
            
            # 映射用户ID
            old_user_id = row_dict[user_id_field]
            if old_user_id not in old_user_map:
                continue
            
            old_user_info = old_user_map[old_user_id]
            new_user_id = new_users.get(old_user_info['name']) or new_users_email.get(old_user_info['email'])
            
            if not new_user_id:
                continue
            
            # 更新用户ID
            row_dict[user_id_field] = new_user_id
            
            # 构建插入语句
            placeholders = ','.join(['?' for _ in common_column_names])
            insert_sql = f"INSERT INTO {table_name} ({','.join(common_column_names)}) VALUES ({placeholders})"
            
            cursor_new.execute(insert_sql, list(row_dict.values()))
            migrated += 1
        except Exception as e:
            print(f"  ❌ 迁移失败: {e}")
    
    print(f"  ✅ 表 {table_name}: 迁移 {migrated} 条记录")
    return migrated

def migrate_all_data():
    """迁移所有数据"""
    print("\n" + "=" * 80)
    print("开始迁移所有数据...")
    print("=" * 80)
    
    conn_old = sqlite3.connect(OLD_DATABASE)
    conn_new = sqlite3.connect(NEW_DATABASE)
    
    total_migrated = 0
    
    # 迁移简单表
    simple_tables = [
        'roles',
        'permissions',
        'role_permissions',
        'member_levels'
    ]
    
    print("\n--- 迁移基础数据表 ---")
    for table in simple_tables:
        count = migrate_simple_table(conn_old, conn_new, table)
        total_migrated += count
    
    # 迁移需要用户ID映射的表
    user_mapping_tables = [
        ('user_roles', 'user_id'),
        ('user_member_levels', 'user_id'),
        ('pending_rewards', 'user_id'),
        ('referrals', 'referrer_id'),
        ('audit_logs', 'user_id'),
        ('experts', 'user_id')
    ]
    
    print("\n--- 迁移用户关联数据表 ---")
    for table, user_field in user_mapping_tables:
        count = migrate_with_user_mapping(conn_old, conn_new, table, user_field)
        total_migrated += count
    
    # 迁移用户贡献数据
    print("\n--- 迁移用户贡献数据 ---")
    cursor_old = conn_old.cursor()
    cursor_new = conn_new.cursor()
    
    # 设置 row_factory 以便访问字段名
    conn_new.row_factory = sqlite3.Row
    cursor_new = conn_new.cursor()
    
    cursor_new.execute("SELECT id, username, email FROM users")
    new_users = {row['username']: row['id'] for row in cursor_new.fetchall()}
    
    # 恢复 row_factory
    conn_new.row_factory = None
    cursor_new = conn_new.cursor()
    
    cursor_old.execute("SELECT * FROM user_contributions_v2")
    old_data = cursor_old.fetchall()
    
    if old_data:
        cursor_old.execute("PRAGMA table_info(user_contributions_v2)")
        columns = cursor_old.fetchall()
        column_names = [col[1] for col in columns]
        
        # 获取用户ID映射
        conn_new.row_factory = sqlite3.Row
        cursor_new = conn_new.cursor()
        
        cursor_new.execute("SELECT id, username, email FROM users")
        new_users = {row['username']: row['id'] for row in cursor_new.fetchall()}
        new_users_email = {row['email']: row['id'] for row in cursor_new.fetchall() if row['email']}
        
        conn_new.row_factory = None
        cursor_new = conn_new.cursor()
        
        cursor_old.execute("SELECT id, name, email FROM users")
        old_users = cursor_old.fetchall()
        old_user_map = {}
        for old_user in old_users:
            old_user_id, name, email = old_user
            old_user_map[old_user_id] = {'name': name, 'email': email}
        
        migrated = 0
        for row in old_data:
            try:
                row_dict = dict(zip(column_names, row))
                
                # 映射用户ID
                old_user_id = row_dict['user_id']
                if old_user_id not in old_user_map:
                    continue
                
                old_user_info = old_user_map[old_user_id]
                new_user_id = new_users.get(old_user_info['name']) or new_users_email.get(old_user_info['email'])
                
                if not new_user_id:
                    continue
                
                # 更新用户ID
                row_dict['user_id'] = new_user_id
                
                # 插入数据
                placeholders = ','.join(['?' for _ in column_names])
                insert_sql = f"INSERT INTO user_contributions ({','.join(column_names)}) VALUES ({placeholders})"
                cursor_new.execute(insert_sql, list(row_dict.values()))
                migrated += 1
            except Exception as e:
                print(f"  ❌ 迁移失败: {e}")
        
        print(f"  ✅ 表 user_contributions: 迁移 {migrated} 条记录")
        total_migrated += migrated
    
    conn_new.commit()
    conn_new.close()
    conn_old.close()
    
    print("\n" + "=" * 80)
    print(f"数据迁移完成！共迁移 {total_migrated} 条记录")
    print("=" * 80)

if __name__ == '__main__':
    print("=" * 80)
    print("完整数据迁移和同步")
    print("=" * 80)
    
    # 1. 备份数据库
    print("\n步骤 1: 备份数据库")
    if not backup_database():
        print("❌ 备份失败，终止迁移")
        exit(1)
    
    # 2. 创建缺失的表
    print("\n步骤 2: 创建缺失的表")
    create_missing_tables()
    
    # 3. 迁移所有数据
    print("\n步骤 3: 迁移所有数据")
    migrate_all_data()
    
    print("\n" + "=" * 80)
    print("✅ 数据同步完成！")
    print("=" * 80)
    print("\n请重启后端服务以使更改生效。")
