# 灵值生态园 - 关键信息速查表

## 🎯 项目核心信息

| 项目 | 值 |
|------|-----|
| 项目名称 | 灵值生态园智能体系统 |
| 公司名称 | 陕西媄月商业艺术有限责任公司 |
| 公网IP | 123.56.142.143 |
| 前端端口 | 80/443 |
| 后端端口 | 8001 |
| 智能体模型 | DeepSeek-V3-2 |
| JWT有效期 | 7天 |
| 默认管理员 | admin / admin123 |

---

## 📂 关键路径速查

| 用途 | 路径 |
|------|------|
| 前端代码 | `web-app/` |
| 后端代码 | `admin-backend/` |
| 前端构建输出 | `public/` (注意：不是dist!) |
| 数据库 | `admin-backend/lingzhi_ecosystem.db` |
| 配置文件 | `config/agent_llm_config.json` |
| 后端日志 | `logs/app_backend.log` 或 `/app/work/logs/bypass/app.log` |
| 数据库备份 | `admin-backend/backups/` |
| 文档 | `docs/` |

---

## 🔑 关键配置

### 前端构建配置
```typescript
// web-app/vite.config.ts
outDir: '../public'  // 重要！
```

### API地址检测
```typescript
// web-app/src/services/api.ts
// 自动检测，支持3种方式：
1. 环境变量 VITE_API_BASE_URL
2. localStorage.getItem('apiBaseURL')
3. 智能检测（自动添加:8001端口）
```

### 数据库连接
```python
# admin-backend/app.py
DATABASE = 'lingzhi_ecosystem.db'
conn.row_factory = sqlite3.Row  # 返回Row对象
```

---

## 🔌 核心API接口

### 认证
```
POST /api/login          # 登录（支持手机验证码）
POST /api/register       # 注册
POST /api/send-code      # 发送验证码
GET  /api/user/info      # 获取用户信息
PUT  /api/user/profile   # 更新资料
GET  /api/user/security/settings # 安全设置
GET  /api/user/devices    # 设备列表
```

### 智能体
```
POST /api/agent/chat                           # 发送消息
GET  /api/agent/conversations/:id              # 对话历史
```

### 签到
```
POST /api/checkin          # 签到
GET  /api/checkin/history  # 历史
GET  /api/checkin/status   # 今日状态
```

### 合伙人
```
POST /api/partner/check-qualification  # 检查资格
POST /api/partner/apply                # 申请
GET  /api/partner/status/:userId       # 状态
```

### 充值
```
GET  /api/recharge/tiers      # 档位
POST /api/recharge/create     # 创建订单
GET  /api/recharge/company-accounts  # 公司账户
```

---

## 🗄️ 核心数据表

| 表名 | 主要字段 | 说明 |
|------|---------|------|
| users | id, username, email, phone, total_lingzhi | 用户表 |
| checkin_records | user_id, checkin_date, lingzhi_earned | 签到记录 |
| partner_applications | user_id, current_lingzhi, status | 合伙人申请 |
| recharge_tiers | name, price, base_lingzhi, bonus_lingzhi | 充值档位 |
| recharge_records | user_id, amount, payment_status | 充值记录 |
| user_devices | user_id, device_id, is_current | 设备管理 |
| login_sessions | user_id, token, device_id, expires_at | 登录会话 |
| agents | id, name, system_prompt, model_config | 智能体 |
| conversations | id, user_id, conversation_id, messages | 对话记录 |
| system_notifications | id, title, content, target_user_id | 系统通知 |

---

## ⚠️ 重要陷阱和注意事项

### 1. 前端构建输出 ⚠️⚠️⚠️
**陷阱：** 误以为输出在 `dist` 目录
**真相：** 输出在 `public` 目录
```typescript
// vite.config.ts
outDir: '../public'  // 不是dist!
```

### 2. 用户数据格式化 ⚠️⚠️
**陷阱：** 手动构造返回数据导致字段不一致
**真相：** 必须使用 `format_user_data()`
```python
# ✅ 正确
return jsonify({'success': True, 'data': format_user_data(user)})

# ❌ 错误
return jsonify({'success': True, 'data': dict(user)})
```

### 3. API地址配置 ⚠️
**陷阱：** 公网访问时API请求失败
**真相：** 使用智能检测，自动修正端口
```typescript
// 访问 http://YOUR_DOMAIN
// 自动使用 http://YOUR_DOMAIN:8001 作为API地址
```

### 4. 密码验证 ⚠️
**陷阱：** 只支持一种加密方式
**真相：** 支持SHA256和bcrypt双密码兼容
```python
def verify_password(password, password_hash):
    # 先尝试bcrypt，再尝试SHA256
```

### 5. Row对象访问 ⚠️
**陷阱：** 使用 `.get()` 方法访问Row对象
**真相：** Row对象不支持 `.get()`，使用字典语法或 `in` 检查
```python
# ❌ 错误
value = user.get('field', default)

# ✅ 正确
value = user['field'] if 'field' in user.keys() else default
```

### 6. 数据库迁移 ⚠️
**陷阱：** 重复添加字段报错
**真相：** 使用try-except包裹
```python
try:
    cursor.execute("ALTER TABLE users ADD COLUMN new_field TEXT")
except:
    pass  # 字段已存在
```

### 7. JWT过期 ⚠️
**陷阱：** Token过期后无法访问
**真相：** 前端自动处理401，跳转登录
```typescript
// 响应拦截器
if (error.response?.status === 401) {
  localStorage.removeItem('token')
  window.location.href = '/login'
}
```

### 8. 单点登录 ⚠️
**陷阱：** 多设备同时登录
**真相：** 新登录会使旧会话失效（默认启用）

---

## 🚀 常用命令

### 开发
```bash
cd web-app && npm run dev          # 前端开发服务器
cd admin-backend && python app.py  # 后端服务
```

### 构建
```bash
cd web-app && npm run build        # 构建前端
```

### 部署
```bash
./auto-deploy.sh deploy           # 自动部署
./setup-public-access.sh          # 公网配置
./test-public-access.sh           # 测试验证
```

### 日志
```bash
tail -f logs/app_backend.log      # 实时日志
tail -n 50 logs/app_backend.log    # 最后50行
```

### 数据库
```bash
sqlite3 admin-backend/lingzhi_ecosystem.db
```

---

## 🐛 问题诊断流程

### 问题：登录失败

1. 检查后端是否运行
   ```bash
   curl http://localhost:8001/api/health
   ```

2. 查看后端日志
   ```bash
   tail -f logs/app_backend.log
   ```

3. 检查密码加密方式
   ```bash
   # 数据库中查看password_hash
   # $2b$ 开头是bcrypt
   # 其他是SHA256
   ```

### 问题：修改资料不显示

1. 检查后端是否使用 `format_user_data()`
2. 检查前端是否使用后端返回的数据
3. 查看Network响应内容

### 问题：公网访问500错误

1. 检查前端API地址配置
2. 访问 `/api-config` 测试连接
3. 检查后端端口是否开放
4. 检查防火墙和安全组

### 问题：前端构建找不到文件

1. 检查输出目录是 `public`，不是 `dist`
2. 检查 `vite.config.ts` 中的 `outDir` 配置
3. 重新构建：`npm run build`

### 问题：旧用户无法登录

1. 检查数据库中 `password_hash` 格式
2. 确认 `verify_password()` 支持双密码
3. 测试登录，查看日志

---

## 📊 数据类型对照表

### 前端 vs 后端

| 前端类型 | 后端类型 | 说明 |
|---------|---------|------|
| User.id | INTEGER | 数字类型 |
| User.totalLingzhi | total_lingzhi (INTEGER) | 驼峰命名 |
| User.username | username (TEXT) | 文本类型 |
| User.email | email (TEXT) | 文本类型 |
| User.phone | phone (TEXT) | 文本类型 |

### 命名规范

| 类型 | 后端 | 前端 |
|------|------|------|
| 字段命名 | snake_case | camelCase |
| 日期 | TIMESTAMP | string (ISO格式) |
| 布尔值 | INTEGER (0/1) | boolean |

---

## 🔐 安全配置清单

- ✅ JWT Token认证（7天有效期）
- ✅ 双密码加密（SHA256 + bcrypt）
- ✅ CORS已配置
- ✅ 参数化查询（防SQL注入）
- ✅ 单点登录机制
- ✅ 设备管理
- ✅ 安全日志
- ✅ 手机验证码二次验证
- ✅ 定期数据库备份

---

## 📝 最近更新记录

### 2026-02-02
- ✅ 修复公网IP访问500错误
- ✅ 添加智能API地址检测
- ✅ 添加API配置页面
- ✅ 修复个人资料更新不显示
- ✅ 添加单点登录机制
- ✅ 添加设备管理功能
- ✅ 添加安全设置页面

---

## 📞 快速联系

### 问题报告
1. 查看后端日志：`logs/app_backend.log`
2. 查看浏览器控制台（F12）
3. 查看Network请求详情
4. 查看此速查表

### 文档参考
- `docs/CONTEXT_PANORAMA.md` - 完整上下文文档
- `docs/PUBLIC_DEPLOYMENT.md` - 公网部署指南
- `docs/QUICK_FIX_500_ERROR.md` - 快速修复指南

---

**最后更新：** 2026-02-02
**版本：** v2.0.0
