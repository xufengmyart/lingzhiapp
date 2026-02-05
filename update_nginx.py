#!/usr/bin/env python3
"""
添加v9.0 API到Nginx配置
"""

import paramiko

# 云服务器配置
SERVER_HOST = '123.56.142.143'
SERVER_PORT = 22
SERVER_USER = 'root'
SERVER_PASSWORD = 'Meiyue@root123'

def update_nginx():
    """更新Nginx配置"""
    print("=" * 80)
    print("更新Nginx配置 - 添加v9.0 API代理")
    print("=" * 80)
    
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(SERVER_HOST, SERVER_PORT, SERVER_USER, SERVER_PASSWORD)
        print("✅ 连接成功")
        
        # 1. 查看当前配置
        print("\n1. 查看当前Nginx配置...")
        stdin, stdout, stderr = ssh.exec_command('cat /etc/nginx/sites-available/lingzhi-frontend.conf')
        current_config = stdout.read().decode('utf-8')
        print(current_config)
        
        # 2. 更新配置，添加v9.0 API代理
        print("\n2. 更新配置...")
        new_config = current_config.replace(
            "    # API 反向代理\n    location /api/ {\n        proxy_pass http://127.0.0.1:8001/api/;",
            "    # API 反向代理（智能体）\n    location /api/ {\n        proxy_pass http://127.0.0.1:8001/api/;"
        )
        
        # 检查是否已经包含v9.0配置
        if "/api/v9/" not in current_config:
            # 在文件末尾添加v9.0 API配置
            v9_config = '''
    # v9.0 API 反向代理
    location /api/v9/ {
        proxy_pass http://127.0.0.1:8080/api/v9/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }
}
'''
            new_config = current_config.rstrip() + v9_config
            
            # 上传新配置
            stdin, stdout, stderr = ssh.exec_command('cat > /etc/nginx/sites-available/lingzhi-frontend.conf', get_pty=True)
            stdin.write(new_config)
            stdin.close()
            stdout.read()
            print("✅ 配置已更新")
        else:
            print("✅ v9.0配置已存在，跳过")
        
        # 3. 测试配置
        print("\n3. 测试Nginx配置...")
        stdin, stdout, stderr = ssh.exec_command('nginx -t')
        output = stdout.read().decode('utf-8')
        error = stderr.read().decode('utf-8')
        
        print(output)
        if error:
            print(error)
        
        if "successful" in output.lower():
            # 4. 重启Nginx
            print("\n4. 重启Nginx...")
            stdin, stdout, stderr = ssh.exec_command('systemctl reload nginx')
            output = stdout.read().decode('utf-8')
            print("✅ Nginx已重启")
            
            # 5. 测试访问
            print("\n5. 测试访问...")
            stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost/api/health')
            health = stdout.read().decode('utf-8')
            print(f"/api/health: {health}")
            
            stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v9/referrals')
            code = stdout.read().decode('utf-8').strip()
            print(f"/api/v9/referrals: HTTP {code} (预期401，未授权)")
            
            print("\n" + "=" * 80)
            print("✅ Nginx配置更新完成！")
            print("=" * 80)
            print(f"\n访问地址:")
            print(f"  前端: http://{SERVER_HOST}")
            print(f"  智能体API: http://{SERVER_HOST}/api/")
            print(f"  v9.0 API: http://{SERVER_HOST}/api/v9/")
        else:
            print("❌ Nginx配置测试失败")
        
    except Exception as e:
        print(f"❌ 更新失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        ssh.close()

def get_pty():
    """返回True以获取PTY"""
    return True

if __name__ == '__main__':
    update_nginx()
