# 部署脚本归档文档

## 概述

本文档归档了灵值生态园系统的所有部署脚本和相关文档，帮助团队快速了解和使用。

---

## 📁 文件结构

```
/workspace/projects/
├── universal_deploy.py              # 🚀 统一万能部署脚本（推荐使用）
├── deploy_history.json              # 部署历史记录
├── .deploy_hashes.json              # 文件哈希记录（增量部署用）
│
├── admin_management_api_complete.py # 完整后台管理 API
├── admin_management_api.py          # 后台管理 API（已部署）
│
├── docs/
│   ├── ADMIN_API_MAPPING.md         # 后台管理与前端对应关系
│   ├── DEPLOYMENT_GUIDE.md          # 部署指南
│   └── API_REFERENCE.md             # API 参考文档
│
└── scripts/
    └── legacy/                      # 历史部署脚本（已归档）
        ├── auto_deploy.py
        ├── auto_fix_production.py
        ├── redeploy_admin_api.py
        └── ...
```

---

## 🚀 推荐部署方式：统一万能部署脚本

### 特性

✅ **增量部署**：基于文件哈希判断是否需要上传，避免重复上传
✅ **模块化**：支持单独部署指定模块
✅ **自动验证**：部署后自动验证功能
✅ **备份机制**：部署前自动备份
✅ **日志记录**：完整的部署日志
✅ **标准化**：统一的部署流程

### 使用方法

#### 1. 部署所有模块
```bash
python3 universal_deploy.py --all
```

#### 2. 仅部署后台管理 API
```bash
python3 universal_deploy.py --admin_api
```

#### 3. 部署多个模块
```bash
python3 universal_deploy.py --admin_api --routes --config
```

#### 4. 强制部署（跳过增量检查）
```bash
python3 universal_deploy.py --all --force
```

#### 5. 查看帮助
```bash
python3 universal_deploy.py --help
```

### 支持的模块

| 模块 | 说明 | 优先级 |
|------|------|--------|
| `backend` | 后端主程序 | 1 |
| `admin_api` | 后台管理 API | 2 |
| `routes` | 路由模块 | 3 |
| `config` | 配置文件 | 4 |

### 部署流程

```
1. 连接服务器
   ↓
2. 备份当前版本
   ↓
3. 检查文件变化（哈希比对）
   ↓
4. 上传变化的文件
   ↓
5. 重置管理员密码
   ↓
6. 重启服务
   ↓
7. 验证功能
   ↓
8. 保存日志
```

---

## 📋 历史部署脚本（已归档）

以下脚本已整合到 `universal_deploy.py` 中，不再单独使用：

| 脚本名 | 功能 | 状态 |
|--------|------|------|
| `auto_deploy.py` | 自动部署后台管理 | ✅ 已整合 |
| `auto_fix_production.py` | 修复生产环境 | ✅ 已整合 |
| `redeploy_admin_api.py` | 重新部署后台 API | ✅ 已整合 |
| `fix_login_issue.py` | 修复登录问题 | ✅ 已整合 |
| `reset_admin_password.py` | 重置管理员密码 | ✅ 已整合 |
| `check_service_status.py` | 检查服务状态 | ✅ 已整合 |
| `verify_complete_api.py` | 验证 API | ✅ 已整合 |

---

## 🔍 部署历史

### 查看部署历史

```bash
cat deploy_history.json
```

### 部署历史格式

```json
[
  {
    "timestamp": "2024-02-17T22:30:00",
    "backup": "backup_20240217_223000",
    "success": true,
    "ok_count": 8,
    "total_count": 8,
    "logs": [
      "[2024-02-17 22:30:00] [INFO] 连接成功",
      "[2024-02-17 22:30:05] [INFO] 上传文件: admin_management_api.py"
    ]
  }
]
```

---

## 📊 部署验证标准

### 自动验证的 API

| API 端点 | 方法 | 说明 |
|---------|------|------|
| `/api/admin/login` | POST | 登录验证 |
| `/api/admin/users` | GET | 用户列表验证 |
| `/api/admin/agents` | GET | 智能体列表验证 |
| `/api/admin/knowledge-bases` | GET | 知识库列表验证 |
| `/api/admin/roles` | GET | 角色列表验证 |
| `/api/admin/permissions` | GET | 权限列表验证 |
| `/api/admin/user-types` | GET | 用户类型验证 |
| `/api/admin/system/status` | GET | 系统状态验证 |

### 成功标准

- ✅ 至少 60% 的测试通过
- ✅ 登录功能必须正常
- ✅ 核心功能正常

---

## 🔐 访问凭证

### 生产环境

**服务器：**
- 地址：123.56.142.143
- 用户：root
- 密码：Meiyue@root123

**管理员账号：**
- 登录地址：https://meiyueart.com/admin/login
- 用户名：admin
- 密码：admin123

**API 基础地址：**
- HTTP: http://localhost:8080
- HTTPS: https://meiyueart.com

---

## 📝 相关文档

### 核心文档

1. **[后台管理与前端对应关系](./docs/ADMIN_API_MAPPING.md)**
   - 详细说明每个前端页面对应的后端 API
   - 包含调用示例和响应格式

2. **[部署指南](./docs/DEPLOYMENT_GUIDE.md)**
   - 详细的部署流程说明
   - 常见问题排查

3. **[API 参考文档](./docs/API_REFERENCE.md)**
   - 完整的 API 接口文档
   - 请求/响应示例

### 辅助文档

- [系统架构文档](./docs/SYSTEM_ARCHITECTURE.md)
- [数据库设计文档](./docs/DATABASE_SCHEMA.md)
- [开发规范文档](./docs/DEVELOPMENT_STANDARDS.md)

---

## ⚠️ 注意事项

### 部署前

1. **检查本地代码**
   - 确保代码无语法错误
   - 测试本地功能正常

2. **备份数据库**
   - 导出数据库备份
   - 保存到安全位置

3. **通知团队**
   - 通知相关人员维护时间
   - 提前准备回滚方案

### 部署中

1. **监控日志**
   - 实时查看部署日志
   - 关注错误信息

2. **验证功能**
   - 部署后立即验证核心功能
   - 确认无异常后再继续

### 部署后

1. **清理临时文件**
   - 删除部署脚本生成的临时文件
   - 清理日志文件

2. **更新文档**
   - 更新版本信息
   - 记录变更内容

3. **监控运行状态**
   - 持续监控系统运行
   - 及时处理异常

---

## 🚨 故障处理

### 常见问题

#### 1. 部署失败

**症状：** 部署过程中报错

**解决方案：**
```bash
# 查看部署日志
cat deploy_history.json | tail -20

# 检查服务器日志
ssh root@123.56.142.143
tail -n 50 /tmp/app.log
```

#### 2. 登录失败

**症状：** 无法登录后台

**解决方案：**
```bash
# 重置密码
python3 -c "
import sqlite3
import bcrypt
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()
pwd = bcrypt.hashpw('admin123'.encode(), bcrypt.gensalt()).decode()
cursor.execute(\"UPDATE admins SET password_hash = ? WHERE username = 'admin'\", (pwd,))
conn.commit()
conn.close()
print('密码已重置')
"
```

#### 3. API 404 错误

**症状：** 访问 API 返回 404

**解决方案：**
```bash
# 检查服务是否运行
ps aux | grep python

# 检查端口是否监听
netstat -tlnp | grep 8080

# 重启服务
pkill -f 'python.*app.py'
cd /root/workspace/admin-backend
nohup python3 app.py > /tmp/app.log 2>&1 &
```

---

## 📞 联系方式

如有问题，请联系：
- 技术负责人：[联系方式]
- 运维团队：[联系方式]

---

## 🔄 更新日志

| 日期 | 版本 | 说明 |
|------|------|------|
| 2024-02-17 | v2.0.0 | 创建统一万能部署脚本，整合所有历史脚本 |
| 2024-02-17 | v1.9.0 | 完善后台管理 API，添加项目管理 |
| 2024-02-17 | v1.8.0 | 修复登录问题，优化部署流程 |
| 2024-02-01 | v1.0.0 | 初始版本 |

---

## 📌 总结

### 最佳实践

1. ✅ **使用统一部署脚本**：`universal_deploy.py`
2. ✅ **增量部署**：节省时间和带宽
3. ✅ **自动验证**：确保功能正常
4. ✅ **备份机制**：失败时可快速回滚
5. ✅ **日志记录**：便于问题追踪

### 推荐工作流

```bash
# 1. 开发和测试本地
# 2. 提交代码到 Git
# 3. 使用统一部署脚本部署
python3 universal_deploy.py --all

# 4. 验证功能
# 5. 如有问题，查看日志排查
# 6. 必要时回滚到备份版本
```

---

**文档版本：** v2.0.0
**最后更新：** 2024-02-17
**维护人员：** Coze Coding
