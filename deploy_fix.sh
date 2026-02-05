#!/bin/bash

set -e

echo "=========================================="
echo "灵值生态园 - 一键修复部署脚本"
echo "=========================================="

PROJECT_DIR="/workspace/projects"
BACKEND_DIR="$PROJECT_DIR/admin-backend"

# 1. 停止旧服务
echo "停止旧服务..."
pkill -f "python3 app.py" 2>/dev/null || true
pkill -f "python3 main_server" 2>/dev/null || true
sleep 3

# 2. 安装依赖
echo "安装依赖..."
pip3 install flask flask-cors flask-jwt-extended bcrypt pyjwt httpx -q

# 3. 创建修复后的main_server
echo "创建main_server_fixed.py..."
cat > "$PROJECT_DIR/main_server_fixed.py" << 'EOF'
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

# 4. 启动服务
echo "启动后端Flask服务（8080端口）..."
cd "$BACKEND_DIR"
nohup python3 app.py > /tmp/flask_backend.log 2>&1 &
sleep 5

echo "启动前端代理服务（9000端口）..."
cd "$PROJECT_DIR"
nohup python3 main_server_fixed.py > /tmp/main_server_fixed.log 2>&1 &
sleep 5

# 5. 验证
echo ""
echo "验证服务..."
echo ""
echo "端口监听:"
lsof -i:8080 -i:9000 2>/dev/null | grep LISTEN
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
curl -s -X POST http://localhost:9000/api/agent/chat -H "Content-Type: application/json" -d '{"message":"你好"}' | head -100
echo ""
echo ""
echo "部署完成！"
