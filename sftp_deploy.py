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

    # 上传index.html
    print("\n【上传index.html】")
    local_path = "/workspace/projects/public/index.html"
    remote_path = "/var/www/frontend/index.html"
    sftp.put(local_path, remote_path)
    print("  ✅ index.html")

    # 上传CSS
    print("\n【上传CSS文件】")
    local_path = "/workspace/projects/public/assets/index-C6o-EcmT.css"
    remote_path = "/var/www/frontend/assets/index-C6o-EcmT.css"
    sftp.put(local_path, remote_path)
    print("  ✅ index-C6o-EcmT.css")

    # 上传JS
    print("\n【上传JS文件】")
    local_path = "/workspace/projects/public/assets/index-DTCeM_v7.js"
    remote_path = "/var/www/frontend/assets/index-DTCeM_v7.js"
    sftp.put(local_path, remote_path)
    print("  ✅ index-DTCeM_v7.js")

    # 上传其他文件
    print("\n【上传其他文件】")
    other_files = [
        ("manifest.json", "manifest.json"),
        ("manifest.webmanifest", "manifest.webmanifest"),
        ("registerSW.js", "registerSW.js"),
        ("icon-192x192.svg", "icon-192x192.svg"),
        ("icon-512x512.svg", "icon-512x512.svg"),
        ("apple-touch-icon.svg", "apple-touch-icon.svg"),
        ("mask-icon.svg", "mask-icon.svg"),
    ]

    for filename, remote_filename in other_files:
        local_path = f"/workspace/projects/public/{filename}"
        remote_path = f"/var/www/frontend/{remote_filename}"
        sftp.put(local_path, remote_path)
        print(f"  ✅ {remote_filename}")

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
    print(stdout.read().decode('utf-8'))

    # 测试访问
    print("\n【测试访问】")
    cmd = "curl -I https://127.0.0.1/ -k 2>&1 | head -5"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    if "200" in output:
        print("✅ HTTPS访问正常")
    else:
        print("❌ HTTPS访问异常")

    # 重启Nginx
    print("\n【重启Nginx】")
    cmd = "systemctl reload nginx && echo 'OK'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print("✅ Nginx已重启")

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                      部署完成                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("📱 访问：https://meiyueart.com")
    print("🔐 登录：admin / admin123")
    print("💡 清除浏览器缓存：Ctrl + Shift + R")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
