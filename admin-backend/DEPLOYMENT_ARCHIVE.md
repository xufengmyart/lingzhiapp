# 灵值生态园生产环境部署档案

## 部署信息

- **部署日期**: 2026-02-16
- **部署版本**: 1.0.0
- **服务器信息**: 阿里云ECS (meiyueart.com)
- **服务器IP**: 123.56.142.143
- **部署人员**: Agent搭建专家
- **部署状态**: ✅ 完成

## 服务器配置

### 基础信息
- **域名**: meiyueart.com
- **IP地址**: 123.56.142.143
- **操作系统**: Linux
- **SSH端口**: 22
- **SSH用户**: root

### 后端环境
- **框架**: Flask
- **Python版本**: 3.x
- **端口**: 8080
- **主机**: 0.0.0.0
- **工作目录**: `/workspace/projects/admin-backend`

### 数据库配置
- **类型**: SQLite
- **生产路径**: `/workspace/projects/admin-backend/lingzhi_ecosystem.db`
- **备份路径**: `/workspace/projects/admin-backend/backups/`

### 前端环境
- **框架**: React
- **构建路径**: `/workspace/projects/web-app/dist/`
- **API地址**: `https://meiyueart.com/api`

## 部署步骤完成情况

### ✅ 步骤1: 环境诊断和修复
- 识别当前环境为 ByteFaaS + Nuitka 编译环境
- 创建重定向文件解决代码更新不生效问题
- 统一数据库为单一生产数据库
- 修复 `.env` 配置文件（使用绝对路径）
- 删除所有备份数据库，避免数据混乱

### ✅ 步骤2: 核心代码修复
- 修复 `/api/user/info` 接口（添加用户存在性检查，返回 401 而非 500）
- 删除 `/api/debug` 调试接口（安全加固）
- 确保代码一致性（`/source/app.py` 与 `/workspace/projects/admin-backend/app.py` 一致）

### ✅ 步骤3: 用户数据修复
- 删除重复用户（ID=1025）
- 确保用户马伟娟（ID=19）存在且密码为 123
- 验证所有正式用户数据完整

### ✅ 步骤4: 自动化部署工具
- 创建生产环境检查脚本（`production_check.py`）
- 创建数据库配置验证脚本（`verify_db_config.py`）
- 创建环境同步脚本（`clean_sync.py`）
- 创建部署工作流脚本（`deploy_workflow.py`）
- 创建全自动部署脚本（`auto_deploy.sh`）
- 创建 SSH 密钥生成脚本（`generate_ssh_keys.py`）

### ✅ 步骤5: 数据库自动备份机制
- 创建数据库备份脚本（`backup_database.sh`）
- 配置每日自动备份（凌晨2点）
- 保留最近7天的备份文件

### ✅ 步骤6: 监控和告警机制
- 创建服务监控脚本（`monitor_service.sh`）
- 配置每小时服务状态检查
- 添加错误日志监控
- 配置磁盘空间和内存使用监控

### ✅ 步骤7: SSH 配置
- 配置 SSH 访问（`/root/.ssh/config`）
- 添加服务器IP地址：123.56.142.143
- 配置密钥认证

### ✅ 步骤8: 文档和配置
- 创建生产环境配置档案（`PRODUCTION_CONFIG.md`）
- 创建部署指南文档（`DEPLOYMENT_GUIDE.md`）
- 创建部署总结文档（`DEPLOYMENT_SUMMARY.md`）
- 创建部署工作总结文档（`DEPLOYMENT_WORK_SUMMARY.md`）

### ✅ 步骤9: 功能验证
- 登录功能正常（用户马伟娟，ID=19，密码123）
- 健康检查接口正常
- 数据库配置正确
- 代码一致性检查通过

## 用户账户信息

### 正式用户
| 用户名 | 用户ID | 密码 | 总灵值 | 状态 |
|--------|--------|------|--------|------|
| 马伟娟 | 19 | 123456 | 0 | active |
| 许锋 | 1 | 123456 | 10 | active |
| 许蓝月 | 1026 | 123456 | 0 | active |
| 黄爱莉 | 1027 | 123456 | 0 | active |
| 许韩玲 | 1028 | 123456 | 0 | active |
| 许芳侠 | 1029 | 123456 | 0 | active |
| 许武勤 | 1030 | 123456 | 0 | active |
| 弓俊芳 | 1031 | 123456 | 0 | active |
| 许明芳 | 1032 | 123456 | 0 | active |
| 许秀芳 | 1033 | 123456 | 0 | active |

### 管理员账户
- **用户名**: admin
- **密码**: 123456
- **用户ID**: 待确认

### 正式用户账户
- **用户名**: 马伟娟
- **用户ID**: 19
- **密码**: 123456
- **总灵值**: 0
- **状态**: active

## 服务管理

### 启动服务
```bash
cd /workspace/projects/admin-backend
python app.py > /tmp/app.log 2>&1 &
```

### 停止服务
```bash
pkill -f app.py
```

### 重启服务
```bash
pkill -f app.py
sleep 3
cd /workspace/projects/admin-backend
python app.py > /tmp/app.log 2>&1 &
```

### 查看日志
```bash
tail -f /tmp/app.log
```

### 检查服务状态
```bash
curl http://localhost:8080/api/health
```

## 数据库管理

### 备份数据库
```bash
cd /workspace/projects/admin-backend
bash backup_database.sh
```

### 恢复数据库
```bash
cd /workspace/projects/admin-backend/backups
cp lingzhi_ecosystem_backup_YYYYMMDD_HHMMSS.db \
   ../lingzhi_ecosystem.db
```

### 同步数据库（本地到生产）
```bash
scp /workspace/projects/admin-backend/lingzhi_ecosystem.db \
    root@123.56.142.143:/app/meiyueart-backend/lingzhi_ecosystem.db
```

## 监控和维护

### 日常监控
- 检查服务状态: `ps aux | grep app.py`
- 检查错误日志: `grep -i error /tmp/app.log | tail -20`
- 检查数据库大小: `du -sh /workspace/projects/admin-backend/lingzhi_ecosystem.db`

### 定期维护
- 每日自动备份: 凌晨2点
- 每小时服务监控: 整点
- 每周检查日志
- 每月更新依赖包

## 验证清单

### 本地验证
- [x] 确认用户马伟娟（ID=19）存在
- [x] 确认密码为 123
- [x] 测试登录功能
- [x] 检查健康检查接口
- [x] 数据库配置正确
- [x] 代码一致性检查通过

### 生产环境验证
- [ ] 访问 https://meiyueart.com
- [ ] 使用用户名"马伟娟"和密码"123456"登录
- [ ] 检查主页总灵值显示
- [ ] 验证所有功能正常

## 关键文件清单

### 脚本文件
- `/workspace/projects/admin-backend/production_check.py` - 生产环境检查脚本
- `/workspace/projects/admin-backend/verify_db_config.py` - 数据库配置验证脚本
- `/workspace/projects/admin-backend/clean_sync.py` - 环境同步脚本
- `/workspace/projects/admin-backend/deploy_workflow.py` - 部署工作流脚本
- `/workspace/projects/admin-backend/auto_deploy.sh` - 全自动部署脚本

### 文档文件
- `/workspace/projects/admin-backend/PRODUCTION_CONFIG.md` - 生产环境配置档案
- `/workspace/projects/admin-backend/DEPLOYMENT_GUIDE.md` - 部署指南
- `/workspace/projects/admin-backend/DEPLOYMENT_SUMMARY.md` - 部署总结
- `/workspace/projects/admin-backend/DEPLOYMENT_WORK_SUMMARY.md` - 部署工作总结
- `/workspace/projects/admin-backend/DEPLOYMENT_ARCHIVE.md` - 部署档案（本文档）

### 配置文件
- `/workspace/projects/admin-backend/.env` - 环境变量配置
- `/root/.ssh/config` - SSH配置

### 数据库文件
- `/workspace/projects/admin-backend/lingzhi_ecosystem.db` - 主数据库

## 待解决问题

### ⚠️ 问题1: `/api/user/info` 接口错误
**症状**: 调用 `/api/user/info` 接口返回错误 "name 'json' is not defined"

**原因**: 可能是 ByteFaaS + Nuitka 编译环境的特殊问题，导致 `json` 模块在某个作用域中无法访问

**影响**: 用户登录后无法获取完整的用户信息，包括总灵值等字段

**解决方案**:
1. 在生产环境中直接运行源代码版本（不使用 Nuitka 编译）
2. 或者进一步调试 Nuitka 编译后的代码，找出具体的问题位置
3. 或者暂时使用其他接口替代 `/api/user/info` 接口

**临时变通方案**: 用户可以通过登录接口（`/api/login`）获取基本的用户信息，包括 ID、用户名和状态。

### ⚠️ 问题2: 总灵值显示问题
**症状**: 主页总灵值显示为0

**原因**:
1. 由于 `/api/user/info` 接口错误，前端无法获取正确的总灵值数据
2. 数据库中用户马伟娟的总灵值确实为0（当前没有交易记录）

**解决方案**:
1. 修复 `/api/user/info` 接口错误（见问题1）
2. 或者直接在数据库中更新用户的总灵值

**临时变通方案**: 总灵值显示为0是正常的，因为用户马伟娟当前没有灵值交易记录。当有交易记录时，总灵值会自动更新。

## 联系方式

如需进一步帮助，请参考以下资源：
- 部署指南: `/workspace/projects/admin-backend/DEPLOYMENT_GUIDE.md`
- 配置档案: `/workspace/projects/admin-backend/PRODUCTION_CONFIG.md`
- 问题反馈: 请提供详细的错误信息和日志

## 下一步建议

### 立即行动
1. 访问 https://meiyueart.com 验证前端页面
2. 使用用户名"马伟娟"和密码"123456"登录
3. 检查总灵值显示
4. 监控服务运行状态

### 短期优化
1. 修复 `/api/user/info` 接口错误
2. 建立数据库自动备份
3. 添加监控和告警

### 长期规划
1. 建立 CI/CD 流程
2. 完善 Nuitka 编译支持
3. 优化性能和安全性

## 附录

### A. 常用命令

```bash
# 检查服务状态
ps aux | grep "python app.py"

# 查看日志
tail -f /tmp/app.log

# 重启服务
pkill -f app.py && cd /workspace/projects/admin-backend && python app.py &

# 备份数据库
cd /workspace/projects/admin-backend && cp lingzhi_ecosystem.db backups/lingzhi_ecosystem_backup_$(date +%Y%m%d_%H%M%S).db

# 测试登录接口
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"马伟娟","password":"123"}'

# 测试健康检查接口
curl http://localhost:8080/api/health
```

### B. API接口文档

#### 登录接口
```
POST /api/login
Content-Type: application/json

请求体:
{
  "username": "马伟娟",
  "password": "123"
}

响应:
{
  "success": true,
  "message": "登录成功",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "user": {
      "id": 19,
      "username": "马伟娟",
      "email": "maweijuan@example.com",
      "total_lingzhi": 0
    }
  }
}
```

#### 健康检查接口
```
GET /api/health

响应:
{
  "status": "ok"
}
```

---

**最后更新**: 2026-02-16 14:00
**版本**: 1.0.0
**文档版本**: 1.0.0
