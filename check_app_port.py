#!/usr/bin/env python3
"""
检查app.py端口配置并启动
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

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

    # 1. 查看app.py的端口配置
    print("【检查端口配置】")
    cmd = "grep -n 'app.run\\|port\\|PORT\\|8001' /root/lingzhi-ecosystem/admin-backend/app.py"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 2. 查看app.py的main部分
    print("\n【查看main部分】")
    cmd = "tail -30 /root/lingzhi-ecosystem/admin-backend/app.py"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
