#!/usr/bin/env python3
import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname, port, username, password)

# 检查后端代码
stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/backend/ | head -30')
output = stdout.read().decode('utf-8')
print("后端目录内容:")
print(output)

# 检查数据库文件
stdin, stdout, stderr = ssh.exec_command('ls -la /var/www/backend/*.db')
output = stdout.read().decode('utf-8')
print("\n数据库文件:")
print(output)

# 检查数据库文件大小
stdin, stdout, stderr = ssh.exec_command('wc -c /var/www/backend/lingzhi_ecosystem.db')
output = stdout.read().decode('utf-8')
print("\n数据库文件大小:")
print(output)

ssh.close()
