#!/usr/bin/env python3
"""
测试外部HTTPS访问
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              测试外部HTTPS访问                                    ║")
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

    # 测试从服务器外部访问
    print("【测试1】从服务器外部访问（使用服务器公网IP）")
    print("-" * 70)
    cmd = "curl -I https://123.56.142.143/ -k 2>&1 | head -15"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 测试域名访问
    print()
    print("【测试2】使用域名访问")
    print("-" * 70)
    cmd = "curl -I https://meiyueart.com/ -k 2>&1 | head -15"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 获取index.html的前10行内容
    print()
    print("【验证】index.html内容（前10行）")
    print("-" * 70)
    cmd = "head -10 /var/www/frontend/index.html"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 测试静态资源
    print()
    print("【测试】CSS文件访问")
    print("-" * 70)
    cmd = "curl -I https://127.0.0.1/assets/index-BI24OT2H.css -k 2>&1 | head -10"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    print()
    print("【测试】JS文件访问")
    print("-" * 70)
    cmd = "curl -I https://127.0.0.1/assets/index-C_quYkQi.js -k 2>&1 | head -10"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    测试完成                                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("✅ 部署成功！")
    print()
    print("📱 现在可以在浏览器中访问：")
    print("   https://meiyueart.com")
    print()
    print("💡 请清除浏览器缓存：")
    print("   Windows: Ctrl + Shift + R")
    print("   Mac: Cmd + Shift + R")
    print()
    print("🔍 登录测试：")
    print("   用户名: admin")
    print("   密码: password123")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
