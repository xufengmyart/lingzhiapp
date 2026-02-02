#!/bin/bash
# 紧急修复脚本 - 解决用户反馈的具体问题

echo "=================================================="
echo "灵值生态园 - 紧急修复"
echo "=================================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 1. 检查Dashboard页面结构
echo -e "${BLUE}[1] 检查Dashboard页面结构${NC}"
if grep -q "项目入口" /workspace/projects/web-app/src/pages/Dashboard.tsx; then
    echo -e "${GREEN}✓ 找到项目入口部分${NC}"
    grep -A 5 "项目入口" /workspace/projects/web-app/src/pages/Dashboard.tsx | head -10
else
    echo -e "${RED}✗ 未找到项目入口部分${NC}"
fi
echo ""

# 2. 检查是否有文件名显示问题
echo -e "${BLUE}[2] 检查文件名显示${NC}"
# 搜索可能显示文件名的地方
FILES=$(grep -rn "File:" /workspace/projects/web-app/src/ 2>/dev/null | grep -v node_modules | grep -v ".git")
if [ -n "$FILES" ]; then
    echo -e "${YELLOW}发现文件名显示代码:${NC}"
    echo "$FILES"
else
    echo -e "${GREEN}✓ 未发现文件名显示代码${NC}"
fi
echo ""

# 3. 重新构建前端
echo -e "${BLUE}[3] 重新构建前端${NC}"
cd /workspace/projects/web-app
npm run build 2>&1 | tail -10
echo ""

# 4. 检查构建结果
echo -e "${BLUE}[4] 检查构建结果${NC}"
if [ -f ../public/index.html ]; then
    echo -e "${GREEN}✓ 前端构建成功${NC}"
    echo "构建文件:"
    ls -lh ../public/assets/ 2>/dev/null
else
    echo -e "${RED}✗ 前端构建失败${NC}"
fi
echo ""

# 5. 重启集成服务器
echo -e "${BLUE}[5] 重启集成服务器${NC}"
pkill -f "integrated_server.py"
sleep 2
nohup python3 /workspace/projects/integrated_server.py > /tmp/integrated_server.log 2>&1 &
sleep 2
if pgrep -f "integrated_server.py" > /dev/null; then
    echo -e "${GREEN}✓ 集成服务器已重启${NC}"
else
    echo -e "${RED}✗ 集成服务器重启失败${NC}"
fi
echo ""

# 6. 测试访问
echo -e "${BLUE}[6] 测试访问${NC}"
curl -s -o /dev/null -w "首页访问: HTTP %{http_code}\n" http://127.0.0.1/
curl -s -o /dev/null -w "API访问: HTTP %{http_code}\n" http://127.0.0.1/api/health
echo ""

echo "=================================================="
echo -e "${GREEN}修复完成！${NC}"
echo "=================================================="
echo ""
echo "请刷新浏览器，检查以下内容："
echo "1. 首页是否有'项目入口'部分（中视频、西安美学侦探、合伙人计划）"
echo "2. 是否还有'File: [assets/image.png]'字体排列问题"
echo ""
echo "如果问题仍然存在，请提供更多详细信息："
echo "1. 截图或具体的问题描述"
echo "2. 问题出现的具体页面"
echo "3. 浏览器和版本信息"
echo ""
