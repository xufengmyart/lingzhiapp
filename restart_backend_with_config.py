#!/usr/bin/env python3
"""
上传修改后的app.py并重启后端服务
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PASSWORD = "Meiyue@root123"

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          上传app.py并重启后端服务                                 ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(
            hostname=SERVER_HOST,
            port=22,
            username=SERVER_USER,
            password=SERVER_PASSWORD,
            timeout=30
        )

        sftp = ssh.open_sftp()

        # 1. 上传app.py
        print("\n【1】上传app.py...")
        local_file = "/workspace/projects/admin-backend/app.py"
        remote_file = "/root/lingzhi-ecosystem/admin-backend/app.py"
        sftp.put(local_file, remote_file)
        print("  ✅ app.py已上传")

        sftp.close()

        # 2. 停止后端服务
        print("\n【2】停止后端服务...")
        stdin, stdout, stderr = ssh.exec_command("pkill -9 -f 'python3 app.py'", timeout=30)
        stdout.read()
        print("  ✅ 后端服务已停止")

        import time
        time.sleep(2)

        # 3. 启动后端服务
        print("\n【3】启动后端服务...")
        stdin, stdout, stderr = ssh.exec_command(
            "cd /root/lingzhi-ecosystem/admin-backend && nohup python3 app.py > /tmp/backend.log 2>&1 &",
            timeout=30
        )
        stdout.read()
        print("  ✅ 后端服务已启动")

        # 4. 等待服务启动
        time.sleep(5)

        # 5. 检查服务状态
        print("\n【4】检查服务状态...")
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python3 app.py' | grep -v grep", timeout=10)
        result = stdout.read().decode()
        if result:
            print("  ✅ 后端进程运行中")
        else:
            print("  ❌ 后端进程未运行")

        # 6. 检查日志
        print("\n【5】查看启动日志】")
        stdin, stdout, stderr = ssh.exec_command("tail -15 /tmp/backend.log", timeout=10)
        print(stdout.read().decode())

        # 7. 检查端口
        print("\n【6】检查端口】")
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep 8080", timeout=10)
        result = stdout.read().decode()
        if result:
            print("  ✅ 8080端口监听中")
        else:
            print("  ❌ 8080端口未监听")

        print("\n╔══════════════════════════════════════════════════════════════════╗")
        print("║          后端服务已重启！                                        ║")
        print("╚══════════════════════════════════════════════════════════════════╝")

    except Exception as e:
        print(f"\n❌ 操作失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

    return True

if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)
