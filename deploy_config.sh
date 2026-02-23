#!/bin/bash
################################################################################
# 部署配置文件
# 用途: 存储生产环境配置信息
################################################################################

# ========== 服务器配置 ==========
PRODUCTION_SERVER="user@meiyueart.com"
PRODUCTION_URL="https://meiyueart.com"
APP_PATH="/var/www/meiyueart.com/admin-backend"

# ========== 数据库配置 ==========
DB_PATH="$APP_PATH/data/lingzhi_ecosystem.db"

# ========== 服务配置 ==========
SERVICE_NAME="lingzhi_admin_backend"
SUPERVISOR_CONFIG="/etc/supervisor/conf.d/lingzhi.conf"

# ========== 备份配置 ==========
BACKUP_DIR="$HOME/backups"
RETENTION_DAYS=30

# ========== API配置 ==========
API_BASE="$PRODUCTION_URL/api"

# ========== 告警配置 ==========
ALERT_EMAIL="ops@meiyueart.com"

# ========== 验证配置 ==========
MAX_RESPONSE_TIME=5000  # 5秒
HEALTH_CHECK_URL="$API_BASE/health"

# ========== 日志配置 ==========
LOG_FILE="/var/log/flask_backend.log"
ERROR_LOG="/var/log/flask_error.log"
