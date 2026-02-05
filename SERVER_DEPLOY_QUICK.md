# 🚀 服务器端部署 - 立即执行

您已经在服务器上了，请直接执行以下命令：

## 方法1：快速部署（如果tar包已在服务器上）

```bash
# 一键部署
if [ -f "/root/dream-frontend-deploy.tar.gz" ]; then
    echo "开始部署..."
    BACKUP_DIR="/var/www/frontend.backup.$(date +%Y%m%d_%H%M%S)"
    mkdir -p /var/www/frontend
    [ -d "/var/www/frontend" ] && cp -r /var/www/frontend "$BACKUP_DIR" 2>/dev/null || true
    rm -rf /var/www/frontend/*
    mkdir -p /tmp/dream
    tar -xzf /root/dream-frontend-deploy.tar.gz -C /tmp/dream
    cp -r /tmp/dream/* /var/www/frontend/
    chown -R root:root /var/www/frontend
    chmod -R 755 /var/www/frontend
    systemctl restart nginx
    echo "✓ 部署完成"
    echo "访问：https://meiyueart.com/dream-selector"
else
    echo "错误：找不到 /root/dream-frontend-deploy.tar.gz"
    echo "请先上传tar包到服务器"
fi
```

## 方法2：如果没有tar包，使用SFTP上传

### 在本地环境执行（不是在服务器上）：

```bash
# 上传tar包
scp /workspace/projects/dream-frontend-deploy.tar.gz root@123.56.142.143:/root/
```

### 然后在服务器上执行（复制上面的方法1命令）

---

## 验证部署

部署完成后，执行：

```bash
# 检查文件
ls -lh /var/www/frontend/assets/

# 应该看到：
# index-CkydMeua.js  (约704K)
# index-CxUAxLXV.css (约82K)

# 检查Nginx状态
systemctl status nginx
```

---

## 清除浏览器缓存并访问

1. **Windows:** `Ctrl + Shift + R`
2. **Mac:** `Cmd + Shift + R`
3. **或使用无痕模式**

访问：https://meiyueart.com/dream-selector

---

## 如果tar包不在服务器上

### 方案A：上传tar包

在本地执行：
```bash
scp /workspace/projects/dream-frontend-deploy.tar.gz root@123.56.142.143:/root/
```

### 方案B：服务器上直接构建（需要项目代码）

如果服务器上有项目代码：
```bash
cd /path/to/project/web-app
npm run build
cp -r public/* /var/www/frontend/
systemctl restart nginx
```

---

## 快速检查

```bash
# 检查tar包是否存在
ls -lh /root/dream-frontend-deploy.tar.gz

# 检查当前部署的文件
ls -lh /var/www/frontend/assets/

# 检查Nginx日志
tail -n 20 /var/log/nginx/error.log
```
