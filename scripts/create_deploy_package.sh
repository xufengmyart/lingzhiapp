#!/bin/bash

# 部署包打包脚本
# 将所有必要文件打包，方便上传到云服务器

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================="
echo "  灵值生态园 - 部署包打包"
echo "========================================="
echo ""

# 临时目录
TEMP_DIR=$(mktemp -d)
echo "临时目录: ${TEMP_DIR}"

# 项目路径
PROJECT_PATH="/workspace/projects"

# 步骤1：构建前端
echo -e "${YELLOW}[1/5] 构建前端...${NC}"
cd ${PROJECT_PATH}/web-app
npm run build
echo -e "${GREEN}✓ 前端构建完成${NC}"

# 步骤2：创建目录结构
echo -e "${YELLOW}[2/5] 创建目录结构...${NC}"
mkdir -p ${TEMP_DIR}/{admin-backend,web-app-dist,scripts}
echo -e "${GREEN}✓ 目录结构创建完成${NC}"

# 步骤3：复制后端文件
echo -e "${YELLOW}[3/5] 复制后端文件...${NC}"
cp -r ${PROJECT_PATH}/admin-backend/* ${TEMP_DIR}/admin-backend/

# 排除不需要的文件
rm -rf ${TEMP_DIR}/admin-backend/__pycache__
rm -rf ${TEMP_DIR}/admin-backend/.pytest_cache
rm -rf ${TEMP_DIR}/admin-backend/*.pyc

echo -e "${GREEN}✓ 后端文件复制完成${NC}"
echo "  文件数量: $(find ${TEMP_DIR}/admin-backend -type f | wc -l)"

# 步骤4：复制前端文件
echo -e "${YELLOW}[4/5] 复制前端文件...${NC}"
cp -r ${PROJECT_PATH}/public/* ${TEMP_DIR}/web-app-dist/
echo -e "${GREEN}✓ 前端文件复制完成${NC}"
echo "  文件数量: $(find ${TEMP_DIR}/web-app-dist -type f | wc -l)"

# 步骤5：复制部署脚本
echo -e "${YELLOW}[5/5] 复制部署脚本...${NC}"
cp ${PROJECT_PATH}/scripts/cloud_auto_deploy.sh ${TEMP_DIR}/scripts/
chmod +x ${TEMP_DIR}/scripts/cloud_auto_deploy.sh
echo -e "${GREEN}✓ 部署脚本复制完成${NC}"

# 打包
echo ""
echo "========================================="
echo "  打包文件"
echo "========================================="

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_NAME="lingzhi_ecosystem_deploy_${TIMESTAMP}.tar.gz"
ARCHIVE_PATH="${PROJECT_PATH}/${ARCHIVE_NAME}"

cd ${TEMP_DIR}
tar -czf ${ARCHIVE_PATH} admin-backend web-app-dist scripts

ARCHIVE_SIZE=$(du -h ${ARCHIVE_PATH} | cut -f1)
echo -e "${GREEN}✓ 打包完成${NC}"
echo "  文件名: ${ARCHIVE_NAME}"
echo "  大小: ${ARCHIVE_SIZE}"
echo "  路径: ${ARCHIVE_PATH}"

# 显示包内容
echo ""
echo "包内容:"
echo "  admin-backend/ - 后端代码"
echo "  web-app-dist/ - 前端文件"
echo "  scripts/cloud_auto_deploy.sh - 自动部署脚本"

# 清理临时目录
rm -rf ${TEMP_DIR}

echo ""
echo "========================================="
echo "  下一步操作"
echo "========================================="
echo ""
echo "1. 上传到云服务器:"
echo "   scp ${ARCHIVE_NAME} root@123.56.142.143:/tmp/"
echo ""
echo "2. 解压并部署:"
echo "   ssh root@123.56.142.143"
echo "   cd /tmp"
echo "   tar -xzf ${ARCHIVE_NAME}"
echo "   cd admin-backend"
echo "   ../scripts/cloud_auto_deploy.sh"
echo ""
echo "3. 访问应用:"
echo "   http://123.56.142.143"
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  打包完成！${NC}"
echo -e "${GREEN}========================================${NC}"
