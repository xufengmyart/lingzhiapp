#!/usr/bin/env python3
"""
检查后端API状态
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║                  检查后端API状态                                  ║")
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

    # 1. 检查后端进程
    print("【1】检查后端进程")
    print("-" * 70)
    cmd = "ps aux | grep 'python.*app.py' | grep -v grep"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    if output:
        print("✅ 后端进程运行中")
        print(output)
    else:
        print("❌ 后端进程未运行")

    # 2. 检查端口监听
    print()
    print("【2】检查后端端口监听")
    print("-" * 70)
    cmd = "netstat -tlnp | grep :8001"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    if output:
        print("✅ 8001端口监听中")
        print(output)
    else:
        print("❌ 8001端口未监听")

    # 3. 测试API健康检查
    print()
    print("【3】测试API健康检查")
    print("-" * 70)
    cmd = "curl -s http://127.0.0.1:8001/api/health 2>&1 || echo 'Health endpoint not found'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 4. 测试登录API
    print()
    print("【4】测试登录API")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8001/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"password123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 5. 检查后端日志
    print()
    print("【5】检查后端日志（最后10行）")
    print("-" * 70)
    cmd = "tail -10 /root/lingzhi-ecosystem/admin-backend/app.log 2>/dev/null || echo 'Log file not found'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 6. 检查数据库
    print()
    print("【6】检查数据库用户")
    print("-" * 70)
    cmd = """curl -s http://127.0.0.1:8001/api/admin/users \\
      -H "Authorization: Bearer test" 2>&1 | head -20"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
