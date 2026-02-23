# 生产环境用户管理文档

## 用户列表

生产环境共有 **23个用户**。

### 默认密码信息

| 用户ID | 用户名 | 密码 | 手机号 | 邮箱 | 状态 | 总灵值 |
|--------|--------|------|--------|------|------|--------|
| 1 | 许锋 | 123 | - | xufeng@meiyueart.cn | active | 10 |
| 2 | CTO（待定） | 123 | - | cto@meiyue.com | active | 0 |
| 3 | CMO（待定） | 123 | - | cmo@meiyue.com | active | 0 |
| 4 | COO（待定） | 123 | - | coo@meiyue.com | active | 0 |
| 5 | CFO（待定） | 123 | - | cfo@meiyue.com | active | 0 |
| 6 | 测试用户A | 123 | 13800138001 | test_a@example.com | active | 0 |
| 7 | 测试用户B | 123 | 13800138002 | test_b_1769397229@example.com | active | 0 |
| 10 | admin | 123456 | - | admin@meiyueart.com | active | 40 |
| 19 | 马伟娟 | 123456 | 13800000019 | maweijuan_prod@example.com | active | 10 |
| 201 | 17372200593 | 123 | 13800138000 | test@example.com | active | 10 |
| 219 | wechat_user_003 | 123 | 13900139003 | wechat_test003@example.com | active | 0 |
| 220 | 微信用户98710 | 123 | 13900139999 | - | active | 0 |
| 1012 | user_4fb8b315 | 未知密码 | - | - | active | 0 |
| 1015 | test_checkin | 123456 | - | test_checkin@example.com | active | 10 |
| 1016 | test_checkin2 | 123456 | - | test_checkin2@example.com | active | 10 |
| 1026 | 许蓝月 | 123 | 13815011153 | 许蓝月@example.com | active | 0 |
| 1027 | 黄爱莉 | 123 | 13857659801 | 黄爱莉@example.com | active | 0 |
| 1028 | 许韩玲 | 123 | 13890510313 | 许韩玲@example.com | active | 0 |
| 1029 | 许芳侠 | 123 | 13864217476 | 许芳侠@example.com | active | 0 |
| 1030 | 许武勤 | 123 | 13848525154 | 许武勤@example.com | active | 0 |
| 1031 | 弓俊芳 | 123 | 13857024618 | 弓俊芳@example.com | active | 0 |
| 1032 | 许明芳 | 123 | 13863921784 | 许明芳@example.com | active | 0 |
| 1033 | 许秀芳 | 123 | 13830749161 | 许秀芳@example.com | active | 0 |

## 密码规则

### 默认密码分类

1. **管理员账号**: `123456`
   - 用户ID: 10
   - 用户名: admin

2. **测试账号**: `123456`
   - 用户ID: 1015 (test_checkin)
   - 用户ID: 1016 (test_checkin2)
   - 用户ID: 19 (马伟娟)

3. **其他大部分用户**: `123`

### 安全建议

⚠️ **重要提醒**：
- 所有密码已使用 bcrypt 加密存储
- 建议用户首次登录后立即修改密码
- 不要在生产环境中使用简单密码（如 123、123456）
- 定期提醒用户更换密码

## 登录方式

### 使用用户名登录
```
用户名: admin
密码: 123456
```

### 使用手机号登录
```
手机号: 13800000019
密码: 123456
```

## 常见操作

### 重置用户密码

```bash
cd /workspace/projects/admin-backend

# 使用 Python 脚本重置
python3 -c "
import sqlite3
import bcrypt

user_id = 19  # 用户ID
new_password = '123456'  # 新密码

# 生成密码哈希
password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())

# 更新数据库
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash.decode('utf-8'), user_id))
conn.commit()
conn.close()

print(f'用户 {user_id} 密码已重置为: {new_password}')
"
```

### 查询用户信息

```bash
cd /workspace/projects/admin-backend

python3 -c "
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# 查询指定用户
user_id = 19
cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
user = cursor.fetchone()
print(dict(user))

conn.close()
"
```

### 查看所有用户统计

```bash
cd /workspace/projects/admin-backend

python3 -c "
import sqlite3
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()

# 用户总数
cursor.execute('SELECT COUNT(*) FROM users')
total_users = cursor.fetchone()[0]

# 活跃用户数
cursor.execute('SELECT COUNT(*) FROM users WHERE status = \"active\"')
active_users = cursor.fetchone()[0]

# 总灵值
cursor.execute('SELECT SUM(total_lingzhi) FROM users')
total_lingzhi = cursor.fetchone()[0] or 0

print(f'用户总数: {total_users}')
print(f'活跃用户: {active_users}')
print(f'总灵值: {total_lingzhi}')

conn.close()
"
```

## 用户分类

### 管理员
- **admin** (ID: 10) - 系统管理员

### 核心团队成员
- **许锋** (ID: 1) - 创始人
- **CTO/CMO/COO/CFO** (ID: 2-5) - 待定岗位

### 测试用户
- **测试用户A** (ID: 6)
- **测试用户B** (ID: 7)
- **test_checkin** (ID: 1015)
- **test_checkin2** (ID: 1016)

### 普通用户
- **马伟娟** (ID: 19)
- **许蓝月** (ID: 1026)
- **黄爱莉** (ID: 1027)
- **许韩玲** (ID: 1028)
- **许芳侠** (ID: 1029)
- **许武勤** (ID: 1030)
- **弓俊芳** (ID: 1031)
- **许明芳** (ID: 1032)
- **许秀芳** (ID: 1033)

### 微信用户
- **wechat_user_003** (ID: 219)
- **微信用户98710** (ID: 220)
- **17372200593** (ID: 201)

### 其他
- **user_4fb8b315** (ID: 1012) - 密码未知

## 数据备份

### 备份数据库
```bash
cd /workspace/projects/admin-backend

# 备份到 backups 目录
cp lingzhi_ecosystem.db backups/lingzhi_ecosystem_backup_$(date +%Y%m%d_%H%M%S).db

# 查看备份列表
ls -lh backups/
```

### 恢复数据库
```bash
cd /workspace/projects/admin-backend

# 停止服务
pkill -9 -f "python.*app.py"

# 恢复备份
cp backups/lingzhi_ecosystem_backup_YYYYMMDD_HHMMSS.db lingzhi_ecosystem.db

# 重启服务
python3 app.py &
```

## 安全建议

1. **定期备份**: 每天备份一次数据库
2. **密码策略**: 强制用户使用复杂密码
3. **权限管理**: 限制管理员账号数量
4. **日志监控**: 监控异常登录行为
5. **定期审计**: 定期检查用户列表和权限

## 联系方式

如有问题，请联系：
- 技术支持: admin@meiyueart.com
- 系统管理员: admin

---

**最后更新**: 2026-02-16
**版本**: 1.0
