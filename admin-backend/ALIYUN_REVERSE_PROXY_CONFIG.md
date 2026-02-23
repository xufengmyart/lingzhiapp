# 阿里云 ECS 配置反向代理完整指南

## 问题诊断

经过测试，发现当前架构如下：

```
用户请求
  ↓
[云服务商 Nginx] ← 问题所在！
  - 监听 80 (HTTP)
  - 监听 443 (HTTPS)
  - 拦截所有请求
  - 返回 401 或重定向
  ↓
[容器内 Nginx] ← 我们的配置
  - 监听 80
  - 监听 443
  - 已配置反向代理
  ↓
[Gunicorn + Flask]
  - 监听 8080
```

**关键发现：** 云服务商的 Nginx 在容器外，我们的 Nginx 在容器内。外部 Nginx 先拦截请求，因此我们的配置无法生效。

---

## 解决方案

### 方案 1: 配置云服务商的 Nginx（推荐）

这是最彻底的解决方案，需要联系阿里云技术支持。

#### 提交工单的信息

**工单主题：** `紧急 - 容器内 ECS 实例需要配置反向代理`

**问题描述：**

```
我的 ECS 实例运行在 Docker 容器中，容器内已配置 Nginx 反向代理（监听 80/443 端口）。
但是容器外的阿里云 Nginx 代理层拦截了所有请求，导致无法正常访问。

当前情况：
1. 容器内 Nginx 已正确配置，监听 80/443 端口
2. 容器内 Nginx 已配置 /api/ 路径的反向代理到 8080 端口
3. 本地访问（127.0.0.1）正常工作
4. 但外部访问被云服务商 Nginx 拦截

期望的配置：
- 取消对 /api/* 路径的拦截
- 或者将请求转发到容器内的 Nginx（80/443 端口）
- 或者直接将 /api/* 转发到容器内的 8080 端口

实例信息：
- 实例 ID：[您的实例 ID]
- 公网 IP：123.56.142.143
- 域名：meiyueart.com
- 容器内 Nginx 配置：/etc/nginx/sites-available/meiyueart-https.conf
```

**配置要求：**

请云服务商配置以下规则：

```nginx
# 方式 1：转发到容器内 Nginx
location /api/ {
    proxy_pass http://127.0.0.1:80/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# 方式 2：直接转发到后端 8080 端口
location /api/ {
    proxy_pass http://127.0.0.1:8080/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# 方式 3：取消拦截，所有请求转发到容器内 Nginx
location / {
    proxy_pass http://127.0.0.1:80/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

---

### 方案 2: 使用阿里云 SLB（负载均衡）

如果云服务商无法配置 Nginx，可以使用阿里云 SLB。

#### 步骤 1: 创建 SLB 实例

1. 登录阿里云控制台
2. 进入"负载均衡" → "传统型负载均衡 CLB"
3. 点击"创建实例"
4. 选择地域：与 ECS 相同
5. 选择实例类型：私网或公网（根据需求）
6. 选择规格：按需选择
7. 点击"立即购买"

#### 步骤 2: 配置监听

1. 进入 SLB 实例详情
2. 点击"添加监听"
3. 配置 HTTP 监听：
   - 监听协议：HTTP
   - 监听端口：80
   - 转发策略：轮询
   - 健康检查：开启，HTTP /health

4. 配置 HTTPS 监听（如果需要 SSL）：
   - 监听协议：HTTPS
   - 监听端口：443
   - SSL 证书：上传或选择证书
   - 转发策略：轮询
   - 健康检查：开启，HTTPS /health

#### 步骤 3: 添加后端服务器

1. 进入 SLB 实例详情
2. 点击"添加后端服务器"
3. 选择您的 ECS 实例
4. 端口：80
5. 权重：100
6. 点击"添加"

#### 步骤 4: 配置转发规则

1. 进入"监听配置" → "转发规则"
2. 添加规则：
   - 域名：meiyueart.com
   - URL 路径：/api/*
   - 转发目标：选择 ECS 实例
   - 端口：80
   - 健康检查：HTTP /api/health

#### 步骤 5: 修改域名解析

将域名 `meiyueart.com` 的 A 记录指向 SLB 的公网 IP。

---

### 方案 3: 使用阿里云 API 网关

更高级的方案，提供更强的功能。

#### 步骤 1: 创建 API 网关

1. 进入"云原生 API 网关"
2. 创建网关实例
3. 选择地域和规格

#### 步骤 2: 创建 API 分组

1. 进入"API 管理" → "分组"
2. 创建分组，命名为 `meiyueart-api`

#### 步骤 3: 创建 API

1. 进入"API 管理" → "API 列表"
2. 点击"创建 API"
3. 配置：
   - API 名称：Login API
   - 请求路径：/api/login
   - 请求方法：POST
   - 安全认证：无认证（或根据需求选择）
   - 后端服务：HTTP
   - 后端地址：http://127.0.0.1:8080/api/login
   - 后端请求方法：POST
4. 点击"发布"

#### 步骤 4: 绑定域名

1. 进入"域名管理"
2. 绑定域名：api.meiyueart.com（或使用主域名）
3. 配置 DNS 解析

---

### 方案 4: 临时绕过方案（快速解决）

如果需要快速上线，可以使用 8080 端口直接访问。

#### 步骤 1: 开放 8080 端口

1. 进入 ECS 实例详情
2. 点击"安全组"
3. 点击"配置规则"
4. 添加入方向规则：
   - 规则方向：入方向
   - 授权策略：允许
   - 协议类型：自定义 TCP
   - 端口范围：8080/8080
   - 授权对象：0.0.0.0/0
   - 描述：Flask Backend API

#### 步骤 2: 修改前端配置

修改前端 API 基础 URL：

```javascript
// 原配置
const API_BASE_URL = 'https://meiyueart.com/api';

// 临时配置
const API_BASE_URL = 'http://123.56.142.143:8080/api';
```

或者在 `.env` 文件中：

```bash
VITE_API_BASE_URL=http://123.56.142.143:8080/api
```

#### 步骤 3: 重新构建并部署

```bash
npm run build
# 将构建产物部署到服务器
```

---

## 验证配置

### 测试本地 Nginx（应该成功）

```bash
curl -X POST https://127.0.0.1/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  --insecure
```

### 测试域名访问（配置成功后应该成功）

```bash
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  --insecure
```

### 测试 SLB（如果配置了 SLB）

```bash
curl -X POST http://<SLB-IP>/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 当前状态

### 已完成的工作

- ✅ 容器内 Nginx 已配置（监听 80/443）
- ✅ 反向代理规则已配置（/api/ → 127.0.0.1:8080/api/）
- ✅ SSL 证书已配置（自签名）
- ✅ 本地测试成功（127.0.0.1）
- ✅ CORS 已配置
- ✅ Gunicorn 运行正常（8080 端口）

### 待完成的工作

- ⏳ 配置云服务商 Nginx 代理规则（需要联系技术支持）
- 或
- ⏳ 配置 SLB 负载均衡
- 或
- ⏳ 开放 8080 端口（临时方案）

---

## 推荐方案优先级

| 方案 | 优点 | 缺点 | 优先级 | 时间成本 |
|------|------|------|--------|---------|
| 配置云服务商 Nginx | 最彻底，无额外成本 | 需要技术支持 | ⭐⭐⭐⭐⭐ | 2-4 小时 |
| 使用 SLB | 稳定、可扩展 | 需要额外费用 | ⭐⭐⭐⭐ | 30 分钟 |
| 使用 API 网关 | 功能强大、安全 | 配置复杂、费用高 | ⭐⭐⭐ | 1 小时 |
| 开放 8080 端口 | 快速、简单 | 不安全、临时 | ⭐⭐ | 10 分钟 |

---

## 下一步行动

1. **立即行动（临时方案）：**
   - 开放 8080 端口
   - 修改前端配置
   - 测试并上线

2. **本周内（推荐方案）：**
   - 提交工单，要求配置云服务商 Nginx
   - 或配置 SLB 负载均衡
   - 改回原前端配置

3. **长期优化：**
   - 申请正式 SSL 证书（阿里云免费证书）
   - 配置 CDN 加速
   - 配置监控和告警

---

## 联系阿里云技术支持

### 工单类型
- 产品：云服务器 ECS
- 问题类型：配置与管理
- 紧急程度：高（生产环境）

### 提供的信息
- 实例 ID：[您的实例 ID]
- 公网 IP：123.56.142.143
- 域名：meiyueart.com
- 容器内 Nginx 配置：/etc/nginx/sites-available/meiyueart-https.conf
- 当前问题：云服务商 Nginx 拦截请求，无法访问容器内服务

### 期望的解决方案
取消对 /api/* 路径的拦截，或将请求转发到容器内 Nginx（80/443 端口）。

---

## 附录：配置文件

### 容器内 Nginx 配置

位置：`/etc/nginx/sites-available/meiyueart-https.conf`

内容：已配置 HTTPS 监听 443 端口，/api/ 路径反向代理到 8080 端口。

### 后端配置

- Gunicorn：监听 0.0.0.0:8080
- Flask：已配置 CORS
- 数据库：SQLite（本地文件）

---

**提示：** 建议优先尝试联系阿里云技术支持，这是最彻底、成本最低的解决方案。如果急需上线，可以先使用方案 4（开放 8080 端口）作为临时方案。
