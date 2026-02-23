# 🚀 生产环境部署快速参考卡片

> **重要**: 每次部署前必须先阅读此卡片！

---

## 📋 一键部署流程（标准）

### 步骤1: 修改代码
```bash
cd /workspace/projects/admin-backend/routes
vi user_system.py  # 修改文件
```

### 步骤2: 执行部署
```bash
bash /workspace/projects/deploy_one_click.sh
```

### 步骤3: 修复字段错误（如有）
```bash
# 检查错误
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "sqlite3 /app/meiyueart-backend/data/lingzhi_ecosystem.db '.schema 表名'"

# 修改文件
vi /workspace/projects/admin-backend/routes/xxx.py

# 上传文件
sshpass -p 'Meiyue@root123' scp -P 22 \
  /workspace/projects/admin-backend/routes/xxx.py \
  root@meiyueart.com:/app/meiyueart-backend/routes/

# 重启服务
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "pkill -f 'python.*app.py' && cd /app/meiyueart-backend && \
   nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &"
```

### 步骤4: 验证部署
```bash
# 健康检查
curl -s https://meiyueart.com/api/health | python3 -m json.tool

# 用户登录
TOKEN=$(curl -s -X POST https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

# 用户信息（推荐人字段）
curl -s -X GET "https://meiyueart.com/api/user/info" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 密码修改
curl -s -X POST "https://meiyueart.com/api/user/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"oldPassword": "admin123", "newPassword": "NewPass123!"}' \
  | python3 -m json.tool
```

---

## 🔑 固定信息

### 服务器信息
```
服务器: meiyueart.com
IP: 123.56.142.143
端口: 22
用户: root
密码: Meiyue@root123
```

### 路径信息
```
后端: /app/meiyueart-backend
数据库: /app/meiyueart-backend/data/lingzhi_ecosystem.db
前端: /var/www/meiyueart.com
日志: /var/log/meiyueart-backend/app.log
备份: /var/www/backups/
```

### 测试账号
```
管理员: admin / admin123
普通用户: 马伟娟 / 123
其他用户: 所有用户密码123
```

---

## ⚠️ 常见字段错误

### referral_relationships 表
| 错误 | 正确 |
|------|------|
| `referred_user_id` | `referee_id` ✅ |

---

## 📝 验证检查清单

- [ ] 健康检查通过
- [ ] 用户登录正常
- [ ] 推荐人字段显示
- [ ] 密码修改功能正常
- [ ] API响应时间 < 5秒
- [ ] 服务状态正常
- [ ] 日志无ERROR

---

## 📚 相关文档

- **标准流程**: `/workspace/projects/STANDARD_DEPLOYMENT_PROCESS.md`
- **部署历史**: `/workspace/projects/deploy_archive/DEPLOYMENT_HISTORY.md`
- **部署脚本**: `/workspace/projects/deploy_one_click.sh`

---

**重要**: 以后所有部署必须严格按照标准流程执行！

**流程版本**: v1.0
**最后更新**: 2026-02-22
