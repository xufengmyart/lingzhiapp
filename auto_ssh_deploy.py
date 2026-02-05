#!/usr/bin/env python3
"""
自动SSH到服务器并执行部署脚本
使用paramiko库实现SSH连接
"""

import os
import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("❌ paramiko库未安装")
    print("正在安装...")
    os.system("pip install paramiko")
    import paramiko

# 服务器配置
SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22

# 部署命令
DEPLOY_COMMAND = """curl -fsSL "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/deploy_frontend_from_storage_c62bf332.sh?sign=1770417491-0-0-0" | bash"""

def execute_ssh_command(host, user, port, command, password=None, key_path=None):
    """通过SSH执行命令"""
    print("=" * 70)
    print("🚀 开始SSH连接到服务器")
    print("=" * 70)
    print(f"主机: {host}")
    print(f"用户: {user}")
    print(f"端口: {port}")
    print()

    # 创建SSH客户端
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # 尝试使用密钥认证
        if key_path and os.path.exists(key_path):
            print(f"🔑 使用密钥文件: {key_path}")
            private_key = paramiko.RSAKey.from_private_key_file(key_path)
            ssh.connect(host, port=port, username=user, pkey=private_key)
        # 否则使用密码
        elif password:
            print(f"🔐 使用密码认证")
            ssh.connect(host, port=port, username=user, password=password)
        else:
            print("❌ 需要提供密码或密钥文件路径")
            return False

        print("✅ SSH连接成功")
        print()

        # 执行部署命令
        print("=" * 70)
        print("📤 执行部署命令")
        print("=" * 70)
        print(f"命令: {command}")
        print()

        stdin, stdout, stderr = ssh.exec_command(command, timeout=300)

        # 实时输出
        while True:
            line = stdout.readline()
            if not line:
                break
            print(line.strip())

        # 获取错误输出
        err_output = stderr.read().decode('utf-8')
        if err_output:
            print("\n❌ 错误输出:")
            print(err_output)

        # 获取退出状态
        exit_status = stdout.channel.recv_exit_status()

        print()
        print("=" * 70)
        if exit_status == 0:
            print("✅ 部署命令执行成功！")
        else:
            print(f"❌ 部署命令执行失败，退出状态码: {exit_status}")
        print("=" * 70)

        return exit_status == 0

    except paramiko.AuthenticationException:
        print("❌ SSH认证失败")
        print("请检查用户名、密码或密钥文件")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH连接错误: {e}")
        return False
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        return False
    finally:
        ssh.close()

def main():
    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║        灵值生态园 - 自动SSH部署工具                            ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    # 尝试从环境变量读取SSH密钥路径
    key_path = os.getenv("SSH_PRIVATE_KEY_PATH")

    # 尝试从环境变量读取SSH密码
    password = os.getenv("SSH_PASSWORD")

    # 如果都没有，提示用户
    if not key_path and not password:
        print("⚠️  未找到SSH认证信息")
        print()
        print("请设置环境变量：")
        print("  export SSH_PASSWORD='your_password'")
        print("  或")
        print("  export SSH_PRIVATE_KEY_PATH='/path/to/private_key'")
        print()
        print("或者手动在服务器上执行：")
        print(f"  {DEPLOY_COMMAND}")
        return

    # 执行部署
    success = execute_ssh_command(
        host=SERVER_HOST,
        user=SERVER_USER,
        port=SERVER_PORT,
        command=DEPLOY_COMMAND,
        password=password,
        key_path=key_path
    )

    if success:
        print()
        print("🎉 部署完成！")
        print()
        print("📱 现在请访问：")
        print("   https://meiyueart.com")
        print()
        print("💡 清除浏览器缓存：")
        print("   Windows: Ctrl + Shift + R")
        print("   Mac: Cmd + Shift + R")
        print()
    else:
        print()
        print("❌ 部署失败")
        print()
        print("请尝试手动在服务器上执行：")
        print(f"  {DEPLOY_COMMAND}")
        print()

if __name__ == "__main__":
    main()
