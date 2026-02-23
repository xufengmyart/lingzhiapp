# API 参考文档

## 目录

1. [认证](#认证)
2. [用户管理](#用户管理)
3. [智能体管理](#智能体管理)
4. [知识库管理](#知识库管理)
5. [角色权限管理](#角色权限管理)
6. [用户类型管理](#用户类型管理)
7. [统计数据](#统计数据)
8. [系统管理](#系统管理)

---

## 认证

### POST /api/admin/login

管理员登录

**请求头：**
```
Content-Type: application/json
```

**请求体：**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**响应：**
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

## 用户管理

### GET /api/admin/users

获取用户列表

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| limit | integer | 否 | 每页数量，默认 20 |
| status | string | 否 | 用户状态筛选 |
| keyword | string | 否 | 关键词搜索（用户名/邮箱/手机） |

**响应：**
```json
{
  "success": true,
  "data": {
    "users": [
      {
        "id": 1,
        "username": "user001",
        "email": "user@example.com",
        "phone": "13800138000",
        "status": "active",
        "total_lingzhi": 1000,
        "created_at": "2024-01-01 10:00:00",
        "last_login_at": "2024-02-17 15:30:00"
      }
    ],
    "total": 1234,
    "page": 1,
    "limit": 20
  }
}
```

---

### GET /api/admin/users/stats

获取用户统计

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "total": 1234,
    "today_new": 10,
    "active": 567,
    "by_status": {
      "active": 1000,
      "inactive": 200,
      "banned": 34
    }
  }
}
```

---

### GET /api/admin/users/:id

获取用户详情

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "user": {
      "id": 1,
      "username": "user001",
      "email": "user@example.com",
      "phone": "13800138000",
      "status": "active",
      "total_lingzhi": 1000,
      "created_at": "2024-01-01 10:00:00"
    },
    "checkin_records": [],
    "lingzhi_records": []
  }
}
```

---

### PUT /api/admin/users/:id/status

更新用户状态

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "status": "active"
}
```

**响应：**
```json
{
  "success": true,
  "message": "用户状态更新成功"
}
```

---

## 智能体管理

### GET /api/admin/agents

获取智能体列表

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| limit | integer | 否 | 每页数量，默认 20 |
| status | string | 否 | 状态筛选 |
| keyword | string | 否 | 关键词搜索 |

**响应：**
```json
{
  "success": true,
  "data": {
    "agents": [
      {
        "id": 1,
        "name": "智能助手",
        "description": "通用智能助手",
        "system_prompt": "...",
        "model_config": {},
        "tools": [],
        "status": "active",
        "avatar_url": null,
        "created_at": "2024-01-01 10:00:00"
      }
    ],
    "total": 56,
    "page": 1,
    "limit": 20
  }
}
```

---

### POST /api/admin/agents

创建智能体

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "智能助手",
  "description": "通用智能助手",
  "system_prompt": {},
  "model_config": {
    "model": "gpt-4",
    "temperature": 0.7
  },
  "tools": ["web_search", "code_interpreter"],
  "status": "active",
  "avatar_url": null,
  "created_by": 1
}
```

**响应：**
```json
{
  "success": true,
  "message": "智能体创建成功",
  "data": {
    "id": 57
  }
}
```

---

### PUT /api/admin/agents/:id

更新智能体

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "智能助手",
  "description": "更新后的描述",
  "status": "active"
}
```

**响应：**
```json
{
  "success": true,
  "message": "智能体更新成功"
}
```

---

### DELETE /api/admin/agents/:id

删除智能体

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "message": "智能体删除成功"
}
```

---

## 知识库管理

### GET /api/admin/knowledge-bases

获取知识库列表

**请求头：**
```
Authorization: Bearer <token>
```

**查询参数：**
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| page | integer | 否 | 页码，默认 1 |
| limit | integer | 否 | 每页数量，默认 20 |
| keyword | string | 否 | 关键词搜索 |

**响应：**
```json
{
  "success": true,
  "data": {
    "knowledge_bases": [
      {
        "id": 1,
        "name": "产品文档",
        "description": "产品相关文档",
        "vector_db_id": "kb_123",
        "document_count": 100,
        "category_id": 1,
        "tags": ["产品", "文档"],
        "is_public": true,
        "view_count": 567,
        "created_at": "2024-01-01 10:00:00"
      }
    ],
    "total": 23,
    "page": 1,
    "limit": 20
  }
}
```

---

### POST /api/admin/knowledge-bases

创建知识库

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "产品文档",
  "description": "产品相关文档",
  "created_by": 1,
  "category_id": 1,
  "tags": ["产品", "文档"],
  "is_public": true
}
```

**响应：**
```json
{
  "success": true,
  "message": "知识库创建成功",
  "data": {
    "id": 24
  }
}
```

---

### PUT /api/admin/knowledge-bases/:id

更新知识库

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "产品文档",
  "description": "更新后的描述",
  "tags": ["产品", "文档", "更新"]
}
```

**响应：**
```json
{
  "success": true,
  "message": "知识库更新成功"
}
```

---

### DELETE /api/admin/knowledge-bases/:id

删除知识库

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "message": "知识库删除成功"
}
```

---

## 角色权限管理

### GET /api/admin/roles

获取角色列表

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "roles": [
      {
        "id": 1,
        "name": "admin",
        "display_name": "管理员",
        "description": "系统管理员",
        "level": 0,
        "is_system": true,
        "permissions": [
          {
            "id": 1,
            "name": "user.manage",
            "display_name": "用户管理",
            "module": "user"
          }
        ]
      }
    ]
  }
}
```

---

### POST /api/admin/roles

创建角色

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "editor",
  "display_name": "编辑员",
  "description": "内容编辑员",
  "level": 2,
  "is_system": false,
  "permissions": [1, 2, 3]
}
```

**响应：**
```json
{
  "success": true,
  "message": "角色创建成功",
  "data": {
    "id": 4
  }
}
```

---

### PUT /api/admin/roles/:id

更新角色

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "display_name": "编辑员",
  "description": "内容编辑员",
  "permissions": [1, 2, 3, 4]
}
```

**响应：**
```json
{
  "success": true,
  "message": "角色更新成功"
}
```

---

### DELETE /api/admin/roles/:id

删除角色

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "message": "角色删除成功"
}
```

---

### GET /api/admin/permissions

获取所有权限

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "permissions": [
      {
        "id": 1,
        "name": "user.manage",
        "display_name": "用户管理",
        "description": "管理用户",
        "module": "user"
      },
      {
        "id": 2,
        "name": "agent.manage",
        "display_name": "智能体管理",
        "description": "管理智能体",
        "module": "agent"
      }
    ]
  }
}
```

---

## 用户类型管理

### GET /api/admin/user-types

获取用户类型列表

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "user_types": [
      {
        "id": 1,
        "name": "normal",
        "display_name": "普通用户",
        "description": "基础用户",
        "level": 1,
        "benefits": {
          "discount": 1.0,
          "priority": 0
        }
      }
    ]
  }
}
```

---

### POST /api/admin/user-types

创建用户类型

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "name": "vip",
  "display_name": "VIP 会员",
  "description": "高级会员",
  "level": 3,
  "benefits": {
    "discount": 0.9,
    "priority": 1,
    "features": ["advanced_search", "export"]
  }
}
```

**响应：**
```json
{
  "success": true,
  "message": "用户类型创建成功",
  "data": {
    "id": 4
  }
}
```

---

### PUT /api/admin/user-types/:id

更新用户类型

**请求头：**
```
Authorization: Bearer <token>
Content-Type: application/json
```

**请求体：**
```json
{
  "display_name": "超级 VIP",
  "description": "最高级会员",
  "benefits": {
    "discount": 0.8,
    "priority": 2
  }
}
```

**响应：**
```json
{
  "success": true,
  "message": "用户类型更新成功"
}
```

---

## 统计数据

### GET /api/admin/stats/overview

获取总体统计

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "users": 1234,
    "agents": 56,
    "knowledge_bases": 23,
    "today_active": 89
  }
}
```

---

## 系统管理

### GET /api/admin/system/status

获取系统状态

**请求头：**
```
Authorization: Bearer <token>
```

**响应：**
```json
{
  "success": true,
  "data": {
    "database": {
      "size_mb": 125.5,
      "tables": 50
    },
    "system": {
      "memory_percent": 65.5,
      "disk_percent": 75.2
    }
  }
}
```

---

## 错误码

| 错误码 | 说明 | HTTP 状态码 |
|--------|------|-------------|
| `UNAUTHORIZED` | 未认证 | 401 |
| `FORBIDDEN` | 无权限 | 403 |
| `NOT_FOUND` | 资源不存在 | 404 |
| `INVALID_PARAMS` | 参数错误 | 400 |
| `INTERNAL_ERROR` | 服务器内部错误 | 500 |
| `TOO_MANY_REQUESTS` | 请求过于频繁 | 429 |
| `INVALID_ADMIN_PASSWORD` | 管理员密码错误 | 401 |
| `ADMIN_NOT_FOUND` | 管理员不存在 | 401 |

---

**文档版本：** v1.0.0
**最后更新：** 2024-02-17
