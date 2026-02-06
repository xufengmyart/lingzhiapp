#!/usr/bin/env python3
"""
使用正确的数据库修复admin账户
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              使用正确的数据库修复admin账户                           ║")
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

    # 列出 lingzhi_ecosystem.db 中的表
    print("【步骤1】列出 lingzhi_ecosystem.db 中的所有表...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 lingzhi_ecosystem.db '.tables'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 检查users表结构
    print("【步骤2】检查users表结构...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 lingzhi_ecosystem.db '.schema users'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 查看所有用户
    print("【步骤3】查看所有用户...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 lingzhi_ecosystem.db 'SELECT id, username, email, is_admin, require_phone_verification FROM users'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 创建admin账户（如果不存在）
    print("【步骤4】创建/更新admin账户...")
    print("-" * 70)
    cmd = """
cd /var/www/backend
python3 << 'PYTHON_EOF'
import bcrypt
import sqlite3

# 连接数据库
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 生成密码hash
password = "password123"
salt = bcrypt.gensalt()
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
print(f"密码Hash: {password_hash}")

# 检查admin是否存在
cursor.execute('SELECT id FROM users WHERE username=?', ('admin',))
result = cursor.fetchone()

if result:
    print(f"admin账户已存在，ID: {result[0]}")
    # 更新admin账户
    cursor.execute('''
        UPDATE users SET 
        password = ?,
        email = 'admin@lingzhi.com',
        require_phone_verification = 0
        WHERE username = ?
    ''', (password_hash, 'admin'))
    print("✅ admin账户已更新")
else:
    print("admin账户不存在，创建新账户...")
    # 创建admin账户
    cursor.execute('''
        INSERT INTO users (username, password, email, is_admin, require_phone_verification)
        VALUES (?, ?, ?, 1, 0)
    ''', ('admin', password_hash, 'admin@lingzhi.com'))
    print("✅ admin账户已创建")

conn.commit()
conn.close()
PYTHON_EOF
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))
    print()

    # 验证admin账户
    print("【步骤5】验证admin账户...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 lingzhi_ecosystem.db 'SELECT id, username, email, is_admin, require_phone_verification FROM users WHERE username=\"admin\"'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 测试登录
    print("【步骤6】测试登录...")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)
    print()

    # 测试HTTPS登录
    print("【步骤7】测试HTTPS登录...")
    print("-" * 70)
    cmd = """curl -s -X POST https://127.0.0.1/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password123"}' -k"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)
    print()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    修复完成                                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
