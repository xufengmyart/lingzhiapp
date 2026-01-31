# 🚀 WebAPP 完整部署指南

## 📋 当前状态

✅ **已完成**：
- Nginx 安装并运行
- SSL 证书配置完成
- 防火墙和安全组配置完成
- 项目代码构建完成

⏳ **待完成**：
- 推送代码到 GitHub
- 在服务器上拉取最新代码
- 配置 Nginx 指向 WebAPP
- 验证部署成功

---

## 第一步：推送代码到 GitHub（5分钟）

### 操作步骤

#### 1. 检查当前 Git 状态
```bash
cd /workspace/projects
git status
```

#### 2. 推送代码到 GitHub
```bash
git push origin main
```

#### 3. 确认推送成功
看到以下信息表示成功：
```
Enumerating objects: ...
Writing objects: ...
To https://github.com/xufengmyart/lingzhiapp.git
   xxx..xxx  main -> main
```

✅ **完成标志**：代码推送成功

---

## 第二步：连接到服务器（3分钟）

### 使用 Xshell 连接

1. **打开 Xshell**
2. **连接到服务器**
   - 主机：`123.56.142.143`
   - 端口：`22`
   - 用户名：`root`
   - 密码：你的服务器密码

✅ **完成标志**：看到 `[root@xxx ~]#` 提示符

---

## 第三步：在服务器上拉取最新代码（5分钟）

### 操作步骤

#### 1. 进入项目目录
```bash
cd /var/www/lingzhiapp
```

#### 2. 拉取最新代码
```bash
git pull origin main
```

#### 3. 确认文件已更新
```bash
ls -la public/
```

应该看到：
```
drwxr-xr-x  2 root root 4096 assets
-rw-r--r--  1 root root 1092 index.html
-rw-r--r--  1 root root 1807 manifest.json
-rw-r--r--  1 root root  324 apple-touch-icon.svg
-rw-r--r--  1 root root  302 icon-192x192.svg
-rw-r--r--  1 root root  334 icon-512x512.svg
-rw-r--r--  1 root root  302 mask-icon.svg
```

#### 4. 检查 assets 目录
```bash
ls -la public/assets/
```

应该看到：
```
-rw-r--r-- 1 root root 271574 index-Bn5-qrV2.js
-rw-r--r-- 1 root root  25271 index-BtL4IVBk.css
```

✅ **完成标志**：所有文件都已更新

---

## 第四步：配置 Nginx（10分钟）

### 操作步骤

#### 1. 检查现有配置
```bash
cat /etc/nginx/conf.d/meiyueart.com.conf
```

如果配置文件存在且正确，跳到第 5 步

#### 2. 创建或编辑配置文件
```bash
nano /etc/nginx/conf.d/meiyueart.com.conf
```

#### 3. 粘贴以下配置

```nginx
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;

    root /var/www/lingzhiapp/public;
    index index.html;

    # 支持前端路由（React Router）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;
}

# HTTPS 配置（如果已配置 SSL）
server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com;

    root /var/www/lingzhiapp/public;
    index index.html;

    # SSL 证书配置（Let's Encrypt）
    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 支持前端路由（React Router）
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript
               application/x-javascript application/xml+rss
               application/javascript application/json;
}

# HTTP 重定向到 HTTPS（可选）
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;
    return 301 https://$server_name$request_uri;
}
```

#### 4. 保存并退出
- 按 `Ctrl + O`
- 按 `Enter`
- 按 `Ctrl + X`

#### 5. 测试配置
```bash
nginx -t
```

应该看到：
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

#### 6. 重启 Nginx
```bash
systemctl restart nginx
```

#### 7. 确认 Nginx 运行正常
```bash
systemctl status nginx
```

应该看到：
```
Active: active (running)
```

✅ **完成标志**：Nginx 配置成功并重启

---

## 第五步：验证部署（10分钟）

### 测试1：检查网站是否可访问

1. **打开浏览器**
2. **访问网站**
   - HTTP：`http://meiyueart.com`
   - HTTPS：`https://meiyueart.com`

3. **确认可以访问**
   - ✅ 看到"灵值生态园 - 智能体APP"首页
   - ✅ HTTPS 显示小锁图标

---

### 测试2：测试登录功能

1. **访问登录页**
   ```
   https://meiyueart.com/login
   ```

2. **输入登录信息**
   - 用户名：`admin`
   - 密码：`admin123`

3. **点击登录**
   - ✅ 登录成功，跳转到首页

---

### 测试3：测试所有功能

| 功能 | 测试方法 | 预期结果 |
|------|---------|---------|
| 输入框文字 | 在用户名输入框输入"test" | ✅ 文字可见（深灰色） |
| 密码显示 | 在密码框输入"123" | ✅ 显示圆点 |
| 用户管理 | 点击"用户管理" | ✅ 正常显示 |
| 经济模型 | 点击"经济模型" | ✅ 正常显示 |
| 智能对话 | 点击"智能对话"，发送"你好" | ✅ 有回复 |
| 用户旅程 | 点击"用户旅程" | ✅ 正常显示 |
| 合伙人管理 | 点击"合伙人管理" | ✅ 正常显示 |

---

### 测试4：测试 PWA 功能（手机）

1. **在手机浏览器访问**
   ```
   https://meiyueart.com
   ```

2. **尝试安装应用**
   - 点击浏览器菜单
   - 查找"添加到主屏幕"或"安装应用"
   - 点击安装

3. **验证安装成功**
   - ✅ 手机桌面出现应用图标
   - ✅ 点击图标可以打开应用
   - ✅ 应用可以离线运行

---

### 测试5：检查 SSL 证书

1. **点击地址栏的小锁图标**
2. **查看证书信息**
3. **确认**
   - ✅ 证书颁发者：Let's Encrypt
   - ✅ 证书状态：有效
   - ✅ 有效期：90 天（会自动续期）

---

## 📊 完成检查清单

### 服务器端
- [ ] 代码已推送到 GitHub
- [ ] 服务器上已拉取最新代码
- [ ] public 目录包含所有必要文件
- [ ] Nginx 配置正确
- [ ] Nginx 运行正常
- [ ] SSL 证书配置正确

### 访问测试
- [ ] HTTP 可以访问
- [ ] HTTPS 可以访问
- [ ] HTTP 自动重定向到 HTTPS
- [ ] 没有安全警告

### 功能测试
- [ ] 登录功能正常（admin/admin123）
- [ ] 输入框文字可见
- [ ] 所有模块可以点击
- [ ] 智能对话功能正常
- [ ] 路由跳转正常

### PWA 测试
- [ ] manifest.json 可以访问
- [ ] 可以安装到手机主屏幕
- [ ] 应用图标正确显示
- [ ] 应用名称正确

---

## 🔧 常见问题

### 问题1：访问网站显示 404 错误

**解决方案**：
```bash
# 检查文件是否存在
ls -la /var/www/lingzhiapp/public/

# 检查 Nginx 配置
cat /etc/nginx/conf.d/meiyueart.com.conf

# 重启 Nginx
systemctl restart nginx
```

---

### 问题2：登录后页面无法加载

**解决方案**：
```bash
# 检查 Nginx 配置是否有 try_files
cat /etc/nginx/conf.d/meiyueart.com.conf | grep try_files

# 应该看到：
# try_files $uri $uri/ /index.html;

# 如果没有，重新配置 Nginx
nano /etc/nginx/conf.d/meiyueart.com.conf

# 添加：
# location / {
#     try_files $uri $uri/ /index.html;
# }

# 重启 Nginx
systemctl restart nginx
```

---

### 问题3：SSL 证书过期或无效

**解决方案**：
```bash
# 手动续期证书
certbot renew

# 重启 Nginx
systemctl restart nginx

# 检查证书状态
certbot certificates
```

---

### 问题4：静态资源加载失败

**解决方案**：
```bash
# 检查文件权限
chmod -R 755 /var/www/lingzhiapp/public
chown -R nginx:nginx /var/www/lingzhiapp/public

# 重启 Nginx
systemctl restart nginx
```

---

### 问题5：PWA 无法安装

**解决方案**：
```bash
# 检查 manifest.json
cat /var/www/lingzhiapp/public/manifest.json

# 检查是否可以访问
curl https://meiyueart.com/manifest.json

# 清除浏览器缓存并重试
```

---

## 🎉 部署完成！

### 你现在拥有：

| 项目 | 状态 | 地址 |
|------|------|------|
| 访问地址 | ✅ | https://meiyueart.com |
| 登录账号 | ✅ | admin / admin123 |
| HTTPS | ✅ | Let's Encrypt 证书 |
| PWA | ✅ | 可安装到手机 |
| 稳定性 | ✅ | 自己的服务器 |

---

## 📈 后续维护

### 日常维护命令

**查看 Nginx 日志**：
```bash
# 错误日志
tail -f /var/log/nginx/error.log

# 访问日志
tail -f /var/log/nginx/access.log
```

**重启 Nginx**：
```bash
systemctl restart nginx
```

**更新代码**：
```bash
cd /var/www/lingzhiapp
git pull origin main
```

**更新 SSL 证书**：
```bash
certbot renew
```

---

### 定期备份

**备份网站文件**：
```bash
# 创建备份目录
mkdir -p /var/backups

# 备份网站
tar -czf /var/backups/lingzhiapp-$(date +%Y%m%d).tar.gz /var/www/lingzhiapp

# 恢复备份
tar -xzf /var/backups/lingzhiapp-20250131.tar.gz -C /
```

**自动备份脚本**：
```bash
# 创建备份脚本
nano /usr/local/bin/backup-lingzhiapp.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/var/backups"
DATE=$(date +%Y%m%d)
tar -czf $BACKUP_DIR/lingzhiapp-$DATE.tar.gz /var/www/lingzhiapp
# 保留最近 7 天的备份
find $BACKUP_DIR -name "lingzhiapp-*.tar.gz" -mtime +7 -delete
```

```bash
# 添加执行权限
chmod +x /usr/local/bin/backup-lingzhiapp.sh

# 添加到 crontab（每天凌晨 2 点备份）
crontab -e

# 添加：
0 2 * * * /usr/local/bin/backup-lingzhiapp.sh
```

---

## 💡 提示

1. **定期更新**：定期更新系统和软件
   ```bash
   yum update -y
   ```

2. **监控磁盘空间**：
   ```bash
   df -h
   ```

3. **监控系统资源**：
   ```bash
   top
   ```

4. **监控访问日志**：
   ```bash
   tail -f /var/log/nginx/access.log
   ```

---

## 📞 需要帮助？

如果遇到问题，请提供以下信息：
1. 在哪一步遇到问题
2. 具体的错误信息
3. 执行的命令和输出

祝你部署成功！🎉
