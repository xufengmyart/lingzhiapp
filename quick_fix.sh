#!/bin/bash
# 快速修复脚本 - 解决高优先级问题

echo "=================================================="
echo "灵值生态园 - 快速修复脚本"
echo "=================================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 问题1: 清理备份文件
echo -e "${YELLOW}[1/3] 清理备份文件...${NC}"
cd /workspace/projects/admin-backend/backups
if [ -f ../backup_clean.sh ]; then
    chmod +x ../backup_clean.sh
    ../backup_clean.sh
    echo -e "${GREEN}✓ 备份清理完成${NC}"
else
    echo -e "${RED}✗ 备份清理脚本不存在${NC}"
fi
echo ""

# 问题2: 配置ESLint
echo -e "${YELLOW}[2/3] 配置ESLint...${NC}"
cd /workspace/projects/web-app
if [ -f .eslintrc.json ]; then
    echo -e "${GREEN}✓ ESLint配置已存在${NC}"
else
    echo -e "${RED}✗ ESLint配置文件不存在${NC}"
fi

# 检查依赖
if npm list eslint 2>&1 | grep -q "eslint@"; then
    echo -e "${GREEN}✓ ESLint已安装${NC}"
else
    echo -e "${YELLOW}! ESLint未安装，正在安装...${NC}"
    npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-react eslint-plugin-react-hooks 2>&1 | tail -3
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ ESLint安装成功${NC}"
    else
        echo -e "${RED}✗ ESLint安装失败${NC}"
    fi
fi
echo ""

# 问题3: 检查构建包大小
echo -e "${YELLOW}[3/3] 检查构建包大小...${NC}"
if [ -f ../public/assets/index-*.js ]; then
    js_size=$(du -h ../public/assets/index-*.js | cut -f1)
    echo "当前JavaScript包大小: $js_size"
    if [ ${js_size%M} -gt 1 ]; then
        echo -e "${YELLOW}! 包大小超过1MB，建议优化${NC}"
    else
        echo -e "${GREEN}✓ 包大小合理${NC}"
    fi
else
    echo -e "${RED}✗ 构建文件不存在${NC}"
fi
echo ""

# 系统状态检查
echo "=================================================="
echo "系统状态检查"
echo "=================================================="

# 检查Flask服务
if pgrep -f "python3.*app.py" > /dev/null; then
    echo -e "${GREEN}✓ Flask服务运行中${NC}"
else
    echo -e "${RED}✗ Flask服务未运行${NC}"
fi

# 检查集成服务器
if pgrep -f "integrated_server.py" > /dev/null; then
    echo -e "${GREEN}✓ 集成服务器运行中${NC}"
else
    echo -e "${RED}✗ 集成服务器未运行${NC}"
fi

# 检查磁盘空间
disk_usage=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $disk_usage -lt 80 ]; then
    echo -e "${GREEN}✓ 磁盘空间充足 (${disk_usage}%)${NC}"
else
    echo -e "${YELLOW}! 磁盘空间不足 (${disk_usage}%)${NC}"
fi

# 检查数据库
if [ -f admin-backend/lingzhi_ecosystem.db ]; then
    db_size=$(du -h admin-backend/lingzhi_ecosystem.db | cut -f1)
    echo -e "${GREEN}✓ 数据库正常 ($db_size)${NC}"
else
    echo -e "${RED}✗ 数据库不存在${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}快速修复完成！${NC}"
echo "=================================================="
echo ""
echo "下一步建议："
echo "1. 配置HTTPS（参考HTTPS配置指南.md）"
echo "2. 优化前端构建包大小"
echo "3. 集成性能监控系统"
echo ""
echo "详细问题分析请查看: 遗留问题分析报告与解决方案.md"
