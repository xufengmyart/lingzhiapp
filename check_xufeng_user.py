#!/usr/bin/env python3
"""
检查数据库中的所有用户
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

    print("【查看所有用户】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db 'SELECT id, username, email, phone, is_admin, is_verified, is_active, require_phone_verification FROM users;'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    print("\n【搜索许锋用户】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db \"SELECT * FROM users WHERE username LIKE '%许%' OR username LIKE '%锋%';\""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    print("\n【查看users表结构】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db '.schema users'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
