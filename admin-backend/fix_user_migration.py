#!/usr/bin/env python3
"""
用户数据修复和迁移脚本
用于恢复旧数据库的用户数据到新数据库
"""

import sqlite3
import hashlib
import os

# 数据库路径
OLD_DATABASE = '../灵值生态园智能体移植包/src/auth/auth.db'
NEW_DATABASE = 'lingzhi_ecosystem.db'

def migrate_users():
    """迁移用户数据"""
    print("=" * 80)
    print("开始迁移用户数据...")
    print("=" * 80)
    
    # 检查旧数据库
    if not os.path.exists(OLD_DATABASE):
        print(f"错误：旧数据库不存在: {OLD_DATABASE}")
        return
    
    # 连接旧数据库
    conn_old = sqlite3.connect(OLD_DATABASE)
    cursor_old = conn_old.cursor()
    
    # 查询旧用户
    cursor_old.execute("SELECT id, name, email, phone, password_hash, created_at FROM users")
    old_users = cursor_old.fetchall()
    
    print(f"\n旧数据库中的用户数量: {len(old_users)}")
    
    if not old_users:
        print("旧数据库中没有用户数据")
        conn_old.close()
        return
    
    # 连接新数据库
    conn_new = sqlite3.connect(NEW_DATABASE)
    cursor_new = conn_new.cursor()
    
    # 查询新数据库中的用户
    cursor_new.execute("SELECT COUNT(*) FROM users")
    new_user_count = cursor_new.fetchone()[0]
    print(f"新数据库中的用户数量（迁移前）: {new_user_count}")
    
    migrated_count = 0
    skipped_count = 0
    error_count = 0
    
    for old_user in old_users:
        old_id, name, email, phone, password_hash, created_at = old_user
        
        # 处理重复邮箱：添加后缀
        username = name
        if email:
            # 检查是否已存在相同邮箱的用户
            cursor_new.execute("SELECT COUNT(*) FROM users WHERE email = ?", (email,))
            email_count = cursor_new.fetchone()[0]
            if email_count > 0:
                # 添加序号后缀
                username = f"{name}_{old_id}"
                print(f"  ⚠️  邮箱重复: {email}，用户名改为: {username}")
        
        # 检查是否已存在相同用户名的用户
        cursor_new.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor_new.fetchone():
            skipped_count += 1
            print(f"  ⊘ 跳过（用户名已存在）: {username}")
            continue
        
        # 插入新用户
        try:
            cursor_new.execute(
                """INSERT INTO users 
                   (username, email, phone, password_hash, total_lingzhi, status, login_type, created_at) 
                   VALUES (?, ?, ?, ?, 0, 'active', 'phone', ?)""",
                (username, email or '', phone or '', password_hash, created_at)
            )
            migrated_count += 1
            print(f"  ✅ 迁移成功: {username} ({email or '无邮箱'})")
        except Exception as e:
            error_count += 1
            print(f"  ❌ 迁移失败: {username} - {str(e)}")
    
    # 提交更改
    conn_new.commit()
    
    # 查询迁移后的用户数量
    cursor_new.execute("SELECT COUNT(*) FROM users")
    final_user_count = cursor_new.fetchone()[0]
    
    # 关闭连接
    conn_new.close()
    conn_old.close()
    
    # 打印结果
    print("\n" + "=" * 80)
    print("迁移完成！")
    print("=" * 80)
    print(f"迁移成功: {migrated_count} 个用户")
    print(f"跳过重复: {skipped_count} 个用户")
    print(f"迁移失败: {error_count} 个用户")
    print(f"\n新数据库中的用户数量（迁移后）: {final_user_count}")
    
    # 验证迁移结果
    print("\n验证迁移结果...")
    conn_new = sqlite3.connect(NEW_DATABASE)
    cursor_new = conn_new.cursor()
    
    cursor_new.execute("SELECT id, username, email, SUBSTR(password_hash, 1, 10) as prefix FROM users ORDER BY id")
    users = cursor_new.fetchall()
    
    print(f"\n{'ID':<5} {'用户名':<30} {'邮箱':<30} {'密码前缀':<15}")
    print("-" * 80)
    for user in users:
        user_id, username, email, prefix = user
        print(f"{user_id:<5} {username:<30} {email or '无邮箱':<30} {prefix:<15}")
    
    conn_new.close()

def backup_database():
    """备份数据库"""
    print("\n" + "=" * 80)
    print("备份数据库...")
    print("=" * 80)
    
    import shutil
    from datetime import datetime
    
    # 创建备份目录
    backup_dir = './admin-backend/backups'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    # 备份文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f"{backup_dir}/lingzhi_ecosystem_backup_{timestamp}.db"
    
    # 复制数据库
    try:
        shutil.copy2(NEW_DATABASE, backup_file)
        print(f"✅ 数据库备份成功: {backup_file}")
    except Exception as e:
        print(f"❌ 数据库备份失败: {str(e)}")

if __name__ == '__main__':
    # 1. 备份数据库
    backup_database()
    
    # 2. 迁移用户数据
    migrate_users()
    
    print("\n" + "=" * 80)
    print("修复完成！请重启后端服务。")
    print("=" * 80)
