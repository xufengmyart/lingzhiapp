#!/usr/bin/env python3
"""
检查完整的数据库结构
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              检查完整的数据库结构                                  ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print()

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

    # 获取所有schema
    print("【步骤1】获取所有表结构...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 lingzhi_ecosystem.db '.schema'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 查看所有表
    print("【步骤2】列出所有表...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 lingzhi_ecosystem.db '.tables'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
