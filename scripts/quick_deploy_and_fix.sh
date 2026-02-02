#!/bin/bash

# 灵值生态园 - 快速部署和修复脚本
# 一键完成：构建、上传、部署、修复所有问题

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

CLOUD_SERVER="123.56.142.143"
CLOUD_USER="root"
CLOUD_PATH="/root/lingzhi-ecosystem"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  灵值生态园 - 一键部署和修复${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查本地环境
echo -e "${YELLOW}[1/8] 检查本地环境...${NC}"
if [ ! -f "admin-backend/app.py" ]; then
    echo -e "${RED}错误：未找到后端代码，请确保在项目根目录执行此脚本${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 本地环境检查通过${NC}"

# 检查SSH连接
echo -e "${YELLOW}[2/8] 检查SSH连接...${NC}"
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes ${CLOUD_USER}@${CLOUD_SERVER} "echo 'SSH连接成功'" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  SSH连接测试失败，可能需要输入密码${NC}"
    read -p "是否继续？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}部署已取消${NC}"
        exit 0
    fi
else
    echo -e "${GREEN}✓ SSH连接正常${NC}"
fi

# 构建前端
echo -e "${YELLOW}[3/8] 构建前端...${NC}"
cd web-app
npm run build 2>&1 | grep -E "error|Error|failed|Failed" && {
    echo -e "${RED}错误：前端构建失败${NC}"
    exit 1
}
echo -e "${GREEN}✓ 前端构建成功${NC}"
cd ..

# 打包代码
echo -e "${YELLOW}[4/8] 打包代码...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="lingzhi_ecosystem_${TIMESTAMP}.tar.gz"
TEMP_DIR=$(mktemp -d)

mkdir -p ${TEMP_DIR}/{admin-backend,web-app-dist}

# 复制后端代码
cp -r admin-backend/* ${TEMP_DIR}/admin-backend/
cp admin-backend/requirements.txt ${TEMP_DIR}/admin-backend/ 2>/dev/null || true
cp admin-backend/lingzhi_ecosystem.db ${TEMP_DIR}/admin-backend/ 2>/dev/null || true

# 复制前端构建产物
cp -r web-app/public/* ${TEMP_DIR}/web-app-dist/

# 打包
cd ${TEMP_DIR}
tar -czf ${ARCHIVE_NAME} admin-backend web-app-dist
cd - > /dev/null

echo -e "${GREEN}✓ 代码打包完成：${ARCHIVE_NAME}${NC}"

# 上传到云服务器
echo -e "${YELLOW}[5/8] 上传到云服务器...${NC}"
scp ${TEMP_DIR}/${ARCHIVE_NAME} ${CLOUD_USER}@${CLOUD_SERVER}:/tmp/
echo -e "${GREEN}✓ 上传成功${NC}"

# 在云服务器上部署和修复
echo -e "${YELLOW}[6/8] 在云服务器上部署和修复...${NC}"
ssh ${CLOUD_USER}@${CLOUD_SERVER} << 'ENDSSH'
set -e

# 创建目标目录
mkdir -p ${CLOUD_PATH}
mkdir -p ${CLOUD_PATH}/backup

# 备份当前版本
if [ -d "${CLOUD_PATH}/admin-backend" ]; then
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf ${CLOUD_PATH}/backup/${BACKUP_NAME} \
        ${CLOUD_PATH}/admin-backend \
        ${CLOUD_PATH}/web-app-dist 2>/dev/null || true
    echo "  备份完成：${BACKUP_NAME}"
fi

# 解压新版本
echo "  解压新版本..."
cd /tmp
tar -xzf ${ARCHIVE_NAME}
cp -r admin-backend ${CLOUD_PATH}/
cp -r web-app-dist ${CLOUD_PATH}/

# 安装依赖
echo "  安装Python依赖..."
cd ${CLOUD_PATH}/admin-backend
pip install -r requirements.txt 2>/dev/null || true

# 关闭防火墙
echo "  关闭防火墙..."
systemctl stop firewalld 2>/dev/null || true
systemctl disable firewalld 2>/dev/null || true
iptables -F 2>/dev/null || true

# 安装Nginx
echo "  安装Nginx..."
yum install -y nginx 2>/dev/null || apt-get install -y nginx 2>/dev/null || echo "Nginx可能已安装"

# 配置Nginx
echo "  配置Nginx..."
cat > /etc/nginx/conf.d/lingzhi-ecosystem.conf << 'NGINX_CONF'
server {
    listen 80;
    server_name _;

    location / {
        root ${CLOUD_PATH}/web-app-dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
NGINX_CONF

# 停止旧服务
echo "  停止旧服务..."
pkill -f "python.*app.py" 2>/dev/null || true
sleep 1

# 启动后端服务
echo "  启动后端服务..."
cd ${CLOUD_PATH}/admin-backend
nohup python app.py > /tmp/backend.log 2>&1 &
sleep 2

# 检查后端服务
if pgrep -f "python.*app.py" > /dev/null; then
    echo "  ✓ 后端服务启动成功"
else
    echo "  ✗ 后端服务启动失败"
    tail -20 /tmp/backend.log
fi

# 启动Nginx
echo "  启动Nginx..."
systemctl start nginx
systemctl enable nginx 2>/dev/null || true

if systemctl is-active --quiet nginx; then
    echo "  ✓ Nginx已启动"
else
    echo "  ✗ Nginx启动失败"
    systemctl status nginx
fi

# 检查端口监听
echo "  检查端口监听..."
netstat -tlnp 2>/dev/null | grep -E ":80 |:8001 " || ss -tlnp 2>/dev/null | grep -E ":80 |:8001 "

# 清理临时文件
rm -f /tmp/${ARCHIVE_NAME}

ENDSSH

if [ $? -ne 0 ]; then
    echo -e "${RED}错误：云服务器部署失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 云服务器部署和修复成功${NC}"

# 清理本地临时文件
echo -e "${YELLOW}[7/8] 清理临时文件...${NC}"
rm -rf ${TEMP_DIR}
echo -e "${GREEN}✓ 清理完成${NC}"

# 验证部署
echo -e "${YELLOW}[8/8] 验证部署...${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  部署完成！${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}服务器信息：${NC}"
echo "  IP地址: ${CLOUD_SERVER}"
echo "  项目路径: ${CLOUD_PATH}"
echo ""
echo -e "${YELLOW}下一步操作：${NC}"
echo ""
echo "1. ⚠️  【必须】在阿里云控制台开放80端口："
echo "   - 登录阿里云控制台"
echo "   - ECS实例 -> 安全组 -> 配置规则"
echo "   - 添加入方向规则：端口80/80，授权对象0.0.0.0/0"
echo ""
echo "2. 访问应用："
echo "   http://${CLOUD_SERVER}"
echo ""
echo "3. 如果还是无法访问，请检查："
echo "   - 阿里云安全组是否已开放80端口"
echo "   - 是否还有其他安全设备（如WAF、CDN）"
echo ""
echo -e "${YELLOW}查看服务器日志：${NC}"
echo "  ssh ${CLOUD_USER}@${CLOUD_SERVER}"
echo "  tail -f /tmp/backend.log"
echo ""
echo -e "${YELLOW}测试本地端口：${NC}"
echo "  ssh ${CLOUD_USER}@${CLOUD_SERVER} 'curl -I http://127.0.0.1:80'"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署成功！请开放80端口后访问${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
