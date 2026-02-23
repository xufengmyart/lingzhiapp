# 后台管理与前端对应关系详细说明

## 概述

本文档详细说明后台管理 API 与前端页面的对应关系，帮助开发者快速理解系统架构。

## 目录结构

```
前端 (React)                    后端 (Flask API)
================================================================================
src/pages/
├── AdminLogin.tsx      ←→    POST /api/admin/login
│                             POST /api/admin/logout
│
├── AdminDashboard.tsx  ←→    GET  /api/admin/stats/overview
│                             GET  /api/admin/system/status
│
├── UserManagement.tsx  ←→    GET  /api/admin/users
│                             GET  /api/admin/users/stats
│                             GET  /api/admin/users/<id>
│                             PUT  /api/admin/users/<id>/status
│                             PUT  /api/admin/users/<id>/lingzhi
│
├── RoleManagement.tsx  ←→    GET  /api/admin/roles
│                             POST /api/admin/roles
│                             PUT  /api/admin/roles/<id>
│                             DELETE /api/admin/roles/<id>
│                             GET  /api/admin/permissions
│                             POST /api/admin/permissions
│
├── UserTypeManagement.tsx ←→  GET  /api/admin/user-types
│                             POST /api/admin/user-types
│                             PUT  /api/admin/user-types/<id>
│                             DELETE /api/admin/user-types/<id>
│
├── AgentManagement.tsx  ←→    GET  /api/admin/agents
│                             POST /api/admin/agents
│                             PUT  /api/admin/agents/<id>
│                             DELETE /api/admin/agents/<id>
│                             GET  /api/admin/agents/<id>/stats
│
├── KnowledgeManagement.tsx ←→ GET  /api/admin/knowledge-bases
│                             POST /api/admin/knowledge-bases
│                             PUT  /api/admin/knowledge-bases/<id>
│                             DELETE /api/admin/knowledge-bases/<id>
│                             GET  /api/admin/knowledge-bases/<id>/documents
│                             POST /api/admin/knowledge-bases/<id>/documents
│
├── ProjectManagement.tsx ←→    GET  /api/admin/projects
│                             POST /api/admin/projects
│                             PUT  /api/admin/projects/<id>
│                             DELETE /api/admin/projects/<id>
│
├── NewsManagement.tsx   ←→    GET  /api/admin/news/articles
│                             POST /api/admin/news/articles
│                             PUT  /api/admin/news/articles/<id>
│                             DELETE /api/admin/news/articles/<id>
│
└── SystemSettings.tsx   ←→    GET  /api/admin/settings
│                             PUT  /api/admin/settings
│                             GET  /api/admin/system/status
│                             GET  /api/admin/system/logs
```

## 详细对应关系

### 1. 登录模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| AdminLogin.tsx | `/api/admin/login` | POST | 管理员登录 |
| AdminLogin.tsx | `/api/admin/logout` | POST | 管理员登出 |

**前端调用示例：**
```typescript
const login = async (username: string, password: string) => {
  const response = await fetch('/api/admin/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password })
  })
  const data = await response.json()
  if (data.success) {
    localStorage.setItem('adminToken', data.data.token)
  }
}
```

**后端响应示例：**
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 1,
      "username": "admin",
      "role": "admin"
    }
  }
}
```

---

### 2. 仪表盘模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| AdminDashboard.tsx | `/api/admin/stats/overview` | GET | 总体统计数据 |
| AdminDashboard.tsx | `/api/admin/system/status` | GET | 系统状态 |

**前端调用示例：**
```typescript
const loadStats = async () => {
  const token = localStorage.getItem('adminToken')
  const response = await fetch('/api/admin/stats/overview', {
    headers: { 'Authorization': `Bearer ${token}` }
  })
  const data = await response.json()
  setStats(data.data)
}
```

**后端响应示例：**
```json
{
  "success": true,
  "data": {
    "users": 1234,
    "agents": 56,
    "knowledge_bases": 23,
    "today_active": 89,
    "system": {
      "memory_percent": 65.5,
      "disk_percent": 75.2
    }
  }
}
```

---

### 3. 用户管理模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| UserManagement.tsx | `/api/admin/users` | GET | 获取用户列表 |
| UserManagement.tsx | `/api/admin/users` | GET | 搜索/筛选用户 |
| UserManagement.tsx | `/api/admin/users/stats` | GET | 用户统计 |
| UserManagement.tsx | `/api/admin/users/<id>` | GET | 获取用户详情 |
| UserManagement.tsx | `/api/admin/users/<id>/status` | PUT | 更新用户状态 |
| UserManagement.tsx | `/api/admin/users/<id>/lingzhi` | PUT | 修改用户灵值 |

**前端调用示例：**
```typescript
const loadUsers = async (page: number, keyword: string) => {
  const token = localStorage.getItem('adminToken')
  const response = await fetch(
    `/api/admin/users?page=${page}&keyword=${keyword}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  )
  const data = await response.json()
  setUsers(data.data.users)
}
```

**后端响应示例：**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "user001",
        "email": "user@example.com",
        "status": "active",
        "total_lingzhi": 1000,
        "created_at": "2024-01-01 10:00:00"
      }
    ],
    "total": 1234,
    "page": 1,
    "limit": 20
  }
}
```

---

### 4. 智能体管理模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| AgentManagement.tsx | `/api/admin/agents` | GET | 获取智能体列表 |
| AgentManagement.tsx | `/api/admin/agents` | POST | 创建智能体 |
| AgentManagement.tsx | `/api/admin/agents/<id>` | GET | 获取智能体详情 |
| AgentManagement.tsx | `/api/admin/agents/<id>` | PUT | 更新智能体 |
| AgentManagement.tsx | `/api/admin/agents/<id>` | DELETE | 删除智能体 |
| AgentManagement.tsx | `/api/admin/agents/<id>/stats` | GET | 智能体统计 |

**前端调用示例：**
```typescript
const createAgent = async (agentData: any) => {
  const token = localStorage.getItem('adminToken')
  const response = await fetch('/api/admin/agents', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify(agentData)
  })
  return await response.json()
}
```

**后端响应示例：**
```json
{
  "success": true,
  "message": "智能体创建成功",
  "data": {
    "id": 123
  }
}
```

---

### 5. 知识库管理模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| KnowledgeManagement.tsx | `/api/admin/knowledge-bases` | GET | 获取知识库列表 |
| KnowledgeManagement.tsx | `/api/admin/knowledge-bases` | POST | 创建知识库 |
| KnowledgeManagement.tsx | `/api/admin/knowledge-bases/<id>` | GET | 获取知识库详情 |
| KnowledgeManagement.tsx | `/api/admin/knowledge-bases/<id>` | PUT | 更新知识库 |
| KnowledgeManagement.tsx | `/api/admin/knowledge-bases/<id>` | DELETE | 删除知识库 |
| KnowledgeManagement.tsx | `/api/admin/knowledge-bases/<id>/documents` | GET | 获取文档列表 |
| KnowledgeManagement.tsx | `/api/admin/knowledge-bases/<id>/documents` | POST | 上传文档 |

**前端调用示例：**
```typescript
const uploadDocument = async (kbId: number, file: File) => {
  const token = localStorage.getItem('adminToken')
  const formData = new FormData()
  formData.append('file', file)

  const response = await fetch(`/api/admin/knowledge-bases/${kbId}/documents`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  })
  return await response.json()
}
```

---

### 6. 角色权限管理模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| RoleManagement.tsx | `/api/admin/roles` | GET | 获取角色列表 |
| RoleManagement.tsx | `/api/admin/roles` | POST | 创建角色 |
| RoleManagement.tsx | `/api/admin/roles/<id>` | GET | 获取角色详情 |
| RoleManagement.tsx | `/api/admin/roles/<id>` | PUT | 更新角色 |
| RoleManagement.tsx | `/api/admin/roles/<id>` | DELETE | 删除角色 |
| RoleManagement.tsx | `/api/admin/permissions` | GET | 获取所有权限 |

**前端调用示例：**
```typescript
const createRole = async (roleData: any) => {
  const token = localStorage.getItem('adminToken')
  const response = await fetch('/api/admin/roles', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      name: 'editor',
      display_name: '编辑员',
      description: '可以编辑内容',
      level: 2,
      permissions: [1, 2, 3]
    })
  })
  return await response.json()
}
```

---

### 7. 用户类型管理模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| UserTypeManagement.tsx | `/api/admin/user-types` | GET | 获取用户类型列表 |
| UserTypeManagement.tsx | `/api/admin/user-types` | POST | 创建用户类型 |
| UserTypeManagement.tsx | `/api/admin/user-types/<id>` | GET | 获取用户类型详情 |
| UserTypeManagement.tsx | `/api/admin/user-types/<id>` | PUT | 更新用户类型 |
| UserTypeManagement.tsx | `/api/admin/user-types/<id>` | DELETE | 删除用户类型 |

**前端调用示例：**
```typescript
const createUserType = async (userTypeData: any) => {
  const token = localStorage.getItem('adminToken')
  const response = await fetch('/api/admin/user-types', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      name: 'vip',
      display_name: 'VIP 会员',
      description: '高级会员',
      level: 3,
      benefits: {
        "discount": 0.9,
        "priority": 1,
        "features": ["advanced_search", "export"]
      }
    })
  })
  return await response.json()
}
```

---

### 8. 新闻管理模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| NewsManagement.tsx | `/api/admin/news/articles` | GET | 获取新闻列表 |
| NewsManagement.tsx | `/api/admin/news/articles` | POST | 创建新闻 |
| NewsManagement.tsx | `/api/admin/news/articles/<id>` | GET | 获取新闻详情 |
| NewsManagement.tsx | `/api/admin/news/articles/<id>` | PUT | 更新新闻 |
| NewsManagement.tsx | `/api/admin/news/articles/<id>` | DELETE | 删除新闻 |
| NewsManagement.tsx | `/api/admin/news/categories` | GET | 获取新闻分类 |
| NewsManagement.tsx | `/api/admin/news/categories` | POST | 创建新闻分类 |

---

### 9. 项目管理模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| ProjectManagement.tsx | `/api/admin/projects` | GET | 获取项目列表 |
| ProjectManagement.tsx | `/api/admin/projects` | POST | 创建项目 |
| ProjectManagement.tsx | `/api/admin/projects/<id>` | GET | 获取项目详情 |
| ProjectManagement.tsx | `/api/admin/projects/<id>` | PUT | 更新项目 |
| ProjectManagement.tsx | `/api/admin/projects/<id>` | DELETE | 删除项目 |

---

### 10. 系统设置模块

| 前端组件 | API 端点 | 方法 | 说明 |
|---------|---------|------|------|
| SystemSettings.tsx | `/api/admin/settings` | GET | 获取系统设置 |
| SystemSettings.tsx | `/api/admin/settings` | PUT | 更新系统设置 |
| SystemSettings.tsx | `/api/admin/system/status` | GET | 获取系统状态 |
| SystemSettings.tsx | `/api/admin/system/logs` | GET | 获取系统日志 |

---

## 认证机制

所有后台管理 API 都使用 JWT Token 进行认证：

1. **登录获取 Token**
   ```
   POST /api/admin/login
   → 返回 token
   ```

2. **在请求头中携带 Token**
   ```
   GET /api/admin/users
   Headers: Authorization: Bearer <token>
   ```

3. **Token 有效期**
   - 默认 7 天
   - 过期后需要重新登录

---

## 错误处理

### 标准错误响应格式
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

### 常见错误码
| 错误码 | 说明 |
|--------|------|
| `UNAUTHORIZED` | 未认证（token 无效或过期） |
| `FORBIDDEN` | 无权限 |
| `NOT_FOUND` | 资源不存在 |
| `INVALID_PARAMS` | 参数错误 |
| `INTERNAL_ERROR` | 服务器内部错误 |

---

## 分页规范

所有列表接口都支持分页：

**请求参数：**
```
GET /api/admin/users?page=1&limit=20&status=active&keyword=test
```

**响应格式：**
```json
{
  "success": true,
  "data": {
    "items": [...],
    "total": 1234,
    "page": 1,
    "limit": 20
  }
}
```

---

## 数据验证

### 前端验证
- 表单字段必填性验证
- 字段类型验证
- 字段长度验证
- 业务逻辑验证

### 后端验证
- Token 有效性验证
- 权限验证
- 数据格式验证
- 业务规则验证
- SQL 注入防护

---

## 性能优化

1. **列表分页**：默认每页 20 条记录
2. **缓存机制**：统计数据缓存 5 分钟
3. **索引优化**：关键字段建立数据库索引
4. **异步处理**：耗时操作异步处理

---

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0.0 | 2024-02-01 | 初始版本 |
| v1.1.0 | 2024-02-17 | 完善模块，添加项目管理 |
