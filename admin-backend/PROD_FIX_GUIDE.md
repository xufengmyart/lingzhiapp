# 生产环境修复指南

## 问题说明

1. **用户登录问题**：
   - 用户马伟娟（ID=19）在生产环境无法用密码123登录
   - 实际可用密码是123456
   - 需要将密码改为123

2. **总灵值显示问题**：
   - 主页总灵值显示为0
   - 需要检查前端显示逻辑

## 本地环境状态

✅ **已完成修复**：
- 所有用户密码已重置为123
- 用户马伟娟ID=1025，可以用密码123登录
- 服务运行正常（http://localhost:8080）

## 生产环境修复步骤

由于无法直接访问生产环境数据库，需要通过以下方式修复：

### 方案1：SSH登录生产环境执行修复脚本

1. **SSH登录生产服务器**
   ```bash
   ssh root@meiyueart.com
   ```

2. **找到生产环境数据库**
   ```bash
   find / -name "lingzhi_ecosystem.db" 2>/dev/null
   ```

3. **执行修复脚本**
   ```bash
   cd /path/to/admin-backend
   python3 prod_fix.py
   ```

### 方案2：通过API直接重置密码

1. **获取管理员token**
   ```bash
   curl -X POST https://meiyueart.com/api/login \
     -H "Content-Type: application/json" \
     -d '{"username": "admin", "password": "123456"}'
   ```

2. **重置马伟娟的密码**
   ```bash
   curl -X POST https://meiyueart.com/api/admin/user/reset-password \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <admin_token>" \
     -d '{"username": "马伟娟", "new_password": "123"}'
   ```

### 方案3：直接修改数据库

1. **登录生产服务器**
   ```bash
   ssh root@meiyueart.com
   ```

2. **连接数据库**
   ```bash
   sqlite3 /path/to/lingzhi_ecosystem.db
   ```

3. **更新密码**
   ```python
   import bcrypt
   password = "123"
   password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
   UPDATE users SET password_hash = '<password_hash>' WHERE id = 19;
   ```

## 验证修复

修复完成后，验证用户登录：
```bash
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "马伟娟", "password": "123"}'
```

## 总灵值显示问题修复

检查前端代码中的总灵值显示逻辑：

1. **检查API返回数据**
   ```bash
   curl -X GET https://meiyueart.com/api/user/info \
     -H "Authorization: Bearer <user_token>"
   ```

2. **检查前端Dashboard组件**
   - 文件：`web-app/src/pages/Dashboard.tsx`
   - 检查`user?.total_lingzhi`的显示逻辑

3. **检查缓存机制**
   - 清除localStorage缓存
   - 重新加载页面

## 本地测试结果

✅ 所有用户已成功创建并可用密码123登录：
- 马伟娟 (ID: 1025)
- 许锋 (ID: 1)
- 许蓝月 (ID: 1026)
- 黄爱莉 (ID: 1027)
- 许韩玲 (ID: 1028)
- 许芳侠 (ID: 1029)
- 许武勤 (ID: 1030)
- 弓俊芳 (ID: 1031)
- 许明芳 (ID: 1032)
- 许秀芳 (ID: 1033)

## 下一步

1. **在生产环境执行修复脚本**
2. **验证用户登录**
3. **检查总灵值显示**
4. **重启生产服务**
