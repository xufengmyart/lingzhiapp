#!/usr/bin/env python3
"""
灵值生态园智能体 - 数据库连接工具
直接连接 SQLite 数据库并查看信息
"""

import sqlite3
import os
from datetime import datetime
from pathlib import Path

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(__file__), "auth.db")

class DatabaseConnector:
    """数据库连接器"""
    
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """连接数据库"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.cursor = self.conn.cursor()
            print(f"✓ 成功连接数据库: {self.db_path}")
            print(f"  数据库大小: {os.path.getsize(self.db_path) / 1024:.2f} KB")
            return True
        except Exception as e:
            print(f"✗ 连接数据库失败: {str(e)}")
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("✓ 数据库连接已关闭")
    
    def get_tables(self):
        """获取所有表"""
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = self.cursor.fetchall()
        return [table[0] for table in tables]
    
    def get_table_info(self, table_name: str):
        """获取表结构"""
        self.cursor.execute(f"PRAGMA table_info({table_name})")
        return self.cursor.fetchall()
    
    def get_table_count(self, table_name: str):
        """获取表记录数"""
        try:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = self.cursor.fetchone()[0]
            return count
        except:
            return 0
    
    def show_tables_info(self):
        """显示所有表的信息"""
        print("\n" + "="*80)
        print("📊 数据库表信息")
        print("="*80)
        
        tables = self.get_tables()
        print(f"\n总表数: {len(tables)}\n")
        
        print(f"{'表名':<30} {'记录数':<10} {'字段数':<10}")
        print("-" * 80)
        
        for table in tables:
            columns = self.get_table_info(table)
            count = self.get_table_count(table)
            print(f"{table:<30} {count:<10} {len(columns):<10}")
    
    def show_table_structure(self, table_name: str):
        """显示表结构"""
        print("\n" + "="*80)
        print(f"📋 表结构: {table_name}")
        print("="*80)
        
        columns = self.get_table_info(table_name)
        print(f"\n字段数: {len(columns)}\n")
        
        print(f"{'字段名':<25} {'类型':<15} {'非空':<8} {'默认值':<15}")
        print("-" * 80)
        
        for col in columns:
            cid, name, type_name, not_null, default, pk = col
            not_null_str = "✓" if not_null else " "
            default_str = str(default) if default else ""
            print(f"{name:<25} {type_name:<15} {not_null_str:<8} {default_str:<15}")
    
    def show_users(self):
        """显示用户信息"""
        print("\n" + "="*80)
        print("👥 用户信息")
        print("="*80)
        
        try:
            self.cursor.execute("""
                SELECT id, name, email, position, created_at, is_active
                FROM users
                LIMIT 20
            """)
            users = self.cursor.fetchall()
            
            if users:
                print(f"\n总用户数: {self.get_table_count('users')}\n")
                print(f"{'ID':<5} {'姓名':<15} {'邮箱':<25} {'职位':<15} {'创建时间'}")
                print("-" * 80)
                
                for user in users:
                    uid, name, email, position, created_at, is_active = user
                    created_str = datetime.fromisoformat(created_at).strftime("%Y-%m-%d") if created_at else ""
                    print(f"{uid:<5} {name:<15} {email:<25} {position:<15} {created_str}")
            else:
                print("暂无用户数据")
        except Exception as e:
            print(f"✗ 查询用户信息失败: {str(e)}")
    
    def show_roles(self):
        """显示角色信息"""
        print("\n" + "="*80)
        print("🎭 角色信息")
        print("="*80)
        
        try:
            self.cursor.execute("""
                SELECT id, name, english_name, level, description
                FROM roles
                ORDER BY level
            """)
            roles = self.cursor.fetchall()
            
            if roles:
                print(f"\n总角色数: {len(roles)}\n")
                print(f"{'ID':<5} {'角色名称':<15} {'英文名':<20} {'级别':<8} {'描述'}")
                print("-" * 80)
                
                for role in roles:
                    rid, name, eng_name, level, desc = role
                    print(f"{rid:<5} {name:<15} {eng_name:<20} {level:<8} {desc[:30]}")
            else:
                print("暂无角色数据")
        except Exception as e:
            print(f"✗ 查询角色信息失败: {str(e)}")
    
    def show_permissions(self):
        """显示权限信息"""
        print("\n" + "="*80)
        print("🔑 权限信息")
        print("="*80)
        
        try:
            self.cursor.execute("""
                SELECT id, code, name, description
                FROM permissions
                LIMIT 30
            """)
            permissions = self.cursor.fetchall()
            
            if permissions:
                total = self.get_table_count('permissions')
                print(f"\n总权限数: {total} (显示前30个)\n")
                print(f"{'ID':<5} {'权限代码':<25} {'权限名称':<20} {'描述'}")
                print("-" * 80)
                
                for perm in permissions:
                    pid, code, name, desc = perm
                    print(f"{pid:<5} {code:<25} {name:<20} {desc[:30]}")
            else:
                print("暂无权限数据")
        except Exception as e:
            print(f"✗ 查询权限信息失败: {str(e)}")
    
    def show_experts(self):
        """显示资源库专家信息"""
        print("\n" + "="*80)
        print("👨‍🏫 资源库专家信息")
        print("="*80)
        
        try:
            self.cursor.execute("""
                SELECT id, name, expertise, hourly_fee, contact_info
                FROM experts
                ORDER BY hourly_fee
            """)
            experts = self.cursor.fetchall()
            
            if experts:
                print(f"\n总专家数: {len(experts)}\n")
                print(f"{'ID':<5} {'专家姓名':<15} {'专长':<25} {'时薪(元)':<15} {'联系方式'}")
                print("-" * 80)
                
                for expert in experts:
                    eid, name, expertise, fee, contact = expert
                    print(f"{eid:<5} {name:<15} {expertise:<25} {fee:<15} {contact[:30]}")
            else:
                print("暂无专家数据")
        except Exception as e:
            print(f"✗ 查询专家信息失败: {str(e)}")


def main():
    """主函数"""
    print("="*80)
    print("灵值生态园智能体 - 数据库连接工具")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    # 创建连接器
    connector = DatabaseConnector()
    
    # 连接数据库
    if not connector.connect():
        return
    
    try:
        # 显示表信息
        connector.show_tables_info()
        
        # 显示用户信息
        connector.show_users()
        
        # 显示角色信息
        connector.show_roles()
        
        # 显示权限信息
        connector.show_permissions()
        
        # 显示专家信息
        connector.show_experts()
        
        # 显示数据库文件信息
        print("\n" + "="*80)
        print("💾 数据库文件信息")
        print("="*80)
        print(f"文件路径: {connector.db_path}")
        print(f"文件大小: {os.path.getsize(connector.db_path) / 1024:.2f} KB")
        print(f"修改时间: {datetime.fromtimestamp(os.path.getmtime(connector.db_path)).strftime('%Y-%m-%d %H:%M:%S')}")
        
        # 显示数据库版本
        connector.cursor.execute("SELECT sqlite_version()")
        version = connector.cursor.fetchone()[0]
        print(f"SQLite 版本: {version}")
        
    except Exception as e:
        print(f"\n✗ 执行查询时出错: {str(e)}")
    finally:
        # 关闭连接
        connector.close()


if __name__ == "__main__":
    main()
