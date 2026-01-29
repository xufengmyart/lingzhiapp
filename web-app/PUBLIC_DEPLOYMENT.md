# 🌐 灵值生态园APP - 公网部署指南

## 📋 前置要求

### 服务器要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **CPU**: 2核以上
- **内存**: 2GB以上
- **硬盘**: 20GB以上
- **网络**: 公网IP

### 域名要求
- 已注册域名
- 域名已解析到服务器IP（A记录）

---

## 🚀 快速部署方案

### 方案1：使用免费云服务（推荐新手）

#### 1.1 购买服务器

**推荐平台**：
- 腾讯云：https://cloud.tencent.com/
- 阿里云：https://www.aliyun.com/
- 华为云：https://www.huaweicloud.com/

**配置推荐**：
- 2核4GB
- 带宽3Mbps
- 系统盘40GB

**费用**：
- 新用户：¥50-100/年

#### 1.2 购买域名

**推荐平台**：
- 阿里云万网：https://wanwang.aliyun.com/
- 腾讯云DNSPod：https://dnspod.cloud.tencent.com/
- GoDaddy：https://www.godaddy.com/

**费用**：
- .com域名：¥60-100/年
- .cn域名：¥30-50/年

#### 1.3 部署步骤

```bash
# 1. 连接服务器（SSH）
ssh root@your-server-ip

# 2. 安装必要软件
apt-get update
apt-get install -y nginx nodejs npm git

# 3. 克隆项目（如果有代码仓库）
git clone your-repo-url
cd web-app

# 4. 构建项目
npm install
npm run build

# 5. 复制到Nginx目录
mkdir -p /var/www/lingzhi-ecosystem
cp -r dist/* /var/www/lingzhi-ecosystem/

# 6. 配置Nginx
cp nginx-production.conf /etc/nginx/sites-available/lingzhi-ecosystem
ln -s /etc/nginx/sites-available/lingzhi-ecosystem /etc/nginx/sites-enabled/

# 7. 替换域名
sed -i 's/yourdomain.com/your-actual-domain.com/g' /etc/nginx/sites-available/lingzhi-ecosystem

# 8. 测试并重启Nginx
nginx -t
systemctl restart nginx
systemctl enable nginx

# 9. 配置SSL证书
certbot --nginx -d your-actual-domain.com
```

#### 1.4 验证部署

```bash
# 测试网站访问
curl -I https://your-actual-domain.com

# 查看Nginx日志
tail -f /var/log/nginx/lingzhi-ecosystem-access.log
```

---

### 方案2：使用免费托管平台（最简单）

#### 2.1 Vercel（推荐）

**特点**：
- ✅ 完全免费
- ✅ 自动HTTPS
- ✅ 全球CDN
- ✅ 自动部署

**步骤**：

1. 注册Vercel账号：https://vercel.com/
2. 连接GitHub仓库
3. 导入项目
4. 自动构建部署

**配置**：
在项目根目录创建 `vercel.json`：

```json
{
  "version": 2,
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/static-build",
      "config": {
        "distDir": "dist"
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "/index.html"
    }
  ]
}
```

#### 2.2 Netlify（推荐）

**特点**：
- ✅ 免费额度大
- ✅ 自动HTTPS
- ✅ 表单处理
- ✅ 函数支持

**步骤**：

1. 注册Netlify账号：https://www.netlify.com/
2. 连接GitHub仓库
3. 配置构建设置
   - Build command: `npm run build`
   - Publish directory: `dist`

**重定向规则**（`_redirects`文件）：
```
/* /index.html 200
```

#### 2.3 GitHub Pages（免费）

**特点**：
- ✅ 完全免费
- ✅ 与GitHub集成
- ✅ 自动部署

**步骤**：

1. 将代码推送到GitHub
2. 进入仓库设置
3. 启用GitHub Pages
4. 选择源为 `gh-pages` 分支

**部署脚本**：

```bash
# 安装gh-pages
npm install -D gh-pages

# 添加到package.json
"scripts": {
  "deploy": "gh-pages -d dist"
}

# 部署
npm run build
npm run deploy
```

---

### 方案3：使用容器化部署

#### 3.1 Docker部署

**优势**：
- 环境隔离
- 易于迁移
- 版本控制

**Dockerfile**（已创建）：

```dockerfile
FROM node:18-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", daemon off;"]
```

**构建和运行**：

```bash
# 构建镜像
docker build -t lingzhi-ecosystem:latest .

# 运行容器
docker run -d -p 80:80 --name lingzhi-webapp lingzhi-ecosystem:latest
```

#### 3.2 Docker Compose

**docker-compose.yml**（已创建）：

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "80:80"
    restart: unless-stopped
    environment:
      - NODE_ENV=production
```

**部署**：

```bash
# 启动
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止
docker-compose down
```

---

## 🔐 SSL证书配置

### Let's Encrypt（免费）

#### 自动配置

```bash
# 安装certbot
apt-get install -y certbot python3-certbot-nginx

# 自动配置SSL
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
certbot renew --dry-run
```

#### 手动配置

```bash
# 获取证书
certbot certonly --nginx -d yourdomain.com

# 配置Nginx
ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
```

---

## 🚀 CDN加速

### Cloudflare（免费）

**特点**：
- 免费CDN
- 免费SSL
- DDoS防护
- 全球加速

**步骤**：

1. 注册Cloudflare：https://www.cloudflare.com/
2. 添加域名
3. 修改DNS服务器
4. 启用CDN和缓存

### 阿里云CDN

**特点**：
- 国内加速快
- 免费额度
- 易于配置

**步骤**：

1. 登录阿里云控制台
2. 开通CDN服务
3. 添加域名
4. 配置源站IP
5. 启用加速

---

## 📊 性能优化

### 1. 开启Gzip压缩（已配置）

### 2. 启用HTTP/2（已配置）

### 3. 使用CDN

### 4. 图片优化

```bash
# 安装图片压缩工具
npm install -D imagemin imagemin-pngquant imagemin-mozjpeg

# 优化脚本
# 添加到package.json
"scripts": {
  "optimize-images": "node scripts/optimize-images.js"
}
```

### 5. 代码分割（Vite自动完成）

---

## 📈 监控和分析

### 1. Google Analytics

```html
<!-- 在index.html中添加 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
```

### 2. 百度统计

```html
<!-- 在index.html中添加 -->
<script>
var _hmt = _hmt || [];
(function() {
  var hm = document.createElement("script");
  hm.src = "https://hm.baidu.com/hm.js?YOUR_ID";
  var s = document.getElementsByTagName("script")[0];
  s.parentNode.insertBefore(hm, s);
})();
</script>
```

---

## 🛡️ 安全加固

### 1. 配置防火墙

```bash
# 安装UFW
apt-get install -y ufw

# 允许SSH
ufw allow 22/tcp

# 允许HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# 启用防火墙
ufw enable
```

### 2. 配置fail2ban

```bash
# 安装
apt-get install -y fail2ban

# 配置
cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
systemctl enable fail2ban
systemctl start fail2ban
```

### 3. 定期备份

```bash
# 创建备份脚本
cat > /root/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/lingzhi-ecosystem"
DATE=$(date +%Y%m%d-%H%M%S)
tar -czf "$BACKUP_DIR/backup-$DATE.tar.gz" /var/www/lingzhi-ecosystem
# 保留最近7天的备份
find $BACKUP_DIR -name "backup-*.tar.gz" -mtime +7 -delete
EOF

# 添加到crontab
chmod +x /root/backup.sh
crontab -e
# 添加：0 2 * * * /root/backup.sh
```

---

## 📞 故障排查

### 问题1：无法访问网站

```bash
# 检查Nginx状态
systemctl status nginx

# 检查端口监听
netstat -tlnp | grep :80
netstat -tlnp | grep :443

# 检查防火墙
ufw status
```

### 问题2：SSL证书无效

```bash
# 检查证书有效期
certbot certificates

# 重新获取证书
certbot --nginx -d yourdomain.com --force-renewal
```

### 问题3：502 Bad Gateway

```bash
# 检查后端服务
# 检查Nginx配置
nginx -t
# 查看错误日志
tail -f /var/log/nginx/error.log
```

---

## 🎉 部署完成清单

- [ ] 服务器已购买并配置
- [ ] 域名已购买并解析
- [ ] 代码已部署到服务器
- [ ] Nginx已配置
- [ ] SSL证书已安装
- [ ] 防火墙已配置
- [ ] CDN已配置（可选）
- [ ] 备份脚本已配置
- [ ] 监控已配置（可选）
- [ ] 网站可访问测试通过

---

## 📚 相关文档

- `DEPLOYMENT.md` - 详细部署文档
- `nginx-production.conf` - Nginx配置
- `deploy-production.sh` - 部署脚本

---

**部署完成后，您的应用就可以通过公网访问了！** 🚀
