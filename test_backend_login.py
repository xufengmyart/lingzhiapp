#!/usr/bin/env python3
"""
测试后端登录（使用正确的端口8080）
"""
import paramiko

SERVER_HOST = "123.56.142.143"
SERVER_USER = "root"
SERVER_PORT = 22
SERVER_PASSWORD = "Meiyue@root123"

print("╔══════════════════════════════════════════════════════════════════╗")
print("║              测试后端登录                                          ║")
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

    # 测试后端API状态
    print("【步骤1】测试后端API状态...")
    print("-" * 70)
    cmd = "curl -s http://127.0.0.1:8080/api/status | head -20"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 测试登录
    print("【步骤2】测试登录...")
    print("-" * 70)
    cmd = """curl -s -X POST http://127.0.0.1:8080/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password123"}'"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)
    print()

    # 检查Nginx配置
    print("【步骤3】检查Nginx API代理配置...")
    print("-" * 70)
    cmd = "cat /etc/nginx/sites-enabled/default | grep -A 10 'location /api/'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 更新Nginx配置（如果需要）
    print("【步骤4】更新Nginx API代理配置...")
    print("-" * 70)
    cmd = """
cat > /tmp/nginx-api-fix.conf << 'EOF'
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com;

    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # 前端静态文件
    location / {
        root /var/www/frontend;
        index index.html;
        try_files \$uri \$uri/ /index.html;

        # 安全headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;

        # 禁用缓存
        add_header Cache-Control "no-cache, no-store, must-revalidate" always;
        add_header Pragma "no-cache" always;
        add_header Expires "0" always;
    }

    # API反向代理（使用正确的后端端口8080）
    location /api/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 300s;
        proxy_connect_timeout 75s;
    }

    # 静态资源
    location ~* \.(jpg|jpeg|png|gif|ico|svg|woff|woff2|ttf|eot|webmanifest)$ {
        root /var/www/frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

cp /tmp/nginx-api-fix.conf /etc/nginx/sites-enabled/default
nginx -t && echo "✅ Nginx配置已更新"
"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 重启Nginx
    print("【步骤5】重启Nginx...")
    print("-" * 70)
    cmd = "systemctl reload nginx && echo '✅ Nginx已重启'"
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    print(stdout.read().decode('utf-8'))
    print()

    # 测试HTTPS登录
    print("【步骤6】测试HTTPS登录...")
    print("-" * 70)
    cmd = """curl -s -X POST https://127.0.0.1/api/login -H "Content-Type: application/json" -d '{"username":"admin","password":"password123"}' -k"""
    stdin, stdout, stderr = ssh.exec_command(cmd, timeout=30)
    output = stdout.read().decode('utf-8')
    print(output)
    print()

    print("╔══════════════════════════════════════════════════════════════════╗")
    print("║                    测试完成                                      ║")
    print("╚══════════════════════════════════════════════════════════════════╝")
    print()

except Exception as e:
    print(f"❌ 错误: {e}")
finally:
    ssh.close()
