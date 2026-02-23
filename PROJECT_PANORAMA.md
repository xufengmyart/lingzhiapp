# 灵值生态园智能体系统 - 全景学习文档

**文档生成时间**: 2026年2月18日 23:30
**学习目的**: 为明天无缝工作做好基础，避免上下文限制造成的断章取义

---

## 🏗️ 一、系统架构概览

### 1.1 项目信息
- **项目名称**: 灵值生态园智能体系统
- **当前版本**: V9.24.0
- **项目类型**: React前端 + Flask/FastAPI后端
- **部署地址**: https://meiyueart.com
- **生产服务器**: 123.56.142.143 (阿里云ECS)
- **工作目录**: /workspace/projects

### 1.2 技术栈

#### 前端技术栈
```
框架: React 18.3.1
语言: TypeScript 5.4.5
构建工具: Vite 5.4.21
样式: Tailwind CSS 3.4.3
路由: React Router 6.22.3
状态管理: Context API
图标: Lucide React
动画: Framer Motion
```

#### 后端技术栈
```
框架: Python Flask
认证: JWT (PyJWT 2.8.0)
密码加密: bcrypt (统一使用)
数据库: SQLite (生产环境) / PostgreSQL (备选)
CORS: Flask-CORS 4.0.0
日志: 自定义日志系统
大模型: doubao-seed-1-6-251015
```

#### 部署技术栈
```
Web服务器: Nginx
进程管理: nohup + 后台运行
端口配置:
  - Nginx: 80/443
  - Flask后端: 5000 (默认) / 8080 (配置)
  - React前端: 通过Nginx托管
```

---

## 📂 二、项目目录结构

### 2.1 根目录结构
```
/workspace/projects/
├── admin-backend/          # 后端代码
├── web-app/                # 前端代码
├── config/                 # 配置文件
├── scripts/                # 脚本工具
├── docs/                   # 文档
├── assets/                 # 资源文件
├── tests/                  # 测试文件
├── deploy_one_click.sh     # 一键部署脚本
├── .env                    # 环境变量
├── .env.example            # 环境变量示例
├── .env.production         # 生产环境配置
└── PROJECT_PANORAMA.md     # 本文档
```

### 2.2 后端目录结构 (admin-backend/)
```
admin-backend/
├── app.py                  # 主应用入口
├── config.py               # 配置管理模块
├── database.py             # 数据库连接和工具函数
├── logger.py               # 日志系统
├── main.py                 # 备用入口
├── requirements.txt        # Python依赖
├── .env                    # 后端环境变量
├── database.db             # 本地SQLite数据库（临时）
├── data/
│   └── lingzhi_ecosystem.db  # 生产数据库
├── routes/                 # API路由模块
│   ├── admin.py            # 管理员功能
│   ├── agent.py            # 智能体对话
│   ├── auth.py             # 用户认证
│   ├── checkin.py          # 签到系统
│   ├── recharge.py         # 充值系统
│   ├── feedback.py         # 反馈功能
│   ├── user_profile.py     # 用户资料
│   └── ...                 # 其他路由
├── middleware/             # 中间件
│   ├── jwt_auth.py         # JWT认证中间件
│   ├── error_handler.py    # 错误处理中间件
│   ├── request_logger.py   # 请求日志中间件
│   └── response_converter.py  # 响应转换中间件
└── scripts/                # 后端脚本
```

### 2.3 前端目录结构 (web-app/)
```
web-app/
├── src/
│   ├── main.tsx            # 应用入口
│   ├── App.tsx             # 路由配置
│   ├── components/         # 组件
│   │   ├── Layout.tsx      # 布局组件
│   │   ├── Navigation.tsx  # 导航栏
│   │   ├── ErrorBoundary.tsx  # 错误边界
│   │   ├── ProtectedRoute.tsx  # 路由守卫
│   │   └── ...             # 其他组件
│   ├── contexts/           # Context状态管理
│   │   ├── AuthContext.tsx # 认证状态
│   │   ├── ChatContext.tsx # 对话状态
│   │   └── ...             # 其他Context
│   ├── pages/              # 页面组件
│   │   ├── LoginFull.tsx   # 登录页
│   │   ├── RegisterManual.tsx  # 注册页
│   │   ├── Chat.tsx        # 对话页
│   │   ├── Dashboard.tsx   # 仪表盘
│   │   ├── AdminLogin.tsx  # 管理员登录
│   │   ├── AdminDashboard.tsx  # 管理员仪表盘
│   │   └── ...             # 其他页面
│   └── hooks/              # 自定义Hook
├── public/                 # 静态资源
├── dist/                   # 构建输出
├── package.json            # 前端依赖
├── vite.config.ts          # Vite配置
├── tsconfig.json           # TypeScript配置
└── .env.production         # 生产环境变量
```

---

## 🗄️ 三、数据库结构

### 3.1 数据库配置
- **类型**: SQLite
- **生产数据库路径**: `/app/meiyueart-backend/lingzhi_ecosystem.db`
- **开发数据库路径**: `admin-backend/data/lingzhi_ecosystem.db`
- **表数量**: 28个表

### 3.2 核心数据表

#### 用户相关 (3个表)
```sql
-- users: 用户基本信息 (22个字段)
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50),
    email VARCHAR(100),
    phone VARCHAR(20),
    password_hash VARCHAR(255),
    total_lingzhi INTEGER,
    status VARCHAR(20),
    last_login_at DATETIME,
    avatar_url VARCHAR(500),
    real_name VARCHAR(50),
    is_verified BOOLEAN,
    login_type VARCHAR(20),
    wechat_openid VARCHAR(100),
    wechat_unionid VARCHAR(100),
    wechat_nickname VARCHAR(100),
    wechat_avatar VARCHAR(500),
    referrer_id INTEGER,
    location VARCHAR(200),
    bio TEXT,
    website VARCHAR(200),
    created_at DATETIME,
    updated_at DATETIME
);

-- user_profiles: 用户详细资料 (13个字段)
CREATE TABLE user_profiles (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    real_name VARCHAR(50),
    phone VARCHAR(20),
    email VARCHAR(100),
    id_card VARCHAR(20),
    bank_account VARCHAR(50),
    bank_name VARCHAR(100),
    address VARCHAR(500),
    is_completed BOOLEAN,
    completed_at DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);

-- admins: 管理员账户 (5个字段)
CREATE TABLE admins (
    id INTEGER PRIMARY KEY,
    username VARCHAR(50) UNIQUE,
    password_hash VARCHAR(255),
    role VARCHAR(20),
    created_at DATETIME
);
```

#### 业务功能 (5个表)
```sql
-- conversations: 对话历史 (8个字段)
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY,
    agent_id INTEGER,
    user_id INTEGER,
    conversation_id VARCHAR(100),
    messages TEXT,  -- JSON格式存储
    title VARCHAR(200),
    created_at DATETIME,
    updated_at DATETIME
);

-- agents: 智能体配置 (11个字段)
CREATE TABLE agents (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    system_prompt TEXT,
    model_config TEXT,  -- JSON格式
    tools TEXT,  -- JSON格式
    status VARCHAR(20),
    avatar_url VARCHAR(500),
    created_by INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);

-- feedback: 用户反馈 (10个字段)
CREATE TABLE feedback (
    id INTEGER PRIMARY KEY,
    conversation_id INTEGER,
    agent_id INTEGER,
    user_id INTEGER,
    type VARCHAR(50),
    rating INTEGER,
    question TEXT,
    comment TEXT,
    contribution_value INTEGER,
    created_at DATETIME
);

-- checkin_records: 签到记录 (5个字段)
CREATE TABLE checkin_records (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    checkin_date DATE,
    lingzhi_earned INTEGER,
    created_at DATETIME
);

-- recharge_records: 充值记录 (17个字段)
CREATE TABLE recharge_records (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    tier_id INTEGER,
    order_no VARCHAR(100),
    amount NUMERIC(10, 2),
    base_lingzhi INTEGER,
    bonus_lingzhi INTEGER,
    total_lingzhi INTEGER,
    payment_method VARCHAR(20),
    payment_status VARCHAR(20),
    payment_time DATETIME,
    transaction_id VARCHAR(100),
    voucher_id INTEGER,
    audit_status VARCHAR(20),
    bank_info TEXT,
    status VARCHAR(20),
    created_at DATETIME
);
```

#### 内容管理 (3个表)
```sql
-- knowledge_bases: 知识库 (8个字段)
CREATE TABLE knowledge_bases (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    vector_db_id VARCHAR(100),
    document_count INTEGER,
    created_by INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);

-- knowledge_documents: 知识库文档 (11个字段)
CREATE TABLE knowledge_documents (
    id INTEGER PRIMARY KEY,
    knowledge_base_id INTEGER,
    title VARCHAR(200),
    content TEXT,
    file_path VARCHAR(500),
    file_type VARCHAR(50),
    file_size INTEGER,
    embedding_status VARCHAR(20),
    embedding_error TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- company_news: 公司动态 (12个字段)
CREATE TABLE company_news (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    content TEXT,
    author_id INTEGER,
    status VARCHAR(20),
    view_count INTEGER,
    like_count INTEGER,
    cover_image_url VARCHAR(500),
    tags TEXT,  -- JSON格式
    created_at DATETIME,
    updated_at DATETIME
);
```

#### 财务相关 (4个表)
```sql
-- recharge_tiers: 充值档位 (13个字段)
CREATE TABLE recharge_tiers (
    id INTEGER PRIMARY KEY,
    name VARCHAR(100),
    description TEXT,
    price NUMERIC(10, 2),
    base_lingzhi INTEGER,
    bonus_lingzhi INTEGER,
    bonus_percentage INTEGER,
    partner_level INTEGER,
    benefits TEXT,
    status VARCHAR(20),
    sort_order INTEGER,
    created_at DATETIME,
    updated_at DATETIME
);

-- transfer_vouchers: 转账凭证 (14个字段)
CREATE TABLE transfer_vouchers (
    id INTEGER PRIMARY KEY,
    recharge_record_id INTEGER,
    user_id INTEGER,
    image_url VARCHAR(500),
    transfer_amount NUMERIC(10, 2),
    transfer_time DATETIME,
    transfer_account VARCHAR(200),
    remark TEXT,
    audit_status VARCHAR(20),
    audit_user_id INTEGER,
    audit_time DATETIME,
    audit_remark TEXT,
    created_at DATETIME,
    updated_at DATETIME
);

-- referral_codes: 推荐码 (7个字段)
CREATE TABLE referral_codes (
    id INTEGER PRIMARY KEY,
    referrer_id INTEGER,
    code TEXT,
    status TEXT,
    expires_at TIMESTAMP,
    used_count INTEGER,
    created_at TIMESTAMP
);

-- referral_commissions: 推荐佣金 (12个字段)
CREATE TABLE referral_commissions (
    id INTEGER PRIMARY KEY,
    referrer_id INTEGER,
    referee_id INTEGER,
    level INTEGER,
    transaction_id INTEGER,
    transaction_type VARCHAR(50),
    original_amount NUMERIC(10, 2),
    commission_rate NUMERIC(5, 4),
    commission_amount NUMERIC(10, 2),
    status VARCHAR(20),
    settled_at DATETIME,
    created_at DATETIME
);
```

#### 资产相关 (5个表)
```sql
-- digital_assets: 数字资产 (11个字段)
CREATE TABLE digital_assets (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    asset_type VARCHAR(50),
    asset_name VARCHAR(200),
    description TEXT,
    image_url VARCHAR(500),
    asset_metadata TEXT,  -- JSON格式
    rarity VARCHAR(20),
    value NUMERIC(10, 2),
    is_transferable BOOLEAN,
    created_at DATETIME
);

-- user_resources: 用户资源 (11个字段)
CREATE TABLE user_resources (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    resource_type VARCHAR(50),
    resource_name VARCHAR(200),
    description TEXT,
    availability VARCHAR(20),
    estimated_value NUMERIC(10, 2),
    status VARCHAR(20),
    tags TEXT,  -- JSON格式
    created_at DATETIME,
    updated_at DATETIME
);

-- projects: 项目 (14个字段)
CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    title VARCHAR(200),
    description TEXT,
    project_type VARCHAR(50),
    budget NUMERIC(10, 2),
    required_skills TEXT,  -- JSON格式
    required_assets TEXT,  -- JSON格式
    duration INTEGER,
    location VARCHAR(200),
    status VARCHAR(20),
    creator_id INTEGER,
    deadline DATETIME,
    created_at DATETIME,
    updated_at DATETIME
);

-- project_participants: 项目参与者 (9个字段)
CREATE TABLE project_participants (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    user_id INTEGER,
    role VARCHAR(50),
    contribution TEXT,
    reward NUMERIC(10, 2),
    reward_status VARCHAR(20),
    joined_at DATETIME,
    completed_at DATETIME
);

-- resource_matches: 资源匹配 (10个字段)
CREATE TABLE resource_matches (
    id INTEGER PRIMARY KEY,
    project_id INTEGER,
    user_id INTEGER,
    resource_id INTEGER,
    match_score NUMERIC(5, 4),
    match_reason TEXT,
    status VARCHAR(20),
    user_response TEXT,
    response_at DATETIME,
    created_at DATETIME
);
```

#### 其他 (8个表)
```sql
-- lingzhi_consumption_records: 灵值消耗记录 (8个字段)
-- user_benefits: 用户权益 (8个字段)
-- agent_knowledge_bases: 智能体-知识库关联 (4个字段)
-- asset_transactions: 资产交易 (10个字段)
-- asset_earnings: 资产收益 (8个字段)
-- company_accounts: 公司账户 (12个字段)
-- sessions: 会话 (7个字段)
-- referral_relationships: 推荐关系 (6个字段)
```

---

## 🔌 四、API路由结构

### 4.1 后端API路由清单

#### 认证系统 (auth_bp)
```
POST /api/login              # 用户登录
POST /api/register           # 用户注册
POST /api/send-code          # 发送验证码
POST /api/verify-code        # 验证验证码
POST /api/reset-password     # 重置密码
GET  /api/verify-user        # 验证用户
POST /api/wechat/login       # 微信登录
GET  /api/wechat/callback    # 微信回调
```

#### 管理员功能 (admin_bp)
```
POST /api/admin/login                # 管理员登录
GET  /api/admin/users                # 获取用户列表
POST /api/admin/users                # 创建用户
PUT  /api/admin/users/<id>           # 更新用户
PUT  /api/admin/users/<id>/status    # 更新用户状态
PUT  /api/admin/users/<id>/lingzhi   # 修改灵值
GET  /api/admin/users/export         # 导出用户
GET  /api/admin/agents               # 获取智能体列表
GET  /api/admin/stats                # 获取统计数据
PUT  /api/admin/vouchers/<id>/audit  # 审核充值凭证
```

#### 智能体对话 (agent_bp)
```
POST /api/agent/chat              # 智能体对话
GET  /api/agent/conversations/<id> # 获取对话历史
GET  /api/agents                  # 获取智能体列表
POST /api/feedback                # 提交反馈
```

#### 签到系统 (checkin_bp)
```
POST /api/checkin          # 签到
GET  /api/checkin/status   # 签到状态
```

#### 充值系统 (recharge_bp)
```
GET  /api/recharge/tiers               # 获取充值档位
POST /api/recharge/create-order        # 创建订单
POST /api/recharge/upload-voucher      # 上传转账凭证
POST /api/recharge/complete-payment    # 完成支付
GET  /api/recharge/records             # 充值记录
```

#### 反馈功能 (feedback_bp)
```
POST /api/feedback           # 提交反馈
GET  /api/feedback/list      # 反馈列表
```

#### 用户资料 (user_profile_bp)
```
GET  /api/user/profile       # 获取用户资料
PUT  /api/user/profile       # 更新用户资料
GET  /api/user/info          # 获取用户信息
```

#### 推荐系统 (referral_bp)
```
GET  /api/referral/code      # 获取推荐码
POST /api/referral/use       # 使用推荐码
GET  /api/referral/stats     # 推荐统计
```

#### 其他功能
```
GET  /api/health             # 健康检查
GET  /api/stats              # 获取统计数据
GET  /api/news               # 公司动态
GET  /api/knowledge-bases    # 知识库列表
POST /api/company/accounts   # 公司账户
```

### 4.2 前端路由结构

#### 公共路由
```
/                           # 登录页
/login-full                 # 登录页（完整版）
/register                   # 注册页
/forgot-password            # 忘记密码
/admin/login                # 管理员登录
/api-config                 # API配置
/wechat/callback            # 微信回调
/referral                   # 推荐页
```

#### 用户路由（需要登录）
```
/dashboard                  # 仪表盘
/chat                       # 智能体对话
/knowledge                  # 知识库
/economy                    # 经济系统
/partner                    # 合作伙伴
/guide                      # 用户指南
/value-guide                # 灵值指南
/medium-video               # 视频项目
/xian-aesthetics            # 仙人美学
/profile                    # 个人资料
/security                   # 安全设置
/recharge                   # 充值
/feedback                   # 反馈
/user-resources             # 用户资源
/project-pool               # 项目池
/merchant-pool              # 商家池
/merchant-detail/:id        # 商家详情
/aesthetic-tasks            # 美学任务
/digital-assets             # 数字资产
/docs                       # 文档
/bounty-hunter              # 赏金猎人
/culture-translation        # 文化翻译
/culture-projects           # 文化项目
/company-news               # 公司动态
/company-projects           # 公司项目
/company-info               # 公司信息
/company-users              # 公司用户
/company-knowledge          # 公司知识
/referral                   # 推荐网络
/dividend-pool              # 分红池
/journey                    # 用户旅程
/assets                     # 资产
/user-learning              # 用户学习
/merchant-workbench         # 商家工作台
/expert-workbench           # 专家工作台
/analytics-dashboard        # 分析仪表盘
/user-resources-market      # 用户资源市场
```

#### 管理员路由（需要管理员登录）
```
/admin                      # 管理员仪表盘
/admin/agents               # 智能体管理
/admin/knowledge            # 知识库管理
/admin/users                # 用户管理
/admin/profile-edit         # 用户资料编辑
/admin/contribution         # 贡献管理
/admin/roles                # 角色管理
/admin/user-types           # 用户类型管理
/admin/assets               # 资产管理
/admin/projects             # 项目管理
/admin/merchants            # 商家管理
/admin/aesthetic-tasks      # 美学任务管理
/admin/digital-assets       # 数字资产管理
/admin/sacred-sites         # 圣地管理
/admin/cultural-projects    # 文化项目管理
/analytics-dashboard        # 分析仪表盘
```

---

## 🔐 五、认证与安全

### 5.1 密码加密方式
- **统一算法**: bcrypt
- **哈希长度**: 60字符
- **默认密码**: 123（测试账号）

### 5.2 JWT认证
```python
# JWT配置
JWT_SECRET_KEY = "gyXB-7pi2Lc3jXSdvK3_fUJNs0VS4hBP6L4ncBXLVE3iME8pkpPsA4KhppwQbK0_fX4"
JWT_EXPIRATION = 604800  # 7天
JWT_ALGORITHM = 'HS256'

# Token生成
def generate_token(admin_id, username, role):
    payload = {
        'admin_id': admin_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
```

### 5.3 测试账号

#### 管理员账号
| 用户名 | 密码 | ID | 备注 |
|--------|------|----|----|
| admin | admin123 | 1 | 默认管理员 |

#### 用户账号
| 用户名 | 密码 | ID | 备注 |
|--------|------|----|----|
| 许锋 | 123 | 1 | 普通用户 |
| 马伟娟 | 123 | 19 | 普通用户 |
| admin | 123456 | 10 | 管理员账号（双重角色） |

---

## 🚀 六、部署流程

### 6.1 生产环境配置
```yaml
服务器信息:
  地址: meiyueart.com
  IP: 123.56.142.143
  SSH用户: root
  SSH密码: Meiyue@root123
  SSH端口: 22

后端服务:
  路径: /app/meiyueart-backend
  启动文件: app.py
  运行方式: python3 app.py
  运行端口: 5000 (默认) / 8080 (配置)
  虚拟环境: /app/meiyueart-backend/venv
  日志文件: /var/log/meiyueart-backend/app.log

数据库:
  类型: SQLite
  文件: /app/meiyueart-backend/lingzhi_ecosystem.db

Nginx:
  配置文件: /etc/nginx/sites-available/meiyueart-https.conf
  代理端口: 5000
  API路径: /api
```

### 6.2 一键部署脚本
```bash
# 部署脚本路径
./deploy_one_click.sh

# 部署流程
1. 清理云服务器垃圾
2. 备份生产环境
3. 上传后端代码
4. 同步数据库
5. 更新Nginx配置并重启后端服务
6. 验证部署
```

### 6.3 常用命令

#### 查看服务状态
```bash
# 查看后端服务
ssh root@meiyueart.com "ps aux | grep 'python.*app.py' | grep -v grep"

# 查看后端日志
ssh root@meiyueart.com "tail -f /var/log/meiyueart-backend/app.log"

# 重启后端服务
ssh root@meiyueart.com "cd /app/meiyueart-backend && pkill -9 -f 'python.*app.py' && sleep 2 && source venv/bin/activate && nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &"
```

#### 测试API
```bash
# 健康检查
curl https://meiyueart.com/api/health

# 管理员登录
curl -X POST https://meiyueart.com/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 用户登录
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"马伟娟","password":"123"}'

# 提交反馈
curl -X POST https://meiyueart.com/api/feedback \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -H "X-User-ID: 1037" \
  -d '{"type":"helpful","question":"测试反馈","agent_id":1}'
```

---

## 📝 七、最近修复记录

### 7.1 反馈功能修复 (2026-02-18 22:50)
**问题**:
- 提交反馈失败，前端显示"提交失败"
- 后端返回404错误
- 用户无法获得灵值奖励

**原因**:
1. 后端代码存在重复代码，导致feedback函数定义不完整
2. 前端API路径错误（`/api/agent/feedback`应为`/api/feedback`）
3. 前端环境变量缺失（`VITE_API_URL`未定义）

**修复**:
1. 删除`admin-backend/routes/agent.py`第671-690行的重复代码
2. 修改前端API路径为`/feedback`
3. 添加环境变量`VITE_API_URL=/api`

### 7.2 管理员登录功能修复 (2026-02-18 23:20)
**问题**:
- 管理员登录失败
- 前端无法获取token
- 后端缺少JWT token生成逻辑

**原因**:
1. 数据库缺少`admins`表
2. 登录路由没有生成和返回JWT token

**修复**:
1. 创建`admins`表
2. 添加默认管理员账号`admin/admin123`
3. 添加`generate_token()`和`verify_token()`函数
4. 修改登录路由，返回token和admin信息

### 7.3 生产环境清理 (2026-02-18 23:00)
**清理内容**:
- 删除所有旧版本备份文件（约535 MB）
- 清理后端备份文件（约2.5 MB）
- 清理临时文件（约350 MB）
- 清理日志文件（保留最新）
- 清理Python缓存

**总计节省**: 约887.5 MB

---

## ⚙️ 八、关键配置文件

### 8.1 后端环境变量 (.env)
```bash
# 基础配置
FLASK_APP=app
FLASK_ENV=production
DEBUG=False

# JWT配置
SECRET_KEY=nv4wNeBNbJKGdjW17tyKMtriAlk7_5zE1Dnt-YUcTXB4zn7oKE13uvIL2AyNYzoQa44
JWT_SECRET_KEY=gyXB-7pi2Lc3jXSdvK3_fUJNs0VS4hBP6L4ncBXLVE3iME8pkpPsA4KhppwQbK0_fX4
JWT_EXPIRATION=604800

# 数据库配置
DATABASE_PATH=/workspace/projects/admin-backend/data/lingzhi_ecosystem.db

# 服务器配置
HOST=0.0.0.0
PORT=8080
SERVER_NAME=meiyueart.com

# Coze大模型配置
COZE_WORKLOAD_IDENTITY_API_KEY=WU9RNGFQTmZTc3VnbnRCMmsyWUtDcDZHOWJMa0g5ZVk6NVN5cHNRbkNidjFzWHNEVnJ4UTZKQlN1SUxYMlU3ZEtidVRXbDYwWDFyZW9sdmhQbTU1QVdQaVJHcVo4b1BoWA==
COZE_INTEGRATION_MODEL_BASE_URL=https://integration.coze.cn/api/v3
COZE_INTEGRATION_BASE_URL=https://integration.coze.cn
COZE_PROJECT_ID=7597768668038643746

# 微信配置
WECHAT_APP_ID=your-wechat-app-id
WECHAT_APP_SECRET=your-wechat-app-secret
WECHAT_REDIRECT_URI=https://meiyueart.com/wechat/callback

# 公司信息
COMPANY_NAME=灵值生态园科技有限公司
COMPANY_CREDIT_CODE=your-company-credit-code
COMPANY_ACCOUNT_NAME=your-account-name
COMPANY_ACCOUNT_NUMBER=your-account-number
COMPANY_BANK_NAME=your-bank-name
COMPANY_BANK_BRANCH=your-bank-branch

# 文件上传配置
UPLOAD_FOLDER=/workspace/projects/admin-backend/uploads
MAX_CONTENT_LENGTH=16777216
ALLOWED_EXTENSIONS=png,jpg,jpeg,gif,pdf,doc,docx

# CORS配置
CORS_ORIGINS=https://meiyueart.com,http://meiyueart.com
CORS_METHODS=GET,POST,PUT,DELETE,OPTIONS
CORS_ALLOW_HEADERS=Content-Type,Authorization

# 日志配置
LOG_DIR=/workspace/projects/admin-backend/logs
LOG_LEVEL=INFO

# 备份配置
BACKUP_ENABLED=True
BACKUP_RETENTION_DAYS=30
BACKUP_SCHEDULE=0 2 * * *

# 其他配置
ENV=production
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=True
SENTRY_DSN=
ENABLE_ERROR_TRACKING=False
```

### 8.2 前端环境变量 (.env.production)
```bash
# API服务地址配置 - 使用相对路径
# 通过 Nginx 反向代理到后端服务
VITE_API_URL=/api
VITE_API_BASE_URL=/api
```

---

## 🎯 九、核心业务逻辑

### 9.1 灵值计费系统
- **计费规则**: 每5分钟消耗1灵值
- **反馈奖励**:
  - helpful（有帮助）: 10 灵值
  - not_helpful（无帮助）: 5 灵值
  - suggestion（建议）: 15 灵值
- **签到奖励**: 每日签到获得灵值奖励

### 9.2 智能体对话系统
- **大模型**: doubao-seed-1-6-251015
- **对话存储**: `conversations`表的`messages`字段（JSON格式）
- **对话记忆**: 使用滑动窗口保留最近20轮对话
- **反馈机制**: 支持三种反馈类型，记录到`feedback`表

### 9.3 充值系统
- **充值档位**: `recharge_tiers`表定义不同档位
- **支付方式**: 银行转账
- **审核流程**: 上传转账凭证 -> 管理员审核 -> 充值成功
- **充值记录**: `recharge_records`表记录所有充值记录

---

## 🚨 十、已知问题和注意事项

### 10.1 端口配置问题
- **问题描述**: Nginx配置中的代理端口不一致
- **当前状态**: 部署脚本使用5000端口
- **配置文件**: 端口8080
- **建议**: 统一使用5000端口

### 10.2 数据库同步
- **问题**: 本地数据库和生产数据库需要手动同步
- **解决**: 部署脚本会自动同步`admin-backend/data/lingzhi_ecosystem.db`

### 10.3 密码哈希兼容性
- **问题**: 存在多种密码哈希格式（bcrypt、scrypt、sha256）
- **解决**: 统一使用bcrypt哈希
- **注意**: 旧数据需要迁移

### 10.4 前端环境变量
- **问题**: 前端使用`VITE_API_URL`，但部分地方使用`VITE_API_BASE_URL`
- **解决**: 统一使用`VITE_API_URL=/api`

---

## 📚 十一、重要文档清单

### 核心文档
- `README.md` - 项目总体说明
- `WORK_PRINCIPLES.md` - 工作原则
- `PROJECT_PANORAMA.md` - 本文档（全景学习）

### 部署文档
- `PRODUCTION_CONFIG_FINAL.md` - 生产环境配置
- `admin-backend/DEPLOYMENT_GUIDE.md` - 部署指南
- `admin-backend/PRODUCTION_CONFIG.md` - 生产环境配置

### 修复报告
- `admin-backend/data/feedback_fix_report.md` - 反馈功能修复
- `admin-backend/data/cleanup_and_fix_report.md` - 清理与修复
- `COMPREHENSIVE_API_FIX_REPORT.md` - API综合修复
- `COMPREHENSIVE_FIX_REPORT.md` - 综合修复

### 技术文档
- `docs/COMPLETE_SOLUTION_SUMMARY.md` - 完整解决方案
- `docs/COMPREHENSIVE_SYSTEM_ANALYSIS_REPORT.md` - 系统分析
- `docs/API_DOCUMENTATION.md` - API文档
- `docs/DATABASE_STANDARDS.md` - 数据库规范

---

## 🔍 十二、快速定位指南

### 12.1 查找用户信息
```bash
# 查询用户
cd admin-backend && python3 -c "
import sqlite3
conn = sqlite3.connect('data/lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute('SELECT id, username, total_lingzhi, status FROM users')
for row in cursor.fetchall():
    print(row)
conn.close()
"
```

### 12.2 查看API路由
```bash
# 查看所有注册的蓝图
cd admin-backend && grep -n "app.register_blueprint" app.py

# 查看特定蓝图的路由
cd admin-backend && grep -n "@.*_bp.route" routes/*.py
```

### 12.3 查看数据库表结构
```bash
# 查看所有表
cd admin-backend && python3 -c "
import sqlite3
conn = sqlite3.connect('data/lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\")
for table in cursor.fetchall():
    print(table[0])
conn.close()
"

# 查看表结构
cd admin-backend && python3 -c "
import sqlite3
conn = sqlite3.connect('data/lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute('PRAGMA table_info(users)')
for col in cursor.fetchall():
    print(col)
conn.close()
"
```

### 12.4 查看日志
```bash
# 查看后端日志
tail -n 50 admin-backend/backend.log

# 查看生产服务器日志
ssh root@meiyueart.com "tail -n 50 /var/log/meiyueart-backend/app.log"
```

---

## 💡 十三、工作原则（归档）

### 原则一：确定性优先
- **核心要求**: 所有技术选择只使用一种确定格式
- **禁止行为**: 不做算法检测、格式自动识别等复杂逻辑
- **必须行为**: 统一使用一种技术方案

### 原则二：默认第一环境为生产环境
- **核心要求**: 所有操作默认在生产环境执行
- **操作规范**: 直接连接生产服务器，不在测试环境浪费时间

### 原则三：全流程自主执行
- **核心要求**: 所有过程由AI自主完成
- **执行流程**: 读取需求 -> 自主分析 -> 自主执行 -> 返回结果 -> 归档记录
- **禁止行为**: 不给用户操作指令，不展示过程

---

## 📊 十四、系统状态总结

### 当前版本
- **前端**: V9.24.0
- **后端**: V9.24.0
- **部署状态**: 正常运行

### 功能完整性
- ✅ 用户认证系统
- ✅ 智能体对话系统
- ✅ 灵值计费系统
- ✅ 反馈功能
- ✅ 签到系统
- ✅ 充值系统
- ✅ 推荐系统
- ✅ 管理员后台
- ⚠️ 知识库系统（未使用）
- ⚠️ 数字资产系统（待完善）

### 数据完整性
- ✅ users表（7个用户）
- ✅ conversations表（52条记录）
- ✅ checkin_records表（4条记录）
- ✅ agents表（2个智能体）
- ⚠️ knowledge_bases表（未使用）
- ⚠️ recharge_records表（无数据）

### 部署健康度
- ✅ 前端服务正常
- ✅ 后端服务正常
- ✅ 数据库连接正常
- ✅ API调用正常
- ✅ 管理员登录正常
- ✅ 用户登录正常

---

## 🎓 十五、明天无缝工作指南

### 15.1 快速开始
1. **进入工作目录**: `cd /workspace/projects`
2. **查看本全景文档**: `cat PROJECT_PANORAMA.md`
3. **检查服务状态**: `./deploy_one_click.sh`（最后一步验证）
4. **开始工作**: 根据需求进行开发或修复

### 15.2 常用命令速查
```bash
# 部署到生产环境
./deploy_one_click.sh

# 查看数据库
cd admin-backend && python3 -c "import sqlite3; conn = sqlite3.connect('data/lingzhi_ecosystem.db'); cursor = conn.cursor(); cursor.execute('SELECT * FROM users'); print(cursor.fetchall())"

# 查看后端日志
tail -f admin-backend/backend.log

# 启动后端服务（本地）
cd admin-backend && python3 app.py

# 构建前端
cd web-app && npm run build

# 测试API
curl -X POST https://meiyueart.com/api/admin/login -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'
```

### 15.3 问题定位流程
1. **查看日志**: `tail -n 50 admin-backend/backend.log`
2. **检查API**: 使用curl测试相关API
3. **查看数据库**: 检查相关表的数据
4. **查看代码**: 定位问题代码并修复
5. **重新部署**: `./deploy_one_click.sh`
6. **验证修复**: 在生产环境测试

### 15.4 关键文件快速定位
- **主入口**: `admin-backend/app.py`
- **配置**: `admin-backend/config.py`
- **数据库**: `admin-backend/database.py`
- **路由**: `admin-backend/routes/*.py`
- **前端路由**: `web-app/src/App.tsx`
- **对话页**: `web-app/src/pages/Chat.tsx`
- **管理员登录**: `web-app/src/pages/AdminLogin.tsx`
- **数据库**: `admin-backend/data/lingzhi_ecosystem.db`

---

## ✅ 总结

本文档记录了灵值生态园智能体系统的完整全景，包括：
1. 系统架构和技术栈
2. 项目目录结构
3. 数据库结构（28个表）
4. API路由清单
5. 前端路由结构
6. 认证与安全配置
7. 部署流程
8. 最近修复记录
9. 关键配置文件
10. 核心业务逻辑
11. 已知问题
12. 重要文档清单
13. 快速定位指南
14. 系统状态总结
15. 明天无缝工作指南

**文档维护**: 每次重要更新后更新本文档
**文档版本**: V1.0
**最后更新**: 2026年2月18日 23:30

---

**全景学习完成！明天可以直接开始工作。**
