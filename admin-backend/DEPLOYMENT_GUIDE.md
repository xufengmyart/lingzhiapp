# 生产环境部署指南

## 概述

本指南详细说明了灵值生态园智能体系统的生产环境部署流程，包括数据库同步、服务管理、故障排查等关键步骤。

## 前置条件

### 1. 环境准备
- 本地开发环境已配置完成
- 数据库文件位于 `/workspace/projects/admin-backend/lingzhi_ecosystem.db`
- 用户ID=19（马伟娟）已创建，密码为 123

### 2. 依赖安装
```bash
cd /workspace/projects/admin-backend
pip install requests bcrypt
```

## 部署流程

### 方式一：自动化部署（推荐）

使用自动化部署脚本，一键完成部署：

```bash
cd /workspace/projects/admin-backend
python deploy_workflow.py
```

该脚本会自动执行以下步骤：
1. 检查本地环境（数据库、用户ID=19）
2. 同步数据库到生产环境
3. 验证生产环境部署结果

### 方式二：手动部署

如果自动化部署失败，可以按以下步骤手动部署：

#### 步骤1: 检查本地环境

```bash
# 检查数据库文件
ls -l /workspace/projects/admin-backend/lingzhi_ecosystem.db

# 检查用户ID=19
python3 <<EOF
import sqlite3
import bcrypt

conn = sqlite3.connect('/workspace/projects/admin-backend/lingzhi_ecosystem.db')
cursor = conn.cursor()

# 检查用户是否存在
cursor.execute("SELECT username FROM users WHERE id = 19")
user = cursor.fetchone()
if user:
    print(f"✅ 用户ID=19存在: {user[0]}")
else:
    print("❌ 用户ID=19不存在")

# 检查密码
cursor.execute("SELECT password_hash FROM users WHERE id = 19")
hash_result = cursor.fetchone()
if hash_result:
    if bcrypt.checkpw(b'123', hash_result[0].encode('utf-8')):
        print("✅ 密码正确")
    else:
        print("❌ 密码不正确")
else:
    print("❌ 用户不存在")

conn.close()
EOF
```

#### 步骤2: 同步数据库到生产环境

**方法A: 使用API同步**（如果无法SSH）

```bash
python3 <<EOF
import requests

PRODUCTION_API_URL = "https://meiyueart.com/api"

# 1. 管理员登录获取token
login_response = requests.post(
    f"{PRODUCTION_API_URL}/login",
    json={"username": "admin", "password": "123456"},
    timeout=10
)

if not login_response.json().get("success"):
    print("❌ 管理员登录失败")
    exit(1)

token = login_response.json().get("data", {}).get("token")
print("✅ 管理员登录成功")

# 2. 创建/更新用户ID=19
create_user_response = requests.post(
    f"{PRODUCTION_API_URL}/admin/user/create",
    json={
        "username": "马伟娟",
        "password": "123",
        "email": "maweijuan@example.com",
        "phone": "13800000019"
    },
    headers={"Authorization": f"Bearer {token}"},
    timeout=10
)

if create_user_response.json().get("success"):
    print("✅ 用户创建成功")
else:
    # 如果创建失败，尝试更新密码
    update_password_response = requests.post(
        f"{PRODUCTION_API_URL}/admin/user/reset-password",
        json={
            "username": "马伟娟",
            "new_password": "123"
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if update_password_response.json().get("success"):
        print("✅ 密码更新成功")
    else:
        print("❌ 密码更新失败")
        exit(1)

EOF
```

**方法B: 使用SSH同步**（如果有SSH权限）

```bash
# 备份生产数据库
ssh root@meiyueart.com "cp /app/meiyueart-backend/lingzhi_ecosystem.db /app/meiyueart-backend/backups/lingzhi_ecosystem_backup_$(date +%Y%m%d_%H%M%S).db"

# 同步数据库
scp /workspace/projects/admin-backend/lingzhi_ecosystem.db \
    root@meiyueart.com:/app/meiyueart-backend/lingzhi_ecosystem.db

# 重启服务
ssh root@meiyueart.com "pkill -f app.py && sleep 3 && cd /app/meiyueart-backend && nohup python app.py > /var/log/meiyueart-backend/app.log 2>&1 &"
```

#### 步骤3: 验证部署

```bash
python3 <<EOF
import requests

PRODUCTION_API_URL = "https://meiyueart.com/api"

# 1. 测试登录
login_response = requests.post(
    f"{PRODUCTION_API_URL}/login",
    json={"username": "马伟娟", "password": "123"},
    timeout=10
)

if not login_response.json().get("success"):
    print("❌ 登录失败")
    print(login_response.json())
    exit(1)

user_data = login_response.json().get("data", {}).get("user", {})

if user_data.get("id") != 19:
    print(f"❌ 用户ID错误（应为19，实际{user_data.get('id')}）")
    exit(1)

print(f"✅ 登录成功，用户ID={user_data.get('id')}, 用户名={user_data.get('username')}")

# 2. 验证总灵值显示
token = login_response.json().get("data", {}).get("token")
user_info_response = requests.get(
    f"{PRODUCTION_API_URL}/user/info",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10
)

if not user_info_response.json().get("success"):
    print("❌ 获取用户信息失败")
    print(user_info_response.json())
    exit(1)

user_info = user_info_response.json().get("data", {}).get("user", {})
total_lingzhi = user_info.get("total_lingzhi", 0)
print(f"✅ 总灵值={total_lingzhi}")

print("\n✅ 部署验证成功！")
print("验证步骤: 访问 https://meiyueart.com，使用用户名'马伟娟'和密码'123'登录，检查主页总灵值显示")

EOF
```

## 验证清单

部署完成后，请执行以下验证：

- [ ] 用户马伟娟（ID=19）可以登录
- [ ] 密码为 123
- [ ] 主页总灵值显示正常（不为0）
- [ ] 所有API接口返回正确
- [ ] 前端页面正常加载
- [ ] 没有错误日志

## 故障排查

### 问题1: 用户ID=19登录失败

**症状**: 使用用户名"马伟娟"和密码"123"登录，返回错误

**排查步骤**:
```bash
# 检查用户是否存在
python3 <<EOF
import sqlite3

conn = sqlite3.connect('/workspace/projects/admin-backend/lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM users WHERE id = 19")
user = cursor.fetchone()
if user:
    print(f"✅ 用户存在: {user[1]}")  # 第2列是username
else:
    print("❌ 用户不存在")
conn.close()
EOF

# 检查密码是否正确
python3 <<EOF
import sqlite3
import bcrypt

conn = sqlite3.connect('/workspace/projects/admin-backend/lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute("SELECT password_hash FROM users WHERE id = 19")
hash_result = cursor.fetchone()
if hash_result:
    if bcrypt.checkpw(b'123', hash_result[0].encode('utf-8')):
        print("✅ 密码正确")
    else:
        print("❌ 密码不正确")
else:
    print("❌ 用户不存在")
conn.close()
EOF
```

**解决方案**:
```bash
# 重置用户密码
python3 <<EOF
import sqlite3
import bcrypt

conn = sqlite3.connect('/workspace/projects/admin-backend/lingzhi_ecosystem.db')
cursor = conn.cursor()

# 生成密码hash
password_hash = bcrypt.hashpw(b'123', bcrypt.gensalt()).decode('utf-8')

# 更新密码
cursor.execute(
    "UPDATE users SET password_hash = ? WHERE id = 19",
    (password_hash,)
)

conn.commit()
conn.close()

print("✅ 密码已重置为 123")
EOF
```

### 问题2: 总灵值显示为0

**症状**: 用户登录后，主页总灵值显示为0

**排查步骤**:
```bash
# 检查数据库中总灵值
python3 <<EOF
import sqlite3

conn = sqlite3.connect('/workspace/projects/admin-backend/lingzhi_ecosystem.db')
cursor = conn.cursor()

# 检查用户表
cursor.execute("SELECT id, username, total_lingzhi FROM users WHERE id = 19")
user = cursor.fetchone()
if user:
    print(f"用户ID={user[0]}, 用户名={user[1]}, 总灵值={user[2]}")
else:
    print("用户不存在")

conn.close()
EOF

# 检查API响应
python3 <<EOF
import requests

PRODUCTION_API_URL = "https://meiyueart.com/api"

login_response = requests.post(
    f"{PRODUCTION_API_URL}/login",
    json={"username": "马伟娟", "password": "123"},
    timeout=10
)

if login_response.json().get("success"):
    token = login_response.json().get("data", {}).get("token")
    user_info_response = requests.get(
        f"{PRODUCTION_API_URL}/user/info",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if user_info_response.json().get("success"):
        user_info = user_info_response.json().get("data", {}).get("user", {})
        print(f"API返回总灵值={user_info.get('total_lingzhi', 0)}")
    else:
        print("❌ API返回错误")
        print(user_info_response.json())
else:
    print("❌ 登录失败")
    print(login_response.json())
EOF
```

**解决方案**:
- 如果数据库中总灵值为0，需要灵值交易或活动发放灵值
- 如果数据库中有灵值但API返回0，检查 `/api/user/info` 接口实现
- 如果API返回正确但前端显示0，检查前端代码

### 问题3: 数据库连接失败

**症状**: 服务启动后报错"database is locked"或"no such table"

**排查步骤**:
```bash
# 检查数据库文件权限
ls -l /workspace/projects/admin-backend/lingzhi_ecosystem.db

# 检查数据库是否被其他进程占用
lsof /workspace/projects/admin-backend/lingzhi_ecosystem.db

# 检查数据库完整性
sqlite3 /workspace/projects/admin-backend/lingzhi_ecosystem.db "PRAGMA integrity_check;"
```

**解决方案**:
```bash
# 停止所有占用数据库的进程
pkill -f app.py
sleep 3

# 修复数据库
sqlite3 /workspace/projects/admin-backend/lingzhi_ecosystem.db "PRAGMA integrity_check;"
sqlite3 /workspace/projects/admin-backend/lingzhi_ecosystem.db "VACUUM;"

# 重启服务
cd /workspace/projects/admin-backend
python app.py
```

### 问题4: API请求超时

**症状**: API请求响应缓慢或超时

**排查步骤**:
```bash
# 检查服务状态
curl -v https://meiyueart.com/api/health

# 检查网络连接
ping meiyueart.com

# 检查DNS解析
nslookup meiyueart.com
```

**解决方案**:
- 增加API请求超时时间（从10秒增加到30秒）
- 检查生产服务器负载（CPU、内存、网络）
- 优化数据库查询性能

## 监控和维护

### 日常监控

```bash
# 检查服务状态
curl https://meiyueart.com/api/health

# 检查错误日志
grep -i error /app/work/logs/bypass/app.log | tail -20

# 检查数据库大小
du -sh /workspace/projects/admin-backend/lingzhi_ecosystem.db
```

### 定期备份

```bash
# 每日自动备份
cat > /etc/cron.daily/backup_lingzhi.sh <<EOF
#!/bin/bash
BACKUP_DIR="/workspace/projects/admin-backend/backups"
DB_PATH="/workspace/projects/admin-backend/lingzhi_ecosystem.db"
TIMESTAMP=\$(date +%Y%m%d_%H%M%S)

mkdir -p \$BACKUP_DIR
cp \$DB_PATH \$BACKUP_DIR/lingzhi_ecosystem_backup_\$TIMESTAMP.db

# 保留最近7天的备份
find \$BACKUP_DIR -name "lingzhi_ecosystem_backup_*.db" -mtime +7 -delete

echo "数据库备份完成: \$BACKUP_DIR/lingzhi_ecosystem_backup_\$TIMESTAMP.db"
EOF

chmod +x /etc/cron.daily/backup_lingzhi.sh
```

## 附录

### A. 完整的部署命令

```bash
# 1. 检查本地环境
python3 <<EOF
import sqlite3
import bcrypt

conn = sqlite3.connect('/workspace/projects/admin-backend/lingzhi_ecosystem.db')
cursor = conn.cursor()

cursor.execute("SELECT username FROM users WHERE id = 19")
user = cursor.fetchone()

if not user:
    print("❌ 用户ID=19不存在")
    exit(1)

cursor.execute("SELECT password_hash FROM users WHERE id = 19")
hash_result = cursor.fetchone()

if not bcrypt.checkpw(b'123', hash_result[0].encode('utf-8')):
    print("❌ 密码不正确")
    exit(1)

print(f"✅ 本地环境检查通过: 用户={user[0]}")
conn.close()
EOF

# 2. 同步数据库到生产环境（使用API）
python3 <<EOF
import requests

PRODUCTION_API_URL = "https://meiyueart.com/api"

login_response = requests.post(
    f"{PRODUCTION_API_URL}/login",
    json={"username": "admin", "password": "123456"},
    timeout=10
)

if not login_response.json().get("success"):
    print("❌ 管理员登录失败")
    exit(1)

token = login_response.json().get("data", {}).get("token")
print("✅ 管理员登录成功")

create_user_response = requests.post(
    f"{PRODUCTION_API_URL}/admin/user/create",
    json={
        "username": "马伟娟",
        "password": "123",
        "email": "maweijuan@example.com",
        "phone": "13800000019"
    },
    headers={"Authorization": f"Bearer {token}"},
    timeout=10
)

if create_user_response.json().get("success"):
    print("✅ 用户创建成功")
else:
    update_password_response = requests.post(
        f"{PRODUCTION_API_URL}/admin/user/reset-password",
        json={
            "username": "马伟娟",
            "new_password": "123"
        },
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )

    if update_password_response.json().get("success"):
        print("✅ 密码更新成功")
    else:
        print("❌ 密码更新失败")
        exit(1)

print("✅ 数据库同步成功")
EOF

# 3. 验证部署
python3 <<EOF
import requests

PRODUCTION_API_URL = "https://meiyueart.com/api"

login_response = requests.post(
    f"{PRODUCTION_API_URL}/login",
    json={"username": "马伟娟", "password": "123"},
    timeout=10
)

if not login_response.json().get("success"):
    print("❌ 登录失败")
    exit(1)

user_data = login_response.json().get("data", {}).get("user", {})

if user_data.get("id") != 19:
    print(f"❌ 用户ID错误（应为19，实际{user_data.get('id')}）")
    exit(1)

print(f"✅ 登录成功，用户ID={user_data.get('id')}")

token = login_response.json().get("data", {}).get("token")
user_info_response = requests.get(
    f"{PRODUCTION_API_URL}/user/info",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10
)

if not user_info_response.json().get("success"):
    print("❌ 获取用户信息失败")
    exit(1)

user_info = user_info_response.json().get("data", {}).get("user", {})
total_lingzhi = user_info.get("total_lingzhi", 0)
print(f"✅ 总灵值={total_lingzhi}")

print("\n✅ 部署验证成功！")
print("访问 https://meiyueart.com，使用用户名'马伟娟'和密码'123'登录")
EOF
```

### B. 常用SQL查询

```sql
-- 查看所有用户
SELECT id, username, email, total_lingzhi, is_active FROM users;

-- 查看用户ID=19的详细信息
SELECT * FROM users WHERE id = 19;

-- 查看最近的交易记录
SELECT * FROM transactions ORDER BY created_at DESC LIMIT 10;

-- 统计总用户数
SELECT COUNT(*) FROM users;

-- 统计总灵值
SELECT SUM(total_lingzhi) FROM users;

-- 查看用户排名（按总灵值）
SELECT id, username, total_lingzhi FROM users ORDER BY total_lingzhi DESC LIMIT 10;
```

### C. API接口文档

#### 登录接口
```
POST /api/login
Content-Type: application/json

请求体:
{
  "username": "马伟娟",
  "password": "123"
}

响应:
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 19,
      "username": "马伟娟",
      "email": "maweijuan@example.com",
      "total_lingzhi": 0
    }
  }
}
```

#### 获取用户信息接口
```
GET /api/user/info
Authorization: Bearer {token}

响应:
{
  "success": true,
  "data": {
    "user": {
      "id": 19,
      "username": "马伟娟",
      "email": "maweijuan@example.com",
      "total_lingzhi": 0
    }
  }
}
```

## 联系支持

如果在部署过程中遇到问题，请联系：

- 技术支持邮箱: support@example.com
- 在线文档: https://docs.example.com
- 问题反馈: https://github.com/example/lingzhi-ecosystem/issues

---

**最后更新**: 2026-02-16
**版本**: 1.0.0
