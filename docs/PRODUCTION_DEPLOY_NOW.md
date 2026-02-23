# 🚀 生产环境快速部署指南

## ⚠️ 重要说明

当前环境（扣子容器）中没有安装 Docker，无法直接执行 Docker 部署。

**正确的部署流程**：
1. 使用远程部署脚本连接到生产服务器
2. 在生产服务器上安装 Docker 和 Docker Compose
3. 同步代码并执行部署

---

## 📋 方案选择

### 方案一：使用远程部署脚本（推荐）

自动化完成所有部署步骤，一键部署到生产服务器。

```bash
# 赋予脚本执行权限
chmod +x scripts/remote-deploy.sh

# 执行远程部署
bash scripts/remote-deploy.sh
```

**脚本会自动完成**：
- ✅ 检查服务器连接
- ✅ 安装 Docker 和 Docker Compose
- ✅ 同步代码到服务器
- ✅ 配置环境变量
- ✅ 创建目录结构
- ✅ 构建前端应用
- ✅ 部署后端服务
- ✅ 执行健康检查

### 方案二：手动部署（用于调试）

如果需要手动控制部署过程，请按照以下步骤操作。

---

## 🔧 手动部署步骤

### 第一步：连接到生产服务器

```bash
# SSH 连接
ssh root@123.56.142.143

# 输入密码：Meiyue@root123
```

### 第二步：安装 Docker

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 第三步：安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 第四步：创建部署目录

```bash
# 创建部署目录
mkdir -p /opt/lingzhi-ecosystem
cd /opt/lingzhi-ecosystem
```

### 第五步：上传代码

**在本地机器（当前环境）执行**：

#### 方法 1：使用 rsync（推荐，需要先安装）

```bash
# 安装 rsync（如果未安装）
apt-get install rsync

# 同步代码（排除不必要的文件）
rsync -avz --delete \
  --exclude='.git' \
  --exclude='node_modules' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  --exclude='.pytest_cache' \
  --exclude='.vscode' \
  --exclude='.idea' \
  --exclude='*.log' \
  --exclude='backups' \
  --exclude='*.db' \
  ./ root@123.56.142.143:/opt/lingzhi-ecosystem/
```

#### 方法 2：使用 SCP

```bash
# 复制核心文件
scp -r admin-backend/ root@123.56.142.143:/opt/lingzhi-ecosystem/
scp -r web-app/ root@123.56.142.143:/opt/lingzhi-ecosystem/
scp -r config/ root@123.56.142.143:/opt/lingzhi-ecosystem/
scp -r monitoring/ root@123.56.142.143:/opt/lingzhi-ecosystem/
scp -r scripts/ root@123.56.142.143:/opt/lingzhi-ecosystem/
scp docker-compose.yml root@123.56.142.143:/opt/lingzhi-ecosystem/
scp .env.production root@123.56.142.143:/opt/lingzhi-ecosystem/
```

### 第六步：配置环境变量

**在服务器上执行**：

```bash
cd /opt/lingzhi-ecosystem

# 复制环境变量文件
cp .env.production .env

# 编辑环境变量（可选）
vim .env
```

### 第七步：创建必要目录

```bash
cd /opt/lingzhi-ecosystem

# 创建目录
mkdir -p data
mkdir -p admin-backend/logs
mkdir -p admin-backend/storage
mkdir -p admin-backend/backups
mkdir -p nginx/logs
mkdir -p monitoring/prometheus/data
mkdir -p monitoring/grafana/data
mkdir -p monitoring/grafana/provisioning/datasources
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/loki/data

# 设置权限
chmod -R 755 admin-backend/logs
chmod -R 755 nginx/logs
```

### 第八步：构建前端

```bash
cd /opt/lingzhi-ecosystem/web-app

# 安装依赖
npm install

# 构建前端
npm run build
```

### 第九步：执行部署

```bash
cd /opt/lingzhi-ecosystem

# 赋予部署脚本执行权限
chmod +x scripts/production-deploy.sh

# 执行部署
sudo bash scripts/production-deploy.sh
```

---

## ✅ 验证部署

### 在服务器上执行：

```bash
# 检查服务状态
docker-compose ps

# 查看服务日志
docker-compose logs -f backend

# 健康检查
curl http://localhost:8080/api/health

# 应该返回: {"status": "ok", "message": "Service is healthy"}
```

---

## 🌐 访问服务

部署成功后，在浏览器中访问：

- **前端**: http://123.56.142.143
- **API**: http://123.56.142.143/api
- **健康检查**: http://123.56.142.143/api/health
- **Prometheus** (如启用): http://123.56.142.143:9090
- **Grafana** (如启用): http://123.56.142.143:3000

---

## 📊 监控和管理

### 查看日志

```bash
# 在服务器上执行
cd /opt/lingzhi-ecosystem

# 查看后端日志
docker-compose logs -f backend

# 查看所有服务日志
docker-compose logs -f
```

### 管理服务

```bash
# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 启动服务
docker-compose up -d

# 查看资源使用
docker stats
```

### 数据备份

```bash
# 备份数据库
docker cp lingzhi-backend:/app/lingzhi_ecosystem.db ./backups/lingzhi_ecosystem_$(date +%Y%m%d).db

# 恢复数据库
docker cp ./backups/lingzhi_ecosystem_backup.db lingzhi-backend:/app/lingzhi_ecosystem.db
docker-compose restart backend
```

---

## 🔒 安全配置

### 配置防火墙

```bash
# 开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 配置 SSL/HTTPS

```bash
# 安装 certbot
sudo apt-get install certbot

# 获取 SSL 证书
sudo certbot certonly --standalone -d www.meiyueart.com

# 配置 Nginx SSL
vim config/nginx/nginx.conf
# 取消注释 HTTPS 配置部分

# 重启 Nginx
docker-compose restart nginx
```

---

## 🆘 故障排查

### 问题 1：容器启动失败

```bash
# 查看容器日志
docker-compose logs backend

# 检查配置文件
docker-compose config

# 检查端口占用
netstat -tlnp | grep :8080
```

### 问题 2：健康检查失败

```bash
# 手动执行健康检查
docker exec lingzhi-backend curl -f http://localhost:8080/api/health

# 检查后端服务
docker exec lingzhi-backend ps aux
```

### 问题 3：数据库连接失败

```bash
# 检查数据库文件
ls -la data/lingzhi_ecosystem.db

# 检查文件权限
docker exec lingzhi-backend ls -la /app/lingzhi_ecosystem.db
```

---

## 📞 联系支持

如果遇到问题：

1. 查看日志：`docker-compose logs -f`
2. 查看文档：`docs/deployment-docker.md`
3. 查看部署清单：`docs/DEPLOYMENT_CHECKLIST.md`

---

## 📚 相关文档

- [Docker 部署详细文档](docs/deployment-docker.md)
- [快速部署指南](docs/QUICK_DEPLOY.md)
- [部署检查清单](docs/DEPLOYMENT_CHECKLIST.md)

---

**部署脚本位置**：
- 远程部署：`scripts/remote-deploy.sh`
- 生产部署：`scripts/production-deploy.sh`

**服务器信息**：
- IP: 123.56.142.143
- 用户: root
- 密码: Meiyue@root123
- 部署路径: /opt/lingzhi-ecosystem
