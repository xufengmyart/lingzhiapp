# 灵值生态智能体 Web APP

灵值生态园的现代化Web应用，基于React + TypeScript + Vite构建。

**版本**: v7.3 PWA移动应用完全集成版

## ✨ 新增功能 (v7.3)

### 🎯 PWA支持
- ✅ 可安装到桌面和主屏幕
- ✅ 支持离线运行
- ✅ Service Worker自动更新
- ✅ 应用图标和启动画面

### 📱 移动应用打包
- ✅ Capacitor配置完整
- ✅ 支持Android原生应用打包
- ✅ 支持iOS原生应用打包
- ✅ 一键构建脚本

### 🌐 公网部署方案
- ✅ 一键部署脚本 (Linux/Mac/Windows)
- ✅ Docker容器化部署
- ✅ 生产环境Nginx配置
- ✅ SSL证书自动化配置
- ✅ Cloudflare/阿里云CDN支持

### 🔗 Coze平台集成
- ✅ 4种集成方案
- ✅ Coze对话组件
- ✅ API接口对接
- ✅ DeepLink深度链接
- ✅ 数据互通方案

### 🚀 快速部署

#### 一键部署脚本

**Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

**Windows:**
```batch
deploy.bat
```

#### 部署选项
1. 本地开发服务器
2. Docker容器部署
3. 生产环境部署 (Nginx)
4. 静态文件导出
5. 移动应用打包
6. 仅构建项目

## 📋 部署文档

| 文档 | 说明 |
|------|------|
| [QUICK_DEPLOY.md](./QUICK_DEPLOY.md) | 快速部署指南（推荐先看） |
| [PUBLIC_DEPLOYMENT.md](./PUBLIC_DEPLOYMENT.md) | 公网部署完整指南 |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | 详细部署文档 |
| [COZE_INTEGRATION.md](./COZE_INTEGRATION.md) | Coze平台集成方案 |

## 🚀 传统方式（仍然支持）

### 开发模式

```bash
npm install
npm run dev
```

访问: http://localhost:5173

### 生产部署

#### 方式1: 使用Node.js服务器（推荐）

```bash
# 构建项目
npm run build

# 启动生产服务器
./start-production.sh
```

访问: http://localhost:3000

#### 方式2: 使用Docker

```bash
# 构建Docker镜像
docker build -t lingzhi-ecosystem-webapp:latest .

# 运行容器
docker run -d -p 80:80 --name lingzhi-webapp lingzhi-ecosystem-webapp:latest
```

## 📦 技术栈

- **框架**: React 18.3.1
- **语言**: TypeScript 5.4.5
- **构建工具**: Vite 5.4.21
- **样式**: Tailwind CSS 3.4.3
- **路由**: React Router
- **HTTP**: Axios
- **状态管理**: React Context API
- **PWA**: vite-plugin-pwa, Workbox
- **移动应用**: Capacitor 5.x
- **容器化**: Docker, Docker Compose
- **Web服务器**: Nginx

## 📁 项目结构

```
web-app/
├── public/                     # 静态资源
│   ├── manifest.json          # PWA应用清单
│   ├── icon-*.svg             # PWA图标
│   └── favicon.ico
├── src/
│   ├── components/            # 公共组件
│   │   ├── CozeAssistant.tsx  # Coze对话组件
│   │   ├── Layout.tsx         # 布局组件
│   │   └── Navigation.tsx     # 导航组件
│   ├── contexts/              # Context上下文
│   │   └── AuthContext.tsx    # 认证上下文
│   ├── pages/                 # 页面组件
│   │   ├── ChatPage.tsx       # 智能对话
│   │   ├── EconomyPage.tsx    # 经济模型
│   │   ├── JourneyPage.tsx    # 用户旅程
│   │   ├── PartnerPage.tsx    # 合伙人管理
│   │   ├── ProfilePage.tsx    # 个人中心
│   │   ├── StatsPage.tsx      # 统计数据
│   │   └── WelcomePage.tsx    # 欢迎页
│   ├── services/              # API服务
│   │   ├── api.ts             # API接口
│   │   ├── mockApi.ts         # Mock API
│   │   └── types.ts           # TypeScript类型
│   ├── utils/                 # 工具函数
│   │   ├── calculate.ts       # 计算逻辑
│   │   └── deepLink.ts        # DeepLink处理
│   └── main.tsx               # 入口文件
├── dist/                      # 构建产物
├── production-server.js       # 生产服务器
├── nginx.conf                 # 开发环境Nginx配置
├── nginx-production.conf      # 生产环境Nginx配置
├── Dockerfile                 # Docker配置
├── docker-compose.yml         # Docker Compose配置
├── capacitor.config.ts        # Capacitor配置
├── build-mobile.bat           # 移动应用构建脚本
├── deploy.sh                  # 一键部署脚本 (Linux/Mac)
├── deploy.bat                 # 一键部署脚本 (Windows)
├── start-production.sh        # 生产启动脚本
└── docs/                      # 文档目录
    ├── QUICK_DEPLOY.md        # 快速部署指南
    ├── PUBLIC_DEPLOYMENT.md   # 公网部署指南
    ├── DEPLOYMENT.md          # 详细部署文档
    └── COZE_INTEGRATION.md    # Coze集成方案
```

## 🎯 功能模块

### 核心功能
- ✅ 用户认证（登录/注册）
- ✅ 智能对话界面
- ✅ 经济模型功能展示
- ✅ 用户旅程管理
- ✅ 合伙人管理
- ✅ 个人中心
- ✅ 统计数据可视化

### 新增功能 (v7.3)
- ✅ **PWA支持** - 可安装到桌面，支持离线运行
- ✅ **移动应用打包** - 支持Android/iOS原生应用
- ✅ **一键部署** - Linux/Mac/Windows三平台支持
- ✅ **Coze集成** - 智能体对话集成
- ✅ **公网部署** - 多种部署方案，支持SSL/CDN

## 📖 部署文档

### 🚀 快速开始（推荐新手）

**10分钟完成部署，用户即可访问！**

⭐ **[📖 10分钟快速部署 - 精简版](./QUICK_START_10MIN.md)** - 只看这个就够了！
⭐ **[📖 用户操作指南](./USER_ACTION_GUIDE.md)** - 详细步骤说明
⭐ **[📊 部署准备清单](./DEPLOYMENT_CHECKLIST.md)** - 检查系统已完成的工作

### ☁️ 云平台部署

**5分钟免费部署到公网，让用户可以访问！**

👉 **[⚡ 5分钟云部署 - 快速操作清单](./QUICK_CLOUD_DEPLOY.md)** - 最快路线
👉 **[📖 云部署 - 分步骤详细操作指南](./CLOUD_DEPLOY_STEP_BY_STEP.md)** - 每步都有说明
👉 **[📚 云部署 - 完整全景指南](./CLOUD_DEPLOYMENT_FULL_GUIDE.md)** - 了解所有方案
👉 **[📑 云部署文档中心](./CLOUD_DOCS_INDEX.md)** - 所有文档导航

### 🤖 系统自动化报告

👉 **[📊 系统自动化完成情况报告](./SYSTEM_AUTOMATION_REPORT.md)** - 查看系统已完成的工作

### 📝 部署方案对比

| 方案 | 难度 | 时间 | 费用 | 公网访问 | 文档 |
|------|------|------|------|----------|------|
| **Vercel/Netlify** ⭐ | ⭐ | 5分钟 | 免费 | ✅ | [5分钟云部署](./QUICK_CLOUD_DEPLOY.md) |
| **1. 本地开发服务器** | ⭐ | 1分钟 | 免费 | ❌ | [查看详情](./DEPLOY_LOCAL.md) |
| **3. 生产环境部署** | ⭐⭐⭐ | 15-30分钟 | ¥80-200/年 | ✅ | [查看详情](./PUBLIC_DEPLOYMENT.md) |
| **4. Docker容器部署** | ⭐⭐ | 5-10分钟 | 低成本 | ✅ | [查看详情](./DEPLOYMENT.md) |
| **5. 移动应用打包** | ⭐⭐⭐⭐⭐ | 30-60分钟 | 免费-$99/年 | ✅ | [查看详情](./DEPLOYMENT.md#移动应用打包) |

### 📚 其他文档

- [QUICK_DEPLOY.md](./QUICK_DEPLOY.md) - 快速部署指南
- [COZE_INTEGRATION.md](./COZE_INTEGRATION.md) - Coze平台集成方案
- [TIMEOUT_FIX.md](./TIMEOUT_FIX.md) - 对话超时问题排查

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

# 代码检查
npm run lint

# 启动生产服务器
./start-production.sh

# 停止生产服务器
pkill -f production-server.js

# 查看日志
tail -f /app/work/logs/bypass/web-app-production.log
```

## 🌐 访问地址

- 开发环境: http://localhost:5173
- 生产环境: http://localhost:3000

## 📞 技术支持

如有问题，请查看:
1. [DEPLOYMENT.md](./DEPLOYMENT.md) - 详细部署文档
2. 日志文件: `/app/work/logs/bypass/web-app-production.log`
3. 浏览器控制台错误信息

## 📝 版本信息

- **当前版本**: v7.3 PWA移动应用完全集成版
- **上一版本**: v7.2 双配置完全融合版
- **构建大小**: 296KB (gzip后84KB)
- **最后更新**: 2026-01-28

### 版本历史

**v7.3 (2026-01-28)**
- ✅ 添加PWA支持（可安装、离线运行）
- ✅ 配置Capacitor移动应用打包
- ✅ 创建一键部署脚本（Linux/Mac/Windows）
- ✅ 编写公网部署完整指南
- ✅ 编写Coze平台集成方案
- ✅ 优化Nginx生产环境配置
- ✅ 添加Docker Compose配置

**v7.2 (2026-01-27)**
- ✅ 双配置完全融合
- ✅ Mock API服务
- ✅ 修复AuthProvider问题
- ✅ 优化用户体验
