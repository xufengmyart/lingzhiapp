# 🚀 云服务器部署指南 - 完整版

## 📦 部署包已准备就绪

部署包已创建：
- **文件名**: `lingzhi_ecosystem_deploy_20260202_170838.tar.gz`
- **大小**: 3.8M
- **位置**: `/workspace/projects/lingzhi_ecosystem_deploy_20260202_170838.tar.gz`

---

## 🚀 快速部署（3步）

### 方式1：使用SCP上传（推荐）

如果你有SSH客户端：

```bash
# 1. 上传部署包
scp /workspace/projects/lingzhi_ecosystem_deploy_20260202_170838.tar.gz root@123.56.142.143:/tmp/

# 2. SSH登录到服务器
ssh root@123.56.142.143

# 3. 解压并部署
cd /tmp
tar -xzf lingzhi_ecosystem_deploy_20260202_170838.tar.gz
cd admin-backend
../scripts/cloud_auto_deploy.sh
```

### 方式2：使用阿里云Web终端

1. 登录阿里云控制台：https://ecs.console.aliyun.com/
2. ECS实例 -> 远程连接 -> VNC连接
3. 在Web终端中执行以下命令：

```bash
# 方式2A：通过wget下载（如果有HTTP服务器）
# 需要先在本地启动HTTP服务器

# 方式2B：手动复制文件内容（较慢）
# 不推荐，文件太大
```

### 方式3：使用阿里云OSS中转

1. 上传部署包到阿里云OSS
2. 在云服务器上使用wget下载

---

## 📝 详细部署步骤

### 步骤1：准备云服务器

SSH登录到云服务器：

```bash
ssh root@123.56.142.143
```

### 步骤2：上传部署包

在你的本地电脑上：

```bash
scp lingzhi_ecosystem_deploy_20260202_170838.tar.gz root@123.56.142.143:/tmp/
```

### 步骤3：解压部署包

在云服务器上：

```bash
cd /tmp
tar -xzf lingzhi_ecosystem_deploy_20260202_170838.tar.gz
ls -la
```

应该看到：
- admin-backend/
- web-app-dist/
- scripts/

### 步骤4：运行自动部署脚本

```bash
cd admin-backend
../scripts/cloud_auto_deploy.sh
```

脚本会自动完成：
- ✅ 关闭防火墙
- ✅ 安装依赖
- ✅ 配置Nginx
- ✅ 启动后端服务
- ✅ 启动Nginx
- ✅ 测试服务

### 步骤5：开放阿里云安全组端口 ⚠️ 最关键！

1. 登录阿里云控制台：https://ecs.console.aliyun.com/
2. ECS实例 -> 安全组 -> 配置规则
3. 添加入方向规则：

| 配置项 | 值 |
|--------|-----|
| 规则方向 | 入方向 |
| 授权策略 | 允许 |
| 协议类型 | TCP |
| 端口范围 | 80/80, 8080/8080 |
| 授权对象 | 0.0.0.0/0 |
| 优先级 | 1 |

4. 保存并等待1-2分钟生效

### 步骤6：访问应用

打开浏览器：http://123.56.142.143

---

## 🔧 手动部署（如果自动脚本失败）

### 1. 关闭防火墙

```bash
systemctl stop firewalld
systemctl disable firewalld
iptables -F
iptables -X
```

### 2. 安装依赖

```bash
# CentOS/RHEL
yum install -y nginx python3 python3-pip

# Ubuntu/Debian
apt-get install -y nginx python3 python3-pip

# 安装Python依赖
cd /root/lingzhi-ecosystem/admin-backend
pip3 install -r requirements.txt
```

### 3. 配置Nginx

```bash
cat > /etc/nginx/conf.d/lingzhi-ecosystem.conf << 'EOF'
server {
    listen 80;
    server_name _;

    location / {
        root /root/lingzhi-ecosystem/web-app-dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 测试配置
nginx -t
```

### 4. 启动后端服务

```bash
cd /root/lingzhi-ecosystem/admin-backend
nohup python3 app.py > /tmp/backend.log 2>&1 &

# 检查服务
ps aux | grep python3
tail -f /tmp/backend.log
```

### 5. 启动Nginx

```bash
systemctl start nginx
systemctl enable nginx

# 检查服务
systemctl status nginx
```

### 6. 测试访问

```bash
# 测试后端API
curl http://127.0.0.1:8080/api/login -X POST \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# 测试前端
curl -I http://127.0.0.1:80/
```

---

## 🔍 验证部署

### 检查服务状态

```bash
# 检查后端服务
ps aux | grep python3

# 检查Nginx服务
systemctl status nginx

# 检查端口监听
netstat -tlnp | grep -E ":80 |:8080 "
```

### 检查日志

```bash
# 后端日志
tail -f /tmp/backend.log

# Nginx错误日志
tail -f /var/log/nginx/error.log

# Nginx访问日志
tail -f /var/log/nginx/access.log
```

### 测试功能

1. **访问前端**: http://123.56.142.143
2. **测试登录**:
   - 用户名: admin
   - 密码: admin123
3. **测试签到**: 登录后点击签到按钮

---

## 🛠️ 故障排查

### 问题1：502 Bad Gateway

**原因**: 后端服务未启动或端口配置错误

**解决**:
```bash
# 检查后端服务
ps aux | grep python3

# 重启后端
cd /root/lingzhi-ecosystem/admin-backend
pkill -f "python.*app.py"
nohup python3 app.py > /tmp/backend.log 2>&1 &

# 查看日志
tail -f /tmp/backend.log
```

### 问题2：404 Not Found

**原因**: 前端文件路径错误

**解决**:
```bash
# 检查前端文件
ls -la /root/lingzhi-ecosystem/web-app-dist/

# 应该有 index.html 和 assets 目录

# 检查Nginx配置
cat /etc/nginx/conf.d/lingzhi-ecosystem.conf
```

### 问题3：连接被拒绝

**原因**: 阿里云安全组未开放端口

**解决**:
1. 登录阿里云控制台
2. ECS实例 -> 安全组 -> 配置规则
3. 添加80端口规则
4. 等待1-2分钟生效

### 问题4：防火墙阻止

**原因**: 服务器防火墙未关闭

**解决**:
```bash
systemctl stop firewalld
systemctl disable firewalld
iptables -F
```

---

## 📊 部署清单

### 云服务器要求

- [ ] 操作系统：CentOS 7+ / Ubuntu 18.04+
- [ ] Python 3.8+
- [ ] Node.js 18+（仅构建时需要）
- [ ] 80端口开放（阿里云安全组）
- [ ] 8080端口开放（可选，用于API直接访问）
- [ ] 至少1GB内存
- [ ] 至少10GB磁盘空间

### 部署步骤检查

- [ ] 上传部署包到云服务器
- [ ] 解压部署包
- [ ] 运行自动部署脚本
- [ ] 检查服务状态
- [ ] 开放阿里云安全组端口
- [ ] 测试访问应用
- [ ] 测试登录功能
- [ ] 测试签到功能

---

## 🎯 快速命令参考

```bash
# 上传部署包
scp lingzhi_ecosystem_deploy_*.tar.gz root@123.56.142.143:/tmp/

# SSH登录
ssh root@123.56.142.143

# 解压和部署
cd /tmp
tar -xzf lingzhi_ecosystem_deploy_*.tar.gz
cd admin-backend
../scripts/cloud_auto_deploy.sh

# 检查服务
systemctl status nginx
ps aux | grep python3
netstat -tlnp | grep -E ":80 |:8080 "

# 查看日志
tail -f /tmp/backend.log
tail -f /var/log/nginx/error.log

# 重启服务
systemctl restart nginx
cd /root/lingzhi-ecosystem/admin-backend
pkill -f "python.*app.py"
nohup python3 app.py > /tmp/backend.log 2>&1 &
```

---

## 📞 获取帮助

如果部署过程中遇到问题：

1. 查看日志文件
2. 运行诊断脚本（如果有）
3. 查看详细文档：`docs/CONNECTION_FIX_COMPLETE.md`
4. 提供错误信息截图

---

**部署完成后，访问 http://123.56.142.143**
