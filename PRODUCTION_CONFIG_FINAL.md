# 灵值生态园 - 生产环境配置文档（最终版）

## 服务器信息
- **服务器地址**: meiyueart.com
- **IP地址**: 123.56.142.143
- **SSH用户**: root
- **SSH密码**: Meiyue@root123
- **SSH端口**: 22

## 后端服务配置
- **后端路径**: /app/meiyueart-backend
- **启动文件**: app.py
- **运行方式**: python3 app.py
- **运行端口**: 5000 (默认)
- **虚拟环境**: /app/meiyueart-backend/venv
- **日志文件**: /var/log/meiyueart-backend/app.log

## 数据库配置
- **数据库类型**: SQLite
- **数据库文件**: /app/meiyueart-backend/lingzhi_ecosystem.db
- **密码加密方式**: Werkzeug scrypt (scrypt:32768:8:1)

## Nginx配置
- **配置文件**: /etc/nginx/sites-available/meiyueart-https.conf
- **代理端口**: 5000
- **API路径**: /api

## 测试账号
| 用户名 | 密码 | ID | 用途 |
|--------|------|----|----|
| admin | 123456 | 10 | 管理员账号 |
| 马伟娟 | 123 | 19 | 普通用户 |
| 许锋 | 123 | 1 | 普通用户 |

## 部署流程
1. 清理云服务器垃圾
2. 备份生产环境
3. 上传后端代码
4. 同步数据库
5. 更新Nginx配置并重启后端服务
6. 验证部署

## 一键部署脚本
```bash
./deploy_one_click.sh
```

## 常用命令

### 查看后端服务状态
```bash
ssh root@meiyueart.com "ps aux | grep 'python.*app.py' | grep -v grep"
```

### 查看后端日志
```bash
ssh root@meiyueart.com "tail -f /var/log/meiyueart-backend/app.log"
```

### 重启后端服务
```bash
ssh root@meiyueart.com "cd /app/meiyueart-backend && pkill -9 -f 'python.*app.py' && sleep 2 && source venv/bin/activate && nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &"
```

### 测试登录
```bash
# 测试管理员登录
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 测试用户登录
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"马伟娟","password":"123"}'
```

## 注意事项
1. Flask应用默认运行在5000端口
2. Nginx配置需要指向5000端口
3. 密码使用scrypt加密格式
4. 所有数据库操作通过SQLite完成
5. 后端服务使用Flask开发服务器（生产环境建议使用gunicorn）

## 备份位置
- **备份目录**: /var/www/backups
- **备份命名**: backend_backup_YYYYMMDD_HHMMSS.tar.gz

## 更新日志
- 2026-02-18: 修复密码验证逻辑，支持scrypt格式
- 2026-02-18: 修正Nginx代理配置，使用5000端口
- 2026-02-18: 重置用户数据，确保所有测试账号可用
