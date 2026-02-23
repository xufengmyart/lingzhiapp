# 自动缓存清除系统 - 使用文档

## 概述

本系统实现了一套完整的自动缓存清除机制，所有访问 `meiyueart.com` 的用户都能自动清除缓存并加载最新版本，无需手动操作。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                          │
│  ┌──────────────────────────────────────────────────┐  │
│  │  version-manager.js (版本管理器)                 │  │
│  │  - 检测版本变化                                   │  │
│  │  - 自动清除缓存                                   │  │
│  │  - 强制刷新页面                                   │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  Service Worker (sw.js)                          │  │
│  │  - 拦截网络请求                                   │  │
│  │  - 控制缓存策略                                   │  │
│  │  - 自动更新                                       │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                            ↓
                            ↓ 请求
                            ↓
┌─────────────────────────────────────────────────────────┐
│                      Nginx 服务器                        │
│  - HTML/JSON/SW: 禁用缓存                                │
│  - JS/CSS/图片: 长期缓存                                 │
│  - API: 不缓存                                            │
└─────────────────────────────────────────────────────────┘
                            ↓
                            ↓ 代理
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    前端应用 (React)                       │
│  - 版本信息: version.json                                │
│  - API 地址: http://localhost:8080                      │
└─────────────────────────────────────────────────────────┘
                            ↓
                            ↓ 调用
                            ↓
┌─────────────────────────────────────────────────────────┐
│                    后端服务 (Flask)                       │
│  - 端口: 8080                                            │
│  - 用户认证                                              │
│  - 业务逻辑                                              │
└─────────────────────────────────────────────────────────┘
```

## 核心文件

### 1. Service Worker (`public/sw.js`)

**功能**:
- 拦截网络请求，控制缓存策略
- HTML 文件：不缓存（network-only）
- API 请求：不缓存（network-only）
- 静态资源：缓存优先（cache-first）

**缓存策略**:
```javascript
- HTML 文件: network-only (总是从网络获取)
- API 请求: network-only (总是从网络获取)
- JS/CSS/图片: cache-first (优先使用缓存)
```

### 2. 版本管理器 (`public/version-manager.js`)

**功能**:
- 检测版本变化
- 自动清除所有缓存
- 强制刷新页面
- 定期检查更新（每5分钟）

**工作流程**:
```
1. 页面加载时读取版本号
2. 对比本地版本和服务器版本
3. 如果版本不同：
   - 清除所有缓存
   - 清除 localStorage/sessionStorage
   - 显示更新提示
   - 自动刷新页面
```

### 3. 版本信息 (`public/version.json`)

**格式**:
```json
{
  "version": "20260209-1000",
  "buildTime": "2026-02-09T10:00:00+08:00",
  "description": "自动缓存清除版本",
  "features": [
    "Service Worker 自动更新",
    "版本检测与自动刷新",
    "缓存自动清除"
  ]
}
```

### 4. Nginx 配置 (`nginx-auto-cache-clear.conf`)

**缓存策略**:
```nginx
- HTML 文件: no-cache, no-store, must-revalidate
- sw.js: no-cache, no-store, must-revalidate
- version.json: no-cache, no-store, must-revalidate
- version-manager.js: no-cache, no-store, must-revalidate
- JS/CSS/图片: public, immutable (1年)
- API: no-cache, no-store, must-revalidate
```

## 部署步骤

### 方法 1: 使用自动部署脚本（推荐）

```bash
cd /workspace/projects/web-app
chmod +x deploy-auto-cache-clear.sh
./deploy-auto-cache-clear.sh
```

脚本会自动完成：
1. ✅ 更新版本号
2. ✅ 构建前端
3. ✅ 部署到生产目录
4. ✅ 验证部署

### 方法 2: 手动部署

```bash
# 1. 进入前端目录
cd /workspace/projects/web-app

# 2. 更新版本号（修改以下文件）
# - public/version.json
# - public/version-manager.js (APP_VERSION)
# - public/sw.js (VERSION)

# 3. 构建前端
npm run build

# 4. 部署
rm -rf /var/www/frontend/*
cp -r dist/* /var/www/frontend/

# 5. 验证
ls -la /var/www/frontend/
```

## Nginx 配置

### 应用新的 Nginx 配置

```bash
# 1. 复制配置文件到 Nginx 目录
sudo cp /workspace/projects/web-app/nginx-auto-cache-clear.conf /etc/nginx/sites-available/meiyueart.com

# 2. 创建软链接（如果不存在）
sudo ln -sf /etc/nginx/sites-available/meiyueart.com /etc/nginx/sites-enabled/

# 3. 测试配置
sudo nginx -t

# 4. 重载 Nginx
sudo nginx -s reload

# 5. 重启 Nginx（如果需要）
sudo systemctl restart nginx
```

## 测试步骤

### 1. 清除浏览器缓存
- **Windows/Linux**: `Ctrl + Shift + Delete`
- **Mac**: `Cmd + Shift + Delete`

### 2. 访问网站
```
https://meiyueart.com/
```

### 3. 打开开发者工具 (F12)

#### Console 标签
应该看到以下日志：
```
[版本管理] 脚本已加载，版本: 20260209-1000
[版本管理] 初始化，当前版本: 20260209-1000
[版本管理] Service Worker 注册成功: https://meiyueart.com/
[SW] Service Worker 已加载，版本: 20260209-1000
[SW] 安装中... 20260209-1000
[SW] 缓存创建成功: lingzhi-ecosystem-20260209-1000
[SW] 激活中... 20260209-1000
```

#### Application 标签
1. 点击左侧 "Service Workers"
2. 应该看到一个已激活的 Service Worker
3. 状态应该是 "Activated"

#### Network 标签
1. 刷新页面
2. 查看 `version.json` 请求
3. Response Headers 应该包含：
   ```
   Cache-Control: no-cache, no-store, must-revalidate
   Pragma: no-cache
   Expires: 0
   ```

### 4. 测试自动更新

#### 模拟版本更新
```bash
# 1. 修改版本号
cd /workspace/projects/web-app
sed -i "s/20260209-1000/20260209-1100/g" public/version.json

# 2. 重新构建
npm run build

# 3. 部署
rm -rf /var/www/frontend/*
cp -r dist/* /var/www/frontend/
```

#### 验证自动更新
1. 刷新浏览器页面
2. 应该看到"系统更新中"的提示
3. 页面自动刷新
4. Console 显示新版本号

### 5. 测试登录功能
1. 使用账号: `admin / admin123`
2. 登录应该成功
3. 检查 Network 标签，确认 API 请求发送到 `http://localhost:8080`

## 常见问题

### Q1: Service Worker 注册失败

**症状**: Console 显示 `[SW] Service Worker 注册失败`

**原因**:
- 浏览器不支持 Service Worker
- HTTPS 配置问题
- 文件路径错误

**解决方案**:
1. 检查浏览器是否支持 Service Worker
2. 确保使用 HTTPS（localhost 除外）
3. 检查 `sw.js` 文件是否存在

### Q2: 版本检测不工作

**症状**: 版本更新后没有自动刷新

**原因**:
- `version.json` 被缓存
- 版本号未更新
- 网络请求失败

**解决方案**:
1. 检查 Nginx 配置，确保 `version.json` 禁用缓存
2. 确认版本号已更新
3. 检查 Console 日志，确认网络请求

### Q3: 缓存未清除

**症状**: 旧版本文件仍在使用

**原因**:
- Service Worker 未激活
- 浏览器缓存策略问题

**解决方案**:
1. 在 Application → Service Workers 中点击 "Unregister"
2. 刷新页面
3. 检查 Nginx 配置

### Q4: API 请求失败

**症状**: 登录失败，返回 401 错误

**原因**:
- API 地址配置错误
- 后端服务未启动
- 端口配置错误

**解决方案**:
1. 确认后端服务运行在 8080 端口
2. 检查 `.env.production` 配置
3. 查看 Nginx API 代理配置

## 版本发布流程

### 标准流程

```bash
# 1. 修改代码
# ... 开发新功能 ...

# 2. 运行部署脚本
./deploy-auto-cache-clear.sh

# 3. 脚本自动完成：
#    - 更新版本号
#    - 构建前端
#    - 部署到生产目录
#    - 验证部署

# 4. 用户下次访问时自动更新
```

### 快速流程（适用于小改动）

```bash
# 1. 修改代码

# 2. 构建和部署
cd /workspace/projects/web-app
npm run build
rm -rf /var/www/frontend/*
cp -r dist/* /var/www/frontend/

# 3. 注意：用户不会自动更新，需要手动刷新
```

## 维护建议

### 定期检查

1. **每月检查一次**:
   - Service Worker 激活状态
   - 版本号是否正确更新
   - 缓存策略是否生效

2. **每次部署后**:
   - 验证版本号
   - 测试自动更新功能
   - 检查 Console 日志

3. **性能监控**:
   - 监控页面加载时间
   - 检查缓存命中率
   - 优化资源加载

### 故障排查

1. **查看日志**:
   ```bash
   # 浏览器 Console
   # Nginx 日志: /var/log/nginx/meiyueart-*.log
   # 后端日志: /workspace/projects/admin-backend/backend.log
   ```

2. **清除缓存**:
   ```javascript
   // 在浏览器 Console 中执行
   caches.keys().then(keys => {
     return Promise.all(keys.map(key => caches.delete(key)))
   })
   ```

3. **注销 Service Worker**:
   ```javascript
   // 在浏览器 Console 中执行
   navigator.serviceWorker.getRegistrations().then(registrations => {
     registrations.forEach(registration => registration.unregister())
   })
   ```

## 总结

本自动缓存清除系统实现了：

✅ **无需用户操作**: 所有缓存清除和更新自动完成
✅ **自动版本检测**: 定期检查版本变化
✅ **智能缓存策略**: HTML/API 不缓存，静态资源长期缓存
✅ **平滑更新**: 显示友好的更新提示
✅ **易于维护**: 自动化部署脚本，简化发布流程

用户无需手动清理缓存，系统会自动处理所有更新流程！
