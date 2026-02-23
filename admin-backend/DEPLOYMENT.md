# 部署指南

## 快速部署

### 1. 重启后端服务

```bash
# 停止旧服务
pkill -f "python app.py"

# 启动新服务
cd /workspace/projects/admin-backend
nohup python app.py > /var/log/meiyueart-backend/app.log 2>&1 &

# 或者使用systemd（如果配置了）
sudo systemctl restart meiyueart-backend
```

### 2. 验证服务

```bash
# 检查服务状态
curl -s http://localhost:5000/api/projects

# 测试登录
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

### 3. 测试修改密码功能

```bash
# 获取token
TOKEN=$(curl -s -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}' \
  | python -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

# 修改密码
curl -X POST http://localhost:5000/api/user/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"oldPassword":"test123","newPassword":"newpassword123"}'
```

## 功能说明

### 新增API接口

#### 1. 用户修改密码
- **路径**: `POST /api/user/change-password`
- **需要认证**: 是（JWT Token）
- **请求体**:
```json
{
  "oldPassword": "当前密码",
  "newPassword": "新密码"
}
```
- **响应**:
```json
{
  "success": true,
  "message": "密码修改成功"
}
```

#### 2. 管理员重置用户密码
- **路径**: `PUT /api/admin/users/<user_id>/password`
- **需要认证**: 是（管理员Token）
- **请求体**:
```json
{
  "password": "新密码"
}
```
- **响应**:
```json
{
  "success": true,
  "message": "密码重置成功"
}
```

### 修复的API接口

#### 1. 项目列表
- **路径**: `GET /api/projects`
- **修复内容**:
  - 修复了SQL查询错误（移除不存在的表引用）
  - 修正了字段映射
  - 确保返回正确的数据格式
- **响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "项目名称",
      "description": "项目描述",
      "category": "项目类型",
      "status": "active",
      "budget": 10000.00,
      "progress": 0,
      "priority": "medium",
      "startDate": "2026-02-20",
      "endDate": "2026-03-20",
      "userId": 1,
      "userName": "创建者",
      "createdAt": "2026-02-20 10:00:00",
      "updatedAt": "2026-02-20 10:00:00"
    }
  ]
}
```

## 前端集成

### 用户修改密码界面

```javascript
// 修改密码示例
async function changePassword(oldPassword, newPassword) {
  const token = localStorage.getItem('token');
  
  const response = await fetch('/api/user/change-password', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      oldPassword: oldPassword,
      newPassword: newPassword
    })
  });
  
  const data = await response.json();
  
  if (data.success) {
    alert('密码修改成功');
  } else {
    alert('密码修改失败: ' + data.message);
  }
}
```

### 获取项目列表

```javascript
// 获取项目列表示例
async function getProjects() {
  const response = await fetch('/api/projects');
  const data = await response.json();
  
  if (data.success) {
    const projects = data.data; // 数组
    // 处理项目列表
    projects.forEach(project => {
      console.log(project.name);
    });
  }
}
```

## 测试用户

| 用户名 | 密码 | 角色 | 用途 |
|--------|------|------|------|
| admin | 123 | 管理员 | 后台管理、重置用户密码 |
| testuser | test123 | 普通用户 | 测试用户功能 |
| partner | partner123 | 合伙人 | 测试合伙人功能 |

## 注意事项

1. **JWT Token**: 确保前端在请求头中正确传递 `Authorization: Bearer <token>`
2. **密码长度**: 新密码必须至少6位
3. **密码验证**: 用户修改密码需要提供正确的旧密码
4. **管理员权限**: 重置用户密码需要管理员权限
5. **数据格式**: 项目列表接口返回的 `data` 字段是一个数组

## 故障排查

### 问题1: 接口返回404
**解决方案**: 检查后端服务是否已重启，路由是否正确注册

### 问题2: 接口返回401
**解决方案**: 检查JWT Token是否有效，是否正确传递

### 问题3: 接口返回500
**解决方案**: 查看后端日志 `/var/log/meiyueart-backend/app.log`

### 问题4: 修改密码失败
**解决方案**:
- 检查旧密码是否正确
- 检查新密码长度是否至少6位
- 检查新旧密码是否相同

## 监控和日志

### 查看后端日志
```bash
tail -f /var/log/meiyueart-backend/app.log
```

### 查看服务状态
```bash
ps aux | grep "python app.py"
```

### 重启服务
```bash
# 停止服务
pkill -f "python app.py"

# 启动服务
cd /workspace/projects/admin-backend
nohup python app.py > /var/log/meiyueart-backend/app.log 2>&1 &
```

## 更新日志

### 2026-02-20
- ✅ 修复项目管理接口（/projects）数据格式问题
- ✅ 新增用户修改密码功能
- ✅ 新增管理员重置用户密码功能
- ✅ 优化JWT Token验证
- ✅ 完善错误处理和日志记录
