# 灵值生态园 - 开发环境配置文档

> 本文档详细说明了开发环境的配置规范、时间同步保障以及认证错误的修复方案。

---

## 目录

- [1. 系统要求](#1-系统要求)
- [2. 环境配置](#2-环境配置)
- [3. 时间同步保障](#3-时间同步保障)
- [4. 安全配置](#4-安全配置)
- [5. 认证错误修复](#5-认证错误修复)
- [6. 部署流程](#6-部署流程)
- [7. 常见问题](#7-常见问题)

---

## 1. 系统要求

### 1.1 开发环境

- **操作系统**: Ubuntu 20.04+ / macOS 12+ / Windows 10+
- **Python**: 3.9+
- **Node.js**: 16+
- **Git**: 2.30+

### 1.2 生产环境

- **服务器**: Ubuntu 20.04+
- **Python**: 3.9+
- **Web服务器**: Nginx 1.18+
- **数据库**: SQLite (内置)

---

## 2. 环境配置

### 2.1 初始化脚本

项目提供了自动化环境初始化脚本 `setup_environment.sh`，可一键配置开发环境：

```bash
# 运行环境初始化
./setup_environment.sh
```

脚本会自动完成：
- ✅ 检查系统时间和时区
- ✅ 安装Python和Node.js依赖
- ✅ 创建必要的目录结构
- ✅ 检查环境变量配置文件
- ✅ 验证数据库配置

### 2.2 环境变量配置

#### 项目根目录 (`.env`)

```env
# GitHub 配置
GITHUB_USERNAME=xufengmyart
GITHUB_TOKEN=ghp_xxxxx

# 服务器配置
SERVER_USER=root
SERVER_HOST=123.56.142.143
SERVER_PASSWORD=Meiyue@root123
SERVER_PATH=/var/www/html

# 部署配置
MONITOR_INTERVAL=30
BACKUP_RETENTION_DAYS=7
```

#### 后端目录 (`admin-backend/.env`)

```env
# Flask 应用配置
FLASK_APP=app.py
FLASK_ENV=production
FLASK_DEBUG=false

# 安全配置（重要！）
SECRET_KEY=<生成的强随机密钥>
JWT_SECRET=<生成的强随机密钥>
JWT_EXPIRATION=604800

# 服务器配置
SERVER_HOST=0.0.0.0
SERVER_PORT=8080

# CORS配置
CORS_ORIGINS=https://meiyueart.com,https://www.meiyueart.com
```

### 2.3 生成安全密钥

```bash
# 生成SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"

# 生成JWT_SECRET
python3 -c "import secrets; print('JWT_SECRET=' + secrets.token_urlsafe(32))"
```

---

## 3. 时间同步保障

### 3.1 检查系统时间

```bash
# 查看当前时间
date

# 查看时区配置
timedatectl status
```

### 3.2 配置时区

```bash
# 设置为上海时区
sudo timedatectl set-timezone Asia/Shanghai

# 验证时区
timedatectl
```

### 3.3 配置NTP同步

```bash
# 安装NTP
sudo apt-get update
sudo apt-get install -y ntp

# 启动NTP服务
sudo systemctl start ntp
sudo systemctl enable ntp

# 验证NTP状态
sudo systemctl status ntp

# 手动同步时间
sudo ntpdate -s time.nist.gov
```

### 3.4 检查NTP同步状态

```bash
# 查看时间同步状态
timedatectl status

# 输出示例：
# System clock synchronized: yes
# NTP service: active
```

---

## 4. 安全配置

### 4.1 密钥安全

**必须遵守的原则：**
- ✅ 使用强随机密钥（至少32字符）
- ✅ 不要在代码中硬编码密钥
- ✅ 不要将.env文件提交到Git
- ✅ 定期更换密钥
- ✅ 不同环境使用不同密钥

### 4.2 .gitignore配置

确保 `.env` 文件已添加到 `.gitignore`：

```gitignore
# 环境变量配置
.env
.env.local
.env.*.local

# 敏感文件
*.db
*.log
backups/
logs/
```

### 4.3 权限配置

```bash
# 设置.env文件权限（仅所有者可读写）
chmod 600 admin-backend/.env
chmod 600 .env
```

---

## 5. 认证错误修复

### 5.1 常见认证错误

#### 错误1: JWT验证失败

**症状**：
```
{"message": "认证失败", "success": false}
```

**原因**：
- JWT_SECRET配置不一致
- Token已过期
- Token格式错误

**解决方案**：
```bash
# 1. 检查JWT_SECRET配置
grep JWT_SECRET admin-backend/.env

# 2. 确保前后端使用相同的JWT_SECRET
# 3. 重启后端服务
```

#### 错误2: 用户名或密码错误

**症状**：
```
{"message": "用户名或密码错误", "success": false}
```

**原因**：
- 密码哈希不匹配
- 数据库中用户不存在
- 用户状态异常

**解决方案**：
```bash
# 1. 检查用户是否存在
sqlite3 admin-backend/lingzhi_ecosystem.db "SELECT * FROM users WHERE username='用户名'"

# 2. 重置用户密码
python3 -c "
import bcrypt
import sqlite3
password='新密码'
password_hash=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
conn=sqlite3.connect('admin-backend/lingzhi_ecosystem.db')
cursor=conn.cursor()
cursor.execute('UPDATE users SET password_hash=? WHERE username=?', (password_hash.decode('utf-8'), '用户名'))
conn.commit()
conn.close()
"
```

### 5.2 环境变量加载问题

#### 问题：.env文件未被加载

**症状**：
后端日志中未显示"环境变量已加载"

**解决方案**：

确保 `app.py` 开头有加载环境变量的代码：

```python
# 加载环境变量配置文件
try:
    from dotenv import load_dotenv
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"✅ 环境变量已加载: {env_path}")
except ImportError:
    print("⚠️  python-dotenv未安装，使用默认环境变量")
```

安装python-dotenv：

```bash
pip3 install python-dotenv
```

---

## 6. 部署流程

### 6.1 配置验证

在部署前运行配置验证：

```bash
python3 validate_config.py
```

检查项：
- ✅ .env文件存在
- ✅ JWT_SECRET已配置
- ✅ .env文件在.gitignore中
- ✅ 数据库存在
- ✅ 必要的文件存在

### 6.2 部署到服务器

#### 方法1: 使用自动化脚本

```bash
# 部署环境配置
python3 deploy_environment_config.py

# 部署后端代码
python3 restart_backend_with_config.py
```

#### 方法2: 手动部署

```bash
# 1. 上传.env文件
sftp root@123.56.142.143
put admin-backend/.env /root/lingzhi-ecosystem/admin-backend/.env
quit

# 2. SSH到服务器
ssh root@123.56.142.143

# 3. 安装python-dotenv
pip3 install python-dotenv

# 4. 重启后端服务
cd /root/lingzhi-ecosystem/admin-backend
pkill -9 -f 'python3 app.py'
nohup python3 app.py > /tmp/backend.log 2>&1 &

# 5. 检查服务状态
ps aux | grep 'python3 app.py'
netstat -tlnp | grep 8080
tail -f /tmp/backend.log
```

### 6.3 验证部署

```bash
# 测试后端健康检查
curl https://meiyueart.com/api/login \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}'

# 检查后端日志
ssh root@123.56.142.143 "tail -20 /tmp/backend.log"
```

---

## 7. 常见问题

### Q1: 后端启动失败，提示"Port 8080 is in use"

**A:** 端口被占用，需要停止占用进程：

```bash
# 查找占用端口的进程
lsof -i :8080

# 停止进程
kill -9 <PID>

# 或者停止所有Python进程
pkill -9 -f python
```

### Q2: JWT token验证失败

**A:** 检查JWT_SECRET配置：

1. 确认 `.env` 文件中的 JWT_SECRET 配置正确
2. 确认后端已重启并加载了新的环境变量
3. 检查Token是否已过期（默认7天）

### Q3: 登录后立即掉线

**A:** 可能的原因：
1. JWT_SECRET不一致
2. 前端Token存储问题
3. Token验证中间件问题

解决方法：
```bash
# 清除浏览器缓存
# 重新登录
# 检查后端日志中的Token验证错误
```

### Q4: 数据库文件损坏

**A:** 从备份恢复：

```bash
# 查看可用备份
ls -lh admin-backend/backups/

# 恢复最新备份
cp admin-backend/backups/lingzhi_ecosystem_backup_YYYYMMDD_HHMMSS.db admin-backend/lingzhi_ecosystem.db
```

### Q5: 时间不同步导致Token验证失败

**A:** 同步系统时间：

```bash
# 同步NTP时间
sudo ntpdate -s time.nist.gov

# 重启后端服务
pkill -9 -f 'python3 app.py'
cd admin-backend && nohup python3 app.py > /tmp/backend.log 2>&1 &
```

---

## 8. 维护检查清单

### 每日检查
- [ ] 检查后端服务状态
- [ ] 查看后端日志是否有错误
- [ ] 检查NTP同步状态

### 每周检查
- [ ] 检查数据库备份
- [ ] 检查磁盘空间
- [ ] 检查系统更新

### 每月检查
- [ ] 更换JWT_SECRET和SECRET_KEY（如果需要）
- [ ] 检查用户账号状态
- [ ] 审查访问日志

---

## 9. 附录

### 9.1 配置文件结构

```
.
├── .env                      # 项目环境变量
├── admin-backend/
│   ├── .env                  # 后端环境变量
│   ├── app.py                # Flask应用
│   └── lingzhi_ecosystem.db  # 数据库
├── web-app/
│   ├── package.json          # 前端依赖
│   └── vite.config.ts        # Vite配置
├── setup_environment.sh      # 环境初始化脚本
├── validate_config.py        # 配置验证脚本
└── deploy_environment_config.py  # 部署脚本
```

### 9.2 相关文档

- [项目README](../README.md)
- [部署指南](../README-部署指南.md)
- [API文档](../docs/API.md)

---

**文档版本**: v1.0
**最后更新**: 2026-02-06
**维护者**: 开发团队
