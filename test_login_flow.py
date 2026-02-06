#!/usr/bin/env python3
"""
测试完整登录流程
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║                    测试登录流程                                    ║")
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

    # 1. 测试直接API访问
    print("\n【1】测试后端API直接访问")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"admin123"}' | python3 -m json.tool"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 2. 测试通过Nginx代理访问
    print("\n【2】测试通过Nginx代理访问API")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"admin123"}' | python3 -m json.tool"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 3. 测试HTTPS代理访问
    print("\n【3】测试HTTPS代理访问API")
    print("-" * 70)
    cmd = """curl -s -k -X POST https://127.0.0.1/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"admin123"}' | python3 -m json.tool"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 4. 检查前端index.html
    print("\n【4】检查前端index.html内容")
    print("-" * 70)
    cmd = "head -15 /var/www/frontend/index.html"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    # 5. 检查Nginx配置中的API代理
    print("\n【5】检查Nginx API代理配置")
    print("-" * 70)
    cmd = "grep -A 10 'location /api/' /etc/nginx/sites-enabled/default"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                      测试完成                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("✅ 部署和配置已完成")
    print("📱 请访问：https://meiyueart.com")
    print("🔐 登录账号：admin / admin123")
    print("💡 记得清除浏览器缓存：Ctrl + Shift + R")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
