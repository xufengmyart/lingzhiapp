#!/usr/bin/env python3
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PASSWORD = "Meiyue@root123"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname=SERVER_HOST, port=22, username=SERVER_USER, password=SERVER_PASSWORD, timeout=30)
    
    print("检查数据库文件完整性...")
    cmd = "cd /var/www/backend && ls -la *.db"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    
    print("\n检查最新备份文件...")
    cmd = "ls -lt /var/www/backend/backups/*.db | head -5"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    
    print("\n检查数据库是否损坏...")
    cmd = "cd /var/www/backend && sqlite3 lingzhi_ecosystem.db '.tables'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    
    print("\n尝试检查完整性...")
    cmd = "cd /var/www/backend && sqlite3 lingzhi_ecosystem.db 'PRAGMA integrity_check;'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

except Exception as e:
    print(f"错误: {e}")
finally:
    ssh.close()
