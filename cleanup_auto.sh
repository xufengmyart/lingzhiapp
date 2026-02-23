#!/bin/bash
# 灵值生态园项目 - 自动清理脚本
# 用于定期清理项目中的垃圾文件

set -e

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_DIR="/workspace/projects"
BACKEND_DIR="$PROJECT_DIR/admin-backend"
FRONTEND_DIR="$PROJECT_DIR/web-app"

# 日志函数
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 显示欢迎信息
echo "========================================="
echo "🧹 灵值生态园项目 - 自动清理脚本"
echo "========================================="
echo ""

# 检查项目目录是否存在
if [ ! -d "$PROJECT_DIR" ]; then
    log_error "项目目录不存在: $PROJECT_DIR"
    exit 1
fi

log_info "开始清理项目..."

# 1. 清理 Python 编译文件
log_info "清理 Python 编译文件 (.pyc)..."
PYC_COUNT=$(find "$PROJECT_DIR" -name "*.pyc" -type f | wc -l)
if [ "$PYC_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -name "*.pyc" -delete
    log_info "已删除 $PYC_COUNT 个 .pyc 文件"
else
    log_info "没有找到 .pyc 文件"
fi

# 2. 清理 Python 缓存目录
log_info "清理 Python 缓存目录 (__pycache__)..."
PYCACHE_COUNT=$(find "$PROJECT_DIR" -name "__pycache__" -type d | wc -l)
if [ "$PYCACHE_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null
    log_info "已删除 $PYCACHE_COUNT 个 __pycache__ 目录"
else
    log_info "没有找到 __pycache__ 目录"
fi

# 3. 清理前端构建产物
log_info "清理前端构建产物 (dist/)..."
if [ -d "$FRONTEND_DIR/dist" ]; then
    rm -rf "$FRONTEND_DIR/dist"
    log_info "已删除 dist 目录"
else
    log_info "dist 目录不存在"
fi

# 4. 清理 Vite 缓存
log_info "清理 Vite 缓存..."
VITE_CACHE=$(find "$FRONTEND_DIR" -name ".vite" -type d | wc -l)
if [ "$VITE_CACHE" -gt 0 ]; then
    find "$FRONTEND_DIR" -name ".vite" -type d -exec rm -rf {} + 2>/dev/null
    log_info "已清理 Vite 缓存"
else
    log_info "Vite 缓存不存在"
fi

# 5. 清理旧备份文件（保留最近30天）
log_info "清理旧备份文件（保留最近30天）..."
BACKUP_COUNT=$(find "$PROJECT_DIR" -name "*.backup*" -type f -mtime +30 | wc -l)
if [ "$BACKUP_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -name "*.backup*" -type f -mtime +30 -delete
    log_info "已删除 $BACKUP_COUNT 个旧备份文件"
else
    log_info "没有找到超过30天的备份文件"
fi

# 6. 清理 SQLite 临时文件
log_info "清理 SQLite 临时文件..."
WAL_COUNT=$(find "$PROJECT_DIR" -name "*.db-wal" -type f | wc -l)
SHM_COUNT=$(find "$PROJECT_DIR" -name "*.db-shm" -type f | wc -l)
if [ "$WAL_COUNT" -gt 0 ] || [ "$SHM_COUNT" -gt 0 ]; then
    find "$PROJECT_DIR" -name "*.db-wal" -delete
    find "$PROJECT_DIR" -name "*.db-shm" -delete
    log_info "已清理 SQLite 临时文件"
else
    log_info "没有找到 SQLite 临时文件"
fi

# 7. 清理临时文件
log_info "清理临时文件..."
find "$PROJECT_DIR" -type f \( -name "*.tmp" -o -name "*.temp" -o -name "*~" -o -name ".DS_Store" \) -delete
log_info "临时文件清理完成"

# 8. 清理日志文件（保留最近7天）
log_info "清理旧日志文件（保留最近7天）..."
LOG_COUNT=$(find "$BACKEND_DIR/logs" -name "*.log" -type f -mtime +7 2>/dev/null | wc -l)
if [ "$LOG_COUNT" -gt 0 ]; then
    find "$BACKEND_DIR/logs" -name "*.log" -type f -mtime +7 -delete
    log_info "已删除 $LOG_COUNT 个旧日志文件"
else
    log_info "没有找到超过7天的日志文件"
fi

# 9. 显示磁盘空间
echo ""
log_info "当前磁盘空间："
df -h "$PROJECT_DIR" | tail -1 | awk '{print "  总容量: "$2", 已使用: "$3", 可用: "$4", 使用率: "$5}'

# 10. 显示项目大小
echo ""
log_info "项目大小："
du -sh "$PROJECT_DIR/admin-backend" "$PROJECT_DIR/web-app" "$PROJECT_DIR/scripts" | awk '{print "  "$2": "$1}'

# 完成提示
echo ""
echo "========================================="
log_info "✅ 清理完成！"
echo "========================================="
echo ""
echo "清理统计："
echo "  - .pyc 文件: $PYC_COUNT 个"
echo "  - __pycache__ 目录: $PYCACHE_COUNT 个"
echo "  - 旧备份文件: $BACKUP_COUNT 个"
echo "  - SQLite 临时文件: $((WAL_COUNT + SHM_COUNT)) 个"
echo "  - 旧日志文件: $LOG_COUNT 个"
echo ""
echo "下次清理建议时间：7天后"
echo ""
