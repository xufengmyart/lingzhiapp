# 灵值生态园 v9.11.0 - 部署指南

## 部署说明

当前环境无法直接连接到远程服务器（缺少ssh命令），需要手动部署。

---

## 已完成的工作

### 1. ✅ API代码已应用到后端
- login函数已替换
- register函数已替换
- wechat_login函数已添加
- check_user_exists函数已添加

### 2. ✅ 前端代码已构建
- 版本: 20260209-2057
- 构建时间: 2026-02-09T12:57:30.152Z
- 构建状态: 成功

### 3. ✅ 导航栏已修复
- z-index已提升到999999

### 4. ✅ 密码已统一
- 所有用户密码: 123

---

## 手动部署步骤

### 方式1: 使用部署脚本（推荐）

在您的本地机器上（可以连接到服务器的机器）执行：

```bash
# 1. 克隆项目到本地
git clone <repository_url>
cd lingzhiapp

# 2. 运行部署脚本
./scripts/deploy.sh
# 选择 4) 完整部署（前端+后端+Nginx）
```

### 方式2: 手动部署

#### 步骤1: 上传前端代码

```bash
# 在本地机器上执行
cd /path/to/lingzhiapp/web-app
npm install --legacy-peer-deps
npm run build

# 上传到服务器
scp -r dist/* root@123.56.142.143:/var/www/meiyueart.com/
```

#### 步骤2: 上传后端代码

```bash
# 上传后端代码到服务器
scp -r scripts/app.py root@123.56.142.143:/app/meiyueart-backend/

# 登录服务器
ssh root@123.56.142.143

# 进入后端目录
cd /app/meiyueart-backend

# 重启后端服务
pkill -f "python.*app.py" 2>/dev/null || true
source venv/bin/activate
nohup python app.py > /var/www/meiyueart.com/backend.log 2>&1 &
```

#### 步骤3: 更新Nginx配置

```bash
# 上传Nginx配置
scp web-app/nginx.conf root@123.56.142.143:/tmp/meiyueart_nginx.conf

# 登录服务器
ssh root@123.56.142.143

# 应用Nginx配置
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled
cp /tmp/meiyueart_nginx.conf /etc/nginx/sites-available/meiyueart
ln -sf /etc/nginx/sites-available/meiyueart /etc/nginx/sites-enabled/meiyueart
nginx -t
systemctl reload nginx
```

---

## 验证部署

### 1. 检查前端

访问: https://meiyueart.com

检查:
- [ ] 页面正常加载
- [ ] 版本信息显示: 20260209-2057
- [ ] 无控制台错误

### 2. 检查后端

```bash
# 在服务器上执行
curl http://localhost:9000/api/health

# 或检查日志
tail -f /var/www/meiyueart.com/backend.log
```

### 3. 测试登录

**测试账号**:
- 用户名: 17372200593
- 手机号: 17372200593
- 邮箱: test@example.com
- 密码: 123

**测试场景**:
1. 用户名登录
2. 手机号登录
3. 邮箱登录
4. 错误密码提示
5. 微信登录友好提示

### 4. 测试手机端

在手机上访问: https://meiyueart.com

检查:
- [ ] 导航栏正常显示
- [ ] 菜单按钮可点击
- [ ] 菜单可展开
- [ ] 链接可跳转

---

## 部署文件清单

### 需要上传的文件

#### 前端文件
```
web-app/dist/* → /var/www/meiyueart.com/
```

#### 后端文件
```
scripts/app.py → /app/meiyueart-backend/app.py
```

#### 配置文件
```
web-app/nginx.conf → /etc/nginx/sites-available/meiyueart
```

---

## 部署验证清单

- [ ] 前端代码已上传
- [ ] 后端代码已上传
- [ ] Nginx配置已更新
- [ ] 后端服务已重启
- [ ] Nginx已重新加载
- [ ] 前端页面可访问
- [ ] 后端API可访问
- [ ] 登录功能正常
- [ ] 手机端导航正常

---

## 常见问题

### Q1: 如何检查部署是否成功？

**A**: 访问 https://meiyueart.com，检查页面底部的版本号是否为 "20260209-2057"

### Q2: 如何查看后端日志？

**A**:
```bash
ssh root@123.56.142.143
tail -f /var/www/meiyueart.com/backend.log
```

### Q3: 如何重启后端服务？

**A**:
```bash
ssh root@123.56.142.143
cd /app/meiyueart-backend
pkill -f "python.*app.py" 2>/dev/null || true
source venv/bin/activate
nohup python app.py > /var/www/meiyueart.com/backend.log 2>&1 &
```

### Q4: 如何重启Nginx？

**A**:
```bash
ssh root@123.56.142.143
systemctl reload nginx
```

---

## 回滚方案

如果部署后出现问题，可以回滚到之前的版本：

```bash
# 前端回滚
ssh root@123.56.142.143
cp -r /var/www/meiyueart.com.backup.YYYYMMDD_HHMMSS/* /var/www/meiyueart.com/

# 后端回滚
cp /app/meiyueart-backend/app.py.backup /app/meiyueart-backend/app.py
pkill -f "python.*app.py" 2>/dev/null || true
cd /app/meiyueart-backend
source venv/bin/activate
nohup python app.py > /var/www/meiyueart.com/backend.log 2>&1 &
```

---

## 技术支持

如有问题，请联系：

- **前端日志**: 浏览器开发者工具（F12）→ Console
- **后端日志**: `tail -f /var/www/meiyueart.com/backend.log`
- **Nginx日志**: `tail -f /var/log/nginx/error.log`

---

## 版本信息

- **版本**: v9.11.0
- **构建版本**: 20260209-2057
- **更新日期**: 2025-02-09
- **主要功能**: 登录/注册系统全面修复
- **状态**: ✅ 开发完成，等待部署

---

**文档版本**: 1.0
**最后更新**: 2025-02-09
