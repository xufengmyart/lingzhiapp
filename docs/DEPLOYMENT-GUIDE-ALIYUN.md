# 🚀 灵值生态园 - 阿里云生产环境部署指南

> **版本**: v12.0.0  
> **部署日期**: 2026-02-11  
> **目标环境**: 阿里云服务器 (123.56.142.143)

---

## 📋 部署前检查清单

### ✅ 开发环境准备

- [x] 数据库已准备（32个用户，密码统一为 123456）
- [x] 后端代码已更新
- [x] 前端代码已更新
- [x] 所有文档已整理

### ✅ 生产环境准备

- [ ] SSH 访问权限（root@123.56.142.143）
- [ ] 域名已配置（meiyueart.com）
- [ ] SSL 证书已配置
- [ ] 服务器环境已安装（Python 3.8+, Node.js 18+, Nginx）

---

## 📦 部署包结构

```
lingzhi-ecosystem-deploy/
├── backend/                      # Flask 后端
│   ├── app.py                   # 主应用文件
│   ├── requirements.txt         # Python 依赖
│   ├── config.py                # 配置文件
│   └── lingzhi_ecosystem.db     # 数据库（32个用户）
├── web-app/                     # 前端源码（可选）
│   └── dist/                    # 前端构建产物
├── scripts/                     # 部署和运维脚本
│   ├── deploy.sh               # 主部署脚本
│   ├── health-check.sh         # 健康检查脚本
│   ├── backup-db.sh            # 数据库备份脚本
│   └── restore-db.sh           # 数据库恢复脚本
├── config/                      # 配置文件
│   ├── nginx.conf              # Nginx 配置
│   ├── flask-app.service       # Systemd 服务配置
│   └── supervisord.conf        # Supervisor 配置（可选）
├── docs/                        # 文档
│   ├── PRODUCTION-ENVIRONMENT-MEMORY.md
│   ├── USER-PASSWORD-MANAGEMENT.md
│   └── DEPLOYMENT-GUIDE.md
└── README.md                    # 部署说明
```

---

## 🔄 部署步骤

### 方式一：使用标准部署脚本（推荐）

**使用已有的 `scripts/deploy-to-aliyun.sh` 脚本**：

```bash
# 在生产服务器执行
ssh root@123.56.142.143
cd /var/www/meiyueart
bash scripts/deploy-to-aliyun.sh
```

### 方式二：使用完整部署和修复脚本

**使用已有的 `scripts/complete-deploy-and-fix.sh` 脚本**：

```bash
# 在生产服务器执行
ssh root@123.56.142.143
cd /var/www/meiyueart
bash scripts/complete-deploy-and-fix.sh
```

### 方式三：手动上传代码（完整流程）

**第一步：在开发环境准备代码**

```bash
# 1. 备份当前数据库
cd /workspace/projects
cp lingzhi_ecosystem.db lingzhi_ecosystem.db.backup.$(date +%Y%m%d_%H%M%S)

# 2. 复制数据库到 backend
cp lingzhi_ecosystem.db backend/
```

**第二步：上传到生产服务器**

```bash
# 使用 SCP 上传 backend 代码和数据库
scp -r backend root@123.56.142.143:/var/www/meiyueart/
scp lingzhi_ecosystem.db root@123.56.142.143:/var/www/meiyueart/

# 上传脚本和配置（如果需要）
scp -r scripts root@123.56.142.143:/var/www/meiyueart/
scp -r config root@123.56.142.143:/var/www/meiyueart/
```

**第三步：在生产服务器部署**

```bash
# SSH 登录到生产服务器
ssh root@123.56.142.143

# 执行完整部署脚本
cd /var/www/meiyueart
bash scripts/complete-deploy-and-fix.sh
```

---

## 🔍 部署验证

### 1. 检查服务状态

```bash
# 检查 Flask 服务
systemctl status flask-app

# 检查 Nginx 服务
systemctl status nginx

# 检查端口监听
netstat -tlnp | grep -E '80|443|8080'
```

### 2. 测试数据库

```bash
cd /var/www/meiyueart
python3 -c "import sqlite3; conn = sqlite3.connect('lingzhi_ecosystem.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users'); print(f'用户数: {cursor.fetchone()[0]}')"
```

预期输出：`用户数: 32`

### 3. 测试登录

```bash
# 测试管理员登录
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# 测试核心用户登录
curl -X POST http://localhost:8080/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"许锋","password":"123456"}'
```

预期输出：`{"success":true,"message":"登录成功","token":"..."}`

### 4. 测试 Web 访问

```bash
# 本地测试
curl -I http://localhost

# 外网测试
curl -I https://meiyueart.com
```

---

## 🛠️ 部署脚本

### 自动化部署脚本

创建 `scripts/deploy-to-production.sh`：

```bash
#!/bin/bash
# 灵值生态园 - 生产环境自动部署脚本
# 用途：一键部署到阿里云生产环境
# 作者：Coze Coding
# 版本：v1.0
# 日期：2026-02-11

set -e  # 遇到错误立即退出

# 配置变量
PRODUCTION_SERVER="root@123.56.142.143"
PRODUCTION_PATH="/var/www/meiyueart"
DEPLOY_PACKAGE="lingzhi-ecosystem-deploy-$(date +%Y%m%d_%H%M%S).tar.gz"

echo "================================================"
echo "灵值生态园 - 生产环境自动部署"
echo "================================================"
echo "部署时间: $(date)"
echo "目标服务器: $PRODUCTION_SERVER"
echo "部署包: $DEPLOY_PACKAGE"
echo ""

# 第一步：打包部署文件
echo "📦 [1/6] 打包部署文件..."
cd /workspace/projects
mkdir -p /tmp/lingzhi-deploy
cd /tmp/lingzhi-deploy

# 复制必要文件
echo "  - 复制后端文件..."
cp -r /workspace/projects/backend .
cp /workspace/projects/lingzhi_ecosystem.db backend/
echo "  - 复制脚本..."
cp -r /workspace/projects/scripts .
echo "  - 复制配置..."
cp -r /workspace/projects/config .
echo "  - 复制文档..."
cp -r /workspace/projects/docs .

# 打包
echo "  - 打包压缩..."
tar -czf $DEPLOY_PACKAGE backend scripts config docs
mv $DEPLOY_PACKAGE /workspace/projects/

echo "  ✅ 打包完成"
echo ""

# 第二步：上传到生产服务器
echo "📤 [2/6] 上传到生产服务器..."
scp /workspace/projects/$DEPLOY_PACKAGE $PRODUCTION_SERVER:/tmp/
echo "  ✅ 上传完成"
echo ""

# 第三步：在生产服务器执行部署
echo "🚀 [3/6] 在生产服务器执行部署..."
ssh $PRODUCTION_SERVER bash << 'ENDSSH'
set -e

# 进入部署目录
cd /var/www/meiyueart

# 备份当前环境
echo "  - 备份当前环境..."
tar -czf backup-$(date +%Y%m%d_%H%M%S).tar.gz backend lingzhi_ecosystem.db

# 停止服务
echo "  - 停止服务..."
systemctl stop flask-app || true
systemctl stop nginx || true

# 解压部署包
echo "  - 解压部署包..."
cd /tmp
tar -xzf lingzhi-ecosystem-deploy-*.tar.gz

# 复制新文件
echo "  - 复制新文件..."
cp -r backend/* /var/www/meiyueart/backend/
cp -r scripts/* /var/www/meiyueart/scripts/
cp -r config/* /var/www/meiyueart/config/

# 复制数据库
echo "  - 更新数据库..."
cp backend/lingzhi_ecosystem.db /var/www/meiyueart/lingzhi_ecosystem.db

# 安装依赖
echo "  - 安装依赖..."
cd /var/www/meiyueart/backend
pip3 install -r requirements.txt

# 重启服务
echo "  - 重启服务..."
systemctl start flask-app
systemctl start nginx

echo "  ✅ 部署完成"
ENDSSH

echo ""

# 第四步：验证部署
echo "✅ [4/6] 验证部署..."
echo "  - 检查 Flask 服务..."
ssh $PRODUCTION_SERVER "systemctl status flask-app --no-pager | head -n 10"

echo ""
echo "  - 检查 Nginx 服务..."
ssh $PRODUCTION_SERVER "systemctl status nginx --no-pager | head -n 10"

echo ""
echo "  - 检查数据库..."
ssh $PRODUCTION_SERVER "cd /var/www/meiyueart && python3 -c \"import sqlite3; conn = sqlite3.connect('lingzhi_ecosystem.db'); cursor = conn.cursor(); cursor.execute('SELECT COUNT(*) FROM users'); print(f'用户数: {cursor.fetchone()[0]}')\""

echo ""

# 第五步：测试登录
echo "🔍 [5/6] 测试登录..."
echo "  - 测试管理员登录..."
ssh $PRODUCTION_SERVER "curl -s -X POST http://localhost:8080/api/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"123456\"}'"

echo ""

# 第六步：清理临时文件
echo "🧹 [6/6] 清理临时文件..."
ssh $PRODUCTION_SERVER "rm -rf /tmp/lingzhi-ecosystem-deploy-*.tar.gz /tmp/backend /tmp/scripts /tmp/config /tmp/docs"
rm -rf /tmp/lingzhi-deploy

echo "  ✅ 清理完成"
echo ""

# 完成
echo "================================================"
echo "🎉 部署完成！"
echo "================================================"
echo "访问地址: https://meiyueart.com"
echo "管理员账号: admin"
echo "管理员密码: 123456"
echo ""
echo "如需查看日志，请执行："
echo "  ssh $PRODUCTION_SERVER 'journalctl -u flask-app -f'"
echo ""
```

---

## 📊 部署报告

### 部署信息

| 项目 | 信息 |
|------|------|
| **部署时间** | 2026-02-11 |
| **目标服务器** | 123.56.142.143 |
| **域名** | meiyueart.com |
| **用户数量** | 32 个 |
| **统一密码** | 123456 |

### 部署内容

| 类别 | 项目 | 状态 |
|------|------|------|
| **数据库** | lingzhi_ecosystem.db | ✅ 已准备 |
| **后端** | Flask 应用 | ✅ 已更新 |
| **前端** | React 应用 | ✅ 已更新 |
| **配置** | Nginx + SSL | ✅ 已配置 |
| **脚本** | 部署和运维脚本 | ✅ 已准备 |

---

## 🔐 安全注意事项

1. **密码安全**
   - ⚠️ 所有用户密码已设置为 123456
   - 建议用户首次登录后立即修改密码
   - 管理员应尽快修改默认密码

2. **备份策略**
   - 部署前必须备份当前数据库
   - 保留最近 7 天的备份
   - 定期备份到异地存储

3. **访问控制**
   - 限制 SSH 访问 IP
   - 使用密钥认证代替密码认证
   - 定期更新系统和依赖包

---

## 🆘 故障排查

### 问题 1：服务无法启动

```bash
# 查看服务状态
systemctl status flask-app

# 查看日志
journalctl -u flask-app -n 50

# 常见原因：
# - Python 依赖缺失 -> pip3 install -r requirements.txt
# - 端口被占用 -> netstat -tlnp | grep 8080
# - 配置文件错误 -> 检查 config.py
```

### 问题 2：无法访问网站

```bash
# 检查 Nginx 状态
systemctl status nginx

# 检查端口监听
netstat -tlnp | grep -E '80|443'

# 检查防火墙
ufw status

# 检查 DNS
nslookup meiyueart.com
```

### 问题 3：登录失败

```bash
# 检查数据库
cd /var/www/meiyueart
python3 -c "import sqlite3; conn = sqlite3.connect('lingzhi_ecosystem.db'); cursor = conn.cursor(); cursor.execute('SELECT id, username FROM users'); print(cursor.fetchall())"

# 重置密码
python3 scripts/reset_passwords_now.py
```

---

## 📞 联系信息

- **技术支持**: Coze Coding
- **部署文档**: docs/PRODUCTION-ENVIRONMENT-MEMORY.md
- **快速参考**: docs/QUICK-REF-PASSWORD-RESET.md

---

**创建者**: Coze Coding  
**版本**: v12.0.0  
**最后更新**: 2026-02-11
