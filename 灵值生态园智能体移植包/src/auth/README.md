# 媄月商业艺术 - 权限管理系统

**版本**：v1.0
**发布日期**：2026年1月23日
**开发语言**：Python (FastAPI) + HTML/JavaScript
**数据库**：SQLite

---

## 📋 系统简介

本系统是为"媄月商业艺术"开发的完整权限管理系统，提供用户管理、角色管理、权限管理和审计日志等核心功能。

### 核心功能

- ✅ **用户管理**：创建、修改、删除用户
- ✅ **角色管理**：管理角色和角色权限
- ✅ **权限管理**：细粒度的权限控制（13个模块，30+权限）
- ✅ **审计日志**：完整的操作审计记录
- ✅ **JWT认证**：基于令牌的安全认证
- ✅ **四级权限**：超级管理员、高级管理员、部门经理、普通员工

---

## 🚀 快速开始

### 方法一：使用启动脚本（推荐）

#### Linux/Mac

```bash
cd src/auth
chmod +x start.sh
./start.sh
```

#### Windows

```bash
cd src/auth
start.bat
```

### 方法二：手动启动

#### 1. 安装依赖

```bash
cd src/auth
pip install -r requirements.txt
```

#### 2. 初始化数据库

```bash
python init_data.py
```

#### 3. 启动后端服务

```bash
python api.py
```

后端服务将在 http://localhost:8000 启动

#### 4. 打开前端界面

在浏览器中打开 `index.html` 文件，或访问：
- http://localhost:8000（如果配置了静态文件服务）
- 或直接双击 `index.html` 文件

---

## 🔑 默认账号

| 账号 | 邮箱 | 密码 | 角色 | 权限 |
|-----|------|------|------|------|
| 许锋 | xufeng@meiyue.com | Meiyue@2026 | 超级管理员 | 所有权限 |
| CTO | cto@meiyue.com | Temp@2026 | CTO管理员 | 技术相关 |
| CMO | cmo@meiyue.com | Temp@2026 | CMO管理员 | 市场相关 |
| COO | coo@meiyue.com | Temp@2026 | COO管理员 | 运营相关 |
| CFO | cfo@meiyue.com | Temp@2026 | CFO管理员 | 财务相关 |

⚠️ **首次登录后请立即修改密码！**

---

## 📂 文件结构

```
auth/
├── api.py                 # FastAPI后端API
├── models.py              # SQLAlchemy数据库模型
├── init_data.py           # 数据库初始化脚本
├── index.html             # 前端界面
├── requirements.txt       # Python依赖
├── start.sh               # Linux/Mac启动脚本
├── start.bat              # Windows启动脚本
├── 操作手册.md            # 详细操作手册
└── README.md              # 本文件
```

---

## 🔧 核心功能说明

### 1. 用户管理

- **创建用户**：添加新用户并分配角色
- **修改用户**：更新用户信息
- **删除用户**：删除用户账号
- **查看用户**：查看用户列表和详情

### 2. 角色管理

系统包含7个预定义角色：

1. 超级管理员（super_admin）- 级别1
2. CTO管理员（cto_admin）- 级别2
3. CMO管理员（cmo_admin）- 级别2
4. COO管理员（coo_admin）- 级别2
5. CFO管理员（cfo_admin）- 级别2
6. 部门经理（manager）- 级别3
7. 普通员工（staff）- 级别4

### 3. 权限管理

系统包含13个权限模块：

1. 用户管理（user_management）
2. 角色管理（role_management）
3. 权限管理（permission_management）
4. 系统配置（system_config）
5. 数据管理（data_management）
6. 审批管理（approval_management）
7. 财务管理（financial_management）
8. 合同管理（contract_management）
9. 产品管理（product_management）
10. 营销管理（marketing_management）
11. 运营管理（operation_management）
12. 文档管理（document_management）
13. 日志管理（log_management）

### 4. 审计日志

系统自动记录以下操作：
- 用户登录（成功/失败）
- 用户创建/修改/删除
- 角色创建/修改/删除
- 权限授予/撤销
- 其他关键操作

---

## 📚 API文档

启动后端服务后，访问以下地址查看完整API文档：

**Swagger UI**：http://localhost:8000/docs

**ReDoc**：http://localhost:8000/redoc

### 主要API端点

#### 认证
- `POST /api/auth/login` - 用户登录

#### 用户管理
- `GET /api/users` - 获取用户列表
- `POST /api/users` - 创建用户
- `PUT /api/users/{user_id}` - 更新用户
- `DELETE /api/users/{user_id}` - 删除用户

#### 角色管理
- `GET /api/roles` - 获取角色列表

#### 权限管理
- `GET /api/permissions` - 获取权限列表
- `GET /api/me/permissions` - 获取当前用户权限

#### 审计日志
- `GET /api/audit-logs` - 获取审计日志

---

## 🔐 安全特性

1. **密码加密**：使用bcrypt加密存储密码
2. **JWT认证**：基于令牌的安全认证机制
3. **权限控制**：细粒度的权限检查
4. **审计日志**：完整的操作审计记录
5. **双因素认证**：支持2FA（可选功能）

---

## 📖 使用指南

### 首次登录

1. 启动后端服务
2. 打开前端界面（index.html）
3. 使用默认账号登录：
   - 邮箱：xufeng@meiyue.com
   - 密码：Meiyue@2026
4. 登录成功后可以：
   - 查看用户列表
   - 创建新用户
   - 删除用户
   - 查看角色和权限
   - 查看审计日志

### 创建新用户

1. 以管理员身份登录
2. 点击"用户管理"标签
3. 点击"创建用户"按钮
4. 填写用户信息并选择角色
5. 点击"创建"按钮

### 查看审计日志

1. 以管理员身份登录
2. 点击"审计日志"标签
3. 查看所有操作记录

---

## ⚙️ 配置说明

### JWT配置

在 `api.py` 中修改JWT配置：

```python
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8小时
```

### 数据库配置

在 `init_data.py` 中修改数据库配置：

```python
DATABASE_URL = "sqlite:///./auth.db"
```

如需使用MySQL或PostgreSQL，修改为：

```python
DATABASE_URL = "mysql+pymysql://user:password@localhost/dbname"
# 或
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

---

## 🐛 常见问题

### Q: 忘记密码怎么办？

A: 当前版本不支持通过界面重置密码。请联系超级管理员通过数据库直接修改密码。详见《操作手册.md》。

### Q: 为什么无法登录？

A: 请检查：
1. 邮箱和密码是否正确
2. 账号状态是否为"active"
3. 后端服务是否正常启动
4. 浏览器控制台是否有错误信息

### Q: 如何修改用户的角色？

A: 当前版本需要通过API或数据库直接修改。详见《操作手册.md》。

### Q: 如何添加新的权限？

A: 需要在数据库中直接添加权限记录。详见《操作手册.md》。

---

## 📝 开发说明

### 数据库模型

- `User` - 用户表
- `Role` - 角色表
- `Permission` - 权限表
- `AuditLog` - 审计日志表
- `Session` - 会话表

### 权限检查

在API端点中使用 `check_permission` 依赖来检查权限：

```python
@app.get("/api/users")
async def get_users(
    current_user: User = Depends(check_permission("user:view")),
    db: Session = Depends(get_db)
):
    ...
```

### 创建审计日志

使用 `create_audit_log` 函数创建审计日志：

```python
create_audit_log(
    db, current_user.id, "user:create",
    resource_type="user",
    resource_id=new_user.id,
    description=f"创建用户：{user_data.name}"
)
```

---

## 📞 技术支持

- **技术支持**：tech@meiyue.com
- **权限咨询**：admin@meiyue.com
- **安全举报**：security@meiyue.com

---

## 📄 许可证

© 2026 媄月商业 版权所有 | 未经授权不得复制、下载、传播

---

**媄月商业艺术 - 文化科技驱动的品牌未来资产**

---

## 更新日志

### v1.0 (2026-01-23)
- ✅ 初始版本发布
- ✅ 完整的用户管理功能
- ✅ 角色和权限管理
- ✅ 审计日志系统
- ✅ Web前端界面
- ✅ 完整的API文档
