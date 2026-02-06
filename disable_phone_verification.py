#!/usr/bin/env python3
"""
禁用许锋账号的手机验证要求
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║          禁用许锋账号的手机验证要求                              ║")
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

    # 禁用手机验证要求
    print("\n【禁用手机验证要求】")
    print("-" * 70)

    cmd = """cd /root/lingzhi-ecosystem/admin-backend && python3 -c "
import sqlite3

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 更新许锋账号，禁用手机验证
cursor.execute('UPDATE users SET require_phone_verification = 0 WHERE username = ?', ('许锋',))
conn.commit()

print('✅ 已禁用许锋账号的手机验证要求')

# 验证更新
cursor.execute('SELECT username, require_phone_verification FROM users WHERE username = ?', ('许锋',))
result = cursor.fetchone()
print(f'   用户名: {result[0]}')
print(f'   手机验证要求: {result[1]} (0=不需要, 1=需要)')

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

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
