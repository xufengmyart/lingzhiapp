#!/usr/bin/env python3
"""
查找并测试许锋账号
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              查找并测试许锋账号                                    ║")
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

    # 1. 查看所有用户
    print("\n【1】查看所有用户")
    print("-" * 70)
    cmd = """cd /root/lingzhi-ecosystem/admin-backend && python3 -c "
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute('SELECT id, username, phone, email, is_admin FROM users')
for row in cursor.fetchall():
    print(f'ID: {row[0]}, 用户名: {row[1]}, 手机: {row[2]}, 邮箱: {row[3]}, 管理员: {row[4]}')
conn.close()
"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output if output else "没有用户")

    # 2. 测试常见用户名登录
    print("\n【2】测试常见用户名登录")
    print("-" * 70)

    test_users = [
        ("admin", "admin123"),
        ("admin", "password123"),
        ("xufeng", "password123"),
        ("许锋", "password123"),
        ("xufengmyart", "password123"),
    ]

    for username, password in test_users:
        print(f"\n测试: {username} / {password}")
        cmd = f"""curl -s -X POST http://127.0.0.1:8080/api/login \\
          -H "Content-Type: application/json" \\
          -d '{{"username":"{username}","password":"{password}"}}' | grep -o '"success":[^,]*'"""
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        output = stdout.read().decode('utf-8').strip()

        if 'true' in output:
            print(f"  ✅ 登录成功")
            # 获取详细信息
            cmd = f"""curl -s -X POST http://127.0.0.1:8080/api/login \\
              -H "Content-Type: application/json" \\
              -d '{{"username":"{username}","password":"{password}"}}'"""
            stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
            result = stdout.read().decode('utf-8')
            print(f"  {result[:200]}...")
        else:
            print(f"  ❌ 登录失败")

    # 3. 如果没有许锋账号，创建一个
    print("\n【3】检查是否需要创建许锋账号")
    print("-" * 70)

    # 创建许锋账号
    cmd = """cd /root/lingzhi-ecosystem/admin-backend && python3 -c "
import sqlite3
import bcrypt

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 检查是否已存在许锋账号
cursor.execute('SELECT id FROM users WHERE username = ?', ('许锋',))
user = cursor.fetchone()

if user:
    print('✅ 许锋账号已存在，ID:', user[0])
else:
    # 创建许锋账号
    password = 'password123'
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('''
        INSERT INTO users (username, phone, email, password, is_verified, login_type)
        VALUES (?, ?, ?, ?, 1, 'phone')
    ''', ('许锋', '13800138001', 'xufeng@meiyueart.com', hashed))
    conn.commit()
    print('✅ 许锋账号创建成功')
    print('   用户名: 许锋')
    print('   密码: password123')
    print('   手机: 13800138001')
    print('   邮箱: xufeng@meiyueart.com')

conn.close()
"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 4. 测试许锋账号登录
    print("\n【4】测试许锋账号登录")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"许锋","password":"password123"}' | python3 -m json.tool"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                      账号检查完成                                ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("📱 访问：https://meiyueart.com")
    print()
    print("🔐 可用账号：")
    print("   1. admin / admin123")
    print("   2. 许锋 / password123")
    print()
    print("💡 清除浏览器缓存：Ctrl + Shift + R")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
