# 前端配置指南 - 绕过云服务商拦截

## 问题说明

云服务商的 Nginx 拦截了所有 API 请求，导致前端无法正常调用后端接口。

## 解决方案：前端直接连接后端 8080 端口

### 方案 A: 修改 API 基础 URL（推荐）

#### 1. 找到前端配置文件

在项目中查找以下文件之一：
- `.env` (环境变量文件)
- `.env.development` (开发环境配置)
- `.env.production` (生产环境配置)
- `src/config.js` 或 `src/config.ts` (配置文件)
- `src/api/config.js` 或 `src/api/config.ts` (API 配置文件)

#### 2. 修改 API 基础 URL

```javascript
// 原配置（被拦截）
const API_BASE_URL = 'https://meiyueart.com/api';

// 新配置（绕过云服务商）
const API_BASE_URL = 'http://123.56.142.143:8080/api';
```

或者在 `.env` 文件中：

```bash
# 原配置
VITE_API_BASE_URL=https://meiyueart.com/api

# 新配置
VITE_API_BASE_URL=http://123.56.142.143:8080/api
```

#### 3. 重新构建前端

```bash
# 如果使用 Vite
npm run build

# 如果使用 Webpack
npm run build
```

#### 4. 部署前端

将构建产物复制到服务器：

```bash
# 假设构建产物在 dist 目录
cp -r dist/* /var/www/meiyueart-v2/
```

---

### 方案 B: 使用配置切换（更灵活）

创建一个配置切换机制，允许在不同环境下使用不同的 API 地址：

```javascript
// src/config/api.js

const API_CONFIG = {
  development: 'http://127.0.0.1:8080/api',  // 本地开发
  production: 'http://123.56.142.143:8080/api',  // 生产环境
  // 如果将来云服务商配置好了，可以改回：
  // production: 'https://meiyueart.com/api',
};

const ENV = import.meta.env.MODE || 'production';
export const API_BASE_URL = API_CONFIG[ENV];
```

---

### 方案 C: 使用环境变量（最佳实践）

#### 1. 创建 `.env.production`

```bash
# .env.production
VITE_API_BASE_URL=http://123.56.142.143:8080/api
```

#### 2. 在代码中使用

```javascript
// src/utils/request.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export async function login(username, password) {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  return response.json();
}
```

#### 3. 构建时使用生产环境配置

```bash
npm run build
```

---

## 临时测试方案

如果只是想快速测试，可以直接在浏览器控制台中修改：

```javascript
// 临时覆盖 API 配置
localStorage.setItem('api_base_url', 'http://123.56.142.143:8080/api');

// 或者在页面加载前注入
window.API_BASE_URL = 'http://123.56.142.143:8080/api';
```

---

## 安全注意事项

### ⚠️ HTTP vs HTTPS

使用 `http://123.56.142.143:8080` 意味着：
- ❌ 数据传输未加密
- ❌ 密码和 token 可能被窃取
- ❌ 不适合生产环境

**解决方案：**
1. 为 8080 端口配置 SSL 证书
2. 使用云服务商提供的负载均衡
3. 或者等待云服务商配置好反向代理

### ✅ 最佳实践

长期解决方案应该是：
1. 联系云服务商，配置反向代理
2. 使用 HTTPS 访问
3. 不需要修改前端配置

---

## 完整示例

### 示例 1: React + Vite

```javascript
// .env.production
VITE_API_BASE_URL=http://123.56.142.143:8080/api

// src/api/index.js
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const api = {
  login: async (username, password) => {
    const response = await fetch(`${API_BASE_URL}/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    });
    return response.json();
  },

  // 其他 API 方法...
};
```

### 示例 2: Vue 3

```javascript
// .env.production
VITE_API_BASE_URL=http://123.56.142.143:8080/api

// src/api/index.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api';

export const login = async (username: string, password: string) => {
  const response = await fetch(`${API_BASE_URL}/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  });
  return response.json();
};
```

---

## 验证配置

配置完成后，测试 API 是否可以正常访问：

```javascript
// 在浏览器控制台中运行
fetch('http://123.56.142.143:8080/api/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ username: 'admin', password: 'admin123' }),
})
  .then(r => r.json())
  .then(data => console.log(data));
```

如果返回：
```json
{
  "success": true,
  "message": "登录成功",
  "data": { ... }
}
```

说明配置成功！

---

## 回滚方案

如果云服务商配置好了反向代理，可以改回原配置：

```javascript
// 改回使用 HTTPS
const API_BASE_URL = 'https://meiyueart.com/api';
```

---

## 故障排查

### 问题 1: CORS 错误

```
Access to XMLHttpRequest at 'http://123.56.142.143:8080/api/login'
from origin 'https://meiyueart.com' has been blocked by CORS policy
```

**解决方案：**
- 后端已经配置了 CORS（已完成）
- 确保 Flask 正确处理 OPTIONS 预检请求

### 问题 2: 混合内容错误

```
Mixed Content: The page at 'https://meiyueart.com' was loaded over HTTPS,
but requested an insecure resource 'http://123.56.142.143:8080/api/login'
```

**解决方案：**
- 为 8080 端口配置 SSL 证书
- 或者在浏览器中允许混合内容（不推荐）

### 问题 3: 连接超时

```
Failed to fetch: Network request failed
```

**解决方案：**
- 检查云服务商防火墙是否开放了 8080 端口
- 联系云服务商技术支持

---

## 下一步

1. ✅ 修改前端配置
2. ✅ 重新构建前端
3. ✅ 部署前端
4. ✅ 测试登录功能
5. ⏳ 联系云服务商，配置反向代理
6. ⏳ 改回 HTTPS 配置

---

**提示**: 这是一个临时解决方案。长期来看，还是应该让云服务商配置好反向代理，使用 HTTPS 访问。
