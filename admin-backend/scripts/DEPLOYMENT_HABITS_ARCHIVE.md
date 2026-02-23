# 部署习惯和流程档案
## 档案编号: DEPLOYMENT-HABIT-001
## 创建日期: 2026-02-15

---

## 核心原则（必须遵守）

### 1. 部署定义
**所有"部署"操作，默认指部署到生产环境（meiyueart.com）**

- 生产环境地址: https://meiyueart.com
- 生产服务器: 123.56.142.143
- 前端路径: /var/www/meiyueart.com
- 后端路径: /opt/lingzhi-ecosystem/backend
- 后端服务: gunicorn (port 8080)

### 2. 全自动闭环
**任何部署操作必须一次性完成，不能分步骤或留待后续**

- 前端构建 → 上传 → 部署 → 验证（一气呵成）
- 后端修复 → 数据库更新 → 服务重启 → 验证（一气呵成）
- 绝不允许"待执行"、"待部署"的状态

### 3. 使用已有脚本
**优先使用已有的全自动部署脚本，不要重复创建**

- 前端部署: `./deploy.sh`
- 后端部署: `admin-backend/scripts/deploy_backend_fix_real.sh`
- 脚本位置固定，每次都从同一位置调用

---

## 标准部署流程

### 前端部署（5分钟）

```bash
# 1. 执行全自动部署脚本
cd /workspace/projects
./deploy.sh

# 脚本会自动完成：
# - 构建前端
# - 上传到对象存储
# - 部署到生产服务器
# - 验证部署
```

**预期输出**:
```
✅ 部署完成！
版本: 20260215-1111
访问地址: https://meiyueart.com
```

### 后端部署（5分钟）

```bash
# 1. 执行后端修复脚本
cd /workspace/projects
./admin-backend/scripts/deploy_backend_fix_real.sh

# 脚本会自动完成：
# - 备份生产环境
# - 更新数据库表结构
# - 重启后端服务
# - 验证部署
```

**预期输出**:
```
✓ 数据库表结构已更新
✓ 后端服务已重启
✓ 部署完成！
```

---

## 常见错误及解决方案

### 错误1: 重新创建部署脚本
**错误表现**: 每次部署都创建新的脚本

**正确做法**:
- 使用已有的 `./deploy.sh`
- 使用已有的 `deploy_backend_fix_real.sh`
- 不要重复创建

### 错误2: 分步骤部署
**错误表现**: 先构建，再问是否部署，再上传...

**正确做法**:
- 一次性执行完整脚本
- 不允许中间暂停
- 不允许用户确认（除非严重错误）

### 错误3: 忽略生产环境
**错误表现**: 只在本地测试，不部署到生产环境

**正确做法**:
- 所有部署默认到生产环境
- 除非明确说"本地测试"，否则都部署到生产环境

### 错误4: 不验证部署结果
**错误表现**: 部署完成后不验证

**正确做法**:
- 自动验证版本号
- 自动验证健康检查
- 自动验证关键功能

---

## 部署检查清单

### 部署前
- [ ] 确认修改已完成
- [ ] 确认本地测试通过
- [ ] 确认部署脚本存在

### 部署中
- [ ] 执行全自动部署脚本
- [ ] 观察部署过程
- [ ] 确认无错误

### 部署后
- [ ] 验证版本号
- [ ] 验证网站可访问
- [ ] 验证关键功能
- [ ] 记录部署日志

---

## 部署脚本位置

### 前端部署
```
/workspace/projects/deploy.sh
```

### 后端部署
```
/workspace/projects/admin-backend/scripts/deploy_backend_fix_real.sh
```

### 其他部署脚本
```
/workspace/projects/admin-backend/scripts/
├── deploy.sh
├── deploy_agent_v3.sh
├── deploy_prod_v1.2.0.sh
├── incremental_deploy.sh
└── auto_deploy.sh
```

---

## 生产环境信息

### 服务器配置
- **地址**: 123.56.142.143
- **用户**: root
- **密码**: Meiyue@root123
- **系统**: Ubuntu 24.04.3 LTS

### 路径配置
- **前端**: /var/www/meiyueart.com
- **后端**: /opt/lingzhi-ecosystem/backend
- **数据库**: /opt/lingzhi-ecosystem/backend/lingzhi_ecosystem.db

### 服务配置
- **Web服务器**: Nginx
- **应用服务器**: Gunicorn
- **后端端口**: 8080
- **前端端口**: 443 (HTTPS)

---

## 验证命令

### 前端验证
```bash
# 检查版本号
curl -s https://meiyueart.com/ | grep -o "app-version.*" | head -1

# 检查网站可访问
curl -I https://meiyueart.com/

# 检查关键文件
curl -s https://meiyueart.com/assets/index-*.css | head -1
```

### 后端验证
```bash
# 健康检查
curl -s https://meiyueart.com/api/health

# 检查服务状态
ssh root@123.56.142.143 "ps aux | grep gunicorn | grep -v grep"

# 检查数据库
ssh root@123.56.142.143 "ls -lh /opt/lingzhi-ecosystem/backend/lingzhi_ecosystem.db"
```

---

## 回滚方案

### 前端回滚
```bash
ssh root@123.56.142.143 << 'EOF'
BACKUP_DATE="20260215_111212"
cp -r /var/www/meiyueart.com/backup_$BACKUP_DATE/* /var/www/meiyueart.com/
EOF
```

### 后端回滚
```bash
ssh root@123.56.142.143 << 'EOF'
cd /opt/lingzhi-ecosystem/backend
BACKUP_DIR="backup_20260215_111339"
cp $BACKUP_DIR/* ./
pkill -f gunicorn
source venv/bin/activate
nohup gunicorn -w 1 -b 0.0.0.0:8080 app:app > server.log 2>&1 &
EOF
```

---

## 经验教训

### 教训1: 记不住部署目标
**问题**: 总是忘记"部署"指的是生产环境

**解决方案**:
- 在档案中明确记录
- 每次部署前查看档案
- 严格执行全自动部署

### 教训2: 重复创建脚本
**问题**: 每次都创建新的部署脚本

**解决方案**:
- 维护一套标准部署脚本
- 修改现有脚本而不是创建新的
- 脚本位置固定

### 教训3: 分步骤执行
**问题**: 部署过程被打断，分步骤执行

**解决方案**:
- 使用全自动脚本
- 一次性执行所有步骤
- 不允许中间暂停

### 教训4: 验证不充分
**问题**: 部署后验证不全面

**解决方案**:
- 自动验证版本号
- 自动验证关键功能
- 记录验证结果

---

## 持续改进

### 短期改进
1. ✅ 创建部署习惯档案
2. ✅ 标准化部署流程
3. ✅ 固定脚本位置

### 长期改进
1. ⏳ 实现CI/CD流程
2. ⏳ 自动化测试
3. ⏳ 监控告警系统

---

## 参考

### 相关文档
- 部署指南: `admin-backend/scripts/PRODUCTION_DEPLOYMENT_GUIDE.md`
- 部署报告: `admin-backend/scripts/PRODUCTION_DEPLOYMENT_FINAL.md`
- 部署脚本: `./deploy.sh`, `deploy_backend_fix_real.sh`

### 历史记录
- 2026-02-15: 创建部署习惯档案
- 2026-02-15: 全自动部署到生产环境成功

---

**记住：所有部署默认指生产环境，必须一次性完成，使用已有脚本！**

---

**档案维护**: Coze Coding
**最后更新**: 2026-02-15
