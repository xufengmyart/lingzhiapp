#!/bin/bash

# 闭环部署脚本 - 梦幻版页面部署

echo "=========================================="
echo "  梦幻版页面闭环部署脚本"
echo "=========================================="
echo ""

# 服务器配置
SERVER_USER="root"  # 根据实际情况修改
SERVER_IP="123.56.142.143"
SERVER_PATH="/var/www/frontend"
LOCAL_BUILD="public"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "步骤 1/4: 检查本地构建产物..."
if [ ! -d "$LOCAL_BUILD" ]; then
    echo -e "${RED}✗${NC} 构建产物不存在: $LOCAL_BUILD"
    exit 1
fi

echo -e "${GREEN}✓${NC} 构建产物检查完成"
echo ""

echo "步骤 2/4: 上传到服务器..."
rsync -avz --delete \
    --exclude='.git' \
    --exclude='node_modules' \
    $LOCAL_BUILD/* \
    $SERVER_USER@$SERVER_IP:$SERVER_PATH/

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} 上传失败"
    echo ""
    echo "请检查："
    echo "  1. 服务器IP是否正确: $SERVER_IP"
    echo "  2. SSH密钥是否配置"
    echo "  3. 网络连接是否正常"
    exit 1
fi

echo -e "${GREEN}✓${NC} 上传完成"
echo ""

echo "步骤 3/4: 重启Nginx..."
ssh $SERVER_USER@$SERVER_IP "systemctl restart nginx"

if [ $? -ne 0 ]; then
    echo -e "${RED}✗${NC} Nginx重启失败"
    exit 1
fi

echo -e "${GREEN}✓${NC} Nginx已重启"
echo ""

echo "步骤 4/4: 验证部署..."
echo "请在浏览器中测试以下URL:"
echo ""
echo "  梦幻风格选择器: ${YELLOW}https://meiyueart.com/dream-selector${NC}"
echo "  梦幻版登录: ${YELLOW}https://meiyueart.com/login-full${NC}"
echo "  梦幻版注册: ${YELLOW}https://meiyueart.com/register-full${NC}"
echo ""
echo "提示："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 使用无痕模式测试"
echo "  3. 检查浏览器控制台是否有错误"
echo ""

echo "=========================================="
echo "  ✅ 闭环部署完成！"
echo "=========================================="
