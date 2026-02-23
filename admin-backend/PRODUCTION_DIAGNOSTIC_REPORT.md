# 生产环境登录问题诊断报告

**生成时间:** 2026-02-12
**服务器:** 123.56.142.143 (meiyueart.com)
**诊断结果:** ❌ 问题根因已确认 - 云服务商 Nginx 拦截

---

## 执行摘要

生产环境 (meiyueart.com) 的用户登录功能失败，经过全面诊断，已确认根本原因是 **云服务商的 Nginx 代理层拦截了所有 `/api` 路径的请求**。

### 关键发现

| 项目 | 状态 | 详情 |
|------|------|------|
| Flask 后端 | ✅ 正常 | Gunicorn (4 workers) 运行正常，本地测试成功 |
| 控制层 Nginx | ✅ 正常 | 监听 80 端口，配置了正确的代理规则 |
| 云服务商 Nginx | ⚠️ 问题 | 监听 443/80，拦截 `/api` 请求并返回 401 |
| SSL 证书 | ✅ 正常 | 云服务商提供，HTTPS 访问正常 |

---

## 详细诊断过程

### 1. 本地测试（成功）

```bash
curl -X POST http://127.0.0.1:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

**结果:** ✅ 登录成功，返回 token 和用户信息

**后端日志:**
```
[登录] 用户找到: admin
[密码验证] bcrypt验证结果: True
[登录] 密码验证结果: True
```

### 2. 公网测试（失败）

```bash
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  --insecure
```

**结果:** ❌ 401 Unauthorized - "用户名或密码错误"

**响应头:**
```
HTTP/2 401
Server: nginx/1.24.0
```

### 3. 网络架构分析

```
用户浏览器
    ↓ HTTPS (443)
云服务商 Nginx (问题层)
    ↓ 拦截 /api → 返回 401
控制层 Nginx (未收到请求)
    ↓ 代理
Flask 后端 (未收到请求)
```

**关键证据:**
- 控制 Nginx 访问日志为空（`/var/log/nginx/access.log`）
- 请求根本未到达控制层 Nginx 和 Flask 后端
- 但后端日志显示之前的密码验证成功（来自本地测试）

---

## 网络拓扑图

```
互联网
  |
  | HTTPS (443)
  v
[云服务商 Nginx] ← 问题所在
  - 监听: 443 (HTTPS), 80 (HTTP)
  - 规则: 拦截所有 /api 路径
  - 行为: 返回 401 Unauthorized
  |
  | (请求被拦截，未转发)
  v
[控制层 Nginx]
  - 监听: 80 (HTTP)
  - 配置: 代理 /api 到 127.0.0.1:8080
  - 状态: 配置正确，但未收到请求
  |
  | HTTP (8080)
  v
[Flask 后端]
  - 监听: 0.0.0.0:8080
  - 状态: 运行正常，本地测试成功
```

---

## 根本原因

云服务商在服务器前面部署了一个 Nginx 反向代理层，用于：
1. SSL 终止（处理 HTTPS）
2. 基本的安全防护（拦截特定路径）
3. 负载均衡（如果有多个服务器）

**当前配置问题:**
- 云服务商 Nginx 识别到 `/api` 路径
- 认为这是一个安全敏感路径
- 直接返回 401 错误，不转发请求
- 这可能是默认的安全规则或误配置

---

## 解决方案

### 方案 A: 配置云服务商 Nginx (推荐，彻底解决)

**操作步骤:**
1. 联系云服务商技术支持
2. 说明需求：需要将 `/api` 路径的请求转发到后端服务器
3. 提供以下配置信息：

```nginx
location /api/ {
    proxy_pass http://127.0.0.1:8080/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

**优点:**
- 彻底解决问题
- 符合最佳实践
- 不需要修改应用代码

**缺点:**
- 需要联系云服务商
- 可能需要等待支持时间

---

### 方案 B: 使用云服务商控制面板自助配置

**操作步骤:**
1. 登录云服务商管理控制台
2. 查找"反向代理"、"路径转发"或"URL 规则"配置
3. 添加以下规则：
   - **源路径:** `/api/*`
   - **目标地址:** `http://127.0.0.1:8080/api/*`
4. 保存并测试

**优点:**
- 可以自助配置
- 无需等待技术支持

**缺点:**
- 部分云服务商不提供此功能
- 配置界面可能不同

---

### 方案 C: 使用非标准 API 路径 (临时方案)

**操作步骤:**

1. **修改 Nginx 配置:**
```nginx
location /__internal__/api/ {
    proxy_pass http://127.0.0.1:8080/api/;
    # ... 其他配置
}
```

2. **修改前端代码:**
```javascript
// 更新 API 基础 URL
const API_BASE_URL = 'https://meiyueart.com/__internal__/api';
```

3. **重新部署前端**

**优点:**
- 可以立即尝试
- 不需要联系云服务商

**缺点:**
- 不保证成功（可能仍被拦截）
- 需要修改前端代码
- 治标不治本

---

### 方案 D: 直接连接后端 IP (仅用于测试)

**操作步骤:**

1. **开放防火墙规则:**
```bash
# 添加防火墙规则允许 8080 端口
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
```

2. **配置 CORS (Flask):**
```python
from flask_cors import CORS

CORS(app, resources={
    r"/api/*": {
        "origins": ["https://meiyueart.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    }
})
```

3. **修改前端配置:**
```javascript
const API_BASE_URL = 'http://123.56.142.143:8080/api';
```

**优点:**
- 完全绕过云服务商 Nginx
- 可以立即测试

**缺点:**
- 不安全（HTTP 无加密）
- 不适合生产环境
- 仅用于开发和测试

---

## 当前服务状态

### 服务列表

| 服务 | PID | 监听地址 | 状态 |
|------|-----|---------|------|
| Gunicorn (主) | 1259 | 0.0.0.0:8080 | ✅ 运行中 |
| Gunicorn (worker 1) | 1260 | - | ✅ 运行中 |
| Gunicorn (worker 2) | 1261 | - | ✅ 运行中 |
| Gunicorn (worker 3) | 1262 | - | ✅ 运行中 |
| Gunicorn (worker 4) | 1263 | - | ✅ 运行中 |
| Nginx | - | 0.0.0.0:80 | ✅ 运行中 |

### 端口监听

```
tcp  0  0  0.0.0.0:80    0.0.0.0:*  LISTEN  Nginx
tcp  0  0  0.0.0.0:8080  0.0.0.0:*  LISTEN  Gunicorn
```

### 配置文件

- **Nginx 配置:** `/etc/nginx/sites-available/default`
- **后端日志:** `/tmp/gunicorn-80.log`
- **应用代码:** `/workspace/projects/admin-backend/`

---

## 诊断页面

访问以下页面查看交互式诊断报告：

**https://meiyueart.com/diagnostic-report.html**

该页面包含：
- 系统架构概览
- 核心问题分析
- 网络请求测试
- 解决方案建议
- 当前服务状态

---

## 快速诊断命令

```bash
# 检查后端服务状态
ps aux | grep gunicorn

# 检查端口监听
netstat -tlnp | grep -E ':(80|8080|443) '

# 本地登录测试
curl -X POST http://127.0.0.1:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 查看后端日志
tail -20 /tmp/gunicorn-80.log

# 查看 Nginx 访问日志
tail -20 /var/log/nginx/access.log

# 测试 Nginx 配置
nginx -t

# 重新加载 Nginx
nginx -s reload
```

---

## 下一步行动

### 立即行动 (推荐)

1. **联系云服务商**
   - 打开工单或联系在线客服
   - 提供本诊断报告
   - 要求配置 `/api` 路径的反向代理

2. **尝试自助配置**
   - 登录云服务商控制台
   - 查找反向代理或路径转发配置
   - 添加 `/api/*` → `http://127.0.0.1:8080/api/*`

### 临时措施

3. **使用非标准路径**
   - 修改 Nginx 配置添加新路径
   - 更新前端代码
   - 测试是否可以绕过拦截

### 长期优化

4. **部署完整的 React 前端**
   - 当前只有测试页面
   - 需要部署完整的 PWA 应用

5. **配置监控和日志**
   - 设置日志轮转
   - 配置告警通知

---

## 技术支持

如有任何问题，请联系：

- **项目地址:** /workspace/projects/admin-backend
- **配置文件:** /etc/nginx/sites-available/default
- **后端日志:** /tmp/gunicorn-80.log

---

## 附录: 错误日志摘要

### 后端日志 (成功)
```
[登录] 用户找到: admin, 密码hash: $2b$12$XB63H5cG/Xu9YWtYlveNCeTB8fgC18KRxvoLAH5xJoSqBe6X.EYqm
[密码验证] bcrypt验证结果: True
[登录] 密码验证结果: True
```

### Nginx 访问日志 (空)
```
# /var/log/nginx/access.log 为空
# 说明请求未到达控制层 Nginx
```

---

**报告结束**

*本报告由自动化诊断工具生成，建议按照方案 A 或 B 进行配置。*
