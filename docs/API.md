# 灵值生态园 API 文档

## 命名规范

### 字段命名风格

- **后端API响应**：统一使用 `camelCase` 格式（JavaScript/TypeScript 约定）
- **数据库字段**：使用 `snake_case` 格式（数据库约定）
- **转换规则**：后端在返回响应前自动将数据库字段转换为 `camelCase`

### 示例转换

| snake_case (数据库) | camelCase (API) |
|---------------------|-----------------|
| `agent_id`          | `agentId`       |
| `conversation_id`   | `conversationId`|
| `total_lingzhi`     | `totalLingzhi`  |
| `avatar_url`        | `avatarUrl`     |
| `real_name`         | `realName`      |

## 通用响应格式

### 成功响应

```json
{
  "success": true,
  "message": "操作成功",
  "data": {
    // 具体数据
  }
}
```

### 错误响应

```json
{
  "success": false,
  "error": "错误描述信息"
}
```

## API 端点

### 1. 认证相关

#### POST /api/login

用户登录

**请求体**：
```json
{
  "username": "admin",
  "password": "123456"
}
```

**响应**：
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIs...",
    "user": {
      "id": 10,
      "username": "admin",
      "realName": "管理员",
      "avatarUrl": "https://...",
      "totalLingzhi": 100,
      "phone": "13800000000",
      "email": "admin@example.com"
    }
  }
}
```

### 2. 智能对话相关

#### POST /api/agent/chat

发送智能对话消息

**请求体**：
```json
{
  "message": "你好",
  "agentId": 1,
  "conversationId": "123",
  "enableMemory": false,
  "enableThinking": false
}
```

**请求参数**：
- `message` (string, 必填): 用户消息内容
- `agentId` (number, 可选): 智能体ID，默认为1
- `conversationId` (string, 可选): 对话ID，不传则创建新对话
- `enableMemory` (boolean, 可选): 是否启用记忆功能，默认false
- `enableThinking` (boolean, 可选): 是否启用深度思考模式，默认false

**响应**：
```json
{
  "success": true,
  "message": "对话成功",
  "data": {
    "reply": "你好！我是灵值生态园的智能向导...",
    "response": "你好！我是灵值生态园的智能向导...",
    "conversationId": "123",
    "agentId": 1,
    "message": "你好",
    "thinking": null
  }
}
```

**字段说明**：
- `reply` (string): AI回复内容（保留用于兼容）
- `response` (string): AI回复内容（推荐使用）
- `conversationId` (string): 对话ID
- `agentId` (number): 智能体ID
- `message` (string): 原始用户消息
- `thinking` (string|null): 深度思考过程（仅在启用深度思考时有值）

### 3. 签到系统

#### GET /api/checkin/status

获取签到状态

**响应**：
```json
{
  "success": true,
  "data": {
    "checkedIn": true,
    "todayLingzhi": 10,
    "consecutiveDays": 3,
    "totalLingzhi": 110,
    "rewards": [
      {
        "day": 1,
        "lingzhi": 10
      }
    ],
    "tomorrow": {
      "reward": 15,
      "baseReward": 10,
      "bonus": 5,
      "consecutiveDays": 4,
      "tip": "🔥 连续签到第 4 天，明天可获得 15 灵值！",
      "description": "连续签到奖励"
    },
    "checkinTip": "✨ 今日已签到，获得 10 灵值！",
    "milestoneTip": "连续签到 3 天，再签到 4 天可获得连续7天奖励！"
  }
}
```

#### POST /api/checkin

执行签到

**响应**：
```json
{
  "success": true,
  "message": "✨ 签到成功！获得10灵值，开启美好的一天~",
  "data": {
    "todayLingzhi": 10,
    "consecutiveDays": 1,
    "totalLingzhi": 110
  }
}
```

### 4. 用户信息

#### GET /api/user/info

获取当前用户信息

**响应**：
```json
{
  "success": true,
  "data": {
    "id": 1028,
    "username": "许韩玲",
    "realName": "许韩玲",
    "avatarUrl": null,
    "phone": "13800000030",
    "email": "xuhanling@example.com",
    "totalLingzhi": 110,
    "balance": 110,
    "createdAt": "2026-02-18T16:34:00.070411",
    "bio": null,
    "location": null,
    "interests": []
  }
}
```

### 5. 智能体管理

#### GET /api/admin/agents

获取智能体列表

**响应**：
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "文化助手",
      "description": "帮助您了解中华文化",
      "avatar": "🎭",
      "status": "active",
      "model": "doubao-seed-1-6-251015",
      "systemPrompt": "...",
      "createdAt": "2026-02-01T00:00:00"
    }
  ]
}
```

## 错误代码

| HTTP状态码 | 错误类型 | 说明 |
|-----------|---------|------|
| 200 | - | 成功 |
| 400 | Bad Request | 请求参数错误 |
| 401 | Unauthorized | 未授权（需要登录） |
| 403 | Forbidden | 无权限访问 |
| 404 | Not Found | 资源不存在 |
| 429 | Too Many Requests | 请求过于频繁 |
| 500 | Internal Server Error | 服务器内部错误 |
| 502 | Bad Gateway | 网关错误 |
| 503 | Service Unavailable | 服务暂时不可用 |
| 504 | Gateway Timeout | 网关超时 |

## 工具函数

### 后端字段名转换

后端提供了 `utils/response_utils.py` 模块，用于处理字段名转换：

```python
from utils.response_utils import (
    snake_to_camel,
    camel_to_snake,
    transform_dict_keys,
    success_response,
    error_response
)

# 转换单个字段名
camel = snake_to_camel('agent_id')  # -> 'agentId'

# 转换整个字典
data = transform_dict_keys(db_result, to_camel=True)

# 生成标准响应
response = success_response(data, "操作成功")
```

## 版本历史

### V1.0.0 (2026-02-18)
- 统一使用 camelCase 命名规范
- 添加字段名转换工具
- 完善API文档

## 注意事项

1. 所有日期时间字段使用 ISO 8601 格式
2. 所有金额和数值使用数字类型（不是字符串）
3. 布尔值使用 `true`/`false`（小写）
4. 空值使用 `null`
5. 分页参数从1开始（不是0）
6. 响应中的字段名统一使用 camelCase
