#!/usr/bin/env python3
import paramiko
import bcrypt

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

print("=" * 80)
print("重置所有用户密码为 123456")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname, port, username, password)

    new_password = '123456'
    salt = bcrypt.gensalt()
    new_password_hash = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')

    print(f"\n生成新密码哈希...")
    print(f"新密码: {new_password}")
    print(f"哈希: {new_password_hash}")

    reset_script = f'''#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("/var/www/backend/lingzhi_ecosystem.db")
cursor = conn.cursor()

new_hash = "{new_password_hash}"

cursor.execute("UPDATE users SET password_hash = ?", (new_hash,))
affected = cursor.rowcount

conn.commit()

cursor.execute("SELECT username FROM users")
users = cursor.fetchall()

print(f"已重置 {affected} 个用户的密码")
print("用户列表:")
for user in users:
    print(f"  - {user[0]}")

conn.close()
'''

    sftp = ssh.open_sftp()
    with sftp.file('/tmp/reset_all_passwords.py', 'w') as f:
        f.write(reset_script)
    sftp.close()
    print("✅ 脚本已上传")

    print("\n执行重置...")
    stdin, stdout, stderr = ssh.exec_command('python3 /tmp/reset_all_passwords.py')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    print(output)
    if error:
        print(f"错误: {error}")

    print("\n验证登录...")
    stdin, stdout, stderr = ssh.exec_command(
        'curl -s -X POST http://localhost:8001/api/login -H "Content-Type: application/json" -d \'{"username":"许锋","password":"123456"}\' | python3 -m json.tool'
    )
    login_result = stdout.read().decode('utf-8')

    print("登录测试结果:")
    print(login_result)

    if '"success": true' in login_result:
        print("\n✅ 密码重置成功！可以正常登录了！")
    else:
        print("\n⚠️  登录测试失败")

    print("\n==========================================")
    print("✅ 全部完成！")
    print("==========================================")
    print(f"\n访问: http://123.56.142.143")
    print(f"所有用户密码: 123456")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
