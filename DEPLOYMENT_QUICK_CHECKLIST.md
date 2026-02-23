# ⚡ 部署快速检查清单

> 推荐人字段显示和密码修改功能修复 - 生产环境部署

**部署日期**: 2026-02-22
**部署人员**: _________________
**目标环境**: meiyueart.com

---

## 📋 部署前检查

### 环境检查
- [ ] SSH连接正常：`ssh user@meiyueart.com`
- [ ] 磁盘空间充足：`ssh user@meiyueart.com 'df -h'`
- [ ] 内存资源充足：`ssh user@meiyueart.com 'free -h'`

### 代码检查
- [ ] `user_system.py` 已更新（包含推荐人查询逻辑）
- [ ] `change_password.py` 存在（路由: `/api/user/change-password`）
- [ ] 本地测试通过
- [ ] 版本一致性检查通过

### 配置检查
- [ ] `deploy_config.sh` 已配置
- [ ] 生产服务器地址正确
- [ ] 应用路径正确
- [ ] 服务名称正确

---

## 🚀 部署执行清单

### 步骤1: 备份生产环境
```bash
# 执行备份
ssh user@meiyueart.com << 'ENDSSH'
    BACKUP_DIR="$HOME/backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p $BACKUP_DIR
    cp /var/www/meiyueart.com/admin-backend/routes/user_system.py $BACKUP_DIR/
    cp /var/www/meiyueart.com/admin-backend/routes/change_password.py $BACKUP_DIR/
    cp /var/www/meiyueart.com/admin-backend/data/lingzhi_ecosystem.db $BACKUP_DIR/
    echo "备份完成: $BACKUP_DIR"
ENDSSH
```

- [ ] 备份完成
- [ ] 备份路径已记录: _________________

---

### 步骤2: 上传修复文件
```bash
# 上传文件
scp admin-backend/routes/user_system.py \
    user@meiyueart.com:/var/www/meiyueart.com/admin-backend/routes/

scp admin-backend/routes/change_password.py \
    user@meiyueart.com:/var/www/meiyueart.com/admin-backend/routes/
```

- [ ] user_system.py 上传成功
- [ ] change_password.py 上传成功

---

### 步骤3: 安装依赖
```bash
# 安装bcrypt
ssh user@meiyueart.com "pip3 install bcrypt"
```

- [ ] bcrypt 安装成功
- [ ] 版本确认: `python3 -c "import bcrypt; print(bcrypt.__version__)"`

---

### 步骤4: 重启服务
```bash
# 重启服务
ssh user@meiyueart.com "sudo supervisorctl restart lingzhi_admin_backend"

# 检查状态
ssh user@meiyueart.com "sudo supervisorctl status lingzhi_admin_backend"
```

- [ ] 服务重启成功
- [ ] 服务状态: RUNNING
- [ ] 进程ID: _________________

---

### 步骤5: 等待服务启动
```bash
# 等待健康检查通过
for i in {1..30}; do
    if curl -sf https://meiyueart.com/api/health > /dev/null; then
        echo "✅ 服务已启动"
        break
    fi
    echo "等待服务启动... ($i/30)"
    sleep 2
done
```

- [ ] 服务启动成功
- [ ] 健康检查通过

---

## ✅ 部署验证清单

### API测试

#### 测试1: 健康检查
```bash
curl https://meiyueart.com/api/health
```

**预期结果**: `{"success":true,"status":"healthy","database":"connected"}`
- [ ] 通过

---

#### 测试2: 用户登录
```bash
TOKEN=$(curl -s -X POST https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")
```

**预期结果**: 获取到token字符串
- [ ] 通过

---

#### 测试3: 推荐人字段（核心）
```bash
curl -s -X GET https://meiyueart.com/api/user/info \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool
```

**预期结果**: 返回包含 `"referrer": {...}` 的JSON
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "admin",
      "referrer": {
        "id": 123,
        "username": "referrer_name",
        "avatar": "avatar_url"
      }
    }
  }
}
```
- [ ] referrer 字段存在
- [ ] referrer 包含 id
- [ ] referrer 包含 username
- [ ] referrer 包含 avatar

---

#### 测试4: 密码修改（核心）
```bash
curl -s -X POST https://meiyueart.com/api/user/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"oldPassword": "123", "newPassword": "TempPass123!"}'
```

**预期结果**:
- 如果有推荐人：返回 `{"success":true,"message":"密码修改成功"}`
- 如果没有推荐人：返回 `{"success":false,"message":"旧密码错误"}` 或相关错误
- ❌ 不应该返回404

- [ ] API可访问（非404）
- [ ] 返回正确的响应

---

#### 测试5: API响应时间
```bash
time curl -s https://meiyueart.com/api/health > /dev/null
```

**预期结果**: 响应时间 < 5秒
- [ ] 通过

---

### 功能验证

#### 浏览器验证
- [ ] 访问 https://meiyueart.com
- [ ] 登录系统
- [ ] 打开用户资料页面
- [ ] 检查推荐人字段显示
- [ ] 测试密码修改功能

---

### 日志检查

#### 服务日志
```bash
ssh user@meiyueart.com "sudo tail -50 /var/log/flask_backend.log"
```

- [ ] 无ERROR级别错误
- [ ] 无异常堆栈信息

---

## 📊 部署总结

### 测试结果统计

| 测试项 | 状态 | 备注 |
|--------|------|------|
| 健康检查 | [ ] | |
| 用户登录 | [ ] | |
| 推荐人字段 | [ ] | ⭐核心功能 |
| 密码修改 | [ ] | ⭐核心功能 |
| 响应时间 | [ ] | |

**通过率**: ___/5 (___%)

---

### 部署状态

- [ ] ✅ **部署成功** - 所有测试通过
- [ ] ⚠️ **部分成功** - 部分测试失败，需修复
- [ ] ❌ **部署失败** - 部署失败，需回滚

---

### 遇到的问题

| 问题 | 解决方案 | 状态 |
|------|---------|------|
| | | |
| | | |
| | | |

---

## 🔄 回滚操作（如需）

### 回滚步骤
```bash
# 1. 查找最新备份
ssh user@meiyueart.com "ls -lht ~/backups/ | head -5"

# 2. 恢复文件
BACKUP_DIR="YYYYMMDD_HHMMSS"
ssh user@meiyueart.com << 'ENDSSH'
    cp ~/backups/$BACKUP_DIR/user_system.py \
       /var/www/meiyueart.com/admin-backend/routes/
    cp ~/backups/$BACKUP_DIR/change_password.py \
       /var/www/meiyueart.com/admin-backend/routes/
ENDSSH

# 3. 重启服务
ssh user@meiyueart.com "sudo supervisorctl restart lingzhi_admin_backend"

# 4. 验证回滚
curl https://meiyueart.com/api/health
```

- [ ] 回滚完成
- [ ] 服务恢复正常

---

## 📝 部署记录

**部署开始时间**: ________:______
**部署完成时间**: ________:______
**总耗时**: ________ 分钟

**部署人员签名**: _________________

**审批人员签名**: _________________

---

## 📞 联系信息

| 团队 | 联系方式 | 职责 |
|------|---------|------|
| 运维团队 | ops@meiyueart.com | 部署执行、监控维护 |
| 开发团队 | dev@meiyueart.com | 代码修复、技术支持 |
| 紧急支持 | emergency@meiyueart.com | 24小时紧急响应 |

---

**检查清单版本**: v1.0
**创建时间**: 2026-02-22

**提示**: 请在部署过程中逐项勾选，确保所有步骤都已完成。
