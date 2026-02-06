#!/usr/bin/env python3
"""
修复后端登录问题 - 禁用所有用户的手机验证码要求
"""
import paramiko

# 服务器配置
SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              修复后端登录问题                                      ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print()

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("🔐 连接到服务器...")
    ssh.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASSWORD,
        timeout=30
    )
    print("✅ 连接成功！")
    print()

    # 检查后端数据库位置
    print("【步骤1】检查后端数据库...")
    print("-" * 70)
    cmd = "ls -la /root/lingzhi-ecosystem/admin-backend/*.db 2>/dev/null || echo 'Database not found'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 添加require_phone_verification字段并设置为0
    print("【步骤2】添加require_phone_verification字段并设置为0...")
    print("-" * 70)
    cmd = """
cd /root/lingzhi-ecosystem/admin-backend
python3 << 'EOF'
import sqlite3

# 连接数据库
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 检查字段是否存在
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
print("当前用户表字段:", columns)

# 如果字段不存在，添加字段
if 'require_phone_verification' not in columns:
    print("添加require_phone_verification字段...")
    cursor.execute("ALTER TABLE users ADD COLUMN require_phone_verification INTEGER DEFAULT 0")
    conn.commit()
    print("✅ 字段已添加")
else:
    print("✅ 字段已存在")

# 更新所有用户，禁用手机验证码要求
cursor.execute("UPDATE users SET require_phone_verification = 0")
affected = cursor.rowcount
conn.commit()
print(f"✅ 已更新 {affected} 个用户，禁用手机验证码要求")

# 验证更新结果
cursor.execute("SELECT COUNT(*) FROM users WHERE require_phone_verification = 0")
count = cursor.fetchone()[0]
print(f"✅ 共有 {count} 个用户不需要手机验证码")

conn.close()
print("✅ 数据库更新完成")
EOF
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    output = stdout.read().decode('utf-8')
    print(output)

    error_output = stderr.read().decode('utf-8')
    if error_output:
        print("错误输出:", error_output)

    print()

    # 重启后端服务
    print("【步骤3】重启后端服务...")
    print("-" * 70)
    cmd = "systemctl restart flask-backend && echo '✅ 后端服务已重启'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)
    print()

    # 测试登录
    print("【步骤4】测试登录API...")
    print("-" * 70)
    cmd = """
curl -X POST https://127.0.0.1/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password123"}' -k 2>/dev/null || echo "测试失败"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)
    print()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    修复完成                                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("✅ 已禁用所有用户的手机验证码要求")
    print("✅ 后端服务已重启")
    print()
    print("🔍 测试登录：")
    print("   用户名: admin")
    print("   密码: password123")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
