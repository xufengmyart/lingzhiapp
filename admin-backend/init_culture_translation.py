#!/usr/bin/env python3
"""
执行文化转译数据库表创建脚本
"""

import sqlite3
import json
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'lingzhi_ecosystem.db')

def execute_sql_file(sql_file_path):
    """执行SQL文件"""
    print(f"📂 读取SQL文件: {sql_file_path}")

    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_content = f.read()

    print(f"📝 SQL内容长度: {len(sql_content)} 字符")

    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # 更智能的SQL分割：支持 CREATE TABLE 语句
        statements = []
        current_statement = []
        in_create_table = False
        paren_count = 0

        for line in sql_content.split('\n'):
            line = line.strip()
            if not line or line.startswith('--'):
                continue

            current_statement.append(line)

            # 检测 CREATE TABLE 语句
            if 'CREATE TABLE' in line.upper():
                in_create_table = True

            # 计算括号数量
            if in_create_table:
                paren_count += line.count('(')
                paren_count -= line.count(')')

            # 如果括号平衡且语句以分号结尾，则结束
            if not in_create_table and line.endswith(';'):
                statement = ' '.join(current_statement)
                statements.append(statement)
                current_statement = []
            elif in_create_table and paren_count == 0 and line.endswith(';'):
                statement = '\n'.join(current_statement)
                statements.append(statement)
                current_statement = []
                in_create_table = False
                paren_count = 0

        print(f"🔍 找到 {len(statements)} 条SQL语句")

        # 执行每条语句
        success_count = 0
        error_count = 0
        for i, stmt in enumerate(statements, 1):
            try:
                print(f"⚙️  执行第 {i}/{len(statements)} 条语句... (长度: {len(stmt)} 字符)")
                cursor.execute(stmt)
                success_count += 1
                print(f"   ✅ 成功")
            except Exception as e:
                error_count += 1
                print(f"   ❌ 失败: {e}")
                if i < 5:  # 打印前5个失败的语句
                    print(f"   语句内容: {stmt[:200]}...")

        conn.commit()
        print(f"\n🎉 执行完成！成功: {success_count}, 失败: {error_count}/{len(statements)}")

        # 验证表是否创建成功
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'translation%'")
        tables = cursor.fetchall()
        print(f"\n📋 创建的转译相关表: {len(tables)}")
        for table in tables:
            print(f"   - {table[0]}")

        # 验证项目数据
        cursor.execute("SELECT COUNT(*) FROM translation_projects")
        project_count = cursor.fetchone()[0]
        print(f"\n📦 转译项目数量: {project_count}")

        if project_count > 0:
            cursor.execute("SELECT project_code, title FROM translation_projects")
            projects = cursor.fetchall()
            print("   项目列表:")
            for project in projects:
                print(f"   - {project[0]}: {project[1]}")

    except Exception as e:
        print(f"❌ 执行SQL文件失败: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()

if __name__ == '__main__':
    sql_file = os.path.join(os.path.dirname(__file__), 'database_culture_translation.sql')
    if os.path.exists(sql_file):
        execute_sql_file(sql_file)
    else:
        print(f"❌ SQL文件不存在: {sql_file}")
