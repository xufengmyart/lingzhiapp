# 版本回滚流程
## 流程版本: v2.0
## 基于版本: 7140912
## 创建日期: 2026-02-15

---

## 📋 流程概述

### 目标
确保在部署失败或出现严重问题时，能够快速、安全地回滚到上一个稳定版本。

### 原则
1. **快速响应**: 发现问题后立即启动回滚流程
2. **安全第一**: 回滚过程中优先保证数据安全
3. **完整回滚**: 回滚必须完整，不能部分回滚
4. **验证优先**: 回滚后必须立即验证
5. **记录完整**: 所有回滚操作必须记录

---

## 🚨 回滚触发条件

### 自动触发条件
- [ ] 关键功能不可用（登录、支付等）
- [ ] 数据库错误导致无法访问
- [ ] 安全漏洞被确认
- [ ] 性能严重下降（响应时间 > 10s）
- [ ] 错误率超过 10%

### 手动触发条件
- [ ] 用户反馈严重问题
- [ ] 监控发现异常
- [ ] 代码审查发现严重问题
- [ ] 测试未通过但已部署

---

## 🔄 回滚类型

### 类型 1: 前端回滚
**适用场景**: 前端页面错误、样式问题、功能异常

**回滚时间**: 约 2 分钟

**影响范围**: 前端界面

### 类型 2: 后端回滚
**适用场景**: 后端 API 错误、逻辑错误、服务不可用

**回滚时间**: 约 3 分钟

**影响范围**: 后端 API、业务逻辑

### 类型 3: 数据库回滚
**适用场景**: 数据库错误、数据丢失、数据不一致

**回滚时间**: 约 5 分钟

**影响范围**: 数据库、数据

### 类型 4: 全量回滚
**适用场景**: 前后端同时出现问题、重大版本问题

**回滚时间**: 约 10 分钟

**影响范围**: 全系统

---

## 📝 回滚流程（标准化）

### 阶段 1: 问题确认

#### 1.1 问题诊断
```bash
# 检查服务状态
curl https://meiyueart.com/api/health

# 检查错误日志
ssh root@123.56.142.143 "tail -50 /opt/lingzhi-ecosystem/backend/server.log"

# 检查数据库
ssh root@123.56.142.143 "ls -lh /opt/lingzhi-ecosystem/backend/lingzhi_ecosystem.db"
```

#### 1.2 影响评估
- [ ] 确认问题范围（前端/后端/数据库）
- [ ] 评估影响程度（轻微/严重/紧急）
- [ ] 确认是否需要回滚
- [ ] 评估回滚风险

#### 1.3 决策记录
```bash
# 记录回滚决策
cat > ROLLBACK_LOG_$(date +%Y%m%d_%H%M%S).md << 'EOF'
# 回滚日志
## 时间: $(date +%Y-%m-%d %H:%M:%S)
## 回滚原因:
## 问题描述:
## 影响范围:
## 决策人:
EOF
```

---

### 阶段 2: 回滚准备

#### 2.1 确认备份
```bash
# 查看可用的备份
ssh root@123.56.142.143 << 'EOF'
ls -lh /var/www/meiyueart.com/ | grep backup
ls -lh /opt/lingzhi-ecosystem/backend/ | grep backup
ls -lh /opt/lingzhi-ecosystem/backend/lingzhi_ecosystem.db.*
EOF
```

#### 2.2 选择备份
```bash
# 选择最新的稳定备份
BACKUP_DATE="YYYYMMDD_HHMMSS"

# 确认备份完整
ssh root@123.56.142.143 << 'EOF'
ls -lh /var/www/meiyueart.com/backup_$BACKUP_DATE
ls -lh /opt/lingzhi-ecosystem/backend/backup_$BACKUP_DATE
EOF
```

#### 2.3 通知相关人员
```bash
# 发送回滚通知
echo "开始回滚！时间: $(date)，备份: $BACKUP_DATE" | mail -s "回滚通知" team@example.com
```

---

### 阶段 3: 执行回滚

#### 3.1 前端回滚（如需要）
```bash
ssh root@123.56.142.143 << 'EOF'
BACKUP_DATE="YYYYMMDD_HHMMSS"

# 停止服务
systemctl stop nginx

# 恢复文件
cp -r /var/www/meiyueart.com/backup_$BACKUP_DATE/* /var/www/meiyueart.com/

# 启动服务
systemctl start nginx

# 验证服务
systemctl status nginx
EOF
```

#### 3.2 后端回滚（如需要）
```bash
ssh root@123.56.142.143 << 'EOF'
BACKUP_DIR="backup_YYYYMMDD_HHMMSS"

# 停止服务
cd /opt/lingzhi-ecosystem/backend
pkill -f gunicorn

# 恢复文件
cp $BACKUP_DIR/* ./

# 启动服务
source venv/bin/activate
nohup gunicorn -w 1 -b 0.0.0.0:8080 app:app > server.log 2>&1 &

# 验证服务
sleep 3
ps aux | grep gunicorn | grep -v grep
EOF
```

#### 3.3 数据库回滚（如需要）
```bash
ssh root@123.56.142.143 << 'EOF'
BACKUP_DATE="YYYYMMDD_HHMMSS"

# 停止服务
cd /opt/lingzhi-ecosystem/backend
pkill -f gunicorn

# 恢复数据库
cp lingzhi_ecosystem.db.backup_$BACKUP_DATE lingzhi_ecosystem.db

# 启动服务
source venv/bin/activate
nohup gunicorn -w 1 -b 0.0.0.0:8080 app:app > server.log 2>&1 &

# 验证服务
sleep 3
ps aux | grep gunicorn | grep -v grep
EOF
```

---

### 阶段 4: 验证回滚

#### 4.1 健康检查
```bash
# 检查前端
curl -I https://meiyueart.com
# 期望: 200 OK

# 检查后端
curl https://meiyueart.com/api/health
# 期望: {"status": "ok"}

# 检查数据库
curl https://meiyueart.com/api/user/info
# 期望: 正常响应
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

### 阶段 5: 记录回滚

#### 5.1 更新回滚日志
```bash
cat >> ROLLBACK_LOG_$(date +%Y%m%d_%H%M%S).md << 'EOF'

## 回滚完成
- 回滚时间: $(date +%Y-%m-%d %H:%M:%S)
- 回滚备份: $BACKUP_DIR
- 回滚状态: ✅ 成功

## 验证结果
- 健康检查: ✅ 通过
- 功能验证: ✅ 通过
- 服务状态: ✅ 正常

## 问题分析
(分析回滚原因和根本原因)

## 预防措施
(提出预防类似问题的措施)
EOF
```

#### 5.2 通知相关人员
```bash
# 发送回滚完成通知
echo "回滚完成！时间: $(date)，备份: $BACKUP_DIR" | mail -s "回滚完成通知" team@example.com
```

---

## 🔧 回滚脚本

### 前端回滚脚本
```bash
#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
SERVER="root@123.56.142.143"
PASSWORD="Meiyue@root123"
BACKUP_DATE="${1:-$(date +%Y%m%d_%H%M%S)}"

echo "========================================="
echo "前端回滚脚本"
echo "========================================="
echo ""

# 确认回滚
echo -e "${YELLOW}确认要回滚前端到 $BACKUP_DATE 吗？(y/n)${NC}"
read -r confirm

if [ "$confirm" != "y" ]; then
    echo "回滚已取消"
    exit 0
fi

# 执行回滚
echo -e "${YELLOW}开始回滚前端...${NC}"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << EOF
echo "1. 停止 Nginx 服务..."
systemctl stop nginx

echo "2. 恢复前端文件..."
cp -r /var/www/meiyueart.com/backup_$BACKUP_DATE/* /var/www/meiyueart.com/

echo "3. 启动 Nginx 服务..."
systemctl start nginx

echo "4. 验证服务..."
systemctl status nginx
EOF

# 验证回滚
echo ""
echo -e "${YELLOW}验证回滚结果...${NC}"
sleep 2

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://meiyueart.com)
if [ "$HEALTH_CHECK" == "200" ]; then
    echo -e "${GREEN}✓ 回滚成功！${NC}"
else
    echo -e "${RED}✗ 回滚失败！HTTP 状态码: $HEALTH_CHECK${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo -e "${GREEN}✅ 前端回滚完成！${NC}"
echo "========================================="
```

### 后端回滚脚本
```bash
#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
SERVER="root@123.56.142.143"
PASSWORD="Meiyue@root123"
BACKUP_DIR="${1:-backup_$(date +%Y%m%d_%H%M%S)}"

echo "========================================="
echo "后端回滚脚本"
echo "========================================="
echo ""

# 确认回滚
echo -e "${YELLOW}确认要回滚后端到 $BACKUP_DIR 吗？(y/n)${NC}"
read -r confirm

if [ "$confirm" != "y" ]; then
    echo "回滚已取消"
    exit 0
fi

# 执行回滚
echo -e "${YELLOW}开始回滚后端...${NC}"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << EOF
cd /opt/lingzhi-ecosystem/backend

echo "1. 停止 Gunicorn 服务..."
pkill -f gunicorn
sleep 2

echo "2. 恢复后端文件..."
cp $BACKUP_DIR/* ./

echo "3. 启动 Gunicorn 服务..."
source venv/bin/activate
nohup gunicorn -w 1 -b 0.0.0.0:8080 app:app > server.log 2>&1 &
sleep 3

echo "4. 验证服务..."
ps aux | grep gunicorn | grep -v grep
EOF

# 验证回滚
echo ""
echo -e "${YELLOW}验证回滚结果...${NC}"
sleep 2

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://meiyueart.com/api/health)
if [ "$HEALTH_CHECK" == "200" ]; then
    echo -e "${GREEN}✓ 回滚成功！${NC}"
else
    echo -e "${RED}✗ 回滚失败！HTTP 状态码: $HEALTH_CHECK${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo -e "${GREEN}✅ 后端回滚完成！${NC}"
echo "========================================="
```

### 数据库回滚脚本
```bash
#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 配置
SERVER="root@123.56.142.143"
PASSWORD="Meiyue@root123"
BACKUP_DATE="${1:-$(date +%Y%m%d_%H%M%S)}"

echo "========================================="
echo "数据库回滚脚本"
echo "========================================="
echo ""

# 确认回滚
echo -e "${YELLOW}⚠️  数据库回滚会丢失所有数据！确认要回滚吗？(y/n)${NC}"
read -r confirm

if [ "$confirm" != "y" ]; then
    echo "回滚已取消"
    exit 0
fi

# 二次确认
echo -e "${RED}⚠️  最后确认：真的要回滚数据库吗？(yes/no)${NC}"
read -r confirm2

if [ "$confirm2" != "yes" ]; then
    echo "回滚已取消"
    exit 0
fi

# 执行回滚
echo -e "${YELLOW}开始回滚数据库...${NC}"
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no $SERVER << EOF
cd /opt/lingzhi-ecosystem/backend

echo "1. 停止 Gunicorn 服务..."
pkill -f gunicorn
sleep 2

echo "2. 备份当前数据库..."
cp lingzhi_ecosystem.db lingzhi_ecosystem.db.before_rollback_$(date +%Y%m%d_%H%M%S)

echo "3. 恢复数据库..."
cp lingzhi_ecosystem.db.backup_$BACKUP_DATE lingzhi_ecosystem.db

echo "4. 启动 Gunicorn 服务..."
source venv/bin/activate
nohup gunicorn -w 1 -b 0.0.0.0:8080 app:app > server.log 2>&1 &
sleep 3

echo "5. 验证服务..."
ps aux | grep gunicorn | grep -v grep
EOF

# 验证回滚
echo ""
echo -e "${YELLOW}验证回滚结果...${NC}"
sleep 2

HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://meiyueart.com/api/health)
if [ "$HEALTH_CHECK" == "200" ]; then
    echo -e "${GREEN}✓ 回滚成功！${NC}"
else
    echo -e "${RED}✗ 回滚失败！HTTP 状态码: $HEALTH_CHECK${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo -e "${GREEN}✅ 数据库回滚完成！${NC}"
echo "========================================="
```

---

## 📊 回滚监控

### 回滚指标
1. **回滚时间**: 前端 < 2min，后端 < 3min，数据库 < 5min
2. **回滚成功率**: > 95%
3. **回滚后恢复时间**: < 5min
4. **数据丢失率**: < 1%

### 回滚统计
- [ ] 回滚次数统计
- [ ] 回滚原因分析
- [ ] 回滚时间统计
- [ ] 回滚成功率统计

---

## 📞 应急联系

### 技术支持
- **维护者**: Coze Coding
- **邮箱**: support@meiyueart.com
- **紧急联系**: https://meiyueart.com/support

### 应急流程
1. 立即停止部署（如正在部署）
2. 确认问题范围和严重程度
3. 选择合适的回滚类型
4. 执行回滚脚本
5. 验证回滚结果
6. 通知相关人员

---

## 📚 相关文档

- [版本档案](./VERSION_7140912_ARCHIVE.md)
- [标准化部署流程](./STANDARD_DEPLOYMENT_PROCESS.md)
- [部署检查清单](./DEPLOYMENT_CHECKLIST.md)
- [部署习惯档案](./DEPLOYMENT_HABITS_ARCHIVE.md)

---

## ✅ 流程确认

### 回滚检查清单
- [x] 问题已确认
- [x] 备份已验证
- [x] 回滚已执行
- [x] 验证已通过
- [x] 日志已记录
- [x] 相关人员已通知

---

**版本回滚流程 v2.0**

**基于版本**: 7140912
**创建日期**: 2026-02-15
**流程状态**: ✅ 已确认

**维护者**: Coze Coding
**最后更新**: 2026-02-15 11:53
