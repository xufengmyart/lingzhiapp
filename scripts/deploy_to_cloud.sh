#!/bin/bash

# 灵值生态园云服务器部署脚本
# 使用方法：./scripts/deploy_to_cloud.sh

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 云服务器配置（请根据实际情况修改）
CLOUD_SERVER_IP="123.56.142.143"
CLOUD_SERVER_USER="root"
CLOUD_SERVER_PATH="/root/lingzhi-ecosystem"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  灵值生态园 - 云服务器部署脚本${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 检查本地环境
echo -e "${YELLOW}[1/6] 检查本地环境...${NC}"
if [ ! -f "admin-backend/app.py" ]; then
    echo -e "${RED}错误：未找到后端代码，请确保在项目根目录执行此脚本${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 本地环境检查通过${NC}"

# 构建前端
echo -e "${YELLOW}[2/6] 构建前端...${NC}"
cd web-app
npm run build
if [ $? -ne 0 ]; then
    echo -e "${RED}错误：前端构建失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 前端构建成功${NC}"
cd ..

# 打包代码
echo -e "${YELLOW}[3/6] 打包代码...${NC}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="lingzhi_ecosystem_${TIMESTAMP}.tar.gz"

# 创建临时目录
TEMP_DIR=$(mktemp -d)
mkdir -p ${TEMP_DIR}/{admin-backend,web-app-dist,scripts}

# 复制后端代码
cp -r admin-backend/* ${TEMP_DIR}/admin-backend/
cp admin-backend/requirements.txt ${TEMP_DIR}/admin-backend/ 2>/dev/null || true

# 复制前端构建产物
cp -r web-app/public/* ${TEMP_DIR}/web-app-dist/

# 复制数据库
cp admin-backend/lingzhi_ecosystem.db ${TEMP_DIR}/admin-backend/ 2>/dev/null || true

# 打包
cd ${TEMP_DIR}
tar -czf ${ARCHIVE_NAME} admin-backend web-app-dist
cd - > /dev/null

echo -e "${GREEN}✓ 代码打包完成：${ARCHIVE_NAME}${NC}"

# 上传到云服务器
echo -e "${YELLOW}[4/6] 上传到云服务器...${NC}"
echo -e "${YELLOW}服务器：${CLOUD_SERVER_USER}@${CLOUD_SERVER_IP}${NC}"
echo -e "${YELLOW}目标路径：${CLOUD_SERVER_PATH}${NC}"

# 检查是否可以SSH连接
if ! ssh -o ConnectTimeout=5 -o BatchMode=yes ${CLOUD_SERVER_USER}@${CLOUD_SERVER_IP} exit 2>/dev/null; then
    echo -e "${YELLOW}SSH连接测试失败，请确保：${NC}"
    echo "  1. 已配置SSH密钥认证"
    echo "  2. 或输入密码进行连接"
    echo ""
    read -p "是否继续上传？(y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}部署已取消${NC}"
        exit 0
    fi
fi

# 上传压缩包
scp ${TEMP_DIR}/${ARCHIVE_NAME} ${CLOUD_SERVER_USER}@${CLOUD_SERVER_IP}:/tmp/
if [ $? -ne 0 ]; then
    echo -e "${RED}错误：上传失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 上传成功${NC}"

# 在云服务器上部署
echo -e "${YELLOW}[5/6] 在云服务器上部署...${NC}"
ssh ${CLOUD_SERVER_USER}@${CLOUD_SERVER_IP} << 'ENDSSH'
set -e

# 创建目标目录
mkdir -p /root/lingzhi-ecosystem
mkdir -p /root/lingzhi-ecosystem/backup

# 备份当前版本
if [ -d "/root/lingzhi-ecosystem/admin-backend" ]; then
    echo "备份当前版本..."
    BACKUP_NAME="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf /root/lingzhi-ecosystem/backup/${BACKUP_NAME} \
        /root/lingzhi-ecosystem/admin-backend \
        /root/lingzhi-ecosystem/web-app-dist \
        /root/lingzhi-ecosystem/admin-backend/*.db 2>/dev/null || true
    echo "备份完成：${BACKUP_NAME}"
fi

# 解压新版本
echo "解压新版本..."
cd /tmp
tar -xzf ${ARCHIVE_NAME}
cp -r admin-backend /root/lingzhi-ecosystem/
cp -r web-app-dist /root/lingzhi-ecosystem/

# 安装依赖
echo "安装Python依赖..."
cd /root/lingzhi-ecosystem/admin-backend
pip install -r requirements.txt 2>/dev/null || true

# 停止旧服务
echo "停止旧服务..."
pkill -f "python app.py" 2>/dev/null || true

# 启动新服务
echo "启动后端服务..."
nohup python app.py > /tmp/backend.log 2>&1 &

# 检查服务状态
sleep 3
if pgrep -f "python app.py" > /dev/null; then
    echo "✓ 后端服务启动成功"
else
    echo "✗ 后端服务启动失败，请检查日志：/tmp/backend.log"
    exit 1
fi

ENDSSH

if [ $? -ne 0 ]; then
    echo -e "${RED}错误：云服务器部署失败${NC}"
    exit 1
fi
echo -e "${GREEN}✓ 云服务器部署成功${NC}"

# 清理临时文件
echo -e "${YELLOW}[6/6] 清理临时文件...${NC}"
rm -rf ${TEMP_DIR}
ssh ${CLOUD_SERVER_USER}@${CLOUD_SERVER_IP} "rm -f /tmp/${ARCHIVE_NAME}"
echo -e "${GREEN}✓ 清理完成${NC}"

# 验证部署
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}下一步操作：${NC}"
echo "1. 在阿里云控制台开放以下端口："
echo "   - 80 (HTTP)"
echo "   - 443 (HTTPS)"
echo "   - 8001 (后端API，可选)"
echo ""
echo "2. 访问地址："
echo "   http://${CLOUD_SERVER_IP}"
echo ""
echo "3. 查看日志："
echo "   ssh ${CLOUD_SERVER_USER}@${CLOUD_SERVER_IP} 'tail -f /tmp/backend.log'"
echo ""
echo -e "${YELLOW}注意：${NC}"
echo "- 首次部署可能需要配置Nginx反向代理"
echo "- 如需使用域名访问，请配置DNS解析"
echo ""
