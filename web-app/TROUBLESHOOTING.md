# 梦幻版页面无法访问 - 故障排查指南

## 🚨 问题描述

页面 URL 显示为 `https://meiyueart.com/dream-selector`，但无法正常访问。

---

## 🔍 诊断步骤

### 第一步：确认页面状态

请告诉我以下情况：
1. **页面显示什么？**
   - [ ] 完全空白
   - [ ] 显示错误信息
   - [ ] 显示部分内容
   - [ ] 404错误

2. **浏览器控制台有什么？**
   - 按 F12 打开开发者工具
   - 查看 Console 标签页
   - 是否有红色错误信息？

---

## 💡 可能的原因和解决方案

### 原因1: 构建产物未正确部署

**症状：** 页面显示空白或 404

**检查：**
```bash
# SSH 登录到服务器
ssh user@123.56.142.143

# 检查构建产物是否存在
ls -la /var/www/frontend/
ls -la /var/www/frontend/index.html
ls -la /var/www/frontend/assets/
```

**解决方案：**
```bash
# 在本地重新构建
cd web-app
npm run build

# 上传到服务器
cd ..
rsync -avz --delete public/* user@123.56.142.143:/var/www/frontend/

# 重启Nginx
ssh user@123.56.142.143 "sudo systemctl restart nginx"
```

---

### 原因2: Nginx 配置问题

**症状：** 页面显示 404 或 502 错误

**检查：**
```bash
# 查看Nginx配置
ssh user@123.56.142.143 "cat /etc/nginx/sites-enabled/default"

# 检查Nginx配置是否包含以下关键配置：
# root /var/www/frontend;
# location / {
#     try_files $uri $uri/ /index.html;
# }
```

**解决方案：**

创建新的Nginx配置：
```bash
# SSH登录服务器
ssh user@123.56.142.143

# 创建配置文件
sudo nano /etc/nginx/sites-available/meiyueart

# 复制以下内容到配置文件：
server {
    listen 80;
    server_name meiyueart.com www.meiyueart.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com;

    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;

    root /var/www/frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# 启用配置
sudo ln -s /etc/nginx/sites-available/meiyueart /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
```

---

### 原因3: 浏览器缓存问题

**症状：** 页面显示旧版本或错误的内容

**解决方案：**

**方法1: 清除缓存**
1. 按 Ctrl+Shift+Delete 打开清除缓存对话框
2. 选择"缓存"和"Cookie"
3. 点击"清除"

**方法2: 无痕模式**
1. 按 Ctrl+Shift+N (Chrome) 或 Ctrl+Shift+P (Firefox)
2. 在无痕模式下访问页面

**方法3: 强制刷新**
- Windows: Ctrl+F5 或 Ctrl+Shift+R
- Mac: Cmd+Shift+R

---

### 原因4: Vite配置问题

**症状：** 页面加载但资源404

**检查：**
```bash
# 检查Vite配置
cat web-app/vite.config.ts
```

**解决方案：**

更新 `web-app/vite.config.ts`：
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  base: '/',  // 添加这行
  build: {
    emptyOutDir: true,
    outDir: '../public',
  },
  plugins: [react()],
  server: {
    port: 3000,
    open: true
  }
})
```

重新构建：
```bash
cd web-app
npm run build
```

---

### 原因5: React Router配置问题

**症状：** 直接访问 `/dream-selector` 显示404，但从首页点击可以

**解决方案：**

确认 `web-app/src/App.tsx` 使用 `BrowserRouter`：
```tsx
import { BrowserRouter } from 'react-router-dom'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>  <!-- 确保使用BrowserRouter -->
        <App />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>,
)
```

---

## 🛠️ 快速诊断命令

### 本地诊断

```bash
# 运行诊断脚本
chmod +x diagnose-deployment.sh
./diagnose-deployment.sh
```

### 服务器诊断

```bash
# SSH登录服务器
ssh user@123.56.142.143

# 检查Nginx状态
sudo systemctl status nginx

# 查看Nginx错误日志
sudo tail -n 50 /var/log/nginx/error.log

# 检查文件是否存在
ls -la /var/www/frontend/
ls -la /var/www/frontend/index.html

# 检查文件内容
cat /var/www/frontend/index.html
```

---

## 🚀 一键部署

```bash
# 给脚本添加执行权限
chmod +x deploy-dream.sh

# 运行部署脚本
./deploy-dream.sh
```

---

## 📋 测试清单

部署后请测试：

- [ ] `https://meiyueart.com/` - 首页
- [ ] `https://meiyueart.com/login` - 传统登录
- [ ] `https://meiyueart.com/register` - 传统注册
- [ ] `https://meiyueart.com/dream-selector` - 梦幻选择器 ⭐
- [ ] `https://meiyueart.com/login-full` - 梦幻登录
- [ ] `https://meiyueart.com/register-full` - 梦幻注册
- [ ] `https://meiyueart.com/design-showcase` - 设计展示

---

## ❓ 需要更多信息

如果以上方案都无法解决问题，请提供：

1. **浏览器控制台截图**（F12 → Console）
2. **Nginx错误日志**
   ```bash
   ssh user@123.56.142.143 "sudo tail -n 100 /var/log/nginx/error.log"
   ```
3. **页面实际显示内容描述**
4. **是否看到任何错误提示**

---

## 🔧 相关文件

- `web-app/vite.config.ts` - Vite配置
- `web-app/nginx-meiyueart.conf` - Nginx配置示例
- `web-app/deploy-dream.sh` - 快速部署脚本
- `web-app/diagnose-deployment.sh` - 诊断脚本
