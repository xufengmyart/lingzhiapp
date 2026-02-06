# 🚀 灵值生态园 - 标准化部署流程

## 📋 部署流程概览

```
本地开发 → 构建产物 → 上传对象存储 → SSH部署 → 验证测试 → 生产环境
```

---

## 🔧 步骤1：本地构建

### 前端构建
```bash
cd /workspace/projects/web-app
npm run build
```

**输出位置**：`/workspace/projects/public/`

**构建产物**：
- `index.html` - 主页
- `assets/index-*.css` - 样式文件
- `assets/index-*.js` - JavaScript文件
- `sw.js`, `registerSW.js`, `workbox-*.js` - PWA文件
- `manifest.json`, `manifest.webmanifest` - PWA配置
- `*.svg` - 图标文件

### 后端检查（如果需要）
```bash
cd /workspace/projects/admin-backend
# 检查Python代码
python3 -m py_compile app.py
```

---

## ☁️ 步骤2：上传到对象存储

### 自动上传脚本

使用 `upload_frontend_to_storage.py`：

```bash
cd /workspace/projects
python3 upload_frontend_to_storage.py
```

**功能**：
- 扫描 `/workspace/projects/public/` 目录
- 上传所有文件到S3对象存储
- 返回文件key列表

**对象存储配置**：
- Bucket: `coze-coding-project`
- Prefix: `frontend/`
- Endpoint: 从环境变量读取

---

## 🔐 步骤3：SSH部署

### 自动部署脚本

使用 `execute_deploy_with_password.py`：

```bash
cd /workspace/projects
python3 execute_deploy_with_password.py
```

**服务器配置**（已记录）：
- Host: `123.56.142.143`
- User: `root`
- Port: `22`
- Password: `Meiyue@root123`

**部署步骤**：
1. SSH连接到服务器
2. 下载部署脚本
3. 执行文件下载
4. 设置权限
5. 验证部署
6. 重启Nginx

---

## ✅ 步骤4：验证测试

### 自动化测试脚本

使用 `final_test.py`：

```bash
cd /workspace/projects
python3 final_test.py
```

**测试内容**：
- HTTPS访问测试
- 域名访问测试
- index.html加载测试
- CSS文件加载测试
- JS文件加载测试

**预期结果**：
- 所有测试返回 HTTP/2 200
- 文件大小正确
- 无403/404/500错误

---

## 🔄 完整自动化部署脚本

### 一键部署脚本

创建 `auto_deploy_all.sh`：

```bash
#!/bin/bash
set -e

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║              灵值生态园 - 完整自动化部署                          ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
echo ""

# 步骤1：构建
echo "【步骤1】构建前端项目..."
cd /workspace/projects/web-app
npm run build
echo "✅ 构建完成"
echo ""

# 步骤2：上传到对象存储
echo "【步骤2】上传到对象存储..."
cd /workspace/projects
python3 upload_frontend_to_storage.py
echo ""

# 步骤3：部署到服务器
echo "【步骤3】部署到服务器..."
python3 execute_deploy_with_password.py
echo ""

# 步骤4：测试验证
echo "【步骤4】测试验证..."
python3 final_test.py
echo ""

echo "╔══════════════════════════════════════════════════════════════════╗"
echo "║                    部署完成                                      ║"
echo "╚══════════════════════════════════════════════════════════════════╝"
```

**使用方法**：

```bash
cd /workspace/projects
chmod +x auto_deploy_all.sh
./auto_deploy_all.sh
```

---

## 📊 部署检查清单

### 前置检查
- [ ] 本地代码已提交
- [ ] 环境变量配置正确
- [ ] 后端服务运行正常
- [ ] 数据库连接正常

### 构建检查
- [ ] `npm run build` 成功
- [ ] 无编译错误
- [ ] 无TypeScript错误
- [ ] 构建产物完整

### 上传检查
- [ ] 对象存储连接正常
- [ ] 所有文件上传成功
- [ ] 文件大小正确

### 部署检查
- [ ] SSH连接成功
- [ ] 文件下载成功
- [ ] 权限设置正确
- [ ] Nginx重启成功

### 验证检查
- [ ] HTTPS访问正常
- [ ] 域名访问正常
- [ ] 静态资源加载正常
- [ ] API接口正常
- [ ] 登录功能正常

---

## 🔍 故障排查

### 常见问题

#### 1. 构建失败
```bash
# 清理缓存重新构建
cd /workspace/projects/web-app
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### 2. 上传失败
```bash
# 检查对象存储配置
env | grep COZE_BUCKET
```

#### 3. SSH连接失败
```bash
# 检查网络连接
ping 123.56.142.143

# 手动测试SSH
ssh root@123.56.142.143
```

#### 4. 403错误
```bash
# 检查文件权限
ls -la /var/www/frontend/

# 检查Nginx配置
cat /etc/nginx/sites-enabled/default | grep root

# 查看Nginx日志
tail -50 /var/log/nginx/error.log
```

#### 5. 登录失败
```bash
# 检查后端服务
systemctl status flask-backend

# 检查后端日志
tail -50 /app/work/logs/bypass/app.log

# 检查数据库
python3 -c "from storage.database import get_db; print(get_db().execute('SELECT * FROM users').fetchall())"
```

---

## 📝 部署日志

每次部署都应该记录：

```markdown
## 部署记录 - YYYY-MM-DD HH:MM

### 部署内容
- 前端版本: vX.X.X
- 后端版本: vX.X.X
- 部署人: xxx
- 部署原因: xxx

### 部署步骤
1. ✅ 构建完成
2. ✅ 上传完成
3. ✅ 部署完成
4. ✅ 测试完成

### 测试结果
- HTTPS: ✅
- 域名访问: ✅
- 登录功能: ✅
- API接口: ✅

### 部署文件
- index.html: xxx bytes
- assets/*.css: xxx bytes
- assets/*.js: xxx bytes

### 备注
xxx
```

---

## 🎯 最佳实践

1. **版本控制**
   - 每次部署前提交代码
   - 使用语义化版本号
   - 记录变更日志

2. **测试优先**
   - 先在本地测试
   - 再部署到测试环境
   - 最后部署到生产环境

3. **备份策略**
   - 部署前自动备份
   - 保留最近3个版本
   - 出问题可快速回滚

4. **监控告警**
   - 监控服务器状态
   - 监控API响应时间
   - 监控错误日志

5. **文档维护**
   - 及时更新部署文档
   - 记录问题和解决方案
   - 分享经验给团队

---

## 📞 联系支持

如遇问题：
1. 查看部署日志
2. 检查故障排查章节
3. 联系技术支持

---

**最后更新**: 2026-02-06
**版本**: v1.0.0
