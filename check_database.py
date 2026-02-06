#!/usr/bin/env python3
"""
检查数据库结构并修复
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              检查数据库结构并修复                                  ║")
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

    # 列出所有表
    print("【步骤1】列出数据库中的所有表...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 eco_garden.db '.tables'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 检查数据库文件
    print("【步骤2】检查数据库文件...")
    print("-" * 70)
    cmd = "ls -la /var/www/backend/eco_garden.db"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 检查后端代码中的数据库路径
    print("【步骤3】检查后端代码中的数据库路径...")
    print("-" * 70)
    cmd = "grep -n 'DATABASE\|eco_garden.db' /var/www/backend/app.py | head -10"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 检查是否有其他数据库文件
    print("【步骤4】查找所有数据库文件...")
    print("-" * 70)
    cmd = "find /var/www/backend -name '*.db' -o -name '*.sqlite' -o -name '*.sqlite3' 2>/dev/null"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 检查后端启动日志
    print("【步骤5】检查后端启动日志...")
    print("-" * 70)
    cmd = "journalctl -u eco-backend -n 50 --no-pager | tail -30"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
