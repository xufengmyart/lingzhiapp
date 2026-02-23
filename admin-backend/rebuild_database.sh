#!/bin/bash
# 重建数据库文件

DB_FILE="/workspace/projects/admin-backend/data/lingzhi_ecosystem.db"
BACKUP_DIR="/workspace/projects/admin-backend/data/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR"

# 备份现有数据库
if [ -f "$DB_FILE" ]; then
    echo "备份现有数据库..."
    cp "$DB_FILE" "$BACKUP_DIR/lingzhi_ecosystem.db.backup.$TIMESTAMP"
    echo "✅ 数据库已备份到: $BACKUP_DIR/lingzhi_ecosystem.db.backup.$TIMESTAMP"
fi

# 删除现有数据库和WAL文件
echo "删除现有数据库..."
rm -f "$DB_FILE"
rm -f "$DB_FILE-wal"
rm -f "$DB_FILE-shm"

echo "✅ 数据库已删除，将在下次启动时自动重建"
