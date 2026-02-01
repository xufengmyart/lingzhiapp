#!/bin/bash

# 微信登录功能快速部署脚本
# 用于快速配置和部署微信登录功能到生产环境

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
SERVER_USER="root"
SERVER_HOST="123.56.142.143"
SERVER_PASSWORD="Meiyue@root123"
SERVER_PATH="/var/www"
BACKEND_PATH="${SERVER_PATH}/backend"
FRONTEND_DIST="${SERVER_PATH}/html"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}微信登录功能快速部署脚本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 步骤 1：检查配置
echo -e "${YELLOW}[步骤 1/6]${NC} 检查配置文件..."

if [ ! -f "admin-backend/.env" ]; then
    echo -e "${RED}✗ 未找到 admin-backend/.env 文件${NC}"
    echo -e "${YELLOW}正在创建示例配置文件...${NC}"
    cp admin-backend/.env.example admin-backend/.env
    echo -e "${GREEN}✓ 已创建 admin-backend/.env 文件${NC}"
    echo -e "${YELLOW}请编辑 admin-backend/.env 文件，填写微信配置信息：${NC}"
    echo ""
    cat << 'EOF'
WECHAT_APP_ID=wx1234567890abcdef
WECHAT_APP_SECRET=1234567890abcdef1234567890abcdef
WECHAT_REDIRECT_URI=https://your-domain.com/wechat/callback
EOF
    echo ""
    echo -e "${YELLOW}编辑完成后，重新运行此脚本${NC}"
    exit 1
fi

# 检查是否已配置微信
if grep -q "your-wechat-app-id" admin-backend/.env; then
    echo -e "${RED}✗ 微信配置尚未填写${NC}"
    echo -e "${YELLOW}请编辑 admin-backend/.env 文件，填写真实的微信配置信息${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 配置文件检查通过${NC}"
echo ""

# 步骤 2：上传后端代码
echo -e "${YELLOW}[步骤 2/6]${NC} 上传后端代码到服务器..."

export SSHPASS="$SERVER_PASSWORD"
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" "mkdir -p $BACKEND_PATH"

rsync -avz --delete \
    -e "sshpass -e ssh -o StrictHostKeyChecking=no" \
    "admin-backend/" \
    "$SERVER_USER@$SERVER_HOST:$BACKEND_PATH/"

echo -e "${GREEN}✓ 后端代码上传完成${NC}"
echo ""

# 步骤 3：上传前端构建产物
echo -e "${YELLOW}[步骤 3/6]${NC} 构建并上传前端代码..."

echo -e "${YELLOW}正在构建前端...${NC}"
cd web-app
npm run build > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 前端构建成功${NC}"
else
    echo -e "${RED}✗ 前端构建失败${NC}"
    exit 1
fi

cd ..

echo -e "${YELLOW}正在上传前端构建产物...${NC}"
rsync -avz --delete \
    -e "sshpass -e ssh -o StrictHostKeyChecking=no" \
    "web-app/dist/" \
    "$SERVER_USER@$SERVER_HOST:$FRONTEND_DIST/"

echo -e "${GREEN}✓ 前端代码上传完成${NC}"
echo ""

# 步骤 4：安装依赖和重启服务
echo -e "${YELLOW}[步骤 4/6]${NC} 安装依赖并重启服务..."

sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << EOF
cd $BACKEND_PATH
pip3 install -r requirements.txt > /dev/null 2>&1
systemctl restart lingzhi-api
sleep 2
systemctl status lingzhi-api --no-pager
EOF

echo -e "${GREEN}✓ 后端服务重启完成${NC}"
echo ""

# 步骤 5：更新 Nginx 配置
echo -e "${YELLOW}[步骤 5/6]${NC} 更新 Nginx 配置..."

# 创建 Nginx 配置
cat > /tmp/wechat-login-nginx.conf << 'EOF'
server {
    listen 80;
    server_name _;

    # 前端静态文件
    location / {
        root /var/www/html;
        try_files $uri $uri/ /index.html;
    }

    # 后端 API 代理
    location /api/ {
        proxy_pass http://localhost:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 上传 Nginx 配置
sshpass -e scp -o StrictHostKeyChecking=no \
    /tmp/wechat-login-nginx.conf \
    "$SERVER_USER@$SERVER_HOST:/etc/nginx/sites-available/default"

# 测试并重启 Nginx
sshpass -e ssh -o StrictHostKeyChecking=no "$SERVER_USER@$SERVER_HOST" << 'EOF'
nginx -t && systemctl reload nginx
EOF

echo -e "${GREEN}✓ Nginx 配置更新完成${NC}"
echo ""

# 步骤 6：验证部署
echo -e "${YELLOW}[步骤 6/6]${NC} 验证部署..."

# 测试后端 API
API_TEST=$(curl -s "http://${SERVER_HOST}:8001/api/public/users/recent?limit=1")

if [[ $API_TEST == *"success"* ]]; then
    echo -e "${GREEN}✓ 后端 API 测试通过${NC}"
else
    echo -e "${RED}✗ 后端 API 测试失败${NC}"
    echo -e "${YELLOW}响应：${NC}$API_TEST"
fi

echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}下一步操作：${NC}"
echo ""
echo "1. 在微信开放平台配置授权回调域："
echo "   - 登录：https://open.weixin.qq.com/"
echo "   - 进入应用详情页"
echo "   - 设置授权回调域为：$(grep WECHAT_REDIRECT_URI admin-backend/.env | cut -d'=' -f2 | sed 's/\/wechat\/callback//')"
echo ""
echo "2. 重启后端服务使配置生效："
echo "   ssh root@${SERVER_HOST} 'systemctl restart lingzhi-api'"
echo ""
echo "3. 测试微信登录："
echo "   - 访问：http://${SERVER_HOST}"
echo "   - 点击登录 -> 微信登录"
echo "   - 扫码授权并验证"
echo ""
echo "4. 查看后端日志："
echo "   ssh root@${SERVER_HOST} 'journalctl -u lingzhi-api -f'"
echo ""
echo -e "${YELLOW}常见问题排查：${NC}"
echo "- 查看《微信登录功能详细操作指南.md》"
echo "- 查看后端日志：ssh root@${SERVER_HOST} 'journalctl -u lingzhi-api -n 50'"
echo "- 查看 Nginx 日志：ssh root@${SERVER_HOST} 'tail -f /var/log/nginx/error.log'"
echo ""
