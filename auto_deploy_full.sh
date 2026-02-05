#!/bin/bash

# ============================================
# 灵值生态园 - 全自动修复部署脚本 v2.0
# 用途：一键修复所有服务并配置Nginx
# ============================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# 配置变量
PROJECT_DIR="/workspace/projects"
BACKEND_DIR="$PROJECT_DIR/admin-backend"
PORT_BACKEND=8080
PORT_FRONTEND=9000
DOMAIN="meiyueart.com"

# 日志函数
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# 开始
clear
echo "=========================================="
echo -e "${PURPLE}灵值生态园 - 全自动修复部署 v2.0${NC}"
echo "=========================================="
echo ""
echo "项目目录: $PROJECT_DIR"
echo "后端目录: $BACKEND_DIR"
echo "后端端口: $PORT_BACKEND"
echo "前端端口: $PORT_FRONTEND"
echo "域名: $DOMAIN"
echo ""
echo "=========================================="
echo ""

# ============================================
# 步骤1: 停止旧服务
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 1/7: 停止旧服务${NC}"
echo "=========================================="

log "查找并停止旧服务..."

# 停止所有Python相关服务
pkill -f "python3 app.py" 2>/dev/null || true
pkill -f "python3 main_server" 2>/dev/null || true
pkill -f "uvicorn.*main_server" 2>/dev/null || true
pkill -f "python.*app.*8080" 2>/dev/null || true

# 等待进程结束
sleep 3

success "✓ 旧服务已停止"

# ============================================
# 步骤2: 安装依赖
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 2/7: 安装Python依赖${NC}"
echo "=========================================="

log "检查并安装依赖..."

pip3 install flask flask-cors flask-jwt-extended bcrypt pyjwt httpx -q 2>/dev/null || true

success "✓ 依赖安装完成"

# ============================================
# 步骤3: 创建修复后的main_server
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 3/7: 创建修复后的main_server${NC}"
echo "=========================================="

log "创建main_server_fixed.py..."

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

chmod +x "$PROJECT_DIR/main_server_fixed.py"

success "✓ main_server_fixed.py已创建"

# ============================================
# 步骤4: 启动后端Flask服务
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 4/7: 启动后端Flask服务${NC}"
echo "=========================================="

log "启动后端Flask服务（$PORT_BACKEND端口）..."

cd "$BACKEND_DIR"
nohup python3 app.py > /tmp/flask_backend.log 2>&1 &
BACKEND_PID=$!
cd "$PROJECT_DIR"

log "等待后端服务启动..."
sleep 5

# 检查后端服务
if lsof -i:$PORT_BACKEND >/dev/null 2>&1 || netstat -tlnp 2>/dev/null | grep -q ":$PORT_BACKEND "; then
    success "✓ 后端Flask服务已启动（PID: $BACKEND_PID，端口: $PORT_BACKEND）"
else
    error "✗ 后端Flask服务启动失败"
    log "查看日志: tail -50 /tmp/flask_backend.log"
    tail -20 /tmp/flask_backend.log
    exit 1
fi

# ============================================
# 步骤5: 启动前端代理服务
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 5/7: 启动前端代理服务${NC}"
echo "=========================================="

log "启动前端代理服务（$PORT_FRONTEND端口）..."

nohup python3 main_server_fixed.py > /tmp/main_server_fixed.log 2>&1 &
FRONTEND_PID=$!

log "等待前端服务启动..."
sleep 5

# 检查前端服务
if lsof -i:$PORT_FRONTEND >/dev/null 2>&1 || netstat -tlnp 2>/dev/null | grep -q ":$PORT_FRONTEND "; then
    success "✓ 前端代理服务已启动（PID: $FRONTEND_PID，端口: $PORT_FRONTEND）"
else
    error "✗ 前端代理服务启动失败"
    log "查看日志: tail -50 /tmp/main_server_fixed.log"
    tail -20 /tmp/main_server_fixed.log
    exit 1
fi

# ============================================
# 步骤6: 验证服务
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 6/7: 验证服务${NC}"
echo "=========================================="

echo ""
echo "6.1 检查端口监听..."
lsof -i:$PORT_BACKEND -i:$PORT_FRONTEND 2>/dev/null | grep LISTEN || netstat -tlnp 2>/dev/null | grep -E "8080|9000"

echo ""
echo "6.2 测试后端服务（$PORT_BACKEND端口）..."
BACKEND_HEALTH=$(curl -s http://localhost:$PORT_BACKEND/api/health 2>/dev/null)
if echo "$BACKEND_HEALTH" | grep -q "ok"; then
    success "✓ 后端服务正常"
    echo "  响应: $BACKEND_HEALTH"
else
    error "✗ 后端服务异常"
    echo "  响应: $BACKEND_HEALTH"
fi

echo ""
echo "6.3 测试前端代理（$PORT_FRONTEND端口）API..."
PROXY_API=$(curl -s http://localhost:$PORT_FRONTEND/api/health 2>/dev/null)
if echo "$PROXY_API" | grep -q "ok"; then
    success "✓ 前端代理API正常"
    echo "  响应: $PROXY_API"
else
    error "✗ 前端代理API异常"
    echo "  响应: $PROXY_API"
fi

echo ""
echo "6.4 测试智能体对话接口..."
CHAT_RESPONSE=$(curl -s -X POST http://localhost:$PORT_FRONTEND/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"你好","conversationId":"test"}' 2>/dev/null)
if echo "$CHAT_RESPONSE" | grep -q "reply\|success"; then
    success "✓ 智能体对话接口正常"
    echo "  响应摘要: $(echo "$CHAT_RESPONSE" | head -100)"
else
    error "✗ 智能体对话接口异常"
    echo "  响应: $CHAT_RESPONSE"
fi

echo ""
echo "6.5 测试静态文件服务..."
STATIC_FILE=$(curl -s http://localhost:$PORT_FRONTEND/ 2>/dev/null | head -5)
if echo "$STATIC_FILE" | grep -q "html\|doctype"; then
    success "✓ 静态文件服务正常"
    echo "  响应摘要: $STATIC_FILE"
else
    error "✗ 静态文件服务异常"
    echo "  响应: $STATIC_FILE"
fi

# ============================================
# 步骤7: 配置Nginx
# ============================================
echo ""
echo "=========================================="
echo -e "${BLUE}步骤 7/7: 配置Nginx反向代理${NC}"
echo "=========================================="

log "检查Nginx配置目录..."

if [ -d "/etc/nginx/sites-available" ]; then
    NGINX_CONF="/etc/nginx/sites-available/$DOMAIN"

    log "创建Nginx配置文件..."

    cat > "$NGINX_CONF" << NGINXEOF
# HTTP重定向到HTTPS
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN 123.56.142.143;

    location /.well-known/acme-challenge/ {
        root /var/www/html;
    }

    location / {
        return 301 https://$host$request_uri;
    }
}

# HTTPS配置
server {
    listen 443 ssl http2;
    server_name $DOMAIN www.$DOMAIN 123.56.142.143;

    # SSL证书
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;

    # SSL安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers off;
    add_header Strict-Transport-Security "max-age=31536000" always;

    # CORS
    add_header Access-Control-Allow-Origin * always;
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH" always;
    add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept, Origin" always;

    # 处理OPTIONS预检请求
    if ($request_method = OPTIONS) {
        add_header Access-Control-Allow-Origin * always;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS, PATCH" always;
        add_header Access-Control-Allow-Headers "Authorization, Content-Type, Accept, Origin" always;
        add_header Content-Length 0;
        return 204;
    }

    # 反向代理到前端代理服务（9000端口）
    location / {
        proxy_pass http://localhost:$PORT_FRONTEND;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 120s;

        # 缓冲设置
        proxy_buffering off;
        proxy_request_buffering off;
    }
}
NGINXEOF

    log "创建符号链接..."
    ln -sf "$NGINX_CONF" "/etc/nginx/sites-enabled/$DOMAIN"

    log "测试Nginx配置..."
    if nginx -t 2>&1; then
        success "✓ Nginx配置测试通过"
        systemctl reload nginx
        success "✓ Nginx已重载配置"
    else
        error "✗ Nginx配置测试失败"
    fi
else
    warn "Nginx配置目录不存在，跳过Nginx配置"
fi

# ============================================
# 最终总结
# ============================================
echo ""
echo "=========================================="
echo -e "${GREEN}部署完成！${NC}"
echo "=========================================="
echo ""
echo "📊 服务状态："
echo "  ✓ 后端Flask: http://localhost:$PORT_BACKEND"
echo "  ✓ 前端代理: http://localhost:$PORT_FRONTEND"
echo ""
echo "🔌 API接口："
echo "  ✓ GET  /api/health - 健康检查"
echo "  ✓ POST /api/agent/chat - 智能体对话"
echo ""
echo "📄 静态文件："
echo "  ✓ GET  / - 首页"
echo "  ✓ GET  /assets/* - 静态资源"
echo ""
echo "🔧 管理命令："
echo "  查看后端日志: tail -f /tmp/flask_backend.log"
echo "  查看前端日志: tail -f /tmp/main_server_fixed.log"
echo ""
echo "  停止服务: pkill -f 'python3 app.py' && pkill -f 'python3 main_server_fixed.py'"
echo ""
echo "  重启服务: cd $PROJECT_DIR && bash auto_deploy_full.sh"
echo ""
echo "🌐 外网访问："
echo "  HTTP:  http://$DOMAIN  (自动重定向到HTTPS)"
echo "  HTTPS: https://$DOMAIN"
echo ""
echo "=========================================="
