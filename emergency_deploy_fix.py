#!/usr/bin/env python3
"""
紧急修复部署
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║                  紧急修复部署                                    ║")
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

    # 1. 恢复之前的文件
    print("\n【1】恢复之前的文件")
    cmd = "ls /root/lingzhi-ecosystem/admin-backend/*.tar.gz 2>/dev/null | tail -1 | xargs -I {} tar -xzf {} -C /var/www/frontend 2>/dev/null || echo 'No backup found'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 2. 重新下载文件（直接从public目录）
    print("\n【2】直接下载文件")
    print("-" * 70)

    files = [
        ("https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/index_7c9726b8.html?sign=1770417491-0-0-0", "index.html"),
        ("https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/index-C6o-EcmT_83216bd2.css?sign=1770417491-0-0-0", "assets/index-C6o-EcmT.css"),
        ("https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/index-DTCeM_v7_ce4325a6.js?sign=1770417491-0-0-0", "assets/index-DTCeM_v7.js"),
    ]

    for url, target in files:
        cmd = f"curl -fsSL -o '/var/www/frontend/{target}' '{url}'"
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        error = stderr.read().decode('utf-8')

        if error:
            print(f"  ❌ {target}")
        else:
            # 检查文件是否存在
            check_cmd = f"test -f '/var/www/frontend/{target}' && echo 'OK' || echo 'FAIL'"
            stdin, stdout, stderr = ssh.exec_command(check_cmd, timeout=30)
            result = stdout.read().decode('utf-8').strip()

            if result == "OK":
                print(f"  ✅ {target}")
            else:
                print(f"  ❌ {target}")

    # 3. 设置权限
    print("\n【3】设置权限")
    cmd = "chmod -R 755 /var/www/frontend && find /var/www/frontend -type f -exec chmod 644 {} \\;"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print("✅ 权限已设置")

    # 4. 验证
    print("\n【4】验证文件")
    cmd = "ls -lh /var/www/frontend/"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    # 5. 测试访问
    print("\n【5】测试访问")
    cmd = "curl -I https://127.0.0.1/ -k 2>&1 | head -5"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))

    # 6. 重启Nginx
    print("\n【6】重启Nginx")
    cmd = "systemctl reload nginx && echo 'OK'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print("✅ Nginx已重启")

    print("\n╔══════════════════════════════════════════════════════════════════╗")
    print("║                      修复完成                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("📱 访问：https://meiyueart.com")
    print("🔐 登录：admin / admin123")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
