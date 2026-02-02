#!/bin/bash
# 备份清理脚本
# 保留最近10个备份文件

BACKUP_DIR="/workspace/projects/admin-backend/backups"
MAX_BACKUPS=10
LOG_FILE="/var/log/backup_clean.log"

echo "==================================================" >> $LOG_FILE
echo "备份清理开始: $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE

cd $BACKUP_DIR

# 统计当前备份文件数量
current_count=$(ls -t *.db 2>/dev/null | wc -l)
echo "当前备份文件数量: $current_count" >> $LOG_FILE

if [ $current_count -gt $MAX_BACKUPS ]; then
    # 删除超过MAX_BACKUPS个的旧备份
    delete_count=$((current_count - MAX_BACKUPS))
    echo "需要删除 $delete_count 个旧备份" >> $LOG_FILE

    ls -t *.db | tail -n +$((MAX_BACKUPS + 1)) | while read file; do
        echo "删除备份文件: $file" >> $LOG_FILE
        rm -f "$file"
    done

    echo "已删除 $delete_count 个旧备份" >> $LOG_FILE
else
    echo "备份文件数量未超过限制，无需清理" >> $LOG_FILE
fi

# 统计清理后的备份文件数量和磁盘空间
final_count=$(ls -t *.db 2>/dev/null | wc -l)
final_size=$(du -sh . | cut -f1)

echo "清理后备份文件数量: $final_count" >> $LOG_FILE
echo "清理后磁盘占用: $final_size" >> $LOG_FILE
echo "备份清理完成: $(date '+%Y-%m-%d %H:%M:%S')" >> $LOG_FILE
echo "==================================================" >> $LOG_FILE
echo "" >> $LOG_FILE

echo "备份清理完成，保留最近$MAX_BACKUPS个备份"
echo "当前备份文件数量: $final_count"
echo "磁盘占用: $final_size"
