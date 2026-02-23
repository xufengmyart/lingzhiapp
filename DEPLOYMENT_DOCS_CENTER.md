# 📚 生产环境部署文档中心

> 所有部署相关文档的统一入口

---

## 🚀 快速开始

**新部署？从这里开始**：
1. 📖 阅读 `STANDARD_DEPLOYMENT_PROCESS.md` - 标准部署流程
2. 📋 查阅 `DEPLOY_QUICK_REFERENCE.md` - 快速参考卡片
3. 🚀 执行 `deploy_one_click.sh` - 一键部署

---

## 📁 文档目录

### 核心文档（必读）

| 文档 | 描述 | 用途 |
|------|------|------|
| **STANDARD_DEPLOYMENT_PROCESS.md** | ⭐ 标准部署流程 | 所有部署必须遵循的标准流程 |
| **DEPLOY_QUICK_REFERENCE.md** | ⭐ 快速参考卡片 | 部署命令速查表 |
| **deploy_one_click.sh** | ⭐ 一键部署脚本 | 自动化部署主脚本 |

### 归档文档

| 文档 | 描述 | 用途 |
|------|------|------|
| **deploy_archive/DEPLOYMENT_HISTORY.md** | 部署历史记录 | 查看所有部署历史 |
| **deploy_output.log** | 部署输出日志 | 查看最新部署日志 |

### 配置文件

| 文件 | 描述 | 用途 |
|------|------|------|
| **.ssh_config** | 生产环境配置 | 服务器连接信息 |

---

## 📊 部署状态

### 最近一次部署
- **时间**: 2026-02-22 16:09
- **版本**: v20260222
- **状态**: ✅ 成功
- **修复**: 推荐人显示、密码修改功能
- **查看**: [部署历史](./deploy_archive/DEPLOYMENT_HISTORY.md)

### 部署统计
- **总部署次数**: 1
- **成功次数**: 1
- **失败次数**: 0
- **成功率**: 100%

---

## 🎯 部署流程（6步）

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

详细说明请查看 [标准部署流程](./STANDARD_DEPLOYMENT_PROCESS.md)

---

## ⚠️ 重要提醒

### 必须遵循
- ✅ 所有部署必须按照标准流程执行
- ✅ 不得擅自修改部署步骤
- ✅ 每次部署必须验证
- ✅ 每次部署必须归档

### 常见错误
- ❌ 数据库字段名错误（referred_user_id → referee_id）
- ❌ 服务未启动（502错误）
- ❌ SSH连接失败

### 解决方案
详见 [标准部署流程](./STANDARD_DEPLOYMENT_PROCESS.md) 的错误处理章节

---

## 🔧 快速命令

### 部署
```bash
bash /workspace/projects/deploy_one_click.sh
```

### 验证
```bash
# 健康检查
curl -s https://meiyueart.com/api/health | python3 -m json.tool

# 用户登录
curl -s -X POST https://meiyueart.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | python3 -m json.tool
```

### 服务管理
```bash
# 重启服务
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "pkill -f 'python.*app.py' && cd /app/meiyueart-backend && \
   nohup python3 app.py > /var/log/meiyueart-backend/app.log 2>&1 &"

# 查看日志
sshpass -p 'Meiyue@root123' ssh -p 22 root@meiyueart.com \
  "tail -50 /var/log/meiyueart-backend/app.log"
```

---

## 📞 联系信息

| 团队 | 邮箱 | 职责 |
|------|------|------|
| 运维团队 | ops@meiyueart.com | 部署执行、监控维护 |
| 开发团队 | dev@meiyueart.com | 代码修复、技术支持 |
| 紧急支持 | emergency@meiyueart.com | 24小时紧急响应 |

---

## 📝 更新日志

### 2026-02-22
- ✅ 创建标准部署流程文档
- ✅ 固化部署步骤
- ✅ 创建部署历史归档
- ✅ 创建快速参考卡片
- ✅ 首次部署成功（v20260222）

---

## 🎯 使用建议

### 新手部署
1. 先阅读快速参考卡片
2. 按照标准流程逐步执行
3. 遇到问题查看错误处理章节

### 熟练人员
1. 直接使用一键部署脚本
2. 查阅快速参考卡片获取命令
3. 完成后更新部署历史

### 问题排查
1. 查看标准流程的错误处理
2. 检查部署日志
3. 联系技术支持

---

**文档版本**: v1.0
**创建时间**: 2026-02-22
**维护**: 自动化部署系统
**状态**: ✅ 已完成

---

## 🔗 快速链接

- [标准部署流程](./STANDARD_DEPLOYMENT_PROCESS.md)
- [快速参考卡片](./DEPLOY_QUICK_REFERENCE.md)
- [部署历史记录](./deploy_archive/DEPLOYMENT_HISTORY.md)
- [一键部署脚本](./deploy_one_click.sh)

---

**重要**: 所有部署必须严格按照标准流程执行，不得擅自修改！
