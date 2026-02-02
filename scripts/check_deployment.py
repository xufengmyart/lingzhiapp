#!/usr/bin/env python3
"""
检查部署状态
"""

import paramiko
import time

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PASSWORD = "Meiyue@root123"

def check_deployment():
    """检查部署状态"""

    # 尝试连接（增加重试）
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            print(f"尝试连接 (第{attempt + 1}次)...")
            ssh.connect(
                hostname=SERVER_HOST,
                username=SERVER_USER,
                password=SERVER_PASSWORD,
                timeout=60
            )
            print("✓ SSH连接成功")
            break
        except Exception as e:
            print(f"✗ 连接失败: {e}")
            if attempt < max_retries - 1:
                print("等待10秒后重试...")
                time.sleep(10)
            else:
                print("无法连接到云服务器")
                return

    try:
        print("\n" + "=" * 50)
        print("  检查部署状态")
        print("=" * 50)

        # 检查文件
        print("\n[1/5] 检查部署文件...")
        stdin, stdout, stderr = ssh.exec_command("ls -la /tmp/admin-backend/ 2>&1 | head -10")
        print(stdout.read().decode())

        # 检查Nginx
        print("\n[2/5] 检查Nginx状态...")
        stdin, stdout, stderr = ssh.exec_command("systemctl status nginx 2>&1 | grep -E 'Active|Loaded'")
        print(stdout.read().decode())

        # 检查后端服务
        print("\n[3/5] 检查后端服务...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python.*app.py' | grep -v grep")
        backend = stdout.read().decode()
        if backend:
            print(f"✓ 后端服务运行中:\n{backend}")
        else:
            print("✗ 后端服务未运行")

        # 检查端口
        print("\n[4/5] 检查端口监听...")
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep -E ':80 |:8080 ' || ss -tlnp 2>/dev/null | grep -E ':80 |:8080 '")
        ports = stdout.read().decode()
        if ports:
            print(f"✓ 端口监听:\n{ports}")
        else:
            print("✗ 端口未监听")

        # 测试访问
        print("\n[5/5] 测试访问...")
        stdin, stdout, stderr = ssh.exec_command("curl -I http://127.0.0.1:80/ 2>/dev/null | head -1")
        nginx_test = stdout.read().decode().strip()
        print(f"  Nginx: {nginx_test}")

        stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8080/api/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}' 2>/dev/null | head -c 100")
        api_test = stdout.read().decode().strip()
        print(f"  API: {api_test}")

        print("\n" + "=" * 50)

        # 如果服务未运行，尝试启动
        if "✗" in backend or "✗" in nginx_test:
            print("\n检测到服务未运行，尝试启动...")

            print("\n启动Nginx...")
            stdin, stdout, stderr = ssh.exec_command("systemctl start nginx")
            stdout.read()

            print("启动后端服务...")
            stdin, stdout, stderr = ssh.exec_command("cd /tmp/admin-backend && nohup python3 app.py > /tmp/backend.log 2>&1 &")
            stdout.read()

            time.sleep(3)

            print("\n重新检查状态...")
            stdin, stdout, stderr = ssh.exec_command("systemctl status nginx 2>&1 | grep Active")
            print("Nginx:", stdout.read().decode())

            stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python.*app.py' | grep -v grep")
            print("后端:", stdout.read().decode())

        ssh.close()

    except Exception as e:
        print(f"✗ 检查失败: {e}")

if __name__ == "__main__":
    check_deployment()
