# 灵值生态园 - 前后台功能对照表

## 📋 前台功能与后台API对照

| 序号 | 前台页面 | 后台路由文件 | 后台API前缀 | 状态 | 说明 |
|-----|---------|------------|------------|------|------|
| 1 | AdminDashboard | admin.py | /api/admin | ✅ 已有 | 管理员仪表盘 |
| 2 | AdminLogin | admin.py | /api/admin | ✅ 已有 | 管理员登录 |
| 3 | AestheticTasks | aesthetic_tasks.py | /api/aesthetic | ✅ 已有 | 美学任务 |
| 4 | AgentManagement | agent.py | /api/agent | ✅ 已有 | 智能体管理 |
| 5 | AnalyticsDashboard | analytics.py | /api/analytics | ✅ 已有 | 数据分析 |
| 6 | ApiConfig | api_compat.py | /api | ✅ 已有 | API配置 |
| 7 | AssetManagement | digital_assets.py | /api/assets | ✅ 已有 | 资产管理 |
| 8 | Assets | digital_assets.py | /api/assets | ✅ 已有 | 资产列表 |
| 9 | BountyHunter | - | - | ❌ 缺失 | 赏金猎人 |
| 10 | Chat | agent.py | /api/agent | ✅ 已有 | 聊天 |
| 11 | ChatMemory | conversation_billing.py | /api/memory | ✅ 已有 | 聊天记忆 |
| 12 | CompanyInfo | - | - | ❌ 缺失 | 公司信息 |
| 13 | CompanyKnowledge | knowledge.py | /api/knowledge | ✅ 已有 | 公司知识库 |
| 14 | CompanyNews | news_articles.py | /api/v9/news | ✅ 已有 | 公司新闻 |
| 15 | CompanyProjects | - | - | ❌ 缺失 | 公司项目 |
| 16 | CompanyUsers | admin.py | /api/admin/users | ✅ 已有 | 公司用户 |
| 17 | Dashboard | checkin.py | /api/checkin | ✅ 已有 | 用户仪表盘 |
| 18 | DigitalAssets | digital_assets.py | /api/assets | ✅ 已有 | 数字资产 |
| 19 | DividendPool | - | - | ❌ 缺失 | 分红池 |
| 20 | Economy | - | - | ❌ 缺失 | 经济系统 |
| 21 | ExpertWorkbench | expert.py | /api/expert | ✅ 已有 | 专家工作台 |
| 22 | Feedback | feedback.py | /api/feedback | ✅ 已有 | 用户反馈 |
| 23 | ForgotPassword | auth.py | /api/auth | ✅ 已有 | 忘记密码 |
| 24 | Journey | - | - | ❌ 缺失 | 用户旅程 |
| 25 | Knowledge | knowledge.py | /api/knowledge | ✅ 已有 | 知识库 |
| 26 | KnowledgeManagement | knowledge.py | /api/knowledge | ✅ 已有 | 知识管理 |
| 27 | LoginFixed | auth.py | /api/auth | ✅ 已有 | 登录 |
| 28 | LoginFull | auth.py | /api/auth | ✅ 已有 | 登录 |
| 29 | MediumVideoProject | medium_video_api.py | /api/video | ✅ 已有 | 中视频项目 |
| 30 | MerchantDetail | merchant.py | /api/merchant | ✅ 已有 | 商家详情 |
| 31 | MerchantPool | merchant.py | /api/merchant | ✅ 已有 | 商家池 |
| 32 | MerchantWorkbench | merchant.py | /api/merchant | ✅ 已有 | 商家工作台 |
| 33 | Partner | partner_api.py | /api/partner | ✅ 已有 | 合伙人 |
| 34 | Profile | user_profile.py | /api/profile | ✅ 已有 | 个人资料 |
| 35 | ProjectPool | - | - | ❌ 缺失 | 项目池 |
| 36 | Recharge | recharge.py | /api/recharge | ✅ 已有 | 充值 |
| 37 | ReferralNetwork | referral_network_api.py | /api/referral-network | ✅ 已有 | 推荐网络 |
| 38 | ReferralPage | referral.py | /api/referral | ✅ 已有 | 推荐页面 |
| 39 | RegisterManual | auth.py | /api/auth | ✅ 已有 | 注册 |
| 40 | RoleManagement | - | - | ❌ 缺失 | 角色管理 |
| 41 | SacredSitesManagement | sacred_sites.py | /api/sacred | ✅ 已有 | 文化圣地 |
| 42 | SecuritySettings | - | - | ❌ 缺失 | 安全设置 |
| 43 | UserGuide | user_guide.py | /api/guide | ✅ 已有 | 用户指南 |
| 44 | UserLearning | - | - | ❌ 缺失 | 用户学习 |
| 45 | UserManagement | admin.py | /api/admin/users | ✅ 已有 | 用户管理 |
| 46 | UserManagementEnhanced | admin.py | /api/admin/users | ✅ 已有 | 增强用户管理 |
| 47 | UserProfileEdit | user_profile.py | /api/profile | ✅ 已有 | 用户资料编辑 |
| 48 | UserResources | - | - | ❌ 缺失 | 用户资源 |
| 49 | UserResourcesMarket | - | - | ❌ 缺失 | 资源市场 |
| 50 | UserTypeManagement | - | - | ❌ 缺失 | 用户类型管理 |
| 51 | ValueGuide | - | - | ❌ 缺失 | 价值指南 |
| 52 | WeChatCallback | wechat_login.py | /api/wechat | ✅ 已有 | 微信回调 |
| 53 | XianAesthetics | aesthetic_tasks.py | /api/aesthetic | ✅ 已有 | 咸美学 |

## 📊 统计

- ✅ 已有后台API: 39个
- ❌ 缺失后台API: 14个

## 🔴 缺失的后台管理功能

### 1. BountyHunter (赏金猎人)
- 前台页面: `/bounty-hunter`
- 需要的后台API:
  - GET /api/admin/bounties - 获取赏金列表
  - POST /api/admin/bounties - 创建赏金
  - PUT /api/admin/bounties/:id - 更新赏金
  - DELETE /api/admin/bounties/:id - 删除赏金

### 2. CompanyInfo (公司信息)
- 前台页面: `/company-info`
- 需要的后台API:
  - GET /api/admin/company/info - 获取公司信息
  - PUT /api/admin/company/info - 更新公司信息

### 3. CompanyProjects (公司项目)
- 前台页面: `/company-projects`
- 需要的后台API:
  - GET /api/admin/projects - 获取项目列表
  - POST /api/admin/projects - 创建项目
  - PUT /api/admin/projects/:id - 更新项目
  - DELETE /api/admin/projects/:id - 删除项目

### 4. DividendPool (分红池)
- 前台页面: `/dividend-pool`
- 需要的后台API:
  - GET /api/admin/dividends - 获取分红记录
  - POST /api/admin/dividends/distribute - 分配分红
  - GET /api/admin/dividends/stats - 分红统计

### 5. Economy (经济系统)
- 前台页面: `/economy`
- 需要的后台API:
  - GET /api/admin/economy/stats - 经济统计
  - GET /api/admin/economy/transactions - 交易记录
  - POST /api/admin/economy/settings - 经济设置

### 6. Journey (用户旅程)
- 前台页面: `/journey`
- 需要的后台API:
  - GET /api/admin/journeys - 获取用户旅程
  - GET /api/admin/journeys/:userId - 获取特定用户旅程

### 7. ProjectPool (项目池)
- 前台页面: `/project-pool`
- 需要的后台API:
  - GET /api/admin/project-pool - 获取项目池
  - PUT /api/admin/project-pool/:id - 更新项目池

### 8. RoleManagement (角色管理)
- 前台页面: `/role-management`
- 需要的后台API:
  - GET /api/admin/roles - 获取角色列表
  - POST /api/admin/roles - 创建角色
  - PUT /api/admin/roles/:id - 更新角色
  - DELETE /api/admin/roles/:id - 删除角色
  - GET /api/admin/roles/:id/permissions - 获取角色权限
  - PUT /api/admin/roles/:id/permissions - 更新角色权限

### 9. SecuritySettings (安全设置)
- 前台页面: `/security-settings`
- 需要的后台API:
  - GET /api/admin/security/settings - 获取安全设置
  - PUT /api/admin/security/settings - 更新安全设置

### 10. UserLearning (用户学习)
- 前台页面: `/user-learning`
- 需要的后台API:
  - GET /api/admin/user-learning - 获取用户学习记录
  - GET /api/admin/user-learning/:userId - 获取特定用户学习

### 11. UserResources (用户资源)
- 前台页面: `/user-resources`
- 需要的后台API:
  - GET /api/admin/user-resources - 获取用户资源
  - POST /api/admin/user-resources - 创建资源
  - PUT /api/admin/user-resources/:id - 更新资源
  - DELETE /api/admin/user-resources/:id - 删除资源

### 12. UserResourcesMarket (资源市场)
- 前台页面: `/resources-market`
- 需要的后台API:
  - GET /api/admin/resources/market - 获取市场资源
  - POST /api/admin/resources/market/approve - 审核资源

### 13. UserTypeManagement (用户类型管理)
- 前台页面: `/user-type-management`
- 需要的后台API:
  - GET /api/admin/user-types - 获取用户类型
  - POST /api/admin/user-types - 创建用户类型
  - PUT /api/admin/user-types/:id - 更新用户类型
  - DELETE /api/admin/user-types/:id - 删除用户类型

### 14. ValueGuide (价值指南)
- 前台页面: `/value-guide`
- 需要的后台API:
  - GET /api/admin/value-guide - 获取价值指南
  - PUT /api/admin/value-guide - 更新价值指南
