#!/bin/bash

# 灵值智能体 v8.1 - 云服务器部署脚本
# 功能：将情绪系统数据库持久化代码同步到云服务器

set -e  # 遇到错误立即退出

echo "=========================================="
echo "灵值智能体 v8.1 - 云服务器部署脚本"
echo "=========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 配置变量（请根据实际情况修改）
REMOTE_USER="your_username"        # 云服务器用户名
REMOTE_HOST="your_server_ip"       # 云服务器IP
REMOTE_PATH="/var/www/backend"     # 云服务器项目路径
SERVICE_NAME="lingzhi-backend"     # 服务名称

# 需要同步的文件
FILES=(
    "src/storage/database/shared/model.py"
    "src/storage/database/emotion_manager.py"
    "src/tools/emotion_tools.py"
    "scripts/test_emotion_database.py"
)

echo -e "${YELLOW}[1/5] 检查本地文件...${NC}"
for file in "${FILES[@]}"; do
    if [ ! -f "$file" ]; then
        echo -e "${RED}错误: 文件 $file 不存在${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ $file${NC}"
done

echo -e "\n${YELLOW}[2/5] 备份本地文件...${NC}"
BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
for file in "${FILES[@]}"; do
    cp "$file" "$BACKUP_DIR/"
done
echo -e "${GREEN}✓ 备份完成: $BACKUP_DIR${NC}"

echo -e "\n${YELLOW}[3/5] 上传文件到云服务器...${NC}"
for file in "${FILES[@]}"; do
    echo "正在上传: $file"
    scp "$file" "$REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/$(dirname $file)/"
done
echo -e "${GREEN}✓ 文件上传完成${NC}"

echo -e "\n${YELLOW}[4/5] 在云服务器上执行数据库迁移...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" << 'ENDSSH'
cd /var/www/backend

# 创建数据库迁移SQL
cat > /tmp/emotion_tables.sql << 'SQLEOF'
-- 创建情绪记录表
CREATE TABLE IF NOT EXISTS emotion_records (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    emotion VARCHAR(20) NOT NULL,
    emotion_name VARCHAR(20) NOT NULL,
    intensity FLOAT NOT NULL,
    context TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT now()
);

-- 创建情绪日记表
CREATE TABLE IF NOT EXISTS emotion_diaries (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    content TEXT NOT NULL,
    emotion VARCHAR(20) NOT NULL,
    emotion_name VARCHAR(20) NOT NULL,
    intensity FLOAT NOT NULL,
    tags JSON,
    created_at TIMESTAMP NOT NULL DEFAULT now())
;

-- 创建索引
CREATE INDEX IF NOT EXISTS ix_emotion_records_user_id ON emotion_records(user_id);
CREATE INDEX IF NOT EXISTS ix_emotion_records_created_at ON emotion_records(created_at);
CREATE INDEX IF NOT EXISTS ix_emotion_records_emotion ON emotion_records(emotion);

CREATE INDEX IF NOT EXISTS ix_emotion_diaries_user_id ON emotion_diaries(user_id);
CREATE INDEX IF NOT EXISTS ix_emotion_diaries_created_at ON emotion_diaries(created_at);

-- 添加表注释
COMMENT ON TABLE emotion_records IS '情绪记录表';
COMMENT ON TABLE emotion_diaries IS '情绪日记表';
SQLEOF

# 执行SQL（请根据实际情况修改数据库连接参数）
psql -h localhost -U postgres -d lingzhi_db -f /tmp/emotion_tables.sql

echo "数据库表创建完成"
ENDSSH
echo -e "${GREEN}✓ 数据库迁移完成${NC}"

echo -e "\n${YELLOW}[5/5] 重启服务...${NC}"
ssh "$REMOTE_USER@$REMOTE_HOST" "sudo systemctl restart $SERVICE_NAME"
echo -e "${GREEN}✓ 服务重启完成${NC}"

echo -e "\n${GREEN}=========================================="
echo "部署完成！"
echo "==========================================${NC}"

echo -e "\n${YELLOW}后续验证步骤：${NC}"
echo "1. 检查服务状态:"
echo "   ssh $REMOTE_USER@$REMOTE_HOST 'sudo systemctl status $SERVICE_NAME'"
echo ""
echo "2. 查看日志:"
echo "   ssh $REMOTE_USER@$REMOTE_HOST 'tail -f /var/www/backend/logs/app.log'"
echo ""
echo "3. 运行测试:"
echo "   ssh $REMOTE_USER@$REMOTE_HOST 'cd /var/www/backend && python scripts/test_emotion_database.py'"

echo -e "\n${GREEN}如果遇到问题，可以从 $BACKUP_DIR 恢复文件${NC}"
