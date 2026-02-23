# 反馈功能修复报告

## 修复时间
2026年2月18日 22:50

## 问题描述

### 问题1: 提交反馈失败
- **现象**: 用户在对话界面提交反馈时，提示"提交反馈失败"
- **原因**: 前端调用的API路径不正确，且后端缺少相应的反馈API路由

### 问题2: 对话时没有显示灵值消耗和奖励
- **现象**: 对话界面没有显示灵值计费信息（消耗灵值、获得灵值）
- **原因**: 前端没有实现计费信息的显示组件

---

## 修复方案

### 1. 后端修复

#### 新增反馈API路由
**文件**: `admin-backend/routes/agent.py`

**新增路由**:
```python
@agent_bp.route('/feedback', methods=['POST'])
def submit_agent_feedback():
    """
    提交智能体反馈
    请求体: { type, question, agent_id }
    响应: { success: true, data: { contribution_value } }
    """
```

**功能说明**:
- 接受反馈类型：helpful（有帮助）/ not_helpful（无帮助）/ suggestion（建议）
- 检查用户是否已提交过相同问题的反馈（防止重复提交）
- 根据反馈类型计算灵值奖励：
  - helpful: 10 灵值
  - not_helpful: 5 灵值
  - suggestion: 15 灵值
- 插入反馈记录到 `feedback` 表
- 更新用户灵值到 `users` 表的 `total_lingzhi` 字段

**请求头**:
- `X-User-ID`: 用户ID（必填）
- `Authorization`: Bearer token（可选）

**请求体**:
```json
{
  "type": "helpful",
  "question": "用户的问题",
  "comment": "可选的评论",
  "agent_id": 1
}
```

**响应**:
```json
{
  "success": true,
  "message": "反馈提交成功",
  "data": {
    "contribution_value": 10
  }
}
```

**错误响应**:
```json
{
  "success": false,
  "error": "您已经提交过该问题的反馈"
}
```

---

### 2. 前端修复

#### 修复反馈API调用
**文件**: `web-app/src/pages/Chat.tsx`

**修改内容**:
```typescript
const handleFeedback = async (type: 'helpful' | 'not_helpful' | 'suggestion', question?: string) => {
  setFeedbackSubmitting(true)
  try {
    const token = localStorage.getItem('token')
    const response = await fetch(`${import.meta.env.VITE_API_URL}/agent/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        'X-User-ID': localStorage.getItem('userId') || ''
      },
      body: JSON.stringify({
        type,
        question: feedbackModal.messageContent,
        comment: question || '',
        agent_id: 1
      })
    })

    const result = await response.json()

    if (result.success) {
      const reward = result.data.contribution_value
      alert(`反馈提交成功！获得 ${reward} 灵值`)
      
      // 添加反馈奖励
      addFeedbackReward(reward)
      
      setFeedbackModal({ open: false, messageId: '', messageContent: '' })
    } else {
      alert(`反馈提交失败：${result.error}`)
    }
  } catch (error) {
    console.error('提交反馈失败:', error)
    alert('提交反馈失败，请稍后再试')
  } finally {
    setFeedbackSubmitting(false)
  }
}
```

**修改点**:
1. 使用原生 `fetch` API 替代 `api.post`
2. 添加 `Authorization` 和 `X-User-ID` 请求头
3. 修复API路径为 `/agent/feedback`
4. 移除 `window.location.reload()`（避免刷新页面）
5. 改进错误处理和用户提示

#### 新增灵值计费显示组件
**文件**: `web-app/src/pages/Chat.tsx`

**新增内容**:
```tsx
{/* 灵值计费信息显示 */}
{isBilling && (
  <div className={`mb-4 p-3 rounded-xl ${chatTheme.bubble.assistant.bg} ${chatTheme.bubble.assistant.border} transition-all duration-300`}>
    <div className="flex items-center justify-between text-sm">
      <div className="flex items-center gap-2">
        <Sparkles className="w-4 h-4 text-[#00C3FF]" />
        <span className="text-[#B4C7E7]">对话时长:</span>
        <span className="text-white font-semibold">{formatDuration(billingInfo.duration)}</span>
      </div>
      {billingInfo.consumedLingzhi > 0 && (
        <div className="flex items-center gap-2">
          <span className="text-[#B4C7E7]">消耗灵值:</span>
          <span className="text-red-400 font-semibold">-{billingInfo.consumedLingzhi}</span>
        </div>
      )}
      {billingInfo.earnedLingzhi > 0 && (
        <div className="flex items-center gap-2">
          <span className="text-[#B4C7E7]">获得灵值:</span>
          <span className="text-green-400 font-semibold">+{billingInfo.earnedLingzhi}</span>
        </div>
      )}
    </div>
    <p className="text-xs text-[#B4C7E7]/60 mt-2">
      计费规则：每5分钟消耗1灵值，提交反馈可获得灵值奖励
    </p>
  </div>
)}
```

**显示内容**:
1. **对话时长**: 显示当前对话的总时长（分钟/秒）
2. **消耗灵值**: 当消耗灵值 > 0 时显示，红色标注
3. **获得灵值**: 当获得灵值 > 0 时显示，绿色标注
4. **计费规则提示**: 显示计费规则的简要说明

**显示条件**: 仅在对话进行中（`isBilling = true`）时显示

**样式特点**:
- 使用助手消息气泡样式（深色背景）
- 响应式布局（移动端友好）
- 流畅的过渡动画
- 清晰的颜色区分（消耗/获得）

---

## 文件修改清单

### 后端修改
- `admin-backend/routes/agent.py`: 新增 `submit_agent_feedback` 路由

### 前端修改
- `web-app/src/pages/Chat.tsx`:
  - 修复 `handleFeedback` 函数
  - 新增灵值计费显示组件

---

## 测试验证

### 后端API测试
```bash
curl -X POST https://meiyueart.com/api/feedback \
  -H "Content-Type: application/json" \
  -H "X-User-ID: 1" \
  -d '{
    "type": "helpful",
    "question": "测试反馈",
    "agent_id": 1
  }'
```

**预期响应**:
```json
{
  "success": true,
  "message": "反馈提交成功",
  "data": {
    "contributionValue": 10
  }
}
```

### 前端功能测试
1. 打开对话页面
2. 发送一条消息
3. 查看是否显示灵值计费信息
4. 点击"反馈"按钮
5. 选择反馈类型并提交
6. 查看是否显示奖励灵值

---

## 数据库结构

### feedback 表结构
```sql
CREATE TABLE IF NOT EXISTS feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    type TEXT NOT NULL,  -- helpful / not_helpful / suggestion
    question TEXT,
    comment TEXT,
    rating INTEGER,
    contribution_value INTEGER NOT NULL,
    created_at TEXT NOT NULL
)
```

### users 表相关字段
```sql
-- 用户灵值字段
total_lingzhi INTEGER DEFAULT 0
```

---

## 灵值计费规则

### 消耗规则
- **计费单位**: 每5分钟消耗1灵值
- **计费方式**: 不足5分钟按5分钟计算
- **计算公式**: `消耗灵值 = ceil(对话时长(秒) / 300)`

### 奖励规则
| 反馈类型 | 奖励灵值 | 说明 |
|---------|---------|------|
| helpful | 10 | 认为回复有帮助 |
| not_helpful | 5 | 认为回复无帮助 |
| suggestion | 15 | 提供建议或改进意见 |

---

## 部署信息

- **部署时间**: 2026年2月18日 22:50
- **生产环境**: https://meiyueart.com
- **后端服务**: http://127.0.0.1:5000

---

## 后续优化建议

1. **防刷机制**
   - 添加用户每日反馈次数限制
   - 添加反馈间隔时间限制

2. **灵值记录**
   - 记录灵值消耗和获得的详细日志
   - 提供灵值流水查询功能

3. **反馈分析**
   - 统计用户反馈数据
   - 分析智能体回复质量
   - 优化智能体回复策略

4. **用户通知**
   - 反馈提交成功后显示Toast通知（替代alert）
   - 灵值变化时显示动画效果

---

## 总结

本次修复成功解决了两个关键问题：

1. ✅ **反馈功能修复**: 新增后端反馈API路由，修复前端API调用，用户现在可以正常提交反馈并获得灵值奖励。

2. ✅ **灵值显示修复**: 新增灵值计费信息显示组件，用户可以实时查看对话消耗和获得的灵值。

修复后的系统提供了更好的用户体验和更透明的灵值管理机制。
