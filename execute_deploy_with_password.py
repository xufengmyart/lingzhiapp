#!/usr/bin/env python3
"""
使用提供的密码SSH连接到服务器并执行部署
"""
import os
import sys

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

# 部署命令
DEPLOY_COMMAND = """curl -fsSL "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/deploy_frontend_from_storage_c62bf332.sh?sign=1770417491-0-0-0" | bash"""

print("╔══════════════════════════════════════════════════════════════════╗")
print("║        灵值生态园 - 自动SSH部署工具                              ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print()
print(f"🔗 连接到: {SERVER_HOST}:{SERVER_PORT}")
print(f"👤 用户: {SERVER_USER}")
print()

# 创建SSH客户端
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("🔐 正在连接...")
    ssh.connect(
        hostname=SERVER_HOST,
        port=SERVER_PORT,
        username=SERVER_USER,
        password=SERVER_PASSWORD,
        timeout=30
    )
    print("✅ SSH连接成功！")
    print()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                   开始执行部署                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    # 执行部署命令
    stdin, stdout, stderr = ssh.exec_command(DEPLOY_COMMAND, timeout=300)

    # 实时输出
    print("📤 部署输出：")
    print("-" * 70)
    while True:
        line = stdout.readline()
        if not line:
            break
        print(line.rstrip())

    # 获取错误输出
    err_output = stderr.read().decode('utf-8')
    if err_output:
        print()
        print("❌ 错误输出：")
        print(err_output)

    # 获取退出状态
    exit_status = stdout.channel.recv_exit_status()

    print("-" * 70)
    print()

    if exit_status == 0:
        print("✅ 部署命令执行成功！")
    else:
        print(f"❌ 部署命令执行失败，退出状态码: {exit_status}")

    print()

    # 验证部署
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                   验证部署结果                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

    verify_commands = [
        "ls -la /var/www/frontend/",
        "curl -I http://127.0.0.1/",
        "curl -I https://127.0.0.1/ -k 2>/dev/null || echo 'HTTPS test failed'"
    ]

    for cmd in verify_commands:
        print(f"执行: {cmd}")
        stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
        output = stdout.read().decode('utf-8')
        print(output)
        print()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                        部署完成                                  ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()
    print("📱 现在请访问：")
    print("   https://meiyueart.com")
    print()
    print("💡 清除浏览器缓存：")
    print("   Windows: Ctrl + Shift + R")
    print("   Mac: Cmd + Shift + R")
    print()

except paramiko.AuthenticationException:
    print("❌ SSH认证失败")
    print("用户名或密码错误")
except Exception as e:
    print(f"❌ 发生错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
