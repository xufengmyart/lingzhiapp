# 🚀 10分钟快速部署 - 精简版

**3个步骤，10分钟完成部署！**

---

## 步骤1：注册账号（2分钟）

### 1.1 注册GitHub（1分钟）
访问：https://github.com/signup
- 注册账号
- 验证邮箱

### 1.2 注册Vercel（1分钟）
访问：https://vercel.com/signup
- 使用GitHub登录

---

## 步骤2：推送代码到GitHub（3分钟）

### 2.1 创建GitHub仓库
1. 登录GitHub
2. 点击右上角 "+" → "New repository"
3. 仓库名：`lingzhi-ecosystem-app`
4. 设置为Public
5. 点击 "Create repository"

### 2.2 推送代码

**Linux/Mac 用户**：
```bash
cd /workspace/projects/web-app
./deploy-helper.sh all
```

**Windows 用户**：
```cmd
cd \workspace\projects\web-app
deploy-helper.bat all
```

**手动操作**：
```bash
cd /workspace/projects/web-app
git remote add origin https://github.com/你的用户名/lingzhi-ecosystem-app.git
git branch -M main
git push -u origin main
```

---

## 步骤3：在Vercel部署（5分钟）

### 3.1 导入仓库
1. 登录Vercel
2. 点击 "Add New..." → "Project"
3. 找到 `lingzhi-ecosystem-app` 仓库
4. 点击 "Import"

### 3.2 部署
1. 确认配置（系统自动检测）
2. 点击 "Deploy"
3. 等待2-3分钟
4. 复制部署URL

### 3.3 测试和分享
1. 打开部署URL
2. 测试登录（用户名：admin，密码：admin123）
3. 分享URL给用户

---

## ✅ 完成！

用户现在可以访问您的应用了！

**部署URL示例**：
```
https://lingzhi-ecosystem-app-xxxx.vercel.app
```

---

## 🆘 遇到问题？

### Git推送失败
使用GitHub Personal Access Token代替密码
https://github.com/settings/tokens

### Vercel部署失败
检查构建日志，重新部署

### 无法访问
等待1-2分钟（CDN缓存），或刷新页面

详细帮助：[USER_ACTION_GUIDE.md](./USER_ACTION_GUIDE.md)
