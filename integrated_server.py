#!/usr/bin/env python3
"""
集成服务器 - 提供静态文件和API代理
监听80端口
"""
import os
import httpx
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse
import threading

class IntegratedHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory='/var/www/lingzhiapp/public', **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

    def do_GET(self):
        # API请求代理到Flask
        if self.path.startswith('/api/'):
            try:
                target_url = f'http://127.0.0.1:8001{self.path}'
                response = httpx.get(target_url, timeout=10)
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    if key.lower() != 'content-encoding':
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.content)
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Backend error: {e}'.encode())
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith('/api/'):
            try:
                content_length = int(self.headers['Content-Length'])
                body = self.rfile.read(content_length)
                target_url = f'http://127.0.0.1:8001{self.path}'
                response = httpx.post(target_url, content=body, timeout=10)
                self.send_response(response.status_code)
                for key, value in response.headers.items():
                    if key.lower() != 'content-encoding':
                        self.send_header(key, value)
                self.end_headers()
                self.wfile.write(response.content)
            except Exception as e:
                self.send_response(502)
                self.send_header('Content-Type', 'text/plain')
                self.end_headers()
                self.wfile.write(f'Backend error: {e}'.encode())

if __name__ == '__main__':
    server = HTTPServer(('0.0.0.0', 80), IntegratedHandler)
    print('服务器启动，监听80端口，支持API代理')
    server.serve_forever()
