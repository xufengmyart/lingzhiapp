# 标准化部署流程文档

## 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v2.0 | 2026-02-09 | 添加全面测试流程，生产环境最少测试 3 次 |

## 核心原则

### 1. 生产环境测试标准
**所有修复或设计除本地测试外，在生产环境中测试必须全方位的，最少三次**

### 2. 测试时机
- **第 1 次测试**: 构建完成后，测试构建产物
- **第 2 次测试**: 部署到生产环境后，测试部署结果
- **第 3 次测试**: 再次验证，确保系统稳定

### 3. 回滚机制
任何测试失败时，自动回滚到备份版本

## 文件清单

### 核心脚本
- `deploy-standardized.sh` - 标准化部署脚本（带 3 次测试）
- `test-deployment.sh` - 全面测试脚本（30 项测试）
- `deploy-auto-cache-clear.sh` - 简化部署脚本

### 配置文件
- `nginx-auto-cache-clear.conf` - Nginx 配置（缓存控制）
- `.env.production` - 生产环境变量

### 文档
- `STANDARDIZED_DEPLOYMENT.md` - 本文档
- `AUTO_CACHE_CLEAR_GUIDE.md` - 自动缓存清除指南
- `QUICK_START.md` - 快速开始

## 测试项目（30 项）

### 后端服务测试（3 项）
1. ✅ 后端服务运行中
2. ✅ 后端端口 8080 监听中
3. ✅ 后端 API 健康检查

### 前端文件测试（11 项）
4. ✅ 前端目录存在
5. ✅ index.html 文件存在
6. ✅ index.html 包含缓存控制
7. ✅ index.html 包含版本管理脚本
8. ✅ Service Worker 文件存在
9. ✅ 版本管理器文件存在
10. ✅ 版本信息文件存在
11. ✅ JS 资源文件存在
12. ✅ CSS 资源文件存在
13. ✅ JS 文件包含正确的 API 地址
14. ✅ 没有旧的 JS 文件残留

### 版本一致性测试（3 项）
15. ✅ version.json 格式正确
16. ✅ version-manager.js 版本号存在
17. ✅ sw.js 版本号存在

### 功能测试（3 项）
18. ✅ 登录 API 响应正确
19. ✅ 注册 API 响应正确
20. ✅ 用户信息 API 响应正确

### 性能测试（2 项）
21. ✅ index.html 大小合理 (< 10KB)
22. ✅ JS 文件大小合理 (< 2MB)

### 安全测试（2 项）
23. ✅ 没有暴露 API 密钥
24. ✅ 没有明显的调试代码

### 数据库测试（3 项）
25. ✅ 数据库文件存在
26. ✅ 数据库文件不为空
27. ✅ admin 用户存在

### 回归测试（3 项）
28. ✅ admin 用户可以登录
29. ✅ 获取灵值信息 API 正常
30. ✅ 推荐码 API 正常

## 部署流程

### 标准部署（推荐）

```bash
cd /workspace/projects/web-app
./deploy-standardized.sh
```

**自动完成以下步骤**:

1. ✅ 环境检查
2. ✅ 备份现有部署
3. ✅ 更新版本号
4. ✅ 清理缓存和旧文件
5. ✅ 构建前端
6. ✅ **第 1 次测试**（构建后测试）
7. ✅ 部署到生产环境
8. ✅ **第 2 次测试**（部署后测试）
9. ✅ **第 3 次测试**（再次验证）
10. ✅ 输出部署报告

### 快速部署（仅用于小改动）

```bash
cd /workspace/projects/web-app
./deploy-auto-cache-clear.sh
```

## 测试失败处理

### 自动回滚机制
任何测试失败时，脚本会自动：
1. 检测失败
2. 停止部署
3. 回滚到最新的备份
4. 输出错误信息
5. 退出并返回错误代码

### 手动回滚
```bash
# 查看可用备份
ls -lh /workspace/projects/web-app/backups/

# 回滚到指定备份
rm -rf /var/www/frontend/*
cp -r /workspace/projects/web-app/backups/frontend_backup_YYYYMMDD_HHMMSS/* /var/www/frontend/
```

## 版本管理

### 版本号格式
```
YYYYMMDD-HHMM
示例: 20260209-1000
```

### 版本号同步
部署脚本会自动同步以下文件的版本号：
- `public/version.json`
- `public/version-manager.js`
- `public/sw.js`
- `index.html`

## 缓存控制

### HTML 文件
```html
<meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
<meta http-equiv="Pragma" content="no-cache" />
<meta http-equiv="Expires" content="0" />
```

### JavaScript 自动检测
```javascript
const currentVersion = '20260209-1000';
const storedVersion = localStorage.getItem('lingzhi_app_version');

if (storedVersion && storedVersion !== currentVersion) {
    // 自动清除所有缓存并刷新
}
```

## 验证步骤

### 1. 查看部署日志
```bash
cd /workspace/projects/web-app
./deploy-standardized.sh 2>&1 | tee deploy.log
```

### 2. 检查测试报告
```
测试统计:
  总测试数: 30
  通过: 30
  失败: 0

  通过率: 100%
```

### 3. 访问网站
```
https://meiyueart.com/
```

### 4. 打开开发者工具 (F12)

#### Console 标签
应该看到：
```
[版本管理] 当前版本: 20260209-1000
[版本管理] 初始化，当前版本: 20260209-1000
[版本管理] Service Worker 注册成功: https://meiyueart.com/
[SW] Service Worker 已加载，版本: 20260209-1000
```

#### Network 标签
- 检查加载的 JS 文件名
- 应该是 `index-BZC2kyOR.js` ✅
- 不应该是 `index-KGT10jHb.js` ❌

### 5. 测试登录
- 使用账号: `admin / admin123`
- 登录应该成功 ✅

## 常见问题

### Q1: 测试失败怎么办？

**A**: 查看测试日志，定位失败的测试项，修复问题后重新部署。

### Q2: 如何跳过某些测试？

**A**: 编辑 `test-deployment.sh`，注释掉不需要的测试项。

### Q3: 部署后用户还是看到旧版本？

**A**: 让用户访问 `https://meiyueart.com/force-refresh.html` 自动清除缓存。

### Q4: 如何查看部署历史？

**A**: 查看备份目录：
```bash
ls -lh /workspace/projects/web-app/backups/
```

## 监控和维护

### 定期检查（建议每周）

1. **检查备份目录**:
   ```bash
   ls -lh /workspace/projects/web-app/backups/
   # 删除超过 30 天的备份
   find /workspace/projects/web-app/backups/ -type d -mtime +30 -exec rm -rf {} \;
   ```

2. **检查磁盘空间**:
   ```bash
   df -h
   ```

3. **查看部署日志**:
   ```bash
   tail -n 100 /workspace/projects/admin-backend/backend.log
   ```

### 性能优化

1. **监控页面加载时间**
2. **检查缓存命中率**
3. **优化资源加载策略**

## 最佳实践

### 1. 本地测试
- 代码修改后，先在本地测试
- 确保功能正常后再部署

### 2. 小步迭代
- 每次只修改一个功能
- 避免大范围改动

### 3. 备份验证
- 部署前确认备份已创建
- 测试回滚流程

### 4. 文档更新
- 重大修改更新文档
- 记录变更历史

### 5. 监控告警
- 关注测试失败率
- 及时处理问题

## 总结

本标准化部署流程确保：

✅ **生产环境最少测试 3 次**
✅ **30 项全面测试覆盖**
✅ **自动回滚机制**
✅ **版本一致性管理**
✅ **缓存自动控制**
✅ **友好的用户体验**

用户无需手动清理缓存，系统自动处理所有更新流程！
