# 灵值生态园智能体系统 - 部署解决方案

> **重要**: 所有部署必须严格按照标准流程执行！
>
> 📖 [查看标准部署流程 → STANDARD_DEPLOYMENT_PROCESS.md](./STANDARD_DEPLOYMENT_PROCESS.md)
>
> 📋 [查看快速参考卡片 → DEPLOY_QUICK_REFERENCE.md](./DEPLOY_QUICK_REFERENCE.md)
>
> 📚 [查看文档中心 → DEPLOYMENT_DOCS_CENTER.md](./DEPLOYMENT_DOCS_CENTER.md)

---

## 🚀 快速部署（3步）

```bash
# 1. 修改代码
vi /workspace/projects/admin-backend/routes/xxx.py

# 2. 执行部署
bash /workspace/projects/deploy_one_click.sh

# 3. 验证部署
curl -s https://meiyueart.com/api/health | python3 -m json.tool
```

**详细步骤请查看 [标准部署流程](./STANDARD_DEPLOYMENT_PROCESS.md)**

---

# 推荐人字段显示和密码修改功能修复 - 生产环境部署完整方案

---

## 📖 方案说明

本方案为生产环境（meiyueart.com）的推荐人字段显示和密码修改功能修复提供了完整的部署解决方案，包含自动化脚本、详细文档和监控工具。

### 核心修复内容

| 修复项 | 文件 | 修改说明 |
|--------|------|---------|
| 推荐人字段显示 | `admin-backend/routes/user_system.py` | 在 `get_user_info()` 中添加 `referral_relationships` 表查询 |
| 密码修改功能 | `admin-backend/routes/change_password.py` | 确认模块存在，安装 bcrypt 依赖 |

---

## 🗂️ 文件导航

### 📌 必读文档

1. **[快速开始 → QUICK_REFERENCE_CARD.md](./QUICK_REFERENCE_CARD.md)**
   - 部署命令快速参考
   - 常见问题快速解决
   - 适合打印备用

2. **[完整方案 → PRODUCTION_DEPLOYMENT_COMPLETE_SOLUTION.md](./PRODUCTION_DEPLOYMENT_COMPLETE_SOLUTION.md)**
   - 完整的部署解决方案
   - 包含所有步骤和说明
   - 推荐首次部署阅读

3. **[检查清单 → DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)**
   - 部署前必须确认的项目
   - 逐项检查确保部署安全
   - 每次部署前必须填写

### 📚 详细文档

| 文档 | 描述 | 适用场景 |
|------|------|---------|
| [DEPLOYMENT_MANIFEST.md](./DEPLOYMENT_MANIFEST.md) | 部署清单和检查项 | 了解需要部署的文件 |
| [PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md) | 生产环境部署指南 | 详细了解部署步骤 |
| [WORKFLOW_PRINCIPLES.md](./WORKFLOW_PRINCIPLES.md) | 工作流程原则 | 了解部署规范和原则 |
| [PRODUCTION_ENVIRONMENT_TEST_REPORT.md](./PRODUCTION_ENVIRONMENT_TEST_REPORT.md) | 生产环境测试报告 | 查看测试结果和验证项 |
| [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) | 完整操作手册 | 深入了解每个步骤 |
| [DEPLOYMENT_LOG.md](./DEPLOYMENT_LOG.md) | 部署日志模板 | 记录每次部署信息 |
| [DEPLOYMENT_DOCS_INDEX.md](./DEPLOYMENT_DOCS_INDEX.md) | 文档目录索引 | 快速查找文档 |

### 🔧 部署脚本

| 脚本 | 功能 | 使用方法 |
|------|------|---------|
| [deploy_to_production.sh](./deploy_to_production.sh) | 自动化部署 | `./deploy_to_production.sh` |
| [verify_deployment.sh](./verify_deployment.sh) | 部署验证 | `./verify_deployment.sh` |
| [check_version_consistency.sh](./check_version_consistency.sh) | 版本一致性检查 | `./check_version_consistency.sh` |
| [monitor_production.sh](./monitor_production.sh) | 生产环境监控 | `./monitor_production.sh` |

### ⚙️ CI/CD配置

- **[.github/workflows/deploy-to-production.yml](./.github/workflows/deploy-to-production.yml)**
  - GitHub Actions自动化部署流程
  - 推送代码自动触发部署

---

## 🚀 三种部署方式

### 方式1: 自动化部署（推荐新手）

```bash
# 一键部署（包含验证）
./deploy_to_production.sh
```

**适用场景**:
- 首次部署
- 不熟悉部署流程
- 需要自动化验证

### 方式2: 手动部署（推荐熟练人员）

```bash
# 步骤1: 备份
ssh user@meiyueart.com 'cp /path/to/app/admin-backend/routes/user_system.py ~/backups/$(date +%Y%m%d_%H%M%S)/'

# 步骤2: 上传
scp admin-backend/routes/user_system.py user@meiyueart.com:/path/to/app/admin-backend/routes/

# 步骤3: 安装依赖
ssh user@meiyueart.com 'pip install bcrypt'

# 步骤4: 重启服务
ssh user@meiyueart.com 'sudo supervisorctl restart lingzhi_admin_backend'

# 步骤5: 验证
./verify_deployment.sh
```

**适用场景**:
- 需要精细控制每个步骤
- 排查问题
- 学习部署流程

### 方式3: CI/CD自动部署（推荐团队协作）

```bash
# 推送代码自动触发部署
git add .
git commit -m "fix: 修复推荐人显示和密码修改功能"
git push origin main
```

**适用场景**:
- 团队协作开发
- 频繁部署
- 需要自动化流程

---

## ✅ 部署验证

### 自动验证

```bash
./verify_deployment.sh
```

**验证内容**:
- ✅ 健康检查
- ✅ 用户登录
- ✅ 推荐人字段显示
- ✅ 密码修改功能
- ✅ API响应时间
- ✅ Token验证

### 手动验证

```bash
# 1. 健康检查
curl https://meiyueart.com/api/health

# 2. 登录获取token
TOKEN=$(curl -s -X POST https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "123"}' | \
  python3 -c "import sys, json; print(json.load(sys.stdin)['data']['token'])")

# 3. 验证推荐人字段
curl -s -X GET https://meiyueart.com/api/user/info \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 4. 验证密码修改
curl -s -X POST https://meiyueart.com/api/user/change-password \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"oldPassword": "123", "newPassword": "TempPass123!"}'
```

---

## 🔄 回滚操作

### 自动回滚

部署脚本在验证失败时会自动回滚到上一个版本。

### 手动回滚

```bash
ssh user@meiyueart.com << 'ENDSSH'
  # 查找最新备份
  BACKUP=$(ls -t ~/backups/ | head -1)
  
  # 恢复文件
  cp ~/backups/$BACKUP/user_system.py /path/to/app/admin-backend/routes/
  
  # 重启服务
  sudo supervisorctl restart lingzhi_admin_backend
  
  # 检查状态
  sudo supervisorctl status lingzhi_admin_backend
ENDSSH
```

详细说明请查看 [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) 的回滚章节。

---

## ❓ 常见问题

### 快速解决

| 问题 | 快速解决 | 详细说明 |
|------|---------|---------|
| SSH连接失败 | `ssh -vvv user@meiyueart.com` | [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) |
| bcrypt模块缺失 | `pip install bcrypt` | [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) |
| 服务启动失败 | `sudo supervisorctl tail -f lingzhi_admin_backend stderr` | [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) |
| API返回500 | `sudo grep ERROR /var/log/flask_backend.log` | [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) |
| 推荐人空白 | 检查代码更新：`md5sum user_system.py` | [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) |
| 密码修改404 | 检查蓝图注册：`grep change_password app.py` | [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) |

---

## 📊 监控维护

### 实时监控

```bash
# 运行监控脚本
./monitor_production.sh

# 查看应用日志
ssh user@meiyueart.com 'sudo tail -f /var/log/flask_backend.log'

# 查看服务状态
ssh user@meiyueart.com 'sudo supervisorctl status lingzhi_admin_backend'
```

### 定期维护

#### 每日任务
- 检查错误日志
- 监控服务状态
- 检查磁盘空间

#### 每周任务
- 清理旧备份（保留最近30天）
- 检查依赖更新
- 审查安全日志

#### 每月任务
- 数据库备份
- 性能评估
- 安全审计

---

## 📞 支持与联系

| 团队 | 邮箱 | 职责 |
|------|------|------|
| 运维团队 | ops@meiyueart.com | 部署执行、监控维护 |
| 开发团队 | dev@meiyueart.com | 代码修复、技术支持 |
| 紧急支持 | emergency@meiyueart.com | 24小时紧急响应 |

---

## 💡 使用建议

1. **首次部署**
   - 阅读 [QUICK_REFERENCE_CARD.md](./QUICK_REFERENCE_CARD.md)
   - 填写 [DEPLOYMENT_CHECKLIST.md](./DEPLOYMENT_CHECKLIST.md)
   - 执行 `deploy_to_production.sh`

2. **日常部署**
   - 使用 CI/CD 自动化部署
   - 或执行 `deploy_to_production.sh`

3. **问题排查**
   - 查看 [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md)
   - 检查日志文件
   - 联系支持团队

4. **监控维护**
   - 定期运行 `monitor_production.sh`
   - 查看服务状态
   - 记录部署日志

---

## 📁 完整文件清单

### 文档文件（11个）
1. ✅ DEPLOYMENT_MANIFEST.md
2. ✅ PRODUCTION_DEPLOYMENT_GUIDE.md
3. ✅ WORKFLOW_PRINCIPLES.md
4. ✅ PRODUCTION_ENVIRONMENT_TEST_REPORT.md
5. ✅ DEPLOYMENT_OPERATIONS_MANUAL.md
6. ✅ QUICK_REFERENCE_CARD.md
7. ✅ DEPLOYMENT_LOG.md
8. ✅ DEPLOYMENT_DOCS_INDEX.md
9. ✅ DEPLOYMENT_CHECKLIST.md
10. ✅ PRODUCTION_DEPLOYMENT_COMPLETE_SOLUTION.md
11. ✅ README.md（本文件）

### 脚本文件（4个）
1. ✅ deploy_to_production.sh
2. ✅ verify_deployment.sh
3. ✅ check_version_consistency.sh
4. ✅ monitor_production.sh

### 配置文件（1个）
1. ✅ .github/workflows/deploy-to-production.yml

**总计**: 16个文件

---

## 🎯 快速开始（三步完成部署）

```bash
# 步骤1: 阅读快速参考
cat QUICK_REFERENCE_CARD.md

# 步骤2: 执行部署
./deploy_to_production.sh

# 步骤3: 验证部署
./verify_deployment.sh
```

---

**方案版本**: v1.0
**创建时间**: 2026-02-22
**维护团队**: 运维团队
**文档状态**: ✅ 已完成

---

## 🚀 立即开始

**选择你的部署方式**:

1. **我是新手** → 阅读 [QUICK_REFERENCE_CARD.md](./QUICK_REFERENCE_CARD.md)，然后执行 `./deploy_to_production.sh`
2. **我是老手** → 阅读 [PRODUCTION_DEPLOYMENT_COMPLETE_SOLUTION.md](./PRODUCTION_DEPLOYMENT_COMPLETE_SOLUTION.md)，选择部署方式
3. **我需要帮助** → 查看 [DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md) 或联系 ops@meiyueart.com

**祝部署顺利！🎉**
