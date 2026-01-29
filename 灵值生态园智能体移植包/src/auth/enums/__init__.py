"""
V2.0 融合版 - 枚举模块

包含所有V2.0相关的枚举类型：
- PartnerLevelType: 合伙人级别枚举
- ReferralLevel: 推荐层级枚举
- RewardType: 奖励类型枚举
- TransactionType: 交易类型枚举
"""

from .partner_level import (
    PartnerLevelType,
    ReferralLevel,
    RewardType,
    TransactionType,
    PARTNER_LEVELS_CONFIG,
    REFERRAL_COMMISSION_RATES,
    get_partner_level_config,
    get_referral_commission_rate,
    get_referral_depth,
    get_contribution_multiplier,
    get_team_bonus_rate,
    get_upgrade_reward
)

__all__ = [
    'PartnerLevelType',
    'ReferralLevel',
    'RewardType',
    'TransactionType',
    'PARTNER_LEVELS_CONFIG',
    'REFERRAL_COMMISSION_RATES',
    'get_partner_level_config',
    'get_referral_commission_rate',
    'get_referral_depth',
    'get_contribution_multiplier',
    'get_team_bonus_rate',
    'get_upgrade_reward'
]
