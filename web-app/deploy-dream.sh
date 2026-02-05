#!/bin/bash

# 梦幻版页面快速部署脚本

echo "=========================================="
echo "  梦幻版页面部署脚本"
echo "=========================================="
echo ""

# 设置变量
SERVER_USER="user"
SERVER_IP="123.56.142.143"
SERVER_PATH="/var/www/frontend"
LOCAL_BUILD="../public"

# 检查函数
check_error() {
    if [ $? -ne 0 ]; then
        echo -e "\n❌ 错误: $1"
        exit 1
    fi
}

echo "步骤 1/4: 清理旧构建产物..."
rm -rf $LOCAL_BUILD
mkdir -p $LOCAL_BUILD
check_error "无法清理构建目录"

echo "✓ 清理完成"
echo ""

echo "步骤 2/4: 构建前端应用..."
cd web-app
npm run build
check_error "构建失败"

echo "✓ 构建完成"
echo ""

echo "步骤 3/4: 上传到服务器..."
cd ..
rsync -avz --delete $LOCAL_BUILD/* $SERVER_USER@$SERVER_IP:$SERVER_PATH/
check_error "上传失败"

echo "✓ 上传完成"
echo ""

echo "步骤 4/4: 重启Nginx..."
ssh $SERVER_USER@$SERVER_IP "sudo systemctl restart nginx"
check_error "重启Nginx失败"

echo "✓ Nginx已重启"
echo ""

echo "=========================================="
echo "  ✅ 部署完成！"
echo "=========================================="
echo ""
echo "访问地址："
echo "  梦幻风格选择器: https://meiyueart.com/dream-selector"
echo "  梦幻版登录: https://meiyueart.com/login-full"
echo "  梦幻版注册: https://meiyueart.com/register-full"
echo "  设计展示: https://meiyueart.com/design-showcase"
echo ""
echo "测试建议："
echo "  1. 清除浏览器缓存"
echo "  2. 使用无痕模式访问"
echo "  3. 检查浏览器控制台是否有错误"
echo ""
