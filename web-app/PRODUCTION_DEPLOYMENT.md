# 生产环境部署指南

## 当前状态

- **生产环境 URL**: https://meiyueart.com
- **当前问题**: 浏览器仍在加载旧版本 JS 文件 (`index-KGT10jHb.js`)
- **新版本**: `index-BZC2kyOR.js` (版本号: 20260209-0935)

## 部署步骤

### 方案1: 自动化部署（推荐）

```bash
# 1. 进入项目目录
cd /workspace/projects/web-app

# 2. 运行生产环境部署脚本
bash deploy-production.sh
```

### 方案2: 手动部署

```bash
# 1. 构建前端（如果还没有构建）
npm run build

# 2. 备份当前版本
BACKUP_DIR="/var/www/meiyueart.com/backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /var/www/meiyueart.com/* "$BACKUP_DIR/"

# 3. 清理并部署新版本
rm -rf /var/www/meiyueart.com/*
cp -r dist/* /var/www/meiyueart.com/

# 4. 设置权限
chmod -R 755 /var/www/meiyueart.com

# 5. 验证部署
ls -la /var/www/meiyueart.com/
grep "20260209-0935" /var/www/meiyueart.com/index.html
```

## 验证部署

### 1. 检查文件是否存在

```bash
# 检查新版本 JS 文件
ls -la /var/www/meiyueart.com/assets/index-BZC2kyOR.js

# 检查版本号
grep "20260209-0935" /var/www/meiyueart.com/index.html
```

### 2. 测试网站访问

```bash
# 测试 HTTP
curl -I https://meiyueart.com/

# 测试 API
curl https://meiyueart.com/api/health
```

### 3. 浏览器测试

**步骤1: 清除浏览器缓存**

Chrome/Edge (Windows):
1. 按 `Ctrl + Shift + Delete`
2. 选择"缓存的图片和文件"
3. 时间范围选择"全部时间"
4. 点击"清除数据"

Chrome/Edge (Mac):
1. 按 `Cmd + Shift + Delete`
2. 选择"缓存的图片和文件"
3. 点击"清除数据"

Firefox (Windows/Mac):
1. 按 `Ctrl + Shift + Delete`
2. 选择"缓存"
3. 点击"立即清除"

**步骤2: 强制刷新页面**

- Windows: `Ctrl + F5`
- Mac: `Cmd + Shift + R`

**步骤3: 验证新版本**

打开浏览器控制台（F12），查看 Network 面板：
- 应该看到 `index-BZC2kyOR.js` 而不是 `index-KGT10jHb.js`
- 应该看到缓存清除提示（右上角黄色框）

## 常见问题

### Q1: 清除缓存后还是加载旧版本

**解决方法**:
1. 尝试使用无痕/隐私模式打开网站
2. 完全关闭浏览器后重新打开
3. 使用其他浏览器测试（Firefox, Edge, Safari）

### Q2: API 返回 401 错误

**解决方法**:
1. 检查后端服务器是否正常运行
2. 检查 API 配置是否正确
3. 查看后端日志: `tail -f /var/log/app.log`

### Q3: HTTPS 证书问题

**解决方法**:
```bash
# 检查证书状态
curl -I https://meiyueart.com/

# 如果证书过期，需要更新证书
# 使用 Let's Encrypt 或其他证书颁发机构
certbot renew
```

## 回滚方法

如果部署后出现问题，可以快速回滚：

```bash
# 找到最近的备份
ls -la /var/www/meiyueart.com/backup_*

# 回滚到指定备份
BACKUP_DIR="/var/www/meiyueart.com/backup_20260209_093000"  # 替换为实际备份目录
rm -rf /var/www/meiyueart.com/*
cp -r "$BACKUP_DIR"/* /var/www/meiyueart.com/

# 验证回滚
ls -la /var/www/meiyueart.com/
```

## 监控日志

### 查看访问日志

```bash
# Nginx 访问日志
tail -f /var/log/nginx/access.log

# Nginx 错误日志
tail -f /var/log/nginx/error.log

# 应用日志
tail -f /var/log/app.log
```

### 搜索特定错误

```bash
# 搜索 401 错误
grep "401" /var/log/nginx/access.log

# 搜索 500 错误
grep "500" /var/log/nginx/error.log

# 搜索旧版本文件引用
grep "index-KGT10jHb.js" /var/log/nginx/access.log
```

## 性能优化

### 启用 Gzip 压缩

在 Nginx 配置中添加：

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
```

### 设置缓存策略

```nginx
# 静态资源缓存 1 年
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}

# HTML 文件不缓存
location ~* \.html$ {
    expires -1;
    add_header Cache-Control "no-cache, no-store, must-revalidate";
}
```

## 安全建议

1. **定期更新**: 定期更新依赖包和系统
2. **备份**: 每次部署前备份
3. **监控**: 设置日志监控和告警
4. **HTTPS**: 强制使用 HTTPS
5. **防火墙**: 配置适当的防火墙规则

## 联系信息

如有问题，请联系：
- 技术支持: [你的邮箱]
- 紧急电话: [你的电话]
