# 部署清单 - 生产环境修复

**部署日期**: 2026-02-22
**部署目标**: meiyueart.com
**部署类型**: 功能修复

---

## 部署文件清单

### 后端文件

| 序号 | 文件路径 | 操作 | 说明 |
|------|---------|------|------|
| 1 | admin-backend/routes/user_system.py | 更新 | 添加推荐人信息查询逻辑 |
| 2 | admin-backend/routes/change_password.py | 确认 | 确保文件存在并可加载 |
| 3 | admin-backend/database.py | 确认 | 确保文件存在并可加载 |
| 4 | admin-backend/app.py | 确认 | 确认change_password蓝图正确注册 |

### 配置文件

| 序号 | 文件路径 | 操作 | 说明 |
|------|---------|------|------|
| 1 | .env.production | 确认 | 确认生产环境配置正确 |

### 依赖包

| 包名 | 版本 | 说明 |
|------|------|------|
| bcrypt | >=4.0.0 | 密码哈希功能 |

---

## 部署检查清单

### 部署前检查

- [ ] 已备份当前生产环境代码
- [ ] 已备份数据库
- [ ] 已在本地测试修改的代码
- [ ] 已准备回滚方案
- [ ] 已通知相关人员

### 部署步骤

- [ ] 上传user_system.py到生产服务器
- [ ] 验证change_password.py存在
- [ ] 验证database.py存在
- [ ] 验证bcrypt已安装
- [ ] 重启Flask服务
- [ ] 检查服务日志
- [ ] 验证健康检查API

### 部署后验证

- [ ] 测试用户登录功能
- [ ] 测试用户信息API（验证推荐人字段）
- [ ] 测试密码修改功能
- [ ] 检查错误日志
- [ ] 验证API响应时间

---

## 回滚方案

如果部署失败，执行以下回滚步骤：

1. **恢复备份的代码**
   ```bash
   cp /path/to/backup/user_system.py.backup /path/to/admin-backend/routes/user_system.py
   ```

2. **重启服务**
   ```bash
   sudo supervisorctl restart lingzhi_admin_backend
   ```

3. **验证回滚成功**
   ```bash
   curl https://meiyueart.com/api/health
   ```

---

## 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 数据库查询失败 | 低 | 中 | 添加错误处理和日志 |
| bcrypt未安装 | 中 | 高 | 部署前检查依赖 |
| 服务启动失败 | 低 | 高 | 检查日志，回滚代码 |
| API响应变慢 | 中 | 中 | 添加数据库索引 |

---

## 相关文档

1. **部署指南**: PRODUCTION_DEPLOYMENT_GUIDE.md
2. **工作流程原则**: WORKFLOW_PRINCIPLES.md
3. **测试报告**: PRODUCTION_ENVIRONMENT_TEST_REPORT.md
4. **自动化脚本**: deploy_to_production.sh

---

**文档版本**: 1.0
**最后更新**: 2026-02-22
