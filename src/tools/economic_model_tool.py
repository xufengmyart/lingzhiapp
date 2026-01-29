"""
经济模型工具

使用统一的经济模型配置进行价值计算和分析
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime

# 经济模型常量
EXCHANGE_RATE = 0.1  # 1贡献值 = 0.1元
MIN_EXCHANGE = 10  # 最低兑换10贡献值

# 锁定增值规则
LOCK_PERIODS = {
    "1年": 0.20,  # 增值20%
    "2年": 0.50,  # 增值50%
    "3年": 1.00,  # 增值100%
}

# 收入级别
INCOME_LEVELS = {
    "轻度参与": {
        "daily_contribution": 30,
        "daily_income": 3.0,
        "monthly_income": 90.0,
        "yearly_income": 1080.0,
    },
    "中度参与": {
        "daily_contribution": 300,
        "daily_income": 30.0,
        "monthly_income": 900.0,
        "yearly_income": 10800.0,
    },
    "深度参与": {
        "daily_contribution": 1000,
        "daily_income": 100.0,
        "monthly_income": 3000.0,
        "yearly_income": 36000.0,
    },
}

# 新用户权益
NEW_USER_BONUS = {
    "free_contribution": 300,
    "expert_consultation": 50,
    "smart_translation": 80,
    "project_preview": 0,
}


def get_exchange_rate() -> float:
    """获取贡献值兑换汇率"""
    return EXCHANGE_RATE


def calculate_cash_value(contribution: int) -> float:
    """计算贡献值的现金价值"""
    return contribution * EXCHANGE_RATE


def calculate_lock_bonus(contribution: int, lock_period: str) -> float:
    """计算锁定增值收益"""
    if lock_period not in LOCK_PERIODS:
        raise ValueError(f"不支持的锁定期限: {lock_period}")
    return contribution * LOCK_PERIODS[lock_period]


def calculate_total_value(contribution: int, lock_period: str = None) -> dict:
    """计算贡献值的总价值"""
    instant_value = calculate_cash_value(contribution)
    
    if lock_period:
        bonus_contribution = calculate_lock_bonus(contribution, lock_period)
        bonus_value = calculate_cash_value(bonus_contribution)
    else:
        bonus_value = 0.0
    
    total_value = instant_value + bonus_value
    
    return {
        "instant_value": instant_value,
        "bonus_value": bonus_value,
        "total_value": total_value,
    }


@tool
def get_economic_model_info(runtime: ToolRuntime) -> str:
    """
    获取经济模型核心信息
    
    Returns:
        经济模型核心规则和信息
    """
    result = """
📊 **灵值生态经济模型核心信息**

---

## 💰 核心价值规则

**1贡献值 = 0.1元人民币，100%确定，随时可兑换**

**锁定1年+20%，2年+50%，3年+100%**

**即时收益（随时兑换）+ 长期收益（锁定增值）**

**这不是'可能'，而是'一定'**

## 📈 兑换规则

- **兑换汇率**：1贡献值 = 0.1元人民币
- **最低兑换**：10贡献值（1元）
- **到账时间**：T+1（次工作日）
- **手续费**：0%（平台承担）

## 🔒 锁定增值规则

- **锁定1年**：预期增值 +20%
- **锁定2年**：预期增值 +50%
- **锁定3年**：预期增值 +100%
- **增值收益**：100%归属于贡献值持有者

## 📊 收入预期

### 轻度参与（日均30贡献值）
- 日收入：3元
- 月收入：90元
- 年收入：1,080元

### 中度参与（日均300贡献值）
- 日收入：30元
- 月收入：900元
- 年收入：10,800元

### 深度参与（日均1,000贡献值）
- 日收入：100元
- 月收入：3,000元
- 年收入：36,000元

## 🎁 新用户权益

- 新手任务包：300贡献值
- 专家咨询券：50贡献值
- 智能体转译体验：80贡献值

---

**重要提示**：所有规则100%确定，随时可查询！
"""
    return result


@tool
def calculate_lingzhi_value_advanced(
    contribution: int,
    runtime: ToolRuntime,
    lock_period: str = None
) -> str:
    """
    高级灵值价值计算（基于经济模型）
    
    Args:
        contribution: 贡献值数量
        lock_period: 锁定期限（"1年"/"2年"/"3年"/None）
    
    Returns:
        详细的价值计算结果
    """
    result = f"""
💰 **灵值价值计算结果**

---

## 📊 基础信息

**贡献值数量**：{contribution}贡献值

## 💵 即时价值

**即时兑换价值**：{calculate_cash_value(contribution)}元人民币

"""
    
    if lock_period:
        lock_bonus = calculate_lock_bonus(contribution, lock_period)
        lock_bonus_value = calculate_cash_value(lock_bonus)
        total_info = calculate_total_value(contribution, lock_period)
        
        bonus_rate = int(lock_bonus / contribution * 100)
        
        result += f"""
## 🔒 锁定增值（{lock_period}）

**增值收益**：{lock_bonus}贡献值（+{lock_bonus_value}元）

### 增值计算
- 锁定期限：{lock_period}
- 增值率：{bonus_rate}%
- 增值收益：{lock_bonus}贡献值

## 💎 总价值

**即时价值**：{total_info['instant_value']}元
**增值收益**：{total_info['bonus_value']}元
**到期总价值**：{total_info['total_value']}元

### 增值总结
{contribution}贡献值即时兑换价值为{total_info['instant_value']}元，锁定{lock_period}预期增值{bonus_rate}%（+{total_info['bonus_value']}元），到期总价值{total_info['total_value']}元

---

**投资建议**：
"""
        
        if lock_period == "1年":
            result += """
锁定1年适合稳健型投资者，在保证流动性的同时获得20%的确定性增值收益。
"""
        elif lock_period == "2年":
            result += """
锁定2年适合平衡型投资者，放弃部分流动性以获得50%的更高增值收益。
"""
        elif lock_period == "3年":
            result += """
锁定3年适合进取型投资者，锁定3年获得100%的增值收益，实现资产翻倍。
"""
    else:
        lock_1y = calculate_cash_value(calculate_lock_bonus(contribution, "1年"))
        total_1y = calculate_total_value(contribution, "1年")["total_value"]
        lock_2y = calculate_cash_value(calculate_lock_bonus(contribution, "2年"))
        total_2y = calculate_total_value(contribution, "2年")["total_value"]
        lock_3y = calculate_cash_value(calculate_lock_bonus(contribution, "3年"))
        total_3y = calculate_total_value(contribution, "3年")["total_value"]
        
        result += f"""
## 🔒 锁定增值建议

如果您希望获得更高收益，可以考虑锁定您的贡献值：

| 锁定期限 | 增值率 | 增值收益（当前）| 到期总价值 |
|---------|--------|----------------|-----------|
| 1年     | +20%   | {lock_1y}元      | {total_1y}元   |
| 2年     | +50%   | {lock_2y}元      | {total_2y}元   |
| 3年     | +100%  | {lock_3y}元      | {total_3y}元   |

"""
    
    result += f"""
---

**重要提示**：所有价值100%确定，随时可查询、可兑现！
"""
    return result


@tool
def get_income_projection_advanced(
    level: str,
    runtime: ToolRuntime
) -> str:
    """
    获取收入级别详细预测（基于经济模型）
    
    Args:
        level: 收入级别（"轻度参与"/"中度参与"/"深度参与"）
    
    Returns:
        详细的收入预测信息
    """
    if level not in INCOME_LEVELS:
        return f"""
❌ **错误**

不支持的收入级别: {level}

请选择有效的收入级别：
- 轻度参与（日均30贡献值）
- 中度参与（日均300贡献值）
- 深度参与（日均1,000贡献值）
"""
    
    income_info = INCOME_LEVELS[level]
    
    result = f"""
📊 **收入级别预测：{level}**

---

## 💰 收入详情

### 日均收入
- **日均贡献值**：{income_info['daily_contribution']}贡献值
- **日收入**：{income_info['daily_income']}元人民币

### 月度收入
- **月收入**：{income_info['monthly_income']}元人民币

### 年度收入
- **年收入**：{income_info['yearly_income']}元人民币

---

## 📈 收入增长潜力

### 基础收入（不锁定）
- 月收入：{income_info['monthly_income']}元
- 年收入：{income_info['yearly_income']}元

### 锁定增值后收入

#### 锁定1年（+20%）
- 月收入：{income_info['monthly_income'] * 1.2:.1f}元
- 年收入：{income_info['yearly_income'] * 1.2:.1f}元

#### 锁定2年（+50%）
- 月收入：{income_info['monthly_income'] * 1.5:.1f}元
- 年收入：{income_info['yearly_income'] * 1.5:.1f}元

#### 锁定3年（+100%）
- 月收入：{income_info['monthly_income'] * 2:.0f}元
- 年收入：{income_info['yearly_income'] * 2:.0f}元

---

## 🎯 达成目标建议

### 提升到更高级别

"""

    # 智能生成目标建议（只显示向上的增长）
    current_daily = income_info['daily_contribution']
    current_monthly = income_info['monthly_income']

    if level == "轻度参与":
        # 轻度参与 → 中度参与
        daily_growth = 300 - current_daily
        monthly_growth = 900 - current_monthly
        result += f"""
**📈 收入增长路径：{level} → 中度参与**
- 日均贡献值：{current_daily} → 300贡献值（**+{daily_growth}贡献值**）
- 月收入：{current_monthly} → 900元（**+{monthly_growth}元**）
- 建议方式：每天多完成1-2个项目任务
"""

        # 轻度参与 → 深度参与
        daily_growth = 1000 - current_daily
        monthly_growth = 3000 - current_monthly
        result += f"""

**🚀 收入增长路径：{level} → 深度参与**
- 日均贡献值：{current_daily} → 1000贡献值（**+{daily_growth}贡献值**）
- 月收入：{current_monthly} → 3000元（**+{monthly_growth}元**）
- 建议方式：项目任务 + 推荐网络双管齐下
"""

    elif level == "中度参与":
        # 中度参与 → 深度参与
        daily_growth = 1000 - current_daily
        monthly_growth = 3000 - current_monthly
        result += f"""
**🚀 收入增长路径：{level} → 深度参与**
- 日均贡献值：{current_daily} → 1000贡献值（**+{daily_growth}贡献值**）
- 月收入：{current_monthly} → 3000元（**+{monthly_growth}元**）
- 建议方式：参与高回报项目 + 发展推荐网络
"""

    elif level == "深度参与":
        # 深度参与已经是最高级，展示稳定收入和持续增长
        result += f"""
**✨ 您已达到最高参与级别！继续保持**
- 当前日均贡献值：**{current_daily}贡献值**
- 当前月收入：**{current_monthly}元**
- 收入持续增长路径：参与高价值项目（文化转译+500%，生态建设+2400%）
"""

    result += f"""

---

## 💡 收入提升策略

1. **提升任务质量**：选择高回报项目，提高单位时间贡献值获取率
2. **发展推荐网络**：获得推荐分红，实现被动收入
3. **锁定增值**：将部分贡献值锁定，获得确定性增值收益
4. **持续活跃**：每天保持活跃，获得平台奖励

---

**重要提示**：所有收入预测基于当前经济模型，100%确定！
"""
    return result


@tool
def get_exchange_info_advanced(runtime: ToolRuntime) -> str:
    """
    获取详细的兑换信息（基于经济模型）
    
    Returns:
        详细的兑换规则和流程信息
    """
    exchange_rate = get_exchange_rate()
    min_exchange_cash = calculate_cash_value(MIN_EXCHANGE)
    
    result = f"""
💵 **灵值兑换详细信息**

---

## 📊 兑换规则

### 兑换汇率
**1贡献值 = {exchange_rate}元人民币**（100%确定）

### 兑换要求
- **最低兑换**：{MIN_EXCHANGE}贡献值（{min_exchange_cash}元）
- **兑换上限**：无上限
- **兑换频率**：不限次数

### 到账规则
- **到账时间**：T+1（次工作日）
- **到账方式**：提现到用户设置的收款账户
- **手续费**：0%（平台承担）

---

## 🔄 兑换流程

### 步骤1：设置收款方式
1. 进入"个人中心"
2. 点击"收款方式管理"
3. 添加银行卡或支付宝账户
4. 完成实名认证

### 步骤2：提交兑换申请
1. 进入"灵值管理"
2. 点击"兑换提现"
3. 输入要兑换的贡献值数量
4. 确认兑换金额和收款账户

### 步骤3：等待到账
- 提交申请后，系统会在1个工作日内处理
- 资金将在次工作日到账
- 到账后会收到通知

---

## 💰 兑换示例

### 示例1：小额兑换
**兑换100贡献值**
- 兑换金额：{calculate_cash_value(100)}元
- 到账时间：T+1（次工作日）
- 实际到账：{calculate_cash_value(100)}元（无手续费）

### 示例2：中等兑换
**兑换1000贡献值**
- 兑换金额：{calculate_cash_value(1000)}元
- 到账时间：T+1（次工作日）
- 实际到账：{calculate_cash_value(1000)}元（无手续费）

### 示例3：大额兑换
**兑换10000贡献值**
- 兑换金额：{calculate_cash_value(10000)}元
- 到账时间：T+1（次工作日）
- 实际到账：{calculate_cash_value(10000)}元（无手续费）

---

## 🔒 锁定增值建议

如果您暂时不需要使用这笔资金，可以考虑锁定增值：

### 锁定1年（+20%）
- 100贡献值 → 120贡献值 → {calculate_cash_value(120)}元
- 增值收益：{calculate_cash_value(20)}元

### 锁定2年（+50%）
- 100贡献值 → 150贡献值 → {calculate_cash_value(150)}元
- 增值收益：{calculate_cash_value(50)}元

### 锁定3年（+100%）
- 100贡献值 → 200贡献值 → {calculate_cash_value(200)}元
- 增值收益：{calculate_cash_value(100)}元

---

## ⚠️ 注意事项

1. **实名认证**：兑换前必须完成实名认证
2. **收款账户**：必须设置有效的收款账户
3. **提现限额**：根据平台风控规则，可能有限额
4. **到账时间**：遇节假日可能顺延
5. **账户安全**：确保收款账户信息安全

---

## 💡 最佳实践

1. **小额多次**：建议小额多次兑换，降低风险
2. **合理规划**：根据实际需要规划兑换金额和时间
3. **锁定增值**：暂时不用的资金考虑锁定增值
4. **关注活动**：平台可能有兑换优惠活动

---

**重要提示**：所有兑换规则100%确定，随时可兑现！
"""
    return result


@tool
def get_new_user_bonus_info(runtime: ToolRuntime) -> str:
    """
    获取新用户权益信息（基于经济模型）
    
    Returns:
        新用户权益详情
    """
    bonus = NEW_USER_BONUS
    
    result = """
🎁 **新用户专属权益**

---

## 🌟 欢迎礼遇

感谢您加入灵值生态园！为您准备了以下新手礼包：

"""

    if "free_contribution" in bonus:
        value = bonus["free_contribution"]
        result += f"""
### 1️⃣ 新手任务包
**价值**：{value}贡献值（{calculate_cash_value(value)}元）

完成以下任务即可获得：
- ✅ 完成实名认证（+50贡献值）
- ✅ 设置收款方式（+50贡献值）
- ✅ 完成首次对话（+50贡献值）
- ✅ 完成首次签到（+50贡献值）
- ✅ 完成首次文化探索（+50贡献值）
- ✅ 完成首次项目任务（+50贡献值）

"""
    
    if "expert_consultation" in bonus:
        value = bonus["expert_consultation"]
        result += f"""
### 2️⃣ 专家咨询券
**价值**：{value}贡献值（{calculate_cash_value(value)}元）

获得一次免费专家咨询服务，包括：
- 🎭 文化转译咨询
- 🎨 美学设计建议
- 💼 商业策略指导

"""
    
    if "smart_translation" in bonus:
        value = bonus["smart_translation"]
        result += f"""
### 3️⃣ 智能体转译体验
**价值**：{value}贡献值（{calculate_cash_value(value)}元）

免费体验智能体文化转译服务：
- 🏛️ 唐文化转译
- 🎨 品牌文化转译
- 📖 空间文化转译

"""

    total_bonus = sum(bonus.values())
    result += f"""
---

## 💰 权益总价值

**总价值**：{total_bonus}贡献值（{calculate_cash_value(total_bonus)}元）

## ⏰ 有效期

所有新手权益自注册之日起**30天内**有效，请及时领取！

## 🎯 如何领取

### 步骤1：完成任务
按照提示完成新手任务，逐步领取奖励

### 步骤2：查看奖励
在"个人中心" → "我的奖励"中查看已获得的奖励

### 步骤3：使用奖励
在相应的功能模块中使用奖励

## 💡 使用建议

1. **优先完成实名认证**：解锁全部功能
2. **设置收款方式**：准备提现
3. **体验核心功能**：感受平台价值
4. **规划长期参与**：选择适合的收入路径

---

## 📞 需要帮助？

如果您在领取新手权益时遇到任何问题，可以：
- 💬 联系客服
- 📖 查看帮助文档
- 🤖 咨询智能体

---

**恭喜您成为灵值生态园的一员！期待与您共同成长！** 🎉
"""
    return result


@tool
def compare_investment_options(
    contribution: int,
    runtime: ToolRuntime
) -> str:
    """
    比较不同的投资选项（即时兑换 vs 锁定增值）
    
    Args:
        contribution: 贡献值数量
    
    Returns:
        详细的比较分析
    """
    instant_value = calculate_cash_value(contribution)
    
    # 计算不同锁定期的收益
    lock_1y_info = calculate_total_value(contribution, "1年")
    lock_2y_info = calculate_total_value(contribution, "2年")
    lock_3y_info = calculate_total_value(contribution, "3年")
    
    result = f"""
📊 **投资选项对比分析**

---

## 💰 基础信息

**投入贡献值**：{contribution}贡献值
**即时价值**：{instant_value}元人民币

---

## 🔄 选项1：即时兑换

### 基本信息
- 兑换金额：{instant_value}元
- 到账时间：T+1（次工作日）
- 流动性：100%

### 优点
✅ 灵活性高，随时可用
✅ 无风险，立即到账
✅ 适合应急资金

### 缺点
⚠️ 无增值收益
⚠️ 机会成本

### 适用场景
- 需要立即使用资金
- 应急资金需求
- 短期资金周转

---

## 🔒 选项2：锁定1年（+20%）

### 基本信息
- 锁定期限：1年
- 增值收益：{lock_1y_info['bonus_value']}元
- 到期总价值：{lock_1y_info['total_value']}元

### 优点
✅ 年化收益率：20%
✅ 风险低，收益确定
✅ 适合稳健投资

### 缺点
⚠️ 流动性受限
⚠️ 需要锁定1年

### 适用场景
- 稳健型投资
- 中期闲置资金
- 对流动性要求不高

### 收益对比
- 即时兑换：{instant_value}元
- 锁定1年：{lock_1y_info['total_value']}元
- **净收益：+{lock_1y_info['bonus_value']}元（+{lock_1y_info['bonus_value']/instant_value*100:.0f}%）**

---

## 🔒 选项3：锁定2年（+50%）

### 基本信息
- 锁定期限：2年
- 增值收益：{lock_2y_info['bonus_value']}元
- 到期总价值：{lock_2y_info['total_value']}元

### 优点
✅ 年化收益率：25%（复利）
✅ 收益较高
✅ 适合平衡型投资

### 缺点
⚠️ 流动性受限
⚠️ 需要锁定2年

### 适用场景
- 平衡型投资
- 长期闲置资金
- 追求较高收益

### 收益对比
- 即时兑换：{instant_value}元
- 锁定2年：{lock_2y_info['total_value']}元
- **净收益：+{lock_2y_info['bonus_value']}元（+{lock_2y_info['bonus_value']/instant_value*100:.0f}%）**

---

## 🔒 选项4：锁定3年（+100%）

### 基本信息
- 锁定期限：3年
- 增值收益：{lock_3y_info['bonus_value']}元
- 到期总价值：{lock_3y_info['total_value']}元

### 优点
✅ 年化收益率：33.3%（复利）
✅ 收益最高
✅ 适合进取型投资

### 缺点
⚠️ 流动性受限
⚠️ 需要锁定3年

### 适用场景
- 进取型投资
- 长期资金规划
- 追求最高收益

### 收益对比
- 即时兑换：{instant_value}元
- 锁定3年：{lock_3y_info['total_value']}元
- **净收益：+{lock_3y_info['bonus_value']}元（+{lock_3y_info['bonus_value']/instant_value*100:.0f}%）**

---

## 📊 收益对比表格

| 选项 | 到期价值 | 增值收益 | 收益率 | 年化收益率 |
|------|---------|---------|--------|-----------|
| 即时兑换 | {instant_value}元 | 0元 | 0% | - |
| 锁定1年 | {lock_1y_info['total_value']}元 | {lock_1y_info['bonus_value']}元 | {lock_1y_info['bonus_value']/instant_value*100:.0f}% | 20% |
| 锁定2年 | {lock_2y_info['total_value']}元 | {lock_2y_info['bonus_value']}元 | {lock_2y_info['bonus_value']/instant_value*100:.0f}% | 25% |
| 锁定3年 | {lock_3y_info['total_value']}元 | {lock_3y_info['bonus_value']}元 | {lock_3y_info['bonus_value']/instant_value*100:.0f}% | 33.3% |

---

## 💡 投资建议

### 短期资金（6个月内）
**推荐：即时兑换**
理由：灵活性高，适合短期资金需求

### 中期资金（6-18个月）
**推荐：锁定1年**
理由：年化20%收益，平衡风险和收益

### 长期资金（18-36个月）
**推荐：锁定2年**
理由：年化25%收益，收益较高

### 超长期资金（3年以上）
**推荐：锁定3年**
理由：年化33.3%收益，收益最高

---

## 🎯 组合策略

如果您有较多的贡献值，可以考虑组合投资：

**示例：{contribution * 10}贡献值组合策略**

- 30% 即时兑换：{contribution * 3}贡献值（{calculate_cash_value(contribution * 3)}元）
- 30% 锁定1年：{contribution * 3}贡献值（{calculate_cash_value(contribution * 3 * 1.2):.1f}元）
- 20% 锁定2年：{contribution * 2}贡献值（{calculate_cash_value(contribution * 2 * 1.5):.1f}元）
- 20% 锁定3年：{contribution * 2}贡献值（{calculate_cash_value(contribution * 2 * 2):.1f}元）

**总价值：{calculate_cash_value(contribution * 3) + calculate_cash_value(contribution * 3 * 1.2) + calculate_cash_value(contribution * 2 * 1.5) + calculate_cash_value(contribution * 2 * 2):.1f}元**

---

**重要提示**：所有投资选项100%确定，无风险！
"""
    return result
