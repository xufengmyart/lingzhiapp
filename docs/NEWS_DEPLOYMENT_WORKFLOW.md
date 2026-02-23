# 动态资讯功能部署工作流程

> **项目**: 灵值生态园智能体系统
> **功能**: 动态资讯管理（包含图片支持、搜索功能、评论系统、分享功能、推送通知、用户行为分析、个性化推荐、资讯置顶、富文本编辑器、多语言支持、动态分类管理、内容审核工作流）
> **完成日期**: 2025-02-16

---

## 📋 概述

本文档记录了动态资讯功能在生产环境中的完整部署工作流程，包括后端API整合、前端组件集成、静态资源修复、构建和部署的详细步骤。

---

## 🚀 部署前检查

### 1. 数据库表检查
在部署前，确保数据库中已创建以下表：

**核心表**:
- `news_articles` - 资讯文章表
- `news_comments` - 评论表
- `news_user_actions` - 用户行为表
- `news_categories` - 分类表
- `news_notifications` - 通知表
- `news_likes` - 点赞表
- `news_audit_logs` - 审核日志表

**检查命令**:
```bash
cd /workspace/projects/admin-backend
python check_database_tables.py
```

### 2. 后端API文件检查
确保以下文件存在：
- `/workspace/projects/admin-backend/app.py` - 主应用文件
- `/workspace/projects/admin-backend/news_articles.py` - 动态资讯API
- `/workspace/projects/admin-backend/news_articles_complete.py` - 完整版API（备份）

### 3. 前端组件检查
确保以下文件存在：
- `/workspace/projects/web-app/src/components/NewsSection.tsx` - 基础资讯组件
- `/workspace/projects/web-app/src/components/NewsSectionComplete.tsx` - 完整资讯组件
- `/workspace/projects/web-app/src/pages/Dashboard.tsx` - 主页面（已集成NewsSectionComplete）

---

## 🔧 部署步骤

### 第一步：后端API整合

#### 1.1 验证Blueprint注册
检查 `/workspace/projects/admin-backend/app.py` 中是否已注册动态资讯Blueprint：

```python
# 注册动态资讯蓝图
try:
    from news_articles import news_bp
    app.register_blueprint(news_bp)
    print("✅ 动态资讯 API 已注册")
except Exception as e:
    print(f"⚠️ 动态资讯功能不可用: {str(e)}")
```

#### 1.2 复制后端源码到部署目录
```bash
cp /workspace/projects/admin-backend/app.py /source/app.py
echo "✅ 后端源码复制成功"
```

#### 1.3 创建重定向文件（强制使用源码版本）
```bash
# 创建 /source/app/__init__.py
cat > /source/app/__init__.py << 'EOF'
"""
强制使用源码版本的应用
"""
import sys
import os

# 确保使用源码目录
WORKSPACE = "/workspace/projects/admin-backend"
if WORKSPACE not in sys.path:
    sys.path.insert(0, WORKSPACE)

# 导入Flask应用
from app import app as flask_app

# 将Flask应用转换为ASGI应用（用于uvicorn）
from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

# 创建FastAPI包装器
fastapi_app = FastAPI()

# 将Flask应用包装为WSGI中间件
fastapi_app.mount("/", WSGIMiddleware(flask_app))

__all__ = ["app"]
EOF

# 创建 /source/app/main.py
cat > /source/app/main.py << 'EOF'
"""
FastAPI主入口 - 使用源码版本的Flask应用
"""
from app import app

__all__ = ["app"]
EOF
```

#### 1.4 验证后端服务
后端服务由runtime-agent自动管理，无需手动重启。

---

### 第二步：前端静态资源修复

#### 2.1 创建缺失的静态资源目录
```bash
mkdir -p /workspace/projects/web-app/public/assets/mock
```

#### 2.2 创建占位图片文件
```bash
# 创建 logo.svg
cat > /workspace/projects/web-app/public/assets/mock/logo.svg << 'EOF'
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="#E0E7FF"/>
  <text x="50" y="55" font-family="Arial" font-size="14" fill="#6366F1" text-anchor="middle">Logo</text>
</svg>
EOF

# 创建 design.png
cat > /workspace/projects/web-app/public/assets/mock/design.png << 'EOF'
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="#DBEAFE"/>
  <text x="50" y="55" font-family="Arial" font-size="14" fill="#3B82F6" text-anchor="middle">Design</text>
</svg>
EOF

# 创建 architecture.png
cat > /workspace/projects/web-app/public/assets/mock/architecture.png << 'EOF'
<svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="100" height="100" fill="#D1FAE5"/>
  <text x="50" y="55" font-family="Arial" font-size="14" fill="#10B981" text-anchor="middle">Arch</text>
</svg>
EOF
```

#### 2.3 验证文件
```bash
ls -la /workspace/projects/web-app/public/assets/mock/
```

预期输出：
```
-rw-r--r-- 1 root root 202 Feb 16 12:02 architecture.png
-rw-r--r-- 1 root root 203 Feb 16 12:02 design.png
-rw-r--r-- 1 root root 202 Feb 16 12:02 logo.svg
```

---

### 第三步：前端构建

#### 3.1 清理旧构建
```bash
cd /workspace/projects/web-app
rm -rf dist
```

#### 3.2 生成版本信息
```bash
npm run generate-version
```

这会生成：
- `/workspace/projects/web-app/public/version.json`
- `/workspace/projects/web-app/public/sw.js`
- `/workspace/projects/web-app/index.html`

#### 3.3 构建前端
```bash
npm run build
```

或者使用单独的命令：
```bash
npx tsc
npx vite build
```

预期输出：
```
vite v5.4.21 building for production...
transforming...
✓ 2192 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                     6.60 kB │ gzip:   2.58 kB
dist/assets/index-vLOWZiL7.css    129.75 kB │ gzip:  19.03 kB
dist/assets/index-C6aFDRRD.js   1,212.56 kB │ gzip: 317.77 kB

✓ built in 16.09s
```

#### 3.4 验证构建产物
```bash
ls -la /workspace/projects/web-app/dist/
```

预期输出应包括：
- `index.html`
- `assets/index-vLOWZiL7.css`
- `assets/index-C6aFDRRD.js`
- `assets/mock/` 目录及其子文件
- `version.json`
- `sw.js`

---

### 第四步：部署到对象存储

#### 4.1 使用部署脚本
```bash
cd /workspace/projects
python deploy_frontend_v2.py
```

#### 4.2 验证上传
预期输出：
```
============================================================
🚀 开始上传前端构建产物到对象存储
============================================================
📂 扫描目录: /workspace/projects/web-app/dist
📤 上传: app-icon.svg -> app-icon.svg
📤 上传: index-C6aFDRRD.js -> assets/index-C6aFDRRD.js
...
✅ 上传完成！共上传 17 个文件
============================================================

🔗 访问地址:
  https://meiyueart.com
```

#### 4.3 清除浏览器缓存
部署完成后，用户需要清除浏览器缓存以获取最新版本：

**方法1：手动清除**
1. 打开浏览器
2. Ctrl + Shift + Delete
3. 选择"缓存的图片和文件"
4. 点击"清除数据"
5. Ctrl + F5 强制刷新

**方法2：使用清除缓存页面**
访问：`https://meiyueart.com/clear-cache.html`

**方法3：使用强制刷新页面**
访问：`https://meiyueart.com/force-refresh.html`

---

## 🔍 验证步骤

### 1. 后端API验证
```bash
curl -X GET "https://meiyueart.com/api/v9/news/articles?limit=5"
```

预期返回：
```json
{
  "success": true,
  "data": [...],
  "pagination": {...}
}
```

### 2. 前端显示验证
1. 访问：`https://meiyueart.com`
2. 登录系统
3. 检查Dashboard页面是否显示动态资讯模块
4. 验证资讯列表、搜索、筛选、评论等功能

### 3. 静态资源验证
```bash
curl -I "https://meiyueart.com/assets/mock/logo.svg"
curl -I "https://meiyueart.com/assets/mock/design.png"
curl -I "https://meiyueart.com/assets/mock/architecture.png"
```

预期返回：
```
HTTP/2 200
```

---

## 📝 部署清单

| 步骤 | 任务 | 状态 | 命令/文件 |
|------|------|------|-----------|
| 1 | 数据库表检查 | ✅ | `check_database_tables.py` |
| 2 | 后端API整合 | ✅ | `app.py`, `news_articles.py` |
| 3 | 源码复制 | ✅ | `cp app.py /source/app.py` |
| 4 | 重定向文件创建 | ✅ | `/source/app/__init__.py`, `/source/app/main.py` |
| 5 | 静态资源修复 | ✅ | `/workspace/projects/web-app/public/assets/mock/` |
| 6 | 前端构建 | ✅ | `npm run build` |
| 7 | 对象存储上传 | ✅ | `deploy_frontend_v2.py` |
| 8 | 浏览器缓存清除 | ⚠️ 用户操作 | 访问清除缓存页面 |

---

## ⚠️ 常见问题

### 问题1：后端API返回500错误

**原因**：数据库连接问题或SQL查询错误

**解决方案**：
1. 检查数据库路径是否正确
2. 验证数据库表结构
3. 查看后端日志：`/app/work/logs/bypass/app.log`
4. 运行测试脚本：`python test_api_errors.py`

### 问题2：前端静态资源404错误

**原因**：静态资源文件不存在或未上传到对象存储

**解决方案**：
1. 检查文件是否存在：`ls -la /workspace/projects/web-app/public/assets/mock/`
2. 重新构建前端：`npm run build`
3. 重新上传到对象存储：`python deploy_frontend_v2.py`

### 问题3：浏览器缓存导致显示旧版本

**原因**：浏览器缓存了旧版本的静态资源

**解决方案**：
1. 使用清除缓存页面：`https://meiyueart.com/clear-cache.html`
2. 手动清除浏览器缓存
3. 使用强制刷新页面：`https://meiyueart.com/force-refresh.html`

### 问题4：服务未自动重启

**原因**：runtime-agent未能检测到文件变更

**解决方案**：
1. 手动终止进程：`kill -9 <pid>`
2. 等待runtime-agent自动重启
3. 检查进程状态：`ps aux | grep -E "python|gunicorn|flask|uvicorn"`

---

## 📚 相关文档

- [动态资讯功能文档](./NEWS_FEATURE_COMPLETE.md)
- [数据库升级脚本](./upgrade_news_database.py)
- [API测试脚本](./test_api_errors.py)
- [数据库表检查脚本](./check_database_tables.py)

---

## 📞 技术支持

### 联系方式
- 项目仓库：`/workspace/projects`
- 后端代码：`/workspace/projects/admin-backend`
- 前端代码：`/workspace/projects/web-app`

### 验证命令
```bash
# 检查后端服务
ps aux | grep -E "python|gunicorn|flask|uvicorn"

# 检查数据库
cd /workspace/projects/admin-backend && python check_database_tables.py

# 测试API
python test_api_errors.py

# 部署前端
cd /workspace/projects && python deploy_frontend_v2.py
```

---

**完成时间**: 2025-02-16
**文档创建时间**: 2025-02-16
**版本**: v1.0.0
**状态**: ✅ 已完成部署

---

## 📌 总结

本次部署完成了以下工作：

✅ **后端API整合**：动态资讯API已成功整合到主应用中
✅ **静态资源修复**：创建了所有缺失的占位图片文件
✅ **前端构建**：成功构建前端应用，包含完整的动态资讯功能
✅ **对象存储上传**：前端构建产物已上传到对象存储
✅ **工作流程文档**：创建了完整的部署工作流程文档

**下一步**：
- 用户清除浏览器缓存后访问 `https://meiyueart.com`
- 验证动态资讯功能是否正常工作
- 根据用户反馈进行优化和调整

---

**备注**：部署过程中遇到的环境问题（Nuitka编译环境）已通过创建重定向文件解决，强制使用源码版本。后端服务由runtime-agent自动管理，无需手动重启。
