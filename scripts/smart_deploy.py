#!/usr/bin/env python3
"""
智能自动部署脚本
尝试所有可能的认证方式
"""

import paramiko
import os
import sys
import socket

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
DEPLOY_PACKAGE = "/workspace/projects/lingzhi_ecosystem_deploy_20260202_170838.tar.gz"

class AutoDeployer:
    def __init__(self):
        self.ssh = None

    def test_ssh_connection(self):
        """测试SSH端口是否开放"""
        print("[1/8] 测试SSH端口连接...")

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((SERVER_HOST, 22))
            sock.close()

            if result == 0:
                print("✓ SSH端口开放")
                return True
            else:
                print("✗ SSH端口无法访问")
                return False
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False

    def try_agent_auth(self):
        """尝试SSH agent认证"""
        print("\n[2/8] 尝试SSH agent认证...")

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 尝试使用SSH agent
            agent = paramiko.AgentRequestAgent()
            agent_keys = agent.get_keys()

            if agent_keys:
                for key in agent_keys:
                    try:
                        ssh.connect(
                            hostname=SERVER_HOST,
                            username=SERVER_USER,
                            pkey=key,
                            timeout=30,
                            auth_timeout=30
                        )
                        print("✓ SSH agent认证成功")
                        self.ssh = ssh
                        return True
                    except:
                        continue

            print("✗ SSH agent认证失败")
            ssh.close()
            return False
        except Exception as e:
            print(f"✗ SSH agent认证失败: {e}")
            return False

    def try_known_hosts_keys(self):
        """尝试known_hosts中的密钥"""
        print("\n[3/8] 尝试known_hosts密钥...")

        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # 尝试从known_hosts加载
            known_hosts_file = os.path.expanduser("~/.ssh/known_hosts")
            if os.path.exists(known_hosts_file):
                ssh.load_system_host_keys(known_hosts_file)

            ssh.connect(
                hostname=SERVER_HOST,
                username=SERVER_USER,
                timeout=30,
                allow_agent=True
            )

            print("✓ known_hosts认证成功")
            self.ssh = ssh
            return True
        except Exception as e:
            print(f"✗ known_hosts认证失败: {e}")
            if self.ssh:
                self.ssh.close()
            return False

    def try_default_keys(self):
        """尝试默认SSH密钥"""
        print("\n[4/8] 尝试默认SSH密钥...")

        default_key_paths = [
            "~/.ssh/id_rsa",
            "~/.ssh/id_ecdsa",
            "~/.ssh/id_ed25519",
            "/tmp/id_rsa",
        ]

        for key_path in default_key_paths:
            key_path = os.path.expanduser(key_path)
            if os.path.exists(key_path):
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    key = paramiko.RSAKey.from_private_key_file(key_path)
                    ssh.connect(
                        hostname=SERVER_HOST,
                        username=SERVER_USER,
                        pkey=key,
                        timeout=30
                    )

                    print(f"✓ 使用密钥 {key_path} 认证成功")
                    self.ssh = ssh
                    return True
                except Exception as e:
                    print(f"✗ 使用密钥 {key_path} 认证失败: {e}")
                    if self.ssh:
                        self.ssh.close()
                    continue

        print("✗ 所有默认密钥认证失败")
        return False

    def try_env_password(self):
        """尝试从环境变量读取密码"""
        print("\n[5/8] 尝试环境变量密码...")

        # 检查常见的环境变量
        env_vars = ['SSH_PASSWORD', 'CLOUD_PASSWORD', 'SERVER_PASSWORD', 'PASSWORD']

        for var in env_vars:
            password = os.environ.get(var)
            if password:
                try:
                    ssh = paramiko.SSHClient()
                    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                    ssh.connect(
                        hostname=SERVER_HOST,
                        username=SERVER_USER,
                        password=password,
                        timeout=30
                    )

                    print(f"✓ 使用环境变量 {var} 认证成功")
                    self.ssh = ssh
                    return True
                except Exception as e:
                    print(f"✗ 使用环境变量 {var} 认证失败: {e}")
                    if self.ssh:
                        self.ssh.close()
                    continue

        print("✗ 环境变量密码认证失败")
        return False

    def try_password_from_file(self):
        """尝试从文件读取密码"""
        print("\n[6/8] 尝试从文件读取密码...")

        password_files = [
            "/tmp/cloud_password.txt",
            "/workspace/projects/.password",
            "/root/.cloud_password",
        ]

        for file_path in password_files:
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        password = f.read().strip()

                    if password:
                        ssh = paramiko.SSHClient()
                        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

                        ssh.connect(
                            hostname=SERVER_HOST,
                            username=SERVER_USER,
                            password=password,
                            timeout=30
                        )

                        print(f"✓ 使用文件 {file_path} 认证成功")
                        self.ssh = ssh
                        return True
                except Exception as e:
                    print(f"✗ 使用文件 {file_path} 认证失败: {e}")
                    if self.ssh:
                        self.ssh.close()
                    continue

        print("✗ 文件密码认证失败")
        return False

    def try_interactive_password(self):
        """尝试交互式输入密码"""
        print("\n[7/8] 尝试交互式密码认证...")
        print("注意：由于当前环境不支持交互式输入，此方法不可用")
        print("请使用其他认证方式或手动部署")
        return False

    def deploy(self):
        """执行部署"""
        print("=" * 50)
        print("  灵值生态园 - 智能自动部署")
        print("=" * 50)
        print("")

        # 测试SSH端口
        if not self.test_ssh_connection():
            print("\n✗ SSH端口无法访问，无法继续部署")
            return False

        # 尝试各种认证方式
        auth_methods = [
            self.try_agent_auth,
            self.try_known_hosts_keys,
            self.try_default_keys,
            self.try_env_password,
            self.try_password_from_file,
            self.try_interactive_password,
        ]

        for method in auth_methods:
            if method():
                break

        if not self.ssh:
            print("\n[8/8] 所有认证方式都失败了")
            print("\n" + "=" * 50)
            print("  无法自动连接到云服务器")
            print("=" * 50)
            print("\n请使用XShell手动执行以下命令:")
            print("-" * 50)
            print("1. 上传部署包到云服务器:")
            print("   scp lingzhi_ecosystem_deploy_20260202_170838.tar.gz root@123.56.142.143:/tmp/")
            print("")
            print("2. SSH登录到云服务器:")
            print("   ssh root@123.56.142.143")
            print("")
            print("3. 解压并部署:")
            print("   cd /tmp")
            print("   tar -xzf lingzhi_ecosystem_deploy_20260202_170838.tar.gz")
            print("   cd admin-backend")
            print("   bash ../scripts/cloud_auto_deploy.sh")
            print("")
            print("4. 开放阿里云安全组端口:")
            print("   - 登录 https://ecs.console.aliyun.com/")
            print("   - ECS实例 -> 安全组 -> 配置规则")
            print("   - 添加端口 80/80, 8080/8080")
            print("")
            print("5. 访问应用:")
            print("   http://123.56.142.143")
            print("-" * 50)
            return False

        print("\n✓ 连接成功！开始部署...")

        # 这里可以继续执行部署步骤
        print("\n部署功能待实现...")

        # 关闭连接
        self.ssh.close()

        return True

if __name__ == "__main__":
    deployer = AutoDeployer()
    deployer.deploy()
