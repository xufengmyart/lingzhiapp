"""
V2.0 融合版 - 贡献值管理器（三维贡献值模型）

功能：
1. 管理三种贡献值类型：
   - 累计贡献值（Cumulative）：用于合伙人层级判定
   - 项目贡献值（Project）：灵值收益核心来源
   - 剩余贡献值（Remaining）：可用于兑换权益、参与项目竞拍
2. 贡献值自动计算与更新
3. 贡献值消费与回收
"""

from sqlalchemy import text
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Dict, Optional
from enum import Enum


class ContributionType(Enum):
    """贡献值类型"""
    CUMULATIVE = "cumulative"  # 累计贡献值
    PROJECT = "project"       # 项目贡献值
    REMAINING = "remaining"   # 剩余贡献值
    INITIAL = "initial"       # 初始灵值
    REFERRAL = "referral"     # 推荐奖励
    COMMISSION = "commission" # 佣金收入
    TEAM = "team"            # 团队收益
    CONSUMED = "consumed"    # 消费贡献值


class ContributionManagerV2:
    """V2.0 贡献值管理器"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def get_user_contribution(self, user_id: int) -> Dict:
        """
        获取用户贡献值信息
        
        Returns:
            贡献值字典
        """
        result = self.session.execute(
            text("""
                SELECT 
                    cumulative_contribution,
                    project_contribution,
                    remaining_contribution,
                    consumed_contribution,
                    initial_contribution,
                    referral_reward,
                    commission_income,
                    team_income,
                    updated_at
                FROM user_contributions_v2
                WHERE user_id = :user_id
            """),
            {"user_id": user_id}
        ).fetchone()
        
        if not result:
            # 如果记录不存在，创建默认记录
            self._init_user_contribution(user_id)
            return self.get_user_contribution(user_id)
        
        return {
            "user_id": user_id,
            "cumulative_contribution": result[0] or 0.0,
            "project_contribution": result[1] or 0.0,
            "remaining_contribution": result[2] or 0.0,
            "consumed_contribution": result[3] or 0.0,
            "initial_contribution": result[4] or 1000.0,
            "referral_reward": result[5] or 0.0,
            "commission_income": result[6] or 0.0,
            "team_income": result[7] or 0.0,
            "updated_at": result[8]
        }
    
    def _init_user_contribution(self, user_id: int):
        """
        初始化用户贡献值记录（新用户默认1000灵值）
        """
        self.session.execute(
            text("""
                INSERT INTO user_contributions_v2 (
                    user_id,
                    cumulative_contribution,
                    project_contribution,
                    remaining_contribution,
                    consumed_contribution,
                    initial_contribution
                ) VALUES (
                    :user_id,
                    1000.0,
                    0.0,
                    1000.0,
                    0.0,
                    1000.0
                )
            """),
            {"user_id": user_id}
        )
        self.session.commit()
    
    def add_contribution(
        self,
        user_id: int,
        amount: float,
        contribution_type: ContributionType,
        description: str = "",
        related_id: Optional[int] = None
    ) -> Dict:
        """
        添加贡献值
        
        Args:
            user_id: 用户ID
            amount: 金额
            contribution_type: 贡献值类型
            description: 描述
            related_id: 关联ID（如项目ID）
        
        Returns:
            更新后的贡献值
        """
        # 更新贡献值
        if contribution_type == ContributionType.PROJECT:
            # 项目贡献值
            self.session.execute(
                text("""
                    UPDATE user_contributions_v2
                    SET project_contribution = project_contribution + :amount,
                        cumulative_contribution = cumulative_contribution + :amount,
                        remaining_contribution = remaining_contribution + :amount,
                        updated_at = datetime('now')
                    WHERE user_id = :user_id
                """),
                {"amount": amount, "user_id": user_id}
            )
        elif contribution_type == ContributionType.REFERRAL:
            # 推荐奖励
            self.session.execute(
                text("""
                    UPDATE user_contributions_v2
                    SET referral_reward = referral_reward + :amount,
                        cumulative_contribution = cumulative_contribution + :amount,
                        remaining_contribution = remaining_contribution + :amount,
                        updated_at = datetime('now')
                    WHERE user_id = :user_id
                """),
                {"amount": amount, "user_id": user_id}
            )
        elif contribution_type == ContributionType.COMMISSION:
            # 佣金收入
            self.session.execute(
                text("""
                    UPDATE user_contributions_v2
                    SET commission_income = commission_income + :amount,
                        cumulative_contribution = cumulative_contribution + :amount,
                        remaining_contribution = remaining_contribution + :amount,
                        updated_at = datetime('now')
                    WHERE user_id = :user_id
                """),
                {"amount": amount, "user_id": user_id}
            )
        elif contribution_type == ContributionType.TEAM:
            # 团队收益
            self.session.execute(
                text("""
                    UPDATE user_contributions_v2
                    SET team_income = team_income + :amount,
                        cumulative_contribution = cumulative_contribution + :amount,
                        remaining_contribution = remaining_contribution + :amount,
                        updated_at = datetime('now')
                    WHERE user_id = :user_id
                """),
                {"amount": amount, "user_id": user_id}
            )
        else:
            # 默认添加到累计贡献值
            self.session.execute(
                text("""
                    UPDATE user_contributions_v2
                    SET cumulative_contribution = cumulative_contribution + :amount,
                        remaining_contribution = remaining_contribution + :amount,
                        updated_at = datetime('now')
                    WHERE user_id = :user_id
                """),
                {"amount": amount, "user_id": user_id}
            )
        
        # 记录交易日志
        self._log_contribution_transaction(
            user_id=user_id,
            amount=amount,
            transaction_type="add",
            contribution_type=contribution_type.value,
            description=description,
            related_id=related_id
        )
        
        self.session.commit()
        
        return self.get_user_contribution(user_id)
    
    def consume_contribution(
        self,
        user_id: int,
        amount: float,
        description: str = "",
        related_id: Optional[int] = None
    ) -> Dict:
        """
        消费贡献值
        
        Args:
            user_id: 用户ID
            amount: 金额
            description: 描述
            related_id: 关联ID
        
        Returns:
            更新后的贡献值
        """
        # 检查余额是否足够
        contribution = self.get_user_contribution(user_id)
        
        if contribution["remaining_contribution"] < amount:
            raise ValueError(f"贡献值不足，当前余额：{contribution['remaining_contribution']}，需要：{amount}")
        
        # 扣除贡献值
        self.session.execute(
            text("""
                UPDATE user_contributions_v2
                SET remaining_contribution = remaining_contribution - :amount,
                    consumed_contribution = consumed_contribution + :amount,
                    updated_at = datetime('now')
                WHERE user_id = :user_id
            """),
            {"amount": amount, "user_id": user_id}
        )
        
        # 记录交易日志
        self._log_contribution_transaction(
            user_id=user_id,
            amount=amount,
            transaction_type="consume",
            contribution_type="consumed",
            description=description,
            related_id=related_id
        )
        
        self.session.commit()
        
        return self.get_user_contribution(user_id)
    
    def _log_contribution_transaction(
        self,
        user_id: int,
        amount: float,
        transaction_type: str,
        contribution_type: str,
        description: str = "",
        related_id: Optional[int] = None
    ):
        """
        记录贡献值交易日志
        """
        # 这里可以扩展为记录到专门的交易日志表
        # 现在暂时记录到audit_logs
        self.session.execute(
            text("""
                INSERT INTO audit_logs (
                    user_id, action, description, created_at
                ) VALUES (
                    :user_id, :action, :description, datetime('now')
                )
            """),
            {
                "user_id": user_id,
                "action": f"contribution_{transaction_type}",
                "description": f"{description}：{amount} ({contribution_type})"
            }
        )
    
    def calculate_project_contribution(
        self,
        difficulty_coefficient: float,
        quality_score: float,
        participation_rate: float
    ) -> float:
        """
        计算项目贡献值
        
        公式：项目贡献值 = 项目难度系数 × 完成质量评分 × 参与度占比
        
        Args:
            difficulty_coefficient: 项目难度系数（0.5-2.0）
            quality_score: 完成质量评分（0-10）
            participation_rate: 参与度占比（0-1）
        
        Returns:
            项目贡献值
        """
        project_contribution = difficulty_coefficient * quality_score * participation_rate * 10
        return project_contribution
    
    def get_contribution_ranking(
        self,
        limit: int = 10,
        order_by: str = "cumulative"
    ) -> list:
        """
        获取贡献值排行榜
        
        Args:
            limit: 返回数量
            order_by: 排序字段（cumulative/project/remaining）
        
        Returns:
            排行榜列表
        """
        if order_by not in ["cumulative", "project", "remaining"]:
            order_by = "cumulative"
        
        column_map = {
            "cumulative": "cumulative_contribution",
            "project": "project_contribution",
            "remaining": "remaining_contribution"
        }
        
        order_column = column_map[order_by]
        
        results = self.session.execute(
            text(f"""
                SELECT 
                    uc.user_id,
                    u.name,
                    u.partner_level,
                    uc.{order_column},
                    uc.updated_at
                FROM user_contributions_v2 uc
                JOIN users u ON uc.user_id = u.id
                ORDER BY uc.{order_column} DESC
                LIMIT :limit
            """),
            {"limit": limit}
        ).fetchall()
        
        ranking = []
        for rank, (user_id, name, partner_level, contribution, updated_at) in enumerate(results, 1):
            ranking.append({
                "rank": rank,
                "user_id": user_id,
                "name": name,
                "partner_level": partner_level or 'normal_user',
                "contribution": contribution or 0.0,
                "updated_at": updated_at
            })
        
        return ranking
    
    def get_user_rank(self, user_id: int, order_by: str = "cumulative") -> Optional[int]:
        """
        获取用户排名
        
        Args:
            user_id: 用户ID
            order_by: 排序字段
        
        Returns:
            排名（如果用户不存在返回None）
        """
        if order_by not in ["cumulative", "project", "remaining"]:
            order_by = "cumulative"
        
        column_map = {
            "cumulative": "cumulative_contribution",
            "project": "project_contribution",
            "remaining": "remaining_contribution"
        }
        
        order_column = column_map[order_by]
        
        result = self.session.execute(
            text(f"""
                SELECT COUNT(*) + 1 as rank
                FROM user_contributions_v2 uc1
                WHERE uc1.{order_column} > (
                    SELECT {order_column}
                    FROM user_contributions_v2 uc2
                    WHERE uc2.user_id = :user_id
                )
            """),
            {"user_id": user_id}
        ).fetchone()
        
        return result[0] if result else None


# 便捷函数
def create_contribution_manager(session: Session) -> ContributionManagerV2:
    """创建贡献值管理器实例"""
    return ContributionManagerV2(session)


if __name__ == "__main__":
    # 测试代码
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    DATABASE_URL = "sqlite:///auth.db"
    engine = create_engine(DATABASE_URL, echo=False)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    try:
        manager = create_contribution_manager(session)
        
        print("="*60)
        print("V2.0 三维贡献值模型测试")
        print("="*60)
        
        # 测试1：获取用户贡献值
        print("\n测试1：获取用户贡献值")
        for user_id in [1, 2, 3]:
            contribution = manager.get_user_contribution(user_id)
            print(f"\n用户{user_id}：")
            print(f"  累计贡献值：{contribution['cumulative_contribution']}")
            print(f"  项目贡献值：{contribution['project_contribution']}")
            print(f"  剩余贡献值：{contribution['remaining_contribution']}")
            print(f"  消费贡献值：{contribution['consumed_contribution']}")
        
        # 测试2：添加项目贡献值
        print("\n\n测试2：添加项目贡献值")
        project_contribution = manager.calculate_project_contribution(
            difficulty_coefficient=1.5,
            quality_score=9.0,
            participation_rate=0.8
        )
        print(f"项目贡献值计算：{project_contribution}")
        
        updated = manager.add_contribution(
            user_id=1,
            amount=project_contribution,
            contribution_type=ContributionType.PROJECT,
            description="完成品牌设计项目"
        )
        print(f"用户1更新后的贡献值：")
        print(f"  项目贡献值：{updated['project_contribution']}")
        print(f"  累计贡献值：{updated['cumulative_contribution']}")
        
        # 测试3：添加推荐奖励
        print("\n\n测试3：添加推荐奖励")
        updated = manager.add_contribution(
            user_id=2,
            amount=100.0,
            contribution_type=ContributionType.REFERRAL,
            description="推荐新用户奖励"
        )
        print(f"用户2更新后的贡献值：")
        print(f"  推荐奖励：{updated['referral_reward']}")
        print(f"  累计贡献值：{updated['cumulative_contribution']}")
        
        # 测试4：贡献值排行榜
        print("\n\n测试4：贡献值排行榜（累计贡献值）")
        ranking = manager.get_contribution_ranking(limit=5, order_by="cumulative")
        for item in ranking:
            print(f"  第{item['rank']}名：{item['name']} - {item['contribution']:.2f}")
        
        # 测试5：用户排名
        print("\n\n测试5：用户排名")
        for user_id in [1, 2, 3]:
            rank = manager.get_user_rank(user_id, order_by="cumulative")
            print(f"  用户{user_id}排名：第{rank}名")
        
        print("\n✅ 测试完成！")
        
    finally:
        session.close()
