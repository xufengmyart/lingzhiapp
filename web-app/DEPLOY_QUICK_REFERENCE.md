# 🎯 一键部署快速参考

**打印或保存这个页面，随时查阅！**

---

## 🚀 三种最快部署方式

### 1️⃣ 本地开发（1分钟）

```bash
cd /workspace/projects/web-app
npm install
npm run dev
```

访问: http://localhost:5173

---

### 2️⃣ Vercel免费部署（5分钟）⭐推荐

```bash
# 1. 推送到GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/yourusername/repo.git
git push -u origin main

# 2. 访问 https://vercel.com/
# 3. 登录 → 导入项目 → Deploy
```

访问: https://your-app.vercel.app

---

### 3️⃣ Netlify免费部署（5分钟）

```bash
# 同上推送到GitHub

# 1. 访问 https://www.netlify.com/
# 2. 登录 → 导入项目
# 3. Build: npm run build
# 4. Publish: dist
# 5. Deploy
```

访问: https://your-app.netlify.app

---

## 📋 环境检查

```bash
# 检查Node.js
node -v  # 需要 v18+

# 检查npm
npm -v   # 需要 v9+

# 检查Git
git --version
```

---

## 🔧 一键部署脚本

### Linux/Mac

```bash
chmod +x deploy.sh
./deploy.sh
```

### Windows

```batch
deploy.bat
```

---

## 📱 移动应用打包

### Android

```bash
npm install @capacitor/core @capacitor/cli @capacitor/android
npx cap init
npx cap add android
npm run build
npx cap sync android
# 打开 android/ 目录用Android Studio构建
```

### iOS (Mac)

```bash
npm install @capacitor/core @capacitor/cli @capacitor/ios
npx cap init
npx cap add ios
npm run build
npx cap sync ios
# 打开 ios/App/App.xcworkspace 用Xcode构建
```

---

## 🌐 生产环境部署

```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 安装依赖
apt-get update
apt-get install -y nginx nodejs npm

# 3. 构建项目
git clone your-repo-url
cd web-app
npm install
npm run build

# 4. 部署
mkdir -p /var/www/lingzhi-ecosystem
cp -r dist/* /var/www/lingzhi-ecosystem/

# 5. 配置Nginx
cp nginx-production.conf /etc/nginx/sites-available/lingzhi-ecosystem
ln -s /etc/nginx/sites-available/lingzhi-ecosystem /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 6. SSL证书
certbot --nginx -d yourdomain.com
```

---

## 🐛 常见问题速查

### 端口被占用

```bash
# Mac/Linux
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### npm安装失败

```bash
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Docker构建失败

```bash
docker system prune -a
docker build -t lingzhi-ecosystem:latest .
```

---

## 📞 帮助文档

- [完整部署指南](./DEPLOYMENT_GUIDE.md)
- [环境准备检查](./SETUP_CHECK.md)
- [部署方案选择](./DEPLOY_CHOICE.md)
- [本地开发](./DEPLOY_LOCAL.md)
- [免费云托管](./DEPLOY_CLOUD.md)
- [生产环境](./PUBLIC_DEPLOYMENT.md)
- [Coze集成](./COZE_INTEGRATION.md)

---

## 🎯 快速决策

```
我要快速测试？
→ 本地开发（1分钟）

我要公网访问（免费）？
→ Vercel/Netlify（5分钟）

我要生产环境？
→ Nginx部署（15分钟）

我要移动应用？
→ Capacitor打包（30分钟）
```

---

**祝部署顺利！** 🚀
