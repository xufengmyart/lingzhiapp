# 动态资讯功能使用指南

> **功能名称**: 首页动态资讯
> **版本**: v9.12.0
> **最后更新**: 2025-02-16

---

## 🎯 功能简介

动态资讯功能为灵值生态园首页提供"发生即报道"的新闻动态展示，支持实时发布、分类筛选、精选标记等功能，让用户第一时间了解系统最新动态。

---

## 🚀 快速开始

### 查看动态资讯

1. 访问灵值生态园首页：https://meiyueart.com
2. 滚动到"动态资讯"区域
3. 查看最新的系统动态和新闻

### 阅读详情

- 点击任意资讯条目，展开查看详细内容
- 再次点击可收起内容
- 浏览量会自动增加

---

## 📊 资讯分类

| 分类 | 标识 | 说明 | 配色 |
|------|------|------|------|
| 通用 | general | 通用资讯 | 灰色渐变 |
| 新功能 | feature | 新功能上线 | 紫粉渐变 |
| 更新 | update | 系统更新 | 绿色渐变 |
| 公告 | announcement | 系统公告 | 橙红渐变 |
| 活动 | event | 活动通知 | 黄橙渐变 |

---

## 💡 功能特点

### 1. 实时性
- 新资讯即时发布
- 智能时间显示（刚刚、X分钟前、X小时前、X天前）
- 实时浏览量统计

### 2. 交互性
- **展开/收起**: 点击资讯查看详情
- **分类筛选**: 点击分类标签筛选资讯
- **精选标记**: 精选资讯带有特殊标识和光晕效果

### 3. 美观性
- **科幻主题**: 统一的应用风格
- **渐变色分类**: 不同分类使用不同的渐变色
- **动画效果**: 悬停、展开等交互动画

---

## 🔧 管理员操作

### 发布新资讯

#### 方式1：使用Python脚本

```python
# 创建文件: admin-backend/create_custom_news.py
import sqlite3
from datetime import datetime
import json

def create_news():
    db_path = '/workspace/projects/admin-backend/lingzhi_ecosystem.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    now = datetime.now()
    cursor.execute("""
        INSERT INTO news_articles
        (title, content, category, tags, is_published, is_featured,
         created_at, updated_at, published_at, author)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        '新资讯标题',
        '资讯内容...',
        'category',  # general, feature, update, announcement, event
        json.dumps(['标签1', '标签2']),
        1,  # is_published
        0,  # is_featured
        now, now, now, 'admin'
    ))

    conn.commit()
    conn.close()
    print('✅ 资讯发布成功')

if __name__ == '__main__':
    create_news()
```

#### 方式2：使用API接口

```bash
curl -X POST https://meiyueart.com/api/v9/news/articles \
  -H "Content-Type: application/json" \
  -d '{
    "title": "新资讯标题",
    "content": "资讯内容...",
    "category": "update",
    "tags": ["更新", "功能"],
    "is_published": true,
    "is_featured": true
  }'
```

### 更新资讯

```python
import sqlite3

def update_news(article_id):
    db_path = '/workspace/projects/admin-backend/lingzhi_ecosystem.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE news_articles
        SET title = ?, content = ?, updated_at = ?
        WHERE id = ?
    """, ('新标题', '新内容', datetime.now(), article_id))

    conn.commit()
    conn.close()
    print('✅ 资讯更新成功')
```

### 删除资讯（软删除）

```python
import sqlite3

def delete_news(article_id):
    db_path = '/workspace/projects/admin-backend/lingzhi_ecosystem.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 软删除：设置 is_published = 0
    cursor.execute("UPDATE news_articles SET is_published = 0 WHERE id = ?", (article_id,))

    conn.commit()
    conn.close()
    print('✅ 资讯删除成功')
```

---

## 📱 前端集成

### 在其他页面使用

```tsx
import NewsSection from '../components/NewsSection'

// 显示所有资讯
<NewsSection limit={10} />

// 只显示精选资讯
<NewsSection limit={5} featured={true} showMore={false} />

// 显示特定分类的资讯
<NewsSection limit={8} category="update" />
```

### Props 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| limit | number | 5 | 每页显示数量 |
| showMore | boolean | true | 是否显示"查看更多"按钮 |
| category | string | - | 分类筛选（general/feature/update/announcement/event） |
| featured | boolean | - | 是否只显示精选 |

---

## 🔍 API接口

### 获取资讯列表

```http
GET /api/v9/news/articles?page=1&limit=10&category=update&featured=1
```

**参数说明**:
- `page`: 页码（默认1）
- `limit`: 每页数量（默认10）
- `category`: 分类筛选（可选）
- `featured`: 精选筛选（1/0，可选）

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "标题",
      "content": "内容",
      "category": "update",
      "tags": ["标签1"],
      "is_featured": true,
      "view_count": 100,
      "published_at": "2025-02-16T12:00:00",
      "author": "admin"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 10,
    "total": 50,
    "total_pages": 5
  }
}
```

### 获取资讯详情

```http
GET /api/v9/news/articles/{id}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "title": "标题",
    "content": "详细内容",
    "category": "update",
    "tags": ["标签1", "标签2"],
    "is_featured": true,
    "view_count": 101,
    "published_at": "2025-02-16T12:00:00",
    "author": "admin"
  }
}
```

---

## 🎨 自定义样式

### 修改分类颜色

编辑 `web-app/src/components/NewsSection.tsx`:

```tsx
const getCategoryColor = (category: string) => {
  const colors: Record<string, string> = {
    general: 'from-blue-500 to-cyan-500',
    feature: 'from-purple-500 to-pink-500',
    update: 'from-green-500 to-emerald-500',
    announcement: 'from-orange-500 to-red-500',
    event: 'from-yellow-500 to-orange-500',
    custom: 'from-red-500 to-purple-500'  // 新增自定义分类
  }
  return colors[category] || 'from-gray-500 to-gray-600'
}
```

### 修改分类名称

```tsx
const getCategoryName = (category: string) => {
  const names: Record<string, string> = {
    general: '通用',
    feature: '新功能',
    update: '更新',
    announcement: '公告',
    event: '活动',
    custom: '自定义'  // 新增自定义分类
  }
  return names[category] || category
}
```

---

## 📊 数据统计

### 查看资讯统计

```python
import sqlite3

def get_news_stats():
    db_path = '/workspace/projects/admin-backend/lingzhi_ecosystem.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 总资讯数
    cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_published = 1")
    total = cursor.fetchone()[0]

    # 精选资讯数
    cursor.execute("SELECT COUNT(*) FROM news_articles WHERE is_published = 1 AND is_featured = 1")
    featured = cursor.fetchone()[0]

    # 总浏览量
    cursor.execute("SELECT SUM(view_count) FROM news_articles")
    total_views = cursor.fetchone()[0] or 0

    # 按分类统计
    cursor.execute("""
        SELECT category, COUNT(*) as count
        FROM news_articles
        WHERE is_published = 1
        GROUP BY category
    """)
    by_category = {row[0]: row[1] for row in cursor.fetchall()}

    conn.close()

    return {
        'total': total,
        'featured': featured,
        'total_views': total_views,
        'by_category': by_category
    }

stats = get_news_stats()
print(f"总资讯数: {stats['total']}")
print(f"精选资讯: {stats['featured']}")
print(f"总浏览量: {stats['total_views']}")
print(f"分类分布: {stats['by_category']}")
```

---

## 🐛 常见问题

### Q1: 资讯不显示？

**原因**:
1. `is_published` 字段未设置为 1
2. 发布时间晚于当前时间
3. 数据库查询失败

**解决方案**:
```sql
-- 检查发布状态
SELECT id, title, is_published, published_at FROM news_articles;

-- 更新发布状态
UPDATE news_articles SET is_published = 1 WHERE id = ?;

-- 设置发布时间
UPDATE news_articles SET published_at = datetime('now') WHERE id = ?;
```

### Q2: 浏览量不增加？

**原因**: 前端未正确调用详情接口

**解决方案**: 确保点击资讯时调用 `/api/v9/news/articles/{id}` 接口

### Q3: 标签显示异常？

**原因**: tags 字段格式不正确

**解决方案**: 确保 tags 字段为 JSON 数组格式
```python
import json
tags = ['标签1', '标签2']
tags_json = json.dumps(tags, ensure_ascii=False)
```

---

## 📞 技术支持

### 相关文档
- 功能完成报告：`docs/NEWS_FEATURE_COMPLETE_REPORT.md`
- 数据库规范：`docs/DATABASE_STANDARDS.md`
- API文档：`API_FIX_REPORT.md`

### 联系方式
如有问题，请联系开发团队。

---

## 📝 更新日志

### v9.12.0 (2025-02-16)
- ✅ 新增动态资讯功能
- ✅ 实现后端API接口
- ✅ 实现前端展示组件
- ✅ 集成到首页Dashboard
- ✅ 创建示例数据

---

**文档创建时间**: 2025-02-16
**版本**: v1.0.0
