# 🏢 灵值生态园 - 生产环境记忆文档

> **版本**: v1.0  
> **创建时间**: 2026-02-11  
> **最后更新**: 2026-02-11  
> **目的**: 记录生产环境的关键信息，便于快速查阅和维护

---

## 🌐 生产环境信息

### 服务器配置

| 项目 | 配置 |
|------|------|
| **服务器类型** | 阿里云服务器 |
| **公网 IP** | 123.56.142.143 |
| **域名** | meiyueart.com |
| **操作系统** | Ubuntu 20.04+ |
| **部署路径** | /var/www/meiyueart |

### 服务配置

| 服务 | 端口 | 协议 | 状态 |
|------|------|------|------|
| Nginx | 80 | HTTP | ✅ 运行中 |
| Nginx | 443 | HTTPS | ✅ 运行中 |
| Flask | 8080 | HTTP | ✅ 运行中 |

### 数据库配置

| 项目 | 配置 |
|------|------|
| **数据库类型** | SQLite |
| **数据库路径** | /var/www/meiyueart/lingzhi_ecosystem.db |
| **备份数据库** | /var/www/meiyueart/lingzhi_ecosystem.db.backup.* |
| **用户数量** | 32 个 |

### 重要路径

```
/var/www/meiyueart/
├── backend/              # Flask 后端
│   ├── app.py          # 主应用文件
│   └── lingzhi_ecosystem.db  # 数据库
├── web-app/dist/       # 前端构建产物
├── scripts/            # 部署和运维脚本
├── config/             # 配置文件
└── logs/               # 日志文件（软链接到 /var/log/）

系统配置:
├── /etc/nginx/sites-available/meiyueart.com
├── /etc/nginx/ssl/
├── /etc/systemd/system/flask-app.service
└── /var/log/
```

---

## 👥 核心用户列表（7-8个）

### 核心用户

| ID | 用户名 | 手机号 | 邮箱 | 角色/说明 | 密码 |
|----|-------|--------|------|----------|------|
| 1 | 许锋 | - | xufeng@meiyueart.cn | 核心用户 | 123456 |
| 2 | CTO（待定） | - | cto@meiyue.com | 技术负责人 | 123456 |
| 3 | CMO（待定） | - | cmo@meiyue.com | 市场负责人 | 123456 |
| 4 | COO（待定） | - | coo@meiyue.com | 运营负责人 | 123456 |
| 5 | CFO（待定） | - | cfo@meiyue.com | 财务负责人 | 123456 |
| 10 | admin | - | admin@meiyueart.com | 管理员 | 123456 |
| 201 | 17372200593 | 17372200593 | test@example.com | 测试用户 | 123456 |

**总计**: 7 个核心用户

---

## 📊 所有用户列表（32个）

| ID | 用户名 | 手机号 | 邮箱 | 密码 | 状态 |
|----|-------|--------|------|------|------|
| 1 | 许锋 | - | xufeng@meiyueart.cn | 123456 | active |
| 2 | CTO（待定） | - | cto@meiyue.com | 123456 | active |
| 3 | CMO（待定） | - | cmo@meiyue.com | 123456 | active |
| 4 | COO（待定） | - | coo@meiyue.com | 123456 | active |
| 5 | CFO（待定） | - | cfo@meiyue.com | 123456 | active |
| 6 | 测试用户A | 13800138001 | test_a@example.com | 123456 | active |
| 7 | 测试用户B | 13800138002 | test_b_1769397229@example.com | 123456 | active |
| 8 | testuser | 13800138000 | test@example.com | 123456 | active |
| 9 | testuser2_updated | 13800138001 | test2_updated@example.com | 123456 | active |
| 10 | admin | - | admin@meiyueart.com | 123456 | active |
| 100 | test_referrer | 13800138000 | test@example.com | 123456 | active |
| 200 | test_referee | 13800138001 | referee@example.com | 123456 | active |
| 201 | 17372200593 | 17372200593 | test@example.com | 123456 | active |
| 202 | test_auto_1770600296 | - | test1770600296@test.com | 123456 | active |
| 203 | test_auto_1770600305 | - | test1770600305@test.com | 123456 | active |
| 204 | test_auto_1770600321 | - | test1770600321@test.com | 123456 | active |
| 205 | test_auto_1770600325 | - | test1770600325@test.com | 123456 | active |
| 206 | test_auto_1770600345 | - | test1770600345@test.com | 123456 | active |
| 207 | test_auto_1770600348 | - | test1770600348@test.com | 123456 | active |
| 208 | test_auto_1770600360 | - | test1770600360@test.com | 123456 | active |
| 209 | testuser_1770601668 | - | test@example.com | 123456 | active |
| 210 | db_test_1770601730 | - | dbtest@example.com | 123456 | active |
| 211 | db_test_1770601734 | - | dbtest@example.com | 123456 | active |
| 212 | check_user_1770601958 | - | check@example.com | 123456 | active |
| 213 | test_user_1770602474 | - | test@example.com | 123456 | active |
| 214 | test_user_1770602497 | 13900139000 | test@example.com | 123456 | active |
| 215 | test_fix_1 | 13800000020 | test_fix_1@example.com | 123456 | active |
| 216 | test_fix_2 | 13800000021 | test_fix_2@example.com | 123456 | active |
| 217 | testuser_referral_20260209_v2 | - | test_referral_v2@example.com | 123456 | active |
| 218 | wechat_test_user | - | wechat_test@example.com | 123456 | active |
| 219 | wechat_user_003 | 13900139003 | wechat_test003@example.com | 123456 | active |
| 220 | 微信用户98710 | 13900139999 | - | 123456 | active |

**总计**: 32 个用户  
**统一密码**: 123456

---

## 🔐 登录信息

### 登录方式

用户可以使用以下方式登录：
- 用户名登录（支持用户名）
- 手机号登录（如果有手机号）

### 登录测试

```bash
# 测试登录脚本
python3 scripts/test_login.py

# API 测试
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

### Web 登录

1. 访问: `https://meiyueart.com`
2. 输入用户名和密码
3. 点击登录

---

## 🛠️ 维护脚本

### 用户管理

| 脚本 | 用途 | 使用方法 |
|------|------|---------|
| `scripts/test_users.py` | 查看用户列表 | `python3 scripts/test_users.py` |
| `scripts/test_login.py` | 测试用户登录 | `python3 scripts/test_login.py` |
| `scripts/reset_passwords-now.py` | 重置所有用户密码 | `python3 scripts/reset_passwords-now.py` |
| `scripts/reset_user_passwords.py` | 交互式密码重置 | `python3 scripts/reset_user_passwords.py` |
| `scripts/import_users.py` | 导入用户 | `python3 scripts/import_users.py` |
| `scripts/reset_and_import_all_users.py` | 完整重置和导入 | `python3 scripts/reset_and_import_all_users.py` |

### 系统管理

| 脚本 | 用途 | 使用方法 |
|------|------|---------|
| `scripts/complete-deploy-and-fix.sh` | 完整部署和修复 | `bash scripts/complete-deploy-and-fix.sh` |
| `scripts/diagnose-and-fix.sh` | 诊断和快速修复 | `bash scripts/diagnose-and-fix.sh` |
| `scripts/fix-login-issue.sh` | 修复登录问题 | `bash scripts/fix-login-issue.sh` |
| `scripts/health-check.sh` | 健康检查 | `bash scripts/health-check.sh` |
| `scripts/setup-cron.sh` | 配置自动监控 | `bash scripts/setup-cron.sh` |

---

## 🚨 快速故障排查

### 登录失败（502 错误）

```bash
# 诊断和修复
cd /var/www/meiyueart
bash scripts/fix-login-issue.sh

# 或手动修复
systemctl restart flask-app
```

### 密码错误

```bash
# 重置所有用户密码
cd /var/www/meiyueart
python3 scripts/reset_passwords_now.py

# 或重置指定用户密码
python3 scripts/reset_user_passwords.py
```

### 服务异常

```bash
# 检查服务状态
systemctl status flask-app
systemctl status nginx

# 查看日志
journalctl -u flask-app -f
tail -f /var/log/nginx/error.log
```

---

## 📞 快速命令

### SSH 登录

```bash
ssh root@123.56.142.143
```

### 查看用户

```bash
cd /var/www/meiyueart
python3 scripts/test_users.py
```

### 重置密码

```bash
cd /var/www/meiyueart
python3 scripts/reset_passwords_now.py
```

### 重启服务

```bash
# Flask 服务
systemctl restart flask-app

# Nginx 服务
systemctl restart nginx
```

### 查看日志

```bash
# Flask 日志
journalctl -u flask-app -f

# Nginx 日志
tail -f /var/log/nginx/error.log

# 健康检查日志
tail -f /var/log/health-check.log
```

---

## 📝 重要提醒

### 环境确认

⚠️  **唯一的生产环境**: 阿里云服务器（123.56.142.143）  
⚠️  **开发环境**: Coze 平台环境（115.190.218.237）- 仅用于开发和测试  
⚠️  **生产数据**: `/var/www/meiyueart/lingzhi_ecosystem.db`  
⚠️  **开发数据**: `/workspace/projects/lingzhi_ecosystem.db`  

### 密码安全

⚠️  所有用户密码已设置为: 123456  
⚠️  建议用户首次登录后立即修改密码  
⚠️  管理员应尽快修改默认密码  
⚠️  定期更换密码以提高安全性  

### 数据备份

⚠️  每次修改数据前先备份  
⚠️  备份文件命名: `lingzhi_ecosystem.db.backup.YYYYMMDD_HHMMSS`  
⚠️  保留最近 7 天的备份  

---

## 📚 相关文档

- [用户密码管理文档](docs/USER-PASSWORD-MANAGEMENT.md)
- [快速参考指南](docs/QUICK-REF-PASSWORD-RESET.md)
- [登录问题诊断](docs/LOGIN-ISSUE-COMPLETE-DIAGNOSIS.md)
- [标准部署配置](docs/STANDARD-DEPLOYMENT-CONFIG.md)

---

## 🎯 快速参考

### 默认密码
```
123456
```

### 生产服务器
```
IP: 123.56.142.143
域名: meiyueart.com
```

### 核心用户
```
1. 许锋 - xufeng@meiyueart.cn
2. CTO - cto@meiyue.com
3. CMO - cmo@meiyue.com
4. COO - coo@meiyue.com
5. CFO - cfo@meiyue.com
6. admin - admin@meiyueart.com
7. 17372200593
```

---

**创建者**: Coze Coding  
**版本**: v1.0  
**最后更新**: 2026-02-11  
**环境**: 阿里云生产环境（123.56.142.143）
