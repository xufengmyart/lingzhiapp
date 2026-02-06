#!/usr/bin/env python3
"""
检查数据库用户
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

    # 1. 查看数据库中的用户
    print("【查看数据库用户】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db 'SELECT id, username, email, is_admin FROM users LIMIT 10;'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 2. 查看管理员用户
    print("\n【查看管理员用户】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && sqlite3 lingzhi_ecosystem.db 'SELECT id, username, email, is_admin FROM users WHERE is_admin=1;'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 3. 测试不同密码
    print("\n【测试admin/admin123】")
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    print("\n【测试admin/password123】")
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
