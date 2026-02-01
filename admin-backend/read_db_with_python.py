#!/usr/bin/env python3
import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname, port, username, password)

# 用Python读取数据库
script = '''
import sqlite3
import os

db_path = '/var/www/backend/lingzhi_ecosystem.db'

print("数据库文件大小:", os.path.getsize(db_path), "bytes")
print("数据库文件是否存在:", os.path.exists(db_path))

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 列出所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("表数量:", len(tables))
    for table in tables:
        print(f"表: {table[0]}")

    # 如果有users表，查看数据
    if any('user' in str(t).lower() for t in tables):
        cursor.execute("SELECT * FROM users LIMIT 10")
        users = cursor.fetchall()
        print("用户数据:")
        for user in users:
            print(user)

    conn.close()
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
'''

stdin, stdout, stderr = ssh.exec_command(f'python3 -c "{script}"')
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')

print(output)
if error:
    print(f"错误: {error}")

ssh.close()
