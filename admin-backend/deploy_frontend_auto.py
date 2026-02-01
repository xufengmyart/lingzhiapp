#!/usr/bin/env python3
"""
自动部署前端到服务器
"""

import paramiko
import os
from datetime import datetime

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

print("=" * 80)
print("灵值生态园 - 前端自动部署")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # 连接服务器
    print(f"\n[1/5] 连接到服务器...")
    ssh.connect(hostname, port, username, password)
    print("✅ 连接成功")

    # 创建备份
    print(f"\n[2/5] 备份现有文件...")
    backup_name = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    stdin, stdout, stderr = ssh.exec_command(f'mkdir -p /var/www/backup && cp -r /var/www/html /var/www/backup/{backup_name} 2>/dev/null || echo "首次部署，无需备份"')
    print("✅ 备份完成")

    # 上传前端文件
    print(f"\n[3/5] 上传前端文件...")
    sftp = ssh.open_sftp()

    # 先删除旧文件
    stdin, stdout, stderr = ssh.exec_command('rm -rf /var/www/html/*')
    stdout.read()

    # 上传 dist 目录下的所有文件
    local_dist = '/workspace/projects/web-app/dist'
    remote_html = '/var/www/html'

    # 确保远程目录存在
    stdin, stdout, stderr = ssh.exec_command(f'mkdir -p {remote_html}')
    stdout.read()

    # 上传所有文件
    for root, dirs, files in os.walk(local_dist):
        for file in files:
            local_path = os.path.join(root, file)
            relative_path = os.path.relpath(local_path, local_dist)
            remote_path = os.path.join(remote_html, relative_path)

            # 创建远程目录
            remote_dir = os.path.dirname(remote_path)
            stdin, stdout, stderr = ssh.exec_command(f'mkdir -p {remote_dir}')
            stdout.read()

            # 上传文件
            sftp.put(local_path, remote_path)

    sftp.close()
    print("✅ 文件上传完成")

    # 设置权限
    print(f"\n[4/5] 设置文件权限...")
    stdin, stdout, stderr = ssh.exec_command('chown -R www-data:www-data /var/www/html && chmod -R 755 /var/www/html')
    print("✅ 权限设置完成")

    # 重启 Nginx（如果需要）
    print(f"\n[5/5] 检查 Nginx 配置...")
    stdin, stdout, stderr = ssh.exec_command('nginx -t')
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if 'successful' in output.lower():
        print("✅ Nginx 配置检查通过")
    else:
        print(f"⚠️  Nginx 配置检查: {output} {error}")

    print("\n==========================================")
    print("✅ 部署完成！")
    print("==========================================")
    print(f"\n访问: http://123.56.142.143")
    print(f"备份位置: /var/www/backup/{backup_name}")

except Exception as e:
    print(f"\n❌ 部署失败: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
