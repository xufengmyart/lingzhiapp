# 🚀 生产环境标准部署流程（固定版本）

> **重要**: 以后所有部署必须严格按照此流程执行，不得擅自修改！

**版本**: v1.0
**创建时间**: 2026-02-22
**最后更新**: 2026-02-22
**状态**: ✅ 已验证可用

---

## 📋 部署流程总览

```
┌─────────────────────────────────────────────────────────────┐
│              生产环境标准部署流程（6步）                      │
└─────────────────────────────────────────────────────────────┘

1️⃣  准备阶段（代码修复）
    ↓
2️⃣  本地测试验证
    ↓
3️⃣  一键自动化部署
    ↓
4️⃣  修复字段错误（如有）
    ↓
5️⃣  生产环境验证
    ↓
6️⃣  归档文档
```

---

## 📝 标准部署步骤（严格执行）

### 步骤1: 准备阶段（代码修复）

**操作**: 在 `/workspace/projects/admin-backend/routes/` 目录下修改相关文件

**常见修复类型**:
- 修复字段错误（如：`referred_user_id` → `referee_id`）
- 修复逻辑错误
- 添加新功能

**示例**:
```bash
cd /workspace/projects/admin-backend/routes
vi user_system.py  # 修改文件
```

**验证**:
```bash
grep -n "关键字" user_system.py  # 确认修改
```

---

### 步骤2: 本地测试验证

**操作**: 确认代码修改正确

**验证命令**:
```bash
# 检查文件内容
cat /workspace/projects/admin-backend/routes/user_system.py

# 检查语法
python3 -m py_compile /workspace/projects/admin-backend/routes/user_system.py
```

---

### 步骤3: 一键自动化部署

**操作**: 执行标准部署脚本

**命令**:
```bash
bash /workspace/projects/deploy_one_click.sh
```

**脚本会自动执行**:
1. ✅ 清理云服务器垃圾
2. ✅ 备份生产环境
3. ✅ 上传后端代码
4. ✅ 部署前端代码
5. ✅ 更新Nginx配置
6. ✅ 重启后端服务
7. ✅ 验证部署结果

**预期输出**:
```
=========================================
🚀 灵值生态园 - 一键全自动部署
=========================================

📋 步骤 1/6: 清理云服务器垃圾...
✅ 云服务器垃圾清理完成

📋 步骤 2/6: 备份生产环境...
✅ 生产环境备份完成

📋 步骤 3/6: 上传后端代码...
✅ 后端代码上传完成

📋 步骤 4/6: 保留生产环境数据库...
✅ 保留生产环境数据库（不覆盖）

📋 步骤 5/7: 部署前端代码...
✅ 前端代码部署完成

📋 步骤 6/7: 更新Nginx配置并重启后端服务...
✅ Nginx配置更新完成
✅ 后端服务重启完成

📋 步骤 7/7: 验证部署...
✅ 健康检查通过
✅ 管理员登录测试通过
✅ 用户登录测试通过

=========================================
✅ 部署完成！
=========================================
```

---

### 步骤4: 修复字段错误（如有）

**操作**: 如果部署后出现数据库字段错误，立即修复

**检查错误**:
```bash
# 查看生产环境数据库表结构
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "sqlite3 /app/meiyueart-backend/data/lingzhi_ecosystem.db '.schema 表名'"
```

**常见字段错误**:
- `referred_user_id` → `referee_id` (referral_relationships表)
- 其他字段名不匹配

**修复步骤**:
```bash
# 1. 修改本地文件
vi /workspace/projects/admin-backend/routes/对应文件.py

# 2. 上传修复文件
sshpass -p 'Meiyue@root123' scp -P 22 \
  /workspace/projects/admin-backend/routes/对应文件.py \
  root@meiyueart.com:/app/meiyueart-backend/routes/

# 3. 重启服务
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "pkill -f 'python.*app.py' 2>/dev/null || true; \
   cd /app/meiyueart-backend && \
   nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 & \
   sleep 3 && echo '服务已重启'"

# 4. 等待服务启动
sleep 5
```

---

### 步骤5: 生产环境验证

**操作**: 执行完整的功能验证

**验证命令**:

#### 5.1 健康检查
```bash
curl -s https://meiyueart.com/api/health | python3 -m json.tool
```

**预期结果**:
```json
{
  "database": "connected",
  "status": "healthy",
  "success": true
}
```

#### 5.2 用户登录
```bash
TOKEN=$(curl -s -X POST https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

echo "Token: $TOKEN"
```

**预期结果**: 输出token字符串

#### 5.3 用户信息API（验证推荐人字段）
```bash
curl -s -X GET "https://meiyueart.com/api/user/info" \
  -H "Authorization: Bearer $TOKEN" \
  | python3 -m json.tool
```

**预期结果**:
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 10,
      "username": "admin",
      "referrer": {  // ⭐ 重点：referrer字段必须存在
        "id": 123,
        "username": "推荐人名称",
        "avatar": "头像URL"
      }
    }
  }
}
```

#### 5.4 密码修改功能
```bash
curl -s -X POST "https://meiyueart.com/api/user/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"oldPassword": "admin123", "newPassword": "NewPass123!"}' \
  | python3 -m json.tool
```

**预期结果**:
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

**恢复密码**:
```bash
curl -s -X POST "https://meiyueart.com/api/user/change-password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"oldPassword": "NewPass123!", "newPassword": "admin123"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['message'])"
```

#### 5.5 其他功能（按需）
```bash
# API响应时间
time curl -s https://meiyueart.com/api/health > /dev/null

# 服务状态
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "ps aux | grep 'python.*app.py' | grep -v grep"

# 查看日志
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "tail -20 /var/log/meiyueart-backend/app.log"
```

---

### 步骤6: 归档文档

**操作**: 记录部署信息

**归档内容**:
```bash
# 创建部署记录
cat > /workspace/projects/deploy_record_$(date +%Y%m%d_%H%M%S).md << EOF
# 部署记录

## 基本信息
- 部署时间: $(date '+%Y-%m-%d %H:%M:%S')
- 部署人员: 自动化部署系统
- 部署版本: v$(date +%Y%m%d)

## 修复内容
- 文件: admin-backend/routes/user_system.py
- 修改: 修复数据库字段名（referred_user_id → referee_id）

## 验证结果
- ✅ 健康检查通过
- ✅ 用户登录正常
- ✅ 推荐人字段显示
- ✅ 密码修改功能正常

## 部署状态
✅ 部署成功
EOF
```

---

## ⚠️ 重要注意事项

### 1. 数据库字段映射（常见问题）

**表**: `referral_relationships`

| 错误字段名 | 正确字段名 | 说明 |
|-----------|-----------|------|
| `referred_user_id` | `referee_id` | 被推荐人ID |
| `referee_id` | `referee_id` | ✅ 正确 |
| `referrer_id` | `referrer_id` | ✅ 正确 |

### 2. 生产环境信息（固定）

```bash
服务器: meiyueart.com
IP: 123.56.142.143
端口: 22
用户: root
密码: Meiyue@root123
后端路径: /app/meiyueart-backend
数据库: /app/meiyueart-backend/data/lingzhi_ecosystem.db
前端路径: /var/www/meiyueart.com
日志: /var/log/meiyueart-backend/app.log
```

### 3. 测试账号（固定）

| 用户名 | 密码 | 角色 |
|--------|------|------|
| admin | admin123 | 管理员 |
| 马伟娟 | 123 | 普通用户 |
| 其他用户 | 123 | 普通用户 |

### 4. 服务管理命令

```bash
# 重启服务
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "pkill -f 'python.*app.py' && cd /app/meiyueart-backend && \
   nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &"

# 查看服务状态
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "ps aux | grep 'python.*app.py' | grep -v grep"

# 查看日志
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "tail -50 /var/log/meiyueart-backend/app.log"

# 查看数据库
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "sqlite3 /app/meiyueart-backend/data/lingzhi_ecosystem.db '.schema 表名'"
```

---

## 🚨 常见错误处理

### 错误1: no such column

**症状**: API返回 `{"error": "no such column: xxx", "success": false}`

**解决方案**:
```bash
# 1. 检查数据库表结构
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "sqlite3 /app/meiyueart-backend/data/lingzhi_ecosystem.db '.schema referral_relationships'"

# 2. 修改代码中的字段名
vi /workspace/projects/admin-backend/routes/对应文件.py

# 3. 上传修复文件
sshpass -p 'Meiyue@root123' scp -P 22 \
  /workspace/projects/admin-backend/routes/对应文件.py \
  root@meiyueart.com:/app/meiyueart-backend/routes/

# 4. 重启服务
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "pkill -f 'python.*app.py' && cd /app/meiyueart-backend && \
   nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &"
```

### 错误2: 502 Bad Gateway

**症状**: 访问API返回502错误

**解决方案**:
```bash
# 1. 检查服务是否运行
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "ps aux | grep 'python.*app.py' | grep -v grep"

# 2. 重启服务
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "pkill -f 'python.*app.py' && cd /app/meiyueart-backend && \
   nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &"

# 3. 等待服务启动
sleep 5

# 4. 验证健康检查
curl -s https://meiyueart.com/api/health
```

### 错误3: 部署脚本执行失败

**症状**: deploy_one_click.sh 执行失败

**解决方案**:
```bash
# 1. 检查网络连接
ping meiyueart.com

# 2. 检查SSH连接
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com "echo '连接成功'"

# 3. 检查SSH工具
which sshpass

# 4. 重新安装SSH工具
apt-get update && apt-get install -y sshpass openssh-client

# 5. 重新执行部署
bash /workspace/projects/deploy_one_click.sh
```

---

## 📊 验证检查清单

每次部署完成后，必须逐项确认：

- [ ] 健康检查通过：`curl https://meiyueart.com/api/health`
- [ ] 用户登录正常：admin/admin123 可以登录
- [ ] 用户信息API返回正确数据
- [ ] 推荐人字段显示（referrer字段存在）
- [ ] 密码修改功能正常
- [ ] API响应时间 < 5秒
- [ ] 服务状态正常（ps aux检查）
- [ ] 日志无ERROR级别错误
- [ ] 部署记录已归档

---

## 📁 相关文件

**部署脚本**:
- `/workspace/projects/deploy_one_click.sh` - 一键部署脚本（主脚本）

**配置文件**:
- `/workspace/projects/.ssh_config` - 生产环境配置

**文档**:
- `STANDARD_DEPLOYMENT_PROCESS.md` - 本文档（标准流程）

---

## 🎯 执行总结

**一句话**: 修改代码 → 执行deploy_one_click.sh → 修复字段错误 → 验证 → 归档

**核心命令**:
```bash
# 1. 修改代码
vi /workspace/projects/admin-backend/routes/xxx.py

# 2. 执行部署
bash /workspace/projects/deploy_one_click.sh

# 3. 修复字段错误（如需要）
# 修改 → 上传 → 重启

# 4. 验证
curl -s https://meiyueart.com/api/health
# ... 执行验证命令

# 5. 归档
# 创建部署记录
```

---

**重要**: 以后所有部署必须严格按照此流程执行，不得擅自修改！

**流程版本**: v1.0
**创建时间**: 2026-02-22
**验证状态**: ✅ 已验证可用
**下次更新**: 如有需要修改，必须更新本文档并重新验证
