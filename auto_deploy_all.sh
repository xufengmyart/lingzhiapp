#!/bin/bash
#
# 灵值生态园 - 一键自动化部署脚本
# 完整流程：构建 → 上传 → 部署 → 测试
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 工作目录
WORKSPACE="/workspace/projects"

echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║        灵值生态园 - 完整自动化部署系统                            ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# 显示部署信息
echo -e "${BLUE}📋 部署信息${NC}"
echo "  工作目录: $WORKSPACE"
echo "  服务器: 123.56.142.143"
echo "  域名: meiyueart.com"
echo ""

# 步骤1：构建前端
echo -e "${YELLOW}【步骤1/4】构建前端项目...${NC}"
echo "----------------------------------------"
cd "$WORKSPACE/web-app"
npm run build

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 构建完成${NC}"
else
    echo -e "${RED}❌ 构建失败${NC}"
    exit 1
fi
echo ""

# 步骤2：上传到对象存储
echo -e "${YELLOW}【步骤2/4】上传到对象存储...${NC}"
echo "----------------------------------------"
cd "$WORKSPACE"
python3 upload_frontend_to_storage.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 上传完成${NC}"
else
    echo -e "${RED}❌ 上传失败${NC}"
    exit 1
fi
echo ""

# 步骤3：部署到服务器
echo -e "${YELLOW}【步骤3/4】部署到服务器...${NC}"
echo "----------------------------------------"
python3 execute_deploy_with_password.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 部署完成${NC}"
else
    echo -e "${RED}❌ 部署失败${NC}"
    exit 1
fi
echo ""

# 步骤4：测试验证
echo -e "${YELLOW}【步骤4/4】测试验证...${NC}"
echo "----------------------------------------"
python3 final_test.py

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 测试完成${NC}"
else
    echo -e "${RED}❌ 测试失败${NC}"
    exit 1
fi
echo ""

# 部署完成
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    🎉 部署成功！                                   ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}📱 访问地址：${NC}"
echo "   https://meiyueart.com"
echo ""
echo -e "${BLUE}💡 清除浏览器缓存：${NC}"
echo "   Windows: Ctrl + Shift + R"
echo "   Mac: Cmd + Shift + R"
echo ""
echo -e "${YELLOW}🔍 测试登录：${NC}"
echo "   用户名: admin"
echo "   密码: password123"
echo ""
