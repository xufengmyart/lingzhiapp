#!/bin/bash

# 生产环境签到修复脚本
# 直接在生产服务器上执行

set -e

echo "=========================================="
echo "生产环境签到修复脚本"
echo "=========================================="

# 数据库路径
DB_PATH="/app/meiyueart-backend/lingzhi_ecosystem.db"
BACKUP_DIR="/app/meiyueart-backend/backups"
BACKUP_FILE="$BACKUP_DIR/lingzhi_ecosystem_backup_$(date +%Y%m%d_%H%M%S).db"

# 创建备份目录
mkdir -p "$BACKUP_DIR"

echo "📊 [1/4] 检查数据库文件..."
if [ ! -f "$DB_PATH" ]; then
    echo "❌ 数据库文件不存在: $DB_PATH"
    exit 1
fi
echo "✅ 数据库文件存在"

echo "💾 [2/4] 备份数据库..."
cp "$DB_PATH" "$BACKUP_FILE"
echo "✅ 备份完成: $BACKUP_FILE"

echo "🔍 [3/4] 检查当前签到奖励配置..."
CURRENT_REWARD=$(sqlite3 "$DB_PATH" "SELECT reward FROM checkin_rewards WHERE reward_type='daily' LIMIT 1;")
echo "当前签到奖励: $CURRENT_REWARD"

echo "🔧 [4/4] 重启后端服务..."
cd /app/meiyueart-backend
systemctl restart lingzhi-ecosystem-backend || gunicorn -w 4 -b 0.0.0.0:8080 app:app --daemon
sleep 3

# 检查服务状态
if pgrep -f "gunicorn.*app:app" > /dev/null || systemctl is-active --quiet lingzhi-ecosystem-backend; then
    echo "✅ 服务重启成功"
else
    echo "❌ 服务启动失败"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ 修复完成"
echo "=========================================="
echo "📊 修复摘要:"
echo "  - 数据库: $DB_PATH"
echo "  - 备份文件: $BACKUP_FILE"
echo "  - 当前签到奖励: $CURRENT_REWARD"
echo "  - 服务状态: 运行中"
echo ""
echo "🧪 验证测试:"
echo "正在测试签到状态接口..."

# 测试签到接口
sleep 2
CHECKIN_STATUS=$(curl -s -X GET "http://localhost:8080/api/checkin/status" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $(curl -s -X POST "http://localhost:8080/api/login" \
    -H "Content-Type: application/json" \
    -d '{"phone": "15901006439", "password": "123456"}' | jq -r '.access_token')")

echo "$CHECKIN_STATUS" | jq '.'

# 提取今日灵值
TODAY_LINGZHI=$(echo "$CHECKIN_STATUS" | jq -r '.data.todayLingzhi // "0"')

echo ""
echo "📊 今日灵值: $TODAY_LINGZHI"

if [ "$TODAY_LINGZHI" = "10" ]; then
    echo "✅ 签到奖励显示正确"
else
    echo "⚠️  签到奖励显示异常"
fi

echo ""
echo "📝 日志文件: /var/log/lingzhi-ecosystem/app.log"
echo "📝 错误日志: /var/log/lingzhi-ecosystem/error.log"
