# 生产环境部署配置归档

**创建时间**: 2026-02-18
**状态**: ⚠️ SSH密钥缺失，需要配置

## 生产环境信息

```
域名: meiyueart.com
IP: 123.56.142.143
SSH: root@meiyueart.com:22
后端: /app/meiyueart-backend
前端: /var/www/meiyueart.com
```

## SSH配置

### 需要的配置文件
```bash
/root/.ssh/id_rsa          # 私钥
/root/.ssh/id_rsa.pub      # 公钥
/root/.ssh/config          # SSH配置
```

### 当前状态
- ❌ `/root/.ssh/id_rsa` - 不存在
- ❌ `/root/.ssh/id_rsa.pub` - 不存在
- ❌ `/root/.ssh/config` - 不存在

## 全自动部署脚本

### 脚本位置
```
/workspace/projects/admin-backend/auto_deploy.sh
```

### 脚本功能
- ✅ 检查SSH连接
- ✅ 检查本地环境
- ✅ 备份生产数据库
- ✅ 同步数据库到生产环境
- ✅ 重启生产服务
- ✅ 验证部署结果

### 脚本配置
```bash
PRODUCTION_SERVER="meiyueart.com"
PRODUCTION_USER="root"
PRODUCTION_PORT="22"
PRODUCTION_SSH_KEY="/root/.ssh/id_rsa"
```

## GitHub Actions配置

### Secrets配置（需要配置）
```
PRODUCTION_HOST=meiyueart.com
PRODUCTION_USER=root
SSH_PRIVATE_KEY=<私钥内容>
```

### Workflow文件
```
.github/workflows/deploy.yml
```

### 触发方式
```bash
# 提交到main分支自动触发
git add .
git commit -m "feat: xxx"
git push origin main
```

## 部署步骤（当前环境）

### 方法1：配置SSH密钥
```bash
# 1. 生成SSH密钥
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""

# 2. 添加公钥到生产服务器
ssh-copy-id -i ~/.ssh/id_rsa.pub root@meiyueart.com

# 3. 测试连接
ssh root@meiyueart.com "echo '连接成功'"

# 4. 执行部署
cd /workspace/projects
bash admin-backend/auto_deploy.sh
```

### 方法2：使用密码
```bash
# 使用sshpass和密码连接
sshpass -p '你的密码' ssh root@meiyueart.com "echo 'test'"

# 如果成功，修改auto_deploy.sh中的ssh命令
```

### 方法3：通过GitHub Actions
```bash
# 1. 配置GitHub secrets
#    - SSH_PRIVATE_KEY: 私钥内容
#    - PRODUCTION_HOST: meiyueart.com
#    - PRODUCTION_USER: root

# 2. 提交代码
git add .
git commit -m "feat: xxx"
git push origin main

# 3. 自动部署
```

## 待解决问题

### 问题1：SSH密钥缺失
- **描述**: `/root/.ssh/id_rsa` 不存在
- **影响**: 无法直接SSH连接到生产服务器
- **解决方案**:
  1. 生成新的SSH密钥对
  2. 将公钥添加到生产服务器的 `~/.ssh/authorized_keys`
  3. 使用GitHub secrets存储私钥

### 问题2：GitHub secrets未配置
- **描述**: GitHub Actions所需的secrets未配置
- **影响**: 无法通过CI/CD自动部署
- **解决方案**:
  1. 进入GitHub仓库的 Settings > Secrets
  2. 添加以下secrets:
     - `SSH_PRIVATE_KEY`: SSH私钥内容
     - `PRODUCTION_HOST`: meiyueart.com
     - `PRODUCTION_USER`: root

### 问题3：Agent系统LSP检查失败
- **描述**: `storage.database.check_in_manager` 导入无法识别
- **影响**: `test_run` 无法执行
- **状态**: ✅ 已修复（已创建 storage 目录结构）

## 之前成功的部署记录

根据Git历史，之前成功的部署包括：
- `21903aa` - 自动化部署到生产环境成功
- `9c6f95e` - 生产环境部署 v1.2.0 - 100%完成
- `62c8033` - 完成灵值生态园生产环境完整部署

这些部署可能通过以下方式完成：
1. SSH密钥认证
2. GitHub Actions
3. 手动部署

## 验证生产环境

```bash
# 健康检查
curl https://meiyueart.com/api/health

# 登录测试
curl -X POST https://meiyueart.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'
```

## 总结

- ✅ 部署脚本已准备：`admin-backend/auto_deploy.sh`
- ✅ 生产环境信息已确认
- ✅ GitHub Actions workflow已配置
- ⚠️ SSH密钥需要配置
- ⚠️ GitHub secrets需要配置

## 下一步行动

1. **配置SSH密钥**（推荐）
   - 生成SSH密钥对
   - 添加公钥到生产服务器
   - 测试SSH连接
   - 执行部署脚本

2. **配置GitHub Actions**（备选）
   - 添加GitHub secrets
   - 提交代码触发部署

3. **手动验证**
   - 测试生产环境API
   - 验证登录功能
   - 检查服务状态
