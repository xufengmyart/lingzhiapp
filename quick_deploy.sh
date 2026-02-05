#!/bin/bash

echo "=========================================="
echo "灵值生态园 - 快速修复部署"
echo "=========================================="

# 1. 停止旧服务
echo ""
echo "[1/6] 停止旧服务..."
pkill -9 -f "python3 app.py" 2>/dev/null || true
pkill -9 -f "python3 main_server" 2>/dev/null || true
pkill -9 -f "uvicorn" 2>/dev/null || true
sleep 3
echo "完成"

# 2. 安装依赖
echo ""
echo "[2/6] 安装依赖..."
pip3 install flask flask-cors flask-jwt-extended bcrypt pyjwt httpx -q 2>/dev/null || true
echo "完成"

# 3. 启动后端
echo ""
echo "[3/6] 启动后端Flask服务..."
cd admin-backend
nohup python3 app.py > /tmp/flask_backend.log 2>&1 &
cd ..
sleep 5
echo "完成"

# 4. 创建main_server
echo ""
echo "[4/6] 创建main_server..."
cat > main_server_fixed.py << 'EOF'
#!/usr/bin/env python3
import os, httpx
from fastapi import FastAPI, Request, Response
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

os.environ["_BYTEFAAS_RUNTIME_PORT"] = ""
app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
public_dir = "/workspace/projects/public"

@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def api_proxy(path: str, request: Request):
    try:
        headers = {"Content-Type": request.headers.get("content-type", "application/json"), "Accept": "application/json"}
        body = await request.body()
        async with httpx.AsyncClient(timeout=30.0, verify=False) as client:
            response = await client.request(method=request.method, url=f"http://127.0.0.1:8080/api/{path}", headers=headers, content=body)
            return Response(content=response.content, status_code=response.status_code, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS", "Access-Control-Allow-Headers": "Content-Type, Authorization"})
    except Exception as e:
        return Response(status_code=502, content=f"Backend error: {e}")

@app.get("/")
async def root():
    with open(os.path.join(public_dir, "index.html"), 'r', encoding='utf-8') as f:
        return Response(content=f.read(), media_type="text/html")

@app.get("/{path:path}")
async def static_files(path: str):
    if path.startswith("api/"): return Response(status_code=404)
    file_location = os.path.join(public_dir, path if path else "index.html")
    if os.path.exists(file_location) and os.path.isfile(file_location):
        return FileResponse(file_location)
    return Response(status_code=404)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000, log_level="info")
EOF
echo "完成"

# 5. 启动前端
echo ""
echo "[5/6] 启动前端代理服务..."
nohup python3 main_server_fixed.py > /tmp/main_server_fixed.log 2>&1 &
sleep 5
echo "完成"

# 6. 配置Nginx
echo ""
echo "[6/6] 配置Nginx..."
if [ -d "/etc/nginx/sites-available" ]; then
    cat > /etc/nginx/sites-available/meiyueart.com << 'NGINX'
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com 123.56.142.143;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$host$request_uri; }
}

server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com 123.56.142.143;

    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept, Origin" always;

    if ($request_method = OPTIONS) {
        add_header Access-Control-Allow-Origin * always;
        add_header Content-Length 0;
        return 204;
    }

    location / {
        proxy_pass http://localhost:9000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
NGINX
    ln -sf /etc/nginx/sites-available/meiyueart.com /etc/nginx/sites-enabled/
    nginx -t && systemctl reload nginx
    echo "完成"
else
    echo "跳过（Nginx目录不存在）"
fi

# 验证
echo ""
echo "=========================================="
echo "验证服务"
echo "=========================================="
echo ""
echo "端口:"
lsof -i:8080 -i:9000 2>/dev/null | grep LISTEN || netstat -tlnp 2>/dev/null | grep -E "8080|9000"
echo ""
echo "后端API:"
curl -s http://localhost:8080/api/health
echo ""
echo ""
echo "前端API:"
curl -s http://localhost:9000/api/health
echo ""
echo ""
echo "智能体对话:"
curl -s -X POST http://localhost:9000/api/agent/chat -H "Content-Type: application/json" -d '{"message":"你好"}' | head -80
echo ""
echo ""
echo "=========================================="
echo "部署完成！"
echo "=========================================="
echo ""
echo "访问: https://meiyueart.com"
echo "日志: tail -f /tmp/flask_backend.log /tmp/main_server_fixed.log"
echo ""
