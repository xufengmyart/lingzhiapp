"""
用户旅程引导工具

帮助智能体识别用户所处的旅程阶段，并提供相应的引导策略。
支持从新用户到合伙人的完整旅程管理。
"""

import json
import os
from datetime import datetime, timedelta
from langchain.tools import tool
from langchain.tools import ToolRuntime

# 用户旅程阶段常量
STAGE_LOGIN_REGISTER = "login_register"  # 登录/注册
STAGE_SYSTEM_EXPERIENCE = "system_experience"  # 系统体验
STAGE_SYSTEM_UNDERSTANDING = "system_understanding"  # 系统了解
STAGE_PATH_SELECTION = "path_selection"  # 选择路径
STAGE_GAIN_LINGZHI = "gain_lingzhi"  # 获得灵值
STAGE_CONSUME_LINGZHI = "consume_lingzhi"  # 兑换/消费灵值
STAGE_PARTNER = "partner"  # 成为合伙人

# 参与级别常量
LEVEL_LIGHT = "light"  # 轻度参与
LEVEL_MEDIUM = "medium"  # 中度参与
LEVEL_DEEP = "deep"  # 深度参与

# 用户旅程数据文件路径
USER_JOURNEY_FILE = "assets/user_journey_data.json"


def _load_journey_data():
    """加载用户旅程数据"""
    try:
        if os.path.exists(USER_JOURNEY_FILE):
            with open(USER_JOURNEY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}


def _save_journey_data(data):
    """保存用户旅程数据"""
    try:
        # 确保assets目录存在
        os.makedirs(os.path.dirname(USER_JOURNEY_FILE), exist_ok=True)
        
        with open(USER_JOURNEY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        return False


def _get_user_stage(user_id: str) -> str:
    """
    根据用户信息判断当前所处的旅程阶段
    
    Args:
        user_id: 用户ID
    
    Returns:
        当前旅程阶段
    """
    data = _load_journey_data()
    
    if user_id not in data:
        return STAGE_LOGIN_REGISTER
    
    user_data = data[user_id]
    
    # 检查是否达到合伙人资格
    total_lingzhi = user_data.get("total_lingzhi", 0)
    if total_lingzhi >= 10000:
        return STAGE_PARTNER
    
    # 检查是否有兑换/消费记录
    if user_data.get("has_consumed", False):
        return STAGE_CONSUME_LINGZHI
    
    # 检查是否开始获得灵值
    if user_data.get("total_lingzhi", 0) > 10:
        return STAGE_GAIN_LINGZHI
    
    # 检查是否已选择路径
    if user_data.get("path_selected", False):
        return STAGE_GAIN_LINGZHI
    
    # 检查是否了解系统
    interaction_count = user_data.get("interaction_count", 0)
    if interaction_count >= 3:
        return STAGE_SYSTEM_UNDERSTANDING
    
    # 检查是否已体验系统
    if interaction_count >= 1:
        return STAGE_SYSTEM_EXPERIENCE
    
    return STAGE_LOGIN_REGISTER


def _get_participation_level(avg_daily_lingzhi: float) -> str:
    """
    根据日均灵值获取参与级别
    
    Args:
        avg_daily_lingzhi: 日均灵值
    
    Returns:
        参与级别
    """
    if avg_daily_lingzhi >= 1000:
        return LEVEL_DEEP
    elif avg_daily_lingzhi >= 300:
        return LEVEL_MEDIUM
    else:
        return LEVEL_LIGHT


@tool
def get_user_journey_stage(user_id: str, runtime: ToolRuntime) -> str:
    """
    获取用户当前所处的旅程阶段
    
    Args:
        user_id: 用户ID（可以是用户名、手机号或唯一标识）
    
    Returns:
        用户旅程阶段及相应的引导建议
    """
    stage = _get_user_stage(user_id)
    
    stage_info = {
        STAGE_LOGIN_REGISTER: {
            "stage": "登录/注册",
            "stage_code": stage,
            "description": "新用户首次访问，需要完成注册和实名认证",
            "next_actions": [
                "完成实名认证",
                "设置收款方式",
                "了解灵值经济体系"
            ],
            "expected_lingzhi": 10
        },
        STAGE_SYSTEM_EXPERIENCE: {
            "stage": "系统体验",
            "stage_code": stage,
            "description": "用户已完成1-3次互动，需要快速体验系统功能",
            "next_actions": [
                "完成文化探索任务",
                "进行智能对话",
                "回答知识问答"
            ],
            "expected_lingzhi": 20
        },
        STAGE_SYSTEM_UNDERSTANDING: {
            "stage": "系统了解",
            "stage_code": stage,
            "description": "用户正在了解灵值经济体系和获得灵值的途径",
            "next_actions": [
                "深入了解灵值经济体系",
                "了解获得灵值的各种途径",
                "选择适合的获得灵值路径"
            ],
            "expected_lingzhi": 50
        },
        STAGE_PATH_SELECTION: {
            "stage": "选择路径",
            "stage_code": stage,
            "description": "用户正在选择获得灵值的具体路径",
            "next_actions": [
                "选择轻松获得灵值路径",
                "选择项目获得灵值路径",
                "选择推荐获得灵值路径"
            ],
            "expected_lingzhi": 100
        },
        STAGE_GAIN_LINGZHI: {
            "stage": "获得灵值",
            "stage_code": stage,
            "description": "用户已开始执行获得灵值的行动",
            "next_actions": [
                "持续完成每日任务",
                "参与项目获得更多灵值",
                "设置长期灵值目标"
            ],
            "expected_lingzhi": 300
        },
        STAGE_CONSUME_LINGZHI: {
            "stage": "兑换/消费灵值",
            "stage_code": stage,
            "description": "用户开始使用灵值进行兑换或消费",
            "next_actions": [
                "选择兑换或锁定灵值",
                "使用灵值消费服务",
                "规划灵值使用策略"
            ],
            "expected_lingzhi": 500
        },
        STAGE_PARTNER: {
            "stage": "成为合伙人",
            "stage_code": stage,
            "description": "用户已达到合伙人资格，可以申请成为合伙人",
            "next_actions": [
                "申请成为合伙人",
                "了解合伙人权益",
                "开始合伙人发展路径"
            ],
            "expected_lingzhi": 10000
        }
    }
    
    info = stage_info.get(stage, stage_info[STAGE_LOGIN_REGISTER])
    
    result = f"""
📍 当前阶段：{info['stage']}（{info['stage_code']}）

📝 阶段描述：
{info['description']}

🎯 建议行动：
"""
    for i, action in enumerate(info['next_actions'], 1):
        result += f"{i}. {action}\n"
    
    result += f"""
💰 目标灵值：{info['expected_lingzhi']}灵值
"""
    
    return result


@tool
def update_user_journey_progress(
    user_id: str,
    lingzhi_gained: int = 0,
    interaction_count: int = 1,
    path_selected: str = "",
    has_consumed: bool = False,
    runtime: ToolRuntime = None
) -> str:
    """
    更新用户旅程进度
    
    Args:
        user_id: 用户ID
        lingzhi_gained: 本次获得的灵值数量
        interaction_count: 本次互动次数（默认1）
        path_selected: 选择的路径（light/medium/deep）
        has_consumed: 是否已进行过兑换或消费
    
    Returns:
        更新结果及当前进度
    """
    data = _load_journey_data()
    
    # 初始化用户数据
    if user_id not in data:
        data[user_id] = {
            "user_id": user_id,
            "first_login": datetime.now().isoformat(),
            "total_lingzhi": 0,
            "interaction_count": 0,
            "path_selected": False,
            "has_consumed": False,
            "stage_history": []
        }
    
    user_data = data[user_id]
    
    # 更新数据
    if lingzhi_gained > 0:
        user_data["total_lingzhi"] += lingzhi_gained
    
    user_data["interaction_count"] += interaction_count
    
    if path_selected:
        user_data["path_selected"] = True
        user_data["participation_level"] = path_selected
    
    if has_consumed:
        user_data["has_consumed"] = has_consumed
    
    # 更新阶段
    current_stage = _get_user_stage(user_id)
    if current_stage != user_data.get("current_stage"):
        user_data["stage_history"].append({
            "stage": current_stage,
            "timestamp": datetime.now().isoformat(),
            "total_lingzhi": user_data["total_lingzhi"]
        })
    
    user_data["current_stage"] = current_stage
    user_data["last_updated"] = datetime.now().isoformat()
    
    # 保存数据
    if _save_journey_data(data):
        stage_names = {
            STAGE_LOGIN_REGISTER: "登录/注册",
            STAGE_SYSTEM_EXPERIENCE: "系统体验",
            STAGE_SYSTEM_UNDERSTANDING: "系统了解",
            STAGE_PATH_SELECTION: "选择路径",
            STAGE_GAIN_LINGZHI: "获得灵值",
            STAGE_CONSUME_LINGZHI: "兑换/消费灵值",
            STAGE_PARTNER: "成为合伙人"
        }
        
        return f"""
✅ 用户旅程进度已更新！

👤 用户ID：{user_id}
📍 当前阶段：{stage_names.get(current_stage, current_stage)}
💰 总灵值：{user_data['total_lingzhi']}灵值
💵 当前价值：{user_data['total_lingzhi'] * 0.1}元
🔄 互动次数：{user_data['interaction_count']}次
🎯 参与级别：{user_data.get('participation_level', '未选择')}
⏰ 最后更新：{datetime.fromisoformat(user_data['last_updated']).strftime('%Y-%m-%d %H:%M:%S')}
"""
    else:
        return "❌ 更新失败，请重试。"


@tool
def get_journey_recommended_path(
    user_id: str,
    available_time: int,
    interest: str,
    runtime: ToolRuntime
) -> str:
    """
    根据用户情况推荐获得灵值的最佳路径
    
    Args:
        user_id: 用户ID
        available_time: 每天可用时间（分钟）
        interest: 用户兴趣（culture/business/social/all）
    
    Returns:
        推荐路径及预期收益
    """
    # 根据时间和兴趣推荐路径
    if available_time < 30:
        # 时间少，推荐轻松获得灵值
        recommended_level = LEVEL_LIGHT
        daily_tasks = [
            "每日签到：10灵值/天",
            "文化探索：5-20灵值/次",
            "简单问答：5-15灵值/次"
        ]
        daily_lingzhi = 30
        monthly_income = 90
    elif available_time < 120:
        # 时间中等，推荐项目获得灵值
        recommended_level = LEVEL_MEDIUM
        daily_tasks = [
            "每日签到：10灵值/天",
            "参与项目任务：50-200灵值/项目",
            "文化探索：5-20灵值/次"
        ]
        daily_lingzhi = 300
        monthly_income = 900
    else:
        # 时间充足，推荐深度参与
        recommended_level = LEVEL_DEEP
        daily_tasks = [
            "每日签到：10灵值/天",
            "参与高价值项目：100-1000灵值/项目",
            "文化探索：5-20灵值/次",
            "推荐好友：获得推荐分红"
        ]
        daily_lingzhi = 1000
        monthly_income = 3000
    
    result = f"""
🎯 根据您的情况，我推荐您选择：**{recommended_level.upper()}级参与路径**

---

## 📊 路径详情

### 💰 预期收益
- 日均获得：{daily_lingzhi}灵值
- 月收入：约{monthly_income}元
- 年收入：约{monthly_income * 12}元
- 锁定增值：额外20%-100%收益

### 📝 每日任务
"""
    for task in daily_tasks:
        result += f"- {task}\n"
    
    result += f"""
### ⏰ 时间投入
- 每日可用时间：{available_time}分钟
- 推荐参与级别：{recommended_level}

### 🚀 升级路径
如果您想要获得更高收入，可以：
1. 增加每日参与时间
2. 提升任务完成质量
3. 发展推荐网络
4. 申请成为合伙人

### 💡 下一步
建议您立即开始执行每日任务，积累您的第一个10灵值！
"""
    
    # 自动更新用户路径选择
    update_user_journey_progress(
        user_id=user_id,
        lingzhi_gained=0,
        interaction_count=0,
        path_selected=recommended_level,
        has_consumed=False
    )
    
    return result


@tool
def get_journey_milestone(user_id: str, runtime: ToolRuntime) -> str:
    """
    获取用户旅程里程碑和成就
    
    Args:
        user_id: 用户ID
    
    Returns:
        用户里程碑和成就信息
    """
    data = _load_journey_data()
    
    if user_id not in data:
        return """
📍 您还没有开始您的旅程！

立即开始，完成以下里程碑：
- 🎯 里程碑1：获得第一个10灵值（1元）
- 🎯 里程碑2：累计获得100灵值（10元）
- 🎯 里程碑3：累计获得1000灵值（100元）
- 🎯 里程碑4：累计获得10000灵值（1000元）- 成为合伙人
"""
    
    user_data = data[user_id]
    total_lingzhi = user_data.get("total_lingzhi", 0)
    
    milestones = [
        {"lingzhi": 10, "name": "初次收获", "reward": "解锁提现功能"},
        {"lingzhi": 100, "name": "积累达人", "reward": "获得积累达人勋章"},
        {"lingzhi": 500, "name": "灵值先锋", "reward": "获得灵值先锋勋章"},
        {"lingzhi": 1000, "name": "价值创造者", "reward": "获得价值创造者勋章"},
        {"lingzhi": 5000, "name": "生态共建者", "reward": "获得生态共建者勋章"},
        {"lingzhi": 10000, "name": "合伙人资格", "reward": "成为正式合伙人"}
    ]
    
    result = f"""
🏆 用户旅程里程碑

📊 当前进度：
💰 总灵值：{total_lingzhi}灵值
💵 当前价值：{total_lingzhi * 0.1}元
🎯 参与级别：{user_data.get('participation_level', '未选择')}

---

## 🏅 里程碑成就

"""
    
    for milestone in milestones:
        lingzhi = milestone["lingzhi"]
        name = milestone["name"]
        reward = milestone["reward"]
        
        if total_lingzhi >= lingzhi:
            result += f"✅ {name}（{lingzhi}灵值）- 已完成\n   奖励：{reward}\n\n"
        else:
            remaining = lingzhi - total_lingzhi
            result += f"⬜ {name}（{lingzhi}灵值）- 距离还有{remaining}灵值\n   奖励：{reward}\n\n"
    
    # 添加阶段历史
    if "stage_history" in user_data and user_data["stage_history"]:
        stage_names = {
            STAGE_LOGIN_REGISTER: "登录/注册",
            STAGE_SYSTEM_EXPERIENCE: "系统体验",
            STAGE_SYSTEM_UNDERSTANDING: "系统了解",
            STAGE_PATH_SELECTION: "选择路径",
            STAGE_GAIN_LINGZHI: "获得灵值",
            STAGE_CONSUME_LINGZHI: "兑换/消费灵值",
            STAGE_PARTNER: "成为合伙人"
        }
        
        result += "---\n## 📈 旅程历程\n\n"
        for stage_record in user_data["stage_history"]:
            stage = stage_record["stage"]
            timestamp = stage_record["timestamp"]
            lingzhi_at_stage = stage_record["total_lingzhi"]
            formatted_time = datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            result += f"⏰ {formatted_time}\n"
            result += f"   阶段：{stage_names.get(stage, stage)}\n"
            result += f"   当时的灵值：{lingzhi_at_stage}灵值\n\n"
    
    return result


@tool
def get_new_user_guide(user_id: str, runtime: ToolRuntime) -> str:
    """
    获取新用户引导指南
    
    Args:
        user_id: 用户ID
    
    Returns:
        新用户引导指南
    """
    guide = f"""
# 🎉 欢迎来到灵值生态园！

亲爱的用户，欢迎您加入**灵值生态**大家庭！我是您的专属向导**灵值生态园**，将陪伴您完成从新手到合伙人的完整旅程。

---

## 🌟 第一步：完成注册准备

### ✅ 实名认证
完成实名认证后，您将：
- 解锁全部功能
- 获得提现资格
- 开始积累您的数字资产

### ✅ 设置收款方式
设置收款方式后，您可以：
- 随时将灵值兑换为现金
- T+1到账（工作日）
- 0手续费

---

## 💰 第二步：了解核心价值

### 灵值 = 贡献值 = 现金

**1灵值 = 0.1元人民币**（100%确定）

这不是"可能"，而是"一定"！

### 双重收益机制
1. **即时收益**：随时兑换现金，T+1到账
2. **长期收益**：锁定增值，享受20%-100%收益

---

## 🚀 第三步：开始您的第一个任务

### 🎯 今日小目标
**获得您的第一个10灵值**（=1元人民币）

### 📝 如何实现
1. **与我对话**：每次有意义的对话都能获得灵值
2. **提出创意**：分享您的文化创意或商业想法
3. **参与话题**：讨论西安文化、唐风美学等话题

### 💰 您的第一个收入
当您积累到**10灵值**时，就可以：
- **立即兑换1元**到您的账户
- **或选择锁定**获得增值收益

---

## 📊 收入预期

### 轻度参与（每天10分钟）
- 日收入：约3元（30灵值/天）
- 月收入：约90元
- 年收入：约1,080元

### 中度参与（每天30分钟）
- 日收入：约30元（300灵值/天）
- 月收入：约900元
- 年收入：约10,800元

### 深度参与（每天60分钟）
- 日收入：约100元（1,000灵值/天）
- 月收入：约3,000元
- 年收入：约36,000元

---

## 🏆 里程碑成就

- 🎯 **初次收获**：获得10灵值（1元）
- 🎯 **积累达人**：获得100灵值（10元）
- 🎯 **灵值先锋**：获得500灵值（50元）
- 🎯 **价值创造者**：获得1,000灵值（100元）
- 🎯 **生态共建者**：获得5,000灵值（500元）
- 🎯 **合伙人资格**：获得10,000灵值（1,000元）

---

## 🤝 成为合伙人

当您累计获得**10,000灵值**时，您将：
- ✅ 获得更高的推荐分红比例（15%/8%/5%）
- ✅ 优先参与高价值项目
- ✅ 获得专属合伙人咨询服务
- ✅ 免费参加线下活动
- ✅ 获得公司股权期权

---

## 💡 我的承诺

作为您的专属向导，我承诺：

1. **全程陪伴**：无论您遇到什么问题，我都在这里帮助您
2. **透明公开**：所有规则清晰透明，没有隐藏费用
3. **价值保障**：每一灵值都锚定0.1元，随时可兑换
4. **持续创新**：不断推出新的功能和机会

---

## 🎉 开始您的旅程

现在，请告诉我：

**您想从哪个话题开始？**

1. 📊 **商业价值**：了解如何通过灵值获得收入
2. 🎭 **文化探索**：探索西安文化与唐风美学
3. 🤝 **社交互动**：与志同道合的朋友交流
4. 🎯 **立即开始**：获得您的第一个灵值

我会用**双螺旋服务法**，将您的**实际需求**与**精神价值**完美融合，陪伴您走好每一步！ 🌈

---

**记住**：**每一次对话都是价值的积累，每一个创意都是财富的种子**。

**现在，开始您的灵值生态探索之旅吧！** 🚀
"""
    
    # 自动记录用户开始旅程
    update_user_journey_progress(
        user_id=user_id,
        lingzhi_gained=0,
        interaction_count=1,
        path_selected="",
        has_consumed=False
    )
    
    return guide
