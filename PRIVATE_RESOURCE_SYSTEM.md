# 私有资源库与项目管理系统 - 完整文档

## 📋 系统概述

私有资源库与项目管理系统是灵值生态园的核心功能之一，实现了从资源录入、自动匹配、项目参与到收益分润的完整闭环流程。

### 核心功能

1. **私有资源库** - 用户可以录入个人拥有的私有资源（政府资源、企业资源、人脉资源等）
2. **授权管理** - 资源必须经过用户本人授权才能被项目调用
3. **智能匹配** - 系统根据资源能解决的问题自动匹配推荐项目
4. **项目参与** - 用户可以申请参与项目，支付参与费后查看项目详情
5. **工作流管理** - 项目分为里程碑和任务，实现精细化分工
6. **分润结算** - 项目完成后根据贡献占比进行收益分润

---

## 🗄️ 数据库设计

### 1. private_resources（私有资源表）

存储用户的私有资源信息。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| user_id | INTEGER | 拥有者用户ID |
| resource_name | TEXT | 资源名称 |
| resource_type | TEXT | 资源类型：government(政府), enterprise(企业), personal(人脉), other(其他) |
| department | TEXT | 部门 |
| contact_name | TEXT | 联系人姓名 |
| contact_phone | TEXT | 联系电话 |
| contact_email | TEXT | 联系邮箱 |
| position | TEXT | 职位（选填） |
| description | TEXT | 资源描述 |
| authorization_status | TEXT | 授权状态：unauthorized(未授权), authorized(已授权), pending(待授权) |
| authorization_note | TEXT | 授权说明 |
| valid_from | DATE | 有效期开始 |
| valid_until | DATE | 有效期结束 |
| can_solve | TEXT | 能解决的问题描述 |
| risk_level | TEXT | 风险等级：low, medium, high |
| verification_status | TEXT | 验证状态：pending(待验证), verified(已验证), rejected(已拒绝) |
| visibility | TEXT | 可见性：private(私有), matchable(可匹配) |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |
| deleted_at | TIMESTAMP | 软删除时间 |

### 2. resource_requirements（资源需求表）

记录项目需要的资源。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 关联项目 |
| requirement_name | TEXT | 需求名称 |
| requirement_type | TEXT | 需求类型 |
| description | TEXT | 需求描述 |
| priority | TEXT | 优先级：low, medium, high, urgent |
| status | TEXT | 状态：open(开放中), filled(已满足), closed(已关闭) |
| quantity_needed | INTEGER | 需要数量 |
| quantity_matched | INTEGER | 已匹配数量 |
| urgency_level | TEXT | 紧急程度：low, normal, high |
| budget_range | TEXT | 预算范围 |

### 3. resource_matches（资源匹配表）

记录系统自动匹配的结果。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| resource_id | INTEGER | 私有资源ID |
| project_id | INTEGER | 项目ID |
| requirement_id | INTEGER | 需求ID（可选） |
| match_score | REAL | 匹配分数 (0-100) |
| match_reason | TEXT | 匹配原因 |
| status | TEXT | 状态：pending(待确认), approved(已接受), rejected(已拒绝) |
| initiated_by | TEXT | 发起方：system(系统), user(用户), admin(管理员) |
| resource_owner_confirmed | BOOLEAN | 资源拥有者确认 |
| project_manager_confirmed | BOOLEAN | 项目经理确认 |

### 4. project_participations（项目参与表）

记录用户参与项目及付费状态。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 项目ID |
| user_id | INTEGER | 用户ID |
| participation_type | TEXT | 参与类型：resource_provider(资源提供者), executor(执行者), investor(投资方) |
| role_name | TEXT | 角色名称 |
| status | TEXT | 状态：applied(已申请), approved(已批准), active(进行中), completed(已完成), terminated(已终止) |
| contribution_description | TEXT | 贡献描述 |
| contribution_share | REAL | 贡献占比 (0-100) |
| resource_ids | TEXT | 关联的资源ID列表（JSON数组） |
| payment_status | TEXT | 支付状态：unpaid(未支付), paid(已支付), refunded(已退款) |
| payment_amount | REAL | 支付金额 |
| payment_method | TEXT | 支付方式 |
| payment_time | TIMESTAMP | 支付时间 |
| payment_transaction_id | TEXT | 支付交易ID |
| approved_by | INTEGER | 审批人ID |
| approved_at | TIMESTAMP | 审批时间 |

### 5. profit_sharing（分润记录表）

记录项目收益分润。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 项目ID |
| user_id | INTEGER | 用户ID |
| participation_id | INTEGER | 参与记录ID |
| total_profit | REAL | 项目总收益 |
| user_share | REAL | 用户应得分润 |
| share_percentage | REAL | 分润比例 (0-100) |
| sharing_rule | TEXT | 分润规则描述 |
| status | TEXT | 状态：pending(待结算), calculated(已计算), distributed(已发放) |
| settlement_period | TEXT | 结算周期：monthly(月结), quarterly(季结), upon_delivery(交付后) |
| distribution_method | TEXT | 发放方式 |
| distribution_time | TIMESTAMP | 发放时间 |
| distribution_transaction_id | TEXT | 发放交易ID |

### 6. project_milestones（项目里程碑表）

项目关键节点。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 项目ID |
| milestone_name | TEXT | 里程碑名称 |
| description | TEXT | 描述 |
| planned_date | DATE | 计划日期 |
| actual_date | DATE | 实际完成日期 |
| status | TEXT | 状态：pending, in_progress, completed, delayed |
| progress_percentage | REAL | 进度百分比 |
| deliverables | TEXT | 交付物描述（JSON） |
| responsible_person_id | INTEGER | 负责人ID |
| budget_allocated | REAL | 分配预算 |
| actual_cost | REAL | 实际成本 |

### 7. project_tasks（项目任务表）

项目具体任务分工。

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INTEGER | 主键 |
| project_id | INTEGER | 项目ID |
| milestone_id | INTEGER | 里程碑ID（可选） |
| task_name | TEXT | 任务名称 |
| description | TEXT | 任务描述 |
| assignee_id | INTEGER | 负责人ID |
| status | TEXT | 状态：pending, in_progress, completed, blocked |
| priority | TEXT | 优先级：low, medium, high, urgent |
| estimated_hours | REAL | 预估工时 |
| actual_hours | REAL | 实际工时 |
| start_date | DATE | 开始日期 |
| due_date | DATE | 截止日期 |

### 8. project_workflow_logs（项目工作流记录表）

记录项目操作日志。

### 9. resource_access_logs（资源访问授权记录表）

记录资源访问请求和授权历史。

### 10. project_transactions（项目资金流水表）

记录所有资金交易（参与费、投资、分润等）。

---

## 🔌 API 接口文档

### 1. 私有资源管理

#### 创建资源

```
POST /api/private-resources
Authorization: Bearer {token}

{
  "resourceName": "教育部政策咨询资源",
  "resourceType": "government",
  "contactName": "李部长",
  "contactPhone": "13800138000",
  "contactEmail": "li@example.com",
  "department": "教育部",
  "position": "副部长",
  "description": "可提供教育部相关政策咨询和指导",
  "authorizationStatus": "authorized",
  "visibility": "matchable",
  "canSolve": "教育政策咨询、项目申报指导",
  "validFrom": "2024-01-01",
  "validUntil": "2025-12-31"
}
```

#### 获取资源列表

```
GET /api/private-resources?status=authorized&resource_type=government
Authorization: Bearer {token}
```

#### 获取资源详情

```
GET /api/private-resources/{resource_id}
Authorization: Bearer {token}
```

#### 更新资源

```
PUT /api/private-resources/{resource_id}
Authorization: Bearer {token}

{
  "resourceName": "更新的资源名称",
  "authorizationStatus": "authorized"
}
```

#### 删除资源

```
DELETE /api/private-resources/{resource_id}
Authorization: Bearer {token}
```

### 2. 授权管理

#### 授权资源给项目

```
POST /api/private-resources/{resource_id}/authorize
Authorization: Bearer {token}

{
  "projectId": 1,
  "accessDuration": "3months",
  "notes": "授权用于项目X"
}
```

### 3. 资源匹配

#### 获取匹配记录

```
GET /api/resource-matches
Authorization: Bearer {token}
```

#### 自动匹配资源

```
POST /api/resource-matches/auto-match
Authorization: Bearer {token}
```

#### 响应匹配

```
POST /api/resource-matches/{match_id}/respond
Authorization: Bearer {token}

{
  "action": "accept"  // or "reject"
}
```

### 4. 项目参与

#### 获取参与记录

```
GET /api/project-participations?status=active
Authorization: Bearer {token}
```

#### 申请参与项目

```
POST /api/project-participations
Authorization: Bearer {token}

{
  "projectId": 1,
  "participationType": "resource_provider",
  "roleName": "资源提供者",
  "contributionDescription": "提供教育政策咨询资源",
  "resourceIds": [1, 2, 3]
}
```

#### 支付参与费

```
POST /api/project-participations/{participation_id}/pay
Authorization: Bearer {token}

{
  "paymentMethod": "alipay"
}
```

#### 审批参与申请（管理员）

```
POST /api/project-participations/{participation_id}/approve
Authorization: Bearer {token}

{
  "action": "approve"  // or "reject"
}
```

### 5. 项目工作流

#### 获取项目里程碑

```
GET /api/projects/{project_id}/milestones
Authorization: Bearer {token}
```

#### 获取项目任务

```
GET /api/projects/{project_id}/tasks
Authorization: Bearer {token}
```

#### 创建项目任务

```
POST /api/projects/{project_id}/tasks
Authorization: Bearer {token}

{
  "milestoneId": 1,
  "taskName": "需求分析",
  "description": "收集并分析项目需求",
  "assigneeId": 10,
  "priority": "high",
  "estimatedHours": 40,
  "dueDate": "2024-03-31"
}
```

#### 更新项目任务

```
PUT /api/projects/{project_id}/tasks/{task_id}
Authorization: Bearer {token}

{
  "status": "completed",
  "actualHours": 35
}
```

### 6. 分润管理

#### 获取分润记录

```
GET /api/profit-sharing
Authorization: Bearer {token}
```

#### 创建分润记录（管理员）

```
POST /api/profit-sharing
Authorization: Bearer {token}

{
  "projectId": 1,
  "userId": 10,
  "participationId": 1,
  "totalProfit": 100000,
  "sharePercentage": 20,
  "settlementPeriod": "upon_delivery",
  "sharingRule": "按贡献占比分润"
}
```

#### 发放分润（管理员）

```
POST /api/profit-sharing/{sharing_id}/distribute
Authorization: Bearer {token}

{
  "distributionMethod": "bank_transfer"
}
```

### 7. 统计和推荐

#### 获取用户资源统计

```
GET /api/dashboard/resource-stats
Authorization: Bearer {token}

响应:
{
  "success": true,
  "message": "获取统计成功",
  "data": {
    "resources": {
      "total": 5,
      "authorized": 3,
      "verified": 2,
      "matchable": 4
    },
    "matches": {
      "total": 10,
      "approved": 5,
      "pending": 3
    },
    "participations": {
      "total": 3,
      "active": 2,
      "completed": 1,
      "totalInvested": 5000
    },
    "profits": {
      "total": 15000,
      "distributed": 8000,
      "pending": 7000
    }
  }
}
```

#### 获取推荐项目

```
GET /api/projects/recommended
Authorization: Bearer {token}
```

---

## 🔄 完整工作流程

### 1. 资源录入流程

```
用户登录 → 录入私有资源 → 设置授权状态 → 设置可见性 → 保存
```

**关键点：**
- 资源必须设置 `authorizationStatus = authorized` 才能参与匹配
- 资源必须设置 `visibility = matchable` 才能被系统匹配
- `can_solve` 字段用于描述资源能解决的问题，是匹配的关键

### 2. 智能匹配流程

```
用户点击"自动匹配" → 系统扫描用户已授权资源 → 匹配项目需求 → 计算匹配分数 → 生成匹配记录 → 用户确认
```

**匹配算法（简化版）：**
- 基础分数：60分
- 资源已验证：+20分
- 低风险资源：+10分
- 项目招募中：+10分

### 3. 项目参与流程

```
用户查看匹配项目 → 申请参与 → 支付参与费（如需要） → 等待审批 → 查看项目详情 → 参与项目
```

**状态流转：**
```
applied → approved → active → completed
           ↓
        rejected
```

### 4. 项目执行流程

```
项目启动 → 创建里程碑 → 创建任务 → 分配任务 → 执行任务 → 完成任务 → 完成里程碑 → 项目交付
```

### 5. 分润结算流程

```
项目交付 → 计算收益 → 创建分润记录 → 审核分润 → 发放分润 → 完成
```

**分润规则：**
- 分润比例根据 `contributionShare` 计算
- 结算周期按 `settlementPeriod` 执行
- 发放方式按 `distributionMethod` 执行

---

## 📊 数据库视图

### project_stats_view（项目统计视图）

```sql
SELECT 
    p.id as project_id,
    p.project_name,
    p.status,
    COUNT(DISTINCT pp.id) as participant_count,
    COUNT(DISTINCT pt.id) as task_count,
    COUNT(DISTINCT pm.id) as milestone_count,
    COALESCE(SUM(pt.actual_hours), 0) as total_hours,
    COALESCE(SUM(CASE WHEN pt.status = 'completed' THEN 1 ELSE 0 END), 0) as completed_tasks
FROM company_projects p
LEFT JOIN project_participations pp ON p.id = pp.project_id
LEFT JOIN project_tasks pt ON p.id = pt.project_id
LEFT JOIN project_milestones pm ON p.id = pm.project_id
GROUP BY p.id;
```

### user_resource_stats_view（用户资源统计视图）

```sql
SELECT 
    u.id as user_id,
    u.username,
    COUNT(DISTINCT pr.id) as total_resources,
    COUNT(DISTINCT CASE WHEN pr.authorization_status = 'authorized' THEN pr.id END) as authorized_resources,
    COUNT(DISTINCT rm.id) as total_matches,
    COUNT(DISTINCT CASE WHEN rm.status = 'approved' THEN rm.id END) as approved_matches,
    COALESCE(SUM(ps.user_share), 0) as total_profits
FROM users u
LEFT JOIN private_resources pr ON u.id = pr.user_id
LEFT JOIN resource_matches rm ON pr.id = rm.resource_id
LEFT JOIN project_participations pp ON u.id = pp.user_id
LEFT JOIN profit_sharing ps ON pp.id = ps.participation_id
GROUP BY u.id;
```

---

## 🔒 安全机制

### 1. 资源隐私保护

- 所有资源默认为 `private`（私有），只有用户本人可查看
- 资源设置为 `matchable` 后，系统才能进行匹配
- 资源必须 `authorizationStatus = authorized` 才能被项目调用
- 所有资源访问都会记录到 `resource_access_logs`

### 2. 授权管理

- 资源授权必须由用户本人发起
- 授权记录包含授权时间、过期时间、授权人信息
- 授权可设置有效期和授权时长

### 3. 权限控制

- 所有API都需要Token认证
- 资源只能由拥有者本人操作
- 项目参与需要审批
- 分润发放需要审核

---

## 📈 扩展方向

### 1. 智能匹配优化

- 引入机器学习算法提升匹配准确度
- 支持多维度匹配（地理位置、行业、技能等）
- 实时推荐系统

### 2. 区块链存证

- 资源授权记录上链
- 项目交付记录上链
- 分润记录上链

### 3. 社交功能

- 用户评价系统
- 资源评分系统
- 项目评论功能

### 4. 智能合约

- 自动化分润
- 智能锁定期
- 自动审批

---

## 📞 技术支持

如遇到问题，请联系技术支持团队。

---

## 📜 更新日志

### v1.0.0 (2024-02-20)

- ✅ 完成数据库设计（10张表）
- ✅ 实现私有资源管理API
- ✅ 实现资源智能匹配
- ✅ 实现项目参与流程
- ✅ 实现项目工作流（里程碑、任务）
- ✅ 实现分润管理
- ✅ 部署到生产环境
- ✅ 完成功能测试

---

## 🎯 下一步计划

1. 前端页面开发
2. 优化匹配算法
3. 添加通知系统
4. 实现报表功能
5. 添加数据可视化

---

**文档版本**: v1.0.0  
**最后更新**: 2024-02-20  
**系统版本**: 20260220-1632
