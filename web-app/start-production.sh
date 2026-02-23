#!/bin/bash

# 灵值生态智能体 Web APP 生产环境启动脚本

set -e

echo "========================================"
echo "灵值生态智能体 Web APP 生产部署"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 配置
PORT=${PORT:-3000}
LOG_DIR="/app/work/logs/bypass"
LOG_FILE="$LOG_DIR/web-app-production.log"

# 确保日志目录存在
mkdir -p "$LOG_DIR"

echo -e "${YELLOW}配置信息:${NC}"
echo "  端口: $PORT"
echo "  日志文件: $LOG_FILE"
echo ""

# 检查构建产物
if [ ! -d "dist" ]; then
    echo -e "${RED}错误: dist 目录不存在！${NC}"
    echo "请先运行: npm run build"
    exit 1
fi

# 停止现有的生产服务器
echo -e "${YELLOW}停止现有服务器...${NC}"
pkill -f "production-server.js" || true
sleep 2

# 启动生产服务器
echo -e "${GREEN}启动生产服务器...${NC}"
nohup node production-server.js > "$LOG_FILE" 2>&1 &
SERVER_PID=$!

# 等待服务器启动
echo "等待服务器启动..."
sleep 3

# 检查服务器是否运行
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✓ 服务器已成功启动！${NC}"
    echo "  PID: $SERVER_PID"
    echo "  地址: http://localhost:$PORT"
    echo ""
    echo -e "${YELLOW}查看日志:${NC}"
    echo "  tail -f $LOG_FILE"
    echo ""
    echo -e "${YELLOW}停止服务器:${NC}"
    echo "  pkill -f production-server.js"
else
    echo -e "${RED}✗ 服务器启动失败！${NC}"
    echo "请检查日志: $LOG_FILE"
    exit 1
fi
