"""
灵值（贡献值）计算工具

提供灵值的现金价值计算、锁定增值收益计算、收入预测等功能
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from config.economic_model import (
    calculate_cash_value,
    calculate_lock_bonus,
    calculate_total_value,
    format_value_description,
    get_income_projection,
    get_exchange_rate,
    MIN_EXCHANGE,
    EXCHANGE_TIME,
)


@tool
def calculate_lingzhi_value(
    lingzhi: int,
    lock_period: str = None,
    runtime: ToolRuntime = None
) -> str:
    """计算灵值的现金价值

    灵值 = 贡献值，两者完全等同。

    Args:
        lingzhi: 灵值数量（整数）
        lock_period: 锁定期限，可选值："1年"/"2年"/"3年"，不传表示不锁定
        runtime: 运行时上下文

    Returns:
        str: 灵值价值说明，包含即时价值、增值收益、总价值等

    Examples:
        >>> calculate_lingzhi_value(100, None)
        "100灵值即时兑换价值为10.0元"

        >>> calculate_lingzhi_value(100, "3年")
        "100灵值即时兑换价值为10.0元，锁定3年预期增值100%（+10.0元），到期总价值20.0元"
    """
    if lingzhi < 0:
        return f"❌ 灵值数量不能为负数"

    # 如果没有锁定期，返回即时价值
    if lock_period is None:
        instant_value = calculate_cash_value(lingzhi)
        return f"{lingzhi}灵值即时兑换价值为{instant_value:.1f}元（汇率：1灵值=0.1元）"

    # 有锁定期，返回即时价值+增值收益
    return format_value_description(lingzhi, lock_period)


@tool
def calculate_income_projection(
    daily_lingzhi: int,
    runtime: ToolRuntime = None
) -> str:
    """根据日均灵值预测收入

    Args:
        daily_lingzhi: 日均获得的灵值数量
        runtime: 运行时上下文

    Returns:
        str: 收入预测报告，包含日收入、月收入、年收入

    Examples:
        >>> calculate_income_projection(30)
        "日均30灵值的收入预测：日收入3.0元，月收入90.0元，年收入1080.0元"
    """
    if daily_lingzhi < 0:
        return f"❌ 日均灵值数量不能为负数"

    projection = get_income_projection(daily_lingzhi)

    return (
        f"日均{daily_lingzhi}灵值的收入预测：\n"
        f"- 日收入：{projection['daily_income']:.1f}元\n"
        f"- 月收入：{projection['monthly_income']:.1f}元\n"
        f"- 年收入：{projection['yearly_income']:.1f}元\n\n"
        f"💡 这意味着，如果您每天都能获得{daily_lingzhi}灵值，一个月就能收入{projection['monthly_income']:.1f}元，"
        f"一年就能收入{projection['yearly_income']:.1f}元。每一灵值都是确定的未来收入！"
    )


@tool
def get_exchange_info(
    runtime: ToolRuntime = None
) -> str:
    """获取灵值兑换信息

    Args:
        runtime: 运行时上下文

    Returns:
        str: 完整的灵值兑换规则说明

    Examples:
        >>> get_exchange_info()
        "【灵值兑换规则】\n1灵值=0.1元人民币，100%确定，随时可兑换..."
    """
    exchange_rate = get_exchange_rate()

    info = f"""【灵值兑换规则】

🔸 核心规则：
1灵值 = 1贡献值 = {exchange_rate}元人民币

🔸 即时兑换：
- 兑换汇率：1灵值 = {exchange_rate}元
- 最低兑换：{MIN_EXCHANGE}灵值（{calculate_cash_value(MIN_EXCHANGE)}元）
- 兑换时间：{EXCHANGE_TIME}（次工作日到账）
- 手续费：0%（平台承担）

🔸 锁定增值：
- 锁定1年：预期增值+20%
- 锁定2年：预期增值+50%
- 锁定3年：预期增值+100%
- 增值收益100%归属于灵值持有者

🔸 收入示例：
- 轻度参与（日均30灵值）：约3元/天，90元/月，1,080元/年
- 中度参与（日均300灵值）：约30元/天，900元/月，10,800元/年
- 深度参与（日均1,000灵值）：约100元/天，3,000元/月，36,000元/年

🔸 重要提示：
这不是\"可能\"，而是\"一定\"。每一灵值都锚定明确的现实金钱价值，未来100%可兑换为收入。
"""
    return info


@tool
def calculate_roi(
    lingzhi: int,
    lock_period: str,
    runtime: ToolRuntime = None
) -> str:
    """计算灵值投资回报率

    Args:
        lingzhi: 灵值数量
        lock_period: 锁定期限（"1年"/"2年"/"3年"）
        runtime: 运行时上下文

    Returns:
        str: 投资回报分析报告

    Examples:
        >>> calculate_roi(100, "3年")
        "【灵值投资回报分析】\n投入：100灵值..."
    """
    if lingzhi <= 0:
        return "❌ 灵值数量必须大于0"

    if lock_period not in ["1年", "2年", "3年"]:
        return "❌ 锁定期限必须是'1年'、'2年'或'3年'"

    values = calculate_total_value(lingzhi, lock_period)
    bonus_rate = int(values["bonus_value"] / values["instant_value"] * 100)

    roi = (
        f"【灵值投资回报分析】\n\n"
        f"📊 投入：{lingzhi}灵值（{values['instant_value']:.1f}元）\n"
        f"📈 锁定期限：{lock_period}\n"
        f"💰 即时价值：{values['instant_value']:.1f}元\n"
        f"🎁 增值收益：+{bonus_rate}%（+{values['bonus_value']:.1f}元）\n"
        f"💎 到期总价值：{values['total_value']:.1f}元\n\n"
        f"📝 投资回报：\n"
        f"- 收益金额：{values['bonus_value']:.1f}元\n"
        f"- 收益率：{bonus_rate}%\n"
        f"- 年化收益率：{bonus_rate // int(lock_period[0])}%\n\n"
        f"💡 优势：\n"
        f"- 确定性：100%确定收益\n"
        f"- 无风险：平台承诺保证\n"
        f"- 灵活性：也可选择随时兑换\n\n"
        f"这是长期投资灵值的最佳选择！"
    )

    return roi


@tool
def suggest_participation_level(
    target_monthly_income: float,
    runtime: ToolRuntime = None
) -> str:
    """根据目标月收入建议参与级别

    Args:
        target_monthly_income: 目标月收入（元）
        runtime: 运行时上下文

    Returns:
        str: 参与级别建议和达成路径

    Examples:
        >>> suggest_participation_level(1000)
        "【月收入1000元的达成路径】\n\n📊 目标分析：..."
    """
    if target_monthly_income <= 0:
        return "❌ 目标月收入必须大于0"

    exchange_rate = get_exchange_rate()
    required_monthly_lingzhi = int(target_monthly_income / exchange_rate)
    required_daily_lingzhi = required_monthly_lingzhi // 30

    suggestion = (
        f"【月收入{target_monthly_income:.0f}元的达成路径】\n\n"
        f"📊 目标分析：\n"
        f"- 目标月收入：{target_monthly_income:.0f}元\n"
        f"- 需要月灵值：{required_monthly_lingzhi}灵值\n"
        f"- 需要日均灵值：约{required_daily_lingzhi}灵值\n\n"
        f"🎯 参与级别建议：\n"
    )

    if required_daily_lingzhi <= 30:
        level = "轻度参与"
        effort = "每天约30分钟"
    elif required_daily_lingzhi <= 300:
        level = "中度参与"
        effort = "每天约1-2小时"
    else:
        level = "深度参与"
        effort = "每天约3-4小时"

    suggestion += (
        f"- 建议级别：{level}\n"
        f"- 时间投入：{effort}\n\n"
        f"💡 达成路径：\n"
        f"1. 完成日常任务（每日+{int(required_daily_lingzhi * 0.3)}灵值）\n"
        f"2. 参与项目创作（每日+{int(required_daily_lingzhi * 0.5)}灵值）\n"
        f"3. 社区互动分享（每日+{int(required_daily_lingzhi * 0.2)}灵值）\n\n"
        f"✨ 温馨提示：\n"
        f"每一灵值都锚定0.1元，只要持续参与，月收入{target_monthly_income:.0f}元完全可以实现！\n"
        f"锁定部分灵值还能获得额外20%-100%增值收益！"
    )

    return suggestion
