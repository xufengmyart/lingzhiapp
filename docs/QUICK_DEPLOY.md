# 灵值生态园 - 生产环境部署指南

## 📋 部署前检查清单

在开始部署之前，请确保已完成以下检查：

### ✅ 服务器要求

- [ ] 操作系统：Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- [ ] 内存：最低 2GB，推荐 4GB+
- [ ] 磁盘：最低 20GB 可用空间
- [ ] CPU：最低 2 核，推荐 4 核+
- [ ] 网络端口：80, 443, 8080 已开放

### ✅ 软件要求

- [ ] Docker 20.10+
- [ ] Docker Compose 2.0+
- [ ] Git（可选，用于版本管理）

### ✅ 配置文件

- [ ] `.env` 文件已配置
- [ ] `docker-compose.yml` 文件已准备
- [ ] `admin-backend/Dockerfile` 已准备
- [ ] `config/nginx/nginx.conf` 已准备

---

## 🚀 快速部署（5 分钟）

### 步骤 1: 安装 Docker

#### Ubuntu/Debian

```bash
# 更新包索引
sudo apt-get update

# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

#### CentOS/RHEL

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sh

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 步骤 2: 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 步骤 3: 克隆代码

```bash
cd /opt
git clone <repository-url> lingzhi-ecosystem
cd lingzhi-ecosystem
```

或者使用其他方式上传代码到服务器。

### 步骤 4: 配置环境变量

```bash
# 复制环境变量模板
cp .env.production .env

# 编辑环境变量（根据实际情况修改）
vim .env
```

**关键配置项**：

```env
# JWT 密钥（建议修改）
JWT_SECRET_KEY=your-secret-key-here

# 扣子 API 密钥
COZE_API_KEY=pat_vvXP4XqRr8zY9jLqS5h7M9rN2P5kQ8tW3Y
COZE_BASE_URL=https://api.coze.com
COZE_PROJECT_ID=7374110429512785930
LLM_MODEL=doubao-seed-1-6-251015

# Grafana 密码（可选）
GRAFANA_PASSWORD=admin123
```

### 步骤 5: 执行部署

```bash
# 使用自动化部署脚本
sudo bash scripts/production-deploy.sh
```

部署脚本会自动完成以下操作：
1. 检查 Docker 环境
2. 创建必要的目录结构
3. 备份现有数据
4. 构建 Docker 镜像
5. 启动服务
6. 执行健康检查

### 步骤 6: 验证部署

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

### 前端访问

在浏览器中访问：
```
http://your-server-ip
```

### API 访问

```bash
# 基础 API 地址
http://your-server-ip/api

# 健康检查
http://your-server-ip/api/health
```

### 监控服务（如已启用）

```bash
# Prometheus
http://your-server-ip:9090

# Grafana（默认账号: admin/admin）
http://your-server-ip:3000

# Loki
http://your-server-ip:3100
```

---

## 📊 监控和日志

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看后端日志
docker-compose logs -f backend

# 查看最新 100 行日志
docker-compose logs --tail=100 backend

# 查看实时日志（带时间戳）
docker-compose logs -f --tail=100 --timestamps backend
```

### 查看日志文件

```bash
# 后端日志
tail -f admin-backend/logs/app.log

# Nginx 日志
tail -f nginx/logs/access.log
tail -f nginx/logs/error.log
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

# 重启特定服务
docker-compose restart backend

# 查看服务状态
docker-compose ps

# 查看资源使用
docker stats
```

### 数据管理

```bash
# 进入后端容器
docker exec -it lingzhi-backend bash

# 查看数据库
docker exec -it lingzhi-backend sqlite3 /app/lingzhi_ecosystem.db

# 备份数据库
docker cp lingzhi-backend:/app/lingzhi_ecosystem.db ./backups/lingzhi_ecosystem_$(date +%Y%m%d).db

# 恢复数据库
docker cp ./backups/lingzhi_ecosystem_backup.db lingzhi-backend:/app/lingzhi_ecosystem.db
```

### 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建和部署
sudo bash scripts/production-deploy.sh
```

---

## 🔒 安全建议

### 1. 修改默认密码

```bash
# 修改 Grafana 密码
vim .env
# 修改 GRAFANA_PASSWORD 行

# 修改 JWT 密钥
# 修改 JWT_SECRET_KEY 行
```

### 2. 配置防火墙

```bash
# Ubuntu/Debian
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable

# CentOS/RHEL
sudo firewall-cmd --permanent --add-port=80/tcp
sudo firewall-cmd --permanent --add-port=443/tcp
sudo firewall-cmd --permanent --add-port=22/tcp
sudo firewall-cmd --reload
```

### 3. 配置 SSL/HTTPS

```bash
# 安装 certbot
sudo apt-get install certbot

# 获取 SSL 证书
sudo certbot certonly --standalone -d www.meiyueart.com

# 配置 Nginx SSL
# 编辑 config/nginx/nginx.conf，取消注释 HTTPS 配置部分
# 修改证书路径为 /etc/letsencrypt/live/www.meiyueart.com/

# 重启 Nginx
docker-compose restart nginx
```

### 4. 限制容器资源

在 `docker-compose.yml` 中添加资源限制：

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## 🔍 故障排查

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器日志
docker-compose logs backend

# 检查配置文件
docker-compose config

# 检查端口占用
netstat -tlnp | grep :8080
```

#### 2. 健康检查失败

```bash
# 手动执行健康检查
docker exec lingzhi-backend curl -f http://localhost:8080/api/health

# 检查后端服务
docker exec lingzhi-backend ps aux
```

#### 3. 数据库连接失败

```bash
# 检查数据库文件权限
ls -la data/lingzhi_ecosystem.db

# 检查数据库文件是否存在
docker exec lingzhi-backend ls -la /app/lingzhi_ecosystem.db
```

#### 4. 磁盘空间不足

```bash
# 检查磁盘使用
df -h

# 清理 Docker 镜像
docker system prune -a

# 清理旧日志
find . -name "*.log" -size +100M -delete
```

### 日志分析

```bash
# 搜索错误日志
docker-compose logs backend | grep -i error

# 查看最近的错误
docker-compose logs --tail=50 backend | grep -i error

# 导出日志
docker-compose logs backend > backend.log
```

---

## 📈 性能优化

### 1. 启用监控服务

```bash
# 启动监控服务
docker-compose --profile monitoring up -d

# 查看 Prometheus
http://your-server-ip:9090

# 查看 Grafana
http://your-server-ip:3000
```

### 2. 配置缓存（可选）

考虑引入 Redis 缓存以提升性能：

1. 在 `docker-compose.yml` 中取消 Redis 配置的注释
2. 重启服务：`docker-compose up -d`

### 3. 数据库优化（可选）

考虑迁移到 PostgreSQL：

1. 在 `docker-compose.yml` 中取消 PostgreSQL 配置的注释
2. 修改环境变量配置
3. 重启服务：`docker-compose up -d`

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

### 恢复数据

```bash
# 恢复数据库
docker cp ./backups/lingzhi_ecosystem_backup.db lingzhi-backend:/app/lingzhi_ecosystem.db
docker-compose restart backend

# 恢复配置
tar -xzf backups/config_backup.tar.gz
```

---

## 📞 技术支持

如果遇到问题：

1. 查看日志：`docker-compose logs -f`
2. 检查文档：`docs/deployment-docker.md`
3. 联系技术支持

---

## 📚 相关文档

- [Docker 部署详细文档](docs/deployment-docker.md)
- [API 文档](API_ENDPOINT_TEST_REPORT.md)
- [架构文档](SYSTEM_ARCHITECTURE.md)

---

**文档版本**: v12.0.0  
**最后更新**: 2025-01-10  
**维护者**: Lingzhi Ecosystem Team
