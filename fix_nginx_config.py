#!/usr/bin/env python3
"""
修复Nginx配置
"""

import paramiko

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect('123.56.142.143', 22, 'root', 'Meiyue@root123')

# 正确的配置
correct_config = '''# 前端静态文件服务配置
server {
    listen 80;
    server_name 123.56.142.143 meiyueart.com www.meiyueart.com;

    # 前端静态文件
    location / {
        root /var/www/lingzhiapp/public;
        try_files $uri $uri/ /index.html;
        index index.html;
        
        # 缓存控制
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API 反向代理（智能体）
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_cache_bypass $http_upgrade;
    }

    # v9.0 API 反向代理（Flask后端）
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

# 写入文件
stdin, stdout, stderr = ssh.exec_command('cat > /etc/nginx/sites-available/lingzhi-frontend.conf << "EOFCONFIG"\n' + correct_config + '\nEOFCONFIG\n', get_pty=True)
stdin.write('\n')
stdin.close()
output = stdout.read()

print("✅ 配置文件已重写")

# 测试配置
stdin, stdout, stderr = ssh.exec_command('nginx -t 2>&1')
output = stdout.read().decode('utf-8')
print("\n配置测试:")
print(output)

if "successful" in output:
    # 重启Nginx
    stdin, stdout, stderr = ssh.exec_command('systemctl reload nginx && echo "✅ Nginx已重启"')
    print(stdout.read().decode('utf-8'))
    
    # 测试访问
    print("\n测试访问:")
    stdin, stdout, stderr = ssh.exec_command('curl -s -o /dev/null -w "%{http_code}" http://localhost/api/v9/referrals')
    code = stdout.read().decode('utf-8').strip()
    print(f"/api/v9/referrals: HTTP {code} (预期401，未授权)")
    
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost/api/health')
    print(f"/api/health: {stdout.read().decode('utf-8').strip()}")

ssh.close()

def get_pty():
    return True
