# 🚀 灵值生态园APP - 一键部署完整指南

**从零到上线，5分钟搞定！**

---

## 📖 目录

1. [快速开始](#快速开始)
2. [部署方案选择](#部署方案选择)
3. [详细部署步骤](#详细部署步骤)
4. [常见问题](#常见问题)
5. [最佳实践](#最佳实践)

---

## 🎯 快速开始

### 3分钟快速部署（推荐）

**如果你想要立即看到效果**：
1. 阅读 [环境准备检查](./SETUP_CHECK.md)
2. 选择 [部署方案](#部署方案选择)
3. 按照对应文档操作

**新手推荐路线**:
1. 先本地测试（1分钟）→ [本地开发服务器](./DEPLOY_LOCAL.md)
2. 再部署到公网（5分钟）→ [免费云托管](./DEPLOY_CLOUD.md)

---

## 🎨 部署方案选择

### 方案对比

| 方案 | 时间 | 难度 | 费用 | 推荐度 | 说明 |
|------|------|------|------|--------|------|
| **1. 本地开发服务器** | 1分钟 | ⭐ | 免费 | ⭐⭐⭐⭐⭐ | 最快，只在本机访问 |
| **2. 免费云托管** | 5分钟 | ⭐ | 免费 | ⭐⭐⭐⭐⭐ | 最推荐，公网访问，自动HTTPS |
| **3. 生产环境部署** | 15-30分钟 | ⭐⭐⭐ | 低成本 | ⭐⭐⭐⭐⭐ | 企业级，完全控制 |
| **4. Docker容器部署** | 5-10分钟 | ⭐⭐ | 低成本 | ⭐⭐⭐⭐ | 容器化，易于迁移 |
| **5. 移动应用打包** | 30-60分钟 | ⭐⭐⭐⭐⭐ | 免费 | ⭐⭐⭐⭐ | 原生应用，上架应用商店 |
| **6. 静态文件导出** | 3分钟 | ⭐⭐ | 任意 | ⭐⭐⭐ | 自定义部署 |

### 快速决策

```
我只想快速看看效果？
→ 方案1：本地开发服务器

我想要公网访问，不想花钱？
→ 方案2：免费云托管（Vercel/Netlify）

我有服务器，想要稳定生产环境？
→ 方案3：生产环境部署（Nginx）

我想要移动应用？
→ 方案5：移动应用打包

我需要自定义部署？
→ 方案6：静态文件导出
```

---

## 📝 详细部署步骤

### 方案1：本地开发服务器（1分钟）

**适用场景**: 快速测试、开发、演示

**详细步骤**: [点击查看](./DEPLOY_LOCAL.md)

**快速命令**:
```bash
cd /workspace/projects/web-app
npm install
npm run dev
```

访问: http://localhost:5173

---

### 方案2：免费云托管（5分钟）⭐推荐

**适用场景**: 个人项目、快速上线、完全免费

**详细步骤**: [点击查看](./DEPLOY_CLOUD.md)

**快速步骤**:

#### Vercel部署（推荐）

1. **推送到GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/yourusername/repo.git
   git push -u origin main
   ```

2. **连接Vercel**:
   - 访问 https://vercel.com/
   - 使用GitHub登录
   - 导入项目
   - 点击Deploy

3. **完成！**: 自动生成域名 `https://your-app.vercel.app`

#### Netlify部署（备选）

1. 访问 https://www.netlify.com/
2. 连接GitHub仓库
3. 配置:
   - Build command: `npm run build`
   - Publish directory: `dist`
4. 点击Deploy

**完成！**: 自动生成域名 `https://your-app.netlify.app`

---

### 方案3：生产环境部署（15-30分钟）

**适用场景**: 企业级应用、需要稳定运行、自定义域名

**详细步骤**: [点击查看](./PUBLIC_DEPLOYMENT.md)

**快速步骤**:

#### 前置准备

1. **购买服务器**（腾讯云/阿里云/华为云）
   - 配置: 2核4GB
   - 系统: Ubuntu 20.04+
   - 费用: ¥50-100/年

2. **购买域名**（阿里云万网/腾讯云DNSPod）
   - 类型: .com 或 .cn
   - 费用: ¥30-100/年

3. **解析域名**
   - 类型: A记录
   - 主机记录: @
   - 记录值: 服务器IP

#### 部署

**方法1：使用一键部署脚本**:
```bash
chmod +x deploy.sh
./deploy.sh
# 选择 3) 生产环境部署
# 输入域名
```

**方法2：手动部署**:
```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 安装依赖
apt-get update
apt-get install -y nginx nodejs npm git

# 3. 克隆项目
git clone your-repo-url
cd web-app

# 4. 构建
npm install
npm run build

# 5. 部署
mkdir -p /var/www/lingzhi-ecosystem
cp -r dist/* /var/www/lingzhi-ecosystem/

# 6. 配置Nginx
cp nginx-production.conf /etc/nginx/sites-available/lingzhi-ecosystem
ln -s /etc/nginx/sites-available/lingzhi-ecosystem /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 7. 配置SSL
certbot --nginx -d yourdomain.com
```

**完成！**: 访问 https://yourdomain.com

---

### 方案4：Docker容器部署（5-10分钟）

**适用场景**: 容器化部署、易于迁移、版本控制

**详细步骤**: [点击查看](./DEPLOYMENT.md)

**快速步骤**:

1. **安装Docker**:
   - Windows/Mac: 下载 Docker Desktop
   - Linux: 参考官方文档

2. **构建镜像**:
```bash
docker build -t lingzhi-ecosystem:latest .
```

3. **运行容器**:
```bash
docker run -d -p 80:80 --name lingzhi-webapp lingzhi-ecosystem:latest
```

**或使用Docker Compose**:
```bash
docker-compose up -d
```

**完成！**: 访问 http://localhost

---

### 方案5：移动应用打包（30-60分钟）

**适用场景**: 原生应用、上架应用商店、iOS/Android用户

**详细步骤**: [点击查看](./DEPLOYMENT.md#移动应用打包)

**快速步骤**:

#### Android

1. **安装Android Studio**: https://developer.android.com/studio

2. **构建APK**:
```bash
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init
npx cap add android
npm run build
npx cap sync android
```

3. **打开Android Studio**:
   - 打开 `android/` 目录
   - Build > Build APK
   - APK位于 `android/app/build/outputs/apk/`

#### iOS（仅Mac）

1. **安装Xcode**: App Store下载

2. **构建IPA**:
```bash
npm install @capacitor/core @capacitor/cli @capacitor/ios
npx cap init
npx cap add ios
npm run build
npx cap sync ios
```

3. **打开Xcode**:
   - 打开 `ios/App/App.xcworkspace`
   - Product > Archive
   - 分发应用

---

### 方案6：静态文件导出（3分钟）

**适用场景**: 自定义部署、部署到其他平台

**快速步骤**:

1. **构建项目**:
```bash
npm run build
```

2. **导出文件**:
   - 文件位于 `dist/` 目录
   - 包含所有静态文件

3. **部署到目标服务器**:
```bash
# 复制到服务器
scp -r dist/* user@server:/var/www/html/

# 或打包传输
tar -czf dist.tar.gz dist/
scp dist.tar.gz user@server:/tmp/
ssh user@server "cd /var/www/html && tar -xzf /tmp/dist.tar.gz"
```

---

## 🐛 常见问题

### 问题1：Node.js未安装

**解决方案**: 访问 https://nodejs.org/ 下载安装

### 问题2：npm install失败

**解决方案**:
```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### 问题3：端口被占用

**解决方案**:
```bash
# 使用其他端口
npm run dev -- --port 3000

# 或终止占用端口的进程
# Mac/Linux
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### 问题4：部署失败

**解决方案**:
```bash
# 本地测试构建
npm run build

# 查看错误日志
npm run build -- --debug
```

### 问题5：访问404

**解决方案**:
- 检查路径配置
- 检查服务器配置
- 查看浏览器控制台错误

---

## 💡 最佳实践

### 开发阶段

1. **使用本地开发服务器**
   - 热重载
   - 快速迭代
   - 调试工具

2. **使用Git版本控制**
   ```bash
   git init
   git add .
   git commit -m "Commit message"
   ```

3. **定期提交代码**
   - 避免丢失进度
   - 便于回滚

### 测试阶段

1. **本地测试**
   - 功能测试
   - 兼容性测试
   - 性能测试

2. **预览构建**
   ```bash
   npm run build
   npm run preview
   ```

### 部署阶段

1. **选择合适的部署方案**
   - 根据需求选择
   - 参考方案对比表

2. **配置环境变量**
   - API地址
   - 其他配置

3. **测试生产环境**
   - 访问测试
   - 功能验证
   - 性能测试

### 运维阶段

1. **监控应用**
   - 访问统计
   - 错误日志
   - 性能指标

2. **定期更新**
   - 安全更新
   - 功能更新

3. **备份配置**
   - 数据备份
   - 配置备份

---

## 📊 成本对比

| 方案 | 服务器 | 域名 | 年度费用 | 说明 |
|------|--------|------|----------|------|
| 本地开发 | ¥0 | ¥0 | ¥0 | 只能在本机访问 |
| Vercel/Netlify | ¥0 | ¥0 | ¥0 | 完全免费 |
| 生产环境 | ¥50-100 | ¥30-100 | ¥80-200 | 需要服务器和域名 |
| Docker | ¥50-100 | ¥30-100 | ¥80-200 | 同上 |
| 移动应用 | ¥0 | ¥0 | ¥0-99 | Android免费，iOS需要$99/年 |

---

## 🎯 推荐路线

### 新手路线（最简单）

1. **本地测试**（1分钟）
   - [本地开发服务器](./DEPLOY_LOCAL.md)
   - 熟悉功能

2. **公网部署**（5分钟）
   - [免费云托管](./DEPLOY_CLOUD.md)
   - 使用Vercel/Netlify

3. **进阶优化**（可选）
   - 配置自定义域名
   - 配置CDN
   - 配置Analytics

### 专业路线

1. **本地开发**
   - 使用Git版本控制
   - 持续集成开发

2. **生产部署**
   - [生产环境部署](./PUBLIC_DEPLOYMENT.md)
   - 配置Nginx
   - 配置SSL

3. **移动应用**（可选）
   - [移动应用打包](./DEPLOYMENT.md#移动应用打包)
   - 上架应用商店

---

## 📞 获取帮助

### 文档

- [环境准备检查](./SETUP_CHECK.md)
- [部署方案选择](./DEPLOY_CHOICE.md)
- [本地开发服务器](./DEPLOY_LOCAL.md)
- [免费云托管](./DEPLOY_CLOUD.md)
- [生产环境部署](./PUBLIC_DEPLOYMENT.md)
- [Coze集成方案](./COZE_INTEGRATION.md)
- [详细部署文档](./DEPLOYMENT.md)

### 常见问题

- 查看本文档的"常见问题"部分
- 查看各个方案的详细文档

### 技术支持

- GitHub Issues
- 邮件联系
- 在线客服

---

## 🎉 开始部署吧！

选择一个方案，立即开始部署：

- **我要快速测试** → [方案1: 本地开发服务器](./DEPLOY_LOCAL.md)
- **我要公网访问（免费）** → [方案2: 免费云托管](./DEPLOY_CLOUD.md)
- **我要生产环境** → [方案3: 生产环境部署](./PUBLIC_DEPLOYMENT.md)
- **我要移动应用** → [方案5: 移动应用打包](./DEPLOYMENT.md#移动应用打包)

---

**祝您部署顺利！** 🚀
