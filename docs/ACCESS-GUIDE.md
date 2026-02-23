# 🚀 灵值生态园 - 访问指南

## ⚠️ 重要提示

**当前域名 `meiyueart.com` 无法访问，请使用以下临时域名：**

---

## ✅ 立即访问

### 方式 1：直接访问（推荐）

点击下方链接进入系统：

```
https://f8ab8c28-f515-4fa3-9fb4-0ca0c3a0d34f.dev.coze.site
```

### 方式 2：访问引导页面

在浏览器中打开以下文件查看详细引导：

```
public/access-guide.html
```

---

## 🔑 登录账号

- **用户名**: `admin`
- **密码**: `admin123`

---

## 📊 系统状态

| 服务 | 状态 | 地址 |
|------|------|------|
| Flask 后端 | ✅ 运行中 | `0.0.0.0:8080` |
| Coze 运行时 | ✅ 运行中 | `0.0.0.0:9000` |
| 临时域名 | ✅ 可用 | `f8ab8c28-...-dev.coze.site` |

### 数据统计

- 项目数量：**10 个**
- 商家数量：**10 个**
- 用户数量：**32 个**
- 数据库大小：**956 KB**

---

## ❓ 为什么无法访问 meiyueart.com？

### 问题原因

```
用户访问: https://meiyueart.com
    ↓
域名解析: 123.56.142.143（公网 IP）
    ↓
实际服务器: 9.128.106.115（Coze 容器内部 IP）
    ↓
❌ IP 不匹配，无法连接
```

### 检查命令

```bash
nslookup meiyueart.com
```

输出：
```
Server:  100.96.0.2
Address: 100.96.0.2#53

Non-authoritative answer:
Name:    meiyueart.com
Address: 123.56.142.143  # ← 这个 IP 不是服务器实际 IP
```

---

## 🛠️ 长期解决方案

### 方案 A：配置 CNAME 记录（推荐）

在域名服务商（阿里云、腾讯云等）处添加 CNAME 记录：

```
类型: CNAME
主机记录: @ / www
记录值: f8ab8c28-f515-4fa3-9fb4-0ca0c3a0d34f.dev.coze.site
TTL: 600
```

### 方案 B：A 记录

如果 Coze 平台提供公网 IP，添加 A 记录：

```
类型: A
主机记录: @ / www
记录值: [Coze平台公网IP]
TTL: 600
```

### 方案 C：更换域名解析服务商

如果当前 DNS 服务商不支持 CNAME 记录，可以考虑：
- Cloudflare（免费，支持 CNAME flattening）
- 腾讯云 DNSPod
- 阿里云 DNS

---

## 🔧 技术架构

```
外部 HTTPS (443)
    ↓
Coze 运行时 (9000)
    ↓
Flask 后端 (8080)
    ↓
SQLite 数据库
```

### 服务启动命令

```bash
cd /workspace/projects/admin-backend
nohup python3 app.py > /tmp/flask.log 2>&1 &
```

### 查看日志

```bash
# Flask 日志
tail -f /tmp/flask.log

# 系统日志
tail -f /app/work/logs/bypass/app.log
```

---

## 📝 系统功能

- ✅ 用户资源池管理
- ✅ 项目资源池（10 个项目）
- ✅ 商家资源池（10 个商家）
- ✅ 分红池系统
- ✅ 智能体对话（集成 LangChain）
- ✅ 数据分析
- ✅ 用户旅程追踪
- ✅ 通知系统
- ✅ 区块链集成
- ✅ 数字资产系统

---

## 🎯 快速测试

### 本地测试

```bash
# 健康检查
curl http://127.0.0.1:8080/api/health

# 项目列表
curl http://127.0.0.1:8080/api/projects

# 商家列表
curl http://127.0.0.1:8080/api/merchants
```

### 运行测试脚本

```bash
bash scripts/test-access.sh
```

---

## 🆘 故障排查

### 问题 1：访问 502 错误

**原因**: 域名解析 IP 与服务器 IP 不匹配

**解决**: 使用 Coze 临时域名访问

### 问题 2：Flask 服务未启动

**检查**:
```bash
ps aux | grep "python.*app.py"
```

**启动**:
```bash
cd admin-backend
python3 app.py
```

### 问题 3：端口被占用

**检查**:
```bash
lsof -i :8080
```

**解决**: 停止占用进程或更换端口

---

## 📞 需要帮助？

如遇到问题，请提供：

1. 访问的 URL
2. 错误信息（截图或日志）
3. 浏览器控制台输出（F12）

---

*文档版本: v1.0*
*更新时间: 2025-02-10 21:50*
