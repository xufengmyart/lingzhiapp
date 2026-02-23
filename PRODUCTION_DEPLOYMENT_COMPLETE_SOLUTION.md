# 灵值生态园智能体系统 - 生产环境部署完整方案

> 为推荐人字段显示和密码修改功能修复提供完整的部署解决方案

---

## 📦 方案概览

本方案提供了从部署准备、执行、验证到监控维护的完整流程，确保生产环境部署的安全性和可靠性。

### 核心修复内容

1. **推荐人字段显示修复**
   - 文件: `admin-backend/routes/user_system.py`
   - 修改: 在 `get_user_info()` 函数中添加 `referral_relationships` 表查询
   - 效果: 用户信息API返回完整的推荐人信息（id, username, avatar）

2. **密码修改功能修复**
   - 文件: `admin-backend/routes/change_password.py`（确认存在）
   - 依赖: bcrypt 模块（需安装）
   - 效果: 用户可以正常修改密码

---

## 🗂️ 文件清单

### 📚 文档文件（11个）

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `DEPLOYMENT_MANIFEST.md` | 部署清单 | 列出所有需要部署的文件和检查项 |
| `PRODUCTION_DEPLOYMENT_GUIDE.md` | 部署指南 | 详细的生产环境部署步骤 |
| `WORKFLOW_PRINCIPLES.md` | 工作原则 | 确立"生产环境强制测试原则" |
| `PRODUCTION_ENVIRONMENT_TEST_REPORT.md` | 测试报告 | 生产环境测试记录和结果 |
| `DEPLOYMENT_OPERATIONS_MANUAL.md` | 操作手册 | 完整的部署操作指南 |
| `QUICK_REFERENCE_CARD.md` | 快速参考 | 部署命令快速查询卡片 |
| `DEPLOYMENT_LOG.md` | 部署日志 | 部署记录模板 |
| `DEPLOYMENT_DOCS_INDEX.md` | 文档索引 | 所有文档的目录索引 |
| `DEPLOYMENT_CHECKLIST.md` | 检查清单 | 部署前必须确认的项目列表 |
| `PRODUCTION_DEPLOYMENT_COMPLETE_SOLUTION.md` | 本文件 | 完整方案概览 |

### 🔧 脚本文件（5个）

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `deploy_to_production.sh` | 自动部署脚本 | 一键部署到生产环境 |
| `verify_deployment.sh` | 验证脚本 | 自动验证部署结果 |
| `check_version_consistency.sh` | 版本检查脚本 | 检查容器和生产环境代码一致性 |
| `monitor_production.sh` | 监控脚本 | 监控生产环境状态并告警 |
| `generate_deploy_report.sh` | 报告生成脚本 | 生成部署执行报告 |

### ⚙️ 配置文件（1个）

| 文件名 | 描述 | 用途 |
|--------|------|------|
| `.github/workflows/deploy-to-production.yml` | CI/CD配置 | GitHub Actions自动化部署流程 |

---

## 🚀 快速开始

### 方式一：自动部署（推荐新手）

```bash
# 1. 阅读快速参考
cat QUICK_REFERENCE_CARD.md

# 2. 执行自动化部署
./deploy_to_production.sh

# 3. 验证部署结果
./verify_deployment.sh
```

### 方式二：手动部署（推荐熟练人员）

```bash
# 1. 备份当前版本
ssh user@meiyueart.com 'cp /path/to/app/admin-backend/routes/user_system.py ~/backups/$(date +%Y%m%d_%H%M%S)/'

# 2. 上传修复文件
scp admin-backend/routes/user_system.py user@meiyueart.com:/path/to/app/admin-backend/routes/

# 3. 安装依赖
ssh user@meiyueart.com 'pip install bcrypt'

# 4. 重启服务
ssh user@meiyueart.com 'sudo supervisorctl restart lingzhi_admin_backend'

# 5. 验证功能
./verify_deployment.sh
```

### 方式三：CI/CD自动部署（推荐团队协作）

```bash
# 推送代码触发自动部署
git add .
git commit -m "fix: 修复推荐人显示和密码修改功能"
git push origin main
```

---

## 📋 部署前准备

### 必须确认项

1. **服务器访问**
   - [ ] SSH密钥已配置
   - [ ] 服务器可正常连接
   - [ ] 有sudo权限

2. **代码准备**
   - [ ] 修复文件已更新
   - [ ] 本地测试通过
   - [ ] 版本一致性检查通过

3. **备份准备**
   - [ ] 当前版本已备份
   - [ ] 备份路径已记录
   - [ ] 回滚方案已准备

### 检查清单

使用 `DEPLOYMENT_CHECKLIST.md` 逐项确认：

```bash
# 查看检查清单
cat DEPLOYMENT_CHECKLIST.md
```

---

## ✅ 部署验证

### 自动验证

```bash
./verify_deployment.sh
```

验证内容：
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

### 浏览器验证

1. 访问 https://meiyueart.com
2. 登录系统
3. 检查推荐人字段显示
4. 测试密码修改功能

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

#### 每日
- 检查错误日志
- 监控服务状态
- 检查磁盘空间

#### 每周
- 清理旧备份
- 检查依赖更新
- 审查安全日志

#### 每月
- 数据库备份
- 性能评估
- 安全审计

---

## ❓ 常见问题

### 问题1: SSH连接失败

**症状**: `Permission denied (publickey)`

**解决方案**:
```bash
# 检查SSH密钥
ssh -vvv user@meiyueart.com
```

### 问题2: bcrypt模块缺失

**症状**: `ModuleNotFoundError: No module named 'bcrypt'`

**解决方案**:
```bash
ssh user@meiyueart.com 'pip install bcrypt'
```

### 问题3: 服务启动失败

**症状**: 服务状态为 `STOPPED`

**解决方案**:
```bash
ssh user@meiyueart.com 'sudo supervisorctl tail -f lingzhi_admin_backend stderr'
```

更多问题请查看 `DEPLOYMENT_OPERATIONS_MANUAL.md`

---

## 📞 支持与联系

| 团队 | 邮箱 | 职责 |
|------|------|------|
| 运维团队 | ops@meiyueart.com | 部署执行、监控维护 |
| 开发团队 | dev@meiyueart.com | 代码修复、技术支持 |
| 紧急支持 | emergency@meiyueart.com | 24小时紧急响应 |

---

## 📝 附录

### A. 目录结构

```
workspace/projects/
├── DEPLOYMENT_MANIFEST.md                    # 部署清单
├── PRODUCTION_DEPLOYMENT_GUIDE.md            # 部署指南
├── WORKFLOW_PRINCIPLES.md                    # 工作原则
├── PRODUCTION_ENVIRONMENT_TEST_REPORT.md     # 测试报告
├── DEPLOYMENT_OPERATIONS_MANUAL.md           # 操作手册
├── QUICK_REFERENCE_CARD.md                   # 快速参考
├── DEPLOYMENT_LOG.md                         # 部署日志
├── DEPLOYMENT_DOCS_INDEX.md                  # 文档索引
├── DEPLOYMENT_CHECKLIST.md                   # 检查清单
├── PRODUCTION_DEPLOYMENT_COMPLETE_SOLUTION.md# 本文件
├── deploy_to_production.sh                   # 自动部署脚本
├── verify_deployment.sh                      # 验证脚本
├── check_version_consistency.sh              # 版本检查脚本
├── monitor_production.sh                     # 监控脚本
└── .github/workflows/deploy-to-production.yml # CI/CD配置
```

### B. 关键配置

```bash
# 服务器配置
PRODUCTION_SERVER="user@meiyueart.com"
APP_PATH="/path/to/app"

# 服务配置
SERVICE_NAME="lingzhi_admin_backend"

# 告警配置
ALERT_EMAIL="ops@meiyueart.com"
MAX_RESPONSE_TIME=5000  # 5秒
```

### C. 部署时间估算

- 自动部署: 10-15分钟
- 手动部署: 15-20分钟
- CI/CD部署: 20-25分钟
- 回滚操作: 5-10分钟

---

## 🎯 下一步行动

1. **立即执行**（5分钟）
   - [ ] 阅读 `QUICK_REFERENCE_CARD.md`
   - [ ] 运行 `check_version_consistency.sh`
   - [ ] 确认备份目录存在

2. **准备部署**（10分钟）
   - [ ] 填写 `DEPLOYMENT_CHECKLIST.md`
   - [ ] 选择部署方式
   - [ ] 通知相关人员

3. **执行部署**（15分钟）
   - [ ] 运行 `deploy_to_production.sh`
   - [ ] 执行 `verify_deployment.sh`
   - [ ] 记录部署日志

4. **监控验证**（持续）
   - [ ] 设置 `monitor_production.sh` 定时任务
   - [ ] 监控服务状态
   - [ ] 检查日志和告警

---

**方案版本**: v1.0
**创建时间**: 2026-02-22
**维护团队**: 运维团队
**文档状态**: ✅ 已完成

---

## 💡 建议

1. **打印快速参考卡片**: 将 `QUICK_REFERENCE_CARD.md` 打印并贴在显示器旁边
2. **保存检查清单**: 在每次部署前使用 `DEPLOYMENT_CHECKLIST.md` 逐项确认
3. **记录部署日志**: 使用 `DEPLOYMENT_LOG.md` 记录每次部署的详细信息
4. **定期备份**: 设置定时任务自动备份生产环境
5. **监控告警**: 使用 `monitor_production.sh` 监控生产环境状态

**祝部署顺利！🚀**
