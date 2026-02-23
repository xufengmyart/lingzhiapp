#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
灵值生态园 - 快速重置所有用户密码（非交互式）
用途：将所有用户的密码统一重置为 123456
作者：Coze Coding
版本：v1.0
日期：2026-02-11
"""

import sqlite3
import hashlib
import sys
import os

# 数据库路径
DATABASE = '/workspace/projects/lingzhi_ecosystem.db'

# 默认密码
DEFAULT_PASSWORD = '123456'

def hash_password(password):
    """密码哈希（SHA256）"""
    return hashlib.sha256(password.encode()).hexdigest()

def main():
    print("=" * 70)
    print("灵值生态园 - 快速重置所有用户密码")
    print("=" * 70)
    print()
    
    # 检查数据库文件
    if not os.path.exists(DATABASE):
        print(f"❌ 错误：数据库文件不存在: {DATABASE}")
        return 1
    
    print(f"✅ 数据库文件: {DATABASE}")
    print(f"📌 默认密码: {DEFAULT_PASSWORD}")
    print()
    
    # 连接数据库
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # 查询当前用户数量
    cursor.execute('SELECT COUNT(*) as count FROM users')
    user_count = cursor.fetchone()['count']
    
    print(f"当前用户数量: {user_count}")
    print()
    
    if user_count == 0:
        print("⚠️  数据库中没有用户，无需重置密码")
        conn.close()
        return 0
    
    # 显示用户列表
    cursor.execute('''
        SELECT id, username, phone, email, status
        FROM users
        ORDER BY id
    ''')
    users = cursor.fetchall()
    
    print("当前用户列表：")
    print("-" * 70)
    print(f"{'ID':<6} {'用户名':<20} {'手机号':<15} {'邮箱':<25} {'状态':<10}")
    print("-" * 70)
    for user in users:
        print(f"{user['id']:<6} {user['username']:<20} {user['phone'] or 'N/A':<15} {user['email'] or 'N/A':<25} {user['status']:<10}")
    
    print()
    print(f"即将将所有 {user_count} 个用户的密码重置为 '{DEFAULT_PASSWORD}'")
    print()
    
    # 备份数据库
    backup_file = f"{DATABASE}.backup.{__import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')}"
    import shutil
    shutil.copy2(DATABASE, backup_file)
    print(f"✅ 数据库已备份到: {backup_file}")
    print()
    
    # 生成密码哈希
    password_hash = hash_password(DEFAULT_PASSWORD)
    print(f"密码哈希: {password_hash}")
    print()
    
    # 更新所有用户的密码
    print("正在重置所有用户密码...")
    cursor.execute('''
        UPDATE users
        SET password_hash = ?, updated_at = CURRENT_TIMESTAMP
    ''', (password_hash,))
    
    affected = cursor.rowcount
    conn.commit()
    
    print(f"✅ 成功！已重置 {affected} 个用户的密码")
    print(f"📌 新密码: {DEFAULT_PASSWORD}")
    print()
    
    # 验证重置结果
    print("验证重置结果...")
    cursor.execute('SELECT password_hash FROM users LIMIT 1')
    row = cursor.fetchone()
    
    if row and row['password_hash'] == password_hash:
        print("✅ 验证通过：密码哈希正确")
    else:
        print("⚠️  验证警告：密码哈希可能不正确")
    
    # 验证所有用户
    cursor.execute('SELECT COUNT(*) FROM users WHERE password_hash = ?', (password_hash,))
    hash_count = cursor.fetchone()[0]
    print(f"✅ 验证通过：{hash_count}/{user_count} 个用户的密码已正确重置")
    
    conn.close()
    
    print()
    print("=" * 70)
    print("操作完成！")
    print("=" * 70)
    print()
    print("📝 提示：")
    print(f"  - 所有用户的新密码为: {DEFAULT_PASSWORD}")
    print("  - 建议用户首次登录后立即修改密码")
    print(f"  - 数据库已备份到: {backup_file}")
    print()
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
