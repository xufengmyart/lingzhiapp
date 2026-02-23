# 生产环境部署准备清单

## ✅ 部署前准备

### 1. 环境准备

- [x] 已创建环境变量文件 `.env.production`
- [x] 已创建 Nginx 配置文件 `config/nginx/nginx.conf`
- [x] 已创建必要的目录结构
- [x] 已创建自动化部署脚本

### 2. 配置文件

- [x] `docker-compose.yml` - Docker 服务编排配置
- [x] `admin-backend/Dockerfile` - 后端容器镜像
- [x] `.dockerignore` - Docker 构建排除文件
- [x] `config/nginx/nginx.conf` - Nginx 反向代理配置
- [x] `scripts/production-deploy.sh` - 生产环境部署脚本
- [x] `scripts/deploy-docker.sh` - Docker 部署脚本

### 3. 监控配置

- [x] `monitoring/prometheus/prometheus.yml` - Prometheus 配置
- [x] `monitoring/loki/config.yml` - Loki 配置
- [x] `monitoring/promtail/config.yml` - Promtail 配置
- [x] `monitoring/grafana/provisioning/datasources/datasources.yml` - Grafana 数据源
- [x] `monitoring/grafana/provisioning/dashboards/dashboards.yml` - Grafana 仪表盘

### 4. CI/CD 配置

- [x] `.github/workflows/deploy.yml` - GitHub Actions 自动化部署

### 5. 文档

- [x] `docs/deployment-docker.md` - Docker 部署详细文档
- [x] `docs/QUICK_DEPLOY.md` - 快速部署指南

---

## 📦 服务器部署步骤

### 第一步：连接到服务器

```bash
# SSH 连接到生产服务器
ssh root@123.56.142.143

# 密码：Meiyue@root123
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

### 第四步：上传代码

#### 方法 1：使用 Git（推荐）

```bash
cd /opt
git clone <repository-url> lingzhi-ecosystem
cd lingzhi-ecosystem
```

#### 方法 2：使用 SCP 上传

```bash
# 在本地机器上执行
scp -r /workspace/projects/* root@123.56.142.143:/opt/lingzhi-ecosystem/
```

#### 方法 3：使用 rsync 同步

```bash
# 在本地机器上执行
rsync -avz --exclude='.git' --exclude='node_modules' \
  /workspace/projects/ root@123.56.142.143:/opt/lingzhi-ecosystem/
```

### 第五步：配置环境变量

```bash
cd /opt/lingzhi-ecosystem

# 复制环境变量文件
cp .env.production .env

# 编辑环境变量（根据实际情况修改）
vim .env
```

**重要配置项**：

```env
# JWT 密钥（建议修改为随机字符串）
JWT_SECRET_KEY=your-random-secret-key-here

# 扣子 API 配置
COZE_API_KEY=pat_vvXP4XqRr8zY9jLqS5h7M9rN2P5kQ8tW3Y
COZE_BASE_URL=https://api.coze.com
COZE_PROJECT_ID=7374110429512785930
LLM_MODEL=doubao-seed-1-6-251015

# Grafana 密码（可选，修改为强密码）
GRAFANA_PASSWORD=your-strong-password-here
```

### 第六步：构建前端（如果需要）

```bash
cd /opt/lingzhi-ecosystem/web-app

# 安装依赖
npm install

# 构建前端
npm run build

# 静态文件会生成到 dist 目录
```

### 第七步：执行部署

```bash
cd /opt/lingzhi-ecosystem

# 赋予部署脚本执行权限
chmod +x scripts/production-deploy.sh

# 执行部署
sudo bash scripts/production-deploy.sh
```

### 第八步：验证部署

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

部署成功后，可以通过以下地址访问服务：

### 前端
```
http://123.56.142.143
```

### API
```
http://123.56.142.143/api
```

### 健康检查
```
http://123.56.142.143/api/health
```

### 监控服务（如已启用）

#### Prometheus
```
http://123.56.142.143:9090
```

#### Grafana
```
http://123.56.142.143:3000
默认账号: admin
默认密码: admin（请在 .env 中修改）
```

#### Loki
```
http://123.56.142.143:3100
```

---

## 🔧 常用管理命令

### 服务管理

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f nginx
```

### 数据管理

```bash
# 进入后端容器
docker exec -it lingzhi-backend bash

# 查看数据库
docker exec -it lingzhi-backend sqlite3 /app/lingzhi_ecosystem.db

# 备份数据库
docker cp lingzhi-backend:/app/lingzhi_ecosystem.db ./backups/lingzhi_ecosystem_$(date +%Y%m%d).db
```

### 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新部署
sudo bash scripts/production-deploy.sh
```

---

## 🔒 安全配置

### 1. 配置防火墙

```bash
# 开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# 查看状态
sudo ufw status
```

### 2. 配置 SSL/HTTPS

```bash
# 安装 certbot
sudo apt-get install certbot

# 获取 SSL 证书
sudo certbot certonly --standalone -d www.meiyueart.com

# 配置 Nginx SSL
vim config/nginx/nginx.conf
# 取消注释 HTTPS 配置部分，修改证书路径

# 重启服务
docker-compose restart nginx
```

### 3. 修改默认密码

```bash
# 修改 Grafana 密码
vim .env
# 修改 GRAFANA_PASSWORD 行

# 修改 JWT 密钥
# 修改 JWT_SECRET_KEY 行
```

---

## 📊 监控和日志

### 启用监控服务

```bash
# 启动监控服务
docker-compose --profile monitoring up -d

# 查看监控服务状态
docker-compose --profile monitoring ps
```

### 查看日志

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看日志文件
tail -f admin-backend/logs/app.log

# 查看 Nginx 日志
tail -f nginx/logs/access.log
tail -f nginx/logs/error.log
```

### Grafana 配置

1. 访问 `http://123.56.142.143:3000`
2. 使用 `admin/admin` 登录
3. 修改密码
4. 配置数据源（Prometheus 和 Loki）
5. 导入仪表盘

---

## 🔄 备份和恢复

### 自动备份

```bash
# 创建备份脚本
cat > /opt/lingzhi-ecosystem/scripts/auto-backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/lingzhi-ecosystem/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker cp lingzhi-backend:/app/lingzhi_ecosystem.db "${BACKUP_DIR}/lingzhi_ecosystem_${DATE}.db"
find "${BACKUP_DIR}" -name "*.db" -mtime +7 -delete
EOF

chmod +x /opt/lingzhi-ecosystem/scripts/auto-backup.sh

# 添加到 crontab
crontab -e
# 每天凌晨 2 点执行备份
0 2 * * * /opt/lingzhi-ecosystem/scripts/auto-backup.sh
```

### 手动备份

```bash
# 备份数据库
docker cp lingzhi-backend:/app/lingzhi_ecosystem.db ./backups/lingzhi_ecosystem_$(date +%Y%m%d).db

# 备份配置
tar -czf backups/config_$(date +%Y%m%d).tar.gz .env config/
```

---

## 🔍 故障排查

### 容器启动失败

```bash
# 查看容器日志
docker-compose logs backend

# 检查配置文件
docker-compose config

# 检查端口占用
netstat -tlnp | grep :8080
```

### 健康检查失败

```bash
# 手动执行健康检查
docker exec lingzhi-backend curl -f http://localhost:8080/api/health

# 检查后端服务
docker exec lingzhi-backend ps aux
```

### 数据库连接失败

```bash
# 检查数据库文件
ls -la data/lingzhi_ecosystem.db

# 检查文件权限
docker exec lingzhi-backend ls -la /app/lingzhi_ecosystem.db
```

---

## 📞 支持

如遇到问题，请查看：

1. 日志文件：`admin-backend/logs/app.log`
2. 容器日志：`docker-compose logs -f`
3. 文档：`docs/deployment-docker.md`
4. 快速部署指南：`docs/QUICK_DEPLOY.md`

---

**服务器信息**：
- IP: 123.56.142.143
- 用户: root
- 密码: Meiyue@root123
- 部署路径: /opt/lingzhi-ecosystem

**部署状态**：
- 配置文件：✅ 已准备
- 部署脚本：✅ 已准备
- 文档：✅ 已准备
- 待执行：服务器部署

**下一步**：
1. 连接到服务器
2. 安装 Docker 和 Docker Compose
3. 上传代码
4. 配置环境变量
5. 执行部署脚本
6. 验证部署结果
