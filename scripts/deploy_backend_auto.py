#!/usr/bin/env python3
"""
自动部署后端到服务器
"""

import paramiko
import os
import tarfile
import tempfile
from datetime import datetime

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

print("=" * 80)
print("灵值生态园 - 后端自动部署")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    # 连接服务器
    print(f"\n[1/7] 连接到服务器...")
    ssh.connect(hostname, port, username, password)
    print("✅ 连接成功")

    # 创建备份
    print(f"\n[2/7] 备份现有文件...")
    backup_name = f"backend_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    stdin, stdout, stderr = ssh.exec_command(f'mkdir -p /root/backup && cp -r /root/lingzhi-ecosystem/admin-backend /root/backup/{backup_name} 2>/dev/null || echo "首次部署，无需备份"')
    print("✅ 备份完成")

    # 打包后端文件
    print(f"\n[3/7] 打包后端文件...")
    temp_dir = tempfile.mkdtemp()
    temp_tar = os.path.join(temp_dir, 'backend.tar.gz')

    with tarfile.open(temp_tar, 'w:gz') as tar:
        tar.add('/workspace/projects/admin-backend', arcname='admin-backend')

    print(f"✅ 打包完成: {os.path.getsize(temp_tar) / 1024 / 1024:.2f} MB")

    # 上传后端文件
    print(f"\n[4/7] 上传后端文件...")
    sftp = ssh.open_sftp()

    # 上传压缩包
    remote_temp = f'/tmp/backend_deploy_{datetime.now().strftime("%Y%m%d_%H%M%S")}.tar.gz'
    sftp.put(temp_tar, remote_temp)
    print(f"✅ 上传完成: {remote_temp}")

    sftp.close()

    # 清理本地临时文件
    os.remove(temp_tar)
    os.rmdir(temp_dir)

    # 解压并安装依赖
    print(f"\n[5/7] 解压并安装依赖...")
    stdin, stdout, stderr = ssh.exec_command(f'''
cd /tmp
rm -rf admin-backend_temp
mkdir -p admin-backend_temp
tar -xzf {remote_temp} -C admin-backend_temp
cd admin-backend_temp/admin-backend

# 安装依赖
pip3 install -r requirements.txt 2>/dev/null || echo "部分依赖安装失败"

# 复制到目标目录
rm -rf /root/lingzhi-ecosystem/admin-backend
mkdir -p /root/lingzhi-ecosystem/admin-backend
cp -r . /root/lingzhi-ecosystem/admin-backend/

# 清理临时文件
rm -rf /tmp/admin-backend_temp {remote_temp}
''')

    # 显示输出
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            output = stdout.channel.recv(1024).decode()
            print(output, end='', flush=True)

    exit_status = stdout.channel.recv_exit_status()
    print("✅ 后端文件部署完成")

    # 停止旧服务
    print(f"\n[6/7] 停止旧服务...")
    stdin, stdout, stderr = ssh.exec_command('pkill -f "python.*app.py" 2>/dev/null || echo "没有运行中的服务"')
    print("✅ 旧服务已停止")

    # 启动新服务
    print(f"\n[7/7] 启动新服务...")
    stdin, stdout, stderr = ssh.exec_command('''
cd /root/lingzhi-ecosystem/admin-backend
nohup python3 app.py > /tmp/backend.log 2>&1 &
sleep 2

# 检查服务状态
if ps aux | grep "python.*app.py" | grep -v grep > /dev/null; then
    echo "✅ 后端服务启动成功"
else
    echo "❌ 后端服务启动失败"
    tail -20 /tmp/backend.log
fi
''')

    # 显示输出
    while not stdout.channel.exit_status_ready():
        if stdout.channel.recv_ready():
            output = stdout.channel.recv(1024).decode()
            print(output, end='', flush=True)
        if stderr.channel.recv_stderr_ready():
            error = stderr.channel.recv_stderr(1024).decode()
            print(error, end='', flush=True)

    print("\n==========================================")
    print("✅ 后端部署完成！")
    print("==========================================")

    # 测试后端API
    print("\n测试后端API...")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://127.0.0.1:8080/api/login -X POST -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}' 2>/dev/null | head -c 200")
    api_test = stdout.read().decode().strip()
    print(f"API响应: {api_test}")

    print(f"\n访问: http://123.56.142.143")
    print(f"备份位置: /root/backup/{backup_name}")

except Exception as e:
    print(f"\n❌ 部署失败: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
