# 灵值生态园 API 文档

**版本**: v1.0  
**基础URL**: `https://meiyueart.com/api`  
**更新时间**: 2026-02-20

---

## 📋 目录

- [认证系统](#认证系统)
- [私有资源库](#私有资源库)
- [通知系统](#通知系统)
- [报表系统](#报表系统)
- [错误码](#错误码)

---

## 认证系统

### 基础URL: `/api/auth`

#### 1. 用户登录

**接口**: `POST /api/auth/login`

**请求参数**:
```json
{
  "username": "用户名",
  "password": "密码"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 10,
      "username": "admin",
      "totalLingzhi": 110,
      "avatarUrl": null,
      "realName": null
    },
    "isNewUser": false,
    "bonusMessage": null
  }
}
```

**测试账号**:
- 管理员: `admin` / `123`
- 用户: `马伟娟` / `123`

#### 2. 用户注册

**接口**: `POST /api/auth/register`

**请求参数**:
```json
{
  "username": "用户名",
  "password": "密码",
  "phone": "手机号",
  "verifyCode": "验证码"
}
```

#### 3. 发送验证码

**接口**: `POST /api/auth/send-code`

**请求参数**:
```json
{
  "phone": "手机号"
}
```

#### 4. 重置密码

**接口**: `POST /api/auth/reset-password`

**请求参数**:
```json
{
  "phone": "手机号",
  "newPassword": "新密码",
  "verifyCode": "验证码"
}
```

---

## 私有资源库

### 基础URL: `/api`

> **注意**: 所有接口都需要在请求头中携带 JWT Token
> `Authorization: Bearer <token>`

#### 1. 获取资源列表

**接口**: `GET /api/private-resources`

**查询参数**:
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20）
- `status`: 状态过滤（可选）

**响应示例**:
```json
{
  "success": true,
  "message": "获取资源列表成功",
  "data": [
    {
      "id": 1,
      "resourceName": "测试资源",
      "resourceType": "资金",
      "description": "这是一个测试资源",
      "estimatedValue": 100000,
      "contactName": "张三",
      "contactPhone": "13800138000",
      "canSolve": "市场推广",
      "authorizationStatus": "unauthorized",
      "verificationStatus": "pending",
      "visibility": "private",
      "riskLevel": "low",
      "createdAt": "2026-02-20 10:20:00",
      "updatedAt": "2026-02-20 10:20:00"
    }
  ]
}
```

#### 2. 创建资源

**接口**: `POST /api/private-resources`

**请求参数**:
```json
{
  "resourceName": "资源名称",
  "resourceType": "资源类型",
  "description": "资源描述",
  "estimatedValue": 100000,
  "contactName": "联系人姓名",
  "contactPhone": "联系电话",
  "canSolve": "可解决的问题"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "资源创建成功",
  "data": {
    "id": 1
  }
}
```

#### 3. 获取资源详情

**接口**: `GET /api/private-resources/<resource_id>`

#### 4. 更新资源

**接口**: `PUT /api/private-resources/<resource_id>`

#### 5. 删除资源

**接口**: `DELETE /api/private-resources/<resource_id>`

#### 6. 授权资源

**接口**: `POST /api/private-resources/<resource_id>/authorize`

**请求参数**:
```json
{
  "authorizationStatus": "authorized",
  "authorizationNote": "授权备注"
}
```

#### 7. 获取匹配列表

**接口**: `GET /api/resource-matches`

#### 8. 自动匹配资源

**接口**: `POST /api/resource-matches/auto-match`

#### 9. 响应匹配

**接口**: `POST /api/resource-matches/<match_id>/respond`

**请求参数**:
```json
{
  "response": "accept",
  "responseNote": "响应备注"
}
```

#### 10. 获取项目参与列表

**接口**: `GET /api/project-participations`

#### 11. 申请项目参与

**接口**: `POST /api/project-participations`

#### 12. 支付参与费用

**接口**: `POST /api/project-participations/<participation_id>/pay`

#### 13. 审批参与申请

**接口**: `POST /api/project-participations/<participation_id>/approve`

#### 14. 获取项目里程碑

**接口**: `GET /api/projects/<project_id>/milestones`

#### 15. 获取项目任务

**接口**: `GET /api/projects/<project_id>/tasks`

#### 16. 创建项目任务

**接口**: `POST /api/projects/<project_id>/tasks`

#### 17. 更新项目任务

**接口**: `PUT /api/projects/<project_id>/tasks/<task_id>`

#### 18. 获取分润列表

**接口**: `GET /api/profit-sharing`

#### 19. 创建分润记录

**接口**: `POST /api/profit-sharing`

#### 20. 分发收益

**接口**: `POST /api/profit-sharing/<sharing_id>/distribute`

---

## 通知系统

### 基础URL: `/api`

> **注意**: 所有接口都需要在请求头中携带 JWT Token
> `Authorization: Bearer <token>`

#### 1. 获取通知列表

**接口**: `GET /api/notifications`

**查询参数**:
- `page`: 页码（默认1）
- `limit`: 每页数量（默认20）
- `status`: 状态过滤（all, read, unread）

**响应示例**:
```json
{
  "success": true,
  "message": "获取通知成功",
  "data": {
    "notifications": [],
    "total": 0,
    "unreadCount": 0
  }
}
```

#### 2. 获取未读通知数量

**接口**: `GET /api/notifications/unread-count`

#### 3. 标记通知已读

**接口**: `POST /api/notifications/<notification_id>/read`

#### 4. 标记所有通知已读

**接口**: `POST /api/notifications/mark-all-read`

#### 5. 删除通知

**接口**: `DELETE /api/notifications/<notification_id>`

#### 6. 创建通知

**接口**: `POST /api/notifications`

**请求参数**:
```json
{
  "title": "通知标题",
  "content": "通知内容",
  "type": "info",
  "priority": "normal"
}
```

#### 7. 发送通知

**接口**: `POST /api/notifications/send`

**请求参数**:
```json
{
  "userId": 10,
  "templateId": 1,
  "data": {
    "projectName": "项目名称"
  }
}
```

---

## 报表系统

### 基础URL: `/api/reports`

> **注意**: 所有接口都需要在请求头中携带 JWT Token
> `Authorization: Bearer <token>`

#### 1. 获取仪表盘数据

**接口**: `GET /api/reports/dashboard`

**响应示例**:
```json
{
  "success": true,
  "message": "获取仪表盘数据成功",
  "data": {
    "resources": {
      "total": 1,
      "authorized": 0,
      "matchable": 0
    },
    "matches": {
      "total": 0,
      "approved": 0,
      "pending": 0
    },
    "participations": {
      "total": 0,
      "active": 0,
      "completed": 0,
      "totalInvested": 0
    },
    "profits": {
      "total": 0,
      "distributed": 0,
      "pending": 0
    },
    "recentActivities": []
  }
}
```

#### 2. 获取项目统计报表

**接口**: `GET /api/reports/projects/summary`

**查询参数**:
- `startDate`: 开始日期（可选）
- `endDate`: 结束日期（可选）

#### 3. 获取资源统计报表

**接口**: `GET /api/reports/resources/summary`

#### 4. 获取分润统计报表

**接口**: `GET /api/reports/profits/summary`

**查询参数**:
- `startDate`: 开始日期（可选）
- `endDate`: 结束日期（可选）

**响应示例**:
```json
{
  "success": true,
  "message": "获取分润统计报表成功",
  "data": {
    "baseStats": {
      "totalRecords": 0,
      "totalProfit": 0,
      "totalUserShare": 0,
      "avgSharePercentage": 0,
      "distributedCount": 0,
      "distributedAmount": 0,
      "pendingAmount": 0
    },
    "monthlyTrend": [],
    "projectProfits": [],
    "settlementDistribution": []
  }
}
```

#### 5. 导出报表

**接口**: `GET /api/reports/export`

**查询参数**:
- `reportType`: 报表类型（projects, resources, profits）
- `format`: 格式（json, csv）

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| `SUCCESS` | 成功 |
| `MISSING_TOKEN` | 缺少认证令牌 |
| `INVALID_TOKEN` | 令牌无效或已过期 |
| `INVALID_TOKEN_FORMAT` | 令牌格式错误 |
| `AUTH_NOT_INITIALIZED` | 认证系统未初始化 |
| `NOT_FOUND` | 资源不存在 |
| `PERMISSION_DENIED` | 权限不足 |
| `VALIDATION_ERROR` | 参数验证失败 |
| `DATABASE_ERROR` | 数据库错误 |

---

## 使用示例

### cURL 示例

```bash
# 1. 登录获取Token
curl -X POST https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123"}'

# 2. 获取资源列表（需要Token）
TOKEN="your_token_here"
curl https://meiyueart.com/api/private-resources \
  -H "Authorization: Bearer $TOKEN"

# 3. 创建资源
curl -X POST https://meiyueart.com/api/private-resources \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "resourceName": "测试资源",
    "resourceType": "资金",
    "description": "资源描述",
    "estimatedValue": 100000,
    "contactName": "张三",
    "contactPhone": "13800138000",
    "canSolve": "市场推广"
  }'

# 4. 获取仪表盘数据
curl https://meiyueart.com/api/reports/dashboard \
  -H "Authorization: Bearer $TOKEN"
```

### JavaScript (Fetch) 示例

```javascript
// 登录
async function login(username, password) {
  const response = await fetch('https://meiyueart.com/api/auth/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ username, password }),
  });
  const data = await response.json();
  return data.data.token;
}

// 获取资源列表
async function getResources(token) {
  const response = await fetch('https://meiyueart.com/api/private-resources', {
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });
  return await response.json();
}

// 创建资源
async function createResource(token, resourceData) {
  const response = await fetch('https://meiyueart.com/api/private-resources', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(resourceData),
  });
  return await response.json();
}
```

---

## 更新日志

### 2026-02-20
- ✅ 修复报表系统SQL查询错误（ambiguous column name）
- ✅ 修复JWT认证中间件集成问题
- ✅ 修复登录API路由前缀（/api/auth/login）
- ✅ 新增私有资源库系统API
- ✅ 新增通知系统API
- ✅ 新增报表系统API

---

## 联系支持

如有问题，请联系技术支持团队。

---

**文档版本**: v1.0  
**最后更新**: 2026-02-20
