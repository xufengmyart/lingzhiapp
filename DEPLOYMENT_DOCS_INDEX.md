# 灵值生态园智能体系统 - 部署文档中心

> 生产环境部署完整指南

---

## 📚 文档索引

### 🚀 快速开始
1. **[QUICK_REFERENCE_CARD.md](./QUICK_REFERENCE_CARD.md)** - 部署快速参考卡片（打印此页）
2. **[DEPLOYMENT_MANIFEST.md](./DEPLOYMENT_MANIFEST.md)** - 部署清单和检查项

### 📖 详细指南
3. **[DEPLOYMENT_OPERATIONS_MANUAL.md](./DEPLOYMENT_OPERATIONS_MANUAL.md)** - 完整部署操作手册
4. **[PRODUCTION_DEPLOYMENT_GUIDE.md](./PRODUCTION_DEPLOYMENT_GUIDE.md)** - 生产环境部署指南

### 🔧 脚本工具
5. **[deploy_to_production.sh](./deploy_to_production.sh)** - 自动化部署脚本
6. **[verify_deployment.sh](./verify_deployment.sh)** - 部署验证脚本
7. **[check_version_consistency.sh](./check_version_consistency.sh)** - 版本一致性检查

### 📋 配置与CI/CD
8. **[.github/workflows/deploy-to-production.yml](./.github/workflows/deploy-to-production.yml)** - GitHub Actions CI/CD配置
9. **[WORKFLOW_PRINCIPLES.md](./WORKFLOW_PRINCIPLES.md)** - 工作流程原则

### 📊 监控与记录
10. **[PRODUCTION_ENVIRONMENT_TEST_REPORT.md](./PRODUCTION_ENVIRONMENT_TEST_REPORT.md)** - 生产环境测试报告
11. **[DEPLOYMENT_LOG.md](./DEPLOYMENT_LOG.md)** - 部署日志模板

---

## 🎯 推荐部署流程

### 第一次部署（推荐）

```bash
# 1. 阅读快速参考
cat QUICK_REFERENCE_CARD.md

# 2. 执行自动化部署
./deploy_to_production.sh

# 3. 验证部署
./verify_deployment.sh
```

### 后续部署

```bash
# 方式1: 自动部署（CI/CD）
git add .
git commit -m "fix: xxx"
git push origin main

# 方式2: 手动部署
./deploy_to_production.sh
```

---

## 📞 支持与联系

- **运维团队**: ops@meiyueart.com
- **开发团队**: dev@meiyueart.com
- **紧急支持**: emergency@meiyueart.com

---

## 🔍 文档使用指南

### 新手部署者
1. 先阅读 `QUICK_REFERENCE_CARD.md`
2. 执行 `deploy_to_production.sh` 自动部署
3. 查看 `DEPLOYMENT_OPERATIONS_MANUAL.md` 了解详情

### 经验部署者
1. 查看 `DEPLOYMENT_MANIFEST.md` 确认部署项
2. 选择部署方式（自动/手动/CI/CD）
3. 使用 `verify_deployment.sh` 验证

### 故障排查
1. 查看 `DEPLOYMENT_OPERATIONS_MANUAL.md` 的常见问题章节
2. 检查部署日志
3. 联系运维团队

---

## 📝 更新日志

### 2026-02-22
- 创建部署文档中心
- 添加自动化部署脚本
- 添加部署验证脚本
- 添加版本一致性检查脚本
- 创建CI/CD配置
- 编写完整操作手册

---

**最后更新**: 2026-02-22
**维护人员**: 运维团队
