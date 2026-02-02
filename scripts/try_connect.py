#!/usr/bin/env python3
"""
创建SSH密钥对并尝试自动部署
"""

import paramiko
import os
import sys

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
DEPLOY_PACKAGE = "/workspace/projects/lingzhi_ecosystem_deploy_20260202_170838.tar.gz"

def create_ssh_key():
    """创建SSH密钥对"""
    print("创建SSH密钥对...")

    try:
        # 使用Python生成RSA密钥对
        key = paramiko.RSAKey.generate(2048)

        # 保存私钥
        private_key_path = "/tmp/id_rsa"
        key.write_private_key_file(private_key_path)
        print(f"✓ 私钥已保存到: {private_key_path}")

        # 保存公钥
        public_key_path = "/tmp/id_rsa.pub"
        with open(public_key_path, 'w') as f:
            f.write(f"{key.get_name()} {key.get_base64()}")

        with open(public_key_path, 'r') as f:
            public_key_content = f.read()
        print(f"✓ 公钥已保存到: {public_key_path}")
        print(f"  公钥内容: {public_key_content}")

        return private_key_path, public_key_content
    except Exception as e:
        print(f"✗ 创建SSH密钥失败: {e}")
        return None, None

def try_connect_with_key(key_path):
    """使用密钥尝试连接"""
    print(f"\n尝试使用密钥连接...")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 加载私钥
        key = paramiko.RSAKey.from_private_key_file(key_path)

        # 尝试连接
        ssh.connect(
            hostname=SERVER_HOST,
            username=SERVER_USER,
            pkey=key,
            timeout=30
        )

        print("✓ SSH连接成功")
        return ssh
    except Exception as e:
        print(f"✗ SSH连接失败: {e}")
        return None

def try_connect_without_auth():
    """尝试无认证连接"""
    print(f"\n尝试无认证连接...")

    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # 尝试无认证连接
        ssh.connect(
            hostname=SERVER_HOST,
            username=SERVER_USER,
            timeout=30
        )

        print("✓ SSH连接成功")
        return ssh
    except Exception as e:
        print(f"✗ SSH连接失败: {e}")
        return None

def main():
    print("=" * 50)
    print("  尝试自动连接到云服务器")
    print("=" * 50)
    print("")

    # 方法1：尝试无认证连接
    ssh = try_connect_without_auth()
    if ssh:
        print("\n✓ 连接成功！")
        ssh.close()
        return

    # 方法2：创建密钥对并尝试连接
    private_key_path, public_key_content = create_ssh_key()
    if private_key_path:
        ssh = try_connect_with_key(private_key_path)
        if ssh:
            print("\n✓ 连接成功！")
            ssh.close()
            return

    # 如果所有方法都失败
    print("\n" + "=" * 50)
    print("  无法自动连接到云服务器")
    print("=" * 50)
    print("\n可能的原因:")
    print("1. 云服务器需要密码认证")
    print("2. 云服务器需要特定的SSH密钥")
    print("3. 云服务器SSH服务未运行")
    print("4. 网络连接问题")
    print("\n请手动连接云服务器并执行:")
    print("  ssh root@123.56.142.143")
    print("  cd /tmp")
    print("  tar -xzf lingzhi_ecosystem_deploy_20260202_170838.tar.gz")
    print("  cd admin-backend")
    print("  bash ../scripts/cloud_auto_deploy.sh")
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()
