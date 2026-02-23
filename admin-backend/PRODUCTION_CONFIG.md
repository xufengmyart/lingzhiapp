# 生产环境配置档案
# 版本: 1.0.0
# 创建日期: 2026-02-16
# 项目: 灵值生态园

## 服务器信息

### 基础信息
- 服务器类型: 阿里云ECS
- 域名: meiyueart.com
- IP地址: 待确认
- 操作系统: Linux (待确认)
- SSH端口: 22
- SSH用户: root

### SSH访问
- SSH配置文件: `/root/.ssh/config`
- 私钥路径: `/root/.ssh/id_rsa`
- 公钥路径: `/root/.ssh/id_rsa.pub`
- 连接命令: `ssh root@meiyueart.com`

## 环境配置

### 后端环境
- 框架: Flask
- Python版本: 3.x
- 端口: 8080
- 主机: 0.0.0.0
- 工作目录: `/app/meiyueart-backend`
- 日志路径: `/var/log/meiyueart-backend/app.log`

### 前端环境
- 框架: React
- 构建路径: `/workspace/projects/web-app/dist/`
- API地址: `https://meiyueart.com/api`
- 静态文件路径: `/app/public`

### 数据库
- 类型: SQLite
- 生产路径: `/app/meiyueart-backend/lingzhi_ecosystem.db`
- 本地路径: `/workspace/projects/admin-backend/lingzhi_ecosystem.db`
- 备份路径: `/app/meiyueart-backend/backups/`

## 用户账户

### 正式用户
| 用户名 | 用户ID | 密码 | 总灵值 | 状态 |
|--------|--------|------|--------|------|
| 马伟娟 | 19 | 123 | 0 | active |
| 许锋 | 1 | 123 | 0 | active |
| 许蓝月 | 1026 | 123 | 0 | active |
| 黄爱莉 | 1027 | 123 | 0 | active |
| 许韩玲 | 1028 | 123 | 0 | active |
| 许芳侠 | 1029 | 123 | 0 | active |
| 许武勤 | 1030 | 123 | 0 | active |
| 弓俊芳 | 1031 | 123 | 0 | active |
| 许明芳 | 1032 | 123 | 0 | active |
| 许秀芳 | 1033 | 123 | 0 | active |

### 管理员账户
- 用户名: admin
- 密码: 123456
- 用户ID: 待确认

## 环境变量

### 生产环境变量
```bash
DATABASE_PATH=/app/meiyueart-backend/lingzhi_ecosystem.db
HOST=0.0.0.0
PORT=8080
DEBUG=false
JWT_SECRET_KEY=meiyueart-production-secret-2026
JWT_EXPIRATION=86400
LOG_LEVEL=INFO
LOG_FILE=/var/log/meiyueart-backend/app.log
BCRYPT_ROUNDS=12
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_TIME=300
API_VERSION=v1
```

## 部署流程

### 自动化部署脚本
- 脚本路径: `/workspace/projects/admin-backend/auto_deploy.sh`
- 执行命令: `bash auto_deploy.sh`

### 部署步骤
1. 检查本地环境
2. 检查SSH连接
3. 备份生产数据库
4. 同步数据库到生产环境
5. 重启生产服务
6. 验证部署结果

### 验证清单
- [ ] 服务启动成功
- [ ] 用户ID=19可以登录
- [ ] 总灵值显示正常
- [ ] 所有API接口正常
- [ ] 前端页面正常加载

## 服务管理

### 启动服务
```bash
cd /app/meiyueart-backend
python app.py > /var/log/meiyueart-backend/app.log 2>&1 &
```

### 停止服务
```bash
pkill -f app.py
```

### 重启服务
```bash
pkill -f app.py
sleep 3
cd /app/meiyueart-backend
python app.py > /var/log/meiyueart-backend/app.log 2>&1 &
```

### 查看日志
```bash
tail -f /var/log/meiyueart-backend/app.log
```

### 检查服务状态
```bash
curl http://localhost:8080/api/health
```

## 数据库管理

### 备份数据库
```bash
cp /app/meiyueart-backend/lingzhi_ecosystem.db \
   /app/meiyueart-backend/backups/lingzhi_ecosystem_backup_$(date +%Y%m%d_%H%M%S).db
```

### 恢复数据库
```bash
cp /app/meiyueart-backend/backups/lingzhi_ecosystem_backup_YYYYMMDD_HHMMSS.db \
   /app/meiyueart-backend/lingzhi_ecosystem.db
```

### 同步数据库（本地到生产）
```bash
scp /workspace/projects/admin-backend/lingzhi_ecosystem.db \
    root@meiyueart.com:/app/meiyueart-backend/lingzhi_ecosystem.db
```

## 监控和告警

### 健康检查
- API: `http://meiyueart.com/api/health`
- 预期响应: `{"status":"ok"}`

### 日志监控
- 应用日志: `/var/log/meiyueart-backend/app.log`
- 错误日志: `grep -i error /var/log/meiyueart-backend/app.log`
- 访问日志: `grep -i POST /api/login /var/log/meiyueart-backend/app.log`

### 性能监控
- CPU: `top`
- 内存: `free -m`
- 磁盘: `df -h`
- 网络: `netstat -tlnp`

## 故障排查

### 服务无法启动
1. 检查日志: `tail -n 50 /var/log/meiyueart-backend/app.log`
2. 检查端口: `netstat -tlnp | grep 8080`
3. 检查进程: `ps aux | grep app.py`
4. 检查权限: `ls -l /app/meiyueart-backend/`

### 数据库错误
1. 检查数据库文件: `ls -l /app/meiyueart-backend/lingzhi_ecosystem.db`
2. 检查数据库权限: `chmod 644 /app/meiyueart-backend/lingzhi_ecosystem.db`
3. 检查数据库完整性: `sqlite3 /app/meiyueart-backend/lingzhi_ecosystem.db "PRAGMA integrity_check;"`

### 用户无法登录
1. 检查用户ID=19是否存在: `sqlite3 /app/meiyueart-backend/lingzhi_ecosystem.db "SELECT * FROM users WHERE id = 19;"`
2. 检查密码hash: `sqlite3 /app/meiyueart-backend/lingzhi_ecosystem.db "SELECT password_hash FROM users WHERE id = 19;"`
3. 重置密码: 参考 `clean_sync.py` 脚本

## 安全配置

### 防火墙规则
```bash
# 开放HTTP端口
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# 开放HTTPS端口
iptables -A INPUT -p tcp --dport 443 -j ACCEPT

# 开放应用端口
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# 保存规则
service iptables save
```

### SSL/TLS配置
- 证书路径: `/etc/nginx/ssl/`
- 配置文件: `/etc/nginx/nginx.conf`
- 自动续期: Let's Encrypt Certbot

## CI/CD配置

### Git仓库
- 仓库地址: 待配置
- 分支策略: master/main
- 触发条件: push到master分支

### 部署流程
1. 代码提交
2. 自动测试
3. 构建前端
4. 同步数据库
5. 重启服务
6. 验证部署

## 维护计划

### 日常维护
- 每日备份数据库
- 每周检查日志
- 每月更新依赖包
- 每季度安全审计

### 紧急响应
- 7x24小时监控
- 故障响应时间: < 15分钟
- 故障解决时间: < 2小时

## 联系信息

### 开发团队
- 负责人: 待确认
- 联系方式: 待确认

### 运维团队
- 负责人: 待确认
- 联系方式: 待确认

## 更新历史

### 2026-02-16
- 创建生产环境配置档案
- 标准化部署流程
- 创建自动化部署脚本
- 配置SSH访问

---

**注意**: 本档案包含敏感信息，请妥善保管，不要泄露给未授权人员。
