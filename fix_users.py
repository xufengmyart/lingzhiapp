#!/usr/bin/env python3
"""
检查并修复用户登录问题
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              检查并修复用户登录问题                              ║")
print("╚══════════════════════════════════════════════════════════════════╝")

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

    # 1. 检查数据库
    print("\n【1】检查数据库文件")
    cmd = "ls -lh /root/lingzhi-ecosystem/admin-backend/*.db"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    # 2. 查看所有用户
    print("\n【2】查看所有用户")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db \"SELECT id, username, phone, email FROM users;\""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output if output else "没有找到用户")

    # 3. 搜索许锋
    print("\n【3】搜索许锋用户")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db \"SELECT * FROM users WHERE username LIKE '%许锋%' OR username LIKE '%xufeng%' OR phone LIKE '%许%';\""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output if output else "没有找到许锋")

    # 4. 查看表结构
    print("\n【4】查看users表结构")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db \".schema users\""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 5. 测试登录
    print("\n【5】测试admin登录")
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"admin123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
