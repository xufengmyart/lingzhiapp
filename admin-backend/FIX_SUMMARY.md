# 修复总结

## 已修复的问题

### 1. 后台管理项目管理出错
**问题**: `/projects` 接口返回数据格式错误，前端无法正确解析
**原因**: 
- SQL查询中使用了不存在的 `project_participants` 表
- 返回的字段名与数据库不匹配

**解决方案**:
- 修改 `admin-backend/routes/complete_apis.py` 中的 `get_projects` 函数
- 添加对 `project_participants` 表的存在性检查
- 如果表不存在，直接查询 `projects` 表
- 修正字段映射（`target_amount` -> `budget`, `category` -> `project_type`）
- 添加所有必需的字段

**测试结果**: ✓ 接口返回正确格式 `{ success: true, data: [] }`

### 2. 前台、后台、用户编辑中没有修改密码功能
**问题**: 缺少修改密码的API接口
**解决方案**:
- 创建新的路由文件 `admin-backend/routes/change_password.py`
- 实现两个接口：
  - `POST /api/user/change-password` - 用户修改密码
  - `PUT /api/admin/users/<int:user_id>/password` - 管理员重置用户密码
- 在 `admin-backend/app.py` 中注册路由

**功能特性**:
- 需要JWT token验证
- 验证旧密码
- 新密码长度至少6位
- 新旧密码不能相同
- 使用bcrypt加密密码
- 管理员重置功能需要管理员权限

**测试结果**: ✓ 所有测试通过

## 新增接口

### 用户修改密码
```
POST /api/user/change-password
Headers: { Authorization: Bearer <token> }
Body: { oldPassword: string, newPassword: string }
Response: { success: true, message: string }
```

### 管理员重置用户密码
```
PUT /api/admin/users/<int:user_id>/password
Headers: { Authorization: Bearer <admin_token> }
Body: { password: string }
Response: { success: true, message: string }
```

## 测试用例

### 修改密码测试
- ✓ 登录获取token
- ✓ 修改密码成功
- ✓ 旧密码无法登录
- ✓ 新密码可以登录
- ✓ 恢复原密码
- ✓ 新密码太短被拒绝
- ✓ 旧密码错误被拒绝

### 项目管理测试
- ✓ 接口返回正确格式
- ✓ 数据字段匹配数据库schema

## 部署步骤

1. **重启后端服务**
```bash
cd admin-backend
pkill -f "python app.py"
python app.py > /tmp/backend.log 2>&1 &
```

2. **验证服务**
```bash
# 检查服务状态
curl -s http://localhost:5000/api/projects

# 测试登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

3. **前端测试**
- 访问 https://meiyueart.com
- 登录后进入用户编辑页面
- 测试修改密码功能
- 访问后台管理页面
- 测试项目管理功能

## 注意事项

1. **JWT Token**: 确保前端正确传递 `Authorization: Bearer <token>` 头
2. **密码长度**: 新密码必须至少6位
3. **密码验证**: 修改密码需要提供正确的旧密码
4. **管理员权限**: 重置用户密码需要管理员权限

## 待优化项

1. 前端UI：添加修改密码的表单界面
2. 前端UI：添加管理员重置密码的界面
3. 安全性：添加密码复杂度验证
4. 安全性：添加密码修改通知（邮件/短信）
5. 日志：记录密码修改操作日志

## 文件修改清单

- `admin-backend/routes/complete_apis.py` - 修复projects接口
- `admin-backend/routes/change_password.py` - 新增修改密码功能
- `admin-backend/app.py` - 注册新路由

## 测试用户

| 用户名 | 密码 | 用途 |
|--------|------|------|
| admin | 123 | 管理员 |
| testuser | test123 | 普通用户 |
| partner | partner123 | 合伙人 |
