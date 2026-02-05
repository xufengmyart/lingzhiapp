#!/usr/bin/env python3
"""
重启云服务器上的后端服务
"""

import paramiko

# 云服务器配置
SERVER_HOST = '123.56.142.143'
SERVER_PORT = 22
SERVER_USER = 'root'
SERVER_PASSWORD = 'Meiyue@root123'

def restart_backend():
    """重启后端服务"""
    print("=" * 80)
    print("重启云服务器后端服务")
    print("=" * 80)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print("✅ 连接成功")
        
        # 1. 停止现有服务
        print("\n1. 停止现有服务...")
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend
            
            # 停止所有Python服务
            pkill -9 -f "python3.*app.py" || true
            pkill -9 -f "python3.*main.py" || true
            
            sleep 2
            
            # 确认没有残留进程
            ps aux | grep -E "(app.py|main.py)" | grep -v grep || echo "✅ 所有进程已停止"
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 2. 检查app.py文件
        print("\n2. 检查app.py文件...")
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend
            head -20 app.py | grep -E "(Flask|app =)"
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 3. 检查Python环境
        print("\n3. 检查Python环境...")
        stdin, stdout, stderr = ssh.exec_command('''
            which python3
            python3 --version
            pip3 list | grep -E "(flask|requests)"
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 4. 安装依赖
        print("\n4. 安装依赖...")
        stdin, stdout, stderr = ssh.exec_command('''
            pip3 install flask flask-cors requests paramiko -q 2>&1 | grep -v "already satisfied"
        ''')
        
        output = stdout.read().decode('utf-8')
        if output:
            print(output)
        else:
            print("✅ 依赖已就绪")
        
        # 5. 启动后端服务（8080端口）
        print("\n5. 启动后端服务（8080端口）...")
        stdin, stdout, stderr = ssh.exec_command('''
            cd /var/www/backend
            
            # 后台启动Flask服务
            nohup python3 app.py > /var/www/backend/flask.log 2>&1 &
            
            sleep 5
            
            # 检查进程
            ps aux | grep "python3 app.py" | grep -v grep
            
            # 检查端口
            netstat -tuln | grep 8080
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 6. 查看启动日志
        print("\n6. 查看启动日志...")
        stdin, stdout, stderr = ssh.exec_command('''
            tail -n 30 /var/www/backend/flask.log
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        # 7. 测试服务
        print("\n7. 测试服务...")
        stdin, stdout, stderr = ssh.exec_command('''
            curl -s http://localhost:8080/api/health || echo "❌ 测试失败"
        ''')
        
        output = stdout.read().decode('utf-8')
        print(output)
        
        print("\n" + "=" * 80)
        print("✅ 后端服务启动完成！")
        print("=" * 80)
        print(f"\n服务地址:")
        print(f"  后端API: http://{SERVER_HOST}:8080")
        print(f"  前端: http://{SERVER_HOST}:8001")
        
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

if __name__ == '__main__':
    restart_backend()
