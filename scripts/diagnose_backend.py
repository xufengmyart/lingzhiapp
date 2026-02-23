#!/usr/bin/env python3
"""
诊断后端问题并修复
"""

import paramiko
import time

# 服务器配置
CONFIG = {
    "hostname": "123.56.142.143",
    "port": 22,
    "username": "root",
    "password": "Meiyue@root123",
}

def ssh_execute(ssh, command):
    """执行SSH命令"""
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    return output, error

def main():
    print("连接到服务器...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(**CONFIG)
    
    print("\n1. 检查后端进程状态...")
    output, _ = ssh_execute(ssh, "ps aux | grep 'python.*app.py' | grep -v grep")
    if output:
        print("后端进程正在运行:")
        print(output)
    else:
        print("后端进程未运行")
    
    print("\n2. 检查后端日志（最后50行）...")
    output, _ = ssh_execute(ssh, "tail -50 /var/www/meiyueart.com/backend.log")
    print(output)
    
    print("\n3. 检查端口占用...")
    output, _ = ssh_execute(ssh, "netstat -tlnp | grep 8080")
    print(output)
    
    print("\n4. 手动启动后端服务...")
    ssh_execute(ssh, '''
        cd /var/www/backend
        # 确保所有需要的文件都在
        ls -la
        
        # 停止旧进程
        pkill -f "python.*app.py" 2>/dev/null || true
        sleep 2
        
        # 启动新进程
        nohup python app.py > /var/www/meiyueart.com/backend.log 2>&1 &
        echo "后端已启动，PID: $!"
        
        # 等待启动
        sleep 5
        
        # 检查进程
        ps aux | grep "python.*app.py" | grep -v grep
    ''')
    
    print("\n5. 测试后端健康检查...")
    for i in range(5):
        time.sleep(2)
        output, _ = ssh_execute(ssh, "curl -s http://127.0.0.1:8080/api/health")
        print(f"尝试 {i+1}/5: {output[:100] if output else '无响应'}")
        
        if '"status": "ok"' in output:
            print("✅ 后端健康检查成功！")
            break
    
    print("\n6. 测试登录接口...")
    output, _ = ssh_execute(ssh, "curl -s -X POST http://127.0.0.1:8080/api/admin/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"123\"}'")
    print(f"登录测试: {output[:200] if output else '无响应'}")
    
    print("\n7. 检查数据库文件...")
    output, _ = ssh_execute(ssh, "ls -lh /var/www/backend/*.db")
    print(output)
    
    ssh.close()
    print("\n诊断完成！")

if __name__ == '__main__':
    main()
