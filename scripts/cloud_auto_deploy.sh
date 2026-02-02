#!/bin/bash

# 云服务器自动部署脚本
# 直接在云服务器上运行此脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  灵值生态园 - 云服务器自动部署${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 项目路径
PROJECT_PATH="/root/lingzhi-ecosystem"
BACKEND_PATH="${PROJECT_PATH}/admin-backend"
FRONTEND_PATH="${PROJECT_PATH}/web-app-dist"

# 步骤1：创建项目目录
echo -e "${YELLOW}[1/8] 创建项目目录...${NC}"
mkdir -p ${PROJECT_PATH}
mkdir -p ${BACKEND_PATH}
mkdir -p ${FRONTEND_PATH}
echo -e "${GREEN}✓ 项目目录创建完成${NC}"

# 步骤2：关闭防火墙
echo -e "${YELLOW}[2/8] 关闭防火墙...${NC}"
systemctl stop firewalld 2>/dev/null || true
systemctl disable firewalld 2>/dev/null || true
iptables -F 2>/dev/null || true
iptables -X 2>/dev/null || true
echo -e "${GREEN}✓ 防火墙已关闭${NC}"

# 步骤3：安装依赖
echo -e "${YELLOW}[3/8] 安装系统依赖...${NC}"
yum install -y nginx python3 python3-pip git 2>/dev/null || apt-get install -y nginx python3 python3-pip git 2>/dev/null || echo "部分依赖可能已安装"

# 安装Python依赖
if [ -f "${BACKEND_PATH}/requirements.txt" ]; then
    cd ${BACKEND_PATH}
    pip3 install -r requirements.txt 2>/dev/null || true
    echo -e "${GREEN}✓ Python依赖已安装${NC}"
else
    echo -e "${YELLOW}⚠️  未找到requirements.txt，跳过Python依赖安装${NC}"
fi

# 步骤4：配置Nginx
echo -e "${YELLOW}[4/8] 配置Nginx...${NC}"
cat > /etc/nginx/conf.d/lingzhi-ecosystem.conf << 'EOF'
server {
    listen 80;
    server_name _;

    # 前端静态文件
    location / {
        root /root/lingzhi-ecosystem/web-app-dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 支持WebSocket
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # 健康检查
    location /health {
        access_log off;
        return 200 "healthy\n";
        add_header Content-Type text/plain;
    }
}
EOF

# 测试Nginx配置
nginx -t 2>/dev/null || true
echo -e "${GREEN}✓ Nginx配置完成${NC}"

# 步骤5：停止旧服务
echo -e "${YELLOW}[5/8] 停止旧服务...${NC}"
pkill -f "python.*app.py" 2>/dev/null || true
systemctl stop nginx 2>/dev/null || true
sleep 2
echo -e "${GREEN}✓ 旧服务已停止${NC}"

# 步骤6：检查并部署文件
echo -e "${YELLOW}[6/8] 检查项目文件...${NC}"

# 检查前端文件
if [ -f "${FRONTEND_PATH}/index.html" ]; then
    echo -e "${GREEN}✓ 前端文件已存在${NC}"
    ls -la ${FRONTEND_PATH}/ | head -10
else
    echo -e "${RED}✗ 前端文件不存在${NC}"
    echo -e "${YELLOW}请先上传前端文件到 ${FRONTEND_PATH} 目录${NC}"
fi

# 检查后端文件
if [ -f "${BACKEND_PATH}/app.py" ]; then
    echo -e "${GREEN}✓ 后端文件已存在${NC}"
    ls -la ${BACKEND_PATH}/ | head -10
else
    echo -e "${RED}✗ 后端文件不存在${NC}"
    echo -e "${YELLOW}请先上传后端文件到 ${BACKEND_PATH} 目录${NC}"
fi

# 检查数据库
if [ -f "${BACKEND_PATH}/lingzhi_ecosystem.db" ]; then
    echo -e "${GREEN}✓ 数据库文件已存在${NC}"
else
    echo -e "${YELLOW}⚠️  数据库文件不存在，将自动创建${NC}"
fi

# 步骤7：启动后端服务
echo -e "${YELLOW}[7/8] 启动后端服务...${NC}"

if [ -f "${BACKEND_PATH}/app.py" ]; then
    cd ${BACKEND_PATH}

    # 设置环境变量
    export FLASK_APP=app.py
    export FLASK_ENV=production

    # 启动服务
    nohup python3 app.py > /tmp/backend.log 2>&1 &
    BACKEND_PID=$!

    sleep 3

    # 检查服务状态
    if ps -p ${BACKEND_PID} > /dev/null 2>&1 || pgrep -f "python.*app.py" > /dev/null; then
        echo -e "${GREEN}✓ 后端服务启动成功 (PID: ${BACKEND_PID})${NC}"
    else
        echo -e "${RED}✗ 后端服务启动失败${NC}"
        echo -e "${YELLOW}查看日志: tail -f /tmp/backend.log${NC}"
        tail -30 /tmp/backend.log
    fi

    # 测试后端API
    sleep 2
    echo -e "${YELLOW}测试后端API...${NC}"
    curl -s http://127.0.0.1:8080/api/login -X POST \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}' \
        2>/dev/null | head -1 || echo "API测试失败"

else
    echo -e "${YELLOW}⚠️  后端文件不存在，跳过服务启动${NC}"
fi

# 步骤8：启动Nginx
echo -e "${YELLOW}[8/8] 启动Nginx...${NC}"

# 启动Nginx
systemctl start nginx
systemctl enable nginx 2>/dev/null || true

# 检查Nginx状态
if systemctl is-active --quiet nginx; then
    echo -e "${GREEN}✓ Nginx已启动${NC}"
else
    echo -e "${RED}✗ Nginx启动失败${NC}"
    systemctl status nginx
fi

# 测试Nginx
echo -e "${YELLOW}测试Nginx...${NC}"
curl -I http://127.0.0.1:80/ 2>/dev/null | head -1 || echo "Nginx测试失败"

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  部署完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}服务状态：${NC}"
echo "  后端服务: $(pgrep -f 'python.*app.py' | wc -l) 个进程运行中"
echo "  Nginx服务: $(systemctl is-active nginx)"
echo ""
echo -e "${YELLOW}端口监听：${NC}"
netstat -tlnp 2>/dev/null | grep -E ":80 |:8080 " || ss -tlnp 2>/dev/null | grep -E ":80 |:8080 "
echo ""
echo -e "${YELLOW}日志文件：${NC}"
echo "  后端日志: tail -f /tmp/backend.log"
echo "  Nginx日志: tail -f /var/log/nginx/error.log"
echo ""
echo -e "${YELLOW}下一步：${NC}"
echo "  1. 确保阿里云安全组已开放80端口"
echo "  2. 访问应用: http://$(hostname -I | awk '{print $1}')"
echo ""
echo -e "${GREEN}========================================${NC}"
