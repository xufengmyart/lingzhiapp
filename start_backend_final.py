#!/usr/bin/env python3
"""
检查并启动后端
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

    # 1. 检查后端进程
    print("【检查后端进程】")
    cmd = "ps aux | grep 'python.*app.py' | grep -v grep"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output if output else "无进程运行")

    # 2. 检查8080端口
    print("\n【检查8080端口】")
    cmd = "netstat -tlnp | grep :8080"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output if output else "端口未监听")

    # 3. 启动后端
    print("\n【启动后端】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && nohup python3 app.py > /tmp/backend.log 2>&1 &"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print("启动命令已执行")

    # 4. 等待并检查
    print("\n【等待5秒后检查】")
    cmd = "sleep 5 && netstat -tlnp | grep :8080"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output if output else "端口仍未监听")

    # 5. 查看日志
    print("\n【查看后端日志】")
    cmd = "tail -30 /tmp/backend.log"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 6. 测试API
    print("\n【测试登录API】")
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
