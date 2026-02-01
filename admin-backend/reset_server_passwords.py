#!/usr/bin/env python3
"""
重置服务器上的用户密码为123456
"""

import paramiko
import bcrypt

def reset_passwords_on_server():
    """连接服务器并重置用户密码"""

    hostname = '123.56.142.143'
    port = 22
    username = 'root'
    password = 'Meiyue@root123'

    print("=" * 80)
    print("开始重置服务器用户密码")
    print("=" * 80)

    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 连接服务器
        print(f"\n[1/3] 连接到服务器...")
        ssh.connect(hostname, port, username, password)
        print("✅ 连接成功")

        # 生成密码哈希
        new_password = '123456'
        salt = bcrypt.gensalt()
        new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

        print(f"\n[2/3] 重置用户密码...")
        print(f"  新密码: {new_password}")
        print(f"  密码哈希: {new_password_hash}")

        # 创建Python脚本来重置密码
        reset_script = f'''#!/usr/bin/env python3
import sqlite3
import bcrypt

conn = sqlite3.connect('/var/www/backend/lingzhi_ecosystem.db')
cursor = conn.cursor()

# 新密码哈希
new_password_hash = '{new_password_hash}'

# 重置用户密码
users_to_reset = ['许锋', 'CTO（待定）', 'CMO（待定）', 'COO（待定）', 'CFO（待定）']

count = 0
for user_name in users_to_reset:
    cursor.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (new_password_hash, user_name)
    )
    affected = cursor.rowcount
    if affected > 0:
        count += 1
        print(f"  ✅ 已重置用户 {{user_name}} 的密码")

conn.commit()
conn.close()

print(f"  ✅ 共重置 {{count}} 个用户的密码")
'''

        # 执行脚本
        stdin, stdout, stderr = ssh.exec_command(reset_script)
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')

        print(output)
        if error:
            print(f"错误: {error}")

        # 验证登录
        print(f"\n[3/3] 验证登录...")
        stdin, stdout, stderr = ssh.exec_command(
            'curl -s -X POST http://localhost:8001/api/login -H "Content-Type: application/json" -d \'{"username":"许锋","password":"123456"}\' | python3 -m json.tool'
        )
        login_result = stdout.read().decode('utf-8')

        print("登录测试结果:")
        print(login_result)

        if '"success": true' in login_result:
            print("\n✅ 密码重置成功！")
        else:
            print("\n⚠️  登录测试失败，请检查")

        print("\n==========================================")
        print("✅ 全部完成！")
        print("==========================================")
        print(f"\n访问: http://123.56.142.143")
        print(f"用户名: 许锋")
        print(f"密码: 123456")

        return True

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        return False

    finally:
        ssh.close()

if __name__ == '__main__':
    reset_passwords_on_server()
