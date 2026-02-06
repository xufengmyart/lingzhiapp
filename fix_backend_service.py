#!/usr/bin/env python3
"""
检查并修复后端服务
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║                  检查并修复后端服务                              ║")
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

    # 1. 检查后端目录
    print("【1】检查后端目录")
    print("-" * 70)
    cmd = "ls -la /root/lingzhi-ecosystem/admin-backend/"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 2. 检查app.py文件
    print()
    print("【2】检查app.py文件")
    print("-" * 70)
    cmd = "test -f /root/lingzhi-ecosystem/admin-backend/app.py && echo 'File exists' || echo 'File not found'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 3. 查看app.py的端口配置
    print()
    print("【3】查看app.py的端口配置")
    print("-" * 70)
    cmd = "grep -n 'port\\|PORT\\|8001' /root/lingzhi-ecosystem/admin-backend/app.py | head -10"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 4. 停止现有进程
    print()
    print("【4】停止现有后端进程")
    print("-" * 70)
    cmd = "pkill -f 'python.*app.py' && sleep 2 && echo 'Processes killed' || echo 'No processes to kill'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 5. 重新启动后端
    print()
    print("【5】重新启动后端")
    print("-" * 70)
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && nohup python3 app.py > /tmp/backend.log 2>&1 & echo 'Backend started'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 6. 等待5秒后检查
    print()
    print("【6】等待5秒后检查端口")
    print("-" * 70)
    cmd = "sleep 5 && netstat -tlnp | grep :8001"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 7. 查看后端日志
    print()
    print("【7】查看后端日志")
    print("-" * 70)
    cmd = "tail -20 /tmp/backend.log"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 8. 测试登录API
    print()
    print("【8】测试登录API")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8001/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"password123"}' | head -50"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
