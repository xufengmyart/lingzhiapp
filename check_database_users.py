#!/usr/bin/env python3
"""
检查数据库和用户
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASSWORD,
        timeout=30
    )

    # 1. 查看数据库位置
    print("【1】数据库位置】")
    cmd = "ls -lh /root/lingzhi-ecosystem/admin-backend/*.db"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    # 2. 查看users表
    print("\n【2】查看users表】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db 'SELECT id, username, email, is_admin, require_phone_verification FROM users LIMIT 10;'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 3. 搜索许锋
    print("\n【3】搜索许锋】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db \"SELECT id, username, email, is_admin, require_phone_verification FROM users WHERE username LIKE '%许%' OR username LIKE '%feng%';\""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 4. 查看表结构
    print("\n【4】users表结构】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db '.schema users'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
