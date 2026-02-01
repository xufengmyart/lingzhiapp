#!/usr/bin/env python3
"""
重启后端服务
"""

import paramiko

hostname = '123.56.142.143'
port = 22
username = 'root'
password = 'Meiyue@root123'

print("=" * 80)
print("重启后端服务")
print("=" * 80)

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(hostname, port, username, password)

    print(f"\n[1/2] 停止旧服务...")
    stdin, stdout, stderr = ssh.exec_command('pkill -f "python.*app.py" || true')
    print("✅ 旧服务已停止")

    print(f"\n[2/2] 启动新服务...")
    stdin, stdout, stderr = ssh.exec_command('cd /var/www/backend && nohup python3 app.py > /tmp/backend.log 2>&1 &')
    print("✅ 后端服务已启动")

    # 等待服务启动
    print(f"\n[3/3] 检查服务状态...")
    import time
    time.sleep(2)

    stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python.*app.py" | grep -v grep')
    output = stdout.read().decode('utf-8')

    if output:
        print("✅ 服务运行正常")
        print(output)
    else:
        print("⚠️  未检测到服务进程，请检查日志")

    print("\n==========================================")
    print("✅ 重启完成！")
    print("==========================================")
    print(f"\n访问: http://123.56.142.143")
    print(f"后端日志: tail -f /tmp/backend.log")

except Exception as e:
    print(f"\n❌ 重启失败: {e}")
    import traceback
    traceback.print_exc()

finally:
    ssh.close()
