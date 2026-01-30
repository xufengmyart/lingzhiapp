# 使用 Cloudflare Pages 部署（推荐）

## 为什么选择 Cloudflare Pages

1. ✅ **完全免费** - 无限制的带宽和部署
2. ✅ **自带全球 CDN** - 访问速度更快
3. ✅ **支持自定义域名** - 可以使用免费域名
4. ✅ **不会被误报** - 独立域名，不会被安全软件拦截

## 快速开始（5 分钟部署）

### 步骤 1：注册 Cloudflare 账号

1. 访问：https://dash.cloudflare.com/sign-up
2. 使用邮箱注册
3. 验证邮箱

### 步骤 2：导入项目

1. 登录 Cloudflare Dashboard
2. 在左侧菜单点击 **"Workers & Pages"**
3. 点击 **"Create application"**
4. 选择 **"Pages"** 标签
5. 点击 **"Connect to Git"**

### 步骤 3：连接 GitHub

1. 点击 **"Connect to GitHub"**
2. 授权 Cloudflare 访问您的 GitHub
3. 找到 `lingzhiapp` 仓库
4. 点击 **"Begin setup"**

### 步骤 4：配置部署

**填入以下配置**：

| 配置项 | 值 |
|--------|-----|
| Project name | `lingzhiapp` |
| Production branch | `main` |
| Framework preset | `None` |
| Build command | （留空） |
| Build output directory | `public` |

点击 **"Save and Deploy"**

### 步骤 5：等待部署

等待 1-2 分钟，部署成功后会显示：
```
✅ Deployment successful
https://lingzhiapp.pages.dev
```

### 步骤 6：访问应用

访问：https://lingzhiapp.pages.dev

**预期结果**：
- ✅ 页面正常显示
- ✅ 输入框文字可见
- ✅ 没有安全警告

---

## 添加自定义域名

### 选项 A：使用免费域名服务

**Freenom（免费顶级域名）**

1. 访问：https://www.freenom.com
2. 搜索想要的域名（如 `lingzhiapp.tk`, `lingzhiapp.ml`, `lingzhiapp.ga`）
3. 注册账号并购买（免费）
4. 在 Cloudflare Pages 添加自定义域名

**Namecheap（便宜域名）**

1. 访问：https://www.namecheap.com
2. 购买域名（约 $10/年）
3. 在 Cloudflare Pages 添加自定义域名

### 选项 B：添加自定义域名到 Cloudflare Pages

1. 访问 Cloudflare Pages Dashboard
2. 点击 `lingzhiapp` 项目
3. 点击 **"Custom domains"** 标签
4. 点击 **"Set up a custom domain"**
5. 输入您的域名（如 `lingzhiapp.tk`）
6. 点击 **"Continue"**
7. 按照提示配置 DNS

---

## 提交误报申请（临时方案）

如果暂时不想使用自定义域名，可以提交误报申请：

### 1. 提交给 Google Safe Browsing

访问：https://safebrowsing.google.com/safebrowsing/report_phish/

**填入以下信息**：
- URL: `https://benevolent-cupcake-53d557.netlify.app`
- Reason: `误报 - 网站是正常的前端应用，没有任何恶意内容`

### 2. 提交给腾讯安全中心

访问：https://urlsec.qq.com/complain.html

**填入以下信息**：
- URL: `https://benevolent-cupcake-53d557.netlify.app`
- 类型：误报
- 说明：网站是正常的前端应用，建议恢复访问

### 3. 提交给 360 安全中心

访问：https://safe.so.360.cn/safe/complaint.html

**填入以下信息**：
- URL: `https://benevolent-cupcake-53d557.netlify.app`
- 类型：误报
- 说明：网站是正常的前端应用，没有任何恶意内容

---

## 等待时间

| 平台 | 处理时间 |
|------|----------|
| Google Safe Browsing | 24-48 小时 |
| 腾讯安全中心 | 1-3 天 |
| 360 安全中心 | 1-3 天 |
| Cloudflare Pages | 立即生效 |

---

## 推荐方案对比

| 方案 | 时间 | 效果 | 费用 |
|------|------|------|------|
| Cloudflare Pages + 默认域名 | 5 分钟 | ⚠️ 仍可能被误报 | 免费 |
| Cloudflare Pages + 免费域名 | 30 分钟 | ✅ 完全解决 | 免费 |
| Cloudflare Pages + 购买域名 | 30 分钟 | ✅ 完全解决 | 约 $10/年 |
| 提交误报申请 | 1-3 天 | ⚠️ 不保证成功 | 免费 |

---

## 现在的建议

### 立即执行（5 分钟）

1. 注册 Cloudflare 账号
2. 导入 GitHub 项目
3. 部署到 Cloudflare Pages
4. 访问 `https://lingzhiapp.pages.dev`

### 后续执行（30 分钟）

1. 获取免费域名（Freenom）
2. 添加自定义域名到 Cloudflare Pages

---

## 紧急备用方案

如果 Cloudflare Pages 也有问题，可以使用：

### Vercel（需要解决网络问题）

1. 使用 VPN 或更换网络
2. 导入项目到 Vercel
3. 配置自定义域名

### GitHub Pages（最简单）

1. 在 GitHub 仓库设置中启用 Pages
2. 选择 `main` 分支和 `/public` 目录
3. 访问 `https://xufengmyart.github.io/lingzhiapp`

---

## 总结

| 问题 | 解决方案 | 时间 |
|------|----------|------|
| 输入框文字不可见 | ✅ 已修复 | 立即生效 |
| 浏览器安全警告 | 使用自定义域名 | 30 分钟 |

**建议**：立即部署到 Cloudflare Pages，并添加自定义域名，永久解决安全警告问题。
