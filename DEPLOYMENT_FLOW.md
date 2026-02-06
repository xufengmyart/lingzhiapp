# 灵值生态园 - 标准部署流程文档

## 📋 概述

本文档定义了从开发环境到生产环境的标准部署流程，确保每次部署的一致性和可靠性。

---

## 🔧 服务器配置

```yaml
服务器IP: 123.56.142.143
SSH用户: root
SSH端口: 22
前端目录: /var/www/frontend
后端目录: /root/lingzhi-ecosystem/admin-backend
后端端口: 8001
Web服务器: Nginx 1.24.0
```

---

## 🚀 标准部署流程

### 步骤1：本地构建前端

```bash
cd /workspace/projects/web-app
npm run build
```

**输出位置**：`/workspace/projects/public/`

**关键文件**：
- `index.html` - 主页
- `assets/index-BI24OT2H.css` - 样式文件
- `assets/index-C_quYkQi.js` - JavaScript
- `sw.js`, `registerSW.js` - Service Worker
- `manifest.json`, `manifest.webmanifest` - PWA配置

---

### 步骤2：上传到对象存储

使用 `upload_frontend_to_storage.py` 脚本：

```bash
python3 upload_frontend_to_storage.py
```

这会将所有构建文件上传到S3对象存储。

---

### 步骤3：SSH部署到服务器

使用 `auto_deploy.py` 脚本自动部署：

```bash
python3 auto_deploy.py
```

**自动执行**：
1. SSH连接到服务器
2. 备份现有文件
3. 下载新文件
4. 设置权限
5. 重启Nginx

---

### 步骤4：验证部署

```bash
python3 verify_deployment.py
```

**验证项**：
- HTTPS访问状态
- 文件完整性
- 静态资源加载
- API连接

---

## 📝 部署脚本说明

### 1. `auto_deploy.py` - 自动部署脚本

功能：
- SSH连接
- 备份现有文件
- 下载并部署新文件
- 设置权限
- 重启Nginx
- 验证部署

### 2. `verify_deployment.py` - 验证脚本

功能：
- 测试HTTPS访问
- 检查文件完整性
- 验证静态资源
- 测试API连接

### 3. `rollback.py` - 回滚脚本

功能：
- 回滚到上一次备份
- 恢复Nginx配置

---

## 🔐 SSH认证信息

**已保存**：
- 用户名：root
- 密码：Meiyue@root123

**安全说明**：
- 密码仅用于自动部署脚本
- 不会在日志中输出
- 建议定期更换密码

---

## 📊 部署检查清单

部署前：
- [ ] 代码已提交到Git
- [ ] 本地测试通过
- [ ] 构建无错误
- [ ] 重要文件已备份

部署后：
- [ ] HTTPS访问正常
- [ ] 所有页面加载正常
- [ ] 静态资源加载正常
- [ ] API连接正常
- [ ] 登录功能正常
- [ ] 清除浏览器缓存后验证

---

## 🚨 常见问题

### 问题1：403 Forbidden

**原因**：文件不在正确位置

**解决**：
```bash
# SSH到服务器
ssh root@123.56.142.143

# 移动文件
cd /var/www/frontend
mv public/* ./
chmod -R 755 .
systemctl reload nginx
```

### 问题2：文件权限错误

**解决**：
```bash
chmod -R 755 /var/www/frontend
find /var/www/frontend -type f -exec chmod 644 {} \;
```

### 问题3：Nginx配置错误

**检查**：
```bash
nginx -t
```

**修复**：
```bash
systemctl reload nginx
```

---

## 📈 部署历史

| 日期 | 版本 | 描述 | 状态 |
|------|------|------|------|
| 2026-02-06 | v9.0 | 生态之梦风格，PWA支持 | ✅ |

---

## 🔄 自动化工作流

### 开发 → 测试 → 生产

```
开发环境
    ↓
本地测试
    ↓
构建前端 (npm run build)
    ↓
上传到对象存储
    ↓
SSH自动部署
    ↓
验证部署
    ↓
生产环境发布
```

---

## 📞 支持联系人

- 技术支持：Agent搭建专家
- 服务器：123.56.142.143
- 文档：DEPLOYMENT_FLOW.md

---

**最后更新**: 2026-02-06
