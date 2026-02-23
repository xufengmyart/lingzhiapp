# 灵值生态智能体 Web APP

灵值生态园的现代化Web应用，基于React + TypeScript + Vite构建。

**版本**: v9.7.0 数字文化模块集成版

## ✨ 最新功能 (v9.7.0)

### 🎨 数字文化模块
- ✅ **文化知识库页面** - 专注文化资源的展示和管理
- ✅ **文化转译工作流** - 知识库元素提取与项目关联的四步流程
- ✅ **文化项目页面** - 数字文化项目展示与参与
- ✅ **西安美学侦探** - 特色文化项目支持

### 🔧 用户知识库共享
- ✅ **用户-知识库关联** - 8个用户 × 5个系统知识库 = 40条关联记录
- ✅ **系统知识库** - 公司介绍、产品介绍、使用指南、常见问题、客服支持
- ✅ **数据持久化** - 所有数据存储在 SQLite 数据库中

### 🎨 UI/UX 优化
- ✅ **科技蓝主题** - 统一的视觉风格
- ✅ **导航栏优化** - 新增"数字文化"核心区域
- ✅ **响应式设计** - 适配各种屏幕尺寸

### 🚀 部署优化
- ✅ **Nginx配置修复** - 解决500错误，网站正常访问
- ✅ **HTTP到HTTPS重定向** - 自动跳转加密连接
- ✅ **CORS配置** - 支持跨域请求
- ✅ **防火墙配置** - 80/443端口正确开放

## 📋 功能模块

### 核心功能
- ✅ 用户认证（登录/注册）
- ✅ 智能对话界面
- ✅ 经济模型功能展示
- ✅ 用户旅程管理
- ✅ 合伙人管理
- ✅ 个人中心
- ✅ 统计数据可视化

### 数字文化模块 (新增)
- ✅ **文化知识库** - 浏览和管理文化资源
- ✅ **文化转译** - 从知识库提取元素并关联项目
- ✅ **文化项目** - 参与数字文化项目

## 📁 项目结构

```
web-app/
├── public/                     # 静态资源
│   ├── manifest.json          # PWA应用清单
│   ├── icon-*.svg             # PWA图标
│   └── favicon.ico
├── src/
│   ├── components/            # 公共组件
│   │   ├── Layout.tsx         # 布局组件
│   │   ├── Navigation.tsx     # 导航组件（含数字文化入口）
│   │   └── ...
│   ├── pages/                 # 页面组件
│   │   ├── ChatPage.tsx       # 智能对话
│   │   ├── EconomyPage.tsx    # 经济模型
│   │   ├── JourneyPage.tsx    # 用户旅程
│   │   ├── PartnerPage.tsx    # 合伙人管理
│   │   ├── ProfilePage.tsx    # 个人中心
│   │   ├── Knowledge.tsx      # 知识库管理
│   │   ├── CultureKnowledge.tsx    # 文化知识库（新增）
│   │   ├── CultureTranslation.tsx  # 文化转译（新增）
│   │   ├── CultureProjects.tsx     # 文化项目（新增）
│   │   └── ...
│   ├── contexts/              # Context上下文
│   ├── services/              # API服务
│   └── utils/                 # 工具函数
└── ...
```

## 🚀 快速开始

### 开发模式

```bash
npm install
npm run dev
```

访问: http://localhost:5173

### 生产部署

#### 构建项目

```bash
npm run build
```

构建产物将生成在 `dist/` 目录。

#### 部署到服务器

```bash
# 上传构建产物到服务器
scp -r dist/* root@123.56.142.143:/var/www/lingzhiapp/public/

# 重载Nginx
ssh root@123.56.142.143 'systemctl reload nginx'
```

访问: https://meiyueart.com

## 📦 技术栈

- **框架**: React 18.3.1
- **语言**: TypeScript 5.4.5
- **构建工具**: Vite 5.4.21
- **样式**: Tailwind CSS 3.4.3
- **路由**: React Router
- **HTTP**: Axios
- **状态管理**: React Context API

## 🌐 访问地址

- **开发环境**: http://localhost:5173
- **生产环境**: https://meiyueart.com
- **API接口**: https://meiyueart.com/api/

## 📊 数据库结构

### 用户知识库关联

```sql
CREATE TABLE user_knowledge_bases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    knowledge_base_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (knowledge_base_id) REFERENCES knowledge_bases(id),
    UNIQUE(user_id, knowledge_base_id)
);
```

**数据统计**:
- 用户数量: 8
- 知识库数量: 5
- 关联记录: 40

**系统知识库**:
1. 公司介绍
2. 产品介绍
3. 使用指南
4. 常见问题
5. 客服支持

## 📝 版本历史

**v9.7.0 (2026-02-07)**
- ✅ 添加数字文化模块（文化知识库、文化转译、文化项目）
- ✅ 实现用户知识库共享功能（40条关联记录）
- ✅ 修复Nginx配置，解决500错误
- ✅ 优化导航栏，新增"数字文化"入口
- ✅ 统一科技蓝主题

**v9.6.x (2026-01-28)**
- ✅ 添加PWA支持
- ✅ 配置Capacitor移动应用打包
- ✅ 一键部署脚本

## 📞 技术支持

如有问题，请查看:
1. Nginx配置: `/etc/nginx/sites-enabled/meiyueart.conf`
2. Flask应用: `/var/www/backend/app.py`
3. 数据库: `/var/www/backend/lingzhi_ecosystem.db`
4. 日志文件: `/var/log/nginx/error.log`

## 🔧 常用命令

```bash
# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 预览构建产物
npm run preview

# SSH连接服务器
ssh root@123.56.142.143

# 查看Nginx状态
systemctl status nginx

# 重载Nginx
systemctl reload nginx

# 查看Flask服务状态
ps aux | grep python

# 查看数据库
sqlite3 /var/www/backend/lingzhi_ecosystem.db
```
