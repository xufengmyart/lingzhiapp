# Flask 应用管理脚本说明

本目录包含 Flask 应用的管理脚本，用于实现自动启动、健康检查、监控告警等功能。

## 脚本列表

### 1. deploy.sh - 标准部署脚本
一键部署脚本，包含环境检查、依赖安装、服务启动、监控配置。

**用法:**
```bash
# 完整部署
./deploy.sh deploy

# 重新部署
./deploy.sh redeploy
```

**功能:**
- ✓ 环境检查（Python、pip、Nginx 等）
- ✓ 依赖安装（requirements.txt 或基础依赖）
- ✓ 创建日志目录
- ✓ 停止旧服务
- ✓ 启动新服务
- ✓ 安装监控定时任务
- ✓ 配置日志轮转
- ✓ 验证服务可用性

### 2. flask-start.sh - 服务启动脚本
服务的启动、停止、重启脚本。

**用法:**
```bash
# 启动服务
./flask-start.sh start

# 停止服务
./flask-start.sh stop

# 重启服务
./flask-start.sh restart

# 查看状态
./flask-start.sh status
```

**功能:**
- ✓ 智能停止旧进程
- ✓ 启动新进程
- ✓ 进程状态检查
- ✓ 健康检查
- ✓ PID 管理

### 3. health-check.sh - 健康检查脚本
定期检查服务状态，异常时自动重启。

**用法:**
```bash
# 执行健康检查（失败时自动重启）
./health-check.sh check

# 强制重启服务
./health-check.sh force-restart

# 检查服务状态
./health-check.sh status
```

**检查项:**
- ✓ 进程是否存在
- ✓ 端口是否监听
- ✓ 健康接口是否响应
- ✓ 登录接口是否正常

### 4. flask-monitor.sh - 监控脚本
定时执行健康检查，自动恢复故障。

**用法:**
```bash
# 执行一次监控检查
./flask-monitor.sh check

# 安装定时任务（每分钟执行一次）
./flask-monitor.sh install

# 卸载定时任务
./flask-monitor.sh uninstall
```

**监控内容:**
- ✓ 健康检查
- ✓ 磁盘空间检查
- ✓ 内存使用检查

## 快速开始

### 首次部署
```bash
cd /workspace/projects/admin-backend
./deploy.sh deploy
```

### 日常管理
```bash
# 查看服务状态
ps aux | grep gunicorn

# 查看日志
tail -f /var/log/flask/error.log

# 重启服务
./flask-start.sh restart

# 手动健康检查
./health-check.sh check
```

## 配置说明

### 环境变量
脚本中的关键配置：

| 变量 | 默认值 | 说明 |
|------|--------|------|
| APP_DIR | /workspace/projects/admin-backend | 应用目录 |
| FLASK_PORT | 8080 | 服务端口 |
| WORKERS | 4 | Worker 数量 |
| LOG_DIR | /var/log/flask | 日志目录 |

### 日志配置
日志轮转配置：`/etc/logrotate.d/flask-app`

```bash
/var/log/flask/*.log {
    daily              # 每天轮转
    rotate 7           # 保留 7 天
    compress           # 压缩旧日志
    delaycompress      # 延迟压缩
    missingok          # 文件不存在不报错
    notifempty         # 空文件不轮转
}
```

### 监控配置
定时任务通过 crontab 管理：

```bash
* * * * * /workspace/projects/admin-backend/flask-monitor.sh check >> /var/log/flask/monitor-cron.log 2>&1
```

## 故障排查

### 服务未启动
```bash
# 检查进程
ps aux | grep gunicorn

# 检查日志
tail -50 /var/log/flask/error.log

# 手动启动
./flask-start.sh start
```

### 健康检查失败
```bash
# 查看健康检查日志
tail -50 /var/log/flask/health-check.log

# 手动执行健康检查
./health-check.sh check -v
```

### 端口占用
```bash
# 检查端口
netstat -tuln | grep 8080

# 查看占用进程
lsof -i :8080

# 强制重启
./flask-start.sh restart
```

### 监控不工作
```bash
# 查看定时任务
crontab -l

# 查看监控日志
tail -50 /var/log/flask/monitor-cron.log

# 重新安装监控
./flask-monitor.sh uninstall
./flask-monitor.sh install
```

## 性能调优

### 增加 Worker 数量
编辑 `flask-start.sh`，修改 `WORKERS` 变量：

```bash
WORKERS=8  # 改为 8 个 worker
```

### 调整超时时间
编辑 `flask-start.sh`，修改 `--timeout` 参数：

```bash
--timeout 180  # 改为 180 秒
```

### 调整最大请求数
编辑 `flask-start.sh`，修改 `--max-requests` 参数：

```bash
--max-requests 5000  # 改为 5000 个请求
```

## 安全建议

1. **限制日志权限**
   ```bash
   chmod 640 /var/log/flask/*.log
   ```

2. **定期清理旧日志**
   ```bash
   find /var/log/flask -name "*.log.*" -mtime +30 -delete
   ```

3. **监控日志大小**
   ```bash
   du -sh /var/log/flask/*
   ```

## 监控告警

### 查看监控日志
```bash
tail -f /var/log/flask/monitor.log
```

### 设置邮件告警
编辑 `health-check.sh`，在重启服务后添加邮件通知：

```bash
# 重启服务后
echo "Flask 服务已自动重启" | mail -s "服务告警" admin@example.com
```

## 版本历史

- v1.0.0 (2026-02-12)
  - 初始版本
  - 实现自动启动、健康检查、监控告警
  - 配置日志轮转

## 技术支持

如有问题，请检查：
1. 日志文件：`/var/log/flask/error.log`
2. 健康检查日志：`/var/log/flask/health-check.log`
3. 监控日志：`/var/log/flask/monitor.log`

## 目录结构

```
/workspace/projects/admin-backend/
├── deploy.sh           # 标准部署脚本
├── flask-start.sh      # 服务启动脚本
├── health-check.sh     # 健康检查脚本
├── flask-monitor.sh    # 监控脚本
├── app.py             # Flask 应用主文件
├── requirements.txt    # Python 依赖
└── README.md          # 本文档
```

---

**文档版本**: 1.0.0
**最后更新**: 2026-02-12
