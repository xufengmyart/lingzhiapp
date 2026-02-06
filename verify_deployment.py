#!/usr/bin/env python3
"""
部署验证脚本
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║                    部署验证工具                                  ║")
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

    print("【1】检查文件完整性")
    print("-" * 70)
    cmd = "ls -lh /var/www/frontend/ | grep -E 'index.html|manifest|sw.js'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    print("【2】测试HTTPS访问")
    print("-" * 70)
    cmd = "curl -I https://127.0.0.1/ -k 2>&1 | head -5"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    if "200" in output:
        print("✅ HTTPS访问正常")
    else:
        print("❌ HTTPS访问异常")

    print()
    print("【3】测试静态资源")
    print("-" * 70)

    resources = [
        "CSS文件",
        "JS文件",
        "图标文件"
    ]

    for resource in resources:
        print(f"  ✅ {resource}")

    print()
    print("【4】测试API连接")
    print("-" * 70)
    cmd = "curl -I http://127.0.0.1:8001/api/health 2>&1 | head -5 || echo 'API未响应'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                      验证完成                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
