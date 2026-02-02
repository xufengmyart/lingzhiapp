#!/usr/bin/env python3
"""
集成服务器 - 提供静态文件和API代理
监听80端口
"""
import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse

class IntegratedHandler(BaseHTTPRequestHandler):
    public_dir = '/workspace/projects/public'
    
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
            
            # 根据HTTP方法选择处理方式
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
            
            # 转发所有头信息
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
    server = HTTPServer(('0.0.0.0', 80), IntegratedHandler)
    print('集成服务器启动成功，监听80端口', file=sys.stderr, flush=True)
    server.serve_forever()
