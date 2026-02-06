#!/usr/bin/env python3
"""
将规范化配置部署到服务器
"""
import paramiko
import os

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PASSWORD = "Meiyue@root123"

def deploy_env_config():
    """部署环境配置到服务器"""
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║          部署环境配置到服务器                                      ║")
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

        # 1. 上传admin-backend/.env
        print("\n【1】上传后端环境配置...")
        local_env = "/workspace/projects/admin-backend/.env"
        remote_env = "/root/lingzhi-ecosystem/admin-backend/.env"
        sftp.put(local_env, remote_env)
        print("  ✅ admin-backend/.env")

        # 2. 创建必要的目录
        print("\n【2】创建必要的目录...")
        stdin, stdout, stderr = ssh.exec_command(
            "mkdir -p /root/lingzhi-ecosystem/admin-backend/logs /root/lingzhi-ecosystem/admin-backend/backups",
            timeout=30
        )
        stdout.read()
        print("  ✅ 日志和备份目录已创建")

        # 3. 验证配置
        print("\n【3】验证配置...")
        stdin, stdout, stderr = ssh.exec_command(
            "cat /root/lingzhi-ecosystem/admin-backend/.env | grep -E 'SECRET_KEY|JWT_SECRET'",
            timeout=30
        )
        print("  服务器配置:")
        print(stdout.read().decode())

        # 4. 重启后端服务
        print("\n【4】重启后端服务以应用新配置...")
        stdin, stdout, stderr = ssh.exec_command(
            "pkill -9 -f 'python3 app.py'",
            timeout=30
        )
        stdout.read()

        import time
        time.sleep(2)

        stdin, stdout, stderr = ssh.exec_command(
            "cd /root/lingzhi-ecosystem/admin-backend && nohup python3 app.py > /tmp/backend.log 2>&1 &",
            timeout=30
        )
        stdout.read()

        time.sleep(3)

        # 检查进程
        stdin, stdout, stderr = ssh.exec_command(
            "ps aux | grep 'python3 app.py' | grep -v grep",
            timeout=30
        )
        result = stdout.read().decode()
        if result:
            print("  ✅ 后端服务已重启")
        else:
            print("  ❌ 后端服务启动失败")

        # 5. 检查日志
        print("\n【5】检查后端日志...")
        stdin, stdout, stderr = ssh.exec_command(
            "tail -5 /tmp/backend.log",
            timeout=30
        )
        print(stdout.read().decode())

        sftp.close()

        print("\n╔══════════════════════════════════════════════════════════════════╗")
        print("║          配置部署完成！                                          ║")
        print("╚══════════════════════════════════════════════════════════════════╝")

    except Exception as e:
        print(f"\n❌ 部署失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        ssh.close()

    return True

if __name__ == '__main__':
    success = deploy_env_config()
    exit(0 if success else 1)
