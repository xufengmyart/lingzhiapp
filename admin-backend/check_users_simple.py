#!/usr/bin/env python3
import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect(hostname, port, username, password)

stdin, stdout, stderr = ssh.exec_command(
    'sqlite3 /var/www/backend/lingzhi_ecosystem.db "SELECT * FROM users"'
)
output = stdout.read().decode('utf-8')
print("users表数据:")
print(output)

stdin, stdout, stderr = ssh.exec_command(
    'sqlite3 /var/www/backend/lingzhi_ecosystem.db ".schema users"'
)
output = stdout.read().decode('utf-8')
print("\nusers表结构:")
print(output)

ssh.close()
