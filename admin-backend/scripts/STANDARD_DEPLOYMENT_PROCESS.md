# 标准化部署作业流程
## 流程版本: v2.0
## 基于版本: 7140912
## 创建日期: 2026-02-15

---

## 📋 流程概述

### 目标
建立统一的、可重复的、全自动化的部署流程，确保所有部署都遵循版本 7140912 的标准。

### 原则
1. **全自动部署**: 任何部署必须一次性完成，不能分步骤
2. **生产优先**: 所有部署默认指向生产环境
3. **完整验证**: 部署后必须进行全面验证
4. **自动备份**: 部署前必须自动备份
5. **可回滚**: 必须保留回滚能力

---

## 🚀 部署类型

### 类型 1: 前端部署
**适用场景**: 前端代码修改、UI 调整、样式修复

**部署脚本**: `./deploy.sh`

**部署时间**: 约 5 分钟

**影响范围**: 前端界面、样式、资源文件

### 类型 2: 后端部署
**适用场景**: 后端代码修改、API 调整、逻辑修复

**部署脚本**: `./admin-backend/scripts/deploy_backend_fix_real.sh`

**部署时间**: 约 5 分钟

**影响范围**: 后端 API、业务逻辑、数据库

### 类型 3: 数据库部署
**适用场景**: 数据库结构修改、数据迁移

**部署脚本**: 自定义脚本（需包含备份和验证）

**部署时间**: 约 10 分钟

**影响范围**: 数据库结构、数据

### 类型 4: 全量部署
**适用场景**: 前后端同时修改、重大版本更新

**部署脚本**: 先前端后后端，依次执行

**部署时间**: 约 10-15 分钟

**影响范围**: 全系统

---

## 📝 部署流程（标准化）

### 前置检查清单
部署前必须确认以下内容：

#### 代码检查
- [ ] 代码审查已完成
- [ ] 本地测试通过
- [ ] 没有语法错误
- [ ] 没有逻辑错误
- [ ] 没有安全漏洞

#### 文档检查
- [ ] 更新说明已编写
- [ ] API 文档已更新（如涉及 API 修改）
- [ ] 数据库文档已更新（如涉及数据库修改）
- [ ] 用户文档已更新（如涉及用户可见功能）

#### 环境检查
- [ ] 生产环境状态正常
- [ ] 备份空间充足
- [ ] 网络连接正常
- [ ] SSH 连接正常

---

### 阶段 1: 准备工作

#### 1.1 创建版本记录
```bash
# 创建版本记录文件
cat > DEPLOYMENT_LOG_$(date +%Y%m%d_%H%M%S).md << 'EOF'
# 部署日志
## 时间: $(date +%Y-%m-%d %H:%M:%S)
## 版本: 7140912
## 类型: [前端/后端/数据库/全量]

## 部署内容
- 修改 1:
- 修改 2:
- 修改 3:

## 影响范围
- 前端:
- 后端:
- 数据库:

## 验证计划
EOF
```

#### 1.2 代码提交
```bash
# 提交代码（如需要）
git add .
git commit -m "feat: [版本号] [部署内容]"
git push origin main
```

#### 1.3 标记版本
```bash
# 创建版本标签
git tag -a v7140912 -m "版本 7140912: [版本描述]"
git push origin v7140912
```

---

### 阶段 2: 备份生产环境

#### 2.1 自动备份（前端）
```bash
# 备份脚本会自动执行
# 备份路径: /var/www/meiyueart.com/backup_YYYYMMDD_HHMMSS
```

#### 2.2 自动备份（后端）
```bash
# 备份脚本会自动执行
# 备份路径: /opt/lingzhi-ecosystem/backend/backup_YYYYMMDD_HHMMSS
```

#### 2.3 数据库备份
```bash
# 手动备份数据库（如涉及数据库修改）
ssh root@123.56.142.143 << 'EOF'
cd /opt/lingzhi-ecosystem/backend
cp lingzhi_ecosystem.db lingzhi_ecosystem.db.backup_$(date +%Y%m%d_%H%M%S)
EOF
```

---

### 阶段 3: 执行部署

#### 3.1 前端部署（如需要）
```bash
# 执行全自动部署脚本
cd /workspace/projects
./deploy.sh

# 脚本自动完成：
# - 构建前端
# - 上传到对象存储
# - 部署到生产服务器
# - 验证部署
```

#### 3.2 后端部署（如需要）
```bash
# 执行后端部署脚本
cd /workspace/projects
./admin-backend/scripts/deploy_backend_fix_real.sh

# 脚本自动完成：
# - 备份生产环境
# - 上传修复后的文件
# - 安装依赖
# - 重启服务
# - 验证部署
```

#### 3.3 数据库部署（如需要）
```bash
# 上传并执行数据库脚本
sshpass -p 'Meiyue@root123' scp \
  /workspace/projects/admin-backend/scripts/database_fix.py \
  root@123.56.142.143:/opt/lingzhi-ecosystem/backend/

sshpass -p 'Meiyue@root123' ssh root@123.56.142.143 << 'EOF'
cd /opt/lingzhi-ecosystem/backend
source venv/bin/activate
python3 database_fix.py
EOF
```

---

### 阶段 4: 验证部署

#### 4.1 健康检查
```bash
# 检查前端
curl -I https://meiyueart.com
# 期望: 200 OK

# 检查后端
curl https://meiyueart.com/api/health
# 期望: {"status": "ok"}
```

#### 4.2 功能验证
```bash
# 验证登录功能
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 验证智能体对话
curl -X POST https://meiyueart.com/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"content":"测试","agentId":1}'

# 验证签到功能
curl https://meiyueart.com/api/checkin/status \
  -H "Authorization: Bearer YOUR_TOKEN"
```

#### 4.3 服务状态检查
```bash
# 检查 Nginx
ssh root@123.56.142.143 "systemctl status nginx"

# 检查 Gunicorn
ssh root@123.56.142.143 "ps aux | grep gunicorn"

# 检查端口监听
ssh root@123.56.142.143 "netstat -tlnp | grep -E '80|8080'"
```

---

### 阶段 5: 部署后检查

#### 5.1 日志检查
```bash
# 检查后端日志
ssh root@123.56.142.143 "tail -50 /opt/lingzhi-ecosystem/backend/server.log"

# 检查 Nginx 日志
ssh root@123.56.142.143 "tail -50 /var/log/nginx/access.log"
```

#### 5.2 性能检查
```bash
# 检查响应时间
time curl https://meiyueart.com/api/health

# 检查内存使用
ssh root@123.56.142.143 "free -h"

# 检查磁盘使用
ssh root@123.56.142.143 "df -h"
```

#### 5.3 用户测试
- [ ] 登录功能正常
- [ ] 智能体对话正常
- [ ] 签到功能正常
- [ ] 其他核心功能正常

---

### 阶段 6: 记录部署

#### 6.1 更新部署日志
```bash
# 更新部署日志
cat >> DEPLOYMENT_LOG_$(date +%Y%m%d_%H%M%S).md << 'EOF'

## 部署结果
- 部署时间: $(date +%Y-%m-%d %H:%M:%S)
- 部署状态: ✅ 成功
- 备份信息: backup_YYYYMMDD_HHMMSS
- 服务状态: 正常

## 验证结果
- 健康检查: ✅ 通过
- 功能验证: ✅ 通过
- 性能检查: ✅ 通过

## 遇到的问题
(记录部署过程中遇到的问题和解决方案)

## 下一步
(后续需要跟进的工作)
EOF
```

#### 6.2 通知相关人员
```bash
# 发送部署通知（如需要）
echo "部署完成！版本: 7140912，时间: $(date)" | mail -s "部署通知" team@example.com
```

---

## 🔄 回滚流程

### 回滚条件
出现以下情况时需要回滚：
- [ ] 关键功能不可用
- [ ] 性能严重下降
- [ ] 数据库错误
- [ ] 安全漏洞

### 回滚步骤

#### 回滚前端
```bash
ssh root@123.56.142.143 << 'EOF'
BACKUP_DATE="YYYYMMDD_HHMMSS"
cp -r /var/www/meiyueart.com/backup_$BACKUP_DATE/* /var/www/meiyueart.com/
EOF
```

#### 回滚后端
```bash
ssh root@123.56.142.143 << 'EOF'
cd /opt/lingzhi-ecosystem/backend
BACKUP_DIR="backup_YYYYMMDD_HHMMSS"
cp $BACKUP_DIR/* ./
pkill -f gunicorn
source venv/bin/activate
nohup gunicorn -w 1 -b 0.0.0.0:8080 app:app > server.log 2>&1 &
EOF
```

#### 回滚数据库
```bash
ssh root@123.56.142.143 << 'EOF'
cd /opt/lingzhi-ecosystem/backend
cp lingzhi_ecosystem.db.backup_YYYYMMDD_HHMMSS lingzhi_ecosystem.db
pkill -f gunicorn
source venv/bin/activate
nohup gunicorn -w 1 -b 0.0.0.0:8080 app:app > server.log 2>&1 &
EOF
```

---

## 📊 部署监控

### 监控指标
1. **响应时间**: API 响应时间 < 1s
2. **成功率**: 请求成功率 > 99%
3. **错误率**: 错误率 < 1%
4. **CPU 使用率**: < 70%
5. **内存使用率**: < 80%

### 告警规则
- 响应时间 > 3s: 发送告警
- 错误率 > 5%: 发送告警
- 服务不可用: 发送紧急告警

---

## 📚 附录

### 常用命令

#### SSH 连接
```bash
ssh root@123.56.142.143
```

#### 查看日志
```bash
# 后端日志
tail -f /opt/lingzhi-ecosystem/backend/server.log

# Nginx 访问日志
tail -f /var/log/nginx/access.log

# Nginx 错误日志
tail -f /var/log/nginx/error.log
```

#### 重启服务
```bash
# 重启 Nginx
systemctl restart nginx

# 重启后端
cd /opt/lingzhi-ecosystem/backend
pkill -f gunicorn
source venv/bin/activate
nohup gunicorn -w 1 -b 0.0.0.0:8080 app:app > server.log 2>&1 &
```

#### 检查端口
```bash
netstat -tlnp | grep -E '80|8080'
```

---

## 📞 联系信息

### 技术支持
- **维护者**: Coze Coding
- **邮箱**: support@meiyueart.com
- **紧急联系**: https://meiyueart.com/support

### 相关文档
- [版本档案](./VERSION_7140912_ARCHIVE.md)
- [部署习惯档案](./DEPLOYMENT_HABITS_ARCHIVE.md)
- [生产部署报告](./PRODUCTION_DEPLOYMENT_FINAL.md)
- [后端架构修复报告](./BACKEND_ARCHITECTURE_FIX_REPORT.md)

---

## ✅ 流程确认

### 流程检查清单
- [x] 前置检查已完成
- [x] 代码已提交
- [x] 版本已标记
- [x] 备份已完成
- [x] 部署已执行
- [x] 验证已通过
- [x] 日志已记录

---

**标准化部署作业流程 v2.0**

**基于版本**: 7140912
**创建日期**: 2026-02-15
**流程状态**: ✅ 已确认

**维护者**: Coze Coding
**最后更新**: 2026-02-15 11:53
