# 数据库使用规范

## 📊 数据库概述

**项目名称**: 灵值生态园智能体系统
**数据库类型**: SQLite
**数据库文件**: `/workspace/projects/admin-backend/lingzhi_ecosystem.db`
**当前版本**: v9.11.0
**最后更新**: 2025-02-07

---

## 🚨 核心规则

### 1. 数据库文件规范

#### 唯一数据源
- ✅ **强制规则**: 生产环境和测试环境统一使用 `/workspace/projects/admin-backend/lingzhi_ecosystem.db`
- ❌ **禁止行为**: 创建任何其他数据库副本（如 `database.db`、`lingzhi.db`、`test.db` 等）
- ⚠️ **后果**: 数据混乱、数据不一致、生产环境数据污染

#### 数据备份
- ✅ **备份策略**: 使用自动化备份脚本定期备份
- ✅ **备份路径**: `/workspace/projects/backups/`
- ✅ **备份频率**: 每日备份 + 重大操作前备份

### 2. 用户数据规范

#### 有效用户命名规则
- ✅ **允许格式**: 
  - 常规用户名（字母开头，可包含字母、数字、下划线）
  - 长度: 3-20 个字符
  - 示例: `user123`、`alice_2024`、`zhangsan`
- ❌ **禁止格式**:
  - `test_auto_*`（自动测试用户）
  - `db_test_*`（数据库测试用户）
  - 以 `test_`、`__test__`、`_test` 开头的用户名
  - 包含特殊字符（如 `@#¥%...`）的用户名

#### 数据清理规则
- ✅ **清理时机**: 每次生产环境更新后
- ✅ **清理方式**: 使用 `cleanup_test_data()` 函数
- ✅ **验证机制**: 清理后必须执行数据一致性验证

### 3. 数据一致性规范

#### 核心一致性规则
```
用户总灵值 = 签到灵值 + 充值灵值
```

#### 验证时机
- ✅ **必验证**: 
  - 执行数据清理后
  - 执行数据修复后
  - 发布新版本前
  - 发现数据异常时
- ✅ **验证工具**: 使用 `verify_data_consistency()` 函数

#### 修复机制
- ✅ **修复时机**: 发现数据不一致时
- ✅ **修复方式**: 使用 `fix_production_lingzhi()` 函数
- ✅ **验证要求**: 修复后必须再次验证一致性

---

## 📋 数据库维护流程

### 日常维护

#### 每日检查
```python
# 1. 检查数据库文件大小
import os
db_path = "/workspace/projects/admin-backend/lingzhi_ecosystem.db"
size = os.path.getsize(db_path)
print(f"数据库大小: {size / 1024:.2f} KB")

# 2. 检查数据一致性
from verify_lingzhi_fix import verify_data_consistency
verify_data_consistency()

# 3. 检查用户数量
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"用户数量: {user_count}")
```

#### 每周优化
```sql
-- 1. 执行数据库优化
VACUUM;

-- 2. 分析查询性能
EXPLAIN QUERY PLAN SELECT * FROM users WHERE id = ?;

-- 3. 检查索引使用情况
PRAGMA index_info(index_name);
```

### 数据清理流程

#### 清理测试数据
```python
from cleanup_test_data import cleanup_test_data, verify_data_consistency

# 1. 备份数据库
backup_database()

# 2. 清理测试数据
cleanup_test_data()

# 3. 验证数据一致性
verify_data_consistency()

# 4. 验证清理结果
conn = sqlite3.connect("/workspace/projects/admin-backend/lingzhi_ecosystem.db")
cursor = conn.cursor()
cursor.execute("SELECT COUNT(*) FROM users WHERE username LIKE 'test_%'")
test_users = cursor.fetchone()[0]
print(f"剩余测试用户: {test_users}")
assert test_users == 0, "清理失败：仍有测试用户存在"
```

---

## 🔧 数据库操作指南

### 连接数据库
```python
import sqlite3

# 正确方式
db_path = "/workspace/projects/admin-backend/lingzhi_ecosystem.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 错误方式（❌ 禁止）
conn = sqlite3.connect("database.db")  # 文件名不规范
conn = sqlite3.connect("./lingzhi.db")  # 路径不规范
```

### 执行查询
```python
# 查询用户信息
cursor.execute("SELECT id, username, total_lingzhi FROM users")
users = cursor.fetchall()

# 使用参数化查询（防止SQL注入）
user_id = 123
cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
user = cursor.fetchone()
```

### 更新数据
```python
# 更新用户灵值
cursor.execute("""
    UPDATE users 
    SET total_lingzhi = ? 
    WHERE id = ?
""", (new_lingzhi, user_id))

# 提交事务
conn.commit()
```

### 事务管理
```python
try:
    # 开始事务
    cursor.execute("BEGIN TRANSACTION")
    
    # 执行多个操作
    cursor.execute("UPDATE users SET total_lingzhi = ? WHERE id = ?", (100, 1))
    cursor.execute("INSERT INTO checkin_records ...")
    
    # 提交事务
    conn.commit()
    
except Exception as e:
    # 回滚事务
    conn.rollback()
    print(f"操作失败，已回滚: {e}")
```

---

## 🚨 常见问题与解决方案

### 问题1: 数据库文件过大
**症状**: 数据库文件超过 10 MB
**解决方案**:
```sql
-- 执行数据库优化
VACUUM;

-- 分析表大小
SELECT name, page_count * page_size as size FROM sqlite_master;
```

### 问题2: 数据不一致
**症状**: 用户总灵值 ≠ 签到灵值 + 充值灵值
**解决方案**:
```python
from fix_production_lingzhi import fix_production_lingzhi, verify_data_consistency

# 1. 修复数据
fix_production_lingzhi()

# 2. 验证修复
verify_data_consistency()
```

### 问题3: 测试数据污染生产环境
**症状**: 数据库中存在大量测试用户（test_auto_*、db_test_*）
**解决方案**:
```python
from cleanup_test_data import cleanup_test_data

# 清理测试数据
cleanup_test_data()
```

### 问题4: 查询性能慢
**症状**: 查询响应时间超过 1 秒
**解决方案**:
```sql
-- 1. 检查查询计划
EXPLAIN QUERY PLAN SELECT * FROM users WHERE username = ?;

-- 2. 添加索引（如需要）
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- 3. 执行数据库优化
VACUUM;
```

---

## 📊 数据库表结构

### users 表
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    total_lingzhi INTEGER DEFAULT 0,
    checkin_lingzhi INTEGER DEFAULT 0,
    recharge_lingzhi INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### checkin_records 表
```sql
CREATE TABLE checkin_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    checkin_date DATE NOT NULL,
    lingzhi_reward INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### recharge_records 表
```sql
CREATE TABLE recharge_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    lingzhi INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
```

---

## 🎯 验收标准

### 数据质量标准
- ✅ **无测试数据**: 数据库中不存在 `test_auto_*`、`db_test_*` 等测试用户
- ✅ **数据一致性**: 所有用户的 `total_lingzhi = checkin_lingzhi + recharge_lingzhi`
- ✅ **数据库大小**: 生产环境数据库大小不超过 2 MB
- ✅ **索引完整**: 所有常用查询字段都有索引
- ✅ **备份完整**: 每日备份文件存在且可恢复

### 操作流程标准
- ✅ **清理流程**: 清理数据 → 验证一致性 → 验证清理结果
- ✅ **修复流程**: 修复数据 → 验证一致性 → 记录修复日志
- ✅ **部署流程**: 备份数据 → 部署代码 → 验证功能 → 验证数据
- ✅ **备份流程**: 定期备份 → 验证备份 → 存储备份

---

## 📝 联系与支持

**维护团队**: 灵值生态园开发团队
**最后更新**: 2025-02-07
**版本**: v1.0.0

**问题反馈**: 如遇到数据库相关问题，请联系开发团队。

---

**文档变更历史**:
- 2025-02-07: 创建数据库使用规范文档
- 2025-02-07: 添加数据清理流程和一致性验证
