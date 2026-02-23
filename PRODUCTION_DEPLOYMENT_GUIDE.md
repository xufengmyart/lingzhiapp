# 生产环境部署指南

**生成日期**: 2026-02-22
**部署目标**: meiyueart.com
**部署类型**: 功能修复和新功能添加

---

## 部署摘要

本次部署包括以下修复和新功能：

1. ✅ **推荐人信息显示修复** - 修复用户信息API，添加推荐人字段
2. ✅ **密码修改功能** - 确保修改密码API正常工作

---

## 部署文件清单

### 需要部署的后端文件

| 文件 | 路径 | 修改内容 |
|------|------|---------|
| user_system.py | admin-backend/routes/user_system.py | 添加推荐人信息查询和返回逻辑 |

### 不需要修改的文件

| 文件 | 路径 | 说明 |
|------|------|------|
| change_password.py | admin-backend/routes/change_password.py | 已存在，确认代码正确 |
| app.py | admin-backend/app.py | 已正确注册change_password蓝图 |

---

## 详细修改说明

### 1. 用户信息API修复 - 添加推荐人字段

**文件**: `admin-backend/routes/user_system.py`

**修改内容**: 在`get_user_info()`函数中添加推荐人信息查询

**修改前**:
```python
# 获取用户灵值余额
user_balance = conn.execute(
    'SELECT total_lingzhi FROM users WHERE id = ?',
    (user_id,)
).fetchone()

conn.close()

# ... 返回用户数据
```

**修改后**:
```python
# 获取用户灵值余额
user_balance = conn.execute(
    'SELECT total_lingzhi FROM users WHERE id = ?',
    (user_id,)
).fetchone()

# 获取用户推荐人信息
referral_info = conn.execute(
    '''
    SELECT
        rr.referrer_id,
        u.username as referrer_username,
        u.avatar_url as referrer_avatar
    FROM referral_relationships rr
    LEFT JOIN users u ON rr.referrer_id = u.id
    WHERE rr.referred_user_id = ?
    LIMIT 1
    ''',
    (user_id,)
).fetchone()

conn.close()

# ... 添加推荐人信息到返回数据
if referral_info:
    referral_dict = dict(referral_info)
    user_data['referrer'] = {
        'id': referral_dict.get('referrer_id'),
        'username': referral_dict.get('referrer_username', ''),
        'avatar': referral_dict.get('referrer_avatar', '')
    }
else:
    user_data['referrer'] = None
```

**影响API**:
- `GET /api/user/info` - 获取用户信息

**返回数据变化**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 10,
      "username": "admin",
      "referrer": {
        "id": 5,
        "username": "referrer_name",
        "avatar": "/uploads/avatars/xxx.png"
      }
      // ... 其他字段
    }
  }
}
```

---

## 部署步骤

### 准备阶段

1. **备份当前生产环境**
   ```bash
   # SSH登录到生产服务器
   ssh user@meiyueart.com

   # 备份应用目录
   cd /path/to/app
   tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz admin-backend
   ```

2. **备份数据库**
   ```bash
   cd /path/to/app/admin-backend
   cp data/lingzhi_ecosystem.db data/lingzhi_ecosystem.db.backup_$(date +%Y%m%d_%H%M%S)
   ```

### 部署后端文件

1. **上传修改后的文件**
   ```bash
   # 在本地执行
   scp admin-backend/routes/user_system.py user@meiyueart.com:/path/to/app/admin-backend/routes/
   ```

2. **验证文件上传**
   ```bash
   # SSH登录到生产服务器
   ssh user@meiyueart.com

   # 检查文件是否存在
   ls -lh /path/to/app/admin-backend/routes/user_system.py

   # 检查文件内容是否正确
   grep -A 10 "获取用户推荐人信息" /path/to/app/admin-backend/routes/user_system.py
   ```

### 重启服务

1. **重启Flask应用**
   ```bash
   # 使用supervisor（推荐）
   sudo supervisorctl restart lingzhi_admin_backend

   # 或使用systemd
   sudo systemctl restart lingzhi-backend

   # 或使用pm2
   pm2 restart lingzhi-backend

   # 或手动重启
   pkill -f "python.*admin-backend"
   cd /path/to/app/admin-backend
   nohup python3 app.py > /var/log/flask_backend.log 2>&1 &
   ```

2. **检查服务状态**
   ```bash
   # 检查进程
   ps aux | grep "python.*admin-backend"

   # 检查日志
   tail -n 50 /var/log/flask_backend.log

   # 检查健康状态
   curl https://meiyueart.com/api/health
   ```

### 验证部署

1. **测试认证功能**
   ```bash
   # 登录获取token
   TOKEN=$(curl -s -X POST https://meiyueart.com/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "123"}' \
     | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

   echo "Token: $TOKEN"
   ```

2. **测试用户信息API（验证推荐人字段）**
   ```bash
   curl -s -X GET "https://meiyueart.com/api/user/info" \
     -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
   ```

   **预期结果**: 返回的用户数据中包含`referrer`字段
   ```json
   {
     "data": {
       "user": {
         "id": 10,
         "username": "admin",
         "referrer": {
           "id": 5,
           "username": "referrer_name",
           "avatar": "/uploads/avatars/xxx.png"
         }
         // ...
       }
     }
   }
   ```

3. **测试密码修改功能**
   ```bash
   curl -s -X POST "https://meiyueart.com/api/user/change-password" \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"oldPassword": "123", "newPassword": "NewPassword123!"}' \
     | python3 -m json.tool
   ```

   **预期结果**: 成功返回
   ```json
   {
     "success": true,
     "message": "密码修改成功"
   }
   ```

   **如果返回404错误**: 说明change_password模块未正确加载
   - 检查日志中的错误信息
   - 确认bcrypt模块已安装: `pip install bcrypt`
   - 确认database.py文件存在

---

## 回滚方案

如果部署后出现问题，立即执行回滚：

1. **恢复文件**
   ```bash
   cd /path/to/app
   tar -xzf backup_YYYYMMDD_HHMMSS.tar.gz admin-backend/routes/user_system.py
   ```

2. **恢复数据库**
   ```bash
   cd /path/to/app/admin-backend
   cp data/lingzhi_ecosystem.db.backup_YYYYMMDD_HHMMSS data/lingzhi_ecosystem.db
   ```

3. **重启服务**
   ```bash
   sudo supervisorctl restart lingzhi_admin_backend
   ```

---

## 监控和日志

### 关键日志位置

| 日志类型 | 路径 | 说明 |
|---------|------|------|
| 应用日志 | /var/log/flask_backend.log | Flask应用主日志 |
| 错误日志 | /var/log/lingzhi/error.log | 错误日志 |
| Nginx日志 | /var/log/nginx/access.log | Nginx访问日志 |
| Nginx日志 | /var/log/nginx/error.log | Nginx错误日志 |

### 监控指标

1. **API响应时间**
   ```bash
   curl -w "@curl-format.txt" -o /dev/null -s "https://meiyueart.com/api/health"
   ```

2. **错误率**
   ```bash
   grep "ERROR\|Exception" /var/log/flask_backend.log | tail -20
   ```

3. **数据库查询性能**
   ```bash
   # 检查数据库文件大小
   ls -lh /path/to/app/admin-backend/data/lingzhi_ecosystem.db

   # 检查数据库锁定
   lsof /path/to/app/admin-backend/data/lingzhi_ecosystem.db
   ```

---

## 常见问题排查

### 问题1: 推荐人字段返回null

**可能原因**:
- referral_relationships表没有推荐关系数据
- 用户没有推荐人

**排查步骤**:
```bash
# SSH登录生产服务器
ssh user@meiyueart.com

# 连接数据库
sqlite3 /path/to/app/admin-backend/data/lingzhi_ecosystem.db

# 查询推荐关系
SELECT * FROM referral_relationships WHERE referred_user_id = 10;
```

### 问题2: 密码修改API返回404

**可能原因**:
- change_password模块未正确加载
- bcrypt模块未安装

**排查步骤**:
```bash
# 检查bcrypt是否安装
pip list | grep bcrypt

# 如果未安装，安装它
pip install bcrypt

# 检查服务日志
tail -n 100 /var/log/flask_backend.log | grep "change_password"

# 重启服务
sudo supervisorctl restart lingzhi_admin_backend
```

### 问题3: API响应缓慢

**可能原因**:
- 数据库查询慢
- 数据库锁定

**排查步骤**:
```bash
# 检查数据库锁定
lsof /path/to/app/admin-backend/data/lingzhi_ecosystem.db

# 检查数据库查询
# 添加SQL查询日志到app.py，然后查看慢查询

# 考虑添加数据库索引
sqlite3 /path/to/app/admin-backend/data/lingzhi_ecosystem.db << EOF
CREATE INDEX IF NOT EXISTS idx_referral_referred ON referral_relationships(referred_user_id);
EOF
```

---

## 部署检查清单

部署前检查：
- [ ] 已备份当前生产环境
- [ ] 已备份数据库
- [ ] 已在本地测试修改的代码
- [ ] 已准备回滚方案

部署后检查：
- [ ] 服务已重启并正常运行
- [ ] 健康检查API返回正常
- [ ] 用户登录功能正常
- [ ] 用户信息API返回推荐人字段
- [ ] 密码修改功能正常
- [ ] 没有新的错误日志
- [ ] API响应时间正常

---

## 联系信息

**部署负责人**: 待定
**技术支持**: 待定
**紧急联系**: 待定

---

**文档版本**: 1.0
**最后更新**: 2026-02-22
