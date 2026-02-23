# 🔄 部署回滚方案

**版本**: v1.0
**创建时间**: 2026-02-22
**适用场景**: 推荐人显示和密码修改功能修复部署

---

## 📋 回滚概述

### 回滚时机

在以下情况下需要执行回滚：

1. **验证测试失败** - 自动化验证脚本测试失败
2. **功能异常** - 推荐人字段无法显示或密码修改功能异常
3. **性能下降** - API响应时间明显变慢
4. **服务不稳定** - 服务频繁崩溃或报错
5. **用户反馈** - 收到用户投诉或异常报告

### 回滚原则

- **快速响应** - 确认问题后立即回滚，不超过15分钟
- **完整回滚** - 回滚所有修改的文件和配置
- **验证回滚** - 回滚后必须验证系统恢复正常
- **记录回滚** - 详细记录回滚原因和过程

---

## 🚀 回滚方案

### 方案1: 自动回滚（推荐）

使用部署脚本自动回滚到上一个版本。

```bash
# 查找最新备份
BACKUP=$(ssh user@meiyueart.com "ls -t ~/backups/ | head -1")

# 恢复文件
scp user@meiyueart.com:~/backups/$BACKUP/user_system.py \
    admin-backend/routes/

scp user@meiyueart.com:~/backups/$BACKUP/change_password.py \
    admin-backend/routes/

# 重新部署
./deploy_now.sh
```

**优点**: 自动化程度高，减少人为错误
**缺点**: 依赖脚本正确性

---

### 方案2: 手动回滚（标准）

直接在生产环境恢复备份文件。

```bash
ssh user@meiyueart.com << 'ENDSSH'
    # 1. 查找最新备份
    echo "查找备份..."
    ls -lht ~/backups/ | head -5

    # 2. 选择要回滚的备份
    BACKUP_DIR="YYYYMMDD_HHMMSS"

    # 3. 恢复文件
    echo "恢复文件..."
    cp ~/backups/$BACKUP_DIR/user_system.py \
       /var/www/meiyueart.com/admin-backend/routes/

    cp ~/backups/$BACKUP_DIR/change_password.py \
       /var/www/meiyueart.com/admin-backend/routes/

    # 4. 验证文件恢复
    echo "验证文件恢复..."
    md5sum /var/www/meiyueart.com/admin-backend/routes/user_system.py
    md5sum /var/www/meiyueart.com/admin-backend/routes/change_password.py

    # 5. 重启服务
    echo "重启服务..."
    sudo supervisorctl restart lingzhi_admin_backend

    # 6. 检查服务状态
    echo "检查服务状态..."
    sudo supervisorctl status lingzhi_admin_backend

    # 7. 验证服务
    echo "验证服务..."
    curl -s https://meiyueart.com/api/health

    echo "✅ 回滚完成"
ENDSSH
```

**优点**: 直接控制，可以查看每个步骤的执行结果
**缺点**: 需要手动执行多个步骤

---

### 方案3: 应急回滚（快速）

在紧急情况下，快速回滚核心功能。

```bash
ssh user@meiyueart.com << 'ENDSSH'
    # 快速恢复并重启
    BACKUP=$(ls -t ~/backups/ | head -1)
    cp ~/backups/$BACKUP/user_system.py /var/www/meiyueart.com/admin-backend/routes/
    cp ~/backups/$BACKUP/change_password.py /var/www/meiyueart.com/admin-backend/routes/
    sudo supervisorctl restart lingzhi_admin_backend
    sleep 5
    sudo supervisorctl status lingzhi_admin_backend
ENDSSH

# 验证回滚
curl https://meiyueart.com/api/health
```

**优点**: 快速，只需一条命令
**缺点**: 步骤较少，缺少验证

---

## 📋 回滚前检查清单

在执行回滚前，请确认：

- [ ] 确认需要回滚的问题
- [ ] 已记录问题和现象
- [ ] 已找到最新备份
- [ ] 通知团队成员即将回滚
- [ ] 准备好回滚验证方案
- [ ] 确认回滚时间窗口

---

## ✅ 回滚验证清单

回滚完成后，必须验证以下项目：

### 服务验证

- [ ] 服务状态为 `RUNNING`
- [ ] 健康检查通过：`curl https://meiyueart.com/api/health`
- [ ] 日志无异常错误

### 功能验证

- [ ] 用户可以正常登录
- [ ] 用户信息API正常返回
- [ ] 系统其他功能正常
- [ ] 用户未报告异常

### 性能验证

- [ ] API响应时间正常
- [ ] 服务资源占用正常
- [ ] 无明显性能下降

---

## 📊 回滚流程图

```
发现问题
    ↓
评估影响
    ↓
确认需要回滚
    ↓
查找备份
    ↓
执行回滚
    ↓
重启服务
    ↓
验证回滚
    ↓
记录回滚
    ↓
分析问题
    ↓
修复问题
    ↓
重新部署
```

---

## 📝 回滚记录模板

```markdown
# 回滚记录

## 基本信息

- **回滚时间**: YYYY-MM-DD HH:MM:SS
- **回滚人员**: _________________
- **回滚版本**: YYYYMMDD_HHMMSS
- **原部署版本**: YYYYMMDD_HHMMSS

## 回滚原因

描述为什么需要回滚：
- 问题现象：
- 影响范围：
- 严重程度：

## 回滚过程

### 执行的回滚方案
- [ ] 方案1: 自动回滚
- [ ] 方案2: 手动回滚
- [ ] 方案3: 应急回滚

### 回滚步骤
1. 备份时间：
2. 恢复文件：
3. 重启服务：
4. 验证回滚：

## 回滚验证

### 服务验证
- [ ] 服务状态正常
- [ ] 健康检查通过

### 功能验证
- [ ] 用户登录正常
- [ ] 用户信息正常
- [ ] 其他功能正常

### 性能验证
- [ ] 响应时间正常
- [ ] 资源占用正常

## 回滚结果

- [ ] ✅ 回滚成功
- [ ] ⚠️ 部分成功
- [ ] ❌ 回滚失败

## 后续计划

- [ ] 分析问题原因
- [ ] 修复问题代码
- [ ] 测试修复方案
- [ ] 重新部署
- [ ] 持续监控

## 备注

记录其他重要信息：
```

---

## 🚨 应急联系方式

### 紧急情况

如果回滚失败或出现严重问题：

1. **立即联系**
   - 运维团队: ops@meiyueart.com
   - 紧急支持: emergency@meiyueart.com

2. **提供信息**
   - 回滚时间和版本
   - 遇到的问题
   - 错误日志

3. **等待指示**
   - 停止操作
   - 等待技术支持

---

## 💡 最佳实践

### 1. 定期备份

```bash
# 添加到crontab，每天凌晨2点自动备份
0 2 * * * ~/auto_backup.sh
```

### 2. 测试回滚

每次部署后，测试回滚流程是否正常：

```bash
# 模拟回滚（不实际执行）
./deploy_now.sh --dry-run
```

### 3. 记录回滚

详细记录每次回滚的原因和过程，用于后续分析和改进。

### 4. 改进流程

根据回滚经验，持续改进部署和回滚流程。

---

## 📚 相关文档

- [部署执行指南](./DEPLOYMENT_EXECUTION_GUIDE.md)
- [部署快速检查清单](./DEPLOYMENT_QUICK_CHECKLIST.md)
- [版本检查报告](./VERSION_CHECK_REPORT.md)
- [部署操作手册](./DEPLOYMENT_OPERATIONS_MANUAL.md)

---

**回滚方案版本**: v1.0
**创建时间**: 2026-02-22
**维护团队**: 运维团队

**重要提示**: 回滚是最后的选择，请在确认无法快速修复问题后再执行回滚。
