#!/bin/bash

echo "=========================================="
echo "灵值生态园 APP 部署测试"
echo "=========================================="

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 测试1: 检查dist目录
echo -e "${YELLOW}[1/5] 检查dist目录...${NC}"
if [ -d "dist" ]; then
    echo -e "${GREEN}✓ dist目录存在${NC}"
else
    echo -e "${RED}✗ dist目录不存在${NC}"
    exit 1
fi

# 测试2: 检查index.html
echo -e "${YELLOW}[2/5] 检查index.html...${NC}"
if [ -f "dist/index.html" ]; then
    echo -e "${GREEN}✓ index.html存在${NC}"
else
    echo -e "${RED}✗ index.html不存在${NC}"
    exit 1
fi

# 测试3: 检查JS文件
echo -e "${YELLOW}[3/5] 检查JS文件...${NC}"
JS_COUNT=$(find dist -name "*.js" | wc -l)
if [ $JS_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ 找到 $JS_COUNT 个JS文件${NC}"
else
    echo -e "${RED}✗ 未找到JS文件${NC}"
    exit 1
fi

# 测试4: 检查CSS文件
echo -e "${YELLOW}[4/5] 检查CSS文件...${NC}"
CSS_COUNT=$(find dist -name "*.css" | wc -l)
if [ $CSS_COUNT -gt 0 ]; then
    echo -e "${GREEN}✓ 找到 $CSS_COUNT 个CSS文件${NC}"
else
    echo -e "${RED}✗ 未找到CSS文件${NC}"
    exit 1
fi

# 测试5: 检查文件大小
echo -e "${YELLOW}[5/5] 检查构建产物大小...${NC}"
TOTAL_SIZE=$(du -sh dist | cut -f1)
echo -e "${GREEN}✓ 总大小: $TOTAL_SIZE${NC}"

echo ""
echo "=========================================="
echo -e "${GREEN}所有测试通过！✓${NC}"
echo "=========================================="
echo ""
echo "构建产物列表:"
ls -lh dist/
echo ""
echo "子目录列表:"
ls -lh dist/assets/ 2>/dev/null || echo "无子目录"
