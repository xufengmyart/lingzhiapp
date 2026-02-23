# 🚀 灵值生态园 - 快速部署参考

> **版本**: v12.0.0  
> **日期**: 2026-02-11

---

## ⚡ 快速部署（推荐）

### 方式一：使用阿里云部署脚本（推荐）

```bash
# 在生产服务器执行
ssh root@123.56.142.143
cd /var/www/meiyueart
bash scripts/deploy-to-aliyun.sh
```

**优点**：
- ✅ 使用标准化脚本
- ✅ 自动安装依赖、配置服务
- ✅ 自动验证服务状态

### 方式二：使用完整部署和修复脚本

```bash
# 在生产服务器执行
ssh root@123.56.142.143
cd /var/www/meiyueart
bash scripts/complete-deploy-and-fix.sh
```

**优点**：
- ✅ 完整的部署流程
- ✅ 自动配置 SSL、Nginx
- ✅ 包含故障恢复功能

### 方式三：手动上传代码

**第一步：在开发环境准备**

```bash
# 复制数据库到 backend
cd /workspace/projects
cp lingzhi_ecosystem.db backend/
```

**第二步：上传到生产服务器**

```bash
# 上传 backend 代码和数据库
scp -r backend root@123.56.142.143:/var/www/meiyueart/
scp lingzhi_ecosystem.db root@123.56.142.143:/var/www/meiyueart/
```

**第三步：在生产服务器部署**

```bash
ssh root@123.56.142.143
cd /var/www/meiyueart
bash scripts/complete-deploy-and-fix.sh
```

---

## 📦 部署包内容

| 文件/目录 | 说明 |
|----------|------|
| `backend/` | Flask 后端代码 |
| `backend/lingzhi_ecosystem.db` | 数据库（32个用户） |
| `scripts/` | 部署和运维脚本 |
| `config/` | 配置文件 |
| `docs/` | 文档 |

---

## ✅ 部署验证

### 检查服务状态

```bash
# Flask 服务
systemctl status flask-app

# Nginx 服务
systemctl status nginx

# 端口监听
netstat -tlnp | grep -E '80|443|8080'
```

### 检查数据库

```bash
cd /var/www/meiyueart
python3 -c "import sqlite3; conn = sqlite3.connect('lingzhi_ecosystem.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users'); print(f'用户数: {cursor.fetchone()[0]}')"
```

### 测试登录

```bash
# 管理员登录
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 核心用户登录
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"许锋","password":"123456"}'
```

### Web 访问

- **HTTP**: http://meiyueart.com
- **HTTPS**: https://meiyueart.com
- **API**: http://123.56.142.143:8080

---

## 👥 核心用户账号

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | 123456 | 管理员 |
| 许锋 | 123456 | 核心用户 |
| CTO（待定） | 123456 | 技术负责人 |
| CMO（待定） | 123456 | 市场负责人 |
| COO（待定） | 123456 | 运营负责人 |
| CFO（待定） | 123456 | 财务负责人 |
| 17372200593 | 123456 | 测试用户 |

**注意**：所有用户密码已统一为 123456

---

## 🔄 回滚操作

### 回滚到备份

```bash
# SSH 登录到生产服务器
ssh root@123.56.142.143

# 停止服务
systemctl stop flask-app
systemctl stop nginx

# 查看备份列表
ls -lh /var/www/meiyueart/backups/

# 恢复备份（选择最新的）
cd /var/www/meiyueart
tar -xzf backups/backup-YYYYMMDD_HHMMSS.tar.gz

# 启动服务
systemctl start flask-app
systemctl start nginx
```

---

## 🛠️ 常用运维命令

### 查看日志

```bash
# Flask 日志
journalctl -u flask-app -f

# Nginx 日志
tail -f /var/log/nginx/error.log
tail -f /var/log/nginx/access.log

# 系统日志
tail -f /var/log/syslog
```

### 重启服务

```bash
# 重启 Flask
systemctl restart flask-app

# 重启 Nginx
systemctl restart nginx

# 重启所有服务
systemctl restart flask-app nginx
```

### 查看端口

```bash
# 查看所有监听端口
netstat -tlnp

# 查看特定端口
netstat -tlnp | grep 8080
netstat -tlnp | grep -E '80|443'
```

### 数据库操作

```bash
# 查看所有用户
cd /var/www/meiyueart
python3 scripts/test_users.py

# 重置所有用户密码
python3 scripts/reset_passwords_now.py

# 测试登录
python3 scripts/test_login.py
```

---

## 🆘 常见问题

### 问题 1：服务无法启动

```bash
# 查看详细错误
journalctl -u flask-app -n 50

# 常见原因：
# 1. 端口被占用 -> netstat -tlnp | grep 8080
# 2. 依赖缺失 -> pip3 install -r requirements.txt
# 3. 配置错误 -> 检查 backend/config.py
```

### 问题 2：无法访问网站

```bash
# 检查 Nginx 状态
systemctl status nginx

# 检查防火墙
ufw status

# 检查 DNS
nslookup meiyueart.com

# 检查 SSL 证书
openssl s_client -connect meiyueart.com:443
```

### 问题 3：登录失败

```bash
# 检查数据库用户
cd /var/www/meiyueart
python3 -c "import sqlite3; conn = sqlite3.connect('lingzhi_ecosystem.db'); cursor = conn.cursor(); cursor.execute('SELECT id, username FROM users'); print(cursor.fetchall())"

# 重置密码
python3 scripts/reset_passwords_now.py

# 测试登录
python3 scripts/test_login.py
```

---

## 📞 联系信息

- **生产服务器**: 123.56.142.143
- **域名**: meiyueart.com
- **技术支持**: Coze Coding
- **详细文档**: docs/DEPLOYMENT-GUIDE-ALIYUN.md
- **生产环境记忆**: docs/PRODUCTION-ENVIRONMENT-MEMORY.md

---

**创建者**: Coze Coding  
**版本**: v12.0.0  
**最后更新**: 2026-02-11
