# 灵值生态园 - 服务器诊断报告

## 诊断时间
2026-02-11 08:38:00

## 问题描述
用户反馈 `meiyueart.com` 域名无法访问外网。

## 诊断结果

### ✅ 域名解析正常
```
meiyueart.com -> 123.56.142.143
```
域名正确解析到阿里云服务器 IP。

### ✅ Nginx 服务正常
- 服务器：123.56.142.143
- Nginx 版本：1.24.0 (Ubuntu)
- 监听端口：80 (HTTP) 和 443 (HTTPS)
- HTTP 到 HTTPS 重定向配置正常

### ❌ Flask 后端服务未运行
访问 `https://123.56.142.143/api/health` 返回：
```html
<html>
<head><title>502 Bad Gateway</title></head>
<body>
<center><h1>502 Bad Gateway</h1></center>
<hr><center>nginx/1.24.0 (Ubuntu)</center>
</body>
</html>
```

**原因分析**：
- Nginx 可以正常接收请求
- 但无法连接到后端 Flask 服务（0.0.0.0:8080）
- 说明 Flask 服务已停止或未启动

## 环境信息

### 当前环境 (Coze 平台)
- 公网 IP：115.190.51.49
- 用途：开发/测试环境
- Flask 服务：已启动在 8080 端口
- Nginx：已配置本地代理

### 生产环境 (阿里云服务器)
- 公网 IP：123.56.142.143
- 用途：生产环境
- Nginx：已配置 HTTPS 和代理
- Flask 服务：**未运行** ❌

## 问题根源

**关键发现**：
1. 当前 Coze 环境与阿里云生产服务器是**两个不同的服务器**
2. Coze 环境的 IP (115.190.51.49) 与阿里云服务器的 IP (123.56.142.143) **不匹配**
3. 用户访问的 `meiyueart.com` 解析到阿里云服务器 (123.56.142.143)
4. 阿里云服务器上的 Flask 后端服务已停止，导致 502 错误

## 解决方案

### 方案 1：重启阿里云服务器上的 Flask 服务（推荐）

**步骤**：
1. 使用 SSH 登录到阿里云服务器：
   ```bash
   ssh root@123.56.142.143
   ```

2. 检查 Flask 服务状态：
   ```bash
   pm2 list
   # 或
   systemctl status flask-app
   ```

3. 重启 Flask 服务：
   ```bash
   cd /path/to/your/app
   pm2 restart flask-app
   # 或
   systemctl restart flask-app
   ```

4. 验证服务是否启动：
   ```bash
   curl http://localhost:8080/api/health
   ```

5. 验证外网访问：
   ```bash
   curl https://meiyueart.com/api/health
   ```

### 方案 2：使用 systemd 管理 Flask 服务

如果还没有配置 systemd 服务，可以创建一个：

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/flask-app.service
```

服务文件内容：
```ini
[Unit]
Description=Flask Application
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/your/app
ExecStart=/usr/bin/python3 backend/app.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable flask-app
sudo systemctl start flask-app
sudo systemctl status flask-app
```

### 方案 3：使用 PM2 管理 Flask 服务

```bash
# 1. 安装 PM2
npm install -g pm2

# 2. 启动服务
cd /path/to/your/app
pm2 start backend/app.py --name flask-app

# 3. 设置开机自启动
pm2 startup
pm2 save
```

## 验证检查清单

完成服务启动后，请验证以下项目：

- [ ] Flask 服务在 8080 端口运行
- [ ] 访问 `http://123.56.142.143:8080/api/health` 返回正常
- [ ] 访问 `https://meiyueart.com/api/health` 返回正常
- [ ] 访问 `https://meiyueart.com` 可以正常打开前端页面
- [ ] 用户可以正常登录

## 预防措施

为了避免类似问题再次发生，建议：

1. **配置服务监控**：使用 Uptime Robot 或类似工具监控服务可用性
2. **配置自动重启**：使用 systemd 或 PM2 的自动重启功能
3. **配置日志监控**：定期检查 Nginx 和 Flask 日志
4. **定期备份**：备份应用代码和数据库

## 联系支持

如果以上方案无法解决问题，请提供以下信息：

1. SSH 登录日志
2. Flask 服务日志：
   ```bash
   tail -f /var/log/flask-app.log
   # 或
   pm2 logs flask-app
   ```
3. Nginx 错误日志：
   ```bash
   tail -f /var/log/nginx/error.log
   ```

---

**生成时间**：2026-02-11
**诊断工具**：Coze Coding
