# HTTPS配置指南

## 问题说明
当前系统使用HTTP协议，浏览器会提示"非加密连接"。为了提供安全的访问体验，建议配置HTTPS。

## 解决方案

### 方案一：使用Let's Encrypt免费SSL证书（推荐）

#### 1. 安装certbot
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot
```

#### 2. 获取SSL证书
```bash
# 如果域名是meiyueart.com
sudo certbot certonly --standalone -d meiyueart.com -d www.meiyueart.com
```

证书将保存到：
- 证书文件: `/etc/letsencrypt/live/meiyueart.com/fullchain.pem`
- 私钥文件: `/etc/letsencrypt/live/meiyueart.com/privkey.pem`

#### 3. 修改集成服务器支持HTTPS

创建新的HTTPS集成服务器 `https_server.py`：

```python
#!/usr/bin/env python3
"""
HTTPS集成服务器 - 提供静态文件和API代理
监听443端口
"""
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import ssl

class IntegratedHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.public_dir = '/workspace/projects/public'
    
    server_version = "IntegratedServer/1.0"
    
    def log_message(self, format, *args):
        print(f"[ACCESS] {self.client_address[0]} - {format % args}", file=sys.stderr, flush=True)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def handle_api(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else None
            
            target_url = f'http://127.0.0.1:8080{self.path}'
            
            if self.command == 'GET':
                req = urllib.request.Request(target_url, method='GET')
            elif self.command == 'POST':
                req = urllib.request.Request(target_url, data=body, method='POST')
            elif self.command == 'PUT':
                req = urllib.request.Request(target_url, data=body, method='PUT')
            elif self.command == 'DELETE':
                req = urllib.request.Request(target_url, method='DELETE')
            else:
                req = urllib.request.Request(target_url, method=self.command)
            
            for key, value in self.headers.items():
                if key.lower() not in ['host', 'content-length', 'transfer-encoding']:
                    req.add_header(key, value)
            
            with urllib.request.urlopen(req, timeout=10) as response:
                self.send_response(response.status)
                for key, value in response.headers.items():
                    if key.lower() not in ['content-encoding', 'transfer-encoding']:
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.read())
        except Exception as e:
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(f'{{"error": "Backend error: {str(e)}"}}'.encode())

    def do_GET(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.handle_static()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_response(404)
            self.end_headers()

    def do_PUT(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_response(404)
            self.end_headers()

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self.handle_api()
        else:
            self.send_response(404)
            self.end_headers()

    def handle_static(self):
        file_path = self.path.lstrip('/')
        if not file_path or file_path == '/':
            file_path = 'index.html'
        
        full_path = os.path.join(self.public_dir, file_path)
        
        if os.path.exists(full_path) and os.path.isfile(full_path):
            with open(full_path, 'rb') as f:
                content = f.read()
            
            content_type = 'text/html'
            if file_path.endswith('.css'):
                content_type = 'text/css'
            elif file_path.endswith('.js'):
                content_type = 'application/javascript'
            elif file_path.endswith('.png'):
                content_type = 'image/png'
            elif file_path.endswith('.jpg') or file_path.endswith('.jpeg'):
                content_type = 'image/jpeg'
            elif file_path.endswith('.svg'):
                content_type = 'image/svg+xml'
            
            self.send_response(200)
            self.send_header('Content-Type', content_type)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 443), IntegratedHandler)
    
    # 配置SSL
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('/etc/letsencrypt/live/meiyueart.com/fullchain.pem', 
                          '/etc/letsencrypt/live/meiyueart.com/privkey.pem')
    
    server.socket = context.wrap_socket(server.socket, server_side=True)
    
    print('HTTPS服务器启动成功，监听443端口', file=sys.stderr, flush=True)
    server.serve_forever()
```

#### 4. 启动HTTPS服务器
```bash
cd /workspace/projects
python3 https_server.py
```

#### 5. 配置HTTP自动跳转HTTPS
修改 `integrated_server.py`，添加HTTP到HTTPS的重定向：

```python
def do_GET(self):
    if self.path.startswith('/api/'):
        self.handle_api()
    else:
        # 重定向到HTTPS
        self.send_response(301)
        self.send_header('Location', f'https://{self.headers.get("Host")}{self.path}')
        self.end_headers()
```

### 方案二：使用自签名证书（仅用于开发测试）

```bash
# 生成自签名证书
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

# 使用证书启动服务器
python3 -c "
import http.server, ssl
context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
context.load_cert_chain('cert.pem', 'key.pem')
httpd = http.server.HTTPServer(('0.0.0.0', 443), IntegratedHandler)
httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
httpd.serve_forever()
"
```

### 方案三：使用反向代理（Nginx）

#### 1. 安装Nginx
```bash
sudo apt-get install nginx
```

#### 2. 获取SSL证书
```bash
sudo certbot certonly --nginx -d meiyueart.com
```

#### 3. 配置Nginx
创建 `/etc/nginx/sites-available/meiyueart.conf`：

```nginx
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
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://127.0.0.1:80;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 4. 启用配置并重启Nginx
```bash
sudo ln -s /etc/nginx/sites-available/meiyueart.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 方案四：使用云服务商提供的SSL证书（阿里云、腾讯云等）

1. 在云服务商控制台申请免费SSL证书
2. 下载证书文件（通常是.pem和.key格式）
3. 按照方案一或方案三配置证书

## 证书自动续期

Let's Encrypt证书有效期为90天，配置自动续期：

```bash
# 编辑cron任务
sudo crontab -e

# 添加以下行（每月1日凌晨3点自动续期）
0 3 1 * * certbot renew --quiet && systemctl restart nginx
```

## 注意事项

1. **端口权限**：HTTPS需要监听443端口，需要root权限或设置capabilities
2. **防火墙**：确保443端口在防火墙中开放
   ```bash
   sudo ufw allow 443/tcp
   ```
3. **证书路径**：确保证书文件路径正确且有读取权限
4. **域名验证**：确保DNS已正确解析到服务器IP

## 快速启动命令

如果已有证书，直接启动：

```bash
cd /workspace/projects
python3 https_server.py
```

访问地址：`https://meiyueart.com`
