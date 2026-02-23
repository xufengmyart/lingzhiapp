# 生产环境部署历史记录

> **重要**: 所有部署记录必须在此归档

---

## 📋 部署历史

### 2026-02-23 15:28 - 文章管理、分享功能和平台信息合并

**部署版本**: v20260223-1528

**部署目的**:
- 实现文章的增删改查功能
- 添加文章审核流程
- 添加分享功能（包含推荐码锁定）
- 将系统新闻和平台信息合二为一

**完成的功能**:

#### 1. 文章增删改查功能 ✅
- **创建文章** (POST `/admin/news/articles`):
  - 管理员可以创建新的文章
  - 支持标题、内容、摘要、分类、封面图等字段
  - 自动生成 slug
  - 支持置顶和精选标记

- **编辑文章** (PUT `/admin/news/articles/<id>`):
  - 管理员可以编辑文章内容
  - 支持部分更新
  - 自动更新修改时间

- **删除文章** (DELETE `/admin/news/articles/<id>`):
  - 管理员可以删除文章
  - 级联删除文章评论

#### 2. 文章审核流程 ✅
- **审核通过** (PUT `/admin/news/articles/<id>/approve`):
  - 将文章状态改为 published
  - 设置发布时间

- **审核拒绝** (PUT `/admin/news/articles/<id>/reject`):
  - 将文章状态改为 rejected
  - 支持填写拒绝原因

#### 3. 分享功能 ✅
- **生成分享链接** (GET `/api/articles/<id>/share`):
  - 自动包含用户推荐码
  - 支持多种分享平台（微信、微博、QQ）
  - 生成分享二维码
  - 当用户通过分享链接注册时，自动锁定推荐关系

#### 4. 平台信息合并 ✅
- 将"系统公告"分类更名为"平台信息"
- 更新描述：平台公告、系统更新和重要通知
- 统一名称，优化用户体验

**新增文件**:
- `routes/share.py` - 文章分享路由
- `scripts/update_category_name.py` - 更新分类名称脚本

**修改文件**:
- `routes/news_articles.py` - 添加编辑、审核接口
- `app.py` - 注册分享蓝图
- `scripts/init_news_and_notifications_tables.py` - 更新分类名称

**API 接口列表**:
- `POST /admin/news/articles` - 创建文章
- `PUT /admin/news/articles/<id>` - 编辑文章
- `DELETE /admin/news/articles/<id>` - 删除文章
- `PUT /admin/news/articles/<id>/approve` - 审核通过
- `PUT /admin/news/articles/<id>/reject` - 审核拒绝
- `GET /api/articles/<id>/share` - 获取分享信息

**数据库更新**:
- 更新分类名称：系统公告 -> 平台信息

**测试结果**:
- ✅ 所有 API 接口已创建
- ✅ 分类名称已更新为"平台信息"
- ✅ 健康检查通过
- ✅ 登录测试通过
- ✅ 分类 API 正常返回

**部署信息**:
- **部署时间**: 2026-02-23 15:28:43 CST
- **服务器**: meiyueart.com
- **后端路径**: /app/meiyueart-backend
- **备份**: /var/www/backups/backend_backup_20260223_152726.tar.gz

**后续建议**:
1. 在前端创建文章管理界面
2. 在文章详情页添加分享按钮
3. 测试推荐关系锁定功能
4. 添加文章审核通知

**备注**:
- 后端 API 已完整实现
- 分类名称已成功更新
- 分享功能已实现并包含推荐码

---

### 2026-02-23 14:37 - 系统优化和内容补充
