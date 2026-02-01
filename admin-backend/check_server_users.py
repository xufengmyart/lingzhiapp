#!/usr/bin/env python3
"""
查看服务器数据库中的用户
"""

import paramiko

def check_users():
    """查看服务器用户"""

    hostname = '123.56.142.143'
    port = 22
    username = 'root'
    password = 'Meiyue@root123'

    print("=" * 80)
    print("查看服务器数据库用户")
    print("=" * 80)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(hostname, port, username, password)

        # 查看用户
        stdin, stdout, stderr = ssh.exec_command('''
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('/var/www/backend/lingzhi_ecosystem.db')
cursor = conn.cursor()

cursor.execute("SELECT id, username, role, created_at FROM users")
users = cursor.fetchall()

print("数据库中的用户:")
print("-" * 80)
for user in users:
    user_id, username, role, created_at = user
    print(f"ID: {user_id}, 用户名: {username}, 角色: {role}, 创建时间: {created_at}")

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
    check_users()
