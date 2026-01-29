# ⚡ 5分钟云部署 - 快速操作清单

**按顺序完成以下步骤，5分钟搞定！**

---

## ✅ 准备清单

- [ ] GitHub账号（免费）
- [ ] 项目代码（已准备好）
- [ ] 浏览器（Chrome/Edge/Firefox）

---

## 🚀 5分钟部署步骤

### 第1分钟：推送代码到GitHub

**1.1 创建GitHub仓库（1分钟）**
```
1. 访问 https://github.com/
2. 登录或注册
3. 点击右上角 "+" > "New repository"
4. 填写：
   - Repository name: lingzhi-ecosystem-app
   - 选择 Public
5. 点击 "Create repository"
```

**1.2 推送代码（1分钟）**
```bash
# 打开终端/命令行
cd /workspace/projects/web-app

# 初始化Git
git init

# 添加文件
git add .

# 提交
git commit -m "Initial commit"

# 连接仓库（替换为你的地址）
git remote add origin https://github.com/yourusername/lingzhi-ecosystem-app.git

# 推送
git branch -M main
git push -u origin main
```

---

### 第2分钟：注册Vercel

```
1. 访问 https://vercel.com/
2. 点击 "Sign Up"
3. 选择 "Continue with GitHub"
4. 授权访问
5. 免费注册完成
```

---

### 第3-4分钟：部署应用

```
1. 登录Vercel后，点击 "Add New..."
2. 选择 "Project"
3. 找到 lingzhi-ecosystem-app 仓库
4. 点击 "Import"
5. 配置：
   - Framework: Vite
   - Build Command: npm run build
   - Output Directory: dist
6. 点击 "Deploy"
7. 等待1-2分钟
```

---

### 第5分钟：访问应用

```
1. 看到 "Congratulations!" 表示成功
2. 点击 "Visit" 按钮
3. 访问自动生成的域名
4. 测试登录功能
5. 完成！🎉
```

---

## 🎯 访问地址

**Vercel自动生成**：
```
https://lingzhi-ecosystem-app-xxxx.vercel.app
```

**例如**：
```
https://lingzhi-ecosystem-app-a1b2c3d4.vercel.app
```

---

## 📱 给用户的链接

**直接发送这个链接**：
```
https://lingzhi-ecosystem-app-xxxx.vercel.app
```

**或生成二维码**：
```
1. 访问二维码生成网站
2. 输入你的域名
3. 生成二维码
4. 用户扫码访问
```

---

## ✅ 验证清单

部署完成后，确认以下内容：

- [ ] 可以通过域名访问
- [ ] 页面加载正常
- [ ] 登录功能正常
- [ ] 可以使用对话功能
- [ ] 移动端访问正常

---

## 🔄 更新应用

**代码修改后，只需推送即可自动更新**：

```bash
git add .
git commit -m "Update: 新功能"
git push
```

Vercel会自动检测并重新部署！

---

## 📞 遇到问题？

**查看详细指南**: [CLOUD_DEPLOYMENT_FULL_GUIDE.md](./CLOUD_DEPLOYMENT_FULL_GUIDE.md)

---

**5分钟搞定，现在开始吧！** 🚀
