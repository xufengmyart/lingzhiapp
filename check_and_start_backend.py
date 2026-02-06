#!/usr/bin/env python3
"""
检查并启动后端服务
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              检查并启动后端服务                                  ║")
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

    # 检查后端服务状态
    print("【步骤1】检查后端服务状态...")
    print("-" * 70)
    cmd = "systemctl status flask-backend | head -20"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 检查端口占用
    print("【步骤2】检查端口8001...")
    print("-" * 70)
    cmd = "ss -tlnp | grep 8001 || echo 'Port 8001 not listening'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 查看后端日志
    print("【步骤3】查看后端日志（最后20行）...")
    print("-" * 70)
    cmd = "tail -20 /app/work/logs/bypass/app.log"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 手动启动后端服务
    print("【步骤4】手动启动后端服务...")
    print("-" * 70)
    cmd = """
cd /root/lingzhi-ecosystem/admin-backend
nohup python3 app.py > /app/work/logs/bypass/app.log 2>&1 &
echo $! > /tmp/flask-backend.pid
sleep 3
ps aux | grep "python3 app.py" | grep -v grep
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 测试后端API
    print("【步骤5】测试后端API...")
    print("-" * 70)
    cmd = "curl -I http://127.0.0.1:8001/api/status 2>&1 | head -10"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    print("✅ 后端服务已启动")

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
