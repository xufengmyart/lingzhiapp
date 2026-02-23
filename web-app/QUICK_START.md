# 自动缓存清除系统 - 快速开始

## 🚀 5 分钟快速部署

### 步骤 1: 应用 Nginx 配置

```bash
# 复制配置文件
sudo cp /workspace/projects/web-app/nginx-auto-cache-clear.conf /etc/nginx/sites-available/meiyueart.com

# 创建软链接
sudo ln -sf /etc/nginx/sites-available/meiyueart.com /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载 Nginx
sudo nginx -s reload
```

### 步骤 2: 运行部署脚本

```bash
cd /workspace/projects/web-app
./deploy-auto-cache-clear.sh
```

### 步骤 3: 测试

1. 打开浏览器访问: `https://meiyueart.com/`
2. 打开开发者工具 (F12)
3. 查看 Console，应该看到 `[版本管理]` 和 `[SW]` 日志
4. 使用 `admin / admin123` 登录

✅ 完成！

## 📋 工作原理

### 用户访问流程

```
1. 用户访问网站
   ↓
2. 版本管理器加载，检测版本
   ↓
3. Service Worker 注册，控制缓存
   ↓
4. 如果版本不同，自动清除缓存并刷新
   ↓
5. 用户看到最新版本
```

### 核心机制

| 组件 | 作用 |
|------|------|
| **version-manager.js** | 检测版本变化，自动清除缓存 |
| **sw.js** | 控制网络请求和缓存策略 |
| **version.json** | 存储版本信息 |
| **Nginx 配置** | 禁用 HTML/JSON 缓存，允许静态资源长期缓存 |

## 🔄 日常更新流程

### 每次部署时

```bash
cd /workspace/projects/web-app
./deploy-auto-cache-clear.sh
```

脚本会自动：
1. ✅ 更新版本号
2. ✅ 构建前端
3. ✅ 部署到生产目录
4. ✅ 用户下次访问时自动更新

### 无需手动操作

- ❌ 不需要用户清理缓存
- ❌ 不需要硬刷新页面
- ❌ 不需要清除浏览器数据

## 🧪 测试自动更新

### 1. 修改版本号

```bash
cd /workspace/projects/web-app
sed -i "s/20260209-1000/20260209-1200/g" public/version.json
```

### 2. 重新部署

```bash
npm run build
rm -rf /var/www/frontend/*
cp -r dist/* /var/www/frontend/
```

### 3. 刷新浏览器

- 应该看到"系统更新中"的提示
- 页面自动刷新
- Console 显示新版本号

## 📁 文件结构

```
web-app/
├── public/
│   ├── sw.js                      # Service Worker
│   ├── version-manager.js         # 版本管理器
│   └── version.json               # 版本信息
├── nginx-auto-cache-clear.conf    # Nginx 配置
├── deploy-auto-cache-clear.sh     # 部署脚本
├── AUTO_CACHE_CLEAR_GUIDE.md      # 详细文档
└── QUICK_START.md                 # 本文档
```

## 🔧 配置说明

### 版本号位置

需要同时更新三个文件的版本号：

1. `public/version.json`
   ```json
   {
     "version": "20260209-1200"
   }
   ```

2. `public/version-manager.js`
   ```javascript
   const APP_VERSION = '20260209-1200'
   ```

3. `public/sw.js`
   ```javascript
   const VERSION = '20260209-1200'
   ```

### 缓存策略

| 文件类型 | 缓存策略 | 原因 |
|---------|---------|------|
| HTML | 不缓存 | 需要总是加载最新 |
| sw.js | 不缓存 | 需要总是加载最新 |
| version.json | 不缓存 | 需要总是检测最新版本 |
| JS/CSS | 长期缓存 | 文件名包含 hash，内容变化会自动失效 |
| 图片 | 长期缓存 | 内容很少变化 |

## ⚠️ 注意事项

### 1. 版本号格式

```
YYYYMMDD-HHMM
例如: 20260209-1000
```

### 2. 部署顺序

1. ✅ 先构建前端
2. ✅ 再部署到生产目录
3. ✅ 最后测试功能

### 3. HTTPS 要求

Service Worker 只能在以下环境下工作：
- HTTPS
- localhost
- 127.0.0.1

## 🎯 成功标志

### Console 日志

应该看到以下日志：

```
[版本管理] 脚本已加载，版本: 20260209-1000
[版本管理] 初始化，当前版本: 20260209-1000
[版本管理] Service Worker 注册成功: https://meiyueart.com/
[SW] Service Worker 已加载，版本: 20260209-1000
```

### Application → Service Workers

状态应该是：
- ✅ Service Worker 已激活
- ✅ 状态: Activated

### Network → Headers

关键文件应该包含：
```
Cache-Control: no-cache, no-store, must-revalidate
```

## 📞 问题排查

### Service Worker 未激活

```javascript
// 在浏览器 Console 中执行
navigator.serviceWorker.getRegistrations().then(registrations => {
  console.log(registrations)
})
```

### 清除所有缓存

```javascript
// 在浏览器 Console 中执行
caches.keys().then(keys => {
  return Promise.all(keys.map(key => caches.delete(key)))
}).then(() => {
  console.log('缓存已清除')
  location.reload(true)
})
```

### 查看当前版本

```javascript
// 在浏览器 Console 中执行
console.log('当前版本:', localStorage.getItem('lingzhi_app_version'))
fetch('/version.json').then(r => r.json()).then(d => console.log('服务器版本:', d.version))
```

## 📚 更多信息

查看详细文档：`AUTO_CACHE_CLEAR_GUIDE.md`

## ✅ 检查清单

部署完成后，确认以下事项：

- [ ] Nginx 配置已应用
- [ ] 前端已构建并部署
- [ ] 版本号已更新
- [ ] Service Worker 已激活
- [ ] Console 日志正常
- [ ] 登录功能正常
- [ ] 自动更新功能测试通过

全部勾选后，系统就正常运行了！🎉
