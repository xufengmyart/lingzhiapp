#!/usr/bin/env python3
"""
生成完整部署方案 - 包含Nginx配置修复
"""
import os
import sys
import subprocess

# 生成Nginx配置
nginx_config = """server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;

    # 重定向到HTTPS
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
        try_files $uri $uri/ /index.html;
        index index.html;
    }

    # API反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
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

    # WebSocket支持
    location /ws/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # 静态资源缓存
    location ~* \\.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
        root /var/www/frontend;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
"""

print("="*80)
print("🔧 Nginx 配置文件")
print("="*80)
print(nginx_config)
print("="*80)

# 保存到文件
with open('/tmp/nginx_meiyueart.conf', 'w') as f:
    f.write(nginx_config)

print("\n✅ Nginx配置已保存到 /tmp/nginx_meiyueart.conf")
print("\n" + "="*80)
print("📋 服务器执行步骤：")
print("="*80)
print("""
1. 上传配置文件到服务器：
   scp /tmp/nginx_meiyueart.conf root@123.56.142.143:/tmp/

2. 在服务器上执行修复命令：
   cd /root
   
   # 备份当前配置
   cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup
   
   # 应用新配置
   cp /tmp/nginx_meiyueart.conf /etc/nginx/sites-enabled/default
   
   # 测试配置
   nginx -t
   
   # 重启Nginx
   systemctl restart nginx
   
   # 验证状态
   systemctl status nginx

3. 重新部署前端：
   cd /root && wget -O public.tar.gz "https://coze-coding-project.tos.coze.site/coze_storage_7597771717536317475/public_v3.tar_3e884757.gz?sign=1770371205-4fbb370610-0-b96757292bda4487a3ad4b530db38a80f16e4c7f2f747392da7addc15d0bcd7a" && rm -rf /var/www/frontend/* && tar -xzf public.tar.gz -C /var/www/frontend/ && chown -R root:root /var/www/frontend && chmod -R 755 /var/www/frontend && systemctl reload nginx && rm -f public.tar.gz

4. 清除浏览器缓存后访问
""")
print("="*80)
