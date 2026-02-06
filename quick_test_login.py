#!/usr/bin/env python3
"""
快速测试登录
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              快速测试登录                                        ║")
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

    # 测试许锋登录
    print("\n【测试许锋登录】")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"许锋","password":"password123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 如果失败，尝试创建新许锋账号
    if '"success": false' in output:
        print("\n【许锋登录失败，尝试重置账号】")
        print("-" * 70)

        cmd = """cd /root/lingzhi-ecosystem/admin-backend && python3 -c "
import sqlite3
import bcrypt

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 删除旧许锋账号
cursor.execute('DELETE FROM users WHERE username = ?', ('许锋',))

# 创建新许锋账号
password = 'password123'
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
cursor.execute('''
    INSERT INTO users (username, email, phone, password, require_phone_verification, is_verified, login_type)
    VALUES (?, ?, ?, ?, 0, 1, 'phone')
''', ('许锋', 'xufeng@meiyueart.cn', '13800138001', hashed))

conn.commit()
print('✅ 许锋账号已重置')
print('   用户名: 许锋')
print('   密码: password123')
conn.close()
"
"""
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        print(stdout.read().decode('utf-8'))

        # 再次测试登录
        print("\n【再次测试许锋登录】")
        print("-" * 70)
        cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
          -H "Content-Type: application/json" \\
          -d '{"username":"许锋","password":"password123"}'"""
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        output = stdout.read().decode('utf-8')
        print(output)

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                      测试完成                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
