#!/usr/bin/env python3
"""
使用SFTP直接上传文件到服务器
"""
import paramiko
from pathlib import Path

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              使用SFTP直接上传文件                                ║")
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

    sftp = ssh.open_sftp()

    # 确保远程目录存在
    print("\n【准备远程目录】")
    try:
        sftp.mkdir("/var/www/frontend/assets")
    except IOError:
        pass  # 目录可能已存在

    # 获取本地文件列表
    public_dir = Path("/workspace/projects/public")

    # 上传index.html
    print("\n【上传index.html】")
    local_path = public_dir / "index.html"
    remote_path = "/var/www/frontend/index.html"
    sftp.put(str(local_path), remote_path)
    print("  ✅ index.html")

    # 上传assets目录下的所有文件
    print("\n【上传assets文件】")
    assets_dir = public_dir / "assets"
    for file in assets_dir.glob("*"):
        if file.is_file():
            remote_path = f"/var/www/frontend/assets/{file.name}"
            sftp.put(str(file), remote_path)
            print(f"  ✅ {file.name}")

    # 上传其他文件
    print("\n【上传其他文件】")
    other_files = [
        "manifest.json",
        "manifest.webmanifest",
        "registerSW.js",
        "sw.js",
        "workbox-*.js",
        "icon-192x192.svg",
        "icon-512x512.svg",
        "apple-touch-icon.svg",
        "mask-icon.svg",
    ]

    for pattern in other_files:
        if "*" in pattern:
            # 处理通配符
            for file in public_dir.glob(pattern):
                if file.is_file():
                    remote_path = f"/var/www/frontend/{file.name}"
                    sftp.put(str(file), remote_path)
                    print(f"  ✅ {file.name}")
        else:
            local_path = public_dir / pattern
            if local_path.exists():
                remote_path = f"/var/www/frontend/{pattern}"
                sftp.put(str(local_path), remote_path)
                print(f"  ✅ {pattern}")

    sftp.close()

    # 设置权限
    print("\n【设置权限】")
    cmd = "chmod -R 755 /var/www/frontend && find /var/www/frontend -type f -exec chmod 644 {} \\;"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print("✅ 权限已设置")

    # 验证文件
    print("\n【验证文件】")
    cmd = "ls -lh /var/www/frontend/ | head -15"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode())

    # 重启Nginx
    print("\n【重启Nginx】")
    cmd = "systemctl restart nginx"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    error = stderr.read().decode()
    if error:
        print(f"❌ 重启失败: {error}")
    else:
        print("✅ Nginx已重启")

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║              部署成功！                                          ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

except Exception as e:
    print(f"\n❌ 部署失败: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
