# Netlify 注册与部署详细指南

## 第一步：注册 Netlify 账号

### 1. 访问 Netlify
打开浏览器访问：https://app.netlify.com

### 2. 点击注册
- 在页面右上角点击 **"Sign up"** 按钮
- 或点击 **"Get started for free"**

### 3. 选择注册方式
**推荐使用 GitHub 注册**（最简单）

点击 **"Sign up with GitHub"**

### 4. 授权 GitHub
- 如果未登录 GitHub，会跳转到 GitHub 登录页面
- 输入 GitHub 用户名和密码，点击 **"Sign in"**

### 5. 授权 Netlify 访问
在 GitHub 授权页面：
- 点击 **"Authorize Netlify"** 按钮
- 允许 Netlify 访问您的 GitHub 仓库

### 6. 填写个人信息
- 输入 **Username**（用户名）
- 输入 **Email**（邮箱）
- 输入 **Full name**（全名）
- 点击 **"Sign up"**

### 7. 验证邮箱（可选）
- Netlify 可能会发送验证邮件
- 检查邮箱，点击验证链接

## 第二步：导入项目到 Netlify

### 1. 进入团队页面
注册成功后，会跳转到 Netlify 团队页面

### 2. 添加新网站
点击 **"Add new site"** 按钮

### 3. 选择导入现有项目
点击 **"Import an existing project"**

### 4. 连接 GitHub
- 点击 **"GitHub"** 图标
- 点击 **"Configure Netlify on GitHub"** 按钮
- 在弹出的 GitHub 授权页面，点击 **"Authorize Netlify"**

### 5. 选择仓库
- 在 **"Only select certain repositories"** 下拉框中
- 搜索或找到 `lingzhiapp` 仓库
- 点击仓库名称左侧的复选框，选中它
- 点击页面底部的 **"Save"** 按钮

### 6. 导入项目
- 回到 Netlify 导入页面
- 在仓库列表中找到 `lingzhiapp`
- 点击 **"Import"** 按钮

## 第三步：配置部署

### 1. 配置构建设置
Netlify 会自动识别项目，显示以下配置：

**Build settings**（构建设置）：
- **Build command**: 留空（无需构建命令）
- **Publish directory**: `public`

**如果自动识别不正确，手动填入**：
- **Publish directory**: `public`

### 2. 高级设置（可选）
点击 **"Advanced"** 展开更多选项：
- **Branch to deploy**: `main`

### 3. 确认配置
检查配置是否正确，然后点击 **"Deploy site"** 按钮

## 第四步：等待部署

### 1. 查看部署进度
- 页面会显示 **"Processing deploy..."**
- 部署过程通常需要 1-2 分钟

### 2. 部署完成
部署成功后，页面顶部会显示：
```
✓ Published master@xxxxxxxx
```

### 3. 获取部署域名
在页面顶部找到 **"Site overview"**
会看到分配的默认域名，格式类似：
```
https://xxxxx.netlify.app
```

**复制这个域名**

## 第五步：访问应用

### 1. 打开浏览器
将复制的域名粘贴到浏览器地址栏

### 2. 按 Enter 访问
应该能看到紫色渐变背景的页面，显示：
```
🚀
灵值生态园
✅ Vercel 部署成功
如果你能看到这个页面，说明应用已成功部署
```

## 常见问题

### Q1: 提示 "No such file or directory"
**解决**：确保 `public` 目录和 `index.html` 文件已推送到 GitHub

### Q2: 部署失败，显示 "Build failed"
**解决**：检查 `netlify.toml` 配置是否正确

### Q3: 访问显示 404
**解决**：确保 `public/index.html` 文件存在

### Q4: 想使用自定义域名
**解决**：
1. 点击 **"Domain settings"**
2. 点击 **"Add custom domain"**
3. 输入您的域名（如 `lingzhiapp.com`）
4. 按照提示配置 DNS

## 部署成功后的下一步

部署成功后，如果想恢复完整的 React 应用功能：

1. 在本地恢复 React 应用代码
2. 将 `web-app/` 目录内容移至 `public/` 目录
3. 推送到 GitHub
4. Netlify 会自动重新部署
