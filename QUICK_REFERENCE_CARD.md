# 部署快速参考卡片

## 🎯 三种部署方式

### 方式1: 一键部署（推荐）
```bash
./deploy_to_production.sh
```

### 方式2: 手动部署
```bash
# 1. 备份
ssh user@meiyueart.com 'cp /path/to/app/admin-backend/routes/user_system.py ~/backups/$(date +%Y%m%d_%H%M%S)/'

# 2. 上传
scp admin-backend/routes/user_system.py user@meiyueart.com:/path/to/app/admin-backend/routes/

# 3. 安装依赖
ssh user@meiyueart.com 'pip install bcrypt'

# 4. 重启服务
ssh user@meiyueart.com 'sudo supervisorctl restart lingzhi_admin_backend'

# 5. 验证
./verify_deployment.sh
```

### 方式3: CI/CD自动部署
```bash
git add .
git commit -m "fix: 修复推荐人显示和密码修改功能"
git push origin main
```

---

## 📋 部署前检查清单

- [ ] 代码已在本地测试通过
- [ ] 版本一致性检查通过
- [ ] 备份当前生产环境
- [ ] 通知团队成员即将部署
- [ ] 确认维护窗口（如需）

---

## ✅ 部署后验证

### 快速验证（5分钟）
```bash
# 1. 运行验证脚本
./verify_deployment.sh

# 2. 检查服务状态
ssh user@meiyueart.com 'sudo supervisorctl status lingzhi_admin_backend'

# 3. 查看最新日志
ssh user@meiyueart.com 'sudo tail -20 /var/log/flask_backend.log'
```

### 完整验证（15分钟）
- [ ] 健康检查通过
- [ ] 用户登录正常
- [ ] 推荐人字段显示
- [ ] 密码修改功能正常
- [ ] 前端页面访问正常
- [ ] 无错误日志

---

## 🔄 紧急回滚

```bash
ssh user@meiyueart.com << 'ENDSSH'
  BACKUP=$(ls -t ~/backups/ | head -1)
  cp ~/backups/$BACKUP/user_system.py /path/to/app/admin-backend/routes/
  sudo supervisorctl restart lingzhi_admin_backend
ENDSSH
```

---

## 📞 常见问题快速解决

| 问题 | 快速解决 |
|------|---------|
| SSH连接失败 | 检查密钥：`ssh -vvv user@meiyueart.com` |
| bcrypt模块缺失 | `pip install bcrypt` |
| 服务启动失败 | `sudo supervisorctl tail -f lingzhi_admin_backend stderr` |
| API返回500 | `sudo grep ERROR /var/log/flask_backend.log` |
| 推荐人空白 | 检查代码更新：`md5sum user_system.py` |
| 密码修改404 | 检查蓝图注册：`grep change_password app.py` |

---

## 🔧 关键命令速查

### 服务器操作
```bash
# 连接服务器
ssh user@meiyueart.com

# 查看服务状态
sudo supervisorctl status

# 查看日志
sudo tail -f /var/log/flask_backend.log

# 重启服务
sudo supervisorctl restart lingzhi_admin_backend
```

### 本地操作
```bash
# 版本一致性检查
./check_version_consistency.sh

# 部署
./deploy_to_production.sh

# 验证
./verify_deployment.sh
```

### 数据库操作
```bash
# 连接数据库
sqlite3 /path/to/app/admin-backend/data/lingzhi_ecosystem.db

# 查看表结构
.schema referral_relationships

# 查询推荐人关系
SELECT * FROM referral_relationships LIMIT 5;
```

---

## 📞 联系方式

| 团队 | 邮箱 |
|------|------|
| 运维团队 | ops@meiyueart.com |
| 开发团队 | dev@meiyueart.com |
| 紧急支持 | emergency@meiyueart.com |

---

**打印此卡片并贴在显示器旁边，方便快速查阅！**
