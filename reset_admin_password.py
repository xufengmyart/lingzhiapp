#!/usr/bin/env python3
"""
检查admin账户和重置密码
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              检查admin账户并重置密码                                ║")
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

    # 检查admin账户
    print("【步骤1】检查admin账户...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 eco_garden.db 'SELECT id, username, password, is_admin, require_phone_verification FROM users WHERE username=\"admin\"'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 检查所有用户
    print("【步骤2】列出所有用户...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 eco_garden.db 'SELECT id, username, email, is_admin, require_phone_verification FROM users'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 重置admin密码为 password123 (使用BCrypt)
    print("【步骤3】重置admin密码...")
    print("-" * 70)
    cmd = """
cd /var/www/backend
python3 << 'PYTHON_EOF'
import bcrypt

# 生成密码hash
password = "password123"
salt = bcrypt.gensalt()
password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
print(f"密码Hash: {password_hash}")
print(f"Salt: {salt.decode('utf-8')}")

# 更新数据库
import sqlite3
conn = sqlite3.connect('eco_garden.db')
cursor = conn.cursor()
cursor.execute('UPDATE users SET password=? WHERE username=?', (password_hash, 'admin'))
conn.commit()
print(f"更新了 {cursor.rowcount} 行")
conn.close()
print("✅ 密码已重置为: password123")
PYTHON_EOF
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    print(stdout.read().decode('utf-8'))
    print(stderr.read().decode('utf-8'))
    print()

    # 验证密码
    print("【步骤4】验证密码...")
    print("-" * 70)
    cmd = "cd /var/www/backend && sqlite3 eco_garden.db 'SELECT username, password FROM users WHERE username=\"admin\"'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 测试登录
    print("【步骤5】测试登录...")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)
    print()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    检查完成                                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
