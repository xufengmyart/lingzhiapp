# 分享系统功能使用指南

## 📖 功能概述

本系统提供完整的分享数据分析功能，包括点击统计、转化率分析、排行榜、推荐关系可视化和奖励机制。

## 🔧 API 接口文档

### 1. 分享点击统计

**接口**: `POST /api/analytics/share/click`

**请求参数**:
```json
{
  "referral_code": "ABC123",
  "article_id": 1,
  "platform": "link"
}
```

**响应**:
```json
{
  "success": true,
  "message": "点击记录成功"
}
```

**使用场景**:
- 用户点击分享链接时调用
- 自动记录点击时间和用户信息
- 更新点击计数

### 2. 分享转化率统计

**接口**: `GET /api/analytics/share/conversion?days=7`

**请求参数**:
- `days`: 统计天数（默认7天）

**响应**:
```json
{
  "success": true,
  "data": {
    "summary": {
      "total_shares": 100,
      "total_clicks": 500,
      "total_registrations": 50,
      "click_rate": 500.0,
      "registration_rate": 10.0
    },
    "daily": [
      {
        "date": "2026-02-23",
        "shares": 20,
        "clicks": 100,
        "registrations": 10
      }
    ]
  }
}
```

**使用场景**:
- 用户查看自己的分享数据
- 分析分享效果
- 制定分享策略

### 3. 分享排行榜

**接口**: `GET /api/analytics/share/leaderboard?period=week&limit=10`

**请求参数**:
- `period`: 统计周期（week/month/all）
- `limit`: 返回数量（默认10）

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "rank": 1,
      "user_id": 1,
      "username": "admin",
      "nickname": "管理员",
      "total_shares": 50,
      "total_clicks": 250,
      "total_registrations": 25
    }
  ]
}
```

**使用场景**:
- 展示优秀分享者
- 激励用户参与分享
- 推广活动

### 4. 推荐关系树

**接口**: `GET /api/analytics/referral/tree`

**权限**: 需要管理员权限

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "username": "admin",
      "nickname": "管理员",
      "referees": [
        {
          "id": 1038,
          "username": "testuser",
          "nickname": "测试用户",
          "registrationDate": "2026-02-23 10:00:00",
          "points": 100
        }
      ]
    }
  ]
}
```

**使用场景**:
- 管理员查看推荐关系
- 分析推荐网络
- 制定运营策略

### 5. 推荐奖励记录

**接口**: `GET /api/analytics/referral/rewards?page=1&per_page=20`

**权限**: 需要管理员权限

**响应**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "referrer_id": 1,
      "referrer_username": "admin",
      "referee_id": 1038,
      "referee_username": "testuser",
      "reward_type": "registration",
      "amount": 50,
      "created_at": "2026-02-23 10:00:00"
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

**使用场景**:
- 管理员查看奖励发放记录
- 财务对账
- 用户咨询

### 6. 手动发放奖励

**接口**: `POST /api/analytics/referral/rewards/manual`

**权限**: 需要管理员权限

**请求参数**:
```json
{
  "target_user_id": 1,
  "amount": 100,
  "reason": "活动奖励"
}
```

**响应**:
```json
{
  "success": true,
  "message": "奖励发放成功"
}
```

**使用场景**:
- 管理员手动调整奖励
- 活动奖励发放
- 补偿操作

## 🎨 前端页面

### 分享数据分析页面

**路由**: `/share-analytics`

**功能模块**:

1. **数据概览**
   - 总分享次数
   - 总点击次数
   - 总注册数
   - 注册转化率

2. **每日趋势**
   - 表格展示每日数据
   - 支持时间筛选

3. **分享排行榜**
   - 周榜、月榜、总榜
   - 前三名特殊标识
   - 转化率进度条

**使用方法**:
```typescript
import { getConversionStats, getShareLeaderboard } from '../services/shareApi';

// 获取转化率统计
const stats = await getConversionStats(token, 7);

// 获取排行榜
const leaderboard = await getShareLeaderboard('week', 10);
```

## 💡 使用示例

### 示例1: 用户分享文章并跟踪转化

```javascript
// 1. 用户生成分享链接（使用推荐码）
const shareData = {
  referral_code: 'ABC123',
  article_id: 1,
  platform: 'link'
};

// 2. 其他用户点击分享链接
await fetch('/api/analytics/share/click', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(shareData)
});

// 3. 新用户注册时记录推荐关系
await fetch('/api/analytics/share/registration', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    referral_code: 'ABC123',
    new_user_id: 1038
  })
});
```

### 示例2: 管理员查看推荐网络

```javascript
const token = localStorage.getItem('token');

// 获取推荐关系树
const response = await fetch('/api/analytics/referral/tree', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const tree = await response.json();
console.log('推荐关系:', tree.data);
```

### 示例3: 前端展示排行榜

```tsx
import React, { useEffect, useState } from 'react';
import { getShareLeaderboard } from '../services/shareApi';

function Leaderboard() {
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    getShareLeaderboard('week', 10).then(data => {
      setLeaderboard(data.data);
    });
  }, []);

  return (
    <div>
      <h2>分享排行榜（本周）</h2>
      <table>
        <thead>
          <tr>
            <th>排名</th>
            <th>用户</th>
            <th>分享数</th>
            <th>点击数</th>
            <th>注册数</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map(item => (
            <tr key={item.rank}>
              <td>{item.rank}</td>
              <td>{item.nickname || item.username}</td>
              <td>{item.total_shares}</td>
              <td>{item.total_clicks}</td>
              <td>{item.total_registrations}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

## 📊 数据分析建议

### 1. 转化率优化
- **高点击低注册**: 检查注册流程是否顺畅
- **低点击高注册**: 可能是测试数据，需要验证
- **正常范围**: 点击率 200-500%，注册率 5-15%

### 2. 排行榜激励
- 定期更新排行榜（周榜、月榜）
- 前三名给予额外奖励
- 新用户进步快给予鼓励

### 3. 推荐关系分析
- 识别核心推荐人
- 分析推荐路径
- 优化推荐激励机制

## 🚀 性能优化建议

### 1. 缓存策略
```python
from utils.performance import cache_decorator

@cache_decorator(ttl=300)
def get_leaderboard(period, limit):
    # 5分钟内不会重复查询数据库
    pass
```

### 2. 异步处理
```python
from utils.performance import async_task

@async_task()
def record_click(data):
    # 异步记录点击，不阻塞主流程
    pass
```

### 3. 数据库索引
- 已为所有查询字段创建索引
- 定期执行 `optimize_database.py`

## 🔒 安全建议

1. **接口权限**
   - 所有接口需要认证
   - 管理员接口需要额外权限验证

2. **数据验证**
   - 验证所有输入参数
   - 防止SQL注入和XSS攻击

3. **速率限制**
   - 建议对频繁调用的接口添加速率限制
   - 防止恶意刷数据

## 📞 技术支持

如有问题，请联系：
- 开发团队: Coze Coding
- 邮箱: support@meiyueart.com
- 文档: https://docs.meiyueart.com

---

*最后更新: 2026-02-23*
