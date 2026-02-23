# 灵值生态园 API 文档

## 版本信息
- **版本**: v11.0.0
- **基础URL**: `https://meiyueart.com/api`
- **文档更新时间**: 2026-02-10

## 认证方式

所有需要认证的 API 都需要在请求头中包含 JWT Token：

```
Authorization: Bearer <your-jwt-token>
```

## 错误响应格式

```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

---

## 一、用户认证 API

### 1.1 用户注册

**端点**: `POST /auth/register`

**请求体**:
```json
{
  "username": "用户名",
  "password": "密码",
  "email": "邮箱（可选）",
  "phone": "手机号（可选）",
  "real_name": "真实姓名（可选）"
}
```

**响应**:
```json
{
  "success": true,
  "message": "注册成功",
  "data": {
    "user_id": 1,
    "username": "用户名",
    "token": "JWT Token"
  }
}
```

### 1.2 用户登录

**端点**: `POST /auth/login`

**请求体**:
```json
{
  "username": "用户名",
  "password": "密码"
}
```

**响应**:
```json
{
  "success": true,
  "message": "登录成功",
  "data": {
    "user_id": 1,
    "username": "用户名",
    "token": "JWT Token",
    "avatar_url": "头像URL"
  }
}
```

### 1.3 获取当前用户信息

**端点**: `GET /user/info`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "username": "用户名",
    "email": "邮箱",
    "phone": "手机号",
    "total_lingzhi": 100,
    "status": "active",
    "avatar_url": "头像URL",
    "real_name": "真实姓名",
    "is_verified": true,
    "created_at": "2026-01-01T00:00:00Z"
  }
}
```

---

## 二、用户管理 API

### 2.1 签到

**端点**: `POST /checkin`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "message": "签到成功，获得10灵值",
  "data": {
    "lingzhi_earned": 10,
    "total_lingzhi": 110,
    "consecutive_days": 5
  }
}
```

### 2.2 获取签到状态

**端点**: `GET /checkin/status`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": {
    "today_checked": true,
    "consecutive_days": 5,
    "total_checkins": 30,
    "last_checkin_date": "2026-02-10"
  }
}
```

---

## 三、圣地管理 API

### 3.1 获取圣地列表

**端点**: `GET /sacred-sites`

**认证**: 需要

**查询参数**:
- `status` (可选): 圣地状态（planning/building/operating）

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "灵山圣地",
      "description": "圣地描述",
      "cultural_theme": "唐风精神",
      "location": "中国江苏",
      "latitude": 31.2304,
      "longitude": 121.4737,
      "status": "operating",
      "image_url": "图片URL",
      "total_investment": 1000000,
      "expected_returns": 1500000,
      "current_value": 1200000,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

### 3.2 创建圣地

**端点**: `POST /sacred-sites`

**认证**: 需要

**请求体**:
```json
{
  "name": "圣地名称",
  "description": "圣地描述",
  "cultural_theme": "文化主题",
  "location": "位置",
  "latitude": 31.2304,
  "longitude": 121.4737,
  "status": "planning",
  "image_url": "图片URL",
  "total_investment": 1000000,
  "expected_returns": 1500000
}
```

**响应**:
```json
{
  "success": true,
  "message": "圣地创建成功",
  "data": {
    "id": 1
  }
}
```

### 3.3 获取圣地详情

**端点**: `GET /sacred-sites/<id>`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "圣地名称",
    "description": "圣地描述",
    "cultural_theme": "文化主题",
    "location": "位置",
    "latitude": 31.2304,
    "longitude": 121.4737,
    "status": "operating",
    "image_url": "图片URL",
    "total_investment": 1000000,
    "expected_returns": 1500000,
    "current_value": 1200000,
    "creator_id": 1,
    "created_at": "2026-01-01T00:00:00Z",
    "updated_at": "2026-02-01T00:00:00Z"
  }
}
```

### 3.4 更新圣地

**端点**: `PUT /sacred-sites/<id>`

**认证**: 需要

**请求体**:
```json
{
  "name": "更新后的名称",
  "description": "更新后的描述",
  "status": "operating",
  "current_value": 1300000
}
```

**响应**:
```json
{
  "success": true,
  "message": "圣地更新成功"
}
```

### 3.5 删除圣地

**端点**: `DELETE /sacred-sites/<id>`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "message": "圣地删除成功"
}
```

### 3.6 获取圣地资源

**端点**: `GET /sacred-sites/<id>/resources`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "site_id": 1,
      "resource_type": "artifact",
      "name": "文物名称",
      "description": "文物描述",
      "value": 50000,
      "status": "available",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

---

## 四、文化项目管理 API

### 4.1 获取项目列表

**端点**: `GET /cultural-projects`

**认证**: 需要

**查询参数**:
- `status` (可选): 项目状态（planning/ongoing/completed）
- `site_id` (可选): 圣地ID

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "古建筑修缮项目",
      "description": "项目描述",
      "site_id": 1,
      "project_type": "renovation",
      "status": "ongoing",
      "progress": 60,
      "budget": 500000,
      "actual_cost": 300000,
      "start_date": "2026-01-01",
      "end_date": "2026-06-01",
      "manager_id": 1,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

### 4.2 创建项目

**端点**: `POST /cultural-projects`

**认证**: 需要

**请求体**:
```json
{
  "name": "项目名称",
  "description": "项目描述",
  "site_id": 1,
  "project_type": "renovation",
  "budget": 500000,
  "start_date": "2026-01-01",
  "end_date": "2026-06-01",
  "manager_id": 1
}
```

### 4.3 获取项目详情

**端点**: `GET /cultural-projects/<id>`

**认证**: 需要

### 4.4 更新项目

**端点**: `PUT /cultural-projects/<id>`

**认证**: 需要

### 4.5 添加项目参与者

**端点**: `POST /cultural-projects/<id>/participants`

**认证**: 需要

**请求体**:
```json
{
  "user_id": 2,
  "role": "architect",
  "contribution": "负责建筑设计",
  "reward": 10000
}
```

---

## 五、用户修行记录 API

### 5.1 获取学习记录

**端点**: `GET /user/learning-records`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "knowledge_id": 1,
      "knowledge_title": "唐风文化",
      "learning_type": "reading",
      "duration": 60,
      "notes": "学习笔记",
      "reward": 10,
      "created_at": "2026-02-10T00:00:00Z"
    }
  ]
}
```

### 5.2 创建学习记录

**端点**: `POST /user/learning-records`

**认证**: 需要

**请求体**:
```json
{
  "knowledge_id": 1,
  "knowledge_title": "唐风文化",
  "learning_type": "reading",
  "duration": 60,
  "notes": "学习笔记"
}
```

### 5.3 获取修行阶段

**端点**: `GET /user/journey-stages`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "stage_name": "初学者",
      "stage_level": 1,
      "description": "初学者阶段",
      "requirements": "完成10次学习",
      "progress": 80,
      "is_completed": false,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

### 5.4 更新修行阶段

**端点**: `POST /user/journey-stages`

**认证**: 需要

**请求体**:
```json
{
  "stage_name": "初学者",
  "stage_level": 1,
  "description": "初学者阶段",
  "requirements": "完成10次学习",
  "progress": 100,
  "is_completed": true
}
```

---

## 六、用户贡献 API

### 6.1 获取贡献记录

**端点**: `GET /user/contributions`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "project_id": 1,
      "contribution_type": "design",
      "description": "贡献描述",
      "status": "approved",
      "review_comment": "审核通过",
      "reward": 500,
      "created_at": "2026-02-10T00:00:00Z"
    }
  ]
}
```

### 6.2 提交贡献

**端点**: `POST /user/contributions`

**认证**: 需要

**请求体**:
```json
{
  "project_id": 1,
  "contribution_type": "design",
  "description": "贡献描述",
  "attachments": {}
}
```

### 6.3 审核贡献

**端点**: `PUT /user/contributions/<id>/review`

**认证**: 需要

**请求体**:
```json
{
  "status": "approved",
  "review_comment": "审核通过",
  "reward": 500
}
```

---

## 七、通证管理 API

### 7.1 获取通证类型

**端点**: `GET /tokens`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "灵值通证",
      "symbol": "LING",
      "description": "灵值生态园权益通证",
      "token_type": "equity",
      "total_supply": 1000000,
      "circulated_supply": 500000,
      "unit_price": 1.0,
      "is_transferrable": true
    }
  ]
}
```

### 7.2 获取用户通证余额

**端点**: `GET /user/tokens`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "token_type_id": 1,
      "token_name": "灵值通证",
      "token_symbol": "LING",
      "balance": 1000,
      "frozen_balance": 100
    }
  ]
}
```

### 7.3 转让通证

**端点**: `POST /tokens/transfer`

**认证**: 需要

**请求体**:
```json
{
  "to_user_id": 2,
  "token_type_id": 1,
  "amount": 100,
  "description": "转账"
}
```

### 7.4 获取交易记录

**端点**: `GET /tokens/transactions`

**认证**: 需要

**查询参数**:
- `page` (可选): 页码，默认1
- `limit` (可选): 每页数量，默认20

**响应**:
```json
{
  "success": true,
  "data": {
    "transactions": [
      {
        "id": 1,
        "from_user_id": 1,
        "to_user_id": 2,
        "token_type_id": 1,
        "amount": 100,
        "transaction_type": "transfer",
        "description": "转账",
        "created_at": "2026-02-10T00:00:00Z"
      }
    ],
    "total": 100,
    "page": 1,
    "limit": 20,
    "pages": 5
  }
}
```

---

## 八、SBT 管理 API

### 8.1 获取 SBT 类型

**端点**: `GET /sbts`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "文化使者",
      "description": "文化贡献者徽章",
      "category": "badge",
      "rarity": "rare",
      "image_url": "图片URL"
    }
  ]
}
```

### 8.2 获取用户 SBT

**端点**: `GET /user/sbts`

**认证**: 需要

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "sbt_type_id": 1,
      "sbt_name": "文化使者",
      "category": "badge",
      "rarity": "rare",
      "metadata": {},
      "issued_at": "2026-02-10T00:00:00Z"
    }
  ]
}
```

### 8.3 颁发 SBT

**端点**: `POST /sbts/issue`

**认证**: 需要

**请求体**:
```json
{
  "user_id": 2,
  "sbt_type_id": 1,
  "issued_reason": "文化贡献",
  "metadata": {}
}
```

---

## 九、社群活动 API

### 9.1 获取活动列表

**端点**: `GET /activities`

**认证**: 需要

**查询参数**:
- `status` (可选): 活动状态（upcoming/ongoing/completed/cancelled）
- `activity_type` (可选): 活动类型（offline/online/hybrid）

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "文化交流会",
      "description": "活动描述",
      "activity_type": "offline",
      "location": "地点",
      "start_time": "2026-03-01T10:00:00Z",
      "end_time": "2026-03-01T12:00:00Z",
      "max_participants": 100,
      "current_participants": 50,
      "status": "upcoming",
      "organizer_id": 1,
      "created_at": "2026-02-10T00:00:00Z"
    }
  ]
}
```

### 9.2 创建活动

**端点**: `POST /activities`

**认证**: 需要

**请求体**:
```json
{
  "title": "活动标题",
  "description": "活动描述",
  "activity_type": "offline",
  "location": "地点",
  "start_time": "2026-03-01T10:00:00Z",
  "end_time": "2026-03-01T12:00:00Z",
  "max_participants": 100
}
```

### 9.3 报名活动

**端点**: `POST /activities/<id>/register`

**认证**: 需要

### 9.4 签到活动

**端点**: `PUT /activities/<id>/check-in`

**认证**: 需要

---

## 十、公司动态 API

### 10.1 获取新闻列表

**端点**: `GET /company-news`

**认证**: 不需要

**查询参数**:
- `page` (可选): 页码，默认1
- `per_page` (可选): 每页数量，默认10
- `category` (可选): 新闻类别
- `status` (可选): 状态

**响应**:
```json
{
  "success": true,
  "data": {
    "news": [
      {
        "id": 1,
        "title": "新闻标题",
        "content": "新闻内容",
        "category": "update",
        "image_url": "图片URL",
        "author_id": 1,
        "published_at": "2026-02-10T00:00:00Z",
        "created_at": "2026-02-10T00:00:00Z"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 50,
      "pages": 5
    }
  }
}
```

### 10.2 创建新闻

**端点**: `POST /company-news`

**认证**: 需要

**请求体**:
```json
{
  "title": "新闻标题",
  "content": "新闻内容",
  "category": "update",
  "image_url": "图片URL",
  "is_published": true
}
```

### 10.3 获取新闻详情

**端点**: `GET /company-news/<id>`

**认证**: 不需要

### 10.4 更新新闻

**端点**: `PUT /company-news/<id>`

**认证**: 需要

### 10.5 删除新闻

**端点**: `DELETE /company-news/<id>`

**认证**: 需要

---

## 十一、智能体对话 API

### 11.1 发送消息

**端点**: `POST /agent/chat`

**认证**: 需要

**请求体**:
```json
{
  "message": "用户消息",
  "conversation_id": "会话ID（可选）"
}
```

**响应**:
```json
{
  "success": true,
  "data": {
    "conversation_id": "会话ID",
    "message": "智能体回复",
    "thinking": "思考过程（如有）"
  }
}
```

### 11.2 获取对话历史

**端点**: `GET /agent/conversations/<conversation_id>`

**认证**: 需要

---

## 附录

### A. 错误代码

| 错误代码 | 说明 |
|---------|------|
| UNAUTHORIZED | 未授权，请先登录 |
| INVALID_TOKEN | Token 无效 |
| MISSING_FIELD | 缺少必填字段 |
| SITE_NOT_FOUND | 圣地不存在 |
| PROJECT_NOT_FOUND | 项目不存在 |
| INSUFFICIENT_BALANCE | 余额不足 |
| ACTIVITY_FULL | 活动名额已满 |

### B. 数据字典

#### 圣地状态 (status)
- `planning`: 规划中
- `building`: 建设中
- `operating`: 运营中

#### 项目类型 (project_type)
- `renovation`: 修缮
- `reconstruction`: 重建
- `creation`: 创作

#### 项目状态 (status)
- `planning`: 规划中
- `ongoing`: 进行中
- `completed`: 已完成

#### 学习类型 (learning_type)
- `reading`: 阅读
- `practice`: 实践
- `meditation`: 冥想

#### 贡献类型 (contribution_type)
- `cultural_decoding`: 文化解码
- `design`: 设计
- `technical`: 技术
- `financial`: 资金
- `content`: 内容

#### 通证类型 (token_type)
- `equity`: 权益通证
- `governance`: 治理通证
- `reward`: 奖励通证

#### 交易类型 (transaction_type)
- `issue`: 发行
- `transfer`: 转让
- `reward`: 奖励
- `stake`: 质押

#### SBT 类别 (category)
- `achievement`: 成就
- `badge`: 勋章
- `identity`: 身份
- `certification`: 认证

#### SBT 稀有度 (rarity)
- `common`: 普通
- `rare`: 稀有
- `epic`: 史诗
- `legendary`: 传说

#### 活动类型 (activity_type)
- `offline`: 线下
- `online`: 线上
- `hybrid`: 混合

#### 活动状态 (status)
- `upcoming`: 即将开始
- `ongoing`: 进行中
- `completed`: 已结束
- `cancelled`: 已取消

#### 新闻类别 (category)
- `update`: 动态
- `event`: 事件
- `recruitment`: 招聘
- `announcement`: 公告

---

**文档版本**: v11.0.0
**最后更新**: 2026-02-10
