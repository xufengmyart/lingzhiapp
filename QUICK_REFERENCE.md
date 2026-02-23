# 快速参考卡片

**最后更新**: 2026年2月18日 23:30

---

## 🚀 快速命令

### 部署
```bash
cd /workspace/projects
./deploy_one_click.sh
```

### 测试管理员登录
```bash
curl -X POST https://meiyueart.com/api/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

### 测试用户登录
```bash
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"马伟娟","password":"123"}'
```

### 查看后端日志
```bash
tail -f /workspace/projects/admin-backend/backend.log
```

### 查看生产日志
```bash
ssh root@meiyueart.com "tail -f /var/log/meiyueart-backend/app.log"
```

### 查看数据库表
```bash
cd /workspace/projects/admin-backend && python3 -c "
import sqlite3
conn = sqlite3.connect('data/lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute(\"SELECT name FROM sqlite_master WHERE type='table' ORDER BY name\")
for table in cursor.fetchall():
    print(table[0])
conn.close()
"
```

### 重启生产后端服务
```bash
ssh root@meiyueart.com "cd /app/meiyueart-backend && pkill -9 -f 'python.*app.py' && sleep 2 && source venv/bin/activate && nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &"
```

---

## 🔑 测试账号

### 管理员
| 用户名 | 密码 | 用途 |
|--------|------|----|
| admin | admin123 | 管理员登录 |

### 用户
| 用户名 | 密码 | ID | 用途 |
|--------|------|----|----|
| 许锋 | 123 | 1 | 普通用户 |
| 马伟娟 | 123 | 19 | 普通用户 |
| admin | 123456 | 10 | 双重角色 |

---

## 📁 关键文件路径

### 后端
```
主入口: /workspace/projects/admin-backend/app.py
配置: /workspace/projects/admin-backend/config.py
数据库: /workspace/projects/admin-backend/data/lingzhi_ecosystem.db
日志: /workspace/projects/admin-backend/backend.log
环境变量: /workspace/projects/admin-backend/.env
路由目录: /workspace/projects/admin-backend/routes/
中间件: /workspace/projects/admin-backend/middleware/
```

### 前端
```
主入口: /workspace/projects/web-app/src/main.tsx
路由: /workspace/projects/web-app/src/App.tsx
对话页: /workspace/projects/web-app/src/pages/Chat.tsx
管理员登录: /workspace/projects/web-app/src/pages/AdminLogin.tsx
Context: /workspace/projects/web-app/src/contexts/
组件: /workspace/projects/web-app/src/components/
环境变量: /workspace/projects/web-app/.env.production
```

### 生产环境
```
后端路径: /app/meiyueart-backend
数据库: /app/meiyueart-backend/lingzhi_ecosystem.db
日志: /var/log/meiyueart-backend/app.log
前端: /var/www/meiyueart.com/
Nginx配置: /etc/nginx/sites-available/meiyueart-https.conf
备份: /var/www/backups/
```

---

## 🔌 核心API

### 认证
```
POST /api/login              # 用户登录
POST /api/register           # 用户注册
POST /api/admin/login        # 管理员登录
POST /api/reset-password     # 重置密码
```

### 智能体
```
POST /api/agent/chat         # 对话
GET  /api/agents             # 智能体列表
POST /api/feedback           # 提交反馈
```

### 用户
```
GET  /api/user/info          # 用户信息
PUT  /api/user/profile       # 更新资料
```

### 签到
```
POST /api/checkin            # 签到
GET  /api/checkin/status     # 签到状态
```

### 充值
```
GET  /api/recharge/tiers     # 充值档位
POST /api/recharge/create-order  # 创建订单
```

---

## 🗄️ 数据库核心表

```
users                 # 用户基本信息（22个字段）
user_profiles         # 用户详细资料（13个字段）
admins                # 管理员账户（5个字段）
conversations         # 对话历史（8个字段）
agents                # 智能体配置（11个字段）
feedback              # 用户反馈（10个字段）
checkin_records       # 签到记录（5个字段）
recharge_records      # 充值记录（17个字段）
recharge_tiers        # 充值档位（13个字段）
knowledge_bases       # 知识库（8个字段）
knowledge_documents   # 知识库文档（11个字段）
```

---

## 🔐 配置信息

### JWT配置
```python
JWT_SECRET_KEY = "gyXB-7pi2Lc3jXSdvK3_fUJNs0VS4hBP6L4ncBXLVE3iME8pkpPsA4KhppwQbK0_fX4"
JWT_EXPIRATION = 604800  # 7天
JWT_ALGORITHM = 'HS256'
```

### 密码加密
```python
# 统一使用bcrypt
import bcrypt
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
```

### 数据库连接
```python
import sqlite3
conn = sqlite3.connect('data/lingzhi_ecosystem.db')
conn.row_factory = sqlite3.Row
```

---

## 🎯 业务规则

### 灵值计费
- 每5分钟消耗1灵值
- helpful反馈: 10灵值
- not_helpful反馈: 5灵值
- suggestion反馈: 15灵值

### 对话系统
- 消息存储: JSON格式在conversations.messages字段
- 记忆窗口: 最近20轮对话
- 大模型: doubao-seed-1-6-251015

---

## 🚨 常见问题

### 端口问题
```
Nginx代理: 5000端口
Flask配置: 8080端口
解决: 统一使用5000端口
```

### API路径
```
错误: /api/agent/feedback
正确: /api/feedback
```

### 环境变量
```
前端: VITE_API_URL=/api
后端: DATABASE_PATH=./data/lingzhi_ecosystem.db
```

---

## 📊 系统状态

### 当前版本
- 前端: V9.24.0
- 后端: V9.24.0

### 部署状态
- 前端: ✅ 正常
- 后端: ✅ 正常
- 数据库: ✅ 正常

### 数据统计
- 用户: 7个
- 对话: 52条
- 签到: 4条
- 智能体: 2个

---

## 🔗 相关文档

- `PROJECT_PANORAMA.md` - 全景学习文档
- `README.md` - 项目说明
- `WORK_PRINCIPLES.md` - 工作原则
- `PRODUCTION_CONFIG_FINAL.md` - 生产配置
- `admin-backend/README.md` - 后端文档

---

**快速参考完成！**
