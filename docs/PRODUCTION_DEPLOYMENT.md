# 灵值生态园生产环境部署指南

## 概述

本文档描述了灵值生态园（Lingzhi Ecosystem）的生产环境部署流程和配置。

## 系统架构

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (80/443)   │
                    └──────┬──────┘
                           │
              ┌────────────┴────────────┐
              │                         │
    ┌─────────▼────────┐      ┌────────▼────────┐
    │  前端静态文件     │      │  后端 API        │
    │  React + Vite    │      │  Flask + Gunicorn│
    │  (port 4174)     │      │  (port 8080)     │
    └──────────────────┘      └─────────┬───────┘
                                        │
                              ┌─────────▼────────┐
                              │  SQLite 数据库    │
                              └──────────────────┘
```

## 技术栈

### 前端
- React 18.3.1
- TypeScript 5.4.5
- Vite 5.4.21
- PWA支持

### 后端
- Python 3.12+
- Flask 3.1.2
- Gunicorn 23.0.0 (生产级WSGI服务器)
- LangChain 1.0.3
- SQLite

### Web服务器
- Nginx (反向代理 + 静态文件服务)

## 前置要求

### 系统要求
- Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- 2核CPU + 4GB内存（最低配置）
- 20GB可用磁盘空间

### 软件依赖
```bash
# 安装基础依赖
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm nginx

# 或使用yum（CentOS/RHEL）
sudo yum install -y python3 python3-pip nodejs nginx
```

## 部署流程

### 方式一：使用自动化部署脚本（推荐）

1. **准备代码**
```bash
# 克隆或上传代码到服务器
cd /workspace/projects

# 确认已构建前端
cd web-app
npm run build
cd ..
```

2. **执行部署脚本**
```bash
# 使用root权限执行
sudo bash deploy-production-standard.sh
```

3. **配置域名**
```bash
# 编辑Nginx配置
sudo nano /etc/nginx/sites-available/lingzhi-ecosystem

# 修改 server_name 为实际域名
# server_name yourdomain.com www.yourdomain.com;

# 保存并退出
```

4. **重启服务**
```bash
sudo systemctl restart nginx
sudo systemctl restart lingzhi-backend
```

### 方式二：手动部署

#### 1. 创建目录结构
```bash
sudo mkdir -p /var/www/lingzhi-ecosystem/frontend
sudo mkdir -p /var/www/lingzhi-ecosystem/backend
sudo mkdir -p /var/log/lingzhi-backend
sudo mkdir -p /var/backups/lingzhi-ecosystem

sudo chown -R www-data:www-data /var/www/lingzhi-ecosystem
sudo chown -R www-data:www-data /var/log/lingzhi-backend
```

#### 2. 部署前端
```bash
# 构建前端
cd web-app
npm run build

# 复制到生产目录
sudo rm -rf /var/www/lingzhi-ecosystem/frontend/*
sudo cp -r dist/* /var/www/lingzhi-ecosystem/frontend/

sudo chmod -R 755 /var/www/lingzhi-ecosystem/frontend
sudo chown -R www-data:www-data /var/www/lingzhi-ecosystem/frontend
```

#### 3. 部署后端
```bash
# 创建虚拟环境
cd /var/www/lingzhi-ecosystem/backend
sudo -u www-data python3 -m venv venv

# 复制文件
sudo cp -f /path/to/admin-backend/app.py /var/www/lingzhi-ecosystem/backend/
sudo cp -f /path/to/admin-backend/gunicorn_config.py /var/www/lingzhi-ecosystem/backend/
sudo cp -f /path/to/admin-backend/requirements.txt /var/www/lingzhi-ecosystem/backend/
sudo cp -f /path/to/admin-backend/.env /var/www/lingzhi-ecosystem/backend/

# 安装依赖
sudo -u www-data venv/bin/pip install -r requirements.txt
```

#### 4. 配置systemd服务
```bash
# 复制服务配置
sudo cp -f /path/to/config/lingzhi-backend.service /etc/systemd/system/

# 重新加载
sudo systemctl daemon-reload

# 启用并启动
sudo systemctl enable lingzhi-backend
sudo systemctl start lingzhi-backend
```

#### 5. 配置Nginx
```bash
# 复制Nginx配置
sudo cp -f /path/to/config/nginx-lingzhi-ecosystem.conf /etc/nginx/sites-available/lingzhi-ecosystem

# 修改域名和路径
sudo nano /etc/nginx/sites-available/lingzhi-ecosystem

# 创建软链接
sudo ln -sf /etc/nginx/sites-available/lingzhi-ecosystem /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重载Nginx
sudo systemctl reload nginx
```

## 配置文件说明

### Gunicorn配置 (`gunicorn_config.py`)

```python
# 关键配置
bind = "0.0.0.0:8080"
workers = multiprocessing.cpu_count() * 2 + 1  # 自动计算worker数
worker_class = "sync"
timeout = 120
max_requests = 1000  # 每个worker处理1000个请求后重启，防止内存泄漏
```

### systemd服务 (`lingzhi-backend.service`)

```ini
[Unit]
Description=Lingzhi Ecosystem Backend Service (Gunicorn)
After=network-online.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/lingzhi-ecosystem/backend
ExecStart=/var/www/lingzhi-ecosystem/backend/venv/bin/gunicorn \
    --config gunicorn_config.py \
    --bind 0.0.0.0:8080 \
    app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### Nginx配置

```nginx
upstream lingzhi_backend {
    server 127.0.0.1:8080 fail_timeout=0;
}

server {
    listen 80;
    server_name yourdomain.com;

    # 前端静态文件
    root /var/www/lingzhi-ecosystem/frontend;
    index index.html;

    # 后端API代理
    location /api/ {
        proxy_pass http://lingzhi_backend/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # SPA路由支持
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

## SSL/HTTPS配置（可选）

如果需要HTTPS支持，使用Let's Encrypt免费证书：

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

## 监控和维护

### 查看服务状态

```bash
# 后端服务
sudo systemctl status lingzhi-backend

# Nginx服务
sudo systemctl status nginx
```

### 查看日志

```bash
# 后端日志
sudo journalctl -u lingzhi-backend -f

# 后端错误日志
sudo tail -f /var/log/lingzhi-backend/lingzhi-backend-error.log

# Nginx访问日志
sudo tail -f /var/log/nginx/lingzhi-ecosystem-access.log

# Nginx错误日志
sudo tail -f /var/log/nginx/lingzhi-ecosystem-error.log
```

### 重启服务

```bash
# 重启后端
sudo systemctl restart lingzhi-backend

# 重启Nginx
sudo systemctl restart nginx
```

### 更新部署

```bash
# 停止服务
sudo systemctl stop lingzhi-backend

# 备份现有文件
cd /var/backups/lingzhi-ecosystem
tar -czf backup_$(date +%Y%m%d_%H%M%S).tar.gz /var/www/lingzhi-ecosystem

# 部署新版本
cd /workspace/projects
sudo bash deploy-production-standard.sh
```

## 性能优化建议

### 1. Gunicorn优化

```python
# 对于高流量网站，可以增加worker数量
workers = 8  # 固定worker数

# 使用异步worker
worker_class = "gevent"  # 需要安装gevent
```

### 2. Nginx优化

```nginx
# 启用缓存
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=1g inactive=60m;

# 压缩优化
gzip_comp_level 9;

# 连接优化
keepalive_timeout 65;
```

### 3. 数据库优化

对于生产环境，建议迁移到PostgreSQL：

```bash
# 安装PostgreSQL
sudo apt install postgresql postgresql-contrib

# 创建数据库
sudo -u postgres createdb lingzhi_ecosystem
```

## 安全建议

1. **防火墙配置**
```bash
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

2. **文件权限**
```bash
# 确保敏感文件不可访问
sudo chmod 600 /var/www/lingzhi-ecosystem/backend/.env
```

3. **定期更新**
```bash
# 更新系统包
sudo apt update && sudo apt upgrade

# 更新Python依赖
cd /var/www/lingzhi-ecosystem/backend
sudo -u www-data venv/bin/pip install --upgrade -r requirements.txt
```

## 故障排除

### 后端无法启动

```bash
# 检查服务状态
sudo systemctl status lingzhi-backend

# 查看详细日志
sudo journalctl -u lingzhi-backend -n 100

# 检查端口占用
sudo lsof -i :8080
```

### Nginx配置错误

```bash
# 测试配置
sudo nginx -t

# 查看错误日志
sudo tail -f /var/log/nginx/error.log
```

### 前端无法访问

```bash
# 检查文件权限
ls -la /var/www/lingzhi-ecosystem/frontend/

# 检查Nginx配置
sudo cat /etc/nginx/sites-available/lingzhi-ecosystem
```

## 备份策略

### 自动备份脚本

创建 `/etc/cron.daily/lingzhi-backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="/var/backups/lingzhi-ecosystem"
DATE=$(date +%Y%m%d_%H%M%S)

# 备份数据库
cp /var/www/lingzhi-ecosystem/backend/lingzhi_ecosystem.db "$BACKUP_DIR/db_$DATE.db"

# 备份配置文件
tar -czf "$BACKUP_DIR/config_$DATE.tar.gz" /var/www/lingzhi-ecosystem/backend/.env

# 保留30天
find "$BACKUP_DIR" -name "*.db" -mtime +30 -delete
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +30 -delete
```

设置执行权限：
```bash
sudo chmod +x /etc/cron.daily/lingzhi-backup.sh
```

## 联系支持

如有问题，请联系技术支持团队。

---

**最后更新**: 2026-02-11
**版本**: v12.0.0
