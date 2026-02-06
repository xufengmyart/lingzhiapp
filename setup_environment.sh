#!/bin/bash
# ═════════════════════════════════════════════════════════════════════════
# 灵值生态园 - 环境配置初始化脚本
# ═════════════════════════════════════════════════════════════════════════

set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          灵值生态园 - 开发环境配置初始化                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查系统时间
echo ""
echo "【1】检查系统时间..."
SYSTEM_TIME=$(date +%s)
CURRENT_YEAR=$(date +%Y)

if [ "$CURRENT_YEAR" -gt 2025 ]; then
    echo -e "${YELLOW}⚠️  警告: 系统时间异常 (${CURRENT_YEAR}年)${NC}"
    echo "   正在同步系统时间..."
    if command -v ntpdate &> /dev/null; then
        ntpdate -s time.nist.gov || true
    fi
else
    echo -e "${GREEN}✅ 系统时间正常${NC}"
fi

# 2. 检查时区配置
echo ""
echo "【2】检查时区配置..."
CURRENT_TZ=$(timedatectl | grep "Time zone" | awk '{print $3}')
if [ "$CURRENT_TZ" == "Asia/Shanghai" ]; then
    echo -e "${GREEN}✅ 时区配置正确 (Asia/Shanghai)${NC}"
else
    echo -e "${YELLOW}⚠️  当前时区: ${CURRENT_TZ}${NC}"
    echo "   正在设置时区为 Asia/Shanghai..."
    timedatectl set-timezone Asia/Shanghai
    echo -e "${GREEN}✅ 时区已设置${NC}"
fi

# 3. 检查Python环境
echo ""
echo "【3】检查Python环境..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | awk '{print $2}')
    echo -e "${GREEN}✅ Python版本: ${PYTHON_VERSION}${NC}"
else
    echo -e "${RED}❌ Python3未安装${NC}"
    exit 1
fi

# 4. 检查Node.js环境
echo ""
echo "【4】检查Node.js环境..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo -e "${GREEN}✅ Node.js版本: ${NODE_VERSION}${NC}"
else
    echo -e "${RED}❌ Node.js未安装${NC}"
    exit 1
fi

# 5. 检查依赖
echo ""
echo "【5】检查Python依赖..."
REQUIRED_DEPS="flask bcrypt pyjwt paramiko"
MISSING_DEPS=""

for dep in $REQUIRED_DEPS; do
    if ! python3 -c "import $dep" 2>/dev/null; then
        MISSING_DEPS="$MISSING_DEPS $dep"
    fi
done

if [ -n "$MISSING_DEPS" ]; then
    echo -e "${YELLOW}⚠️  缺少依赖:${MISSING_DEPS}${NC}"
    echo "   正在安装依赖..."
    pip3 install $MISSING_DEPS
    echo -e "${GREEN}✅ 依赖已安装${NC}"
else
    echo -e "${GREEN}✅ 所有依赖已安装${NC}"
fi

# 6. 创建必要的目录
echo ""
echo "【6】创建必要的目录..."
mkdir -p admin-backend/logs
mkdir -p admin-backend/backups
mkdir -p public/assets
echo -e "${GREEN}✅ 目录创建完成${NC}"

# 7. 检查环境变量配置
echo ""
echo "【7】检查环境变量配置..."
if [ -f "admin-backend/.env" ]; then
    echo -e "${GREEN}✅ 后端环境配置文件存在${NC}"
else
    echo -e "${RED}❌ 缺少 admin-backend/.env 文件${NC}"
    echo "   正在从 .env.example 创建..."
    cp admin-backend/.env.example admin-backend/.env
    echo -e "${YELLOW}⚠️  请编辑 admin-backend/.env 并配置安全密钥${NC}"
fi

if [ -f ".env" ]; then
    echo -e "${GREEN}✅ 项目环境配置文件存在${NC}"
else
    echo -e "${RED}❌ 缺少 .env 文件${NC}"
    exit 1
fi

# 8. 检查Git配置
echo ""
echo "【8】检查Git配置..."
if [ -f ".gitignore" ]; then
    if grep -q ".env" .gitignore; then
        echo -e "${GREEN}✅ .env 文件已添加到 .gitignore${NC}"
    else
        echo -e "${YELLOW}⚠️  .env 未添加到 .gitignore${NC}"
        echo ".env" >> .gitignore
        echo -e "${GREEN}✅ 已添加到 .gitignore${NC}"
    fi
else
    echo -e "${RED}❌ 缺少 .gitignore 文件${NC}"
    exit 1
fi

# 9. 数据库检查
echo ""
echo "【9】检查数据库..."
if [ -f "admin-backend/lingzhi_ecosystem.db" ]; then
    DB_SIZE=$(du -h admin-backend/lingzhi_ecosystem.db | cut -f1)
    echo -e "${GREEN}✅ 数据库存在 (大小: ${DB_SIZE})${NC}"
else
    echo -e "${YELLOW}⚠️  数据库不存在，将在首次运行时自动创建${NC}"
fi

# 10. 配置完成
echo ""
echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║          环境配置完成！                                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""
echo "后续步骤："
echo "  1. 编辑 admin-backend/.env 配置安全密钥"
echo "  2. 运行后端: cd admin-backend && python3 app.py"
echo "  3. 运行前端: cd web-app && npm run dev"
echo ""
echo -e "${GREEN}✅ 配置完成！${NC}"
