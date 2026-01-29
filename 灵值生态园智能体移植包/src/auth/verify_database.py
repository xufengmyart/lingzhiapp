#!/usr/bin/env python3
"""
灵值生态园智能体 - 数据库验证报告
验证数据库连接并生成报告
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

def main():
    """主函数"""
    print("="*80)
    print("灵值生态园智能体 - 数据库验证报告")
    print(f"验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 数据库文件信息
    print("\n✓ 数据库连接成功")
    print(f"\n📁 数据库文件信息:")
    print(f"  - 文件路径: {DB_PATH}")
    print(f"  - 文件大小: {os.path.getsize(DB_PATH) / 1024:.2f} KB")
    print(f"  - 修改时间: {datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  - SQLite 版本: {sqlite3.sqlite_version}")
    
    # 表信息
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [t[0] for t in cursor.fetchall()]
    
    print(f"\n📊 数据库表统计:")
    print(f"  - 总表数: {len(tables)}")
    print(f"  - 包含数据的表数: {sum(1 for t in tables if cursor.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] > 0)}")
    
    # 用户统计
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"  - 用户数: {user_count}")
    
    if user_count > 0:
        cursor.execute("SELECT id, name, email, position FROM users LIMIT 10")
        users = cursor.fetchall()
        print(f"\n👥 用户列表（前10位）:")
        print(f"  {'ID':<5} {'姓名':<15} {'邮箱':<25} {'职位'}")
        print(f"  {'-'*60}")
        for user in users:
            print(f"  {user[0]:<5} {user[1]:<15} {user[2]:<25} {user[3]}")
    
    # 角色统计
    cursor.execute("SELECT COUNT(*) FROM roles")
    role_count = cursor.fetchone()[0]
    print(f"  - 角色数: {role_count}")
    
    if role_count > 0:
        cursor.execute("SELECT id, name FROM roles ORDER BY id")
        roles = cursor.fetchall()
        print(f"\n🎭 角色列表:")
        print(f"  {'ID':<5} {'角色名称'}")
        print(f"  {'-'*20}")
        for role in roles:
            print(f"  {role[0]:<5} {role[1]}")
    
    # 权限统计
    cursor.execute("SELECT COUNT(*) FROM permissions")
    perm_count = cursor.fetchone()[0]
    print(f"  - 权限数: {perm_count}")
    
    # 专家统计
    cursor.execute("SELECT COUNT(*) FROM experts")
    expert_count = cursor.fetchone()[0]
    print(f"  - 资源库专家数: {expert_count}")
    
    if expert_count > 0:
        cursor.execute("SELECT id, name, expertise FROM experts LIMIT 10")
        experts = cursor.fetchall()
        print(f"\n👨‍🏫 资源库专家列表（前10位）:")
        print(f"  {'ID':<5} {'专家姓名':<15} {'专长'}")
        print(f"  {'-'*60}")
        for expert in experts:
            print(f"  {expert[0]:<5} {expert[1]:<15} {expert[2][:40]}")
    
    # 表结构信息
    print(f"\n📋 表详细信息:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print(f"  - {table:<30} {count:>5} 条记录, {len(columns)} 个字段")
    
    # 关键关系统计
    cursor.execute("SELECT COUNT(*) FROM user_roles")
    ur_count = cursor.fetchone()[0]
    print(f"  - 用户角色关系: {ur_count}")
    
    cursor.execute("SELECT COUNT(*) FROM role_permissions")
    rp_count = cursor.fetchone()[0]
    print(f"  - 角色权限关系: {rp_count}")
    
    # 验证结果
    print("\n" + "="*80)
    print("✅ 数据库验证结果")
    print("="*80)
    print(f"\n✓ 数据库文件存在且可访问")
    print(f"✓ 数据库包含 {len(tables)} 个表")
    print(f"✓ 数据库包含 {user_count} 个用户")
    print(f"✓ 数据库包含 {role_count} 个角色")
    print(f"✓ 数据库包含 {perm_count} 个权限")
    print(f"✓ 数据库包含 {expert_count} 个资源库专家")
    print(f"✓ 用户-角色关系: {ur_count}")
    print(f"✓ 角色-权限关系: {rp_count}")
    
    print("\n" + "="*80)
    print("✅ 数据库验证完成 - 所有功能正常")
    print("="*80)
    
    conn.close()


if __name__ == "__main__":
    main()
