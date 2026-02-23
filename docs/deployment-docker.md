# 灵值生态园 - Docker 容器化部署指南

## 📋 目录

- [概述](#概述)
- [架构说明](#架构说明)
- [环境准备](#环境准备)
- [快速开始](#快速开始)
- [详细配置](#详细配置)
- [监控与日志](#监控与日志)
- [故障排查](#故障排查)
- [安全建议](#安全建议)
- [维护与优化](#维护与优化)

---

## 概述

本文档介绍如何使用 Docker 和 Docker Compose 部署灵值生态园系统。容器化部署提供了一致的环境、易于扩展和快速回滚的能力。

### 核心优势

✅ **环境一致性** - 开发、测试、生产环境完全一致  
✅ **快速部署** - 一键部署，自动化流程  
✅ **易于扩展** - 支持水平扩展和负载均衡  
✅ **快速回滚** - 镜像版本化管理，支持秒级回滚  
✅ **资源隔离** - 容器级别的资源隔离  
✅ **监控完善** - 集成 Prometheus + Grafana + Loki  

---

## 架构说明

### 部署架构

```
┌─────────────────────────────────────────────────────────┐
│                      用户浏览器                           │
└────────────────────┬────────────────────────────────────┘
                     │ HTTPS (443) / HTTP (80)
┌────────────────────▼────────────────────────────────────┐
│                  Nginx (反向代理)                         │
│              - SSL 终端                                   │
│              - 静态文件服务                                │
│              - 负载均衡                                   │
└────────────────────┬────────────────────────────────────┘
                     │ 反向代理
┌────────────────────▼────────────────────────────────────┐
│              Flask 后端 (Gunicorn)                       │
│              - RESTful API                                │
│              - 业务逻辑                                    │
│              - 数据访问                                    │
└────────────────────┬────────────────────────────────────┘
                     │ SQLite
┌────────────────────▼────────────────────────────────────┐
│              数据存储 (SQLite)                            │
│              - 持久化存储                                  │
│              - 数据备份                                    │
└─────────────────────────────────────────────────────────┘
```

### 服务列表

| 服务名 | 端口 | 说明 | 可选 |
|--------|------|------|------|
| backend | 8080 | Flask 后端服务 | ❌ |
| nginx | 80, 443 | 反向代理服务器 | ❌ |
| prometheus | 9090 | 监控数据采集 | ✅ |
| grafana | 3000 | 监控可视化 | ✅ |
| loki | 3100 | 日志存储 | ✅ |
| promtail | 9080 | 日志采集 | ✅ |
| postgres | 5432 | PostgreSQL 数据库 | ✅ |
| redis | 6379 | 缓存服务 | ✅ |

---

## 环境准备

### 系统要求

- **操作系统**: Linux (推荐 Ubuntu 20.04+ / CentOS 7+)
- **内存**: 最低 2GB，推荐 4GB+
- **磁盘**: 最低 20GB 可用空间
- **CPU**: 最低 2 核，推荐 4 核+

### 安装 Docker

#### Ubuntu/Debian

```bash
# 更新包索引
sudo apt-get update

# 安装依赖
sudo apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# 添加 Docker 官方 GPG 密钥
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# 添加 Docker 仓库
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# 安装 Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

#### CentOS/RHEL

```bash
# 安装依赖
sudo yum install -y yum-utils

# 添加 Docker 仓库
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# 安装 Docker
sudo yum install -y docker-ce docker-ce-cli containerd.io

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
```

### 安装 Docker Compose

```bash
# 下载 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

### 配置 Docker 用户（可选）

```bash
# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 重新登录或执行以下命令使配置生效
newgrp docker

# 验证
docker ps
```

---

## 快速开始

### 1. 克隆代码

```bash
cd /opt
git clone <repository-url> lingzhi-ecosystem
cd lingzhi-ecosystem
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

**关键配置项**：

```env
# JWT 配置
JWT_SECRET_KEY=your-secret-key-here
JWT_EXPIRATION=86400

# 扣子 API 配置
COZE_API_KEY=your-coze-api-key
COZE_BASE_URL=https://api.coze.com
COZE_PROJECT_ID=your-project-id

# 数据库配置
DATABASE_PATH=/app/lingzhi_ecosystem.db

# Docker Registry 配置（用于 CI/CD）
DOCKER_REGISTRY=registry.cn-hangzhou.aliyuncs.com
DOCKER_USERNAME=your-username
DOCKER_PASSWORD=your-password

# 监控配置
GRAFANA_PASSWORD=admin
```

### 3. 创建必要目录

```bash
# 创建数据目录
mkdir -p data
mkdir -p admin-backend/logs
mkdir -p admin-backend/storage
mkdir -p admin-backend/backups
mkdir -p nginx/logs
mkdir -p monitoring/prometheus/data
mkdir -p monitoring/grafana/data
mkdir -p monitoring/loki/data

# 设置权限
chmod -R 755 admin-backend/logs
chmod -R 755 nginx/logs
```

### 4. 启动服务

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f backend
docker-compose logs -f nginx
```

### 5. 验证部署

```bash
# 健康检查
curl http://localhost:8080/api/health

# 访问前端
# 打开浏览器访问: http://your-server-ip

# 访问监控（如果启用）
# Prometheus: http://your-server-ip:9090
# Grafana: http://your-server-ip:3000 (用户名: admin, 密码: admin)
```

### 6. 初始化数据库

```bash
# 进入后端容器
docker exec -it lingzhi-backend bash

# 初始化数据库
python scripts/init_db.py

# 退出容器
exit
```

---

## 详细配置

### 后端配置

#### Dockerfile 说明

`admin-backend/Dockerfile` 采用多阶段构建：

1. **依赖阶段**: 安装 Python 依赖
2. **运行阶段**: 复制代码和依赖，配置运行环境

#### 环境变量

在 `docker-compose.yml` 中配置：

```yaml
environment:
  - DATABASE_PATH=/app/lingzhi_ecosystem.db
  - JWT_SECRET_KEY=${JWT_SECRET_KEY}
  - JWT_EXPIRATION=86400
  - COZE_WORKLOAD_IDENTITY_API_KEY=${COZE_API_KEY}
  - COZE_INTEGRATION_MODEL_BASE_URL=${COZE_BASE_URL}
  - LOG_LEVEL=INFO
```

#### 健康检查

后端服务配置了健康检查：

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

### Nginx 配置

#### 反向代理配置

```nginx
server {
    listen 80;
    server_name www.meiyueart.com;

    # 反向代理到后端
    location /api {
        proxy_pass http://backend:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 静态文件服务
    location / {
        root /var/www/meiyueart-v2;
        try_files $uri $uri/ /index.html;
    }
}
```

#### SSL 配置（HTTPS）

```bash
# 安装 certbot
sudo apt-get install certbot

# 获取 SSL 证书
sudo certbot certonly --standalone -d www.meiyueart.com

# 证书路径
# /etc/letsencrypt/live/www.meiyueart.com/fullchain.pem
# /etc/letsencrypt/live/www.meiyueart.com/privkey.pem
```

### 数据持久化

#### SQLite 数据库

```yaml
volumes:
  - ./data/lingzhi_ecosystem.db:/app/lingzhi_ecosystem.db
```

#### 日志持久化

```yaml
volumes:
  - ./admin-backend/logs:/app/logs
```

### 资源限制

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

## 监控与日志

### 启用监控

```bash
# 启动监控服务
docker-compose --profile monitoring up -d

# 查看监控服务
docker-compose --profile monitoring ps
```

### Prometheus 配置

访问 `http://your-server-ip:9090`

**监控指标**：
- API 请求量
- API 响应时间
- 错误率
- 系统资源使用

### Grafana 配置

访问 `http://your-server-ip:3000`

**默认账号**：
- 用户名: `admin`
- 密码: `admin`

**配置数据源**：
1. 登录 Grafana
2. 进入 Configuration → Data Sources
3. 添加 Prometheus 数据源
4. 添加 Loki 数据源

### 日志查询

#### Loki 日志查询

访问 Grafana → Explore → 选择 Loki 数据源

**查询示例**：

```logql
# 查询后端所有日志
{job="backend"}

# 查询后端错误日志
{job="backend"} |= "ERROR"

# 查询特定 API 请求
{job="backend"} | json | method="POST" | path="/api/users/signin"

# 查询 Nginx 访问日志
{job="nginx", type="access"}

# 查询 Nginx 错误日志
{job="nginx", type="error"}
```

#### 查看容器日志

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看所有服务日志
docker-compose logs -f

# 查看最近 100 行日志
docker-compose logs --tail=100 backend
```

---

## 故障排查

### 常见问题

#### 1. 容器启动失败

```bash
# 查看容器状态
docker-compose ps

# 查看容器日志
docker-compose logs backend

# 检查配置文件
docker-compose config
```

#### 2. 数据库连接失败

```bash
# 检查数据库文件权限
ls -la data/lingzhi_ecosystem.db

# 进入容器检查
docker exec -it lingzhi-backend bash
ls -la /app/lingzhi_ecosystem.db
```

#### 3. API 返回 500 错误

```bash
# 查看后端日志
docker-compose logs backend | grep ERROR

# 检查环境变量
docker exec lingzhi-backend env | grep COZE

# 进入容器调试
docker exec -it lingzhi-backend bash
python -c "import sqlite3; conn = sqlite3.connect('/app/lingzhi_ecosystem.db'); print(conn.execute('SELECT COUNT(*) FROM users').fetchone())"
```

#### 4. 健康检查失败

```bash
# 手动执行健康检查
docker exec lingzhi-backend curl -f http://localhost:8080/api/health

# 检查服务是否正常启动
docker exec lingzhi-backend ps aux
```

#### 5. 磁盘空间不足

```bash
# 查看磁盘使用
df -h

# 清理 Docker 镜像
docker system prune -a

# 清理日志文件
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

## 安全建议

### 1. 使用非 root 用户运行容器

Dockerfile 已配置为使用非 root 用户：

```dockerfile
USER appuser
```

### 2. 限制容器权限

```yaml
security_opt:
  - no-new-privileges:true
read_only: true
```

### 3. 使用 secrets 管理敏感信息

```yaml
secrets:
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

### 4. 定期更新镜像

```bash
# 更新镜像
docker-compose pull
docker-compose up -d
```

### 5. 配置防火墙

```bash
# 只开放必要端口
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw enable
```

### 6. 配置 SSL/TLS

使用 Let's Encrypt 免费证书：

```bash
sudo certbot certonly --standalone -d www.meiyueart.com
```

---

## 维护与优化

### 备份策略

#### 数据库备份

```bash
# 创建备份脚本
cat > scripts/backup-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/opt/lingzhi-ecosystem/backups"
DATE=$(date +%Y%m%d_%H%M%S)
docker cp lingzhi-backend:/app/lingzhi_ecosystem.db "${BACKUP_DIR}/lingzhi_ecosystem_${DATE}.db"
find "${BACKUP_DIR}" -name "*.db" -mtime +7 -delete
EOF

chmod +x scripts/backup-db.sh

# 添加到 crontab
crontab -e
# 每天凌晨 2 点执行备份
0 2 * * * /opt/lingzhi-ecosystem/scripts/backup-db.sh
```

#### 配置备份

```bash
# 备份配置文件
tar -czf backups/config_$(date +%Y%m%d).tar.gz .env config/
```

### 性能优化

#### 1. 启用缓存

考虑引入 Redis 缓存：

```yaml
redis:
  image: redis:7-alpine
  command: redis-server --appendonly yes
  volumes:
    - ./data/redis:/data
```

#### 2. 数据库优化

考虑迁移到 PostgreSQL：

```yaml
postgres:
  image: postgres:15-alpine
  environment:
    POSTGRES_DB: lingzhi_ecosystem
    POSTGRES_USER: lingzhi
    POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
```

#### 3. 资源限制

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
```

### 自动化部署

使用部署脚本：

```bash
# 使用自动化部署脚本
sudo bash scripts/deploy-docker.sh
```

### 监控告警

配置 Prometheus 告警规则：

```yaml
groups:
  - name: api_alerts
    rules:
      - alert: HighErrorRate
        expr: rate(api_errors_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
```

---

## 附录

### 常用命令

```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 重启服务
docker-compose restart

# 查看日志
docker-compose logs -f [service_name]

# 进入容器
docker exec -it [container_name] bash

# 查看资源使用
docker stats

# 清理资源
docker system prune -a

# 更新服务
docker-compose pull
docker-compose up -d
```

### 目录结构

```
lingzhi-ecosystem/
├── admin-backend/          # 后端代码
│   ├── Dockerfile
│   ├── app.py
│   └── ...
├── web-app/                # 前端代码
│   └── ...
├── config/                 # 配置文件
│   └── nginx/
├── scripts/                # 脚本
│   ├── deploy-docker.sh
│   └── backup-db.sh
├── monitoring/             # 监控配置
│   ├── prometheus/
│   ├── grafana/
│   ├── loki/
│   └── promtail/
├── data/                   # 数据目录
│   └── lingzhi_ecosystem.db
├── docker-compose.yml
└── .env
```

### 相关链接

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Prometheus 文档](https://prometheus.io/docs/)
- [Grafana 文档](https://grafana.com/docs/)
- [Loki 文档](https://grafana.com/docs/loki/latest/)

---

**文档版本**: v12.0.0  
**最后更新**: 2025-01-10  
**维护者**: Lingzhi Ecosystem Team
