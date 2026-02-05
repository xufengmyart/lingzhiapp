#!/bin/bash

# ==========================================
#  梦幻版页面自动部署脚本
#  在服务器上直接运行此脚本
# ==========================================

set -e

echo "=========================================="
echo "  梦幻版页面自动部署开始"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"
EXPECTED_JS="index-CkydMeua.js"
EXPECTED_CSS="index-CxUAxLXV.css"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 步骤1：检查环境
echo -e "${BLUE}步骤 1/6: 检查环境${NC}"
echo "----------------------------"

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}✗${NC} 错误：前端目录不存在: $FRONTEND_DIR"
    exit 1
fi

echo -e "${GREEN}✓${NC} 前端目录存在: $FRONTEND_DIR"
echo ""

# 步骤2：备份现有文件
echo -e "${BLUE}步骤 2/6: 备份现有文件${NC}"
echo "----------------------------"

if [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ]; then
    echo "备份现有文件到: $BACKUP_DIR"
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓${NC} 备份完成"
else
    echo -e "${YELLOW}⚠${NC} 前端目录为空，跳过备份"
fi
echo ""

# 步骤3：清空目标目录
echo -e "${BLUE}步骤 3/6: 清空目标目录${NC}"
echo "----------------------------"

rm -rf "$FRONTEND_DIR"/*
echo -e "${GREEN}✓${NC} 目标目录已清空"
echo ""

# 步骤4：复制新构建产物
echo -e "${BLUE}步骤 4/6: 复制新构建产物${NC}"
echo "----------------------------"

# 检查构建产物位置
BUILD_DIR=""
if [ -d "/workspace/projects/public" ]; then
    BUILD_DIR="/workspace/projects/public"
elif [ -d "./public" ]; then
    BUILD_DIR="./public"
elif [ -d "./web-app/public" ]; then
    BUILD_DIR="./web-app/public"
else
    echo -e "${RED}✗${NC} 错误：找不到构建产物目录"
    echo "请将构建产物放在以下位置之一："
    echo "  - /workspace/projects/public"
    echo "  - ./public"
    echo "  - ./web-app/public"
    exit 1
fi

echo "构建产物位置: $BUILD_DIR"

if [ ! -f "$BUILD_DIR/index.html" ]; then
    echo -e "${RED}✗${NC} 错误：找不到 index.html"
    exit 1
fi

if [ ! -d "$BUILD_DIR/assets" ]; then
    echo -e "${RED}✗${NC} 错误：找不到 assets 目录"
    exit 1
fi

echo "复制文件..."
cp -r "$BUILD_DIR"/* "$FRONTEND_DIR/"
echo -e "${GREEN}✓${NC} 文件复制完成"
echo ""

# 步骤5：设置权限
echo -e "${BLUE}步骤 5/6: 设置权限${NC}"
echo "----------------------------"

chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
echo -e "${GREEN}✓${NC} 权限设置完成"
echo ""

# 步骤6：验证部署
echo -e "${BLUE}步骤 6/6: 验证部署${NC}"
echo "----------------------------"

# 检查关键文件
if [ ! -f "$FRONTEND_DIR/index.html" ]; then
    echo -e "${RED}✗${NC} 错误：index.html 不存在"
    exit 1
fi

if [ ! -f "$FRONTEND_DIR/assets/$EXPECTED_JS" ]; then
    echo -e "${RED}✗${NC} 错误：找不到 $EXPECTED_JS"
    echo "实际存在的文件："
    ls -lh "$FRONTEND_DIR/assets/"
    exit 1
fi

if [ ! -f "$FRONTEND_DIR/assets/$EXPECTED_CSS" ]; then
    echo -e "${RED}✗${NC} 错误：找不到 $EXPECTED_CSS"
    echo "实际存在的文件："
    ls -lh "$FRONTEND_DIR/assets/"
    exit 1
fi

echo -e "${GREEN}✓${NC} 所有关键文件验证通过"
echo ""

# 显示部署结果
echo "=========================================="
echo "  ✅ 部署成功！"
echo "=========================================="
echo ""
echo "部署信息："
echo "  目标目录: $FRONTEND_DIR"
echo "  备份位置: $BACKUP_DIR"
echo ""
echo "部署的文件："
ls -lh "$FRONTEND_DIR/assets/" | grep -E '\.(js|css)$' | awk '{print "  " $9 " (" $5 ")"}'
echo ""

# 重启Nginx
echo "正在重启Nginx..."
if systemctl restart nginx 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Nginx已重启"
else
    echo -e "${YELLOW}⚠${NC} Nginx重启失败，请手动执行："
    echo "  systemctl restart nginx"
fi
echo ""

# 显示访问地址
echo "=========================================="
echo "  访问地址"
echo "=========================================="
echo ""
echo -e "  梦幻风格选择器: ${GREEN}https://meiyueart.com/dream-selector${NC}"
echo -e "  梦幻版登录: ${GREEN}https://meiyueart.com/login-full${NC}"
echo -e "  梦幻版注册: ${GREEN}https://meiyueart.com/register-full${NC}"
echo ""

echo "提示："
echo "  1. 清除浏览器缓存 (Ctrl+Shift+R)"
echo "  2. 使用无痕模式测试"
echo "  3. 如有问题，恢复备份："
echo "     cp -r $BACKUP_DIR/* $FRONTEND_DIR/"
echo ""
