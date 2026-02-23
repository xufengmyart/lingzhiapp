#!/bin/bash

################################################################################
# 灵值生态园 - 配置自动监控 Cron 任务
# 用途：将健康检查脚本添加到 crontab，每分钟运行一次
# 作者：Coze Coding
# 版本：v1.0
# 日期：2026-02-11
################################################################################

set -e

# 配置变量
APP_DIR="/var/www/meiyueart"
HEALTH_CHECK_SCRIPT="$APP_DIR/scripts/health-check.sh"
LOG_FILE="/var/log/health-check.log"

echo "========================================="
echo "配置自动监控 Cron 任务"
echo "========================================="
echo ""

# 检查脚本是否存在
if [ ! -f "$HEALTH_CHECK_SCRIPT" ]; then
    echo "错误: 健康检查脚本不存在: $HEALTH_CHECK_SCRIPT"
    exit 1
fi

# 赋予执行权限
chmod +x $HEALTH_CHECK_SCRIPT

# 创建日志文件
touch $LOG_FILE
chmod 644 $LOG_FILE

# 备份当前 crontab
CRON_BACKUP="/tmp/crontab.backup.$(date +%Y%m%d_%H%M%S)"
crontab -l > $CRON_BACKUP 2>/dev/null || true

# 检查是否已存在健康检查任务
if crontab -l 2>/dev/null | grep -q "health-check.sh"; then
    echo "⚠️  健康检查任务已存在，将替换为新的配置"
    
    # 删除旧的 cron 任务
    crontab -l 2>/dev/null | grep -v "health-check.sh" > /tmp/new_crontab || true
    crontab /tmp/new_crontab
fi

# 添加新的 cron 任务（每分钟运行一次）
(crontab -l 2>/dev/null; echo "* * * * * $HEALTH_CHECK_SCRIPT >> $LOG_FILE 2>&1") | crontab -

echo "✅ Cron 任务配置完成"
echo ""
echo "Cron 任务详情："
crontab -l | grep health-check.sh
echo ""
echo "日志文件: $LOG_FILE"
echo "查看日志: tail -f $LOG_FILE"
echo ""
echo "备份的 crontab: $CRON_BACKUP"
echo ""
echo "========================================="
echo "配置完成！健康检查将每分钟自动运行"
echo "========================================="
