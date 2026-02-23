# 灵值生态园 - 生产环境部署文档

## 系统架构

```
用户浏览器 → Nginx (80端口) → Flask后端 (8080端口)
                      ↓
                 静态文件服务
            (public/ 目录)
```

## 服务组件

### 1. Nginx 反向代理
- **端口**: 80
- **配置文件**: `/etc/nginx/sites-available/meiyueart.com`
- **功能**:
  - 服务前端静态文件
  - 反向代理 API 请求到后端
  - 处理静态资源缓存

### 2. Flask 后端服务
- **端口**: 8080
- **目录**: `/workspace/projects/admin-backend`
- **数据库**: `lingzhi_ecosystem.db`
- **功能**:
  - 用户认证
  - 资源管理（用户、项目、商家、赏金、分红）
  - 智能体对话
  - 知识库管理

## 快速启动

### 首次部署

```bash
# 1. 启动后端服务
cd /workspace/projects/admin-backend
nohup python3 app.py > /tmp/flask_server.log 2>&1 &

# 2. 安装并配置 Nginx
apt-get update && apt-get install -y nginx
nginx

# 3. 验证服务
curl http://localhost/api/health
curl http://localhost/api/merchants
curl http://localhost/api/projects
```

### 使用脚本启动

```bash
# 启动所有服务
./scripts/start-services.sh

# 紧急修复（解决 502 错误）
./scripts/quick-fix.sh
```

## 常见问题

### 1. 502 Bad Gateway

**原因**: 后端服务未运行或 Nginx 配置错误

**解决方案**:
```bash
# 运行紧急修复脚本
./scripts/quick-fix.sh

# 或手动检查
ps aux | grep "python3 app.py"
netstat -tlnp | grep :8080
tail -f /tmp/flask_server.log
```

### 2. 前端页面 404

**原因**: Nginx 静态文件路径配置错误

**解决方案**:
```bash
# 检查 Nginx 配置
cat /etc/nginx/sites-available/meiyueart.com | grep root

# 确保指向正确的目录
ls -la /workspace/projects/public/
```

### 3. API 请求失败

**原因**: 后端服务异常

**解决方案**:
```bash
# 查看后端日志
tail -f /tmp/flask_server.log

# 重启后端服务
pkill -f "python3 app.py"
cd /workspace/projects/admin-backend
nohup python3 app.py > /tmp/flask_server.log 2>&1 &
```

## 服务管理

### 查看服务状态

```bash
# 查看 Nginx 进程
ps aux | grep nginx

# 查看 Flask 进程
ps aux | grep "python3 app.py"

# 查看端口监听
netstat -tlnp | grep -E ":(80|8080) "
```

### 重启服务

```bash
# 重启 Nginx
nginx -s reload

# 重启 Flask
pkill -f "python3 app.py"
cd /workspace/projects/admin-backend
nohup python3 app.py > /tmp/flask_server.log 2>&1 &
```

### 停止服务

```bash
# 停止 Nginx
nginx -s stop

# 停止 Flask
pkill -f "python3 app.py"
```

## 日志位置

| 服务 | 日志位置 |
|------|---------|
| Flask | `/tmp/flask_server.log` |
| Nginx 访问日志 | `/var/log/nginx/access.log` |
| Nginx 错误日志 | `/var/log/nginx/error.log` |

## API 端点

### 健康检查
```
GET /api/health
```

### 认证
```
POST /api/register
POST /api/login
POST /api/logout
GET /api/user/profile
```

### 资源池
```
GET /api/merchants        # 商家列表
GET /api/projects         # 项目列表
GET /api/bounties         # 赏金列表
GET /api/dividend-pool    # 分红池
```

### 智能体
```
POST /api/chat            # 智能体对话
GET /api/agents           # 智能体列表
```

## 数据库操作

```bash
# 连接数据库
cd /workspace/projects/admin-backend
python3 -c "
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()
# 执行 SQL 查询
cursor.execute('SELECT * FROM users LIMIT 5')
print(cursor.fetchall())
conn.close()
"
```

## 性能优化

### Nginx 缓存配置

```nginx
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg)$ {
    expires 7d;
    add_header Cache-Control "public, immutable";
}
```

### 后端优化

- 使用数据库连接池
- 启用响应压缩
- 实现请求限流

## 安全建议

1. **启用 HTTPS**: 使用 Let's Encrypt 证书
2. **防火墙配置**: 只开放必要端口
3. **定期备份**: 备份数据库和配置文件
4. **日志监控**: 监控异常访问和错误
5. **更新依赖**: 定期更新 Python 和 Nginx

## 监控脚本

创建监控脚本定期检查服务健康状态：

```bash
#!/bin/bash
# scripts/monitor.sh

check_service() {
    if curl -s -m 5 http://localhost/api/health > /dev/null; then
        echo "✅ 服务正常"
    else
        echo "❌ 服务异常，重启中..."
        ./scripts/quick-fix.sh
    fi
}

check_service
```

## 联系支持

如遇到问题，请提供以下信息：
1. 错误日志（`/tmp/flask_server.log`）
2. Nginx 日志（`/var/log/nginx/error.log`）
3. 服务状态（`ps aux | grep -E "(nginx|python)"`）
4. 端口监听（`netstat -tlnp | grep -E ":(80|8080)"`）
