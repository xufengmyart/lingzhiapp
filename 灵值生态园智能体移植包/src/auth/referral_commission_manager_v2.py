"""
V2.0 融合版 - 三级推荐佣金系统

功能：
1. 三级推荐佣金计算（10%/5%/3%）
2. 合伙人升级奖励
3. 团队收益计算
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Optional, Tuple
from enums.partner_level import (
    PartnerLevelType,
    ReferralLevel,
    REFERRAL_COMMISSION_RATES,
    get_partner_level_config,
    get_referral_depth,
    get_upgrade_reward,
    get_team_bonus_rate
)


class ReferralCommissionManagerV2:
    """V2.0 推荐佣金管理器"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def calculate_three_level_commission(
        self,
        referrer_id: int,
        referee_id: int,
        contribution_earned: float
    ) -> List[Dict]:
        """
        计算三级推荐佣金
        
        Args:
            referrer_id: 直接推荐人ID
            referee_id: 被推荐人ID
            contribution_earned: 被推荐人获得的贡献值
        
        Returns:
            佣金分配列表（包括三级推荐人）
        """
        commissions = []
        
        # 1. 获取推荐链
        referral_chain = self._get_referral_chain(referrer_id)
        
        if not referral_chain:
            return commissions
        
        # 2. 计算三级推荐佣金
        # 一级推荐（直接推荐）
        level1_referrer = referral_chain[0]
        level1_commission = contribution_earned * REFERRAL_COMMISSION_RATES[ReferralLevel.LEVEL_1]
        
        commissions.append({
            "referrer_id": level1_referrer['id'],
            "referee_id": referee_id,
            "level": 1,
            "rate": REFERRAL_COMMISSION_RATES[ReferralLevel.LEVEL_1],
            "amount": level1_commission,
            "type": "referral_commission",
            "is_upgrade_reward": False
        })
        
        # 二级推荐（如果推荐人是合伙人）
        if len(referral_chain) >= 2:
            level2_referrer = referral_chain[1]
            level2_commission = contribution_earned * REFERRAL_COMMISSION_RATES[ReferralLevel.LEVEL_2]
            
            commissions.append({
                "referrer_id": level2_referrer['id'],
                "referee_id": referee_id,
                "level": 2,
                "rate": REFERRAL_COMMISSION_RATES[ReferralLevel.LEVEL_2],
                "amount": level2_commission,
                "type": "referral_commission",
                "is_upgrade_reward": False
            })
            
            # 三级推荐（如果二级推荐人是高级/创始合伙人）
            if len(referral_chain) >= 3:
                level3_referrer = referral_chain[2]
                level3_commission = contribution_earned * REFERRAL_COMMISSION_RATES[ReferralLevel.LEVEL_3]
                
                commissions.append({
                    "referrer_id": level3_referrer['id'],
                    "referee_id": referee_id,
                    "level": 3,
                    "rate": REFERRAL_COMMISSION_RATES[ReferralLevel.LEVEL_3],
                    "amount": level3_commission,
                    "type": "referral_commission",
                    "is_upgrade_reward": False
                })
        
        return commissions
    
    def _get_referral_chain(self, user_id: int, max_depth: int = 3) -> List[Dict]:
        """
        获取推荐链（最多3级）
        
        Args:
            user_id: 用户ID
            max_depth: 最大深度
        
        Returns:
            推荐人列表（从直接推荐人开始）
        """
        chain = []
        current_id = user_id
        
        for _ in range(max_depth):
            # 查找当前用户的推荐人
            result = self.session.execute(
                text("SELECT referrer_id FROM referrals WHERE referee_id = :user_id AND status = 'active'"),
                {"user_id": current_id}
            ).fetchone()
            
            if not result:
                break
            
            referrer_id = result[0]
            
            # 获取推荐人信息
            referrer_info = self.session.execute(
                text("""
                    SELECT id, name, partner_level 
                    FROM users 
                    WHERE id = :referrer_id
                """),
                {"referrer_id": referrer_id}
            ).fetchone()
            
            if referrer_info:
                chain.append({
                    'id': referrer_info[0],
                    'name': referrer_info[1],
                    'partner_level': referrer_info[2] or 'normal_user'
                })
                current_id = referrer_id
            else:
                break
        
        return chain
    
    def check_partner_upgrade_eligibility(self, user_id: int) -> Tuple[bool, Optional[PartnerLevelType]]:
        """
        检查用户是否符合合伙人升级条件
        
        升级路径：
        1. 累计贡献值达标
        2. 直接投资达标
        
        Returns:
            (是否符合升级条件, 新的合伙人级别)
        """
        # 获取用户当前合伙人级别
        user_info = self.session.execute(
            text("SELECT partner_level FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if not user_info:
            return False, None
        
        current_level_str = user_info[0] or 'normal_user'
        current_level = PartnerLevelType(current_level_str)
        
        # 获取用户累计贡献值
        contribution_info = self.session.execute(
            text("SELECT cumulative_contribution FROM user_contributions_v2 WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        cumulative_contribution = contribution_info[0] if contribution_info else 0.0
        
        # 获取用户直接投资
        user_info_full = self.session.execute(
            text("SELECT direct_investment FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        direct_investment = user_info_full[0] if user_info_full else 0.0
        
        # 检查升级条件（累计灵值 OR 直接投资）
        if cumulative_contribution >= 200000 or direct_investment >= 200000:
            if current_level != PartnerLevelType.FOUNDING_PARTNER:
                return True, PartnerLevelType.FOUNDING_PARTNER
        elif cumulative_contribution >= 100000 or direct_investment >= 100000:
            if current_level != PartnerLevelType.SENIOR_PARTNER:
                return True, PartnerLevelType.SENIOR_PARTNER
        elif cumulative_contribution >= 50000 or direct_investment >= 50000:
            if current_level != PartnerLevelType.REGULAR_PARTNER:
                return True, PartnerLevelType.REGULAR_PARTNER
        
        return False, None
    
    def handle_partner_upgrade(
        self,
        user_id: int,
        new_level: PartnerLevelType,
        is_investment: bool = False,
        investment_amount: float = 0.0
    ) -> Dict:
        """
        处理合伙人升级
        
        Args:
            user_id: 用户ID
            new_level: 新的合伙人级别
            is_investment: 是否通过投资升级
            investment_amount: 投资金额
        
        Returns:
            升级结果
        """
        # 获取升级奖励
        reward_amount = get_upgrade_reward(new_level)
        
        # 更新用户合伙人级别
        self.session.execute(
            text("""
                UPDATE users 
                SET partner_level = :partner_level,
                    updated_at = datetime('now')
                WHERE id = :user_id
            """),
            {
                "partner_level": new_level.value,
                "user_id": user_id
            }
        )
        
        # 如果是投资路径，更新直接投资金额
        if is_investment and investment_amount > 0:
            self.session.execute(
                text("""
                    UPDATE users 
                    SET direct_investment = direct_investment + :investment_amount,
                        updated_at = datetime('now')
                    WHERE id = :user_id
                """),
                {
                    "investment_amount": investment_amount,
                    "user_id": user_id
                }
            )
        
        # 发放升级奖励（如果有）
        if reward_amount > 0:
            self._add_contribution(
                user_id=user_id,
                amount=reward_amount,
                transaction_type="level_upgrade",
                description=f"合伙人升级奖励：{get_partner_level_config(new_level)['name']}"
            )
        
        # 记录升级日志
        self.session.execute(
            text("""
                INSERT INTO audit_logs (
                    user_id, action, description, created_at
                ) VALUES (
                    :user_id, 'partner_upgrade', :description, datetime('now')
                )
            """),
            {
                "user_id": user_id,
                "description": f"升级为{get_partner_level_config(new_level)['name']}"
            }
        )
        
        self.session.commit()
        
        return {
            "success": True,
            "new_level": new_level.value,
            "new_level_name": get_partner_level_config(new_level)['name'],
            "upgrade_reward": reward_amount,
            "is_investment": is_investment,
            "investment_amount": investment_amount
        }
    
    def calculate_team_bonus(
        self,
        user_id: int,
        project_contribution: float
    ) -> float:
        """
        计算团队收益（合伙人额外收益）
        
        Args:
            user_id: 用户ID
            project_contribution: 项目贡献值
        
        Returns:
            团队收益金额
        """
        # 获取用户合伙人级别
        user_info = self.session.execute(
            text("SELECT partner_level FROM users WHERE id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if not user_info:
            return 0.0
        
        partner_level_str = user_info[0] or 'normal_user'
        partner_level = PartnerLevelType(partner_level_str)
        
        # 获取团队收益比例
        team_bonus_rate = get_team_bonus_rate(partner_level)
        
        # 计算团队收益
        team_bonus = project_contribution * team_bonus_rate
        
        return team_bonus
    
    def _add_contribution(
        self,
        user_id: int,
        amount: float,
        transaction_type: str,
        description: str
    ):
        """
        添加贡献值
        
        Args:
            user_id: 用户ID
            amount: 金额
            transaction_type: 交易类型
            description: 描述
        """
        # 更新user_contributions_v2表
        self.session.execute(
            text("""
                UPDATE user_contributions_v2
                SET cumulative_contribution = cumulative_contribution + :amount,
                    remaining_contribution = remaining_contribution + :amount,
                    updated_at = datetime('now')
                WHERE user_id = :user_id
            """),
            {
                "amount": amount,
                "user_id": user_id
            }
        )
    
    def get_referral_tree(
        self,
        user_id: int,
        max_depth: int = 3
    ) -> List[Dict]:
        """
        获取推荐树（包含下级推荐人）
        
        Args:
            user_id: 用户ID
            max_depth: 最大深度
        
        Returns:
            推荐树
        """
        tree = []
        
        def _build_tree(referrer_id: int, current_depth: int):
            if current_depth > max_depth:
                return None
            
            # 查找直接推荐的人
            referees = self.session.execute(
                text("""
                    SELECT u.id, u.name, u.partner_level, r.created_at
                    FROM users u
                    JOIN referrals r ON u.id = r.referee_id
                    WHERE r.referrer_id = :referrer_id AND r.status = 'active'
                """),
                {"referrer_id": referrer_id}
            ).fetchall()
            
            if not referees:
                return None
            
            children = []
            for referee in referees:
                child = {
                    "user_id": referee[0],
                    "name": referee[1],
                    "partner_level": referee[2] or 'normal_user',
                    "joined_at": referee[3],
                    "children": _build_tree(referee[0], current_depth + 1)
                }
                children.append(child)
            
            return children
        
        tree = _build_tree(user_id, 1)
        return tree
    
    def get_referral_statistics(self, user_id: int) -> Dict:
        """
        获取推荐统计信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            统计信息
        """
        # 直接推荐人数
        direct_count = self.session.execute(
            text("""
                SELECT COUNT(*) 
                FROM referrals 
                WHERE referrer_id = :user_id AND status = 'active'
            """),
            {"user_id": user_id}
        ).fetchone()[0]
        
        # 间接推荐人数（2-3级）
        indirect_count = self.session.execute(
            text("""
                WITH RECURSIVE referral_tree AS (
                    SELECT referee_id, 1 as level
                    FROM referrals
                    WHERE referrer_id = :user_id AND status = 'active'
                    
                    UNION ALL
                    
                    SELECT r.referee_id, rt.level + 1
                    FROM referrals r
                    JOIN referral_tree rt ON r.referrer_id = rt.referee_id
                    WHERE r.status = 'active' AND rt.level < 3
                )
                SELECT COUNT(*) 
                FROM referral_tree 
                WHERE level > 1
            """),
            {"user_id": user_id}
        ).fetchone()[0]
        
        # 总佣金收入
        total_commission = self.session.execute(
            text("""
                SELECT SUM(commission_amount) 
                FROM referral_commissions 
                WHERE referrer_id = :user_id AND status = 'paid'
            """),
            {"user_id": user_id}
        ).fetchone()[0] or 0.0
        
        # 团队总贡献值
        team_contribution = self.session.execute(
            text("""
                WITH RECURSIVE team_tree AS (
                    SELECT id, 1 as level
                    FROM users
                    WHERE id = :user_id
                    
                    UNION ALL
                    
                    SELECT u.id, tt.level + 1
                    FROM users u
                    JOIN referrals r ON u.id = r.referee_id
                    JOIN team_tree tt ON r.referrer_id = tt.id
                    WHERE r.status = 'active' AND tt.level < 3
                )
                SELECT COALESCE(SUM(cumulative_contribution), 0)
                FROM user_contributions_v2
                WHERE user_id IN (SELECT id FROM team_tree WHERE id != :user_id)
            """),
            {"user_id": user_id}
        ).fetchone()[0] or 0.0
        
        return {
            "direct_referrals": direct_count,
            "indirect_referrals": indirect_count,
            "total_referrals": direct_count + indirect_count,
            "total_commission": total_commission,
            "team_contribution": team_contribution
        }


# 便捷函数
def create_referral_commission_manager(session: Session) -> ReferralCommissionManagerV2:
    """创建推荐佣金管理器实例"""
    return ReferralCommissionManagerV2(session)


if __name__ == "__main__":
    # 测试代码
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    DATABASE_URL = "sqlite:///auth.db"
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        manager = create_referral_commission_manager(session)
        
        # 测试推荐佣金计算
        print("="*60)
        print("V2.0 三级推荐佣金系统测试")
        print("="*60)
        
        # 假设用户2获得了1000贡献值
        referee_id = 2
        contribution_earned = 1000.0
        
        # 获取推荐人
        referrer_info = session.execute(
            text("SELECT referrer_id FROM referrals WHERE referee_id = :referee_id"),
            {"referee_id": referee_id}
        ).fetchone()
        
        if referrer_info:
            referrer_id = referrer_info[0]
            print(f"\n测试：用户{referee_id}获得{contribution_earned}贡献值")
            print(f"推荐人：用户{referrer_id}")
            
            # 计算三级推荐佣金
            commissions = manager.calculate_three_level_commission(
                referrer_id=referrer_id,
                referee_id=referee_id,
                contribution_earned=contribution_earned
            )
            
            print(f"\n三级推荐佣金分配：")
            for commission in commissions:
                print(f"  第{commission['level']}级：用户{commission['referrer_id']} 获得 {commission['amount']:.2f} 贡献值 ({commission['rate']*100}%)")
        
        # 测试合伙人升级检查
        print(f"\n测试合伙人升级检查：")
        for user_id in [1, 2, 3]:
            can_upgrade, new_level = manager.check_partner_upgrade_eligibility(user_id)
            if can_upgrade:
                print(f"  用户{user_id} 可升级为 {new_level.value}")
            else:
                print(f"  用户{user_id} 暂不可升级")
        
        print("\n✅ 测试完成！")
        
    finally:
        session.close()
