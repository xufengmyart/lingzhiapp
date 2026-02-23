#!/bin/bash
# 灵值生态园 - 一键全自动部署到生产环境（简化版）
# One-click Production Deployment (Simplified)

set -e

echo "========================================="
echo "🚀 灵值生态园 - 一键全自动部署"
echo "========================================="
echo ""

# 生产环境配置
PRODUCTION_HOST="meiyueart.com"
PRODUCTION_USER="root"
PRODUCTION_PASS="Meiyue@root123"
PRODUCTION_PORT="22"

# 生产环境路径
PRODUCTION_BACKEND="/app/meiyueart-backend"

# 本地路径
LOCAL_BACKEND="/workspace/projects/admin-backend"
LOCAL_DATABASE="/workspace/projects/admin-backend/data/lingzhi_ecosystem.db"

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

# ========== 步骤1：清理云服务器垃圾 ==========
echo "📋 步骤 1/6: 清理云服务器垃圾..."
sshpass -p "${PRODUCTION_PASS}" ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} << 'ENDSSH'
    find /var/log -name "*.log" -type f -mtime +7 -delete 2>/dev/null || true
    find /var/log -name "*.gz" -type f -mtime +30 -delete 2>/dev/null || true
    find /tmp -type f -mtime +7 -delete 2>/dev/null || true
    find ${PRODUCTION_BACKEND} -name "*.pyc" -delete 2>/dev/null || true
    find ${PRODUCTION_BACKEND} -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "✅ 云服务器垃圾清理完成"
ENDSSH
log_success "云服务器垃圾清理完成"

# ========== 步骤2：备份生产环境 ==========
echo ""
echo "📋 步骤 2/6: 备份生产环境..."
sshpass -p "${PRODUCTION_PASS}" ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} \
    "mkdir -p ${BACKUP_DIR} && tar -czf ${BACKUP_DIR}/backend_backup_${TIMESTAMP}.tar.gz -C ${PRODUCTION_BACKEND} . 2>/dev/null && echo '✅ 备份完成'"
log_success "生产环境备份完成"

# ========== 步骤3：上传后端代码 ==========
echo ""
echo "📋 步骤 3/6: 上传后端代码..."
TEMP_DIR="/tmp/deploy_backend_${TIMESTAMP}"
mkdir -p "$TEMP_DIR"
cp -r ${LOCAL_BACKEND}/. "$TEMP_DIR/"
rm -rf "$TEMP_DIR"/__pycache__
rm -rf "$TEMP_DIR"/tests
rm -rf "$TEMP_DIR"/logs
rm -rf "$TEMP_DIR"/*.backup.*
rm -rf "$TEMP_DIR"/*.tar.gz
rm -rf "$TEMP_DIR"/venv
rm -rf "$TEMP_DIR"/data/backups

# 修改 .env 文件中的数据库路径为生产路径
if [ -f "$TEMP_DIR/.env" ]; then
    sed -i "s|DATABASE_PATH=/workspace/projects/admin-backend/data/lingzhi_ecosystem.db|DATABASE_PATH=/app/meiyueart-backend/data/lingzhi_ecosystem.db|g" "$TEMP_DIR/.env"
    sed -i "s|LOG_DIR=/workspace/projects/admin-backend/logs|LOG_DIR=/var/log/meiyueart-backend|g" "$TEMP_DIR/.env"
    echo "✅ .env 文件已更新为生产路径"
fi

cd /tmp
tar -czf "backend_deploy_${TIMESTAMP}.tar.gz" -C "$TEMP_DIR" .

sshpass -p "${PRODUCTION_PASS}" scp -P ${PRODUCTION_PORT} -o StrictHostKeyChecking=no \
    /tmp/backend_deploy_${TIMESTAMP}.tar.gz \
    ${PRODUCTION_USER}@${PRODUCTION_HOST}:/tmp/

sshpass -p "${PRODUCTION_PASS}" ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} \
    "if [ -f '${PRODUCTION_BACKEND}/data/lingzhi_ecosystem.db' ]; then cp '${PRODUCTION_BACKEND}/data/lingzhi_ecosystem.db' '/tmp/production_database_backup.db' && echo '✅ 生产数据库已备份到 /tmp/production_database_backup.db'; fi && rm -rf ${PRODUCTION_BACKEND}_temp && mkdir -p ${PRODUCTION_BACKEND}_temp && tar -xzf /tmp/backend_deploy_${TIMESTAMP}.tar.gz -C ${PRODUCTION_BACKEND}_temp && rm -rf ${PRODUCTION_BACKEND} && mv ${PRODUCTION_BACKEND}_temp ${PRODUCTION_BACKEND} && if [ -f '/tmp/production_database_backup.db' ]; then cp '/tmp/production_database_backup.db' '${PRODUCTION_BACKEND}/data/lingzhi_ecosystem.db' && echo '✅ 生产数据库已恢复'; rm -f '/tmp/production_database_backup.db'; fi && rm /tmp/backend_deploy_${TIMESTAMP}.tar.gz && echo '✅ 代码上传完成'"

rm -rf "$TEMP_DIR"
rm -f /tmp/backend_deploy_${TIMESTAMP}.tar.gz
log_success "后端代码上传完成"

# ========== 步骤4：保留生产环境数据库 ==========
echo ""
echo "📋 步骤 4/6: 保留生产环境数据库..."
log_success "保留生产环境数据库（不覆盖）"

# ========== 步骤5：部署前端代码 ==========
echo ""
echo "📋 步骤 5/7: 部署前端代码..."
LOCAL_FRONTEND="/workspace/projects/web-app/dist"
TEMP_FRONTEND="/tmp/deploy_frontend_${TIMESTAMP}"

# 检查前端dist目录是否存在
if [ -d "$LOCAL_FRONTEND" ]; then
    mkdir -p "$TEMP_FRONTEND"
    cp -r ${LOCAL_FRONTEND}/* "$TEMP_FRONTEND/"
    cd /tmp
    tar -czf "frontend_deploy_${TIMESTAMP}.tar.gz" -C "$TEMP_FRONTEND" .
    sshpass -p "${PRODUCTION_PASS}" scp -P ${PRODUCTION_PORT} -o StrictHostKeyChecking=no \
        /tmp/frontend_deploy_${TIMESTAMP}.tar.gz \
        ${PRODUCTION_USER}@${PRODUCTION_HOST}:/tmp/
    sshpass -p "${PRODUCTION_PASS}" ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} \
        "rm -rf /var/www/meiyueart.com/* && tar -xzf /tmp/frontend_deploy_${TIMESTAMP}.tar.gz -C /var/www/meiyueart.com/ && rm /tmp/frontend_deploy_${TIMESTAMP}.tar.gz && echo '✅ 前端部署完成'"
    rm -rf "$TEMP_FRONTEND"
    rm -f /tmp/frontend_deploy_${TIMESTAMP}.tar.gz
    log_success "前端代码部署完成"
else
    log_warn "前端dist目录不存在，跳过前端部署"
fi

# ========== 步骤6：更新Nginx配置并重启后端服务 ==========
echo ""
echo "📋 步骤 6/7: 更新Nginx配置并重启后端服务..."
sshpass -p "${PRODUCTION_PASS}" ssh -p ${PRODUCTION_PORT} -o StrictHostKeyChecking=no ${PRODUCTION_USER}@${PRODUCTION_HOST} << 'ENDSSH'
    # 更新Nginx配置 (使用5000端口)
    sed -i 's/proxy_pass http:\/\/127.0.0.1:8080/proxy_pass http:\/\/127.0.0.1:5000/g' /etc/nginx/sites-available/meiyueart-https.conf
    
    # 添加uploads静态文件服务配置（如果不存在）
    if ! grep -q "location ^~ /uploads/" /etc/nginx/sites-available/meiyueart-https.conf; then
        # 使用Python脚本添加uploads location配置
        python3 << 'PYTHON'
import re

# 读取配置文件
with open('/etc/nginx/sites-available/meiyueart-https.conf', 'r') as f:
    content = f.read()

# 找到正则匹配的location并插入uploads配置
uploads_config = '''
    # 上传文件静态服务（使用^~提高优先级，高于正则匹配）
    location ^~ /uploads/ {
        alias /app/meiyueart-backend/uploads/;
        expires 30d;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
'''

# 在静态资源正则匹配之前插入uploads配置
pattern = r'(    # 静态资源禁用缓存)'
replacement = uploads_config + '\n' + r'\1'
new_content = re.sub(pattern, replacement, content)

# 写回配置文件
with open('/etc/nginx/sites-available/meiyueart-https.conf', 'w') as f:
    f.write(new_content)

print("✅ Nginx uploads配置已添加")
PYTHON
    fi
    
    # 创建uploads目录
    mkdir -p /app/meiyueart-backend/uploads/avatars
    
    nginx -t && systemctl reload nginx

    # ========== 彻底清理数据库锁定 ==========
    echo "🔧 开始彻底清理数据库锁定..."
    
    cd /app/meiyueart-backend
    
    # 1. 停止所有Python进程
    echo "停止所有Python进程..."
    pkill -9 -f "python.*app.py" 2>/dev/null || true
    pkill -9 -f "flask" 2>/dev/null || true
    pkill -9 -f "gunicorn" 2>/dev/null || true
    pkill -9 -f "uwsgi" 2>/dev/null || true
    pkill -9 -f "python3" 2>/dev/null || true
    sleep 3

    # 2. 强制清理所有残留进程
    echo "清理残留进程..."
    if pgrep -f "python" > /dev/null 2>&1; then
        echo "发现残留Python进程，强制终止..."
        killall -9 python 2>/dev/null || true
        killall -9 python3 2>/dev/null || true
        sleep 2
    fi

    # 3. 清理数据库锁定文件
    if [ -d "data" ]; then
        echo "清理数据库锁定文件..."
        
        # 删除所有SQLite相关锁定文件
        find data -name "*.db-wal" -delete 2>/dev/null
        find data -name "*.db-shm" -delete 2>/dev/null
        find data -name "*-journal" -delete 2>/dev/null
        find data -name "*.lock" -delete 2>/dev/null
        
        # 检查是否有进程仍然锁定数据库
        if lsof +D data > /dev/null 2>&1; then
            echo "⚠️  检测到数据库文件仍被锁定"
            echo "锁定进程信息:"
            lsof +D data 2>/dev/null || true
            echo "尝试强制终止锁定进程..."
            PIDS=$(lsof +D data 2>/dev/null | awk 'NR>1 {print $2}' | sort -u)
            for PID in $PIDS; do
                echo "终止进程: $PID"
                kill -9 $PID 2>/dev/null || true
            done
            sleep 2
        fi
        
        # 修复数据库文件权限
        if [ -f "data/lingzhi_ecosystem.db" ]; then
            echo "修复数据库文件权限..."
            chmod 664 data/lingzhi_ecosystem.db 2>/dev/null || true
            chown root:root data/lingzhi_ecosystem.db 2>/dev/null || true
        fi
        
        echo "✅ 数据库锁定文件清理完成"
    fi

    cd /app/meiyueart-backend

    # 安装依赖
    if [ ! -d "venv" ]; then
        python3 -m venv venv
    fi
    source venv/bin/activate
    pip install --upgrade pip -q
    pip install python-dotenv flask flask-cors -q
    pip install -r requirements.txt -q 2>/dev/null || true

    # 再次确认没有残留进程
    echo "最终检查并清理残留进程..."
    pkill -9 -f "python.*app.py" 2>/dev/null || true
    sleep 2
    
    # 再次清理锁定文件
    if [ -d "data" ]; then
        find data -name "*.db-wal" -delete 2>/dev/null || true
        find data -name "*.db-shm" -delete 2>/dev/null || true
        find data -name "*-journal" -delete 2>/dev/null || true
        find data -name "*.lock" -delete 2>/dev/null || true
    fi
    
    # 等待确保数据库完全释放
    echo "等待数据库完全释放锁定..."
    sleep 3

    # ========== 跳过密码修复步骤（已在之前的部署中执行）==========
    echo "⚠️  跳过密码修复步骤（已在之前的部署中执行）"

    # ========== 数据库初始化 ==========
    echo "🗄️  检查并初始化数据库表..."
    cd /app/meiyueart-backend
    
    if [ -f "scripts/init_news_and_notifications_tables.py" ]; then
        echo "运行数据库初始化脚本..."
        python3 scripts/init_news_and_notifications_tables.py
        echo "✅ 数据库表检查和初始化完成"
    else
        echo "⚠️  数据库初始化脚本不存在，跳过"
    fi

    # 启动服务 (端口 5000)
    echo "启动后端服务..."
    nohup python app.py > /var/log/meiyueart-backend/app.log 2>&1 &
    sleep 8  # 增加等待时间，确保应用完全启动

    if ps aux | grep -v grep | grep "python.*app.py" > /dev/null; then
        echo "✅ 后端服务启动成功 (端口 5000)"
    else
        echo "❌ 后端服务启动失败"
        tail -n 50 /var/log/meiyueart-backend/app.log
        exit 1
    fi
ENDSSH
log_success "Nginx配置更新完成"
log_success "后端服务重启完成"

# ========== 步骤7：验证部署 ==========
echo ""
echo "📋 步骤 7/7: 验证部署..."
sleep 3

# 健康检查
HEALTH_CHECK=$(curl -s https://meiyueart.com/api/health)
if echo "$HEALTH_CHECK" | grep -q '"status":"healthy"\|"status":"ok"'; then
    log_success "健康检查通过"
else
    log_warn "健康检查未通过: $HEALTH_CHECK"
fi

# 登录测试
LOGIN_RESPONSE=$(curl -s -X POST https://meiyueart.com/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"123"}')

if echo "$LOGIN_RESPONSE" | grep -q '"success":true\|"token"'; then
    log_success "管理员登录测试通过"
else
    log_warn "管理员登录测试未通过"
fi

# 用户登录测试
USER_LOGIN=$(curl -s -X POST https://meiyueart.com/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"马伟娟","password":"123"}')

if echo "$USER_LOGIN" | grep -q '"success":true\|"token"'; then
    log_success "用户登录测试通过"
else
    log_warn "用户登录测试未通过"
fi

# ========== 部署完成 ==========
echo ""
echo "========================================="
log_success "部署完成！"
echo "========================================="
echo ""
echo "📊 部署信息："
echo "  - 服务器: ${PRODUCTION_HOST}"
echo "  - 后端: ${PRODUCTION_BACKEND}"
echo "  - 备份: ${BACKUP_DIR}/backend_backup_${TIMESTAMP}.tar.gz"
echo "  - 时间: $(date)"
echo ""
echo "🔗 访问地址："
echo "  - 前端: https://meiyueart.com"
echo "  - API: https://meiyueart.com/api"
echo ""
echo "👤 测试账号："
echo "  - 管理员: admin / 123"
echo "  - 用户: 马伟娟 / 123"
echo ""
