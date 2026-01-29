# 权限管理系统 v2.0 - CEO角色和访客管理

**版本**：v2.0
**发布日期**：2026年1月23日
**重大更新**：添加CEO角色、黄爱莉账号、访客管理系统

---

## 🆕 v2.0 新功能

### 1. CEO角色
- **权限级别**：0（高于超级管理员）
- **权限范围**：所有权限
- **初始账号**：
  - 邮箱：huangaili@meiyue.com
  - 密码：Huang@2026
  - 姓名：黄爱莉
  - 职位：CEO

### 2. 访客管理系统
- **访客注册**：支持访客信息完整登记
- **团队管理**：支持团队成员管理
- **团队长审批**：自动检查成员数量，管理员审批
- **访客列表**：查看所有访客信息

### 3. 团队长机制
- **申请条件**：拥有3个以上角色的成员
- **意愿确认**：访客必须愿意成为团队长
- **人工审批**：管理员手动审批

---

## 📋 访客登记信息

### 必填字段
- 姓名
- 微信号
- 联系方式（电话）

### 可选字段
- 推荐人
- 备注
- 收货地址

### 团队长信息
- 是否为团队长
- 是否愿意成为团队长

---

## 🚀 快速开始

### 第一步：初始化数据库

由于v2.0版本添加了访客表和CEO角色，需要使用新的初始化脚本：

```bash
# 如果有旧数据库，先备份
cp auth.db auth.db.backup 2>/dev/null || true

# 删除旧数据库
rm -f auth.db

# 使用新脚本初始化
python init_data_v2.py
```

初始化成功后，您会看到以下账号信息：

```
初始账号信息：
==================================================
CEO账号：
  邮箱：huangaili@meiyue.com
  密码：Huang@2026
  双因素认证密钥：xxxxxxxx

超级管理员账号：
  邮箱：xufeng@meiyue.com
  密码：Xu@2026
  双因素认证密钥：xxxxxxxx
==================================================
```

### 第二步：启动后端服务

```bash
python api.py
```

后端服务将在 http://localhost:8000 启动

### 第三步：访问系统

#### 管理界面
打开 `index.html` 文件

#### 访客注册页面
打开 `visitor_register.html` 文件

#### API文档
访问 http://localhost:8000/docs

---

## 👤 默认账号

| 账号 | 邮箱 | 密码 | 角色 | 级别 |
|-----|------|------|------|------|
| **黄爱莉** | huangaili@meiyue.com | Huang@2026 | CEO | 0 |
| 许锋 | xufeng@meiyue.com | Xu@2026 | 超级管理员 | 1 |
| CTO（待定） | cto@meiyue.com | Temp@2026 | CTO管理员 | 2 |
| CMO（待定） | cmo@meiyue.com | Temp@2026 | CMO管理员 | 2 |
| COO（待定） | coo@meiyue.com | Temp@2026 | COO管理员 | 2 |
| CFO（待定） | cfo@meiyue.com | Temp@2026 | CFO管理员 | 2 |

⚠️ **首次登录后请立即修改密码！**

---

## 💼 使用场景

### 场景1：访客注册

1. 以管理员身份登录系统
2. 点击"访客管理"标签
3. 点击"访客注册"按钮
4. 填写访客信息：
   - 姓名：张三
   - 微信号：zhangsan_wx
   - 电话：13800138000
   - 推荐人：李四（可选）
   - 收货地址：北京市朝阳区xxx（可选）
   - 备注：新访客（可选）
   - 是否愿意成为团队长：勾选
5. 点击"提交注册"

### 场景2：管理团队成员

访客A推荐了访客B、C、D三人加入系统：

1. 在访客管理列表中找到访客A（团队长）
2. 使用API添加团队成员：

```bash
curl -X POST "http://localhost:8000/api/team-members" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "team_leader_id": 1,
    "member_id": 2,
    "role": "销售",
    "notes": "推荐加入"
  }'
```

3. 为访客B、C、D分别添加成员关系

### 场景3：审批团队长

当访客A拥有3个以上成员且愿意成为团队长时：

1. 在访客管理列表中找到访客A
2. 看到"批准团队长"按钮（仅当满足条件时显示）
3. 点击"批准团队长"按钮
4. 系统将访客A设为团队长

### 场景4：黄爱莉CEO登录

1. 打开 `index.html`
2. 输入邮箱：huangaili@meiyue.com
3. 输入密码：Huang@2026
4. 点击"登录"
5. 登录成功后可以管理所有系统功能

---

## 📊 API接口

### 访客管理

#### 创建访客
```bash
POST /api/visitors
Content-Type: application/json
Authorization: Bearer YOUR_TOKEN

{
  "name": "张三",
  "wechat": "zhangsan_wx",
  "phone": "13800138000",
  "referrer": "李四",
  "notes": "新访客",
  "shipping_address": "北京市朝阳区xxx",
  "is_team_leader": false,
  "willing_to_be_leader": true
}
```

#### 获取访客列表
```bash
GET /api/visitors
Authorization: Bearer YOUR_TOKEN

# 按状态筛选
GET /api/visitors?status=active

# 按团队长筛选
GET /api/visitors?is_team_leader=true
```

#### 获取访客详情
```bash
GET /api/visitors/1
Authorization: Bearer YOUR_TOKEN
```

#### 更新访客信息
```bash
PUT /api/visitors/1
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "notes": "重要客户",
  "shipping_address": "上海市浦东新区xxx"
}
```

#### 删除访客
```bash
DELETE /api/visitors/1
Authorization: Bearer YOUR_TOKEN
```

### 团队长管理

#### 审批团队长
```bash
POST /api/visitors/1/approve-leader
Authorization: Bearer YOUR_TOKEN
```

#### 获取团队成员
```bash
GET /api/visitors/1/team-members
Authorization: Bearer YOUR_TOKEN
```

### 团队成员管理

#### 添加团队成员
```bash
POST /api/team-members
Authorization: Bearer YOUR_TOKEN
Content-Type: application/json

{
  "team_leader_id": 1,
  "member_id": 2,
  "role": "销售",
  "notes": "推荐加入"
}
```

#### 移除团队成员
```bash
DELETE /api/team-members/1
Authorization: Bearer YOUR_TOKEN
```

---

## 🔐 权限说明

### 访客管理权限（新增）

| 权限代码 | 权限名称 | 说明 |
|---------|---------|------|
| visitor:create | 创建访客 | 创建访客记录 |
| visitor:delete | 删除访客 | 删除访客记录 |
| visitor:modify | 修改访客 | 修改访客信息 |
| visitor:view | 查看访客 | 查看访客信息 |
| visitor:approve_leader | 审批团队长 | 审批团队长申请 |
| visitor:manage_team | 管理团队 | 管理团队成员 |

### 角色权限分配

| 角色 | visitor:create | visitor:delete | visitor:modify | visitor:view | visitor:approve_leader | visitor:manage_team |
|-----|---------------|---------------|---------------|-------------|---------------------|-------------------|
| CEO | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| 超级管理员 | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| CTO管理员 | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| 部门经理 | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| 普通员工 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |

---

## ⚙️ 数据库表结构

### users表（新增字段）
- `wechat` VARCHAR(50) - 微信号
- `is_ceo` BOOLEAN - 是否为CEO

### visitors表（新表）
- `id` INTEGER - 主键
- `name` VARCHAR(50) - 姓名
- `wechat` VARCHAR(50) - 微信号
- `phone` VARCHAR(20) - 电话
- `referrer` VARCHAR(50) - 推荐人
- `notes` TEXT - 备注
- `shipping_address` TEXT - 收货地址
- `is_team_leader` BOOLEAN - 是否为团队长
- `willing_to_be_leader` BOOLEAN - 是否愿意成为团队长
- `status` VARCHAR(20) - 状态
- `created_at` DATETIME - 创建时间
- `updated_at` DATETIME - 更新时间
- `created_by` INTEGER - 创建人ID

### team_members表（新表）
- `id` INTEGER - 主键
- `team_leader_id` INTEGER - 团队长ID
- `member_id` INTEGER - 成员ID
- `role` VARCHAR(50) - 角色
- `joined_at` DATETIME - 加入时间
- `notes` TEXT - 备注
- `created_at` DATETIME - 创建时间

---

## 🔍 常见问题

### Q1: 如何从v1.0升级到v2.0？

A: 建议重新初始化数据库：

```bash
# 1. 备份现有数据
python -c "from models import SessionLocal, User; db=SessionLocal(); users=db.query(User).all(); [print(f'{u.id},{u.name},{u.email}') for u in users]; db.close()" > users_backup.txt

# 2. 删除旧数据库
rm -f auth.db

# 3. 使用新脚本初始化
python init_data_v2.py
```

### Q2: 团队长审批的条件是什么？

A: 团队长审批需要满足两个条件：
1. 拥有3个以上角色的成员
2. 访客愿意成为团队长（willing_to_be_leader = True）

### Q3: 访客微信号和电话号码是否唯一？

A: 是的，微信号和电话号码都是唯一的，注册时会检查是否已存在。

### Q4: 如何查看访客的团队成员？

A: 有两种方式：
1. 在访客管理列表中查看"团队成员数"列
2. 使用API接口：`GET /api/visitors/{visitor_id}/team-members`

### Q5: CEO和超级管理员的区别是什么？

A:
- **CEO**：级别0，公司首席执行官，拥有所有权限
- **超级管理员**：级别1，拥有所有系统权限

CEO是公司的最高管理者，超级管理员是系统的最高管理员。在实际使用中，CEO通常拥有更高的决策权限。

---

## 📞 技术支持

- **技术支持**：tech@meiyue.com
- **权限咨询**：admin@meiyue.com
- **安全举报**：security@meiyue.com

---

**媄月商业艺术 - 文化科技驱动的品牌未来资产**
**© 2026 媄月商业 版权所有 | 未经授权不得复制、下载、传播**

---

## 版本历史

| 版本 | 日期 | 更新内容 |
|-----|------|---------|
| v2.0 | 2026-01-23 | 添加CEO角色、黄爱莉账号、访客管理系统 |
| v1.0 | 2026-01-23 | 初始版本，基础权限管理系统 |
