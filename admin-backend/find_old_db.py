#!/usr/bin/env python3
import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname, port, username, password)

# 查找旧数据库
stdin, stdout, stderr = ssh.exec_command('find /var/www -name "auth.db" 2>/dev/null')
output = stdout.read().decode('utf-8')
print("查找旧数据库文件:")
print(output)

# 查看后端目录下的数据库文件
stdin, stdout, stderr = ssh.exec_command('find /var/www/backend -name "*.db" 2>/dev/null')
output = stdout.read().decode('utf-8')
print("\n后端目录下的数据库文件:")
print(output)

ssh.close()
