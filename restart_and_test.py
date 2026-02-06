#!/usr/bin/env python3
"""
重启后端服务并测试
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              重启后端服务并测试                                  ║")
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

    # 停止所有后端进程
    print("\n【1】停止所有后端进程】")
    cmd = "pkill -9 -f 'python.*app.py' && sleep 2 && echo '所有进程已停止'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    # 重新启动后端
    print("\n【2】重新启动后端】")
    cmd = "cd /root/lingzhi-ecosystem/admin-backend && nohup python3 app.py > /tmp/backend.log 2>&1 & sleep 3 && echo '后端已启动'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    print(stdout.read().decode('utf-8'))

    # 检查端口
    print("\n【3】检查端口】")
    cmd = "netstat -tlnp | grep :8080"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    # 测试admin登录
    print("\n【4】测试admin登录】")
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"admin123"}' | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"成功: {d.get('success')}, 消息: {d.get('message')}\")\""""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    # 测试许锋登录
    print("\n【5】测试许锋登录】")
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"许锋","password":"password123"}' | python3 -c "import sys, json; d=json.load(sys.stdin); print(f\"成功: {d.get('success')}, 消息: {d.get('message')}\")\""""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                      测试完成                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
