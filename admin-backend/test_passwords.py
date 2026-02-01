#!/usr/bin/env python3
"""
测试常见密码是否匹配
"""

import paramiko
import bcrypt

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

print("=" * 80)
print("测试常见密码")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname, port, username, password)

    # 获取新数据库中的密码哈希
    get_hash_script = '''#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("/var/www/backend/lingzhi_ecosystem.db")
cursor = conn.cursor()

cursor.execute("SELECT username, password_hash FROM users WHERE username = '许锋'")
user = cursor.fetchone()

if user:
    print(user[1])
else:
    print("User not found")

conn.close()
'''

    sftp = ssh.open_sftp()
    with sftp.file('/tmp/get_hash.py', 'w') as f:
        f.write(get_hash_script)
    sftp.close()

    stdin, stdout, stderr = ssh.exec_command('python3 /tmp/get_hash.py')
    password_hash = stdout.read().decode('utf-8').strip()

    print(f"\n密码哈希: {password_hash}")

    # 测试常见密码
    common_passwords = [
        '123456',
        'admin',
        'admin123',
        'password',
        '123456789',
        '111111',
        'xufeng',
        'meiyue',
    ]

    print("\n测试常见密码:")
    print("-" * 80)

    for test_pwd in common_passwords:
        try:
            if bcrypt.checkpw(test_pwd.encode('utf-8'), password_hash.encode('utf-8')):
                print(f"✅ 找到密码: {test_pwd}")
                print(f"\n==========================================")
                print(f"✅ 登录凭证")
                print(f"==========================================")
                print(f"用户名: 许锋")
                print(f"密码: {test_pwd}")
                print(f"\n访问: http://123.56.142.143")
                break
            else:
                print(f"❌ {test_pwd}")
        except Exception as e:
            print(f"❌ {test_pwd} (错误: {e})")
    else:
        print("\n没有找到匹配的常见密码")
        print("\n建议:")
        print("1. 直接重置密码为 123456")
        print("2. 或者联系用户获取正确的密码")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
