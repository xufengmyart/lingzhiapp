#!/usr/bin/env python3
"""
重置许锋账号密码
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              重置许锋账号密码                                      ║")
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

    # 重置许锋账号密码
    print("\n【重置许锋账号密码】")
    print("-" * 70)

    cmd = """cd /root/lingzhi-ecosystem/admin-backend && python3 -c "
import sqlite3
import bcrypt

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 查询许锋账号信息
cursor.execute('SELECT id, username, phone, email FROM users WHERE username = ?', ('许锋',))
user = cursor.fetchone()

if user:
    print('✅ 找到许锋账号')
    print(f'   ID: {user[0]}')
    print(f'   用户名: {user[1]}')
    print(f'   手机: {user[2]}')
    print(f'   邮箱: {user[3]}')

    # 重置密码
    new_password = 'password123'
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('UPDATE users SET password = ? WHERE username = ?', (hashed, '许锋'))
    conn.commit()
    print(f'✅ 密码已重置为: {new_password}')
else:
    print('❌ 未找到许锋账号')

    # 如果不存在，创建一个
    new_password = 'password123'
    hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute('''
        INSERT INTO users (username, phone, email, password, is_verified, login_type)
        VALUES (?, ?, ?, ?, 1, 'phone')
    ''', ('许锋', '13800138001', 'xufeng@meiyueart.com', hashed))
    conn.commit()
    print('✅ 许锋账号创建成功')
    print(f'   密码: {new_password}')

conn.close()
"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 测试登录
    print("\n【测试许锋账号登录】")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"许锋","password":"password123"}' | python3 -m json.tool"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    if '"success": true' in output:
        print("\n✅ 许锋账号登录成功！")
    else:
        print("\n❌ 许锋账号登录失败")

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                      密码重置完成                                ║")
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
