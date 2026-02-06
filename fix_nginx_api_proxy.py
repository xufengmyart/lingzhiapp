#!/usr/bin/env python3
"""
修复Nginx配置 - 将API代理到8080端口
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              修复Nginx配置 - API代理到8080端口                   ║")
print("╚══════════════════════════════════════════════════════════════════╝")
print()

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

    # 1. 备份现有Nginx配置
    print("【1】备份现有Nginx配置")
    cmd = "cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup.$(date +%Y%m%d_%H%M%S)"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print("✅ 备份完成")

    # 2. 更新Nginx配置 - 将API代理到8080端口
    print()
    print("【2】更新Nginx配置")
    print("-" * 70)

    nginx_config = """
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;

    # HTTP重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com;

    # SSL证书配置
    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 前端静态文件
    location / {
        root /var/www/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;

        # 安全headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # 禁用缓存
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    # API反向代理（修复：代理到8080端口）
    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 静态资源缓存
    location ~* \\.(jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot|webmanifest)$ {
        root /var/www/frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # JS/CSS缓存
    location ~* \\.(js|css)$ {
        root /var/www/frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 安全：禁止访问隐藏文件
    location ~ /\\. {
        deny all;
    }

    # 安全：禁止访问敏感文件
    location ~* \\.(sql|db|log|env)$ {
        deny all;
    }
}
"""

    cmd = f"cat > /etc/nginx/sites-enabled/default << 'NGINX_EOF'\n{nginx_config}\nNGINX_EOF"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print("✅ Nginx配置已更新")

    # 3. 测试Nginx配置
    print()
    print("【3】测试Nginx配置")
    print("-" * 70)
    cmd = "nginx -t"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 4. 重新加载Nginx
    print()
    print("【4】重新加载Nginx")
    print("-" * 70)
    cmd = "systemctl reload nginx && echo 'Nginx已重新加载'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 5. 重启后端服务
    print()
    print("【5】重启后端服务")
    print("-" * 70)
    cmd = "pkill -f 'python.*app.py' && sleep 2 && cd /root/lingzhi-ecosystem/admin-backend && nohup python3 app.py > /tmp/backend.log 2>&1 & sleep 3 && echo '后端已重启'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=60)
    output = stdout.read().decode('utf-8')
    print(output)

    # 6. 检查后端端口
    print()
    print("【6】检查后端端口")
    print("-" * 70)
    cmd = "sleep 2 && netstat -tlnp | grep :8080"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    # 7. 测试API连接
    print()
    print("【7】测试API连接")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login \\
      -H "Content-Type: application/json" \\
      -d '{"username":"admin","password":"password123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)

    print()
    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                      配置完成                                    ║")
    print("╚══════════════════════════════════════════════════════════════════╝")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
