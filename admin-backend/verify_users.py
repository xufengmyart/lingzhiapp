#!/usr/bin/env python3
import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname, port, username, password)

verify_script = '''#!/usr/bin/env python3
import sqlite3
conn = sqlite3.connect("/var/www/backend/lingzhi_ecosystem.db")
cursor = conn.cursor()
cursor.execute("SELECT id, username, email, phone, total_lingzhi FROM users")
users = cursor.fetchall()
print("Users:", len(users))
for user in users:
    print(user)
conn.close()
'''

sftp = ssh.open_sftp()
with sftp.file('/tmp/verify_users.py', 'w') as f:
    f.write(verify_script)
sftp.close()

stdin, stdout, stderr = ssh.exec_command('python3 /tmp/verify_users.py')
output = stdout.read().decode('utf-8')
error = stderr.read().decode('utf-8')

print(output)
if error:
    print(f"Error: {error}")

ssh.close()
