#!/usr/bin/env python3
"""
灵值生态园智能体 - 数据库查看工具
查看数据库详细信息
"""

import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

def main():
    """主函数"""
    print("="*80)
    print("灵值生态园智能体 - 数据库详细信息")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 查看所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [t[0] for t in cursor.fetchall()]
        
        print(f"\n数据库包含 {len(tables)} 个表：\n")
        for i, table in enumerate(tables, 1):
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"{i:2d}. {table:<30} ({count} 条记录)")
        
        # 查看用户表结构
        print("\n" + "="*80)
        print("📋 users 表结构")
        print("="*80)
        cursor.execute("PRAGMA table_info(users)")
        columns = cursor.fetchall()
        
        print(f"\n字段数: {len(columns)}\n")
        print(f"{'字段名':<25} {'类型':<15} {'非空':<8} {'主键'}")
        print("-" * 80)
        for col in columns:
            cid, name, type_name, not_null, default, pk = col
            print(f"{name:<25} {type_name:<15} {'✓' if not_null else ' ':<8} {'✓' if pk else ' '}")
        
        # 查看用户数据
        print("\n" + "="*80)
        print("👥 用户数据")
        print("="*80)
        cursor.execute("SELECT * FROM users LIMIT 5")
        users = cursor.fetchall()
        
        if users:
            cursor.execute("PRAGMA table_info(users)")
            col_names = [col[1] for col in cursor.fetchall()]
            
            print(f"\n总用户数: {users[0][0] if users else 0}\n")
            
            # 显示前5个用户的简要信息
            cursor.execute("SELECT id, name, email, position, created_at FROM users LIMIT 5")
            users_data = cursor.fetchall()
            
            print(f"{'ID':<5} {'姓名':<15} {'邮箱':<25} {'职位':<15} {'创建时间'}")
            print("-" * 80)
            for user in users_data:
                created_str = datetime.fromisoformat(user[4]).strftime("%Y-%m-%d") if user[4] else ""
                print(f"{user[0]:<5} {user[1]:<15} {user[2]:<25} {user[3]:<15} {created_str}")
        
        # 查看角色表
        print("\n" + "="*80)
        print("🎭 角色数据")
        print("="*80)
        cursor.execute("SELECT * FROM roles ORDER BY level")
        roles = cursor.fetchall()
        
        if roles:
            print(f"\n总角色数: {len(roles)}\n")
            print(f"{'ID':<5} {'角色名称':<15} {'级别':<8} {'描述'}")
            print("-" * 80)
            for role in roles:
                print(f"{role[0]:<5} {role[1]:<15} {role[4]:<8} {role[3][:40]}")
        
        # 查看资源库专家
        print("\n" + "="*80)
        print("👨‍🏫 资源库专家")
        print("="*80)
        cursor.execute("SELECT * FROM experts")
        experts = cursor.fetchall()
        
        if experts:
            cursor.execute("PRAGMA table_info(experts)")
            col_names = [col[1] for col in cursor.fetchall()]
            
            print(f"\n总专家数: {len(experts)}\n")
            print(f"{'ID':<5} {'姓名':<15} {'专长':<25} {'时薪':<10} {'联系方式'}")
            print("-" * 80)
            
            # 根据实际列名调整
            for expert in experts:
                eid = expert[0]
                name = expert[1] if len(expert) > 1 else ""
                expertise = expert[2] if len(expert) > 2 else ""
                hourly_fee = expert[3] if len(expert) > 3 else ""
                contact = expert[4] if len(expert) > 4 else ""
                print(f"{eid:<5} {name:<15} {expertise:<25} {hourly_fee:<10} {contact[:30]}")
        
        # 数据库文件信息
        print("\n" + "="*80)
        print("💾 数据库信息")
        print("="*80)
        print(f"文件路径: {DB_PATH}")
        print(f"文件大小: {os.path.getsize(DB_PATH) / 1024:.2f} KB")
        print(f"修改时间: {datetime.fromtimestamp(os.path.getmtime(DB_PATH)).strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"SQLite 版本: {sqlite3.sqlite_version}")
        
        # 统计信息
        print("\n" + "="*80)
        print("📊 统计信息")
        print("="*80)
        print(f"总表数: {len(tables)}")
        print(f"用户数: {cursor.execute('SELECT COUNT(*) FROM users').fetchone()[0]}")
        print(f"角色数: {cursor.execute('SELECT COUNT(*) FROM roles').fetchone()[0]}")
        print(f"权限数: {cursor.execute('SELECT COUNT(*) FROM permissions').fetchone()[0]}")
        print(f"专家数: {cursor.execute('SELECT COUNT(*) FROM experts').fetchone()[0]}")
        print(f"用户角色关系: {cursor.execute('SELECT COUNT(*) FROM user_roles').fetchone()[0]}")
        print(f"角色权限关系: {cursor.execute('SELECT COUNT(*) FROM role_permissions').fetchone()[0]}")
        
    finally:
        conn.close()
        print("\n✓ 数据库连接已关闭")

if __name__ == "__main__":
    main()
