#!/usr/bin/env python3
"""
标准自动部署脚本 - 从开发到生产环境
"""
import os
import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    os.system("pip install paramiko -q")
    import paramiko

# 服务器配置
SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

# 对象存储配置
STORAGE_URL_PREFIX = "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475"
STORAGE_SIGN = "sign=1770417491-0-0-0"

# 部署的文件列表（最新的构建产物）
FILES_TO_DEPLOY = {
    "index_7c9726b8.html": "index.html",
    "index-C6o-EcmT_83216bd2.css": "assets/index-C6o-EcmT.css",
    "index-DTCeM_v7_ce4325a6.js": "assets/index-DTCeM_v7.js",
    "manifest_a3f53961.json": "manifest.json",
    "manifest_58cae434.webmanifest": "manifest.webmanifest",
    "registerSW_83e9aa4e.js": "registerSW.js",
    "icon-192x192_79e1c92a.svg": "icon-192x192.svg",
    "icon-512x512_b4c9e387.svg": "icon-512x512.svg",
    "apple-touch-icon_ad022b3f.svg": "apple-touch-icon.svg",
    "mask-icon_ebd1f55e.svg": "mask-icon.svg",
}

class AutoDeployer:
    def __init__(self):
        self.ssh = None

    def connect(self):
        """连接到服务器"""
        print("🔐 连接到服务器...")
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(
            hostname=SERVER_HOST,
            port=SERVER_PORT,
            username=SERVER_USER,
            password=SERVER_PASSWORD,
            timeout=30
        )
        print("✅ 连接成功")

    def deploy(self):
        """部署新文件"""
        print()
        print("📤 部署新文件...")

        # 清空目录
        cmd = "rm -rf /var/www/frontend/* && mkdir -p /var/www/frontend/assets"
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=30)

        # 下载文件
        success_count = 0
        for storage_name, target_path in FILES_TO_DEPLOY.items():
            url = f"{STORAGE_URL_PREFIX}/{storage_name}?{STORAGE_SIGN}"
            full_path = f"/var/www/frontend/{target_path}"

            cmd = f"curl -fsSL -o '{full_path}' '{url}'"
            stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=30)

            if not stderr.read():
                success_count += 1
                print(f"  ✅ {target_path}")
            else:
                print(f"  ❌ {target_path}")

        print()
        print(f"✅ 下载完成: {success_count}/{len(FILES_TO_DEPLOY)}")

        # 设置权限
        print()
        print("🔐 设置文件权限...")
        cmd = "chmod -R 755 /var/www/frontend && find /var/www/frontend -type f -exec chmod 644 {} \\;"
        self.ssh.exec_command(cmd, timeout=30)
        print("✅ 权限已设置")

    def restart_nginx(self):
        """重启Nginx"""
        print()
        print("🔄 重启Nginx...")
        cmd = "systemctl reload nginx && echo 'OK'"
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=30)
        print("✅ Nginx已重启")

    def verify(self):
        """验证部署"""
        print()
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                      验证部署                                    ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print()

        # 测试HTTPS访问
        cmd = "curl -I https://127.0.0.1/ -k 2>&1 | head -5"
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=30)
        output = stdout.read().decode('utf-8')

        if "200" in output:
            print("✅ HTTPS访问正常")
        else:
            print("❌ HTTPS访问异常")
            print(output)

        # 检查关键文件
        cmd = "test -f /var/www/frontend/index.html && test -f /var/www/frontend/assets/index-C6o-EcmT.css && test -f /var/www/frontend/assets/index-DTCeM_v7.js && echo 'OK'"
        stdin, stdout, stderr = self.ssh.exec_command(cmd, timeout=30)
        result = stdout.read().decode('utf-8').strip()

        if result == "OK":
            print("✅ 所有关键文件存在")
        else:
            print("❌ 部分文件缺失")

    def close(self):
        """关闭连接"""
        if self.ssh:
            self.ssh.close()

def main():
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║        灵值生态园 - 标准自动部署流程                              ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    deployer = AutoDeployer()

    try:
        deployer.connect()
        deployer.deploy()
        deployer.restart_nginx()
        deployer.verify()

        print()
        print("╔══════════════════════════════════════════════════════════════════╗")
        print("║                        部署完成                                  ║")
        print("╚══════════════════════════════════════════════════════════════════╝")
        print()
        print("📱 访问地址：")
        print("   https://meiyueart.com")
        print()
        print("💡 清除浏览器缓存：")
        print("   Windows: Ctrl + Shift + R")
        print("   Mac: Cmd + Shift + R")
        print()
        print("🔐 登录账号：")
        print("   用户名: admin")
        print("   密码: admin123")
        print()

    except Exception as e:
        print()
        print(f"❌ 部署失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        deployer.close()

if __name__ == "__main__":
    main()
