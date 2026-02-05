#!/usr/bin/env python3
"""
测试HTTPS访问
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              测试HTTPS访问                                        ║")
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

    # 测试HTTPS访问
    print("【测试】HTTPS本地访问")
    print("-" * 70)
    cmd = "curl -I https://127.0.0.1/ -k 2>&1"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 检查Nginx配置
    print()
    print("【检查】Nginx配置")
    print("-" * 70)
    cmd = "cat /etc/nginx/sites-enabled/default | grep -A 20 'location /'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 检查SSL证书
    print()
    print("【检查】SSL证书状态")
    print("-" * 70)
    cmd = "ls -la /etc/letsencrypt/live/ 2>/dev/null || echo 'No SSL certificates found'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 检查Nginx错误日志
    print()
    print("【检查】Nginx错误日志（最后10行）")
    print("-" * 70)
    cmd = "tail -10 /var/log/nginx/error.log"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
