# 灵值生态园项目 - 上下文全景文档

## 📋 项目概览

### 项目名称
灵值生态园智能体系统

### 项目定位
一个让您日常行为产生真实收益的数字资产系统，融合文化、商业、情绪价值、数字资产、科技和创新六维价值。

### 公司主体
陕西媄月商业艺术有限责任公司

### 核心价值
- 🌱 轻度参与（5分钟/天）：年收入约 1,080 元
- 🌳 中度参与（30分钟/天）：年收入约 10,800 元
- 🏆 深度参与（1小时/天）：年收入 36,000 元+

### 部署信息
- 服务器：阿里云 ECS
- 公网IP：123.56.142.143
- 前端端口：80/443
- 后端端口：8001

---

## 🏗️ 技术架构

### 前端技术栈

**框架和构建工具**
- React 18.3.1 + TypeScript 5.4.5
- Vite 5.4.21 (构建工具)
- React Router 6.22.3 (路由)

**UI和样式**
- Tailwind CSS 3.4.3 (样式框架)
- Lucide React (图标库)
- React Quill 2.0.0 (富文本编辑器)

**状态管理**
- Context API (用户认证、聊天状态)

**开发工具**
- TypeScript 5.4.5
- ESLint (代码检查)
- Vite Plugin PWA (PWA支持)

**构建配置**
- 输出目录：`../public` (注意：不是dist!)
- 开发服务器端口：3000
- 生产构建：`tsc && vite build`

### 后端技术栈

**核心框架**
- Python Flask (Web框架)
- Flask-CORS (跨域支持)

**数据库**
- SQLite (主数据库)
- 文件：`lingzhi_ecosystem.db`

**认证和安全**
- JWT (JSON Web Token) - 有效期7天
- SHA256 和 bcrypt (密码加密，双密码兼容)
- 手机验证码（模拟）

**AI和智能体**
- DeepSeek-V3-2 模型 (智能体核心)
- Coze Coding SDK (大模型集成)
- LangChain (智能体框架)
- 知识库检索

**其他库**
- bcrypt (密码加密)
- PyJWT (JWT处理)
- requests (HTTP请求)

### 部署架构

```
用户浏览器
    ↓
[公网IP:80/443] (Nginx或Web服务器)
    ↓
    ├→ / → 前端静态文件 (React, public目录)
    └→ /api/* → [127.0.0.1:8001] (Flask后端)
```

**关键配置：**
- 前端自动检测API地址并修正为8001端口
- 支持环境变量、localStorage、自动检测三种配置方式
- CORS已配置支持所有来源

---

## 📂 项目结构

### 根目录结构

```
lingzhiapp/
├── admin-backend/           # 后端代码
│   ├── app.py              # Flask主应用 (5467行)
│   ├── add_*.py            # 各种功能补丁脚本
│   ├── check_*.py          # 检查脚本
│   ├── migrate_*.py        # 迁移脚本
│   ├── fix_*.py            # 修复脚本
│   ├── scripts/            # 工具脚本
│   └── lingzhi_ecosystem.db # SQLite数据库
│
├── web-app/                # 前端代码
│   ├── src/
│   │   ├── components/     # 公共组件
│   │   │   ├── Layout.tsx        # 主布局
│   │   │   ├── Navigation.tsx    # 导航栏
│   │   │   ├── ProtectedRoute.tsx # 路由保护
│   │   │   └── MobileRichEditor.tsx # 富文本编辑器
│   │   │
│   │   ├── contexts/       # 上下文
│   │   │   ├── AuthContext.tsx    # 用户认证上下文
│   │   │   └── ChatContext.tsx    # 聊天上下文
│   │   │
│   │   ├── pages/          # 页面组件
│   │   │   ├── Login.tsx          # 登录页
│   │   │   ├── Register.tsx       # 注册页
│   │   │   ├── Dashboard.tsx      # 仪表盘
│   │   │   ├── Chat.tsx           # 智能对话
│   │   │   ├── Economy.tsx        # 经济模型
│   │   │   ├── Partner.tsx        # 合伙人计划
│   │   │   ├── Profile.tsx        # 个人中心
│   │   │   ├── SecuritySettings.tsx # 安全设置
│   │   │   ├── Recharge.tsx       # 充值页面
│   │   │   ├── AdminDashboard.tsx # 管理后台
│   │   │   ├── AgentManagement.tsx # 智能体管理
│   │   │   ├── KnowledgeManagement.tsx # 知识库管理
│   │   │   ├── UserManagement.tsx  # 用户管理
│   │   │   ├── WeChatCallback.tsx  # 微信回调
│   │   │   ├── ApiConfig.tsx       # API配置页面
│   │   │   └── ... (更多页面)
│   │   │
│   │   ├── services/       # API服务
│   │   │   ├── api.ts            # 真实API
│   │   │   └── mockApi.ts        # 模拟API
│   │   │
│   │   ├── types/          # TypeScript类型
│   │   │   └── index.ts
│   │   │
│   │   └── index.css       # 全局样式
│   │
│   ├── package.json        # 前端依赖
│   ├── vite.config.ts      # Vite配置
│   ├── tsconfig.json       # TypeScript配置
│   └── .env.production     # 生产环境变量
│
├── public/                 # 前端构建输出 (注意：不是dist!)
│   ├── index.html
│   ├── assets/
│   └── manifest.json
│
├── config/                 # 配置文件
│   └── agent_llm_config.json  # 智能体配置
│
├── docs/                   # 文档
│   ├── PUBLIC_DEPLOYMENT.md      # 公网部署指南
│   ├── QUICK_FIX_500_ERROR.md   # 快速修复指南
│   └── 500_ERROR_SOLUTION.md    # 完整解决方案
│
├── scripts/                # 脚本
│   ├── deploy.sh
│   ├── auto-deploy.sh
│   └── setup-public-access.sh
│
├── logs/                   # 日志目录
│   └── app_backend.log     # 后端日志
│
├── requirements.txt        # Python依赖
├── package.json            # 根package.json
├── README.md               # 项目说明
└── 灵值生态园智能体移植包/  # 旧系统移植包

```

---

## 🗄️ 数据库结构

### 核心表

#### 1. users (用户表)
```sql
- id INTEGER PRIMARY KEY
- username TEXT UNIQUE (用户名)
- email TEXT (邮箱)
- phone TEXT (手机号)
- password_hash TEXT (密码哈希，支持SHA256和bcrypt)
- total_lingzhi INTEGER DEFAULT 0 (总灵值)
- status TEXT DEFAULT 'active' (状态)
- last_login_at TIMESTAMP (最后登录时间)
- avatar_url TEXT (头像URL)
- real_name TEXT (真实姓名)
- is_verified BOOLEAN DEFAULT 0 (是否已验证)
- login_type TEXT DEFAULT 'phone' (登录类型)
- wechat_openid TEXT UNIQUE (微信OpenID)
- wechat_unionid TEXT (微信UnionID)
- wechat_nickname TEXT (微信昵称)
- wechat_avatar TEXT (微信头像)
- created_at TIMESTAMP
- updated_at TIMESTAMP

# 安全相关字段（近期添加）
- require_phone_verification BOOLEAN DEFAULT 1 (是否需要手机验证)
- single_login_enabled BOOLEAN DEFAULT 1 (是否启用单点登录)
```

#### 2. user_profiles (用户详细信息)
```sql
- id INTEGER PRIMARY KEY
- user_id INTEGER UNIQUE
- real_name TEXT (真实姓名)
- phone TEXT UNIQUE (手机号)
- email TEXT UNIQUE (邮箱)
- id_card TEXT (身份证)
- bank_account TEXT (银行账户)
- bank_name TEXT (银行名称)
- address TEXT (地址)
- is_completed BOOLEAN DEFAULT 0 (是否完善信息)
- completed_at TIMESTAMP
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

#### 3. checkin_records (签到记录)
```sql
- id INTEGER PRIMARY KEY
- user_id INTEGER
- checkin_date DATE (签到日期)
- lingzhi_earned INTEGER DEFAULT 10 (获得灵值)
- created_at TIMESTAMP
UNIQUE(user_id, checkin_date)
```

#### 4. partner_applications (合伙人申请)
```sql
- id INTEGER PRIMARY KEY
- user_id INTEGER
- user_name TEXT
- phone TEXT
- current_lingzhi INTEGER
- reason TEXT
- status TEXT DEFAULT 'pending' (申请状态)
- created_at TIMESTAMP
```

#### 5. recharge_tiers (充值档位)
```sql
- id INTEGER PRIMARY KEY
- name TEXT (档位名称)
- description TEXT (描述)
- price DECIMAL(10,2) (价格)
- base_lingzhi INTEGER (基础灵值)
- bonus_lingzhi INTEGER (赠送灵值)
- bonus_percentage INTEGER (赠送百分比)
- partner_level INTEGER DEFAULT 0 (合伙人等级)
- benefits TEXT (权益说明)
- status TEXT DEFAULT 'active'
- sort_order INTEGER (排序)
```

#### 6. recharge_records (充值记录)
```sql
- id INTEGER PRIMARY KEY
- user_id INTEGER
- tier_id INTEGER
- order_no TEXT UNIQUE (订单号)
- amount DECIMAL(10,2) (金额)
- base_lingzhi INTEGER
- bonus_lingzhi INTEGER
- total_lingzhi INTEGER
- payment_method VARCHAR(20) (支付方式)
- payment_status VARCHAR(20) (支付状态)
- payment_time TIMESTAMP
- transaction_id TEXT (交易ID)
- voucher_id INTEGER (凭证ID)
- audit_status VARCHAR(20) (审核状态)
- bank_info TEXT (银行信息)
- status TEXT DEFAULT 'active'
- created_at TIMESTAMP
```

#### 7. user_devices (设备管理 - 新增)
```sql
- id INTEGER PRIMARY KEY
- user_id INTEGER
- device_id TEXT (设备ID)
- device_name TEXT (设备名称)
- device_type TEXT (设备类型)
- user_agent TEXT
- ip_address TEXT
- location TEXT
- is_current BOOLEAN DEFAULT 0 (是否当前设备)
- last_active_at TIMESTAMP
- created_at TIMESTAMP
UNIQUE(user_id, device_id)
```

#### 8. login_sessions (登录会话 - 新增)
```sql
- id INTEGER PRIMARY KEY
- user_id INTEGER
- token TEXT UNIQUE
- device_id TEXT
- ip_address TEXT
- user_agent TEXT
- expires_at TIMESTAMP
- created_at TIMESTAMP
```

#### 9. security_logs (安全日志 - 新增)
```sql
- id INTEGER PRIMARY KEY
- user_id INTEGER
- event_type TEXT (事件类型)
- ip_address TEXT
- user_agent TEXT
- details TEXT (详情JSON)
- created_at TIMESTAMP
```

#### 10. agents (智能体)
```sql
- id INTEGER PRIMARY KEY
- name TEXT
- description TEXT
- system_prompt TEXT
- model_config TEXT (JSON)
- tools TEXT (JSON数组)
- status TEXT DEFAULT 'active'
- avatar_url TEXT
- created_by INTEGER
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

#### 11. knowledge_bases (知识库)
```sql
- id INTEGER PRIMARY KEY
- name TEXT
- description TEXT
- vector_db_id TEXT
- document_count INTEGER DEFAULT 0
- created_by INTEGER
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

#### 12. knowledge_documents (知识库文档)
```sql
- id INTEGER PRIMARY KEY
- knowledge_base_id INTEGER
- title TEXT
- content TEXT
- file_path TEXT
- file_type TEXT
- file_size INTEGER
- embedding_status TEXT DEFAULT 'pending'
- embedding_error TEXT
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

#### 13. conversations (对话记录)
```sql
- id INTEGER PRIMARY KEY
- agent_id INTEGER
- user_id INTEGER
- conversation_id TEXT
- messages TEXT (JSON)
- title TEXT
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

#### 14. feedback (反馈)
```sql
- id INTEGER PRIMARY KEY
- conversation_id INTEGER
- agent_id INTEGER
- user_id INTEGER
- type TEXT
- rating INTEGER
- question TEXT
- comment TEXT
- contribution_value INTEGER DEFAULT 5
- created_at TIMESTAMP
```

#### 15. company_accounts (公司收款账户)
```sql
- id INTEGER PRIMARY KEY
- account_name TEXT
- account_number TEXT
- bank_name TEXT
- bank_branch TEXT
- company_name TEXT
- company_credit_code TEXT
- account_type TEXT DEFAULT 'primary'
- is_active BOOLEAN DEFAULT 1
- sort_order INTEGER
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

#### 16. transfer_vouchers (转账凭证)
```sql
- id INTEGER PRIMARY KEY
- recharge_record_id INTEGER
- user_id INTEGER
- image_url TEXT
- transfer_amount DECIMAL(10,2)
- transfer_time TIMESTAMP
- transfer_account TEXT
- remark TEXT
- audit_status TEXT DEFAULT 'pending'
- audit_user_id INTEGER
- audit_time TIMESTAMP
- audit_remark TEXT
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

#### 17. system_notifications (系统通知)
```sql
- id INTEGER PRIMARY KEY
- title TEXT
- content TEXT
- notification_type TEXT DEFAULT 'info'
- is_read BOOLEAN DEFAULT 0
- target_user_id INTEGER (NULL表示全员通知)
- created_at TIMESTAMP
- updated_at TIMESTAMP
```

#### 18. user_read_notifications (用户已读通知)
```sql
- id INTEGER PRIMARY KEY
- user_id INTEGER
- notification_id INTEGER
- read_at TIMESTAMP
UNIQUE(user_id, notification_id)
```

#### 19. admins (后台管理员)
```sql
- id INTEGER PRIMARY KEY
- username TEXT UNIQUE
- password_hash TEXT
- role TEXT DEFAULT 'admin'
- created_at TIMESTAMP
```

---

## 🔑 关键配置

### 环境变量

**后端环境变量 (app.py)**
```python
# Coze 集成配置
COZE_WORKLOAD_IDENTITY_API_KEY
COZE_INTEGRATION_MODEL_BASE_URL = 'https://integration.coze.cn/api/v3'
COZE_INTEGRATION_BASE_URL = 'https://integration.coze.cn'
COZE_PROJECT_ID = '7597768668038643746'

# Flask 配置
SECRET_KEY = 'lingzhi-ecosystem-secret-key-2026'
DATABASE = 'lingzhi_ecosystem.db'

# JWT 配置
JWT_SECRET = 'lingzhi-jwt-secret-key'
JWT_EXPIRATION = 7 * 24 * 60 * 60  # 7天

# 微信开放平台配置
WECHAT_APP_ID
WECHAT_APP_SECRET
WECHAT_REDIRECT_URI = 'http://localhost:3000/wechat/callback'
```

**前端环境变量**
```bash
# 生产环境 (web-app/.env.production)
VITE_API_BASE_URL=http://YOUR_PUBLIC_IP:8001
```

### 智能体配置

**文件：config/agent_llm_config.json**

```json
{
  "config": {
    "model": "deepseek-v3-2-251201",
    "temperature": 0.8,
    "top_p": 0.9,
    "max_tokens": 4096,
    "max_completion_tokens": 10000,
    "thinking_type": "enabled",
    "reasoning_effort": "medium"
  },
  "sp": "# 核心身份：媄月\"首席生态官\"...",
  "tools": [
    "知识库搜索",
    "联网搜索",
    "文生图",
    "灵值价值计算",
    "收入预测",
    "兑换信息查询",
    "投资回报计算",
    "参与级别建议",
    "用户签到",
    "签到历史查询",
    "今日签到状态",
    "今日签到统计",
    ...
    // 共100+个工具
  ]
}
```

### 构建配置

**Vite配置 (web-app/vite.config.ts)**
```typescript
{
  build: {
    emptyOutDir: true,
    outDir: '../public',  // 注意：输出到public，不是dist
  },
  server: {
    port: 3000,
    open: true
  }
}
```

---

## 🔌 API接口

### 认证相关

```
POST /api/login          # 用户登录（支持手机验证码）
POST /api/register       # 用户注册
POST /api/send-code      # 发送验证码
GET  /api/user/info      # 获取用户信息
PUT  /api/user/profile   # 更新用户资料
POST /api/user/profile   # 完善用户信息
GET  /api/user/require-complete  # 检查是否需要完善信息
GET  /api/user/devices          # 获取设备列表
DELETE /api/user/devices/:id    # 移除设备
POST /api/user/devices/revoke-all # 移除所有其他设备
GET  /api/user/security/settings # 获取安全设置
PUT  /api/user/security/settings # 更新安全设置
```

### 智能体相关

```
POST /api/agent/chat                           # 发送消息
GET  /api/agent/conversations/:id              # 获取对话历史
GET  /api/admin/agents                         # 获取智能体列表
```

### 经济模型

```
GET  /api/economy/income-projection?level=...  # 收入预测
GET  /api/economy/value?contribution=...      # 价值计算
GET  /api/economy/exchange-info               # 兑换信息
```

### 用户旅程

```
GET  /api/journey/stage/:userId               # 获取用户旅程阶段
PUT  /api/journey/progress/:userId            # 更新进度
GET  /api/journey/milestones/:userId          # 获取里程碑
```

### 合伙人

```
POST /api/partner/check-qualification         # 检查合伙人资格
POST /api/partner/apply                       # 提交合伙人申请
GET  /api/partner/status/:userId              # 获取申请状态
GET  /api/partner/privileges?level=...        # 获取权益
```

### 充值

```
GET  /api/recharge/tiers                       # 获取充值档位
POST /api/recharge/create                     # 创建充值订单
GET  /api/recharge/company-accounts           # 获取公司账户
POST /api/recharge/upload-voucher             # 上传转账凭证
GET  /api/recharge/records                    # 获取充值记录
```

### 签到

```
POST /api/checkin                              # 签到
GET  /api/checkin/history                     # 签到历史
GET  /api/checkin/status                      # 今日签到状态
GET  /api/checkin/statistics                  # 今日签到统计
```

### 系统通知

```
GET  /api/notifications                       # 获取通知
POST /api/notifications/mark-all-read         # 全部标记已读
```

### 管理后台

```
POST /api/admin/login                         # 管理员登录
GET  /api/admin/dashboard                     # 管理后台数据
GET  /api/admin/users                         # 用户列表
GET  /api/admin/agents                       # 智能体管理
GET  /api/admin/knowledge-bases              # 知识库管理
```

### 微信登录

```
GET  /api/wechat/auth-url                     # 获取微信授权URL
GET  /api/wechat/callback                    # 微信回调
```

### 健康检查

```
GET  /api/health                              # 健康检查
GET  /                                        # 服务状态
```

---

## 🎯 核心功能

### 1. 用户认证系统

**登录方式：**
- 用户名+密码登录
- 手机号+密码登录
- 微信开放平台登录
- 手机验证码二次验证（可选）

**安全特性：**
- JWT Token认证（7天有效期）
- 双密码加密兼容（SHA256 + bcrypt）
- 单点登录机制（禁止多处同时登录）
- 设备管理（查看和移除登录设备）
- 安全日志记录

### 2. 灵值系统

**获取灵值：**
- 每日签到：+30灵值/天
- 智能对话：根据互动质量获得灵值
- 完成任务：额外奖励
- 里程碑奖励：累计达到特定值获得奖励

**灵值价值：**
- 100灵值 ≈ 10元
- 1,000灵值 ≈ 100元
- 10,000灵值 ≈ 1,000元

### 3. 合伙人计划

**资格要求：**
- 累计10,000灵值
- 完善个人信息

**权益：**
- 更高的收益倍数
- 优先体验新功能
- 管理权限

### 4. 充值系统

**充值档位：**
- 7个档位（从基础到高级）
- 支付方式：在线支付、公司转账
- 赠送比例：档位越高，赠送越多

### 5. 智能对话

**智能体名称：** 灵值生态园

**能力：**
- 知识库检索
- 联网搜索
- 文生图
- 灵值计算
- 收入预测
- 100+个工具

**人格定位：**
- 商业架构师的智慧
- 文化修行向导的深度
- 情绪价值创造者的温度
- 数字资产财富管理者的远见
- 科技创新者的前瞻
- 文明重构者的使命

---

## 🔧 开发工作流

### 前端开发

```bash
# 安装依赖
cd web-app
npm install

# 启动开发服务器
npm run dev
# 访问: http://localhost:3000

# 构建生产版本
npm run build
# 输出到: ../public

# 预览生产版本
npm run preview
```

### 后端开发

```bash
# 启动后端服务
cd admin-backend
python app.py
# 运行在: http://0.0.0.0:8001

# 查看日志
tail -f ../logs/app_backend.log
```

### 部署流程

**方法1：自动化部署**
```bash
./auto-deploy.sh deploy
```

**方法2：手动部署**
```bash
# 1. 构建前端
cd web-app
npm run build

# 2. 启动后端
cd admin-backend
python app.py

# 3. 部署前端文件
# 将 public 目录部署到Web服务器
```

**方法3：使用部署脚本**
```bash
./setup-public-access.sh
```

---

## ⚠️ 重要注意事项

### 1. 前端构建输出目录

**重要：** 前端构建输出目录是 `../public`，不是 `dist`！

```typescript
// vite.config.ts
build: {
  emptyOutDir: true,
  outDir: '../public',  // 注意这里
}
```

### 2. 用户数据格式化

后端使用 `format_user_data()` 函数统一返回用户数据：

```python
def format_user_data(user_row):
    # 统一字段命名：将下划线命名转换为驼峰命名
    formatted = {
        'id': user_dict.get('id'),
        'username': user_dict.get('username'),
        'totalLingzhi': user_dict.get('total_lingzhi', 0),  # 驼峰命名
        ...
    }
    return formatted
```

所有用户数据相关接口都必须使用此函数！

### 3. API地址智能检测

前端自动检测API地址：

```typescript
const getApiBaseURL = (): string => {
  // 1. 优先使用环境变量
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }

  // 2. 从localStorage读取
  const customApiURL = localStorage.getItem('apiBaseURL')
  if (customApiURL) {
    return customApiURL
  }

  // 3. 智能检测
  const currentOrigin = window.location.origin
  if (!currentOrigin.includes(':8001')) {
    const url = new URL(currentOrigin)
    if (url.port === '80' || url.port === '443' || !url.port) {
      return `${url.protocol}//${url.hostname}:8001`
    }
  }

  return currentOrigin
}
```

访问 `http://YOUR_DOMAIN/api-config` 可手动配置。

### 4. 密码验证

支持双密码验证：

```python
def verify_password(password, password_hash):
    # 1. 先尝试 bcrypt
    if password_hash.startswith('$2b$'):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    # 2. 再尝试 SHA256
    if password_hash == hashlib.sha256(password.encode()).hexdigest():
        return True
    
    return False
```

### 5. 数据库迁移

数据库有自动迁移功能：

```python
# 添加新字段的示例
try:
    cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT")
except:
    pass  # 字段已存在
```

### 6. 日志位置

**后端日志：** `/app/work/logs/bypass/app.log` 或 `logs/app_backend.log`

**查看日志：**
```bash
tail -f logs/app_backend.log
tail -n 50 logs/app_backend.log
```

### 7. 单点登录机制

启用单点登录时，新登录会使旧会话失效：

```python
if single_login_enabled:
    # 删除该用户的所有旧会话
    cursor.execute("DELETE FROM login_sessions WHERE user_id = ?", (user['id'],))
```

---

## 🚨 常见问题

### 问题1：修改个人资料后不显示

**原因：** 后端返回的数据字段名不统一

**解决：** 使用 `format_user_data()` 函数统一返回

### 问题2：公网IP访问500错误

**原因：** 前端API地址配置错误

**解决：**
1. 自动检测已修复，无需配置
2. 或访问 `/api-config` 手动设置
3. 或修改 `.env.production`

### 问题3：构建输出找不到文件

**原因：** 误以为输出在 `dist` 目录

**解决：** 输出在 `public` 目录

### 问题4：旧用户无法登录

**原因：** 只使用了bcrypt验证

**解决：** 使用双密码验证（SHA256 + bcrypt）

### 问题5：微信登录失败

**原因：** 缺少微信开放平台配置

**解决：** 设置环境变量
- `WECHAT_APP_ID`
- `WECHAT_APP_SECRET`
- `WECHAT_REDIRECT_URI`

---

## 📊 系统统计

### 代码量

- 后端：`app.py` 约 5467 行
- 前端页面：20+ 个页面组件
- 数据库表：18+ 个表
- API接口：50+ 个接口

### 用户数据

- 默认管理员：`admin / admin123`
- 默认安全设置：手机验证+单点登录（都启用）
- JWT有效期：7天

### 充值档位

- 7个档位
- 价格范围：几十到几百元
- 赠送比例：5% - 50%

---

## 🔐 安全配置

### 密码安全

- SHA256（旧系统兼容）
- bcrypt（新系统推荐）
- 双密码兼容验证

### API安全

- JWT Token认证
- CORS已配置
- 防止SQL注入（参数化查询）
- 单点登录机制
- 设备管理

### 数据安全

- 定期数据库备份
- 备份位置：`admin-backend/backups/`
- 备份文件命名：`lingzhi_ecosystem_backup_YYYYMMDD_HHMMSS.db`

---

## 📝 最近更新

### 2026-02-02

1. **修复公网IP访问500错误**
   - 添加智能API地址检测
   - 添加API配置页面
   - 添加自动化部署脚本
   - 完善部署文档

2. **修复个人资料更新不显示问题**
   - 添加 `format_user_data()` 函数
   - 统一所有用户数据接口
   - 修复TypeScript类型错误

3. **增强登录安全**
   - 添加单点登录机制
   - 添加手机验证码二次验证
   - 添加设备管理功能
   - 添加安全日志

---

## 🎓 最佳实践

### 前端开发

1. **使用TypeScript类型**：确保类型安全
2. **使用Context**：管理全局状态
3. **使用API统一接口**：`userApi`, `agentApi`等
4. **响应式设计**：Tailwind CSS + 移动优先
5. **错误处理**：try-catch + 友好提示

### 后端开发

1. **使用format_user_data()**：统一返回格式
2. **使用参数化查询**：防止SQL注入
3. **添加日志**：便于调试
4. **异常处理**：返回友好错误信息
5. **数据库迁移**：使用try-except添加新字段

### 部署运维

1. **使用自动化脚本**：`auto-deploy.sh`
2. **检查日志**：`logs/app_backend.log`
3. **定期备份**：数据库自动备份
4. **监控服务**：健康检查API
5. **防火墙配置**：开放必要端口

---

## 📞 技术支持

### 问题排查步骤

1. **查看后端日志**
   ```bash
   tail -f logs/app_backend.log
   ```

2. **检查服务状态**
   ```bash
   ps aux | grep "python app.py"
   curl http://localhost:8001/api/health
   ```

3. **查看浏览器控制台**
   - 按F12打开开发者工具
   - 查看Network标签
   - 查看Console错误

4. **使用API配置页面**
   - 访问 `/api-config`
   - 测试连接
   - 保存配置

### 文档参考

- `docs/PUBLIC_DEPLOYMENT.md` - 公网部署指南
- `docs/QUICK_FIX_500_ERROR.md` - 快速修复指南
- `docs/500_ERROR_SOLUTION.md` - 完整解决方案
- `README.md` - 项目说明

---

## 📌 关键命令速查

```bash
# 前端
cd web-app
npm install              # 安装依赖
npm run dev             # 开发服务器
npm run build           # 构建生产版本

# 后端
cd admin-backend
python app.py           # 启动后端

# 部署
./auto-deploy.sh deploy # 自动部署
./setup-public-access.sh # 公网配置
./test-public-access.sh # 测试验证

# 日志
tail -f logs/app_backend.log # 查看实时日志
tail -n 50 logs/app_backend.log # 查看最后50行

# 数据库
sqlite3 admin-backend/lingzhi_ecosystem.db # 打开数据库
```

---

## 🎯 项目核心价值

**每一次交互都是一次全方位的价值体验：**

- ✅ 文化认知（文化维度）
- ✅ 商业逻辑（商业维度）
- ✅ 情绪共鸣（情绪维度）
- ✅ 财富增长（数字资产维度）
- ✅ 科技赋能（科技维度）
- ✅ 创新实践（创新维度）

---

**文档版本：** v2.0.0
**最后更新：** 2026-02-02
**维护者：** Coze Coding
