"""
灵值生态园 - 核心经济模型配置

定义所有与贡献值（灵值）相关的经济规则和常量
"""

from typing import TypedDict, Dict, Any


class ContributionValueConfig(TypedDict):
    """贡献值价值配置"""
    exchange_rate: float  # 兑换汇率：1贡献值 = ? 元
    min_exchange: int  # 最低兑换数量（贡献值）
    exchange_time: str  # 兑换时间说明
    exchange_fee: float  # 兑换手续费（百分比）


class LockPeriodConfig(TypedDict):
    """锁定增值配置"""
    period: str  # 锁定期限
    bonus_rate: float  # 增值率（百分比）


class EconomicModelConfig:
    """经济模型总配置"""

    def __init__(self):
        # 贡献值（灵值）即时价值规则
        self.contribution_value: ContributionValueConfig = {
            "exchange_rate": 0.1,  # 1贡献值 = 0.1元
            "min_exchange": 10,  # 最低兑换10贡献值（1元）
            "exchange_time": "T+1",  # 次工作日到账
            "exchange_fee": 0.0,  # 0%手续费
        }

        # 锁定增值规则
        self.lock_periods: Dict[str, LockPeriodConfig] = {
            "1年": {
                "period": "1年",
                "bonus_rate": 0.20,  # 增值20%
            },
            "2年": {
                "period": "2年",
                "bonus_rate": 0.50,  # 增值50%
            },
            "3年": {
                "period": "3年",
                "bonus_rate": 1.00,  # 增值100%
            },
        }

        # 收入级别（日均贡献值）
        self.income_levels: Dict[str, Dict[str, Any]] = {
            "轻度参与": {
                "daily_contribution": 30,
                "daily_income": 3.0,  # 30 * 0.1 = 3元
                "monthly_income": 90.0,  # 3 * 30 = 90元
                "yearly_income": 1080.0,  # 90 * 12 = 1080元
            },
            "中度参与": {
                "daily_contribution": 300,
                "daily_income": 30.0,  # 300 * 0.1 = 30元
                "monthly_income": 900.0,  # 30 * 30 = 900元
                "yearly_income": 10800.0,  # 900 * 12 = 10800元
            },
            "深度参与": {
                "daily_contribution": 1000,
                "daily_income": 100.0,  # 1000 * 0.1 = 100元
                "monthly_income": 3000.0,  # 100 * 30 = 3000元
                "yearly_income": 36000.0,  # 3000 * 12 = 36000元
            },
        }

        # 新用户权益
        self.new_user_bonus: Dict[str, Any] = {
            "free_contribution": 300,  # 新手任务包300贡献值
            "expert_consultation": 50,  # 专家咨询券50贡献值
            "smart_translation": 80,  # 智能体转译体验80贡献值
            "project_preview": 0,  # 项目观摩权限
        }

        # 核心规则说明
        self.core_rules: Dict[str, str] = {
            "exchange_rate_desc": "1贡献值 = 0.1元人民币，100%确定，随时可兑换",
            "lock_bonus_desc": "锁定1年+20%，2年+50%，3年+100%",
            "dual_income_desc": "即时收益（随时兑换）+ 长期收益（锁定增值）",
            "determination_desc": "这不是'可能'，而是'一定'",
        }


# 全局配置实例
ECONOMIC_MODEL = EconomicModelConfig()


def get_exchange_rate() -> float:
    """
    获取贡献值兑换汇率

    Returns:
        float: 1贡献值 = ? 元
    """
    return ECONOMIC_MODEL.contribution_value["exchange_rate"]


def calculate_cash_value(contribution: int) -> float:
    """
    计算贡献值的现金价值

    Args:
        contribution: 贡献值数量

    Returns:
        float: 现金价值（元）

    Examples:
        >>> calculate_cash_value(100)
        10.0
        >>> calculate_cash_value(300)
        30.0
    """
    rate = get_exchange_rate()
    return contribution * rate


def calculate_lock_bonus(contribution: int, lock_period: str) -> float:
    """
    计算锁定增值收益

    Args:
        contribution: 贡献值数量
        lock_period: 锁定期限（"1年"/"2年"/"3年"）

    Returns:
        float: 增值收益（贡献值）

    Examples:
        >>> calculate_lock_bonus(100, "1年")
        20.0  # 100 * 20%
        >>> calculate_lock_bonus(100, "3年")
        100.0  # 100 * 100%
    """
    if lock_period not in ECONOMIC_MODEL.lock_periods:
        raise ValueError(f"不支持的锁定期限: {lock_period}")

    bonus_rate = ECONOMIC_MODEL.lock_periods[lock_period]["bonus_rate"]
    return contribution * bonus_rate


def calculate_total_value(contribution: int, lock_period: str = None) -> Dict[str, float]:
    """
    计算贡献值的总价值（即时价值 + 锁定增值）

    Args:
        contribution: 贡献值数量
        lock_period: 锁定期限（None表示不锁定）

    Returns:
        Dict[str, float]: 包含即时价值、增值收益、总价值的字典

    Examples:
        >>> calculate_total_value(100, None)
        {'instant_value': 10.0, 'bonus_value': 0.0, 'total_value': 10.0}

        >>> calculate_total_value(100, "3年")
        {'instant_value': 10.0, 'bonus_value': 10.0, 'total_value': 20.0}
    """
    instant_value = calculate_cash_value(contribution)

    if lock_period:
        bonus_contribution = calculate_lock_bonus(contribution, lock_period)
        bonus_value = calculate_cash_value(bonus_contribution)
    else:
        bonus_value = 0.0

    total_value = instant_value + bonus_value

    return {
        "instant_value": instant_value,  # 即时价值（元）
        "bonus_value": bonus_value,  # 增值收益（元）
        "total_value": total_value,  # 总价值（元）
    }


def format_value_description(contribution: int, lock_period: str = None) -> str:
    """
    格式化贡献值价值说明

    Args:
        contribution: 贡献值数量
        lock_period: 锁定期限（None表示不锁定）

    Returns:
        str: 格式化的价值说明

    Examples:
        >>> format_value_description(100, None)
        '100贡献值即时兑换价值为10元'

        >>> format_value_description(100, "3年")
        '100贡献值即时兑换价值为10元，锁定3年预期增值100%（+10元），到期总价值20元'
    """
    values = calculate_total_value(contribution, lock_period)

    if lock_period:
        bonus_rate = int(ECONOMIC_MODEL.lock_periods[lock_period]["bonus_rate"] * 100)
        return (
            f"{contribution}贡献值即时兑换价值为{values['instant_value']:.1f}元，"
            f"锁定{lock_period}预期增值{bonus_rate}%（+{values['bonus_value']:.1f}元），"
            f"到期总价值{values['total_value']:.1f}元"
        )
    else:
        return f"{contribution}贡献值即时兑换价值为{values['instant_value']:.1f}元"


def get_income_projection(daily_contribution: int) -> Dict[str, float]:
    """
    根据日均贡献值预测收入

    Args:
        daily_contribution: 日均贡献值

    Returns:
        Dict[str, float]: 日收入、月收入、年收入

    Examples:
        >>> get_income_projection(30)
        {'daily_income': 3.0, 'monthly_income': 90.0, 'yearly_income': 1080.0}
    """
    rate = get_exchange_rate()
    daily_income = daily_contribution * rate
    monthly_income = daily_income * 30
    yearly_income = monthly_income * 12

    return {
        "daily_income": daily_income,
        "monthly_income": monthly_income,
        "yearly_income": yearly_income,
    }


# 导出核心常量
EXCHANGE_RATE = 0.1  # 1贡献值 = 0.1元
MIN_EXCHANGE = 10  # 最低兑换10贡献值
EXCHANGE_TIME = "T+1"  # 次工作日到账
EXCHANGE_FEE = 0.0  # 0%手续费

# 别名：灵值 = 贡献值
LINGZHI_EXCHANGE_RATE = EXCHANGE_RATE
LINGZHI_MIN_EXCHANGE = MIN_EXCHANGE


if __name__ == "__main__":
    # 测试代码
    print("=" * 70)
    print("灵值生态园 - 核心经济模型配置测试")
    print("=" * 70)
    print()

    print("1. 基础兑换规则")
    print("-" * 70)
    print(f"1贡献值 = {EXCHANGE_RATE}元")
    print(f"最低兑换: {MIN_EXCHANGE}贡献值（{calculate_cash_value(MIN_EXCHANGE)}元）")
    print(f"兑换时间: {EXCHANGE_TIME}")
    print(f"兑换手续费: {EXCHANGE_FEE * 100}%")
    print()

    print("2. 锁定增值规则")
    print("-" * 70)
    for period, config in ECONOMIC_MODEL.lock_periods.items():
        bonus_rate = int(config["bonus_rate"] * 100)
        print(f"锁定{period}: 预期增值{bonus_rate}%")
    print()

    print("3. 收入级别")
    print("-" * 70)
    for level, config in ECONOMIC_MODEL.income_levels.items():
        print(f"{level}:")
        print(f"  日均贡献值: {config['daily_contribution']}")
        print(f"  日收入: {config['daily_income']:.1f}元")
        print(f"  月收入: {config['monthly_income']:.1f}元")
        print(f"  年收入: {config['yearly_income']:.1f}元")
    print()

    print("4. 示例计算")
    print("-" * 70)
    print(format_value_description(100, None))
    print(format_value_description(100, "1年"))
    print(format_value_description(100, "3年"))
    print()

    print("5. 收入预测")
    print("-" * 70)
    projection = get_income_projection(300)
    print(f"日均300贡献值:")
    print(f"  日收入: {projection['daily_income']:.1f}元")
    print(f"  月收入: {projection['monthly_income']:.1f}元")
    print(f"  年收入: {projection['yearly_income']:.1f}元")
    print()

    print("=" * 70)
    print("✅ 核心经济规则：1贡献值（灵值）= 0.1元，100%确定，随时可兑换")
    print("=" * 70)
