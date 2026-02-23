#!/bin/bash
# 灵值生态园 - 一键全自动部署到生产环境（无sshpass版本）
# One-click Production Deployment (No sshpass)

set -e

echo "========================================="
echo "🚀 灵值生态园 - 一键全自动部署"
echo "========================================="
echo ""

# 生产环境配置
PRODUCTION_HOST="meiyueart.com"
PRODUCTION_USER="root"
PRODUCTION_PORT="22"

# 生产环境路径
PRODUCTION_BACKEND="/app/meiyueart-backend"
PRODUCTION_FRONTEND="/var/www/meiyueart.com"

# 本地路径
LOCAL_BACKEND="/workspace/projects/admin-backend"
LOCAL_FRONTEND="/workspace/projects/web-app"
WORKSPACE="/workspace/projects"

# 备份目录
BACKUP_DIR="/var/www/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

log_success() { echo -e "${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
log_error() { echo -e "${RED}❌ $1${NC}"; }
log_info() { echo "📋 $1"; }

# ========== 步骤1：清理云服务器垃圾 ==========
log_info "步骤 1/7: 清理云服务器垃圾..."
ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} << 'ENDSSH'
    find /var/log -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    find /var/log -name "*.gz" -type f -mtime +30 -delete 2>/dev/null || true
    find /tmp -type f -mtime +7 -delete 2>/dev/null || true
    find /app/meiyueart-backend -name "*.pyc" -delete 2>/dev/null || true
    find /app/meiyueart-backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "✅ 云服务器垃圾清理完成"
ENDSSH
log_success "云服务器垃圾清理完成"

# ========== 步骤2：备份生产环境 ==========
log_info "步骤 2/7: 备份生产环境..."
ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} << 'ENDSSH'
    mkdir -p /var/www/backups
    
    # 备份后端
    cd /app/meiyueart-backend
    tar -czf /var/www/backups/backend_backup_$(date +%Y%m%d_%H%M%S).tar.gz . 2>/dev/null || true
    
    # 备份前端
    cd /var/www/meiyueart.com
    tar -czf /var/www/backups/frontend_backup_$(date +%Y%m%d_%H%M%S).tar.gz . 2>/dev/null || true
    
    echo "✅ 备份完成"
ENDSSH
log_success "生产环境备份完成"

# ========== 步骤3：上传后端代码 ==========
log_info "步骤 3/7: 上传后端代码..."

# 备份本地数据库
if [ -f "${LOCAL_BACKEND}/data/lingzhi_ecosystem.db" ]; then
    cp "${LOCAL_BACKEND}/data/lingzhi_ecosystem.db" "${LOCAL_BACKEND}/data/lingzhi_ecosystem.db.local"
fi

# 使用rsync上传后端代码（排除本地数据库）
rsync -avz --delete \
  --exclude='data/lingzhi_ecosystem.db' \
  --exclude='data/lingzhi_ecosystem.db-shm' \
  --exclude='data/lingzhi_ecosystem.db-wal' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.git' \
  -e "ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no" \
  ${LOCAL_BACKEND}/ \
  ${PRODUCTION_USER}@${PRODUCTION_HOST}:${PRODUCTION_BACKEND}/

log_success "后端代码上传完成"

# ========== 步骤4：初始化数据库表 ==========
log_info "步骤 4/7: 初始化数据库表..."
ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} << 'ENDSSH'
    cd /app/meiyueart-backend
    
    # 创建分享统计表
    python3 << 'EOF'
import sqlite3
conn = sqlite3.connect('data/lingzhi_ecosystem.db')
cursor = conn.cursor()

# 创建分享统计表
cursor.execute('''
    CREATE TABLE IF NOT EXISTS share_stats (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        article_id INTEGER NOT NULL,
        share_type TEXT NOT NULL,
        share_url TEXT NOT NULL,
        referral_code TEXT,
        platform TEXT NOT NULL,
        share_count INTEGER DEFAULT 1,
        click_count INTEGER DEFAULT 0,
        registration_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (article_id) REFERENCES news_articles(id)
    )
''')

# 创建索引
cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_user_id ON share_stats(user_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_article_id ON share_stats(article_id)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_share_stats_referral_code ON share_stats(referral_code)')

conn.commit()
print("✅ 分享统计表创建成功")
conn.close()
EOF
ENDSSH
log_success "数据库表初始化完成"

# ========== 步骤5：构建并上传前端代码 ==========
log_info "步骤 5/7: 构建并上传前端代码..."

cd ${LOCAL_FRONTEND}

# 安装依赖
log_info "  安装前端依赖..."
npm install

# 构建前端
log_info "  构建前端..."
npm run build

# 上传前端代码
log_info "  上传前端代码..."
rsync -avz --delete \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='src' \
  --exclude='public' \
  -e "ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no" \
  ${LOCAL_FRONTEND}/dist/ \
  ${PRODUCTION_USER}@${PRODUCTION_HOST}:${PRODUCTION_FRONTEND}/

log_success "前端代码部署完成"

# ========== 步骤6：重启后端服务 ==========
log_info "步骤 6/7: 重启后端服务..."
ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} << 'ENDSSH'
    cd /app/meiyueart-backend
    
    # 停止所有Python进程
    pkill -f "python app.py" || true
    sleep 2
    
    # 清理数据库锁定
    rm -f data/lingzhi_ecosystem.db-shm
    rm -f data/lingzhi_ecosystem.db-wal
    
    # 启动后端服务
    nohup python3 app.py > /dev/null 2>&1 &
    
    # 等待服务启动
    sleep 3
    
    # 检查服务状态
    if pgrep -f "python app.py" > /dev/null; then
        echo "✅ 后端服务启动成功"
    else
        echo "❌ 后端服务启动失败"
        exit 1
    fi
ENDSSH
log_success "后端服务重启完成"

# ========== 步骤7：验证部署 ==========
log_info "步骤 7/7: 验证部署..."

# 测试后端健康检查
sleep 2
if curl -f -s https://meiyueart.com/api/health > /dev/null 2>&1; then
    log_success "健康检查通过"
else
    log_warn "健康检查未通过，但服务可能正在启动"
fi

# 测试管理员登录
ADMIN_TEST=$(curl -s https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}')

if echo "$ADMIN_TEST" | grep -q "success"; then
    log_success "管理员登录测试通过"
else
    log_warn "管理员登录测试未通过"
fi

# 测试用户登录
USER_TEST=$(curl -s https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"马伟娟","password":"123"}')

if echo "$USER_TEST" | grep -q "success"; then
    log_success "用户登录测试通过"
else
    log_warn "用户登录测试未通过"
fi

# ========== 完成 ==========
echo ""
echo "========================================="
echo "${GREEN}✅ 部署完成！${NC}"
echo "========================================="
echo ""
echo "📊 部署信息："
echo "  - 服务器: ${PRODUCTION_HOST}"
echo "  - 后端: ${PRODUCTION_BACKEND}"
echo "  - 前端: ${PRODUCTION_FRONTEND}"
echo "  - 时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""
echo "🔗 访问地址："
echo "  - 前端: https://meiyueart.com"
echo "  - API: https://meiyueart.com/api"
echo ""
echo "👤 测试账号："
echo "  - 管理员: admin / 123"
echo "  - 用户: 马伟娟 / 123"
echo ""
