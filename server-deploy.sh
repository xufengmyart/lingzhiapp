#!/bin/bash

# ==========================================
#  梦幻版页面 - 服务器端直接部署脚本
#  在服务器上直接运行此脚本
# ==========================================

set -e

echo "=========================================="
echo "  梦幻版页面 - 服务器端部署开始"
echo "  服务器: $(hostname)"
echo "  时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "=========================================="
echo ""

# 配置
FRONTEND_DIR="/var/www/frontend"
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"

# 颜色
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 步骤1：检查环境
echo -e "${BLUE}步骤 1/5: 检查环境${NC}"
echo "----------------------------"

if [ ! -d "$FRONTEND_DIR" ]; then
    mkdir -p "$FRONTEND_DIR"
    echo -e "${GREEN}✓${NC} 创建前端目录: $FRONTEND_DIR"
else
    echo -e "${GREEN}✓${NC} 前端目录存在: $FRONTEND_DIR"
fi
echo ""

# 步骤2：备份
echo -e "${BLUE}步骤 2/5: 备份现有文件${NC}"
echo "----------------------------"

if [ "$(ls -A $FRONTEND_DIR 2>/dev/null)" ]; then
    echo "备份到: $BACKUP_DIR"
    cp -r "$FRONTEND_DIR" "$BACKUP_DIR"
    echo -e "${GREEN}✓${NC} 备份完成"
else
    echo -e "${YELLOW}⚠${NC} 前端目录为空，跳过备份"
fi
echo ""

# 步骤3：检查构建产物
echo -e "${BLUE}步骤 3/5: 检查构建产物${NC}"
echo "----------------------------"

BUILD_DIR=""
for dir in "/root/public" "/root/web-app/public" "/var/www/public"; do
    if [ -d "$dir" ] && [ -f "$dir/index.html" ]; then
        BUILD_DIR="$dir"
        break
    fi
done

if [ -z "$BUILD_DIR" ]; then
    echo -e "${YELLOW}⚠${NC} 未找到构建产物，尝试从位置1复制..."

    # 方案1：如果文件在其他位置
    if [ -f "/root/dream-frontend-deploy.tar.gz" ]; then
        echo "找到tar包，正在解压..."
        mkdir -p /tmp/dream-deploy
        tar -xzf /root/dream-frontend-deploy.tar.gz -C /tmp/dream-deploy
        BUILD_DIR="/tmp/dream-deploy"
    else
        echo -e "${RED}✗${NC} 错误：找不到构建产物"
        echo ""
        echo "请执行以下命令之一："
        echo "  1. 上传tar包: scp dream-frontend-deploy.tar.gz root@$(hostname):/root/"
        echo "  2. 或在服务器上构建: npm run build (需要项目代码)"
        exit 1
    fi
fi

echo "构建产物位置: $BUILD_DIR"
echo ""

# 步骤4：部署
echo -e "${BLUE}步骤 4/5: 部署文件${NC}"
echo "----------------------------"

rm -rf "$FRONTEND_DIR"/*
cp -r "$BUILD_DIR"/* "$FRONTEND_DIR"/

echo -e "${GREEN}✓${NC} 文件复制完成"
echo ""

# 步骤5：设置权限和重启
echo -e "${BLUE}步骤 5/5: 设置权限并重启Nginx${NC}"
echo "----------------------------"

chown -R root:root "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"
echo -e "${GREEN}✓${NC} 权限设置完成"

if systemctl restart nginx 2>/dev/null; then
    echo -e "${GREEN}✓${NC} Nginx已重启"
else
    echo -e "${YELLOW}⚠${NC} Nginx重启失败，请手动执行: systemctl restart nginx"
fi
echo ""

# 验证
echo "=========================================="
echo "  部署结果"
echo "=========================================="
echo ""

if [ -f "$FRONTEND_DIR/index.html" ]; then
    echo -e "${GREEN}✓${NC} index.html 存在"
else
    echo -e "${RED}✗${NC} index.html 不存在"
fi

JS_FILE=$(ls -1 $FRONTEND_DIR/assets/index-*.js 2>/dev/null | head -1)
if [ -n "$JS_FILE" ]; then
    JS_SIZE=$(ls -lh "$JS_FILE" | awk '{print $5}')
    JS_NAME=$(basename "$JS_FILE")
    echo -e "${GREEN}✓${NC} $JS_NAME ($JS_SIZE)"
else
    echo -e "${RED}✗${NC} JS文件不存在"
fi

CSS_FILE=$(ls -1 $FRONTEND_DIR/assets/index-*.css 2>/dev/null | head -1)
if [ -n "$CSS_FILE" ]; then
    CSS_SIZE=$(ls -lh "$CSS_FILE" | awk '{print $5}')
    CSS_NAME=$(basename "$CSS_FILE")
    echo -e "${GREEN}✓${NC} $CSS_NAME ($CSS_SIZE)"
else
    echo -e "${RED}✗${NC} CSS文件不存在"
fi

echo ""
echo "备份位置: $BACKUP_DIR"
echo ""

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
echo "  3. 如有问题，恢复备份: cp -r $BACKUP_DIR/* $FRONTEND_DIR/"
echo ""
