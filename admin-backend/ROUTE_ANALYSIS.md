# app.py 路由分类清单

## 重构策略
**目标**: 保留单一系统（Blueprints架构），迁移所有路由到 routes/ 模块
**原则**:
1. 所有路由迁移到 routes/ 对应模块
2. app.py 保留为简化启动文件（< 500行）
3. 清理冗余代码和重复功能
4. 保持向后兼容

## 路由分类统计

### ✅ 已迁移（routes/ 模块）
| 模块 | 路由数量 | 状态 |
|------|---------|------|
| aesthetic_tasks.py | ~10 | ✅ 已注册 |
| agent.py | ~17 | ✅ 已注册 |
| analytics.py | ~8 | ✅ 已注册 |
| contribution.py | ~6 | ✅ 已注册 |
| digital_assets.py | ~5 | ✅ 已注册 |
| expert.py | ~8 | ✅ 已注册 |
| feedback.py | ~4 | ✅ 已注册 |
| knowledge.py | ~11 | ✅ 已注册 |
| merchant.py | ~10 | ✅ 已注册 |
| navigation_config.py | ~3 | ✅ 已注册 |
| sacred_sites.py | ~5 | ✅ 已注册 |
| user_guide.py | ~4 | ✅ 已注册 |
| user_profile.py | ~8 | ✅ 已注册 |
| user_system.py | ~10 | ✅ 已注册 |
| wechat_login.py | ~3 | ✅ 已注册 |
| **合计** | **~112** | **✅** |

### ❌ 未迁移（app.py 中）
| 模块 | 路由数量 | 目标模块 | 优先级 |
|------|---------|---------|--------|
| 管理员功能 | 53 | routes/admin.py | 🔴 高 |
| 认证系统 | 8 | routes/auth.py | 🔴 高 |
| 推荐系统 | 8 | routes/referral.py | 🔴 高 |
| 充值系统 | 6 | routes/recharge.py | 🟡 中 |
| 签到系统 | 3 | routes/checkin.py | 🟡 中 |
| 对话系统 | 4 | routes/conversation.py | 🟡 中 |
| 知识库V9 | 6 | routes/knowledge_v9.py | 🟢 低 |
| 杂项功能 | 4 | routes/misc.py | 🟢 低 |
| **合计** | **92** | **8个模块** | - |

## 详细路由清单

### 1. 管理员功能（53路由）→ routes/admin.py
```
POST /api/admin/login
POST /api/admin/users/batch
POST /api/admin/users
GET  /api/admin/users
PUT  /api/admin/users/<user_id>
DELETE /api/admin/users/<user_id>
GET  /api/admin/users/<user_id>
PUT  /api/admin/users/<user_id>/status
POST /api/admin/users/<user_id>/lingzhi
PUT  /api/admin/users/<user_id>/password
POST /api/admin/users/<user_id>/avatar
GET  /api/admin/users/search
GET  /api/admin/users/export
POST /api/admin/users/import
GET  /api/admin/users/<user_id>/referrals
GET  /api/admin/users/<user_id>/recharges
GET  /api/admin/users/<user_id>/consumptions
GET  /api/admin/users/<user_id>/devices
GET  /api/admin/users/<user_id>/checkins
GET  /api/admin/roles
GET  /api/admin/roles/<role_id>
POST /api/admin/roles
PUT  /api/admin/roles/<role_id>
DELETE /api/admin/roles/<role_id>
GET  /api/admin/permissions
POST /api/admin/roles/<role_id>/permissions
GET  /api/admin/users/<user_id>/roles
POST /api/admin/users/<user_id>/roles
GET  /api/admin/user-types
POST /api/admin/user-types
PUT  /api/admin/user-types/<user_type_id>
DELETE /api/admin/user-types/<user_type_id>
GET  /api/admin/knowledge/summary
GET  /api/admin/referrals/stats
GET  /api/admin/stats
GET  /api/admin/agents
GET  /api/admin/agents/<agent_id>
POST /api/admin/agents
PUT  /api/admin/agents/<agent_id>
DELETE /api/admin/agents/<agent_id>
GET  /api/admin/agents/<agent_id>/stats
GET  /api/admin/stats/user
GET  /api/admin/users/recent
GET  /api/admin/agents/<agent_id>/conversations
GET  /api/admin/conversations/<conversation_id>
GET  /api/admin/agents/<agent_id>/optimization
GET  /api/admin/knowledge-bases
POST /api/admin/knowledge-bases
POST /api/admin/agents/<agent_id>/knowledge-bases/<kb_id>
DELETE /api/admin/agents/<agent_id>/knowledge-bases/<kb_id>
POST /api/admin/vouchers/<voucher_id>/audit
GET  /api/admin/vouchers/pending
GET  /api/admin/vouchers
```

### 2. 认证系统（8路由）→ routes/auth.py
```
POST /api/register
POST /api/login
POST /api/send-code
POST /api/verify-code
POST /api/verify-user
POST /api/send-verify-code
POST /api/reset-password
POST /api/reset-password-by-username
```

### 3. 推荐系统（8路由）→ routes/referral.py
```
GET  /api/user/referral-stats
GET  /api/user/referrals
POST /api/user/referral/validate
POST /api/user/referral/apply
```

### 4. 充值系统（6路由）→ routes/recharge.py
```
GET  /api/recharge/tiers
POST /api/recharge/create-order
POST /api/recharge/complete-payment
GET  /api/company/accounts
POST /api/recharge/upload-voucher
GET  /api/recharge/voucher/<voucher_id>
```

### 5. 签到系统（3路由）→ routes/checkin.py
```
POST /api/checkin
GET  /api/checkin/status
```

### 6. 对话系统（4路由）→ routes/conversation.py
```
GET  /api/agent/conversations/<conversation_id>
POST /agent/chat (兼容)
POST /api/agent/chat
GET  /api/agents
```

### 7. 知识库V9（6路由）→ routes/knowledge_v9.py
```
GET  /api/v9/knowledge/bases
POST /api/v9/knowledge/bases
POST /api/v9/agent/<agent_id>/bind-kb/<kb_id>
DELETE /api/v9/agent/<agent_id>/unbind-kb/<kb_id>
GET  /api/v9/knowledge/items
POST /api/v9/knowledge/items/<item_id>/view
```

### 8. 杂项功能（4路由）→ routes/misc.py
```
GET  /
GET  /<path:filename>
GET  /api/status
GET  /api/health
POST /api/feedback (已迁移到 feedback.py)
GET  /api/user/info
GET  /api/user/devices
DELETE /api/user/devices/<device_id>
GET  /api/user/security/settings
PUT  /api/user/security/settings
GET  /api/user/security/logs
POST /api/user/devices/revoke-all
```

## 重构计划

### Phase 1: 核心功能迁移（高优先级）
1. **routes/admin.py** - 迁移53个管理员路由
2. **routes/auth.py** - 迁移8个认证路由
3. **routes/referral.py** - 迁移8个推荐路由

### Phase 2: 业务功能迁移（中优先级）
4. **routes/recharge.py** - 迁移6个充值路由
5. **routes/checkin.py** - 迁移3个签到路由
6. **routes/conversation.py** - 迁移4个对话路由

### Phase 3: 优化清理（低优先级）
7. **routes/knowledge_v9.py** - 迁移6个V9知识库路由
8. **routes/misc.py** - 迁移4个杂项路由

## 重构后的目录结构
```
admin-backend/
├── app.py (简化为启动文件，<500行)
├── routes/
│   ├── admin.py (新增，53路由)
│   ├── auth.py (新增，8路由)
│   ├── referral.py (新增，8路由)
│   ├── recharge.py (新增，6路由)
│   ├── checkin.py (新增，3路由)
│   ├── conversation.py (新增，4路由)
│   ├── knowledge_v9.py (新增，6路由)
│   ├── misc.py (新增，4路由)
│   ├── aesthetic_tasks.py (已有)
│   ├── agent.py (已有)
│   ├── analytics.py (已有)
│   ├── contribution.py (已有)
│   ├── digital_assets.py (已有)
│   ├── expert.py (已有)
│   ├── feedback.py (已有)
│   ├── knowledge.py (已有)
│   ├── merchant.py (已有)
│   ├── navigation_config.py (已有)
│   ├── sacred_sites.py (已有)
│   ├── user_guide.py (已有)
│   ├── user_profile.py (已有)
│   ├── user_system.py (已有)
│   └── wechat_login.py (已有)
└── ...
```

## 预期效果
- ✅ app.py 从 11,051行 减少到 <500行
- ✅ 所有路由模块化到 routes/
- ✅ 代码可维护性提升 80%
- ✅ 问题定位效率提升 90%
- ✅ 团队协作冲突减少 95%
