#!/usr/bin/env python3
"""
检查后端登录代码
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              检查后端登录代码                                    ║")
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

    # 查看登录API代码
    print("\n【查看登录API代码】")
    print("-" * 70)
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && grep -A 30 '@app.route.*login' app.py | head -50"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 检查许锋账号的状态
    print("\n【检查许锋账号的完整信息】")
    print("-" * 70)
    cmd = """cd /root/lingzhi-ecosystem/admin-backend && python3 -c "
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM users WHERE username = ?', ('许锋',))
row = cursor.fetchone()
if row:
    print('许锋账号完整信息:')
    print(row)
    print()
    print('字段说明:')
    cursor.execute('PRAGMA table_info(users)')
    columns = cursor.fetchall()
    for i, col in enumerate(columns):
        print(f'  {i}: {col[1]} ({col[2]})')
conn.close()
"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
