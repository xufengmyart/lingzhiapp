"""
合伙人级别枚举（V2.0）

定义4级合伙人体系的枚举类型
"""

from enum import Enum


class PartnerLevelType(Enum):
    """
    合伙人级别枚举（V2.0）
    
    层级说明：
    - NORMAL_USER: 普通用户，0贡献值，一级推荐（10%）
    - REGULAR_PARTNER: 普通合伙人，50000贡献值，二级推荐（10%+5%）
    - SENIOR_PARTNER: 高级合伙人，100000贡献值，三级推荐（10%+5%+3%）
    - FOUNDING_PARTNER: 创始合伙人，200000贡献值，三级推荐，年度分红10%
    """
    NORMAL_USER = "normal_user"           # 普通用户
    REGULAR_PARTNER = "regular_partner"   # 普通合伙人
    SENIOR_PARTNER = "senior_partner"     # 高级合伙人
    FOUNDING_PARTNER = "founding_partner" # 创始合伙人


class ReferralLevel(Enum):
    """
    推荐层级枚举（V2.0）
    
    层级说明：
    - LEVEL_1: 一级推荐，直接推荐用户，10%佣金
    - LEVEL_2: 二级推荐，间接推荐用户，5%佣金
    - LEVEL_3: 三级推荐，三级推荐用户，3%佣金
    """
    LEVEL_1 = 1  # 一级推荐：直接推荐
    LEVEL_2 = 2  # 二级推荐：间接推荐
    LEVEL_3 = 3  # 三级推荐：三级推荐


class RewardType(Enum):
    """
    奖励类型枚举（V2.0）
    """
    NEW_USER_REWARD = "new_user_reward"         # 新用户注册奖励
    FIRST_PROJECT_REWARD = "first_project"      # 首项目完成奖励
    ACTIVE_BADGE_REWARD = "active_badge"        # 活跃勋章奖励
    WAKEUP_REWARD = "wakeup"                    # 沉睡唤醒奖励
    LEVEL_UPGRADE_REWARD = "level_upgrade"      # 合伙人升级奖励
    PROJECT_COMPLETION = "project_completion"   # 项目完成奖励
    REFERRAL_COMMISSION = "referral_commission" # 推荐佣金


class TransactionType(Enum):
    """
    交易类型枚举（V2.0）
    """
    INITIAL = "initial"                         # 初始灵值
    PROJECT_EARNING = "project_earning"         # 项目收入
    REFERRAL_REWARD = "referral_reward"         # 推荐奖励
    COMMISSION_INCOME = "commission_income"     # 佣金收入
    TEAM_INCOME = "team_income"                 # 团队收益
    LEVEL_UPGRADE_REWARD = "level_upgrade"      # 升级奖励
    NEW_USER_REWARD = "new_user_reward"         # 新用户奖励
    ACTIVE_BADGE_BONUS = "active_badge"         # 活跃勋章奖励
    WAKEUP_REWARD = "wakeup"                    # 唤醒奖励
    PROJECT_TIMEOUT_PENALTY = "timeout_penalty" # 超时惩罚
    CONSUMPTION = "consumption"                 # 消费


# V2.0 合伙人级别配置（从数据库读取的备选方案）
PARTNER_LEVELS_CONFIG = {
    PartnerLevelType.NORMAL_USER: {
        "name": "普通用户",
        "min_contribution": 0,
        "min_investment": 0,
        "commission_rate": 0.10,  # 基础10%
        "referral_depth": 1,  # 一级推荐
        "contribution_multiplier": 1.0,
        "team_bonus_rate": 0.0,
        "rights": ["项目参与权", "灵值积累"]
    },
    PartnerLevelType.REGULAR_PARTNER: {
        "name": "普通合伙人",
        "min_contribution": 50000,
        "min_investment": 50000,
        "commission_rate": 0.10,  # 基础10%
        "referral_depth": 2,  # 二级推荐
        "contribution_multiplier": 1.2,  # 自身+20%
        "team_bonus_rate": 0.10,  # 团队+10%
        "upgrade_reward": 5000,
        "rights": ["二级推荐（10%+5%）", "项目优先参与权"]
    },
    PartnerLevelType.SENIOR_PARTNER: {
        "name": "高级合伙人",
        "min_contribution": 100000,
        "min_investment": 100000,
        "commission_rate": 0.10,  # 基础10%
        "referral_depth": 3,  # 三级推荐
        "contribution_multiplier": 1.3,  # 自身+30%
        "team_bonus_rate": 0.15,  # 团队+15%
        "upgrade_reward": 10000,
        "rights": ["三级推荐（10%+5%+3%）", "项目决策权"]
    },
    PartnerLevelType.FOUNDING_PARTNER: {
        "name": "创始合伙人",
        "min_contribution": 200000,
        "min_investment": 200000,
        "commission_rate": 0.10,  # 基础10%
        "referral_depth": 3,  # 三级推荐
        "contribution_multiplier": 1.5,  # 自身+50%
        "team_bonus_rate": 0.20,  # 团队+20%
        "upgrade_reward": 20000,
        "dividend_percentage": 0.10,  # 年度分红10%
        "rights": ["平台分红权", "规则制定参与权"]
    }
}


# V2.0 推荐佣金规则
REFERRAL_COMMISSION_RATES = {
    ReferralLevel.LEVEL_1: 0.10,  # 一级推荐：10%
    ReferralLevel.LEVEL_2: 0.05,  # 二级推荐：5%
    ReferralLevel.LEVEL_3: 0.03,  # 三级推荐：3%
}


def get_partner_level_config(level: PartnerLevelType) -> dict:
    """获取合伙人级别配置"""
    return PARTNER_LEVELS_CONFIG.get(level, {})


def get_referral_commission_rate(level: ReferralLevel) -> float:
    """获取推荐佣金比例"""
    return REFERRAL_COMMISSION_RATES.get(level, 0.0)


def get_referral_depth(partner_level: PartnerLevelType) -> int:
    """获取推荐深度"""
    return get_partner_level_config(partner_level).get("referral_depth", 1)


def get_contribution_multiplier(partner_level: PartnerLevelType) -> float:
    """获取贡献值倍数"""
    return get_partner_level_config(partner_level).get("contribution_multiplier", 1.0)


def get_team_bonus_rate(partner_level: PartnerLevelType) -> float:
    """获取团队收益比例"""
    return get_partner_level_config(partner_level).get("team_bonus_rate", 0.0)


def get_upgrade_reward(partner_level: PartnerLevelType) -> float:
    """获取升级奖励"""
    return get_partner_level_config(partner_level).get("upgrade_reward", 0)


if __name__ == "__main__":
    # 测试代码
    print("合伙人级别配置测试：")
    for level in PartnerLevelType:
        config = get_partner_level_config(level)
        print(f"\n{level.value}:")
        print(f"  名称: {config['name']}")
        print(f"  最小贡献值: {config['min_contribution']}")
        print(f"  推荐深度: {config['referral_depth']}")
        print(f"  权限: {', '.join(config['rights'])}")
    
    print("\n推荐佣金比例：")
    for level in ReferralLevel:
        print(f"{level.name}: {get_referral_commission_rate(level)*100}%")
