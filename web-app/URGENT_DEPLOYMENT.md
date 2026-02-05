# 🚨 紧急：梦幻版页面部署 - 服务器文件未更新

## 🔍 问题诊断

从浏览器日志发现：
- **实际访问的文件：** `index-9000aff5.js` (313 B) ← 旧的文件
- **应该访问的文件：** `index-CkydMeua.js` (688 kB) ← 新构建的文件

**结论：服务器上的构建产物没有更新！**

---

## ⚡ 立即解决方案

### 步骤1：SSH 登录服务器

```bash
ssh root@123.56.142.143
```

### 步骤2：检查服务器文件

```bash
# 检查前端目录
ls -lh /var/www/frontend/assets/

# 你应该看到类似这样的输出：
# index-CkydMeua.js  (688 KB) ← 这才是新的
# index-CxUAxLXV.css  (82 KB)
```

如果看到的是 `index-9000aff5.js`，说明文件是旧的。

### 步骤3：备份并清理旧文件

```bash
# 备份旧文件
cp -r /var/www/frontend /var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)

# 清空目录
rm -rf /var/www/frontend/*
```

### 步骤4：上传新构建产物

**方法A：如果服务器能访问外网**

在服务器上直接执行：

```bash
# 如果项目在服务器上，进入项目目录
cd /path/to/lingzhi-ecosystem/web-app

# 重新构建
npm run build

# 复制到目标目录
cp -r public/* /var/www/frontend/

# 重启Nginx
sudo systemctl restart nginx
```

**方法B：从本地上传**

在本地（有构建产物的机器）执行：

```bash
# 进入项目根目录
cd /workspace/projects

# 使用 scp 上传（需要SSH密钥）
scp -r public/* root@123.56.142.143:/var/www/frontend/

# 或使用 rsync（如果可用）
rsync -avz --delete public/* root@123.56.142.143:/var/www/frontend/
```

**方法C：手动上传文件**

1. 在本地打包：
   ```bash
   cd /workspace/projects
   tar -czf dream-frontend.tar.gz public/
   ```

2. 使用 SFTP 工具（如 FileZilla）上传 `dream-frontend.tar.gz` 到服务器的 `/root/` 目录

3. 在服务器上解压：
   ```bash
   ssh root@123.56.142.143
   cd /var/www/frontend
   rm -rf *
   tar -xzf /root/dream-frontend.tar.gz --strip-components=1
   ```

### 步骤5：验证文件

```bash
# 检查文件是否更新
ls -lh /var/www/frontend/assets/

# 应该看到：
# index-CkydMeua.js  688K Feb  5 13:02
# index-CxUAxLXV.css  82K  Feb  5 13:02
```

### 步骤6：重启Nginx

```bash
sudo systemctl restart nginx

# 检查Nginx状态
sudo systemctl status nginx

# 查看错误日志
sudo tail -n 20 /var/log/nginx/error.log
```

### 步骤7：清除浏览器缓存

在浏览器中：
- **Windows:** 按 `Ctrl + Shift + R` 或 `Ctrl + F5`
- **Mac:** 按 `Cmd + Shift + R`

或使用无痕模式访问。

---

## ✅ 验证部署

访问以下URL：

```
https://meiyueart.com/dream-selector
```

**应该看到：**
- 4个风格卡片（晨曦之梦、星空梦境、森林之梦、极光之梦）
- 可以点击选择风格
- 有"登录账户"和"创建账户"按钮
- 梦幻背景和装饰效果

---

## 🔧 如果还是不行

### 检查Nginx配置

```bash
ssh root@123.56.142.143
cat /etc/nginx/sites-enabled/default
```

确认包含以下配置：

```nginx
server {
    listen 443 ssl http2;
    server_name meiyueart.com www.meiyueart.com;

    ssl_certificate /etc/letsencrypt/live/meiyueart.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/meiyueart.com/privkey.pem;

    root /var/www/frontend;  # ← 确保是这个路径
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;  # ← 重要！
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

如果配置不对，更新后：

```bash
sudo nginx -t  # 测试配置
sudo systemctl restart nginx  # 重启Nginx
```

### 检查文件权限

```bash
ssh root@123.56.142.143

# 检查文件权限
ls -la /var/www/frontend/

# 应该是 root:root 或 www-data:www-data

# 如果权限不对，修复：
sudo chown -R root:root /var/www/frontend/
sudo chmod -R 755 /var/www/frontend/
```

---

## 📊 快速诊断命令

```bash
# 一键检查服务器状态
ssh root@123.56.142.143 << 'EOF'
echo "=== 文件检查 ==="
ls -lh /var/www/frontend/assets/ | head -5

echo -e "\n=== Nginx状态 ==="
sudo systemctl status nginx --no-pager

echo -e "\n=== Nginx配置 ==="
grep -E "(root|try_files)" /etc/nginx/sites-enabled/default | head -5

echo -e "\n=== 错误日志 ==="
sudo tail -n 10 /var/log/nginx/error.log
EOF
```

---

## 📋 完整部署脚本

在服务器上执行：

```bash
#!/bin/bash

# 梦幻版页面完整部署脚本
# 在服务器上执行此脚本

echo "开始部署梦幻版页面..."

# 1. 备份
echo "备份现有文件..."
BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"
cp -r /var/www/frontend $BACKUP_DIR

# 2. 清理
echo "清理目标目录..."
rm -rf /var/www/frontend/*

# 3. 复制新文件（假设在服务器上有项目）
echo "复制新构建产物..."
if [ -d "/root/lingzhi-ecosystem/web-app/public" ]; then
    cp -r /root/lingzhi-ecosystem/web-app/public/* /var/www/frontend/
else
    echo "错误：找不到项目目录！"
    echo "请先上传 public/* 到服务器或确认项目路径"
    exit 1
fi

# 4. 验证
echo "验证文件..."
if [ ! -f "/var/www/frontend/index.html" ]; then
    echo "错误：index.html 不存在！"
    exit 1
fi

echo "构建产物："
ls -lh /var/www/frontend/assets/

# 5. 设置权限
echo "设置权限..."
chown -R root:root /var/www/frontend/
chmod -R 755 /var/www/frontend/

# 6. 重启Nginx
echo "重启Nginx..."
sudo systemctl restart nginx

# 7. 检查状态
echo -e "\n部署完成！"
echo "Nginx状态："
sudo systemctl status nginx --no-pager | head -10

echo -e "\n请访问：https://meiyueart.com/dream-selector"
echo "如果还有问题，恢复备份：cp -r $BACKUP_DIR/* /var/www/frontend/"
```

保存为 `/root/deploy-dream.sh`，然后：

```bash
chmod +x /root/deploy-dream.sh
sudo /root/deploy-dream.sh
```

---

## 🎯 核心问题总结

| 项目 | 应该是什么 | 实际是什么 |
|------|-----------|-----------|
| JS文件名 | index-CkydMeua.js | index-9000aff5.js ❌ |
| JS文件大小 | 688 KB | 313 B ❌ |
| 构建时间 | Feb 5 13:02 | 旧时间 ❌ |

**解决方案：上传新的构建产物到服务器！**

---

## 📞 如果需要帮助

请提供以下信息：

1. 服务器上的文件列表：
   ```bash
   ssh root@123.56.142.143
   ls -lh /var/www/frontend/assets/
   ```

2. Nginx配置：
   ```bash
   cat /etc/nginx/sites-enabled/default
   ```

3. Nginx错误日志：
   ```bash
   sudo tail -n 50 /var/log/nginx/error.log
   ```

---

## ⚠️ 重要提醒

**问题：服务器上的构建产物没有更新！**

**原因：**
- 构建成功，但文件没有上传到服务器
- 或者上传了，但覆盖到了错误的目录

**解决：**
1. 确认上传到 `/var/www/frontend/` 目录
2. 确认重启了Nginx
3. 确认清除了浏览器缓存

**构建产物位置：** `/workspace/projects/public/`  
**目标位置：** `root@123.56.142.143:/var/www/frontend/`