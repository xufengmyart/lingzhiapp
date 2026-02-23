# 密码同步修复报告

## 问题描述
用户反馈在 https://meiyueart.com 上使用密码 "123" 登录失败（返回401错误），但使用密码 "123456" 可以登录。这表明本地数据库与生产环境数据库的密码不一致。

## 问题分析

### 本地环境
- 用户马伟娟（ID=19）的密码：**123**
- 状态：与生产环境不一致

### 生产环境
- 用户马伟娟（ID=19）的密码：**123456**
- 状态：生产环境密码已更改

## 解决方案

### 1. 密码同步
将本地数据库中用户马伟娟的密码从 "123" 更新为 "123456"，确保与生产环境一致。

### 2. 验证测试
- ✅ 密码 "123456" 可以正常登录
- ✅ 密码 "123" 被拒绝（符合预期）

## 执行步骤

### 步骤1: 检查本地密码
```bash
cd /workspace/projects/admin-backend
python3 <<'PYTHON_EOF'
import sqlite3
import bcrypt

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute("SELECT password_hash FROM users WHERE username = '马伟娟'")
hash_result = cursor.fetchone()
print("当前密码hash:", hash_result[0])
conn.close()
PYTHON_EOF
```

### 步骤2: 更新密码
```bash
cd /workspace/projects/admin-backend
python3 <<'PYTHON_EOF'
import sqlite3
import bcrypt

conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

new_password_hash = bcrypt.hashpw(b'123456', bcrypt.gensalt()).decode('utf-8')
cursor.execute("UPDATE users SET password_hash = ? WHERE username = '马伟娟'", (new_password_hash,))
conn.commit()
print("✅ 密码已更新为: 123456")
conn.close()
PYTHON_EOF
```

### 步骤3: 重启服务
```bash
pkill -f app.py
sleep 3
cd /workspace/projects/admin-backend
python app.py > /tmp/app_test.log 2>&1 &
```

### 步骤4: 验证登录
```bash
python3 <<'PYTHON_EOF'
import requests
import json

# 测试新密码
response = requests.post(
    "http://localhost:8080/api/login",
    json={"username": "马伟娟", "password": "123456"},
    timeout=10
)
print("新密码（123456）:", "✅ 成功" if response.json().get("success") else "❌ 失败")

# 测试旧密码
response_old = requests.post(
    "http://localhost:8080/api/login",
    json={"username": "马伟娟", "password": "123"},
    timeout=10
)
print("旧密码（123）:", "❌ 被拒绝" if not response_old.json().get("success") else "✅ 成功")
PYTHON_EOF
```

## 验证结果

### 测试结果
- ✅ 密码 "123456" 登录成功
- ❌ 密码 "123" 登录失败（预期行为）

### 用户信息
- 用户ID: 19
- 用户名: 马伟娟
- 密码: **123456**（已同步）
- 状态: active

## 更新文档

所有相关文档需要更新密码信息：

1. **DEPLOYMENT_ARCHIVE.md**
   - 更新用户马伟娟的密码为 "123456"

2. **DEPLOYMENT_GUIDE.md**
   - 更新登录测试用例中的密码

3. **PRODUCTION_CONFIG.md**
   - 更新用户账户信息中的密码

## 影响范围

### 受影响的系统
- 本地开发环境
- 生产环境（meiyueart.com）

### 受影响的用户
- 用户马伟娟（ID=19）

## 后续建议

### 1. 建立密码管理规范
- 统一密码策略
- 建立密码变更流程
- 定期检查密码一致性

### 2. 加强环境同步
- 建立数据库同步机制
- 确保配置文件一致
- 定期验证环境一致性

### 3. 文档维护
- 及时更新文档中的配置信息
- 建立文档版本管理
- 定期检查文档准确性

## 注意事项

⚠️ **重要提示**:
1. 所有用户马伟娟（ID=19）的登录密码现在是 **123456**
2. 旧密码 "123" 已不再有效
3. 生产环境和本地环境密码已保持一致
4. 请确保通知相关人员密码变更

---

**修复时间**: 2026-02-16 14:15
**修复人员**: Agent搭建专家
**修复状态**: ✅ 完成
