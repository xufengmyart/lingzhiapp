#!/usr/bin/env python3
"""
查看服务器数据库表结构
"""

import paramiko

def check_db_structure():
    """查看数据库结构"""

    hostname = '123.56.142.143'
    port = 22
    username = 'root'
    password = 'Meiyue@root123'

    print("=" * 80)
    print("查看数据库结构")
    print("=" * 80)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, port, username, password)

        # 查看表结构
        stdin, stdout, stderr = ssh.exec_command('''
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('/var/www/backend/lingzhi_ecosystem.db')
cursor = conn.cursor()

# 查看所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("数据库中的表:")
print("-" * 80)
for table in tables:
    print(f"表名: {table[0]}")

print("\n" + "=" * 80)
print("users表结构:")
print("-" * 80)
cursor.execute("PRAGMA table_info(users)")
columns = cursor.fetchall()
for col in columns:
    print(col)

print("\n" + "=" * 80)
print("users表数据:")
print("-" * 80)
cursor.execute("SELECT * FROM users")
users = cursor.fetchall()
for user in users:
    print(user)

conn.close()
EOF
''')

        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        print(output)
        if error:
            print(f"错误: {error}")

    except Exception as e:
        print(f"错误: {e}")
    finally:
        ssh.close()

if __name__ == '__main__':
    check_db_structure()
