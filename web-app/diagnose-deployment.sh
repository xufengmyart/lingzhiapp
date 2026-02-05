#!/bin/bash

# 部署诊断脚本 - 检查梦幻版页面部署状态

echo "=========================================="
echo "  梦幻版页面部署诊断脚本"
echo "=========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查函数
check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✓${NC} 文件存在: $1"
        return 0
    else
        echo -e "${RED}✗${NC} 文件不存在: $1"
        return 1
    fi
}

check_dir() {
    if [ -d "$1" ]; then
        echo -e "${GREEN}✓${NC} 目录存在: $1"
        return 0
    else
        echo -e "${RED}✗${NC} 目录不存在: $1"
        return 1
    fi
}

# 1. 检查源文件
echo "1. 检查源文件..."
check_file "web-app/src/pages/LoginFull.tsx"
check_file "web-app/src/pages/RegisterFull.tsx"
check_file "web-app/src/pages/DreamPageSelector.tsx"
check_file "web-app/src/App.tsx"
echo ""

# 2. 检查构建产物
echo "2. 检查构建产物..."
check_dir "public"
check_dir "public/assets"
check_file "public/index.html"
check_file "public/assets/index-*.js"
check_file "public/assets/index-*.css"
echo ""

# 3. 检查index.html内容
echo "3. 检查index.html配置..."
if [ -f "public/index.html" ]; then
    echo "检查index.html中的脚本引用:"
    grep -o 'src="[^"]*"' public/index.html | head -5
    echo ""
fi

# 4. 检查App.tsx路由配置
echo "4. 检查路由配置..."
if grep -q "dream-selector" "web-app/src/App.tsx"; then
    echo -e "${GREEN}✓${NC} dream-selector 路由已配置"
else
    echo -e "${RED}✗${NC} dream-selector 路由未配置"
fi
if grep -q "login-full" "web-app/src/App.tsx"; then
    echo -e "${GREEN}✓${NC} login-full 路由已配置"
else
    echo -e "${RED}✗${NC} login-full 路由未配置"
fi
if grep -q "register-full" "web-app/src/App.tsx"; then
    echo -e "${GREEN}✓${NC} register-full 路由已配置"
else
    echo -e "${RED}✗${NC} register-full 路由未配置"
fi
echo ""

# 5. 检查Nginx配置
echo "5. 检查Nginx配置..."
echo "请检查服务器上的Nginx配置是否包含以下内容:"
echo "  root /var/www/frontend;"
echo "  location / {"
echo "      try_files \$uri \$uri/ /index.html;"
echo "  }"
echo ""

# 6. 提供解决方案
echo "=========================================="
echo "  常见问题和解决方案"
echo "=========================================="
echo ""
echo "问题1: 页面显示空白"
echo "  - 检查浏览器控制台是否有错误"
echo "  - 清除浏览器缓存"
echo "  - 检查index.html中的资源路径是否正确"
echo ""
echo "问题2: 404错误"
echo "  - 确认Nginx配置了try_files"
echo "  - 确认构建产物在正确的目录"
echo "  - 重启Nginx: sudo systemctl restart nginx"
echo ""
echo "问题3: 路由无法访问"
echo "  - 确认React Router使用BrowserRouter"
echo "  - 确认Nginx配置支持SPA路由"
echo ""
echo "=========================================="
echo "  重新构建和部署命令"
echo "=========================================="
echo ""
echo "# 1. 重新构建"
echo "cd web-app"
echo "npm run build"
echo ""
echo "# 2. 上传到服务器"
echo "rsync -avz --delete ../public/* user@123.56.142.143:/var/www/frontend/"
echo ""
echo "# 3. 重启Nginx"
echo "ssh user@123.56.142.143 'sudo systemctl restart nginx'"
echo ""
echo "=========================================="
