# 🚀 生产环境部署执行指南

**版本**: v1.0
**部署日期**: 2026-02-22
**目标环境**: meiyueart.com (生产环境)

---

## 📋 部署概览

### 修复内容

| 修复项 | 文件 | 修复说明 |
|--------|------|---------|
| 推荐人字段显示 | `admin-backend/routes/user_system.py` | 添加 `referral_relationships` 表查询逻辑 |
| 密码修改功能 | `admin-backend/routes/change_password.py` | 确认模块存在，安装 bcrypt 依赖 |

### 影响范围

- **用户信息API**: `/api/user/info` - 返回推荐人信息
- **密码修改API**: `/api/user/change-password` - 修改用户密码
- **数据库表**: `referral_relationships` - 推荐关系表

---

## 🔧 部署前准备

### 1. 确认服务器访问

```bash
# 测试SSH连接
ssh user@meiyueart.com "echo '连接成功'"

# 如果连接失败，检查：
# 1. SSH密钥是否配置
# 2. 网络是否通畅
# 3. 服务器地址是否正确
```

### 2. 配置部署环境

```bash
# 编辑部署配置文件
vi deploy_config.sh

# 确认以下配置：
# - PRODUCTION_SERVER: 生产服务器地址
# - APP_PATH: 后端应用路径
# - DB_PATH: 数据库路径
# - SERVICE_NAME: 服务名称
```

### 3. 检查本地文件

```bash
# 确认修复文件存在
ls -lh admin-backend/routes/user_system.py
ls -lh admin-backend/routes/change_password.py

# 检查文件内容
grep -n "referral_relationships" admin-backend/routes/user_system.py
grep -n "change-password" admin-backend/routes/change_password.py
```

### 4. 备份策略

```bash
# 创建备份目录
mkdir -p ~/deploy_backups/$(date +%Y%m%d_%H%M%S)

# 备份本地文件
cp admin-backend/routes/user_system.py ~/deploy_backups/$(date +%Y%m%d_%H%M%S)/
cp admin-backend/routes/change_password.py ~/deploy_backups/$(date +%Y%m%d_%H%M%S)/
```

---

## 📦 部署步骤

### 步骤1: 备份生产环境

```bash
# 方式1: 使用脚本自动备份
./deploy_now.sh

# 方式2: 手动备份
ssh user@meiyueart.com << 'ENDSSH'
    # 创建备份目录
    BACKUP_DIR="$HOME/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR

    # 备份后端文件
    cp /var/www/meiyueart.com/admin-backend/routes/user_system.py $BACKUP_DIR/
    cp /var/www/meiyueart.com/admin-backend/routes/change_password.py $BACKUP_DIR/

    # 备份数据库
    cp /var/www/meiyueart.com/admin-backend/data/lingzhi_ecosystem.db $BACKUP_DIR/

    # 记录备份信息
    echo "备份完成: $BACKUP_DIR" > $BACKUP_DIR/backup_info.txt
    date >> $BACKUP_DIR/backup_info.txt

    echo "✅ 备份完成: $BACKUP_DIR"
ENDSSH
```

**验证备份**:
```bash
ssh user@meiyueart.com "ls -lh ~/backups/ | tail -1"
```

---

### 步骤2: 上传修复文件

```bash
# 方式1: 使用脚本自动上传
./deploy_now.sh

# 方式2: 手动上传
scp admin-backend/routes/user_system.py \
    user@meiyueart.com:/var/www/meiyueart.com/admin-backend/routes/

scp admin-backend/routes/change_password.py \
    user@meiyueart.com:/var/www/meiyueart.com/admin-backend/routes/
```

**验证上传**:
```bash
ssh user@meiyueart.com \
    "md5sum /var/www/meiyueart.com/admin-backend/routes/user_system.py"
```

---

### 步骤3: 安装依赖

```bash
# 方式1: 使用脚本自动安装
./deploy_now.sh

# 方式2: 手动安装
ssh user@meiyueart.com << 'ENDSSH'
    cd /var/www/meiyueart.com/admin-backend

    # 检查bcrypt是否已安装
    pip3 list | grep bcrypt

    # 如果未安装，安装bcrypt
    pip3 install bcrypt

    # 验证安装
    python3 -c "import bcrypt; print('bcrypt版本:', bcrypt.__version__)"
ENDSSH
```

**验证安装**:
```bash
ssh user@meiyueart.com "python3 -c 'import bcrypt; print(bcrypt.__version__)'"
```

---

### 步骤4: 重启服务

```bash
# 方式1: 使用脚本自动重启
./deploy_now.sh

# 方式2: 使用Supervisor重启
ssh user@meiyueart.com << 'ENDSSH'
    # 停止服务
    sudo supervisorctl stop lingzhi_admin_backend

    # 等待5秒
    sleep 5

    # 启动服务
    sudo supervisorctl start lingzhi_admin_backend

    # 检查服务状态
    sudo supervisorctl status lingzhi_admin_backend
ENDSSH

# 方式3: 直接重启
ssh user@meiyueart.com "sudo supervisorctl restart lingzhi_admin_backend"
```

**验证服务状态**:
```bash
ssh user@meiyueart.com "sudo supervisorctl status lingzhi_admin_backend"
```

预期输出：
```
lingzhi_admin_backend   RUNNING   pid 12345, uptime 0:00:05
```

---

### 步骤5: 等待服务启动

```bash
# 方式1: 使用脚本自动等待
./deploy_now.sh

# 方式2: 手动等待
for i in {1..30}; do
    if curl -sf https://meiyueart.com/api/health > /dev/null; then
        echo "✅ 服务已启动"
        break
    fi
    echo "等待服务启动... ($i/30)"
    sleep 2
done
```

---

### 步骤6: 验证部署

```bash
# 方式1: 使用自动化验证脚本
./verify_now.sh

# 方式2: 手动验证

# 测试1: 健康检查
curl https://meiyueart.com/api/health

# 测试2: 用户登录
TOKEN=$(curl -s -X POST https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

# 测试3: 推荐人字段
curl -s -X GET https://meiyueart.com/api/user/info \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 检查返回结果中是否包含 referrer 字段

# 测试4: 密码修改
curl -s -X POST https://meiyueart.com/api/user/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"oldPassword": "123", "newPassword": "TempPass123!"}'
```

---

## ✅ 验证检查清单

### API测试

- [ ] 健康检查返回 `{"status": "healthy"}`
- [ ] 用户登录成功，获取到token
- [ ] 用户信息API返回 `referrer` 字段
- [ ] 密码修改API返回成功或预期错误
- [ ] API响应时间 < 5秒

### 服务检查

- [ ] 服务状态为 `RUNNING`
- [ ] 服务进程正常运行
- [ ] 日志中没有ERROR或异常

### 功能检查

- [ ] 推荐人字段正确显示
- [ ] 推荐人信息包含id、username、avatar
- [ ] 密码修改功能可用
- [ ] 用户可以成功修改密码

---

## 🔄 回滚方案

### 自动回滚

如果使用 `deploy_now.sh` 脚本，验证失败时可以执行回滚：

```bash
# 查找最新备份
BACKUP=$(ssh user@meiyueart.com "ls -t ~/backups/ | head -1")

# 恢复文件
scp user@meiyueart.com:~/backups/$BACKUP/user_system.py \
    admin-backend/routes/

scp user@meiyueart.com:~/backups/$BACKUP/change_password.py \
    admin-backend/routes/

# 重新部署
./deploy_now.sh
```

### 手动回滚

```bash
ssh user@meiyueart.com << 'ENDSSH'
    # 查找最新备份
    BACKUP_DIR=$(ls -t ~/backups/ | head -1)

    # 恢复文件
    cp ~/backups/$BACKUP_DIR/user_system.py \
       /var/www/meiyueart.com/admin-backend/routes/

    cp ~/backups/$BACKUP_DIR/change_password.py \
       /var/www/meiyueart.com/admin-backend/routes/

    # 重启服务
    sudo supervisorctl restart lingzhi_admin_backend

    # 验证状态
    sudo supervisorctl status lingzhi_admin_backend
ENDSSH
```

---

## 📊 监控和日志

### 查看服务日志

```bash
# 实时监控
ssh user@meiyueart.com "sudo tail -f /var/log/flask_backend.log"

# 查看最近100行
ssh user@meiyueart.com "sudo tail -100 /var/log/flask_backend.log"

# 查看错误日志
ssh user@meiyueart.com "sudo grep ERROR /var/log/flask_backend.log | tail -20"
```

### 检查服务状态

```bash
# Supervisor状态
ssh user@meiyueart.com "sudo supervisorctl status lingzhi_admin_backend"

# 进程状态
ssh user@meiyueart.com "ps aux | grep flask"

# 端口监听
ssh user@meiyueart.com "sudo netstat -tuln | grep 8080"
```

---

## 📞 故障排查

### 问题1: 服务启动失败

**症状**: 服务状态为 `STOPPED` 或 `FATAL`

**解决方案**:
```bash
# 查看详细日志
ssh user@meiyueart.com "sudo supervisorctl tail -f lingzhi_admin_backend stderr"

# 检查Python环境
ssh user@meiyueart.com "python3 --version"

# 检查依赖
ssh user@meiyueart.com "cd /var/www/meiyueart.com/admin-backend && pip3 list | grep bcrypt"
```

### 问题2: bcrypt模块未找到

**症状**: `ModuleNotFoundError: No module named 'bcrypt'`

**解决方案**:
```bash
ssh user@meiyueart.com "pip3 install bcrypt"
```

### 问题3: 推荐人字段仍然空白

**症状**: 用户信息API返回的referrer字段为null

**解决方案**:
```bash
# 检查文件是否更新
ssh user@meiyueart.com \
  "md5sum /var/www/meiyueart.com/admin-backend/routes/user_system.py"

# 检查数据库表
ssh user@meiyueart.com \
  "sqlite3 /var/www/meiyueart.com/admin-backend/data/lingzhi_ecosystem.db \
   '.schema referral_relationships'"

# 重启服务
ssh user@meiyueart.com "sudo supervisorctl restart lingzhi_admin_backend"
```

### 问题4: 密码修改返回404

**症状**: POST `/api/user/change-password` 返回404

**解决方案**:
```bash
# 检查蓝图注册
ssh user@meiyueart.com \
  "grep -n 'change_password' /var/www/meiyueart.com/admin-backend/app.py"

# 检查路由定义
ssh user@meiyueart.com \
  "ls -la /var/www/meiyueart.com/admin-backend/routes/ | grep change"

# 查看日志
ssh user@meiyueart.com "sudo grep change_password /var/log/flask_backend.log"
```

---

## 📝 部署后操作

### 1. 记录部署日志

```bash
# 填写部署日志
vi DEPLOYMENT_LOG.md

# 记录以下信息：
# - 部署日期和时间
# - 部署人员
# - 部署版本
# - 部署内容
# - 验证结果
# - 遇到的问题
```

### 2. 通知团队

```bash
# 发送通知邮件
echo "部署完成 - 推荐人显示和密码修改功能修复" | \
  mail -s "部署通知" ops@meiyueart.com
```

### 3. 监控观察

```bash
# 持续监控30分钟
for i in {1..30}; do
    echo "=== 检查 $i/30 ==="
    curl -s https://meiyueart.com/api/health
    echo ""
    sleep 60
done
```

---

## ✅ 部署完成检查

部署完成后，请确认以下项目：

- [ ] 所有测试用例通过
- [ ] 服务运行正常
- [ ] 日志无异常错误
- [ ] 功能验证通过
- [ ] 用户可以正常访问
- [ ] 推荐人字段显示正确
- [ ] 密码修改功能可用
- [ ] 部署日志已记录
- [ ] 团队已通知

---

## 🎯 快速命令参考

### 一键部署
```bash
./deploy_now.sh && ./verify_now.sh
```

### 查看状态
```bash
ssh user@meiyueart.com "sudo supervisorctl status lingzhi_admin_backend"
```

### 查看日志
```bash
ssh user@meiyueart.com "sudo tail -50 /var/log/flask_backend.log"
```

### 快速验证
```bash
curl https://meiyueart.com/api/health
```

---

**部署指南版本**: v1.0
**创建时间**: 2026-02-22
**维护团队**: 运维团队

**祝部署顺利！🚀**
