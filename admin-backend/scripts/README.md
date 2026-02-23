# 增量式部署流程文档

## 概述

本文档描述灵值生态园后端服务的标准化增量式部署流程。

## 核心特性

### 增量式部署
- **文件对比**: 对比新旧文件，只更新有变化的文件
- **结构保护**: 保护原有设计和板块，不破坏现有结构
- **安全更新**: 更新前验证文件完整性，确保不影响原设计

### 自动化特性
- **自动备份**: 每次部署前自动创建备份
- **智能对比**: 识别文件变更状态（新增/修改/删除）
- **完整验证**: 部署后自动验证所有功能

### 闭环管理
- **完整日志**: 所有操作都有详细日志
- **失败回滚**: 部署失败时可从备份恢复
- **验证清单**: 完整的功能验证清单

## 快速开始

### 一键部署
```bash
cd /workspace/projects
bash admin-backend/scripts/deploy.sh
```

## 部署流程详解

### 步骤 1: 创建备份
- 创建时间戳备份目录
- 备份核心文件（app.py, 数据库, 路由目录）
- 保留最近5个备份，自动清理旧备份

### 步骤 2: 环境准备
- 创建工作目录
- 创建日志目录
- 验证路径

### 步骤 3: 全局文件分析
- 分析核心文件状态
- 统计路由文件数量
- 识别文件变更类型

### 步骤 4: 结构完整性检查
- **app.py**: 检查 Flask 导入、蓝图注册、CORS 配置
- **签到系统**: 检查字段名（lingzhi_earned）
- **智能体系统**: 检查 LLMClient、Blueprint

### 步骤 5: 数据库配置验证
- 检查智能体配置
- 自动更新为最佳配置（doubao-seed-1-6-251015, max_tokens=4096, thinking=enabled）

### 步骤 6: 依赖安装
- 安装 requirements.txt 中的依赖
- 安装核心依赖（flask, flask-cors, pyjwt, bcrypt, python-dotenv, gunicorn）

### 步骤 7: 部署服务
- 停止现有服务
- 启动 gunicorn 服务
- 等待服务启动（最多10次重试）

### 步骤 8: 功能验证
- **健康检查**: 验证服务基本可用性
- **智能体系统**: 测试回复质量和长度（>1000字符）
- **签到系统**: 验证API可用性（需要登录）

## 文件对比规则

### 变更类型识别
```bash
# 同一文件对比
compare_files(file1, file2)

# 返回值:
# - "new": 文件1不存在，文件2存在（新增）
# - "deleted": 文件1存在，文件2不存在（删除）
# - "same": 文件相同
# - "modified": 文件不同（修改）
```

### 结构保护规则

#### app.py 保护
- ✅ 必须包含 `from flask import Flask`
- ✅ 必须包含 `register_blueprint`
- ✅ 必须包含 CORS 配置

#### 路由文件保护
- ✅ 必须包含 Blueprint 定义
- ✅ 必须包含路由装饰器 `@bp.route`
- ✅ 签到系统必须使用 `lingzhi_earned` 字段

#### 智能体系统保护
- ✅ 必须包含 LLMClient
- ✅ 必须包含 Blueprint

## 备份策略

### 自动备份
```bash
# 备份目录结构
admin-backend/backups/
├── backup_20260215_091411/
│   ├── app.py
│   ├── lingzhi_ecosystem.db
│   └── routes/
├── backup_20260215_092015/
│   └── ...
└── backup_20260215_093015/
    └── ...
```

### 备份保留策略
- 保留最近5个备份
- 自动删除超过5个的旧备份
- 按时间戳命名，便于追溯

### 备份恢复
```bash
# 查看备份列表
ls -lh admin-backend/backups/

# 恢复特定备份
cp -r admin-backend/backups/backup_20260215_091411/* admin-backend/

# 恢复数据库
cp admin-backend/backups/backup_20260215_091411/lingzhi_ecosystem.db admin-backend/
```

## 配置信息

### 服务配置
```bash
工作目录: /workspace/projects/admin-backend
备份目录: /workspace/projects/admin-backend/backups
日志目录: /var/log/meiyueart
服务端口: 8080
Worker进程: 2
超时时间: 120秒
```

### 智能体配置
```json
{
  "model": "doubao-seed-1-6-251015",
  "temperature": 0.7,
  "max_tokens": 4096,
  "top_p": 0.9,
  "thinking": "enabled"
}
```

## API端点

### 基础API
- `GET /api/health` - 健康检查
- `POST /api/login` - 用户登录
- `POST /api/register` - 用户注册

### 签到系统
- `GET /api/checkin/status` - 获取签到状态
- `POST /api/checkin` - 执行签到

### 智能体系统
- `POST /api/chat` - 智能体对话
- `GET /api/conversations/<id>` - 获取对话历史
- `GET /api/conversations` - 获取对话列表

## 日志文件

```
/var/log/meiyueart/
├── access.log      # 访问日志
├── error.log       # 错误日志
└── startup.log     # 启动日志
```

## 故障排查

### 服务启动失败
```bash
# 查看错误日志
tail -n 50 /var/log/meiyueart/error.log

# 检查端口占用
lsof -i:8080

# 恢复备份
cp -r admin-backend/backups/backup_YYYYMMDD_HHMMSS/* admin-backend/
```

### 配置问题
```bash
# 检查智能体配置
cd /workspace/projects/admin-backend
python -c "
import sqlite3, json
conn = sqlite3.connect('lingzhi_ecosystem.db')
cursor = conn.cursor()
cursor.execute('SELECT id, name, model_config FROM agents')
for agent in cursor.fetchall():
    config = json.loads(agent[2])
    print(f'{agent[1]}: {config}')
conn.close()
"
```

### 文件结构问题
```bash
# 验证 app.py 结构
grep "from flask import Flask" admin-backend/app.py
grep "register_blueprint" admin-backend/app.py
grep "CORS" admin-backend/app.py

# 验证签到系统字段
grep "lingzhi_earned" admin-backend/routes/complete_apis.py

# 验证智能体系统
grep "LLMClient" admin-backend/routes/agent.py
grep "Blueprint" admin-backend/routes/agent.py
```

## 部署脚本

### 主部署脚本
```bash
admin-backend/scripts/deploy.sh          # 标准化部署（增量式）⭐
admin-backend/scripts/incremental_deploy.sh  # 增量式部署（完整版）
```

### 文档
```bash
admin-backend/scripts/README.md          # 本文档
admin-backend/scripts/VERIFICATION_REPORT.md  # 验证报告
```

## 验证清单

部署完成后，请验证以下功能：

### 基础功能
- [ ] 服务启动成功
- [ ] 健康检查返回 ok
- [ ] 日志文件正常生成

### 智能体系统
- [ ] 智能体回复长度 > 1000字符
- [ ] 智能体回复质量优秀
- [ ] 包含开场白、事务层、意义层、行动引导

### 签到系统
- [ ] 签到系统API可用
- [ ] 字段名正确（lingzhi_earned）
- [ ] 斐波那契数列奖励正确

### 公司信息
- [ ] 公司名称准确（陕西媄月商业艺术有限责任公司）
- [ ] 无错误日志

### 备份验证
- [ ] 备份文件已创建
- [ ] 备份文件完整
- [ ] 旧备份已清理

## 部署模式对比

### 全新部署 vs 增量部署

| 特性 | 全新部署 | 增量部署 |
|------|---------|---------|
| 备份 | 手动 | 自动 |
| 文件对比 | 无 | 有 |
| 结构保护 | 无 | 有 |
| 回滚能力 | 差 | 强 |
| 风险 | 高 | 低 |
| 速度 | 快 | 中等 |

## 版本历史

### v4.0.0 (2026-02-15)
- 实现增量式部署
- 添加文件对比功能
- 添加结构保护机制
- 自动备份和清理
- 完整验证流程

### v3.0.0 (2026-02-15)
- 增量式部署基础版本
- 文件对比框架

### v2.0.0 (2026-02-15)
- 整合所有部署流程
- 全自动化部署
- 闭环验证

### v1.0.0 (2026-02-01)
- 初始版本
- 基础部署功能

## 最佳实践

### 部署前
1. 确认代码已提交
2. 查看变更日志
3. 准备回滚方案

### 部署中
1. 观察部署日志
2. 检查错误信息
3. 验证每个步骤

### 部署后
1. 验证所有功能
2. 检查日志文件
3. 保留备份记录

## 安全建议

1. **备份管理**: 定期检查备份完整性
2. **访问控制**: 限制部署脚本执行权限
3. **日志审计**: 定期检查部署日志
4. **监控告警**: 设置服务监控告警

## 联系方式

如有问题，请联系技术团队。

---

**注意**: 本文档会持续更新，请使用最新版本。
