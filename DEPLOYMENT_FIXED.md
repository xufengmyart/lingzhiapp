# 📋 部署流程固定化说明

> **重要**: 以后所有部署必须严格按照此固定流程执行！

---

## ✅ 已完成工作

### 1. 创建标准部署流程文档

**文件**: `STANDARD_DEPLOYMENT_PROCESS.md`

**内容**:
- 6步标准部署流程
- 详细的执行步骤
- 常见错误处理
- 验证检查清单
- 固定配置信息

### 2. 创建快速参考卡片

**文件**: `DEPLOY_QUICK_REFERENCE.md`

**内容**:
- 一键部署命令
- 验证命令
- 固定配置信息
- 常见字段错误

### 3. 创建部署历史归档

**文件**: `deploy_archive/DEPLOYMENT_HISTORY.md`

**内容**:
- 所有部署历史记录
- 部署统计
- 快速查询

### 4. 创建文档中心

**文件**: `DEPLOYMENT_DOCS_CENTER.md`

**内容**:
- 所有文档的统一入口
- 快速导航
- 部署状态

### 5. 更新主文档

**文件**: `DEPLOY_README.md`

**内容**:
- 部署流程总入口
- 快速开始指南
- 文档导航

### 6. 创建状态文档

**文件**: `DEPLOYMENT_STATUS.md`

**内容**:
- 当前部署状态
- 服务状态
- 测试账号

---

## 🎯 固定部署流程

### 标准流程（6步）

```
1️⃣ 准备阶段（代码修复）
   ↓
2️⃣ 本地测试验证
   ↓
3️⃣ 一键自动化部署
   ↓
4️⃣ 修复字段错误（如有）
   ↓
5️⃣ 生产环境验证
   ↓
6️⃣ 归档文档
```

### 执行命令

```bash
# 步骤1: 修改代码
vi /workspace/projects/admin-backend/routes/xxx.py

# 步骤2: 执行部署
bash /workspace/projects/deploy_one_click.sh

# 步骤3: 修复字段错误（如有）
# 修改 → 上传 → 重启

# 步骤4: 验证部署
curl -s https://meiyueart.com/api/health | python3 -m json.tool
# ... 执行验证命令

# 步骤5: 归档文档
# 更新部署历史
```

---

## 📁 固定配置信息

### 服务器信息
```
服务器: meiyueart.com
IP: 123.56.142.143
端口: 22
用户: root
密码: Meiyue@root123
```

### 路径信息
```
后端: /app/meiyueart-backend
数据库: /app/meiyueart-backend/data/lingzhi_ecosystem.db
前端: /var/www/meiyueart.com
日志: /var/log/meiyueart-backend/app.log
备份: /var/www/backups/
```

### 测试账号
```
管理员: admin / admin123
普通用户: 马伟娟 / 123
其他用户: 所有用户密码123
```

---

## 📚 文档结构

```
/workspace/projects/
├── DEPLOY_README.md                  # 部署主文档（入口）
├── DEPLOYMENT_STATUS.md              # 当前部署状态
├── DEPLOY_QUICK_REFERENCE.md         # 快速参考卡片
├── DEPLOYMENT_DOCS_CENTER.md         # 文档中心
├── STANDARD_DEPLOYMENT_PROCESS.md    # ⭐ 标准部署流程（核心）
├── deploy_one_click.sh               # ⭐ 一键部署脚本
├── deploy_archive/
│   └── DEPLOYMENT_HISTORY.md         # 部署历史记录
└── deploy_output.log                 # 部署输出日志
```

---

## ⚠️ 重要提醒

### 必须遵循
- ✅ 所有部署必须按照标准流程执行
- ✅ 不得擅自修改部署步骤
- ✅ 每次部署必须验证
- ✅ 每次部署必须归档

### 禁止行为
- ❌ 不要重复询问部署步骤
- ❌ 不要修改固定配置
- ❌ 不要跳过验证步骤
- ❌ 不要忘记归档文档

---

## 🎯 执行总结

**一句话**: 修改代码 → 执行deploy_one_click.sh → 修复字段错误 → 验证 → 归档

**核心命令**:
```bash
bash /workspace/projects/deploy_one_click.sh
```

**核心文档**:
```bash
STANDARD_DEPLOYMENT_PROCESS.md
```

---

## ✅ 固定化完成

### 已固定
- ✅ 部署流程（6步）
- ✅ 部署脚本
- ✅ 配置信息
- ✅ 文档结构
- ✅ 验证标准
- ✅ 归档流程

### 已文档化
- ✅ 标准流程文档
- ✅ 快速参考卡片
- ✅ 部署历史归档
- ✅ 文档中心
- ✅ 状态文档

### 已验证
- ✅ 部署流程已验证可用
- ✅ 所有命令已测试
- ✅ 所有功能已验证

---

## 📝 后续部署要求

### 每次部署前
1. 阅读 `STANDARD_DEPLOYMENT_PROCESS.md`
2. 查阅 `DEPLOY_QUICK_REFERENCE.md`
3. 确认代码修改正确

### 每次部署时
1. 执行 `deploy_one_click.sh`
2. 修复字段错误（如有）
3. 验证部署结果
4. 更新部署历史

### 每次部署后
1. 更新 `DEPLOYMENT_STATUS.md`
2. 更新 `deploy_archive/DEPLOYMENT_HISTORY.md`
3. 检查服务状态

---

**流程版本**: v1.0
**创建时间**: 2026-02-22
**固定化状态**: ✅ 已完成
**验证状态**: ✅ 已验证可用

**重要**: 以后所有部署必须严格按照此固定流程执行，不得擅自修改！
