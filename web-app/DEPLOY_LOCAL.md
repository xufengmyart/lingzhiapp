# 💻 方案1：本地开发服务器部署（1分钟启动）

**最简单方案！无需任何配置，立即使用！**

---

## 🎯 为什么选择这个方案？

✅ **最简单** - 一键启动，无需配置
✅ **最快** - 1分钟即可运行
✅ **免费** - 完全免费
✅ **热重载** - 修改代码自动刷新
✅ **开发友好** - 完整的开发工具

---

## 📋 前置要求

1. ✅ Node.js已安装（v18+）
2. ✅ npm已安装（v9+）
3. ✅ 项目代码完整

**如何检查**:
```bash
node -v  # 应该显示 v18.x.x 或更高
npm -v   # 应该显示 9.x.x 或更高
```

---

## 🚀 部署步骤（1分钟完成）

### 方法1：使用一键部署脚本（推荐）

#### Linux/Mac系统

```bash
# 1. 进入项目目录
cd /workspace/projects/web-app

# 2. 给脚本添加执行权限（只需一次）
chmod +x deploy.sh

# 3. 运行部署脚本
./deploy.sh

# 4. 选择 1) 本地开发服务器
```

#### Windows系统

```batch
# 1. 进入项目目录
cd web-app

# 2. 双击运行 deploy.bat
# 或在命令行运行
deploy.bat

# 3. 选择 1) 本地开发服务器
```

**等待1-2秒，服务器启动！**

---

### 方法2：使用npm命令

```bash
# 1. 进入项目目录
cd /workspace/projects/web-app

# 2. 安装依赖（只需一次）
npm install

# 3. 启动开发服务器
npm run dev
```

**输出示例**:
```
  VITE v5.4.21  ready in 523 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.100:5173/
  ➜  press h + enter to show help
```

---

## 🌐 访问应用

### 本地访问

打开浏览器，访问：
```
http://localhost:5173
```

**或使用快捷方式**:
- Linux/Mac: 按 `Cmd` + `Click` 点击终端中的链接
- Windows: 按 `Ctrl` + `Click` 点击终端中的链接

### 局域网访问（手机等设备）

**步骤**:

1. 查看本机IP地址
```bash
# Windows
ipconfig

# Mac/Linux
ifconfig
```

2. 找到IPv4地址，例如：`192.168.1.100`

3. 在同一WiFi下的手机/平板访问：
```
http://192.168.1.100:5173
```

---

## 🎮 使用指南

### 主要功能

1. **主页** - 欢迎页面，功能概览
2. **智能对话** - 与AI助手对话
3. **经济模型** - 查看收入预测和灵值价值
4. **用户旅程** - 查看当前阶段和进度
5. **合伙人管理** - 管理合伙人和佣金
6. **统计数据** - 可视化数据展示
7. **个人中心** - 个人设置和信息

### 导航方式

- **顶部导航栏** - 点击菜单切换页面
- **侧边导航栏**（移动端） - 点击汉堡菜单打开

### 用户登录

**测试账号**:
- 用户名: `test`
- 密码: `test123`

**或直接使用**:
- 点击"使用游客模式"按钮

---

## 🔧 开发功能

### 热重载

修改代码后，浏览器会自动刷新：
```typescript
// 修改 src/pages/HomePage.tsx
export default function HomePage() {
  return <div>修改后的内容</div>
}

// 保存文件后，浏览器自动刷新
```

### 查看控制台

打开浏览器开发者工具：
- **Windows/Linux**: 按 `F12` 或 `Ctrl+Shift+I`
- **Mac**: 按 `Cmd+Option+I`

### 调试代码

在代码中添加断点：
```typescript
// 在代码中添加 debugger
export default function HomePage() {
  const data = fetchData();
  debugger; // 浏览器会在这里暂停
  return <div>{data}</div>;
}
```

---

## 📱 移动端测试

### 方法1：使用浏览器开发者工具

1. 按 `F12` 打开开发者工具
2. 点击设备图标（Toggle device toolbar）
3. 选择设备型号（iPhone 12, Pixel 5等）
4. 刷新页面查看移动端效果

### 方法2：使用真实设备

**Android设备**:
1. 确保手机和电脑在同一WiFi
2. 查看电脑IP地址（例如：192.168.1.100）
3. 在手机浏览器访问：`http://192.168.1.100:5173`

**iOS设备**:
1. 确保iPhone和Mac在同一WiFi
2. 在Safari中访问：`http://192.168.1.100:5173`

---

## 🎯 PWA测试

### 安装到桌面

1. 在Chrome浏览器中访问应用
2. 点击地址栏右侧的安装图标
3. 点击"安装灵值生态园"
4. 应用会作为独立窗口运行

### 安装到手机主屏幕

**Android (Chrome)**:
1. 访问应用
2. 点击菜单（三个点）
3. 选择"添加到主屏幕"
4. 确认添加

**iOS (Safari)**:
1. 访问应用
2. 点击分享按钮
3. 选择"添加到主屏幕"
4. 确认添加

### 离线测试

1. 安装PWA
2. 断开网络连接
3. 打开应用（应该仍然可以访问）

---

## 🔥 快捷命令

### 代码检查

```bash
npm run lint
```

### 修复代码格式

```bash
npm run lint -- --fix
```

### 类型检查

```bash
npx tsc --noEmit
```

### 清理缓存

```bash
# 清理node_modules
rm -rf node_modules package-lock.json
npm install

# 清理Vite缓存
rm -rf node_modules/.vite
```

---

## 🛑 停止服务器

### 方法1：在终端中按 `Ctrl + C`

### 方法2：查找并终止进程

```bash
# 查找进程
ps aux | grep "vite"

# 终止进程
kill <PID>
```

### 方法3：使用Windows任务管理器

1. 打开任务管理器（Ctrl+Shift+Esc）
2. 找到node.exe进程
3. 结束任务

---

## 🐛 常见问题

### 问题1：端口被占用

**错误信息**:
```
Error: Port 5173 is in use
```

**解决方案**:

```bash
# 方法1：使用其他端口
npm run dev -- --port 3000

# 方法2：查找并终止占用端口的进程

# Mac/Linux
lsof -ti:5173 | xargs kill -9

# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### 问题2：依赖安装失败

**解决方案**:
```bash
# 清理缓存
npm cache clean --force

# 删除node_modules
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

### 问题3：页面空白

**检查步骤**:

1. 打开浏览器开发者工具（F12）
2. 查看Console标签页的错误信息
3. 查看Network标签页，检查资源加载是否失败

**常见原因**:
- 端口被占用
- 代码有错误
- 依赖未安装

### 问题4：样式丢失

**检查步骤**:

1. 查看Network标签页，检查CSS文件是否加载
2. 查看Console标签页，检查是否有错误
3. 确认Tailwind CSS配置正确

**解决方案**:
```bash
# 重新构建
npm run build

# 清理缓存
rm -rf node_modules/.vite
npm run dev
```

---

## 📊 性能优化

### 开发模式性能

开发模式下，Vite会：
- ✅ 启动速度快
- ✅ 热更新快速
- ⚠️ 文件较大（未压缩）
- ⚠️ 未使用生产优化

### 生产构建预览

如果需要测试生产环境性能：

```bash
# 1. 构建生产版本
npm run build

# 2. 预览构建结果
npm run preview
```

访问: `http://localhost:4173`

---

## 🎉 恭喜！

您的本地开发服务器已经启动成功！🚀

**下一步**:
1. 📱 在浏览器访问应用
2. 🔧 测试各个功能模块
3. 📝 开始开发新功能
4. 🚀 部署到公网（参考其他部署方案）

---

## 📚 相关文档

- [部署方案选择](./DEPLOY_CHOICE.md)
- [免费云托管部署](./DEPLOY_CLOUD.md)
- [生产环境部署](./DEPLOY_PRODUCTION.md)
- [移动应用打包](./DEPLOY_MOBILE.md)

---

**开始使用吧！有问题随时查看文档！** 🎯
