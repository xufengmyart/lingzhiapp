"""
灵值生态园 - 分红股权管理系统
基于合伙人模式的分红股权机制

版本: v1.0
更新日期: 2026年1月25日
"""

import os
import sys
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Optional, List, Dict, Tuple
from enum import Enum

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, and_, or_, func
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# 导入模型
from src.auth.models_extended import (
    User, DividendPool, EquityHolding, DividendDistribution,
    UserMemberLevel, MemberLevel, ReferralCommission
)

# 导入用户管理
from src.auth.my_user import MyUser, TransactionType

# 数据库配置
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "auth.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class DividendPoolStatus(Enum):
    """分红池状态枚举"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CLOSED = "closed"


class EquityStatus(Enum):
    """股权状态枚举"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TERMINATED = "terminated"


class DividendStatus(Enum):
    """分红状态枚举"""
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"


class DividendManager:
    """分红股权管理系统核心类"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化分红管理系统
        
        Args:
            db_session: 数据库会话，如果为None则创建新会话
        """
        self.session = db_session if db_session else SessionLocal()
        self.user_mgr = MyUser(self.session)
    
    def __enter__(self):
        """上下文管理器入口"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()
    
    def close(self):
        """关闭数据库会话"""
        if self.session:
            self.session.close()
    
    def commit(self):
        """提交事务"""
        try:
            self.session.commit()
            return True
        except Exception as e:
            self.session.rollback()
            print(f"提交事务失败: {str(e)}")
            return False
    
    # ==================== 分红池管理 ====================
    
    def create_dividend_pool(
        self,
        pool_name: str,
        pool_type: str = "expert",
        initial_amount: Optional[Decimal] = None
    ) -> Optional[DividendPool]:
        """
        创建分红池
        
        Args:
            pool_name: 分红池名称
            pool_type: 分红池类型（expert/general）
            initial_amount: 初始金额
        
        Returns:
            分红池对象，创建失败返回None
        """
        try:
            # 创建分红池
            pool = DividendPool(
                pool_name=pool_name,
                pool_type=pool_type,
                total_pool_amount=initial_amount or Decimal("0.0"),
                available_amount=initial_amount or Decimal("0.0"),
                distributed_amount=Decimal("0.0"),
                status=DividendPoolStatus.ACTIVE.value
            )
            
            self.session.add(pool)
            self.commit()
            
            print(f"✅ 分红池创建成功: {pool_name} (ID: {pool.id})")
            return pool
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 创建分红池失败: {str(e)}")
            return None
    
    def get_dividend_pool(self, pool_id: int) -> Optional[DividendPool]:
        """
        获取分红池信息
        
        Args:
            pool_id: 分红池ID
        
        Returns:
            分红池对象
        """
        try:
            pool = self.session.query(DividendPool).filter(DividendPool.id == pool_id).first()
            return pool
        except Exception as e:
            print(f"❌ 获取分红池信息失败: {str(e)}")
            return None
    
    def add_to_dividend_pool(
        self,
        pool_id: int,
        amount: Decimal,
        description: Optional[str] = None
    ) -> bool:
        """
        向分红池注资
        
        Args:
            pool_id: 分红池ID
            amount: 注资金额
            description: 描述
        
        Returns:
            是否成功
        """
        try:
            pool = self.get_dividend_pool(pool_id)
            if not pool:
                print(f"❌ 分红池不存在: ID={pool_id}")
                return False
            
            # 更新分红池
            pool.total_pool_amount += amount
            pool.available_amount += amount
            pool.updated_at = datetime.now()
            
            # 记录审计日志
            from src.auth.my_user import AuditLog
            log = AuditLog(
                user_id=0,  # 系统操作
                action="add_to_dividend_pool",
                resource_type="dividend_pool",
                resource_id=pool_id,
                description=f"分红池注资: +{amount} 元 ({description or '无描述'})"
            )
            self.session.add(log)
            
            self.commit()
            print(f"✅ 分红池注资成功: {pool.pool_name}, +{amount} 元")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 分红池注资失败: {str(e)}")
            return False
    
    def add_referral_commission_to_pool(self) -> bool:
        """
        将待支付推荐佣金的5%添加到分红池
        
        Returns:
            是否成功
        """
        try:
            # 获取专家分红池
            expert_pool = self.session.query(DividendPool).filter(
                DividendPool.pool_type == "expert",
                DividendPool.status == DividendPoolStatus.ACTIVE.value
            ).first()
            
            if not expert_pool:
                print(f"❌ 专家分红池不存在")
                return False
            
            # 获取所有待支付的推荐佣金
            pending_commissions = self.session.query(ReferralCommission).filter(
                ReferralCommission.status == "pending"
            ).all()
            
            if not pending_commissions:
                print(f"⚠️  无待支付推荐佣金")
                return True
            
            # 计算总额
            total_dividend_contribution = sum(
                c.dividend_pool_contribution for c in pending_commissions
            )
            
            if total_dividend_contribution <= 0:
                return True
            
            # 添加到分红池
            expert_pool.total_pool_amount += total_dividend_contribution
            expert_pool.available_amount += total_dividend_contribution
            expert_pool.updated_at = datetime.now()
            
            # 记录审计日志
            from src.auth.my_user import AuditLog
            log = AuditLog(
                user_id=0,  # 系统操作
                action="add_commission_to_pool",
                resource_type="dividend_pool",
                resource_id=expert_pool.id,
                description=f"推荐佣金分红池注资: +{total_dividend_contribution} 元 ({len(pending_commissions)}笔佣金)"
            )
            self.session.add(log)
            
            self.commit()
            print(f"✅ 推荐佣金分红池注资成功: +{total_dividend_contribution} 元 ({len(pending_commissions)}笔)")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 推荐佣金分红池注资失败: {str(e)}")
            return False
    
    # ==================== 股权管理 ====================
    
    def grant_equity(
        self,
        user_id: int,
        pool_id: int,
        equity_percentage: float,
        expires_date: Optional[datetime] = None
    ) -> bool:
        """
        授予用户股权
        
        Args:
            user_id: 用户ID
            pool_id: 分红池ID
            equity_percentage: 股权百分比（0-100）
            expires_date: 过期日期
        
        Returns:
            是否成功
        """
        try:
            # 检查用户是否存在
            user = self.session.query(User).filter(User.id == user_id).first()
            if not user:
                print(f"❌ 用户不存在: ID={user_id}")
                return False
            
            # 检查分红池是否存在
            pool = self.get_dividend_pool(pool_id)
            if not pool:
                print(f"❌ 分红池不存在: ID={pool_id}")
                return False
            
            # 检查是否已持有股权
            existing = self.session.query(EquityHolding).filter(
                and_(
                    EquityHolding.user_id == user_id,
                    EquityHolding.pool_id == pool_id,
                    EquityHolding.status == EquityStatus.ACTIVE.value
                )
            ).first()
            
            if existing:
                print(f"❌ 用户已持有此分红池股权")
                return False
            
            # 创建股权持有记录
            equity = EquityHolding(
                user_id=user_id,
                pool_id=pool_id,
                equity_percentage=equity_percentage,
                granted_date=datetime.now(),
                expires_date=expires_date,
                status=EquityStatus.ACTIVE.value
            )
            
            self.session.add(equity)
            
            # 更新用户会员级别
            user_level = self.user_mgr.get_member_level(user_id)
            if user_level:
                user_level.equity_percentage = equity_percentage
                user_level.updated_at = datetime.now()
            
            # 记录审计日志
            from src.auth.my_user import AuditLog
            log = AuditLog(
                user_id=user_id,
                action="grant_equity",
                resource_type="equity_holding",
                resource_id=equity.id,
                description=f"授予股权: {equity_percentage}% (分红池: {pool.pool_name})"
            )
            self.session.add(log)
            
            self.commit()
            print(f"✅ 股权授予成功: {user.name}, {equity_percentage}% (分红池: {pool.pool_name})")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 授予股权失败: {str(e)}")
            return False
    
    def get_user_equities(self, user_id: int) -> List[EquityHolding]:
        """
        获取用户的股权持有记录
        
        Args:
            user_id: 用户ID
        
        Returns:
            股权持有记录列表
        """
        try:
            equities = self.session.query(EquityHolding).filter(
                EquityHolding.user_id == user_id,
                EquityHolding.status == EquityStatus.ACTIVE.value
            ).order_by(EquityHolding.granted_date.desc()).all()
            
            return equities
            
        except Exception as e:
            print(f"❌ 获取股权记录失败: {str(e)}")
            return []
    
    def revoke_equity(self, equity_id: int, reason: Optional[str] = None) -> bool:
        """
        撤销股权
        
        Args:
            equity_id: 股权ID
            reason: 撤销原因
        
        Returns:
            是否成功
        """
        try:
            equity = self.session.query(EquityHolding).filter(
                EquityHolding.id == equity_id
            ).first()
            
            if not equity:
                print(f"❌ 股权不存在: ID={equity_id}")
                return False
            
            # 更新用户会员级别
            user_level = self.user_mgr.get_member_level(equity.user_id)
            if user_level:
                user_level.equity_percentage = 0.0
                user_level.updated_at = datetime.now()
            
            # 撤销股权
            equity.status = EquityStatus.TERMINATED.value
            equity.expires_date = datetime.now()
            
            # 记录审计日志
            from src.auth.my_user import AuditLog
            log = AuditLog(
                user_id=equity.user_id,
                action="revoke_equity",
                resource_type="equity_holding",
                resource_id=equity_id,
                description=f"撤销股权: {reason or '无原因'}"
            )
            self.session.add(log)
            
            self.commit()
            print(f"✅ 股权撤销成功: ID={equity_id}")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 撤销股权失败: {str(e)}")
            return False
    
    # ==================== 分配分红 ====================
    
    def distribute_dividends(
        self,
        pool_id: int,
        distribution_amount: Optional[Decimal] = None
    ) -> bool:
        """
        分配分红
        
        Args:
            pool_id: 分红池ID
            distribution_amount: 分配金额（可选，如果不指定则使用可用金额）
        
        Returns:
            是否成功
        """
        try:
            pool = self.get_dividend_pool(pool_id)
            if not pool:
                print(f"❌ 分红池不存在: ID={pool_id}")
                return False
            
            # 确定分配金额
            if distribution_amount is None:
                distribution_amount = pool.available_amount
            elif distribution_amount > pool.available_amount:
                print(f"❌ 分配金额超过可用金额: 需要 {distribution_amount}, 可用 {pool.available_amount}")
                return False
            
            # 获取所有活跃股权持有者
            equities = self.session.query(EquityHolding).filter(
                EquityHolding.pool_id == pool_id,
                EquityHolding.status == EquityStatus.ACTIVE.value
            ).all()
            
            if not equities:
                print(f"❌ 无股权持有者")
                return False
            
            # 计算总股权比例
            total_equity_percentage = sum(e.equity_percentage for e in equities)
            
            if total_equity_percentage == 0:
                print(f"❌ 总股权比例为0")
                return False
            
            # 获取上一轮分配次数
            last_round = self.session.query(
                func.max(DividendDistribution.distribution_round)
            ).filter(DividendDistribution.pool_id == pool_id).scalar() or 0
            
            current_round = last_round + 1
            
            # 分配分红给每个股权持有者
            for equity in equities:
                # 计算分红金额
                dividend_amount = distribution_amount * (Decimal(str(equity.equity_percentage)) / Decimal(str(total_equity_percentage)))
                
                # 创建分红分配记录
                distribution = DividendDistribution(
                    pool_id=pool_id,
                    equity_holding_id=equity.id,
                    distribution_round=current_round,
                    total_pool_amount=distribution_amount,
                    user_equity_percentage=equity.equity_percentage,
                    dividend_amount=dividend_amount,
                    status=DividendStatus.PENDING.value,
                    created_at=datetime.now()
                )
                
                self.session.add(distribution)
                
                # 奖励贡献值（假设 1元 = 10贡献值）
                contribution_reward = float(dividend_amount) * 10
                
                # 更新用户累计分红收益
                user_level = self.user_mgr.get_member_level(equity.user_id)
                if user_level:
                    user_level.total_dividend_earned += dividend_amount
                    user_level.updated_at = datetime.now()
                
                if not self.user_mgr.add_contribution(
                    equity.user_id,
                    contribution_reward,
                    TransactionType.DIVIDEND,
                    f"分红收益: {pool.pool_name} 第{current_round}轮"
                ):
                    print(f"⚠️  贡献值奖励失败: 用户ID={equity.user_id}")
            
            # 更新分红池
            pool.available_amount -= distribution_amount
            pool.distributed_amount += distribution_amount
            pool.last_dividend_date = datetime.now()
            pool.updated_at = datetime.now()
            
            # 记录审计日志
            from src.auth.my_user import AuditLog
            log = AuditLog(
                user_id=0,  # 系统操作
                action="distribute_dividends",
                resource_type="dividend_pool",
                resource_id=pool_id,
                description=f"分配分红: {pool.pool_name} 第{current_round}轮, 总额: {distribution_amount}, 持有者: {len(equities)}人"
            )
            self.session.add(log)
            
            self.commit()
            print(f"✅ 分红分配成功: {pool.pool_name} 第{current_round}轮, {len(equities)}人, 总额: {distribution_amount}")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 分配分红失败: {str(e)}")
            return False
    
    def get_user_dividends(self, user_id: int) -> List[DividendDistribution]:
        """
        获取用户的分红记录
        
        Args:
            user_id: 用户ID
        
        Returns:
            分红记录列表
        """
        try:
            # 获取用户的所有股权
            equities = self.get_user_equities(user_id)
            equity_ids = [e.id for e in equities]
            
            # 获取分红记录
            dividends = self.session.query(DividendDistribution).filter(
                DividendDistribution.equity_holding_id.in_(equity_ids)
            ).order_by(DividendDistribution.created_at.desc()).all()
            
            return dividends
            
        except Exception as e:
            print(f"❌ 获取分红记录失败: {str(e)}")
            return []
    
    # ==================== 统计信息 ====================
    
    def get_dividend_stats(self, pool_id: int) -> Dict:
        """
        获取分红池统计信息
        
        Args:
            pool_id: 分红池ID
        
        Returns:
            统计数据字典
        """
        try:
            pool = self.get_dividend_pool(pool_id)
            if not pool:
                return {}
            
            # 获取活跃股权持有者数量
            equity_count = self.session.query(EquityHolding).filter(
                EquityHolding.pool_id == pool_id,
                EquityHolding.status == EquityStatus.ACTIVE.value
            ).count()
            
            # 获取分红分配次数
            distribution_rounds = self.session.query(
                func.max(DividendDistribution.distribution_round)
            ).filter(DividendDistribution.pool_id == pool_id).scalar() or 0
            
            stats = {
                "pool_name": pool.pool_name,
                "pool_type": pool.pool_type,
                "total_pool_amount": float(pool.total_pool_amount),
                "available_amount": float(pool.available_amount),
                "distributed_amount": float(pool.distributed_amount),
                "equity_holders": equity_count,
                "distribution_rounds": distribution_rounds,
                "last_dividend_date": pool.last_dividend_date.isoformat() if pool.last_dividend_date else None,
                "status": pool.status
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ 获取分红统计失败: {str(e)}")
            return {}


# ==================== 工厂函数 ====================

def get_dividend_manager() -> DividendManager:
    """
    获取分红管理器实例
    
    Returns:
        DividendManager 实例
    """
    return DividendManager()


# ==================== 示例使用 ====================

if __name__ == "__main__":
    # 示例：创建分红池和分配
    with get_dividend_manager() as div_mgr:
        # 创建专家分红池
        pool = div_mgr.create_dividend_pool(
            pool_name="专家分红池",
            pool_type="expert",
            initial_amount=Decimal("100000")  # 初始10万元
        )
        
        if pool:
            # 检查是否有用户达到专家级别并授予股权
            from src.auth.models_extended import MemberLevelType
            
            expert_level = div_mgr.session.query(MemberLevel).filter(
                MemberLevel.level_type == MemberLevelType.EXPERT.value
            ).first()
            
            if expert_level:
                # 查找专家级别的用户
                expert_users = div_mgr.session.query(UserMemberLevel).filter(
                    UserMemberLevel.level_id == expert_level.id
                ).all()
                
                for user_level in expert_users:
                    # 授予股权
                    div_mgr.grant_equity(
                        user_id=user_level.user_id,
                        pool_id=pool.id,
                        equity_percentage=expert_level.dividend_percentage
                    )
            
            # 获取分红池统计
            stats = div_mgr.get_dividend_stats(pool.id)
            print(f"分红池统计: {stats}")
