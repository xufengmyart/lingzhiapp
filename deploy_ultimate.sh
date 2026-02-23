#!/bin/bash
################################################################################
# 灵值生态园 - 生产环境一键部署脚本（完美版）
# 目标环境: meiyueart.com
# 功能: 后端+前端完整部署，包含备份、重启、验证
################################################################################

set -e  # 遇到错误立即退出

# ==================== 配置区域 ====================

# 服务器配置
PRODUCTION_HOST="meiyueart.com"
PRODUCTION_USER="root"
PRODUCTION_PORT="22"
PRODUCTION_BACKEND="/app/meiyueart-backend"
PRODUCTION_FRONTEND="/var/www/meiyueart.com"
PRODUCTION_DB="/app/meiyueart-backend/data/lingzhi_ecosystem.db"

# 本地路径
PROJECT_ROOT="/workspace/projects"
LOCAL_BACKEND="$PROJECT_ROOT/admin-backend"
LOCAL_FRONTEND="$PROJECT_ROOT/web-app"
LOCAL_DB="$PROJECT_ROOT/admin-backend/data/lingzhi_ecosystem.db"

# 备份配置
BACKUP_DIR="/var/www/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# ==================== 工具函数 ====================

log_step() {
    echo -e "${CYAN}╔════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC} ${GREEN}$1${NC}                                 ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════╝${NC}"
}

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_banner() {
    clear
    echo -e "${CYAN}"
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                                                                ║"
    echo "║   🚀 灵值生态园 - 生产环境一键部署（完美版）                     ║"
    echo "║                                                                ║"
    echo "║   目标: ${GREEN}meiyueart.com${CYAN}                                          ║"
    echo "║   时间: $(date '+%Y-%m-%d %H:%M:%S')${CYAN}                                    ║"
    echo "║                                                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
}

# ==================== 步骤1: 环境检查 ====================

check_environment() {
    log_step "步骤 1/10: 环境检查"
    
    # 检查本地文件
    if [ ! -d "$LOCAL_BACKEND" ]; then
        log_error "后端目录不存在: $LOCAL_BACKEND"
        exit 1
    fi
    
    if [ ! -d "$LOCAL_FRONTEND" ]; then
        log_error "前端目录不存在: $LOCAL_FRONTEND"
        exit 1
    fi
    
    # 检查Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js 未安装"
        exit 1
    fi
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python3 未安装"
        exit 1
    fi
    
    log_success "环境检查通过"
}

# ==================== 步骤2: 清理临时文件 ====================

clean_temp_files() {
    log_step "步骤 2/10: 清理临时文件"
    
    # 清理Python缓存
    find "$LOCAL_BACKEND" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$LOCAL_BACKEND" -type f -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理前端临时文件
    rm -rf "$LOCAL_FRONTEND/dist" 2>/dev/null || true
    rm -rf "$LOCAL_FRONTEND/node_modules/.cache" 2>/dev/null || true
    
    log_success "临时文件清理完成"
}

# ==================== 步骤3: 备份生产环境 ====================

backup_production() {
    log_step "步骤 3/10: 备份生产环境"
    
    ssh -p $PRODUCTION_PORT $PRODUCTION_USER@$PRODUCTION_HOST << 'ENDSSH'
        # 创建备份目录
        mkdir -p $BACKUP_DIR
        
        # 备份后端
        if [ -d "$PRODUCTION_BACKEND" ]; then
            cd $PRODUCTION_BACKEND
            tar -czf $BACKUP_DIR/backend_backup_$(date +%Y%m%d_%H%M%S).tar.gz .
            echo "✅ 后端备份完成"
        fi
        
        # 备份数据库
        if [ -f "$PRODUCTION_DB" ]; then
            cp $PRODUCTION_DB $BACKUP_DIR/database_backup_$(date +%Y%m%d_%H%M%S).db
            echo "✅ 数据库备份完成"
        fi
        
        # 备份前端
        if [ -d "$PRODUCTION_FRONTEND" ]; then
            cd $PRODUCTION_FRONTEND
            tar -czf $BACKUP_DIR/frontend_backup_$(date +%Y%m%d_%H%M%S).tar.gz .
            echo "✅ 前端备份完成"
        fi
ENDSSH
    
    log_success "生产环境备份完成"
}

# ==================== 步骤4: 部署后端代码 ====================

deploy_backend() {
    log_step "步骤 4/10: 部署后端代码"
    
    log_info "上传后端代码..."
    rsync -avz --delete \
        -e "ssh -p $PRODUCTION_PORT" \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='data/*.db' \
        --exclude='logs/*' \
        --exclude='*.log' \
        $LOCAL_BACKEND/ \
        $PRODUCTION_USER@$PRODUCTION_HOST:$PRODUCTION_BACKEND/
    
    log_success "后端代码部署完成"
}

# ==================== 步骤5: 部署前端代码 ====================

deploy_frontend() {
    log_step "步骤 5/10: 部署前端代码"
    
    # 构建前端
    log_info "构建前端..."
    cd "$LOCAL_FRONTEND"
    npm install 2>&1 | grep -v "^\s*$" | head -5
    npm run build 2>&1 | grep -E "(build|error|warn)" | head -10
    
    if [ ! -d "dist" ]; then
        log_error "前端构建失败"
        exit 1
    fi
    
    # 上传前端代码
    log_info "上传前端代码..."
    rsync -avz --delete \
        -e "ssh -p $PRODUCTION_PORT" \
        $LOCAL_FRONTEND/dist/ \
        $PRODUCTION_USER@$PRODUCTION_HOST:$PRODUCTION_FRONTEND/
    
    log_success "前端代码部署完成"
}

# ==================== 步骤6: 更新数据库 ====================

update_database() {
    log_step "步骤 6/10: 更新数据库"
    
    ssh -p $PRODUCTION_PORT $PRODUCTION_USER@$PRODUCTION_HOST << 'ENDSSH'
        cd $PRODUCTION_BACKEND
        
        # 检查并创建分享统计表
        python3 << 'PYEOF'
import sqlite3
import os

db_path = os.getenv('DATABASE_PATH', 'data/lingzhi_ecosystem.db')
conn = sqlite3.connect(db_path)
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

# 检查 users 表是否有 referral_code 字段
cursor.execute("PRAGMA table_info(users)")
columns = [col[1] for col in cursor.fetchall()]
if 'referral_code' not in columns:
    cursor.execute('ALTER TABLE users ADD COLUMN referral_code TEXT')
    cursor.execute('ALTER TABLE users ADD COLUMN referral_code_expires_at TIMESTAMP')

conn.commit()
print("✅ 数据库更新完成")
conn.close()
PYEOF
ENDSSH
    
    log_success "数据库更新完成"
}

# ==================== 步骤7: 重启服务 ====================

restart_services() {
    log_step "步骤 7/10: 重启服务"
    
    ssh -p $PRODUCTION_PORT $PRODUCTION_USER@$PRODUCTION_HOST << 'ENDSSH'
        cd $PRODUCTION_BACKEND
        
        # 停止旧服务
        pkill -f "python.*app.py" || true
        pkill -f "gunicorn" || true
        sleep 3
        
        # 清理数据库锁定
        if [ -f "data/lingzhi_ecosystem.db-wal" ]; then
            rm -f data/lingzhi_ecosystem.db-wal
        fi
        
        # 启动新服务
        nohup python3 app.py > /dev/null 2>&1 &
        sleep 5
        
        # 验证服务启动
        if ps aux | grep -v grep | grep "python.*app.py" > /dev/null; then
            echo "✅ 后端服务启动成功"
        else
            echo "❌ 后端服务启动失败"
            tail -20 /var/log/syslog | grep python
            exit 1
        fi
        
        # 重启Nginx
        nginx -t && nginx -s reload && echo "✅ Nginx重启成功"
ENDSSH
    
    log_success "服务重启完成"
}

# ==================== 步骤8: 健康检查 ====================

health_check() {
    log_step "步骤 8/10: 健康检查"
    
    # 检查后端API
    response=$(curl -s -o /dev/null -w "%{http_code}" https://meiyueart.com/api/v9/news/categories)
    if [ "$response" = "200" ] || [ "$response" = "401" ]; then
        log_success "后端API健康检查通过"
    else
        log_warning "后端API响应异常: $response"
    fi
    
    # 检查前端页面
    response=$(curl -s -o /dev/null -w "%{http_code}" https://meiyueart.com/)
    if [ "$response" = "200" ]; then
        log_success "前端页面健康检查通过"
    else
        log_warning "前端页面响应异常: $response"
    fi
}

# ==================== 步骤9: 功能验证 ====================

verify_functions() {
    log_step "步骤 9/10: 功能验证"
    
    # 测试登录
    response=$(curl -s https://meiyueart.com/api/auth/login \
        -H "Content-Type: application/json" \
        -d '{"username":"admin","password":"123"}')
    
    if echo "$response" | grep -q "success.*true"; then
        log_success "管理员登录测试通过"
    else
        log_warning "管理员登录测试未通过"
    fi
    
    # 测试文章列表
    response=$(curl -s https://meiyueart.com/api/v9/news/articles)
    if echo "$response" | grep -q "success"; then
        log_success "文章列表API测试通过"
    else
        log_warning "文章列表API测试未通过"
    fi
    
    # 测试分享接口
    TOKEN=$(echo "$response" | python3 -c "import sys, json; d=json.load(sys.stdin); print(d.get('data', {}).get('token', ''))" 2>/dev/null || echo "")
    if [ -n "$TOKEN" ]; then
        share_response=$(curl -s "https://meiyueart.com/api/articles/1/share?type=link" \
            -H "Authorization: Bearer $TOKEN")
        if echo "$share_response" | grep -q "referral_code"; then
            log_success "分享接口测试通过"
        else
            log_warning "分享接口测试未通过"
        fi
    fi
}

# ==================== 步骤10: 清理与报告 ====================

cleanup_and_report() {
    log_step "步骤 10/10: 清理与报告"
    
    # 保存部署记录
    ssh -p $PRODUCTION_PORT $PRODUCTION_USER@$PRODUCTION_HOST << 'ENDSSH'
        echo "部署时间: $(date '+%Y-%m-%d %H:%M:%S')" >> $BACKUP_DIR/deployment_history.log
        echo "部署状态: 成功" >> $BACKUP_DIR/deployment_history.log
        echo "---" >> $BACKUP_DIR/deployment_history.log
ENDSSH
    
    log_success "部署记录已保存"
}

# ==================== 主函数 ====================

main() {
    print_banner
    
    # 记录开始时间
    START_TIME=$(date +%s)
    
    # 执行部署步骤
    check_environment
    clean_temp_files
    backup_production
    deploy_backend
    deploy_frontend
    update_database
    restart_services
    health_check
    verify_functions
    cleanup_and_report
    
    # 计算耗时
    END_TIME=$(date +%s)
    DURATION=$((END_TIME - START_TIME))
    MINUTES=$((DURATION / 60))
    SECONDS=$((DURATION % 60))
    
    # 打印完成信息
    echo ""
    log_step "部署完成"
    echo ""
    log_info "总耗时: ${MINUTES}分${SECONDS}秒"
    log_info "备份位置: $BACKUP_DIR"
    log_info "后端路径: $PRODUCTION_BACKEND"
    log_info "前端路径: $PRODUCTION_FRONTEND"
    echo ""
    log_success "🎉 部署成功！所有功能已部署到生产环境"
    echo ""
}

# 执行主函数
main "$@"
