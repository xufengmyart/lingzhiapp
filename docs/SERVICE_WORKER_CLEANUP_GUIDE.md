# Service Worker 缓存清理指南

## 问题说明

如果您遇到以下错误：
- "来源为'https://meiyueart.com/src/main.tsx'的模块加载失败"
- "无法加载'https://meiyueart.com/src/main.tsx'。某个 ServiceWorker 拦截了请求并遇到未知错误"

这是由于 Service Worker 缓存了旧版本的资源。

## 解决方案

### 方法 1：自动清理（推荐）

新版本的 Service Worker（v20260223-0022）会自动清理所有缓存。

**操作步骤：**
1. 刷新浏览器页面（按 `Ctrl+F5` 或 `Cmd+Shift+R` 强制刷新）
2. Service Worker 会自动清理所有缓存
3. 页面会自动加载新版本

### 方法 2：手动清理（如果方法 1 无效）

#### Chrome/Edge 浏览器

1. 打开开发者工具（按 `F12`）
2. 进入 `Application` 标签
3. 左侧菜单找到 `Service Workers`
4. 点击 `Unregister` 按钮注销 Service Worker
5. 刷新浏览器页面

#### Firefox 浏览器

1. 打开开发者工具（按 `F12`）
2. 进入 `Application` 或 `应用程序` 标签
3. 左侧菜单找到 `Service Workers`
4. 点击 `Unregister` 按钮注销 Service Worker
5. 刷新浏览器页面

#### Safari 浏览器

1. 打开开发者工具（按 `Cmd+Option+I`）
2. 进入 `Application` 或 `应用程序` 标签
3. 左侧菜单找到 `Service Workers`
4. 点击 `Unregister` 按钮注销 Service Worker
5. 刷新浏览器页面

### 方法 3：使用清理页面

访问以下页面进行手动清理：
- `https://meiyueart.com/unregister-sw.html`
- `https://meiyueart.com/force-refresh.html`

### 方法 4：清除浏览器缓存

#### Chrome/Edge 浏览器

1. 按 `Ctrl+Shift+Delete`（Windows）或 `Cmd+Shift+Delete`（Mac）
2. 选择"缓存的图片和文件"
3. 点击"清除数据"按钮

#### Firefox 浏览器

1. 按 `Ctrl+Shift+Delete`（Windows）或 `Cmd+Shift+Delete`（Mac）
2. 选择"缓存"
3. 点击"立即清除"按钮

#### Safari 浏览器

1. 打开 Safari > 偏好设置
2. 进入"隐私"标签
3. 点击"管理网站数据"
4. 选择"meiyueart.com"
5. 点击"移除"按钮

## 验证清理成功

清理缓存后，您应该能够：
1. 正常访问网站
2. 在浏览器控制台看到版本信息：`[版本管理] 当前版本: 20260223-0022`
3. 不再看到模块加载失败的错误

## 如果问题依然存在

如果以上方法都无法解决问题，请联系管理员并提供：
1. 浏览器名称和版本
2. 操作系统名称和版本
3. 完整的错误信息截图
4. 浏览器控制台的所有错误信息

## 版本信息

- 当前版本：v20260223-0022
- 部署时间：2026-02-23 00:22
- Service Worker：自动清理版本

## 相关链接

- 主页：https://meiyueart.com
- 清理 Service Worker：https://meiyueart.com/unregister-sw.html
- 强制刷新：https://meiyueart.com/force-refresh.html
- 清除缓存：https://meiyueart.com/clear-cache.html
