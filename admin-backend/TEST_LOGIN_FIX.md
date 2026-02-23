# 登录系统修复测试

## 测试目标
验证修复后的登录系统是否正常工作，包括：
1. 账号密码登录 (admin/123456)
2. 管理员登录 (admin/123456)
3. 微信登录接口

## 修复内容

### 1. 密码哈希函数统一
- 将 `hash_password()` 统一为使用bcrypt格式
- 保持向后兼容，支持验证旧格式的密码
- 优化 `verify_password()` 函数，优先验证bcrypt格式

### 2. admin账号密码统一
- 统一密码为 `admin/123456`
- admins表和users表都使用bcrypt哈希
- 启动时自动更新已存在的admin账号密码

### 3. 微信登录增强
- 增加详细的调试日志
- 优化错误处理
- 支持模拟模式和真实微信登录

## 测试用例

### 用例1: 正确的密码登录
```
POST /api/login
{
  "username": "admin",
  "password": "123456"
}

预期: 登录成功，返回token和用户信息
```

### 用例2: 错误的密码登录
```
POST /api/login
{
  "username": "admin",
  "password": "wrongpassword"
}

预期: 登录失败，返回401错误
```

### 用例3: 管理员登录
```
POST /api/admin/login
{
  "username": "admin",
  "password": "123456"
}

预期: 登录成功，返回token和管理员信息
```

### 用例4: 微信登录URL获取
```
GET /api/wechat/login

预期: 返回授权URL（模拟模式或真实模式）
```

## 预期结果
所有测试用例应该能够正常通过，无数据库锁定问题，无认证错误。
