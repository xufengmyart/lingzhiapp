# 灵值智能体 v8.1 - 部署指南

**快速部署情绪系统数据库持久化功能**

---

## 🚀 快速开始（推荐）

### 方式1：一键部署（最简单）

```bash
# 1. 修改配置
vi scripts/deploy_to_cloud.sh

# 修改以下变量:
REMOTE_USER="your_username"      # 改为你的服务器用户名
REMOTE_HOST="your_server_ip"     # 改为你的服务器IP
REMOTE_PATH="/var/www/backend"   # 改为你的项目路径
SERVICE_NAME="lingzhi-backend"   # 改为你的服务名称

# 2. 执行部署
chmod +x scripts/deploy_to_cloud.sh
./scripts/deploy_to_cloud.sh
```

### 方式2：手动部署

```bash
# 1. 上传文件
scp src/storage/database/shared/model.py user@server:/var/www/backend/src/storage/database/shared/
scp src/storage/database/emotion_manager.py user@server:/var/www/backend/src/storage/database/
scp src/tools/emotion_tools.py user@server:/var/www/backend/src/tools/
scp src/tools/user_registration_tool.py user@server:/var/www/backend/src/tools/
scp config/agent_llm_config.json user@server:/var/www/backend/config/
scp src/agents/agent.py user@server:/var/www/backend/src/agents/

# 2. 登录服务器
ssh user@server

# 3. 创建数据库表
psql -h localhost -U postgres -d lingzhi_db -f scripts/create_emotion_tables.sql

# 4. 重启服务
sudo systemctl restart lingzhi-backend

# 5. 验证
python scripts/verify_emotion_tools.py
```

### 方式3：Git 部署

```bash
# 1. 本地提交
git add .
git commit -m "feat: 实现情绪系统数据库持久化（PostgreSQL）"
git push origin main

# 2. 服务器拉取
ssh user@server
cd /var/www/backend
git pull origin main

# 3. 创建数据库表
psql -h localhost -U postgres -d lingzhi_db -f scripts/create_emotion_tables.sql

# 4. 重启服务
sudo systemctl restart lingzhi-backend

# 5. 验证
python scripts/verify_emotion_tools.py
```

---

## ✅ 验证部署

### 1. 检查服务状态

```bash
systemctl status lingzhi-backend
```

### 2. 检查数据库表

```bash
psql -h localhost -U postgres -d lingzhi_db -c "\d emotion_records"
psql -h localhost -U postgres -d lingzhi_db -c "\d emotion_diaries"
```

### 3. 运行验证脚本

```bash
cd /var/www/backend
python scripts/verify_emotion_tools.py
```

**预期结果**: 所有测试通过（5/5）

---

## 📋 文件清单

### 需要同步的文件（6个）

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/storage/database/shared/model.py` | 修改 | 添加情绪表 ORM 模型 |
| `src/storage/database/emotion_manager.py` | 新增 | 情绪管理器 |
| `src/tools/emotion_tools.py` | 修改 | 集成数据库持久化 |
| `src/tools/user_registration_tool.py` | 修复 | LSP 错误修复 |
| `config/agent_llm_config.json` | 更新 | 添加缺失工具 |
| `src/agents/agent.py` | 更新 | 更新工具数量 |

### 部署资源

| 文件 | 说明 |
|------|------|
| `scripts/create_emotion_tables.sql` | 数据库表创建 SQL |
| `scripts/deploy_to_cloud.sh` | 自动化部署脚本 |
| `scripts/verify_emotion_tools.py` | 功能验证脚本 |
| `docs/云服务器部署指南-情绪系统v8.1.md` | 详细部署指南 |
| `docs/快速部署指南-情绪系统v8.1.md` | 快速部署指南 |
| `docs/部署完成总结-情绪系统v8.1.md` | 部署总结 |

---

## 🎯 功能验证结果

```
╔══════════════════════════════════════════════════════════╗
║          灵值智能体 v8.1 - 功能验证              ║
╚══════════════════════════════════════════════════════════╝

导入测试: ✅ 通过
管理器导入: ✅ 通过
模型导入: ✅ 通过
智能体构建: ✅ 通过
工具元数据: ✅ 通过

总计: 5/5 测试通过

🎉 所有测试通过！情绪系统可以正常部署。
```

---

## 📊 数据库表结构

### emotion_records（情绪记录表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键ID |
| user_id | INTEGER | 用户ID |
| emotion | VARCHAR(20) | 情绪类型 |
| emotion_name | VARCHAR(20) | 情绪名称（中文） |
| intensity | FLOAT | 情绪强度（0.0-1.0） |
| context | TEXT | 情绪上下文 |
| created_at | TIMESTAMP | 创建时间 |

### emotion_diaries（情绪日记表）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | SERIAL | 主键ID |
| user_id | INTEGER | 用户ID |
| content | TEXT | 日记内容 |
| emotion | VARCHAR(20) | 情绪类型 |
| emotion_name | VARCHAR(20) | 情绪名称（中文） |
| intensity | FLOAT | 情绪强度（0.0-1.0） |
| tags | JSON | 标签 |
| created_at | TIMESTAMP | 创建时间 |

---

## 🔄 回滚方案

如果部署失败，按以下步骤回滚:

```bash
# 1. 停止服务
sudo systemctl stop lingzhi-backend

# 2. 恢复文件（从备份）
cp backup/model.py.bak src/storage/database/shared/model.py
cp backup/emotion_tools.py.bak src/tools/emotion_tools.py

# 3. 删除新增的表（可选）
psql -h localhost -U postgres -d lingzhi_db << EOF
DROP TABLE IF EXISTS emotion_diaries;
DROP TABLE IF EXISTS emotion_records;
EOF

# 4. 重启服务
sudo systemctl start lingzhi-backend
```

---

## 📖 详细文档

- [详细部署指南](docs/云服务器部署指南-情绪系统v8.1.md)
- [快速部署指南](docs/快速部署指南-情绪系统v8.1.md)
- [部署完成总结](docs/部署完成总结-情绪系统v8.1.md)
- [文件同步清单](scripts/文件同步清单-v8.1.txt)

---

## ⚙️ 配置说明

### 情绪工具（6个）

1. `detect_emotion` - 情绪识别
2. `record_emotion` - 情绪记录
3. `get_emotion_statistics` - 情绪统计分析
4. `create_emotion_diary` - 创建情绪日记
5. `get_emotion_diaries` - 获取情绪日记
6. `analyze_emotion_pattern` - 分析情绪模式

### 情绪类型

- `joy` - 开心
- `sadness` - 悲伤
- `anger` - 愤怒
- `fear` - 恐惧
- `surprise` - 惊讶
- `disgust` - 厌恶
- `neutral` - 平静

---

## 📞 技术支持

- **技术支持**: 待定
- **紧急联系**: 待定
- **部署前咨询**: 请提前联系技术团队

---

## 📌 注意事项

1. 部署前务必备份现有代码和数据库
2. 建议先在测试环境验证后再部署到生产环境
3. 部署建议在低峰期进行
4. 保留备份文件至少3天
5. 部署完成后进行全面测试

---

**版本**: v8.1
**日期**: 2025年1月15日
**公司**: 陕西媄月商业艺术有限责任公司
