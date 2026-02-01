# 灵值生态园 - 公网部署指南

## 问题说明

通过公网IP访问时出现500错误的原因是：
- 前端默认使用 `window.location.origin` 作为API基础地址
- 但前端和后端运行在不同端口（前端：80/443，后端：8001）
- 导致API请求发送到错误的地址

## 解决方案

### 方案1：使用环境变量配置（推荐）

1. **修改 .env.production 文件**

   编辑 `web-app/.env.production`，设置正确的API地址：

   ```bash
   # 如果您的服务器公网IP是 123.45.67.89
   VITE_API_BASE_URL=http://123.45.67.89:8001
   ```

2. **重新构建前端**

   ```bash
   cd web-app
   npm run build
   ```

3. **部署前端文件**

   将 `web-app/dist` 目录的内容部署到您的Web服务器（Nginx/Apache等）

### 方案2：使用Nginx反向代理（推荐用于生产环境）

1. **安装Nginx**

   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install nginx

   # CentOS/RHEL
   sudo yum install nginx
   ```

2. **配置Nginx**

   创建 `/etc/nginx/sites-available/lingzhi-ecosystem`：

   ```nginx
   server {
       listen 80;
       server_name your-domain.com;  # 替换为您的域名或公网IP

       # 前端静态文件
       location / {
           root /path/to/web-app/dist;
           try_files $uri $uri/ /index.html;
       }

       # 后端API代理
       location /api/ {
           proxy_pass http://127.0.0.1:8001;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **启用配置并重启Nginx**

   ```bash
   sudo ln -s /etc/nginx/sites-available/lingzhi-ecosystem /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

4. **修改前端配置**

   编辑 `web-app/.env.production`：

   ```bash
   VITE_API_BASE_URL=/
   ```

5. **重新构建和部署**

   ```bash
   cd web-app
   npm run build
   # 部署dist目录到配置的路径
   ```

### 方案3：使用简单的HTTP服务器（临时方案）

1. **构建前端**

   ```bash
   cd web-app
   npm run build
   ```

2. **使用Python简单HTTP服务器**

   ```bash
   cd dist
   python3 -m http.server 80
   ```

3. **配置环境变量**

   在浏览器中打开前端时，手动添加API地址到localStorage：

   ```javascript
   // 在浏览器控制台执行
   localStorage.setItem('apiBaseURL', 'http://YOUR_PUBLIC_IP:8001');
   location.reload();
   ```

   或修改 `web-app/src/services/api.ts`：

   ```typescript
   const API_BASE_URL = localStorage.getItem('apiBaseURL') || window.location.origin
   ```

## 验证部署

1. **检查后端服务**

   ```bash
   curl http://YOUR_PUBLIC_IP:8001/api/health
   ```

   应该返回：
   ```json
   {"status": "ok"}
   ```

2. **检查前端**

   在浏览器中访问 `http://YOUR_PUBLIC_IP`，查看是否能正常加载

3. **测试登录**

   尝试登录，观察网络请求是否发送到正确的地址（应该是 `http://YOUR_PUBLIC_IP:8001/api/login`）

## 防火墙配置

确保以下端口已开放：

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8001/tcp

# CentOS/RHEL (使用firewalld)
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=8001/tcp
sudo firewall-cmd --reload
```

## 云服务商安全组

如果使用云服务器（阿里云、腾讯云、AWS等），还需要在云服务商的控制台中开放端口：
- 80 (HTTP)
- 443 (HTTPS)
- 8001 (后端API)

## 常见问题

### Q1: 前端能访问，但API请求失败

**A:** 检查前端配置的API地址是否正确。打开浏览器开发者工具（F12），查看Network标签，确认API请求的URL。

### Q2: CORS错误

**A:** 后端已配置CORS支持所有来源。如果仍有问题，检查Nginx配置是否正确设置了代理头。

### Q3: 静态资源404

**A:** 确保Nginx配置了正确的 `root` 路径，并且使用了 `try_files $uri $uri/ /index.html;` 来支持React Router。

## 联系支持

如果遇到其他问题，请联系技术支持。
