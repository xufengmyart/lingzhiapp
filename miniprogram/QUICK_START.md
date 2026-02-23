# 微信小程序快速开始指南

## 🚀 5分钟快速部署

### 第一步：准备密钥（5分钟）

1. **登录微信公众平台**
   - 访问：https://mp.weixin.qq.com/
   - 使用管理员账号登录

2. **获取 AppID**
   - 进入「开发」→「开发设置」
   - 复制「开发者ID」中的 AppID

3. **生成代码上传密钥**
   - 在「开发设置」页面找到「小程序代码上传」
   - 点击「生成」按钮
   - 下载密钥文件（如：`private.wx1234567890.key`）

4. **放置密钥文件**
   ```bash
   # 创建密钥目录
   mkdir -p /workspace/projects/miniprogram/keys

   # 将下载的密钥文件复制到 keys 目录
   # 使用文件管理器或以下命令：
   cp ~/Downloads/private.wx1234567890.key /workspace/projects/miniprogram/keys/

   # 设置文件权限（仅所有者可读写）
   chmod 600 /workspace/projects/miniprogram/keys/private.wx1234567890.key
   ```

5. **配置 IP 白名单**
   - 获取服务器 IP：`curl ifconfig.me`
   - 在微信公众平台的「开发设置」→「IP 白名单」中添加该 IP

### 第二步：更新配置文件（2分钟）

需要更新以下 4 个文件中的 `appid`：

#### 1. project.config.json
```bash
vi /workspace/projects/miniprogram/project.config.json
```
将 `"请填写你的小程序AppID"` 替换为实际的 AppID

#### 2. ci/upload.js
```bash
vi /workspace/projects/miniprogram/ci/upload.js
```
找到第 7 行，将 `appid: '请填写你的小程序AppID'` 替换为实际的 AppID

#### 3. ci/preview.js
```bash
vi /workspace/projects/miniprogram/ci/preview.js
```
找到第 7 行，将 `appid: '请填写你的小程序AppID'` 替换为实际的 AppID

#### 4. miniprogram/utils/config.js
```bash
vi /workspace/projects/miniprogram/miniprogram/utils/config.js
```
将 `appId: '请填写你的小程序AppID'` 替换为实际的 AppID

### 第三步：安装依赖（1分钟）

```bash
cd /workspace/projects/miniprogram
npm install
```

*如果 npm install 超时或失败，请检查网络连接，或使用国内镜像源：*
```bash
npm install --registry=https://registry.npmmirror.com
```

### 第四步：执行部署（1分钟）

```bash
# 使用一键部署脚本
./deploy.sh 1.0.0 "首次发布"

# 或者使用 npm 脚本
npm run upload
```

### 第五步：微信平台发布（5分钟）

1. **登录微信公众平台**
   - 访问：https://mp.weixin.qq.com/

2. **进入版本管理**
   - 点击左侧「版本管理」

3. **选择上传的版本**
   - 你会看到刚上传的版本（版本号：1.0.0）

4. **提交审核**
   - 点击「提交审核」按钮
   - 填写审核信息（可选）
   - 提交

5. **等待审核**
   - 微信通常在 1-3 个工作日内完成审核
   - 审核通过后会收到通知

6. **发布上线**
   - 审核通过后，点击「发布」按钮
   - 小程序正式上线！

## 📱 如何在微信开发者工具中预览

1. **下载微信开发者工具**
   - 访问：https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html
   - 下载适合你操作系统的版本

2. **打开项目**
   - 启动微信开发者工具
   - 扫码登录
   - 点击「+」创建新项目
   - 选择「导入项目」
   - 项目目录：`/workspace/projects/miniprogram/miniprogram`
   - AppID：填写你的小程序 AppID
   - 项目名称：灵值生态园

3. **预览和测试**
   - 点击「预览」按钮，生成二维码
   - 用微信扫码，即可在手机上预览

## 🧪 测试账号

小程序内置了以下测试账号：

| 用户类型 | 用户名 | 密码 |
|---------|--------|------|
| 管理员 | admin | 123 |
| 普通用户 | 马伟娟 | 123 |

## 📂 项目文件说明

### 核心文件

| 文件 | 说明 |
|------|------|
| `miniprogram/app.js` | 小程序入口文件 |
| `miniprogram/app.json` | 小程序全局配置 |
| `miniprogram/app.wxss` | 全局样式 |
| `project.config.json` | 小程序项目配置 |
| `package.json` | Node.js 依赖配置 |

### 页面文件

| 页面 | 路径 | 说明 |
|------|------|------|
| 首页 | `pages/index/index` | 展示快捷入口、最新资源 |
| 登录 | `pages/auth/login/login` | 用户登录 |
| 资源列表 | `pages/resources/list/list` | 资源浏览和搜索 |
| 用户中心 | `pages/user/profile/profile` | 个人信息管理 |

### API 接口文件

| 文件 | 说明 |
|------|------|
| `api/auth.js` | 登录、注册、退出登录 |
| `api/resources.js` | 资源增删改查 |
| `api/user.js` | 用户信息、头像上传 |

### 部署文件

| 文件 | 说明 |
|------|------|
| `ci/upload.js` | 上传代码到微信 |
| `ci/preview.js` | 生成预览二维码 |
| `deploy.sh` | 一键部署脚本 |

## 🛠️ 常用命令

```bash
# 进入项目目录
cd /workspace/projects/miniprogram

# 安装依赖
npm install

# 上传代码
npm run upload

# 生成预览二维码
npm run preview

# 一键部署（指定版本号）
./deploy.sh 1.0.1 "修复登录问题"

# 一键部署（自动版本号）
./deploy.sh
```

## ❓ 常见问题

### Q1: npm install 失败
**A**: 使用国内镜像源
```bash
npm install --registry=https://registry.npmmirror.com
```

### Q2: 上传失败，提示 "IP 不在白名单"
**A**:
1. 获取服务器 IP：`curl ifconfig.me`
2. 在微信公众平台添加该 IP 到白名单
3. 等待 5-10 分钟后重试

### Q3: 上传失败，提示 "密钥不存在"
**A**:
1. 确认密钥文件在 `keys/` 目录
2. 确认密钥文件名与配置中的一致
3. 确认密钥文件权限为 600

### Q4: 编译错误
**A**:
1. 先在微信开发者工具中打开项目
2. 检查是否有语法错误
3. 确保所有页面文件都已创建

### Q5: 登录失败
**A**:
1. 检查后端 API 是否正常：`curl https://meiyueart.com/api/health`
2. 检查网络连接
3. 查看控制台错误信息

## 📞 获取帮助

### 文档
- **项目说明**: [README.md](README.md)
- **部署指南**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **项目总结**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### 微信官方文档
- [小程序开发文档](https://developers.weixin.qq.com/miniprogram/dev/framework/)
- [miniprogram-ci 文档](https://developers.weixin.qq.com/miniprogram/dev/devtools/ci.html)

### 联系方式
- 项目地址: https://github.com/xxx/lingzhi-ecosystem
- 生产环境: https://meiyueart.com

## 🎉 完成部署！

恭喜你！你已成功完成小程序的部署。现在：

1. ✅ 小程序代码已上传到微信服务器
2. ⏳ 等待微信审核通过（1-3个工作日）
3. 🚀 审核通过后即可发布上线
4. 📱 用户可以通过微信搜索你的小程序

---

**祝你使用愉快！** 🎊
