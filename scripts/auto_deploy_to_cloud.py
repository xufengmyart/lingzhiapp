#!/usr/bin/env python3
"""
自动部署到云服务器
使用paramiko自动连接并部署
"""

import paramiko
import tarfile
import os
import sys

# 云服务器配置
SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22

# 部署包配置
DEPLOY_PACKAGE = "/workspace/projects/lingzhi_ecosystem_deploy_20260202_170838.tar.gz"
REMOTE_PATH = "/tmp/"

def connect_to_server():
    """连接到云服务器"""
    print(f"[1/7] 连接到云服务器 {SERVER_HOST}...")

    try:
        # 创建SSH客户端
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 连接服务器（使用密钥认证）
        try:
            # 尝试使用SSH密钥
            ssh.connect(
                hostname=SERVER_HOST,
                port=SERVER_PORT,
                username=SERVER_USER,
                timeout=30
            )
            print("✓ SSH连接成功（使用密钥认证）")
        except Exception as e:
            print(f"✗ SSH密钥认证失败: {e}")
            print("尝试使用密码认证...")

            # 如果密钥认证失败，询问密码
            password = input("请输入SSH密码: ")
            ssh.connect(
                hostname=SERVER_HOST,
                port=SERVER_PORT,
                username=SERVER_USER,
                password=password,
                timeout=30
            )
            print("✓ SSH连接成功（使用密码认证）")

        return ssh
    except Exception as e:
        print(f"✗ SSH连接失败: {e}")
        sys.exit(1)

def upload_package(ssh, local_path, remote_path):
    """上传部署包到云服务器"""
    print(f"\n[2/7] 上传部署包...")

    try:
        # 创建SFTP客户端
        sftp = ssh.open_sftp()

        # 上传文件
        filename = os.path.basename(local_path)
        remote_filepath = os.path.join(remote_path, filename)

        print(f"  上传: {local_path}")
        print(f"  到: {remote_filepath}")

        sftp.put(local_path, remote_filepath)
        sftp.close()

        # 检查文件大小
        local_size = os.path.getsize(local_path)
        print(f"✓ 上传成功 ({local_size / 1024 / 1024:.2f} MB)")

        return remote_filepath
    except Exception as e:
        print(f"✗ 上传失败: {e}")
        sys.exit(1)

def extract_package(ssh, remote_filepath):
    """解压部署包"""
    print(f"\n[3/7] 解压部署包...")

    try:
        # 解压文件
        stdin, stdout, stderr = ssh.exec_command(f"cd /tmp && tar -xzf {remote_filepath}")

        # 等待执行完成
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print("✓ 解压成功")
        else:
            print(f"✗ 解压失败: {stderr.read().decode()}")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 解压失败: {e}")
        sys.exit(1)

def run_deploy_script(ssh):
    """运行部署脚本"""
    print(f"\n[4/7] 运行部署脚本...")

    try:
        # 运行部署脚本
        stdin, stdout, stderr = ssh.exec_command("cd /tmp/admin-backend && bash ../scripts/cloud_auto_deploy.sh")

        # 实时显示输出
        while not stdout.channel.exit_status_ready():
            if stdout.channel.recv_ready():
                output = stdout.channel.recv(1024).decode()
                print(output, end='', flush=True)
            if stderr.channel.recv_stderr_ready():
                error = stderr.channel.recv_stderr(1024).decode()
                print(error, end='', flush=True)

        # 获取退出状态
        exit_status = stdout.channel.recv_exit_status()

        if exit_status == 0:
            print("\n✓ 部署脚本执行成功")
        else:
            print(f"\n✗ 部署脚本执行失败 (状态码: {exit_status})")
            sys.exit(1)
    except Exception as e:
        print(f"✗ 部署脚本执行失败: {e}")
        sys.exit(1)

def check_services(ssh):
    """检查服务状态"""
    print(f"\n[5/7] 检查服务状态...")

    try:
        # 检查Nginx
        stdin, stdout, stderr = ssh.exec_command("systemctl status nginx | grep Active")
        nginx_status = stdout.read().decode().strip()
        print(f"  Nginx: {nginx_status}")

        # 检查后端服务
        stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'python.*app.py' | grep -v grep | wc -l")
        backend_count = stdout.read().decode().strip()
        print(f"  后端服务: {backend_count} 个进程")

        # 检查端口监听
        stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep -E ':80 |:8080 '")
        ports = stdout.read().decode().strip()
        if ports:
            print("  端口监听:")
            for line in ports.split('\n'):
                if line:
                    print(f"    {line}")
        else:
            print("  端口监听: 未检测到")

        print("✓ 服务状态检查完成")
    except Exception as e:
        print(f"✗ 服务状态检查失败: {e}")

def open_security_group():
    """提示开放安全组"""
    print(f"\n[6/7] 阿里云安全组配置")
    print("=" * 50)
    print("⚠️  重要提示：请立即开放阿里云安全组端口")
    print("=" * 50)
    print("\n1. 登录阿里云控制台: https://ecs.console.aliyun.com/")
    print("2. ECS实例 -> 安全组 -> 配置规则")
    print("3. 添加入方向规则:")
    print("   - 端口范围: 80/80, 8080/8080")
    print("   - 协议类型: TCP")
    print("   - 授权对象: 0.0.0.0/0")
    print("4. 保存并等待1-2分钟生效")
    print("\n✓ 安全组配置提示完成")

def test_access(ssh):
    """测试访问"""
    print(f"\n[7/7] 测试本地访问...")

    try:
        # 测试Nginx
        stdin, stdout, stderr = ssh.exec_command("curl -I http://127.0.0.1:80/ 2>/dev/null | head -1")
        nginx_test = stdout.read().decode().strip()
        print(f"  本地80端口: {nginx_test}")

        # 测试后端API
        stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8080/api/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}' 2>/dev/null | head -1")
        api_test = stdout.read().decode().strip()
        print(f"  本地API: {api_test}")

        print("✓ 本地访问测试完成")
    except Exception as e:
        print(f"✗ 本地访问测试失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("  灵值生态园 - 自动部署到云服务器")
    print("=" * 50)
    print("")

    # 检查部署包是否存在
    if not os.path.exists(DEPLOY_PACKAGE):
        print(f"✗ 部署包不存在: {DEPLOY_PACKAGE}")
        sys.exit(1)

    print(f"部署包: {DEPLOY_PACKAGE}")
    print(f"大小: {os.path.getsize(DEPLOY_PACKAGE) / 1024 / 1024:.2f} MB")
    print("")

    # 连接到云服务器
    ssh = connect_to_server()

    # 上传部署包
    remote_filepath = upload_package(ssh, DEPLOY_PACKAGE, REMOTE_PATH)

    # 解压部署包
    extract_package(ssh, remote_filepath)

    # 运行部署脚本
    run_deploy_script(ssh)

    # 检查服务状态
    check_services(ssh)

    # 提示开放安全组
    open_security_group()

    # 测试访问
    test_access(ssh)

    # 关闭连接
    ssh.close()

    # 显示总结
    print("\n" + "=" * 50)
    print("  部署完成！")
    print("=" * 50)
    print("\n访问信息:")
    print(f"  Web应用: http://{SERVER_HOST}")
    print(f"  登录账号: admin / admin123")
    print("\n查看日志:")
    print("  ssh root@123.56.142.143")
    print("  tail -f /tmp/backend.log")
    print("  tail -f /var/log/nginx/error.log")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
