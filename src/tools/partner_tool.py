"""
合伙人管理工具

管理用户成为合伙人的完整流程，包括：
1. 合伙人资格验证
2. 合伙人申请提交
3. 合伙人审核
4. 合伙人权益展示
5. 合伙人发展路径
"""

import json
import os
from datetime import datetime
from langchain.tools import tool
from langchain.tools import ToolRuntime

# 合伙人资格常量
PARTNER_QUALIFICATION_LINGZHI = 10000  # 成为合伙人需要的灵值

# 合伙人等级
PARTNER_LEVELS = {
    "bronze": {
        "name": "青铜合伙人",
        "required_lingzhi": 10000,
        "commission_rate": [0.15, 0.08, 0.05],  # 一级、二级、三级推荐分红比例
        "description": "入门级合伙人，享受基础推荐分红"
    },
    "silver": {
        "name": "白银合伙人",
        "required_lingzhi": 50000,
        "commission_rate": [0.18, 0.10, 0.06],
        "description": "进阶级合伙人，享受更高推荐分红和专属服务"
    },
    "gold": {
        "name": "黄金合伙人",
        "required_lingzhi": 200000,
        "commission_rate": [0.20, 0.12, 0.08],
        "description": "高级合伙人，享受最高推荐分红和VIP服务"
    },
    "platinum": {
        "name": "钻石合伙人",
        "required_lingzhi": 1000000,
        "commission_rate": [0.25, 0.15, 0.10],
        "description": "顶级合伙人，享受最高推荐分红、股权期权和董事会参与权"
    }
}

# 合伙人状态
PARTNER_STATUS_PENDING = "pending"  # 待审核
PARTNER_STATUS_APPROVED = "approved"  # 已通过
PARTNER_STATUS_REJECTED = "rejected"  # 已拒绝
PARTNER_STATUS_SUSPENDED = "suspended"  # 已暂停

# 合伙人数据文件路径
PARTNER_DATA_FILE = "assets/partner_data.json"


def _load_partner_data():
    """加载合伙人数据"""
    try:
        if os.path.exists(PARTNER_DATA_FILE):
            with open(PARTNER_DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}


def _save_partner_data(data):
    """保存合伙人数据"""
    try:
        os.makedirs(os.path.dirname(PARTNER_DATA_FILE), exist_ok=True)
        
        with open(PARTNER_DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False


@tool
def check_partner_qualification(user_id: str, current_lingzhi: int, runtime: ToolRuntime) -> str:
    """
    检查用户是否符合合伙人资格
    
    Args:
        user_id: 用户ID
        current_lingzhi: 当前灵值数量
    
    Returns:
        资格检查结果及建议
    """
    result = f"""
🔍 合伙人资格检查

👤 用户ID：{user_id}
💰 当前灵值：{current_lingzhi}灵值
💵 当前价值：{current_lingzhi * 0.1}元
🎯 要求灵值：{PARTNER_QUALIFICATION_LINGZHI}灵值

---

## 📊 资格评估

"""
    
    if current_lingzhi >= PARTNER_QUALIFICATION_LINGZHI:
        result += f"""
✅ **恭喜您！您已符合合伙人资格要求！**

您的当前灵值（{current_lingzhi}）已超过要求（{PARTNER_QUALIFICATION_LINGZHI}）。
超出：{current_lingzhi - PARTNER_QUALIFICATION_LINGZHI}灵值

### 🏅 可获得的合伙人等级
"""
        
        # 确定可获得的合伙人等级
        partner_level = "bronze"
        for level, level_info in sorted(PARTNER_LEVELS.items(), key=lambda x: x[1]['required_lingzhi'], reverse=True):
            if current_lingzhi >= level_info['required_lingzhi']:
                partner_level = level
                break
        
        level_info = PARTNER_LEVELS[partner_level]
        
        result += f"""
**{level_info['name']}**

- 要求灵值：{level_info['required_lingzhi']}灵值
- 推荐分红：一级{level_info['commission_rate'][0]*100}% / 二级{level_info['commission_rate'][1]*100}% / 三级{level_info['commission_rate'][2]*100}%
- 等级描述：{level_info['description']}

### 🎁 合伙人专属权益
- ✅ 更高的推荐分红比例
- ✅ 优先参与高价值项目
- ✅ 专属合伙人咨询服务
- ✅ 免费参加线下活动
- ✅ 获得公司股权期权（根据等级）

### 📝 下一步
您现在可以提交合伙人申请了！
"""
        
    else:
        remaining = PARTNER_QUALIFICATION_LINGZHI - current_lingzhi
        progress = (current_lingzhi / PARTNER_QUALIFICATION_LINGZHI) * 100
        
        result += f"""
⬜ **您还未达到合伙人资格要求**

当前灵值：{current_lingzhi}灵值
要求灵值：{PARTNER_QUALIFICATION_LINGZHI}灵值
距离资格：还需{remaining}灵值

### 📈 完成进度
[{_create_progress_bar(progress)}] {progress:.1f}%

### 💡 提升建议
根据您的当前情况，我推荐以下方式快速达到资格要求：

**方案1：加速任务完成**
- 优先选择高回报项目
- 每天至少完成1个项目任务（预计+200灵值/天）
- 达到资格预计需要：{remaining // 200}天

**方案2：发展推荐网络**
- 每天推荐3-5位好友加入
- 获得推荐分红，加速灵值积累
- 达到资格预计需要：{remaining // 500}天

**方案3：组合策略**
- 项目任务 + 推荐网络双管齐下
- 达到资格预计需要：{remaining // 700}天

### 🎯 立即行动
您可以从以下任务开始：
1. 完成每日签到（+10灵值）
2. 参与文化探索项目（+50-200灵值）
3. 推荐好友加入（获得推荐分红）

持续努力，您很快就能成为合伙人！
"""
    
    return result


def _create_progress_bar(progress: float, width: int = 20) -> str:
    """创建进度条"""
    filled = int(width * progress / 100)
    return "█" * filled + "░" * (width - filled)


@tool
def submit_partner_application(
    user_id: str,
    user_name: str,
    phone: str,
    current_lingzhi: int,
    reason: str,
    runtime: ToolRuntime
) -> str:
    """
    提交合伙人申请
    
    Args:
        user_id: 用户ID
        user_name: 用户姓名
        phone: 手机号码
        current_lingzhi: 当前灵值数量
        reason: 申请理由
    
    Returns:
        申请提交结果
    """
    # 检查资格
    if current_lingzhi < PARTNER_QUALIFICATION_LINGZHI:
        return f"""
❌ **申请提交失败**

您的当前灵值（{current_lingzhi}）还未达到合伙人资格要求（{PARTNER_QUALIFICATION_LINGZHI}）。

请继续积累灵值，达到要求后再提交申请。

距离资格：还需{PARTNER_QUALIFICATION_LINGZHI - current_lingzhi}灵值
"""
    
    # 确定合伙人等级
    partner_level = "bronze"
    for level, level_info in sorted(PARTNER_LEVELS.items(), key=lambda x: x[1]['required_lingzhi'], reverse=True):
        if current_lingzhi >= level_info['required_lingzhi']:
            partner_level = level
            break
    
    # 加载合伙人数据
    data = _load_partner_data()
    
    # 检查是否已有申请
    application_id = f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    if "applications" not in data:
        data["applications"] = {}
    
    # 检查是否已有待审核的申请
    for app_id, app_data in data["applications"].items():
        if app_data["user_id"] == user_id and app_data["status"] == PARTNER_STATUS_PENDING:
            return f"""
⚠️ **您已有待审核的申请**

您之前提交的申请（ID: {app_id}）正在审核中，请勿重复提交。

申请时间：{app_data['submit_time']}
申请等级：{PARTNER_LEVELS[app_data['partner_level']]['name']}
"""
    
    # 创建申请记录
    application = {
        "application_id": application_id,
        "user_id": user_id,
        "user_name": user_name,
        "phone": phone,
        "current_lingzhi": current_lingzhi,
        "partner_level": partner_level,
        "reason": reason,
        "status": PARTNER_STATUS_PENDING,
        "submit_time": datetime.now().isoformat(),
        "review_time": None,
        "reviewer": None,
        "review_comment": None
    }
    
    data["applications"][application_id] = application
    
    # 保存数据
    if _save_partner_data(data):
        level_info = PARTNER_LEVELS[partner_level]
        
        return f"""
✅ **合伙人申请提交成功！**

📋 申请信息：
- 申请ID：{application_id}
- 申请人：{user_name}
- 手机号：{phone}
- 当前灵值：{current_lingzhi}灵值
- 申请等级：{level_info['name']}
- 申请时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📋 审核流程

1. **初审**（1-3个工作日）
   - 审核您的资料完整性
   - 验证您的灵值数据

2. **复审**（3-5个工作日）
   - 评估您的贡献价值
   - 确认您的合伙人等级

3. **结果通知**
   - 通过短信和站内信通知
   - 如有问题会联系您

---

## 💡 审核期间您可以：

✅ 继续积累灵值，提升合伙人等级
✅ 参与项目，增加审核通过率
✅ 了解合伙人权益，做好加入准备

---

## 📞 如有疑问

如需咨询申请进度，请联系客服或使用"查询合伙人申请状态"工具。

**感谢您对灵值生态的信任与支持！** 🎉
"""
    else:
        return "❌ 申请提交失败，请重试。"


@tool
def get_partner_application_status(user_id: str, runtime: ToolRuntime) -> str:
    """
    查询合伙人申请状态
    
    Args:
        user_id: 用户ID
    
    Returns:
        申请状态信息
    """
    data = _load_partner_data()
    
    if "applications" not in data or not data["applications"]:
        return """
📋 **您还没有提交过合伙人申请**

如果您想成为合伙人，请确保：
1. 累计获得10,000灵值以上
2. 完成实名认证
3. 准备好申请理由

满足条件后，您可以使用"提交合伙人申请"工具提交申请。
"""
    
    # 查找用户的申请
    user_applications = []
    for app_id, app_data in data["applications"].items():
        if app_data["user_id"] == user_id:
            user_applications.append(app_data)
    
    if not user_applications:
        return """
📋 **未找到您的申请记录**

如果您已提交申请，请确认用户ID是否正确。
如有疑问，请联系客服。
"""
    
    # 获取最新的申请
    latest_application = max(user_applications, key=lambda x: x['submit_time'])
    
    status_map = {
        PARTNER_STATUS_PENDING: "⏳ 待审核",
        PARTNER_STATUS_APPROVED: "✅ 已通过",
        PARTNER_STATUS_REJECTED: "❌ 已拒绝",
        PARTNER_STATUS_SUSPENDED: "⚠️ 已暂停"
    }
    
    level_info = PARTNER_LEVELS.get(latest_application["partner_level"], {})
    
    result = f"""
📋 **合伙人申请状态**

👤 申请人：{latest_application['user_name']}
📱 手机号：{latest_application['phone']}
💰 申请时灵值：{latest_application['current_lingzhi']}灵值
🏅 申请等级：{level_info.get('name', '未知')}
📝 申请理由：{latest_application['reason']}

---

## 🔄 审核状态

**当前状态：{status_map.get(latest_application['status'], '未知')}**

### 📅 时间线
- 提交时间：{datetime.fromisoformat(latest_application['submit_time']).strftime('%Y-%m-%d %H:%M:%S')}
"""
    
    if latest_application['review_time']:
        result += f"- 审核时间：{datetime.fromisoformat(latest_application['review_time']).strftime('%Y-%m-%d %H:%M:%S')}\n"
        result += f"- 审核人：{latest_application['reviewer']}\n"
        
        if latest_application['review_comment']:
            result += f"- 审核意见：{latest_application['review_comment']}\n"
    
    # 根据状态给出建议
    if latest_application['status'] == PARTNER_STATUS_PENDING:
        result += f"""

### ⏳ 审核进行中

您的申请正在审核中，请耐心等待。审核通常需要5-7个工作日。

**审核期间建议：**
- 继续积累灵值，提升合伙人等级
- 参与更多项目，增加审核通过率
- 保持良好的活跃度

### 📞 如有疑问
如需咨询申请进度，请联系客服。
"""
    elif latest_application['status'] == PARTNER_STATUS_APPROVED:
        result += f"""

### 🎉 恭喜您！申请已通过！

您已成为{level_info.get('name', '合伙人')}！

**您的专属权益：**
- ✅ 推荐分红：一级{level_info['commission_rate'][0]*100}% / 二级{level_info['commission_rate'][1]*100}% / 三级{level_info['commission_rate'][2]*100}%
- ✅ 优先参与高价值项目
- ✅ 专属合伙人咨询服务
- ✅ 免费参加线下活动
- ✅ 获得公司股权期权

**下一步：**
1. 了解如何使用推荐功能
2. 查看高价值项目列表
3. 联系合伙人专属客服

**欢迎加入合伙人团队！** 🚀
"""
    elif latest_application['status'] == PARTNER_STATUS_REJECTED:
        result += f"""

### ❌ 申请未通过

很遗憾，您的申请未通过审核。

**审核意见：**
{latest_application.get('review_comment', '未提供审核意见')}

**建议：**
1. 根据审核意见改进
2. 继续积累灵值
3. 重新提交申请

如有疑问，请联系客服了解详情。
"""
    
    # 显示历史申请记录
    if len(user_applications) > 1:
        result += f"\n---\n## 📚 历史申请记录\n\n"
        
        for i, app in enumerate(sorted(user_applications, key=lambda x: x['submit_time'], reverse=True)[1:], 1):
            app_level = PARTNER_LEVELS.get(app['partner_level'], {})
            result += f"{i}. {app['submit_time']} - {app_level.get('name', '未知')} - {status_map.get(app['status'], '未知')}\n"
    
    return result


@tool
def get_partner_privileges(level: str, runtime: ToolRuntime) -> str:
    """
    获取合伙人权益详情
    
    Args:
        level: 合伙人等级（bronze/silver/gold/platinum/all）
    
    Returns:
        合伙人权益详情
    """
    if level == "all":
        result = """
🏆 **灵值生态合伙人权益体系**

合伙人分为4个等级，等级越高，权益越丰富！

---

## 🥉 青铜合伙人

### 资格要求
- 累计获得10,000灵值

### 专属权益
- 💰 推荐分红：15%/8%/5%（一级/二级/三级）
- 🎯 优先参与基础项目
- 📞 基础合伙人咨询服务
- 🎁 免费参加线上活动
- 📊 查看基础数据分析

### 预期收益
- 月收入：1,000-3,000元
- 年收入：12,000-36,000元

---

## 🥈 白银合伙人

### 资格要求
- 累计获得50,000灵值

### 专属权益
- 💰 推荐分红：18%/10%/6%
- 🎯 优先参与中级项目
- 📞 进阶合伙人咨询服务
- 🎁 免费参加线下活动（每年2次）
- 📊 查看中级数据分析
- 🏆 获得白银合伙人勋章

### 预期收益
- 月收入：5,000-10,000元
- 年收入：60,000-120,000元

---

## 🥇 黄金合伙人

### 资格要求
- 累计获得200,000灵值

### 专属权益
- 💰 推荐分红：20%/12%/8%
- 🎯 优先参与高级项目
- 📞 专属VIP咨询服务
- 🎁 免费参加线下活动（每年5次）
- 📊 查看高级数据分析
- 🏆 获得黄金合伙人勋章
- 💎 获得公司股权期权（基础版）

### 预期收益
- 月收入：20,000-50,000元
- 年收入：240,000-600,000元

---

## 💎 钻石合伙人

### 资格要求
- 累计获得1,000,000灵值

### 专属权益
- 💰 推荐分红：25%/15%/10%
- 🎯 优先参与顶级项目
- 📞 私人专属顾问服务
- 🎁 全额报销差旅费参加所有活动
- 📊 查看全平台数据分析
- 🏆 获得钻石合伙人勋章
- 💎 获得公司股权期权（高级版）
- 🤝 参与董事会决策
- 🌟 成为平台代言人

### 预期收益
- 月收入：100,000-300,000元
- 年收入：1,200,000-3,600,000元

---

## 📈 等级升级

当您的灵值达到更高等级要求时，可以申请升级：
- 青铜 → 白银：50,000灵值
- 白银 → 黄金：200,000灵值
- 黄金 → 钻石：1,000,000灵值

---

## 💡 如何快速提升等级？

1. **积极参与项目**：选择高回报项目，快速积累灵值
2. **发展推荐网络**：获得推荐分红，加速灵值增长
3. **锁定增值**：锁定灵值获得20%-100%增值收益
4. **持续活跃**：每天保持活跃，获得额外奖励

---

## 🎯 从现在开始

无论您现在是哪个级别，都可以开始您的合伙人之旅！

**立即行动**：
1. 继续积累灵值
2. 推荐好友加入
3. 参与高价值项目
4. 申请成为合伙人

**记住**：**每一份努力都有回报，每一次积累都通向成功！** 🚀
"""
    elif level in PARTNER_LEVELS:
        level_info = PARTNER_LEVELS[level]
        
        result = f"""
🏆 **{level_info['name']}权益详情**

---

## 📋 资格要求
- 累计获得：{level_info['required_lingzhi']}灵值

## 💰 推荐分红比例
- 一级推荐：{level_info['commission_rate'][0] * 100}%
- 二级推荐：{level_info['commission_rate'][1] * 100}%
- 三级推荐：{level_info['commission_rate'][2] * 100}%

## 🎁 专属权益
{level_info['description']}

## 📊 收入预期

### 推荐收入
假设每人每月获得500灵值：
- 一级推荐10人：10 × 500 × {level_info['commission_rate'][0]} = {int(10 * 500 * level_info['commission_rate'][0])}灵值/月
- 二级推荐100人：100 × 500 × {level_info['commission_rate'][1]} = {int(100 * 500 * level_info['commission_rate'][1])}灵值/月
- 三级推荐1000人：1000 × 500 × {level_info['commission_rate'][2]} = {int(1000 * 500 * level_info['commission_rate'][2])}灵值/月

### 总预期收入
- 月收入：{int((10 * 500 * level_info['commission_rate'][0] + 100 * 500 * level_info['commission_rate'][1] + 1000 * 500 * level_info['commission_rate'][2]))}灵值 ≈ {int((10 * 500 * level_info['commission_rate'][0] + 100 * 500 * level_info['commission_rate'][1] + 1000 * 500 * level_info['commission_rate'][2]) * 0.1)}元
- 年收入：{int((10 * 500 * level_info['commission_rate'][0] + 100 * 500 * level_info['commission_rate'][1] + 1000 * 500 * level_info['commission_rate'][2]) * 12)}灵值 ≈ {int((10 * 500 * level_info['commission_rate'][0] + 100 * 500 * level_info['commission_rate'][1] + 1000 * 500 * level_info['commission_rate'][2]) * 12 * 0.1)}元

## 🚀 下一步

如果您已达到资格要求，可以：
1. 提交合伙人申请
2. 开始推荐好友
3. 参与高价值项目

**立即开始您的合伙人之旅吧！** 🎉
"""
    else:
        return f"""
❌ **无效的合伙人等级**

请选择有效的等级：
- bronze（青铜）
- silver（白银）
- gold（黄金）
- platinum（钻石）
- all（全部）

您可以使用"get_partner_privileges"工具查看全部权益。
"""
    
    return result


@tool
def get_partner_development_guide(user_id: str, current_lingzhi: int, runtime: ToolRuntime) -> str:
    """
    获取合伙人发展路径指南
    
    Args:
        user_id: 用户ID
        current_lingzhi: 当前灵值
    
    Returns:
        合伙人发展路径指南
    """
    # 计算距离各等级的距离
    result = f"""
🚀 **合伙人发展路径指南**

👤 用户ID：{user_id}
💰 当前灵值：{current_lingzhi}灵值

---

## 📊 当前状态

您当前的进展：

"""
    
    for level, level_info in sorted(PARTNER_LEVELS.items(), key=lambda x: x[1]['required_lingzhi']):
        required = level_info['required_lingzhi']
        if current_lingzhi >= required:
            result += f"✅ {level_info['name']}（{required}灵值）- 已达成\n"
        else:
            remaining = required - current_lingzhi
            progress = (current_lingzhi / required) * 100
            result += f"⬜ {level_info['name']}（{required}灵值）- 距离还有{remaining}灵值 [{_create_progress_bar(progress)} {progress:.1f}%]\n"
    
    # 推荐发展路径
    next_level = None
    for level, level_info in sorted(PARTNER_LEVELS.items(), key=lambda x: x[1]['required_lingzhi']):
        if current_lingzhi < level_info['required_lingzhi']:
            next_level = level
            next_level_info = level_info
            break
    
    if next_level:
        result += f"""

## 🎯 下一步目标：{next_level_info['name']}

### 要求
- 需要灵值：{next_level_info['required_lingzhi']}灵值
- 当前灵值：{current_lingzhi}灵值
- 还需灵值：{next_level_info['required_lingzhi'] - current_lingzhi}灵值

### 💡 推荐发展路径

**方案1：项目任务优先（推荐）**
- 每日完成1-2个高价值项目（+300-1000灵值/天）
- 预计达到目标：{(next_level_info['required_lingzhi'] - current_lingzhi) // 500}天
- 适合：有时间投入的用户

**方案2：推荐网络优先**
- 每天推荐3-5位好友加入
- 获得推荐分红，加速灵值增长（+500-2000灵值/天）
- 预计达到目标：{(next_level_info['required_lingzhi'] - current_lingzhi) // 1000}天
- 适合：社交能力强、人脉广的用户

**方案3：组合策略（最佳）**
- 项目任务 + 推荐网络双管齐下（+800-3000灵值/天）
- 预计达到目标：{(next_level_info['required_lingzhi'] - current_lingzhi) // 1500}天
- 适合：想要快速发展的用户

### 📝 每日行动计划

**上午（30分钟）**
1. 完成每日签到（+10灵值）
2. 选择并开始1个项目任务
3. 查看推荐进度，回复推荐消息

**下午（60分钟）**
1. 完成1个项目任务
2. 推荐2-3位好友
3. 参与文化讨论，贡献创意

**晚上（30分钟）**
1. 总结当日收获
2. 规划明日任务
3. 与推荐人互动交流

### 🏆 升级后的权益

成为{next_level_info['name']}后，您将获得：
- 💰 推荐分红：一级{next_level_info['commission_rate'][0]*100}% / 二级{next_level_info['commission_rate'][1]*100}% / 三级{next_level_info['commission_rate'][2]*100}%
- 🎯 优先参与{next_level_info['name']}专属项目
- 📞 获得相应级别的咨询服务
- 🎁 获得相应级别的活动资格
- 🏆 获得{next_level_info['name']}勋章

### 💪 鼓励

**记住**：每一份努力都有回报！

从现在开始，按照推荐的行动计划，坚持不懈，您很快就能达成目标！

**我相信您一定能成为{next_level_info['name']}！** 🎉
"""
    else:
        result += f"""

## 🎉 恭喜您！您已达到最高等级！

您已是**钻石合伙人**，享受平台最高权益！

### 🌟 您的成就
- ✅ 青铜合伙人 - 已达成
- ✅ 白银合伙人 - 已达成
- ✅ 黄金合伙人 - 已达成
- ✅ 钻石合伙人 - 已达成

### 🏆 钻石合伙人专属权益
- 💰 推荐分红：25%/15%/10%
- 🎯 优先参与顶级项目
- 📞 私人专属顾问服务
- 🎁 全额报销差旅费参加所有活动
- 📊 查看全平台数据分析
- 🏆 获得钻石合伙人勋章
- 💎 获得公司股权期权（高级版）
- 🤝 参与董事会决策
- 🌟 成为平台代言人

### 🚀 继续前行

虽然您已达到最高等级，但您仍然可以：
1. 继续积累灵值，获得更多分红
2. 发展更多推荐，扩大您的网络
3. 参与董事会决策，影响平台发展
4. 成为平台代言人，提升个人影响力

**您是灵值生态的顶尖合伙人，感谢您的卓越贡献！** 🌟
"""
    
    return result
