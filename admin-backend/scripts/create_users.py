#!/usr/bin/env python3
"""
创建和管理用户数据
"""

import paramiko
import bcrypt

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

# 原用户列表
original_users = [
    {
        'username': 'admin',
        'password': 'admin123',
        'email': 'admin@lingzhi.com',
        'phone': '',
        'real_name': '系统管理员',
        'total_lingzhi': 10000
    },
    {
        'username': '许锋',
        'password': 'lingzhi123',
        'email': 'xufeng@lingzhi.com',
        'phone': '',
        'real_name': '许锋',
        'total_lingzhi': 5000
    },
    {
        'username': 'testuser',
        'password': 'test123',
        'email': 'test@lingzhi.com',
        'phone': '13800138888',
        'real_name': '测试用户',
        'total_lingzhi': 100
    }
]

print("=" * 80)
print("灵值生态园 - 用户数据恢复")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # 连接服务器
    print(f"\n[1/3] 连接到服务器...")
    ssh.connect(hostname, port, username, password)
    print("✅ 连接成功")

    # 创建用户
    print(f"\n[2/3] 创建原用户...")
    for user_data in original_users:
        print(f"\n创建用户: {user_data['username']}")

        # 生成bcrypt密码
        password_hash = bcrypt.hashpw(user_data['password'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        # 在服务器上执行创建用户的SQL
        sql = f'''
        INSERT OR REPLACE INTO users (
            username, email, phone, password_hash, real_name, total_lingzhi,
            login_type, current_stage, phone_bound, created_at
        ) VALUES (
            '{user_data['username']}',
            '{user_data['email']}',
            '{user_data['phone']}',
            '{password_hash}',
            '{user_data['real_name']}',
            {user_data['total_lingzhi']},
            'password',
            'ecosystem_holder',
            1,
            CURRENT_TIMESTAMP
        );
        '''

        stdin, stdout, stderr = ssh.exec_command(
            f"cd /var/www/backend && python3 -c \"import sqlite3; conn = sqlite3.connect('lingzhi_ecosystem.db'); cursor = conn.cursor(); cursor.execute('''{sql}'''); conn.commit(); print('用户创建成功')\""
        )
        result = stdout.read().decode('utf-8')
        print(f"  {result}")

    # 验证用户
    print(f"\n[3/3] 验证用户...")
    stdin, stdout, stderr = ssh.exec_command(
        "cd /var/www/backend && python3 -c \"import sqlite3; conn = sqlite3.connect('lingzhi_ecosystem.db'); cursor = conn.cursor(); cursor.execute('SELECT id, username, email, total_lingzhi FROM users ORDER BY id'); print(cursor.fetchall())\""
    )
    result = stdout.read().decode('utf-8')
    print(result)

    print("\n" + "=" * 80)
    print("✅ 用户数据恢复完成！")
    print("=" * 80)
    print("\n可用的登录账号:")
    for user in original_users:
        print(f"  - 用户名: {user['username']}, 密码: {user['password']}")

except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
