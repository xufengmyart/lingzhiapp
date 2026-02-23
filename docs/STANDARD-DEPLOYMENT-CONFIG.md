# 灵值生态园 - 标准部署配置文档

> **版本**: v2.0  
> **最后更新**: 2026-02-11  
> **用途**: 标准化部署、防止服务停止、快速故障恢复

---

## 📋 目录

1. [环境信息](#环境信息)
2. [系统架构](#系统架构)
3. [部署清单](#部署清单)
4. [服务配置](#服务配置)
5. [自动化脚本](#自动化脚本)
6. [故障恢复](#故障恢复)
7. [监控和维护](#监控和维护)
8. [安全配置](#安全配置)

---

## 🌐 环境信息

### 服务器信息

| 项目 | 配置 |
|------|------|
| 生产服务器 IP | 123.56.142.143 |
| 域名 | meiyueart.com |
| 操作系统 | Ubuntu 20.04+ |
| Python 版本 | 3.8+ |
| Nginx 版本 | 1.18+ |

### 端口配置

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| Nginx HTTP | 80 | HTTP | 重定向到 HTTPS |
| Nginx HTTPS | 443 | HTTPS | 前端和 API |
| Flask API | 8080 | HTTP | 后端 API 服务 |

### 目录结构

```
/var/www/meiyueart/
├── backend/              # Flask 后端
│   ├── app.py           # 主应用文件
│   ├── requirements.txt # Python 依赖
│   ├── venv/            # Python 虚拟环境
│   └── ecosystem.config.json  # PM2 配置（可选）
├── web-app/             # React 前端
│   └── dist/            # 构建产物
├── scripts/             # 部署脚本
│   ├── complete-deploy-and-fix.sh    # 完整部署脚本
│   ├── diagnose-and-fix.sh          # 诊断修复脚本
│   └── deploy-to-aliyun.sh          # 阿里云部署脚本
├── config/              # 配置文件
│   └── flask-app.service            # systemd 服务配置
└── logs/                # 日志目录（软链接到 /var/log）
```

---

## 🏗️ 系统架构

```
用户浏览器
    │
    ▼
┌─────────────────────────────────────┐
│  Nginx (端口 80/443)                │
│  ├─ SSL 终止                        │
│  ├─ 静态文件服务（前端）            │
│  └─ API 反向代理                    │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  Flask API (端口 8080)              │
│  ├─ 应用逻辑                         │
│  ├─ 数据库操作                       │
│  └─ 业务处理                         │
└─────────────────────────────────────┘
    │
    ▼
┌─────────────────────────────────────┐
│  SQLite 数据库                      │
└─────────────────────────────────────┘
```

---

## ✅ 部署清单

### 首次部署

```bash
# 1. SSH 登录到服务器
ssh root@123.56.142.143

# 2. 上传代码（在本地执行）
scp -r backend root@123.56.142.143:/var/www/meiyueart/
scp -r web-app/dist root@123.56.142.143:/var/www/meiyueart/
scp -r scripts root@123.56.142.143:/var/www/meiyueart/
scp -r config root@123.56.142.143:/var/www/meiyueart/

# 3. 运行完整部署脚本（在服务器上执行）
cd /var/www/meiyueart
bash scripts/complete-deploy-and-fix.sh
```

### 快速修复（服务停止）

```bash
# SSH 登录
ssh root@123.56.142.143

# 方案 A: 使用 systemd
systemctl restart flask-app

# 方案 B: 使用诊断脚本
cd /var/www/meiyueart
bash scripts/diagnose-and-fix.sh

# 方案 C: 完整重新部署
cd /var/www/meiyueart
bash scripts/complete-deploy-and-fix.sh
```

---

## ⚙️ 服务配置

### systemd 服务配置

**文件路径**: `/etc/systemd/system/flask-app.service`

```ini
[Unit]
Description=Flask Application - MeiyueArt Ecosystem
After=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/meiyueart/backend
Environment="PATH=/var/www/meiyueart/backend/venv/bin"
ExecStart=/var/www/meiyueart/backend/venv/bin/python app.py
Restart=always
RestartSec=10s
StandardOutput=append:/var/log/flask-app.log
StandardError=append:/var/log/flask-app-error.log

[Install]
WantedBy=multi-user.target
```

**关键配置说明**:
- `Restart=always`: 服务崩溃后自动重启
- `RestartSec=10s`: 重启前等待 10 秒
- `StandardOutput/StandardError`: 日志输出到文件

### Nginx 配置

**文件路径**: `/etc/nginx/sites-available/meiyueart.com`

**关键配置**:
- HTTP (80) 重定向到 HTTPS
- SSL 证书配置
- 静态文件服务
- API 反向代理

### PM2 配置（可选）

**文件路径**: `/var/www/meiyueart/backend/ecosystem.config.json`

```json
{
  "apps": [
    {
      "name": "flask-app",
      "script": "app.py",
      "interpreter": "python3",
      "autorestart": true,
      "max_restarts": 10,
      "restart_delay": 4000
    }
  ]
}
```

---

## 🤖 自动化脚本

### 1. 完整部署脚本

**路径**: `scripts/complete-deploy-and-fix.sh`

**功能**:
- ✅ 检查 root 权限
- ✅ 创建应用目录
- ✅ 设置 Python 虚拟环境
- ✅ 生成 SSL 证书
- ✅ 配置 Nginx
- ✅ 配置 systemd 服务
- ✅ 启动服务
- ✅ 验证服务状态
- ✅ 配置防火墙

**使用方法**:
```bash
cd /var/www/meiyueart
bash scripts/complete-deploy-and-fix.sh
```

### 2. 诊断修复脚本

**路径**: `scripts/diagnose-and-fix.sh`

**功能**:
- 🔍 检查 Nginx 服务
- 🔍 检查 Flask 服务
- 🔍 检查端口占用
- 🔍 检查 SSL 证书
- 🔍 测试外网访问
- 📊 生成诊断报告
- 🛠️ 自动尝试修复

**使用方法**:
```bash
cd /var/www/meiyueart
bash scripts/diagnose-and-fix.sh
```

---

## 🚨 故障恢复

### 故障场景 1: Flask 服务停止

**症状**: 502 Bad Gateway

**诊断**:
```bash
# 检查服务状态
systemctl status flask-app

# 检查日志
journalctl -u flask-app -n 50

# 检查端口
lsof -i :8080
```

**修复**:
```bash
# 重启服务
systemctl restart flask-app

# 查看日志
journalctl -u flask-app -f
```

### 故障场景 2: Nginx 服务停止

**症状**: 无法访问网站

**诊断**:
```bash
# 检查服务状态
systemctl status nginx

# 检查配置
nginx -t

# 检查日志
tail -f /var/log/nginx/error.log
```

**修复**:
```bash
# 重启服务
systemctl restart nginx

# 如果配置错误，修复后重载
nginx -t
systemctl reload nginx
```

### 故障场景 3: SSL 证书问题

**症状**: 浏览器显示 SSL 证书错误

**诊断**:
```bash
# 检查证书
ls -la /etc/nginx/ssl/
openssl x509 -in /etc/nginx/ssl/meiyueart.com.crt -noout -dates
```

**修复**:
```bash
# 重新生成证书
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/meiyueart.com.key \
    -out /etc/nginx/ssl/meiyueart.com.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=MeiyueArt/CN=meiyueart.com"

# 设置权限
chmod 600 /etc/nginx/ssl/meiyueart.com.key

# 重启 Nginx
systemctl restart nginx
```

### 故障场景 4: 端口被占用

**症状**: 服务无法启动

**诊断**:
```bash
# 查找占用进程
lsof -i :8080
netstat -tlnp | grep 8080
```

**修复**:
```bash
# 终止占用进程（替换 PID）
kill -9 <PID>

# 重启服务
systemctl restart flask-app
```

---

## 📊 监控和维护

### 服务状态检查

```bash
# Flask 服务
systemctl status flask-app

# Nginx 服务
systemctl status nginx

# 端口监听
netstat -tlnp | grep -E '80|443|8080'
```

### 日志查看

```bash
# Flask 日志
tail -f /var/log/flask-app.log
tail -f /var/log/flask-app-error.log

# Flask systemd 日志
journalctl -u flask-app -f

# Nginx 日志
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 健康检查

```bash
# 本地健康检查
curl http://localhost:8080/api/health

# HTTPS 健康检查
curl -k https://localhost/api/health

# 外网健康检查
curl https://meiyueart.com/api/health
```

### 定期维护任务

**每日**:
- 检查服务状态
- 查看错误日志
- 验证健康检查接口

**每周**:
- 备份数据库
- 检查磁盘空间
- 更新系统补丁

**每月**:
- 更新依赖包
- 性能优化
- 安全审计

---

## 🔒 安全配置

### 防火墙规则

```bash
# 允许 HTTP
ufw allow 80/tcp

# 允许 HTTPS
ufw allow 443/tcp

# 启用防火墙
ufw enable
```

### SSL 配置

```nginx
# SSL 协议
ssl_protocols TLSv1.2 TLSv1.3;

# 加密套件
ssl_ciphers HIGH:!aNULL:!MD5;

# 会话缓存
ssl_session_cache shared:SSL:10m;
ssl_session_timeout 10m;
```

### 文件权限

```bash
# SSL 密钥
chmod 600 /etc/nginx/ssl/meiyueart.com.key

# SSL 证书
chmod 644 /etc/nginx/ssl/meiyueart.com.crt

# 应用目录
chmod 755 /var/www/meiyueart
```

---

## 📞 应急联系

### 快速诊断命令

```bash
# 一键诊断
cd /var/www/meiyueart && bash scripts/diagnose-and-fix.sh

# 服务状态
systemctl status flask-app nginx

# 完整日志
journalctl -u flask-app -n 100 --no-pager
tail -100 /var/log/nginx/error.log
```

### 故障排除清单

- [ ] 检查服务状态
- [ ] 查看错误日志
- [ ] 验证端口监听
- [ ] 测试健康检查
- [ ] 检查磁盘空间
- [ ] 验证网络连接
- [ ] 检查配置文件
- [ ] 重启相关服务

---

## 📚 相关文档

- [服务器诊断报告](docs/SERVER-DIAGNOSIS-REPORT.md)
- [快速修复指南](docs/QUICK-FIX-GUIDE.md)
- [问题解决总结](docs/ISSUE-RESOLUTION-SUMMARY.md)

---

## 📝 更新历史

| 日期 | 版本 | 更新内容 |
|------|------|----------|
| 2026-02-11 | v2.0 | 创建标准部署配置文档，包含完整的自动化脚本 |
| 2026-02-11 | v1.0 | 初版 |

---

**维护者**: Coze Coding  
**最后更新**: 2026-02-11
