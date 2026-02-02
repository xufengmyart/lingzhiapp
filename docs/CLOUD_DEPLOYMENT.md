# 灵值生态园 - 云服务器部署指南

## 📋 部署前准备

### 1. 阿里云安全组配置

在阿里云控制台开放以下端口：

| 端口 | 协议 | 说明 |
|------|------|------|
| 22 | TCP | SSH（默认已开放） |
| 80 | TCP | HTTP访问（必须开放） |
| 443 | TCP | HTTPS访问（可选） |
| 8001 | TCP | 后端API（可选，用于直接访问API） |

**操作步骤：**
1. 登录阿里云控制台
2. 进入 ECS 实例管理
3. 点击"安全组" -> "配置规则"
4. 添加入方向规则：
   - 端口范围：80/80
   - 授权对象：0.0.0.0/0
   - 协议：TCP

### 2. 本地环境检查

确保本地已安装：
- Node.js 18+
- Python 3.8+
- npm

## 🚀 快速部署

### 方法一：使用自动部署脚本（推荐）

```bash
cd /workspace/projects
./scripts/deploy_to_cloud.sh
```

脚本会自动完成以下操作：
1. ✅ 检查本地环境
2. ✅ 构建前端
3. ✅ 打包代码
4. ✅ 上传到云服务器
5. ✅ 自动部署
6. ✅ 启动服务

### 方法二：手动部署

#### 1. 构建前端

```bash
cd /workspace/projects/web-app
npm run build
```

#### 2. 上传到云服务器

```bash
# 上传后端
cd /workspace/projects
scp -r admin-backend root@123.56.142.143:/root/lingzhi-ecosystem/

# 上传前端构建产物
scp -r web-app/public/* root@123.56.142.143:/root/lingzhi-ecosystem/web-app-dist/

# 上传数据库
scp admin-backend/lingzhi_ecosystem.db root@123.56.142.143:/root/lingzhi-ecosystem/admin-backend/
```

#### 3. 在云服务器上启动服务

```bash
# SSH登录到云服务器
ssh root@123.56.142.143

# 进入项目目录
cd /root/lingzhi-ecosystem/admin-backend

# 安装依赖
pip install -r requirements.txt

# 启动后端服务
nohup python app.py > /tmp/backend.log 2>&1 &
```

## 🔍 验证部署

### 1. 检查服务状态

```bash
# 在云服务器上执行
ps aux | grep "python app.py"
```

### 2. 查看日志

```bash
# 在云服务器上执行
tail -f /tmp/backend.log
```

### 3. 访问应用

打开浏览器访问：
- http://123.56.142.143

## ⚙️ Nginx配置（可选）

如果需要配置Nginx作为反向代理：

```nginx
server {
    listen 80;
    server_name 123.56.142.143;

    # 前端静态文件
    location / {
        root /root/lingzhi-ecosystem/web-app-dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 后端API
    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

安装Nginx并配置：

```bash
# 安装Nginx
yum install -y nginx

# 创建配置文件
cat > /etc/nginx/conf.d/lingzhi-ecosystem.conf << 'EOF'
server {
    listen 80;
    server_name 123.56.142.143;

    location / {
        root /root/lingzhi-ecosystem/web-app-dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8001/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

# 启动Nginx
systemctl start nginx
systemctl enable nginx
```

## 🔄 更新部署

每次更新代码后，重新执行部署脚本即可：

```bash
cd /workspace/projects
./scripts/deploy_to_cloud.sh
```

## 🔧 常见问题

### 问题1：端口访问失败

**原因**：阿里云安全组未开放端口

**解决**：
1. 登录阿里云控制台
2. ECS实例 -> 安全组 -> 配置规则
3. 添加入方向规则，开放80端口

### 问题2：后端服务启动失败

**原因**：依赖未安装或端口被占用

**解决**：
```bash
# 检查日志
tail -f /tmp/backend.log

# 重新安装依赖
cd /root/lingzhi-ecosystem/admin-backend
pip install -r requirements.txt

# 重启服务
pkill -f "python app.py"
nohup python app.py > /tmp/backend.log 2>&1 &
```

### 问题3：前端页面空白

**原因**：前端构建失败或路径配置错误

**解决**：
```bash
# 检查前端文件是否存在
ls -la /root/lingzhi-ecosystem/web-app-dist/

# 重新构建并上传
cd /workspace/projects/web-app
npm run build
scp -r public/* root@123.56.142.143:/root/lingzhi-ecosystem/web-app-dist/
```

## 📞 技术支持

如遇到其他问题，请查看日志文件：
- 后端日志：`/tmp/backend.log`
- Nginx日志：`/var/log/nginx/`

---

**部署完成后，访问 http://123.56.142.143 即可使用灵值生态园！**
