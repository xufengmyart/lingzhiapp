# 灵值生态园智能体系统 - 生产环境部署操作手册

**版本**: v1.0
**最后更新**: 2026-02-22
**适用环境**: 生产环境 (meiyueart.com)
**维护人员**: 运维团队

---

## 📋 目录

1. [快速开始](#快速开始)
2. [环境准备](#环境准备)
3. [部署流程](#部署流程)
4. [验证检查](#验证检查)
5. [常见问题](#常见问题)
6. [回滚操作](#回滚操作)
7. [监控维护](#监控维护)

---

## 🚀 快速开始

### 自动化部署（推荐）

```bash
# 一键部署（包含验证）
./deploy_to_production.sh

# 仅部署不验证
./deploy_to_production.sh --skip-verify

# 验证部署
./verify_deployment.sh
```

### 手动部署

见[手动部署步骤](#手动部署步骤)

---

## 🔧 环境准备

### 前置条件

1. **服务器权限**
   - SSH访问权限: `user@meiyueart.com`
   - sudo权限（用于重启服务）

2. **本地环境**
   - Bash shell
   - git
   - Python 3.12+
   - Node.js 18+

3. **必要配置**
   ```bash
   # 复制并编辑配置文件
   cp deploy_config.example.sh deploy_config.sh
   vi deploy_config.sh
   ```

### 配置说明

`deploy_config.sh` 文件需要配置以下参数：

```bash
# 服务器配置
PRODUCTION_SERVER="user@meiyueart.com"
APP_PATH="/path/to/app"  # 实际应用路径

# 数据库配置
DB_PATH="$APP_PATH/admin-backend/data/lingzhi_ecosystem.db"

# 服务配置
SERVICE_NAME="lingzhi_admin_backend"
SUPERVISOR_CONFIG="/etc/supervisor/conf.d/lingzhi.conf"

# 备份配置
BACKUP_DIR="$HOME/backups"
RETENTION_DAYS=30
```

---

## 📦 部署流程

### 方式一：自动化部署

#### 1. 完整部署流程

```bash
# 步骤1: 版本一致性检查
./check_version_consistency.sh

# 步骤2: 执行部署
./deploy_to_production.sh

# 步骤3: 验证部署
./verify_deployment.sh
```

#### 2. 使用CI/CD

确保GitHub Secrets已配置：
- `SSH_PRIVATE_KEY`: SSH私钥
- `PRODUCTION_SERVER`: 生产服务器地址
- `APP_PATH`: 应用路径

```bash
# 推送代码自动触发部署
git add .
git commit -m "fix: 修复推荐人显示和密码修改功能"
git push origin main
```

### 方式二：手动部署步骤

#### 步骤1: 备份生产环境

```bash
ssh user@meiyueart.com

# 创建备份目录
BACKUP_DIR="$HOME/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

# 备份关键文件
cd /path/to/app
cp admin-backend/routes/user_system.py $BACKUP_DIR/
cp admin-backend/data/lingzhi_ecosystem.db $BACKUP_DIR/

# 记录备份信息
echo "备份完成: $BACKUP_DIR" > $BACKUP_DIR/backup_info.txt
date >> $BACKUP_DIR/backup_info.txt
ls -lh $BACKUP_DIR/ >> $BACKUP_DIR/backup_info.txt

exit
```

#### 步骤2: 上传修复文件

```bash
# 上传用户系统修复文件
scp admin-backend/routes/user_system.py user@meiyueart.com:/path/to/app/admin-backend/routes/

# （可选）上传前端文件
cd web-app && npm run build
scp -r dist/* user@meiyueart.com:/path/to/app/public/
```

#### 步骤3: 安装依赖

```bash
ssh user@meiyueart.com

cd /path/to/app/admin-backend

# 检查并安装bcrypt
pip list | grep bcrypt || pip install bcrypt

# 验证依赖
pip show bcrypt
```

#### 步骤4: 重启服务

```bash
# 方式1: 使用Supervisor（推荐）
sudo supervisorctl restart lingzhi_admin_backend

# 方式2: 使用systemd
sudo systemctl restart lingzhi-backend

# 方式3: 手动重启
sudo supervisorctl stop lingzhi_admin_backend
sudo supervisorctl start lingzhi_admin_backend

# 等待服务启动
sleep 10

# 检查服务状态
sudo supervisorctl status lingzhi_admin_backend
```

#### 步骤5: 验证服务

```bash
# 检查健康接口
curl https://meiyueart.com/api/health

# 检查日志
sudo tail -50 /var/log/flask_backend.log
```

---

## ✅ 验证检查

### 自动验证

```bash
./verify_deployment.sh
```

验证脚本将自动执行以下测试：
- 健康检查
- 用户登录
- 推荐人字段显示
- 密码修改功能
- API响应时间
- Token验证

### 手动验证

#### 1. API测试

```bash
# 健康检查
curl https://meiyueart.com/api/health

# 登录获取token
TOKEN=$(curl -s -X POST https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

# 获取用户信息（验证推荐人字段）
curl -s -X GET https://meiyueart.com/api/user/info \
  -H "Authorization: Bearer $TOKEN" | \
  python3 -m json.tool

# 测试密码修改
curl -s -X POST https://meiyueart.com/api/user/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"oldPassword": "123", "newPassword": "TempPass123!"}'
```

#### 2. 浏览器验证

1. 访问 https://meiyueart.com
2. 登录系统
3. 检查推荐人字段显示
4. 测试密码修改功能

#### 3. 日志检查

```bash
# 查看最新日志
ssh user@meiyueart.com 'sudo tail -100 /var/log/flask_backend.log'

# 查看错误日志
ssh user@meiyueart.com 'sudo grep ERROR /var/log/flask_backend.log | tail -20'

# 实时监控
ssh user@meiyueart.com 'sudo tail -f /var/log/flask_backend.log'
```

---

## ❓ 常见问题

### 问题1: SSH连接失败

**症状**: `Permission denied (publickey)` 或 `Connection refused`

**解决方案**:
```bash
# 检查SSH密钥
ls -la ~/.ssh/

# 测试连接
ssh -vvv user@meiyueart.com

# 检查服务器SSH服务
ssh user@meiyueart.com 'sudo systemctl status sshd'
```

### 问题2: bcrypt模块未找到

**症状**: `ModuleNotFoundError: No module named 'bcrypt'`

**解决方案**:
```bash
ssh user@meiyueart.com

# 检查Python环境
which python3
python3 --version

# 安装bcrypt
pip3 install bcrypt

# 验证安装
python3 -c "import bcrypt; print(bcrypt.__version__)"
```

### 问题3: 服务启动失败

**症状**: 服务状态为 `STOPPED` 或 `FATAL`

**解决方案**:
```bash
ssh user@meiyueart.com

# 查看详细日志
sudo supervisorctl tail -f lingzhi_admin_backend stderr

# 检查配置文件
sudo supervisorctl cat lingzhi_admin_backend

# 检查端口占用
sudo netstat -tuln | grep 5000

# 手动启动测试
cd /path/to/app/admin-backend
python3 app.py
```

### 问题4: API返回500错误

**症状**: 接口调用返回HTTP 500

**解决方案**:
```bash
ssh user@meiyueart.com

# 查看错误日志
sudo grep "ERROR" /var/log/flask_backend.log | tail -50

# 检查数据库
ls -lh /path/to/app/admin-backend/data/

# 检查文件权限
ls -la /path/to/app/admin-backend/routes/
```

### 问题5: 推荐人字段仍然空白

**症状**: 用户信息API返回的referrer字段为null

**解决方案**:
```bash
ssh user@meiyueart.com

# 检查代码是否更新
md5sum /path/to/app/admin-backend/routes/user_system.py

# 检查数据库表结构
sqlite3 /path/to/app/admin-backend/data/lingzhi_ecosystem.db ".schema referral_relationships"

# 查询数据
sqlite3 /path/to/app/admin-backend/data/lingzhi_ecosystem.db \
  "SELECT * FROM referral_relationships LIMIT 5;"

# 重启服务
sudo supervisorctl restart lingzhi_admin_backend
```

### 问题6: 密码修改返回404

**症状**: POST `/api/user/change-password` 返回404

**解决方案**:
```bash
ssh user@meiyueart.com

# 检查蓝图注册
grep -n "change_password" /path/to/app/admin-backend/app.py

# 检查路由定义
ls -la /path/to/app/admin-backend/routes/ | grep change

# 查看完整日志
sudo cat /var/log/flask_backend.log | grep -A 5 "change_password"
```

---

## 🔄 回滚操作

### 自动回滚

部署脚本在验证失败时会自动回滚。

### 手动回滚

#### 步骤1: 选择备份版本

```bash
ssh user@meiyueart.com

# 列出所有备份
ls -lht ~/backups/

# 选择要回滚的版本（例如：20260222_120000）
BACKUP_VERSION="20260222_120000"
```

#### 步骤2: 恢复文件

```bash
# 恢复user_system.py
cp ~/backups/$BACKUP_VERSION/user_system.py \
   /path/to/app/admin-backend/routes/

# （可选）恢复数据库
cp ~/backups/$BACKUP_VERSION/lingzhi_ecosystem.db \
   /path/to/app/admin-backend/data/

# 记录回滚操作
echo "$(date): 回滚到版本 $BACKUP_VERSION" >> /var/log/deployment.log
```

#### 步骤3: 重启服务

```bash
sudo supervisorctl restart lingzhi_admin_backend

# 等待服务启动
sleep 10

# 验证服务状态
sudo supervisorctl status lingzhi_admin_backend
curl https://meiyueart.com/api/health
```

#### 步骤4: 验证回滚

```bash
./verify_deployment.sh
```

---

## 📊 监控维护

### 日志监控

```bash
# 实时监控应用日志
ssh user@meiyueart.com 'sudo tail -f /var/log/flask_backend.log'

# 监控错误日志
ssh user@meiyueart.com 'sudo tail -f /var/log/flask_backend.log | grep ERROR'

# 监控访问日志
ssh user@meiyueart.com 'sudo tail -f /var/log/nginx/access.log'
```

### 性能监控

```bash
# 检查API响应时间
time curl https://meiyueart.com/api/health

# 检查服务资源占用
ssh user@meiyueart.com 'sudo supervisorctl status lingzhi_admin_backend'
ssh user@meiyueart.com 'ps aux | grep flask'

# 检查磁盘空间
ssh user@meiyueart.com 'df -h'
```

### 定期维护

#### 每日任务
- 检查错误日志
- 监控服务状态
- 检查磁盘空间

#### 每周任务
- 清理旧备份（保留最近30天）
- 检查依赖更新
- 审查安全日志

#### 每月任务
- 数据库备份
- 性能评估
- 安全审计

### 备份策略

```bash
# 自动备份脚本（可添加到crontab）
cat > ~/auto_backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="$HOME/backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR
cd /path/to/app
cp admin-backend/routes/user_system.py $BACKUP_DIR/
cp admin-backend/data/lingzhi_ecosystem.db $BACKUP_DIR/

# 清理30天前的备份
find ~/backups -type d -mtime +30 -exec rm -rf {} \;
EOF

chmod +x ~/auto_backup.sh

# 添加到crontab（每天凌晨2点执行）
(crontab -l 2>/dev/null; echo "0 2 * * * ~/auto_backup.sh") | crontab -
```

---

## 📞 联系支持

### 技术支持

- **运维团队**: ops@meiyueart.com
- **开发团队**: dev@meiyueart.com
- **紧急联系**: emergency@meiyueart.com

### 问题报告

遇到问题时，请提供以下信息：
1. 错误信息（截图或日志）
2. 复现步骤
3. 期望结果
4. 实际结果
5. 系统环境信息

---

## 📝 附录

### A. 目录结构

```
/path/to/app/
├── admin-backend/          # Flask后端
│   ├── routes/
│   │   └── user_system.py  # 用户系统（修复）
│   ├── data/
│   │   └── lingzhi_ecosystem.db  # 数据库
│   └── app.py              # 应用入口
├── public/                 # 前端静态文件
└── logs/                   # 日志目录
    └── flask_backend.log   # 应用日志
```

### B. 服务配置

Supervisor配置示例：

```ini
[program:lingzhi_admin_backend]
directory=/path/to/app/admin-backend
command=/usr/bin/python3 app.py
autostart=true
autorestart=true
stderr_logfile=/var/log/flask_backend.log
stdout_logfile=/var/log/flask_backend.log
user=www-data
environment=PYTHONUNBUFFERED="1"
```

### C. 防火墙规则

```bash
# 开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# 查看规则
sudo ufw status
```

---

**文档版本**: v1.0
**最后更新**: 2026-02-22
**维护人员**: 运维团队
