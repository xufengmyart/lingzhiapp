# 快速修复指南 - meiyueart.com 外网访问问题

## 问题诊断结果

✅ **域名解析正常**：meiyueart.com -> 123.56.142.143  
✅ **Nginx 服务正常**：端口 80 和 443 正在监听  
❌ **Flask 后端服务未运行**：导致 502 Bad Gateway 错误

---

## 快速修复步骤（5分钟内完成）

### 方案 A：如果可以直接登录阿里云服务器

```bash
# 1. SSH 登录到阿里云服务器
ssh root@123.56.142.143

# 2. 运行快速诊断和修复脚本
cd /var/www/meiyueart
bash scripts/diagnose-and-fix.sh

# 3. 如果诊断发现问题，手动重启 Flask
systemctl restart flask-app
# 或
pm2 restart flask-app
```

### 方案 B：如果需要先部署代码

```bash
# 1. SSH 登录到阿里云服务器
ssh root@123.56.142.143

# 2. 上传代码（从本地）
# 在本地执行：
scp -r backend root@123.56.142.143:/var/www/meiyueart/

# 3. 在服务器上运行部署脚本
cd /var/www/meiyueart
bash scripts/deploy-to-aliyun.sh
```

---

## 验证修复结果

在阿里云服务器上执行：

```bash
# 1. 检查 Flask 服务
curl http://localhost:8080/api/health

# 2. 检查 HTTPS 访问
curl -k https://localhost/api/health

# 3. 检查外网访问
curl https://meiyueart.com/api/health
```

在本地浏览器访问：
- `https://meiyueart.com` - 应该可以正常打开
- `https://meiyueart.com/api/health` - 应该返回健康检查数据

---

## 服务管理命令

```bash
# 查看 Flask 服务状态
systemctl status flask-app

# 启动 Flask 服务
systemctl start flask-app

# 停止 Flask 服务
systemctl stop flask-app

# 重启 Flask 服务
systemctl restart flask-app

# 查看 Flask 日志
journalctl -u flask-app -f

# 查看 Nginx 日志
tail -f /var/log/nginx/error.log
```

---

## 常见问题

### Q1: systemctl 提示服务不存在
**A**: Flask 服务可能使用 PM2 管理，尝试：
```bash
pm2 list
pm2 restart flask-app
pm2 logs flask-app
```

### Q2: 502 错误仍然存在
**A**: 检查 Flask 服务日志：
```bash
journalctl -u flask-app -n 50
# 或
pm2 logs flask-app --lines 50
```

### Q3: SSL 证书错误
**A**: 重新生成 SSL 证书：
```bash
mkdir -p /etc/nginx/ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/ssl/meiyueart.com.key \
    -out /etc/nginx/ssl/meiyueart.com.crt \
    -subj "/C=CN/ST=Beijing/L=Beijing/O=MeiyueArt/CN=meiyueart.com"
systemctl restart nginx
```

### Q4: 端口被占用
**A**: 查找并终止占用端口的进程：
```bash
# 查找占用 8080 端口的进程
lsof -i :8080

# 终止进程（替换 PID）
kill -9 <PID>
```

---

## 持久化配置

确保服务开机自启动：

```bash
# Flask 服务
systemctl enable flask-app

# Nginx 服务
systemctl enable nginx
```

---

## 技术支持

如遇到无法解决的问题，请提供以下信息：

1. 系统信息：
   ```bash
   uname -a
   cat /etc/os-release
   ```

2. 服务状态：
   ```bash
   systemctl status nginx
   systemctl status flask-app
   ```

3. 错误日志：
   ```bash
   tail -20 /var/log/nginx/error.log
   journalctl -u flask-app -n 20
   ```

4. 端口监听：
   ```bash
   netstat -tlnp | grep -E '80|443|8080'
   ```

---

**生成时间**：2026-02-11  
**版本**：v1.0
