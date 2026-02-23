# 部署指南

## 目录

1. [环境准备](#环境准备)
2. [快速开始](#快速开始)
3. [详细部署流程](#详细部署流程)
4. [模块化部署](#模块化部署)
5. [故障处理](#故障处理)
6. [最佳实践](#最佳实践)

---

## 环境准备

### 本地环境

```bash
# 1. 安装 Python 依赖
pip install paramiko bcrypt python-dateutil

# 2. 配置服务器信息
# 编辑 universal_deploy.py 中的 DeployConfig 类
```

### 服务器环境

```bash
# 1. 安装 Python 依赖
pip install flask flask-cors flask-sqlalchemy bcrypt pyjwt

# 2. 配置环境变量
# 编辑 .env 文件
```

---

## 快速开始

### 1. 首次部署

```bash
# 部署所有模块
python3 universal_deploy.py --all
```

### 2. 增量部署（推荐）

```bash
# 只部署变化的文件
python3 universal_deploy.py --admin_api
```

### 3. 强制全量部署

```bash
# 强制上传所有文件
python3 universal_deploy.py --all --force
```

---

## 详细部署流程

### 步骤 1：代码审查

```bash
# 1. 检查代码语法
python3 -m py_compile admin_management_api.py

# 2. 运行测试
python3 -m pytest tests/

# 3. 代码格式检查
black --check admin_management_api.py
```

### 步骤 2：本地测试

```bash
# 启动本地服务
cd /root/workspace/admin-backend
python3 app.py

# 测试登录
curl -X POST http://localhost:8080/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 步骤 3：执行部署

```bash
# 执行部署
python3 universal_deploy.py --all

# 查看输出
✅ 部署成功！
📋 访问信息:
   登录地址: https://meiyueart.com/admin/login
   用户名: admin
   密码: admin123
```

### 步骤 4：验证功能

```bash
# 1. 登录后台
https://meiyueart.com/admin/login

# 2. 测试各功能模块
- 用户管理
- 智能体管理
- 知识库管理
- 角色权限管理
- 用户类型管理

# 3. 查看日志
ssh root@123.56.142.143
tail -n 100 /tmp/app.log
```

### 步骤 5：监控运行

```bash
# 监控服务状态
ps aux | grep python

# 监控端口
netstat -tlnp | grep 8080

# 监控日志
tail -f /tmp/app.log
```

---

## 模块化部署

### 部署后台管理 API

```bash
# 仅部署后台管理 API
python3 universal_deploy.py --admin_api
```

### 部署路由模块

```bash
# 仅部署路由模块
python3 universal_deploy.py --routes
```

### 组合部署

```bash
# 部署多个模块
python3 universal_deploy.py --admin_api --routes --config
```

---

## 故障处理

### 问题 1：连接服务器失败

**症状：**
```
paramiko.ssh_exception.AuthenticationException: Authentication failed.
```

**解决方案：**
```bash
# 1. 检查服务器信息
# 编辑 universal_deploy.py 中的 DeployConfig 类

# 2. 手动测试连接
ssh root@123.56.142.143

# 3. 检查 SSH 密钥
ssh-keygen -t rsa
ssh-copy-id root@123.56.142.143
```

---

### 问题 2：部署后登录失败

**症状：**
```
{"error_code": "INVALID_ADMIN_PASSWORD", "message": "用户名或密码错误"}
```

**解决方案：**
```bash
# 1. 检查数据库
ssh root@123.56.142.143
sqlite3 /root/workspace/admin-backend/lingzhi_ecosystem.db
SELECT * FROM admins WHERE username = 'admin';

# 2. 重置密码
python3 -c "
import sqlite3, bcrypt
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()
pwd = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
cursor.execute(\"UPDATE admins SET password_hash = ? WHERE username = 'admin'\", (pwd,))
conn.commit()
conn.close()
print('密码已重置')
"

# 3. 测试登录
curl -X POST http://localhost:8080/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

### 问题 3：API 返回 404

**症状：**
```
{"error": "Not Found"}
```

**解决方案：**
```bash
# 1. 检查服务是否运行
ps aux | grep python

# 2. 检查端口
netstat -tlnp | grep 8080

# 3. 检查路由注册
ssh root@123.56.142.143
grep -n 'admin_bp' /root/workspace/admin-backend/app.py

# 4. 重启服务
pkill -f 'python.*app.py'
cd /root/workspace/admin-backend
nohup python3 app.py > /tmp/app.log 2>&1 &
```

---

### 问题 4：部署后部分功能异常

**症状：**
- 登录成功，但部分 API 返回错误
- 服务启动但某些功能不可用

**解决方案：**
```bash
# 1. 查看应用日志
ssh root@123.56.142.143
tail -n 100 /tmp/app.log

# 2. 检查数据库表
sqlite3 /root/workspace/admin-backend/lingzhi_ecosystem.db ".tables"

# 3. 检查文件权限
ls -la /root/workspace/admin-backend/

# 4. 重新部署
python3 universal_deploy.py --all --force
```

---

### 问题 5：部署超时

**症状：**
```
[Command timeout]
```

**解决方案：**
```bash
# 1. 检查服务器负载
ssh root@123.56.142.143
top
free -m

# 2. 清理临时文件
rm -f /tmp/*.py

# 3. 分步部署
python3 universal_deploy.py --admin_api
python3 universal_deploy.py --routes
```

---

## 最佳实践

### 1. 定期备份

```bash
# 创建备份脚本
cat > /root/backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

# 备份数据库
cp /root/workspace/admin-backend/lingzhi_ecosystem.db \
   $BACKUP_DIR/lingzhi_ecosystem_$DATE.db

# 备份配置文件
cp /root/workspace/admin-backend/.env \
   $BACKUP_DIR/env_$DATE

# 删除 30 天前的备份
find $BACKUP_DIR -mtime +30 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /root/backup.sh

# 设置定时任务
crontab -e
# 添加：0 2 * * * /root/backup.sh
```

---

### 2. 监控告警

```bash
# 创建监控脚本
cat > /root/monitor.sh << 'EOF'
#!/bin/bash

# 检查服务是否运行
if ! pgrep -f "python.*app.py" > /dev/null; then
    echo "Service is not running!"
    # 重启服务
    cd /root/workspace/admin-backend
    nohup python3 app.py > /tmp/app.log 2>&1 &
    echo "Service restarted"
fi

# 检查磁盘空间
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "Disk usage is high: $DISK_USAGE%"
    # 发送告警
fi

# 检查内存
MEM_USAGE=$(free | grep Mem | awk '{print $3/$2 * 100.0}')
if [ $(echo "$MEM_USAGE > 80" | bc) -eq 1 ]; then
    echo "Memory usage is high: $MEM_USAGE%"
fi
EOF

chmod +x /root/monitor.sh

# 设置定时任务（每 5 分钟）
crontab -e
# 添加：*/5 * * * * /root/monitor.sh
```

---

### 3. 日志管理

```bash
# 日志轮转
cat > /etc/logrotate.d/app << 'EOF'
/tmp/app.log {
    daily
    rotate 7
    compress
    missingok
    notifempty
    create 644 root root
}
EOF

# 查看日志
tail -f /tmp/app.log

# 搜索错误
grep -i "error\|exception" /tmp/app.log | tail -n 20
```

---

### 4. 版本管理

```bash
# 创建版本标签
git tag v1.0.0
git push origin v1.0.0

# 查看版本历史
git log --oneline --all --decorate

# 回滚到指定版本
git checkout v1.0.0
python3 universal_deploy.py --all --force
```

---

### 5. 性能优化

```bash
# 1. 使用 Gunicorn（生产环境）
pip install gunicorn

# 启动 Gunicorn
cd /root/workspace/admin-backend
gunicorn -w 4 -b 0.0.0.0:8080 app:app \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log \
  --daemon

# 2. 配置 Nginx 反向代理
# /etc/nginx/sites-available/meiyueart.com
server {
    listen 443 ssl;
    server_name meiyueart.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# 3. 启用缓存
# 在 app.py 中添加
from flask_caching import Cache
cache = Cache(app, config={'CACHE_TYPE': 'redis', 'CACHE_REDIS_URL': 'redis://localhost:6379/0'})

@app.route('/api/admin/users')
@cache.cached(timeout=300)
def get_users():
    ...
```

---

## 附录

### A. 常用命令

```bash
# 连接服务器
ssh root@123.56.142.143

# 查看服务状态
ps aux | grep python

# 重启服务
pkill -f 'python.*app.py'
cd /root/workspace/admin-backend && nohup python3 app.py > /tmp/app.log 2>&1 &

# 查看日志
tail -f /tmp/app.log

# 备份数据库
cp lingzhi_ecosystem.db lingzhi_ecosystem_backup_$(date +%Y%m%d).db

# 测试 API
curl -X POST http://localhost:8080/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### B. 环境变量

```bash
# .env 文件示例
DATABASE_URL=sqlite:///lingzhi_ecosystem.db
JWT_SECRET_KEY=your_secret_key_here
JWT_EXPIRATION=604800
DEBUG=False
```

### C. 端口说明

| 端口 | 用途 | 说明 |
|------|------|------|
| 8080 | 后端服务 | Flask 开发服务器 |
| 5000 | 后端服务 | Gunicorn 服务 |
| 443 | HTTPS | Nginx HTTPS |
| 80 | HTTP | Nginx HTTP |

---

**文档版本：** v1.0.0
**最后更新：** 2024-02-17
