#!/usr/bin/env python3
import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname, port, username, password)

# 查看旧数据库中的用户密码
script = '''#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect("/var/www/lingzhiapp/灵值生态园智能体移植包/src/auth/auth.db")
cursor = conn.cursor()

cursor.execute("SELECT name, password_hash FROM users")
users = cursor.fetchall()

print("Old database users:")
for user in users:
    name, password_hash = user
    print(f"Name: {name}")
    print(f"Password hash: {password_hash}")
    print(f"Hash length: {len(password_hash)}")
    print("-" * 40)

conn.close()
'''

sftp = ssh.open_sftp()
with sftp.file('/tmp/check_old_passwords.py', 'w') as f:
    f.write(script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/check_old_passwords.py')
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')

print(output)
if error:
    print(f"Error: {error}")

ssh.close()
