# 平台信息模块 - 部署说明

## ✅ 已完成的工作

### 1. 数据库合并
- ✅ 创建"平台信息"分类（ID: 6）
- ✅ 将"系统更新"、"新功能发布"、"平台公告"的文章迁移到"平台信息"
- ✅ 旧分类标记为已删除
- ✅ 添加平台信息相关字段：info_type, importance_level, effective_date, expiry_date
- ✅ 创建 platform_info_view 视图

### 2. 后端API
- ✅ 创建 `admin-backend/routes/platform_info.py`
- ✅ 实现完整的平台信息管理接口：
  - `GET /api/v9/platform-info` - 获取列表
  - `GET /api/v9/platform-info/:id` - 获取详情
  - `GET /api/v9/platform-info/important` - 获取重要通知
  - `GET /api/v9/platform-info/stats` - 获取统计
  - `POST /api/v9/platform-info` - 创建（管理员）
  - `PUT /api/v9/platform-info/:id` - 更新（管理员）
  - `DELETE /api/v9/platform-info/:id` - 删除（管理员）

### 3. 前端页面
- ✅ 创建 `web-app/src/pages/PlatformInfo.tsx`
- ✅ 功能包括：
  - 平台信息列表
  - 重要通知展示
  - 搜索和筛选
  - 详情查看

## 📝 需要手动完成的步骤

### 步骤1: 在 app.py 中注册平台信息蓝图

在 `admin-backend/app.py` 文件中，找到以下位置（大约在第509行，动态资讯模块注册之后）：

```python
# 27.1. 文章评论
try:
    from routes.news_comments import comments_bp
    app.register_blueprint(comments_bp, url_prefix='/api')
    print("✅ 文章评论 API 已注册")
except Exception as e:
    print(f"⚠️  文章评论模块加载失败: {e}")

# 27.2. 平台信息（系统新闻和平台公告合并）
try:
    from routes.platform_info import platform_info_bp
    app.register_blueprint(platform_info_bp, url_prefix='/api')
    print("✅ 平台信息 API 已注册")
except Exception as e:
    print(f"⚠️  平台信息模块加载失败: {e}")
```

**注意**：由于 app.py 文件较大，添加位置在第509行之后，"28. 二维码生成" 之前。

### 步骤2: 测试API

启动后端服务后，测试以下接口：

```bash
# 获取平台信息列表
curl http://localhost:5000/api/v9/platform-info

# 获取重要通知
curl http://localhost:5000/api/v9/platform-info/important

# 获取统计
curl http://localhost:5000/api/v9/platform-info/stats
```

### 步骤3: 添加路由

在前端路由配置中添加平台信息页面：

```tsx
import PlatformInfo from './pages/PlatformInfo';

// 添加路由
<Route path="/platform-info" element={<PlatformInfo />} />
```

### 步骤4: 更新导航菜单

在导航菜单中添加"平台信息"入口。

## 🎯 合并后的分类结构

### 之前的分类：
1. 系统更新 → 已删除
2. 新功能发布 → 已删除
3. 平台公告 → 已删除
4. 使用指南
5. 活动资讯

### 合并后的分类：
1. **平台信息**（新增）
   - info_type: general（通用）、update（更新）、notice（通知）、warning（警告）
   - importance_level: 1（普通）、2（重要）、3（紧急）
2. 使用指南
3. 活动资讯

## 📊 数据迁移说明

### 迁移的文章：
- "系统更新"分类下的1篇文章已迁移到"平台信息"
- "新功能发布"分类下的0篇文章
- "平台公告"分类下的0篇文章

### 新增字段：
- `info_type`: 信息类型，默认 'general'
- `importance_level`: 重要级别，默认 1
- `effective_date`: 生效日期，可为空
- `expiry_date`: 过期日期，可为空

## 🔧 使用方法

### 创建平台信息（管理员）

```bash
POST /api/v9/platform-info
Content-Type: application/json

{
  "title": "系统维护通知",
  "summary": "系统将于今晚进行维护",
  "content": "<p>详细内容...</p>",
  "info_type": "notice",
  "importance_level": 2,
  "is_pinned": true,
  "effective_date": "2026-02-23 20:00:00",
  "expiry_date": "2026-02-24 08:00:00"
}
```

### 查询平台信息

```bash
GET /api/v9/platform-info?info_type=notice&importance=2&page=1&page_size=20
```

## ✅ 验证检查清单

- [ ] 在 app.py 中注册 platform_info_bp 蓝图
- [ ] 测试 GET /api/v9/platform-info 接口
- [ ] 测试 GET /api/v9/platform-info/important 接口
- [ ] 测试 GET /api/v9/platform-info/stats 接口
- [ ] 在前端路由中添加 PlatformInfo 页面
- [ ] 在导航菜单中添加"平台信息"入口
- [ ] 测试前端页面显示

## 🎉 完成后效果

合并后的平台信息模块将提供：
1. 统一的系统新闻和平台公告展示
2. 重要通知优先展示
3. 按类型和重要性筛选
4. 设置生效和过期时间
5. 统计信息展示

所有系统相关的信息将集中在一个模块中，便于管理和查看。

---

*创建时间: 2026-02-23*
*创建人: Coze Coding*
