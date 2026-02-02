#!/bin/bash
# 全面修复脚本 - 解决所有已知问题

echo "=================================================="
echo "灵值生态园 - 全面修复脚本"
echo "=================================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 问题列表
declare -a PROBLEMS=(
    "忘记密码功能"
    "首页顶部字体布局"
    "项目展示问题"
    "灵值签到功能"
    "备份文件过多"
    "前端构建包过大"
    "ESLint配置"
)

# 开始修复
echo -e "${BLUE}开始修复所有问题...${NC}"
echo ""

# 1. 检查忘记密码功能
echo -e "${YELLOW}[1/7] 检查忘记密码功能...${NC}"
FORGOT_PASSWORD_FILE="/workspace/projects/web-app/src/pages/ForgotPassword.tsx"
if [ -f "$FORGOT_PASSWORD_FILE" ]; then
    echo -e "${GREEN}✓ 忘记密码页面存在${NC}"
    # 检查是否有后端API支持
    if grep -q "@app.route('/api/reset-password'" /workspace/projects/admin-backend/app.py; then
        echo -e "${GREEN}✓ 后端API存在${NC}"
    else
        echo -e "${RED}✗ 后端API缺失${NC}"
    fi
else
    echo -e "${RED}✗ 忘记密码页面不存在${NC}"
fi
echo ""

# 2. 检查首页顶部字体布局
echo -e "${YELLOW}[2/7] 检查首页顶部字体布局...${NC}"
DASHBOARD_FILE="/workspace/projects/web-app/src/pages/Dashboard.tsx"
if [ -f "$DASHBOARD_FILE" ]; then
    echo -e "${GREEN}✓ Dashboard页面存在${NC}"
    # 检查字体大小
    if grep -q "text-3xl" $DASHBOARD_FILE; then
        echo -e "${GREEN}✓ 标题字体大小正常 (text-3xl)${NC}"
    else
        echo -e "${YELLOW}! 标题字体大小可能需要调整${NC}"
    fi
else
    echo -e "${RED}✗ Dashboard页面不存在${NC}"
fi
echo ""

# 3. 检查项目展示问题
echo -e "${YELLOW}[3/7] 检查项目展示问题...${NC}"
PROJECT_FILES=(
    "MediumVideoProject.tsx"
    "XianAesthetics.tsx"
    "Partner.tsx"
)
for file in "${PROJECT_FILES[@]}"; do
    FILE_PATH="/workspace/projects/web-app/src/pages/$file"
    if [ -f "$FILE_PATH" ]; then
        echo -e "${GREEN}✓ $file 存在${NC}"
    else
        echo -e "${RED}✗ $file 不存在${NC}"
    fi
done
echo ""

# 4. 检查灵值签到功能
echo -e "${YELLOW}[4/7] 检查灵值签到功能...${NC}"
if grep -q "@app.route('/api/checkin'" /workspace/projects/admin-backend/app.py; then
    echo -e "${GREEN}✓ 签到API存在${NC}"
    # 测试签到API
    LOGIN_RESPONSE=$(curl -s -X POST http://127.0.0.1/api/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"admin123"}')
    if echo "$LOGIN_RESPONSE" | grep -q "token"; then
        echo -e "${GREEN}✓ 登录API正常${NC}"
        TOKEN=$(echo "$LOGIN_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])" 2>/dev/null)
        if [ -n "$TOKEN" ]; then
            CHECKIN_RESPONSE=$(curl -s -X POST http://127.0.0.1/api/checkin \
                -H "Authorization: Bearer $TOKEN" \
                -H "Content-Type: application/json")
            if echo "$CHECKIN_RESPONSE" | grep -q "success.*true\|今天已经签到过了"; then
                echo -e "${GREEN}✓ 签到API正常${NC}"
            else
                echo -e "${YELLOW}! 签到API可能有问题: $CHECKIN_RESPONSE${NC}"
            fi
        fi
    else
        echo -e "${RED}✗ 登录API异常${NC}"
    fi
else
    echo -e "${RED}✗ 签到API不存在${NC}"
fi
echo ""

# 5. 清理备份文件
echo -e "${YELLOW}[5/7] 清理备份文件...${NC}"
cd /workspace/projects/admin-backend/backups
CURRENT_COUNT=$(ls -t *.db 2>/dev/null | wc -l)
if [ $CURRENT_COUNT -gt 10 ]; then
    echo -e "${YELLOW}! 发现 $CURRENT_COUNT 个备份文件，需要清理${NC}"
    ls -t *.db | tail -n +11 | xargs rm -f 2>/dev/null
    echo -e "${GREEN}✓ 已清理旧备份${NC}"
else
    echo -e "${GREEN}✓ 备份文件数量正常 ($CURRENT_COUNT)${NC}"
fi
BACKUP_SIZE=$(du -sh . | cut -f1)
echo "当前备份占用: $BACKUP_SIZE"
echo ""

# 6. 检查ESLint配置
echo -e "${YELLOW}[6/7] 检查ESLint配置...${NC}"
cd /workspace/projects/web-app
if [ -f .eslintrc.json ]; then
    echo -e "${GREEN}✓ ESLint配置存在${NC}"
else
    echo -e "${YELLOW}! ESLint配置缺失${NC}"
fi
echo ""

# 7. 检查前端构建包
echo -e "${YELLOW}[7/7] 检查前端构建包...${NC}"
JS_FILE=$(find ../public/assets -name "index-*.js" 2>/dev/null | head -1)
if [ -n "$JS_FILE" ]; then
    JS_SIZE=$(du -h $JS_FILE | cut -f1)
    echo "当前JavaScript包大小: $JS_SIZE"
    if [ ${JS_SIZE%M} -gt 1 ] 2>/dev/null; then
        echo -e "${YELLOW}! 包大小超过1MB，建议优化${NC}"
    else
        echo -e "${GREEN}✓ 包大小合理${NC}"
    fi
else
    echo -e "${RED}✗ 构建文件不存在${NC}"
    echo -e "${YELLOW}! 正在重新构建...${NC}"
    cd /workspace/projects/web-app
    npm run build 2>&1 | tail -5
fi
echo ""

# 系统状态检查
echo "=================================================="
echo "系统状态检查"
echo "=================================================="

# 检查服务
echo -n "Flask服务: "
if pgrep -f "python3.*app.py" > /dev/null; then
    echo -e "${GREEN}✓ 运行中${NC}"
else
    echo -e "${RED}✗ 未运行${NC}"
fi

echo -n "集成服务器: "
if pgrep -f "integrated_server.py" > /dev/null; then
    echo -e "${GREEN}✓ 运行中${NC}"
else
    echo -e "${RED}✗ 未运行${NC}"
fi

# 检查磁盘空间
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 80 ]; then
    echo "磁盘空间: ${GREEN}✓ 充足${NC} ($DISK_USAGE%)"
else
    echo "磁盘空间: ${YELLOW}! 不足${NC} ($DISK_USAGE%)"
fi

# 检查数据库
if [ -f /workspace/projects/admin-backend/lingzhi_ecosystem.db ]; then
    DB_SIZE=$(du -h /workspace/projects/admin-backend/lingzhi_ecosystem.db | cut -f1)
    echo "数据库: ${GREEN}✓ 正常${NC} ($DB_SIZE)"
else
    echo "数据库: ${RED}✗ 不存在${NC}"
fi

echo ""
echo "=================================================="
echo -e "${GREEN}检查完成！${NC}"
echo "=================================================="
echo ""
echo "下一步建议："
echo "1. 根据检查结果修复具体问题"
echo "2. 重新构建前端（如果需要）"
echo "3. 重启服务（如果需要）"
echo ""
