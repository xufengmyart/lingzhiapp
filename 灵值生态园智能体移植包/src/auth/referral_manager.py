"""
灵值生态园 - 推荐和佣金管理系统
基于合伙人模式的推荐奖励机制

版本: v1.0
更新日期: 2026年1月25日
"""

import os
import sys
import random
import string
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
    User, Role, UserMemberLevel, MemberLevel,
    Referral, ReferralCommission, Project
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


class ReferralType(Enum):
    """推荐关系类型枚举"""
    DIRECT = "direct"      # 直接推荐
    INDIRECT = "indirect"  # 间接推荐


class ReferralStatus(Enum):
    """推荐状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    CANCELLED = "cancelled"


class ReferralCommissionStatus(Enum):
    """佣金状态枚举"""
    PENDING = "pending"      # 待支付
    PAID = "paid"           # 已支付
    CANCELLED = "cancelled"  # 已取消


class ReferralManager:
    """推荐和佣金管理系统核心类"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化推荐管理系统
        
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
    
    # ==================== 推荐码管理 ====================
    
    def generate_referral_code(self) -> str:
        """
        生成推荐码
        
        Returns:
            推荐码（8位大写字母+数字组合）
        """
        characters = string.ascii_uppercase + string.digits
        while True:
            code = ''.join(random.choices(characters, k=8))
            # 检查推荐码是否已存在
            existing = self.session.query(Referral).filter(
                Referral.referral_code == code
            ).first()
            if not existing:
                return code
    
    def create_referral_relationship(
        self,
        referrer_id: int,
        referee_id: int,
        project_id: Optional[int] = None
    ) -> bool:
        """
        创建推荐关系
        
        Args:
            referrer_id: 推荐人ID
            referee_id: 被推荐人ID
            project_id: 关联项目ID
        
        Returns:
            是否创建成功
        """
        try:
            # 检查用户是否存在
            referrer = self.session.query(User).filter(User.id == referrer_id).first()
            referee = self.session.query(User).filter(User.id == referee_id).first()
            
            if not referrer or not referee:
                print(f"❌ 用户不存在")
                return False
            
            # 检查是否已存在推荐关系
            existing = self.session.query(Referral).filter(
                and_(
                    Referral.referrer_id == referrer_id,
                    Referral.referee_id == referee_id
                )
            ).first()
            
            if existing:
                print(f"❌ 推荐关系已存在")
                return False
            
            # 生成推荐码
            referral_code = self.generate_referral_code()
            
            # 创建推荐关系
            referral = Referral(
                referrer_id=referrer_id,
                referee_id=referee_id,
                referral_code=referral_code,
                project_id=project_id,
                relationship_type=ReferralType.DIRECT.value,
                status=ReferralStatus.ACTIVE.value
            )
            
            self.session.add(referral)
            
            # 奖励推荐人贡献值（新用户注册奖励）
            self.user_mgr.add_contribution(
                referrer_id,
                50.0,  # 推荐新用户奖励50贡献值
                TransactionType.TASK_REWARD,
                f"推荐新用户: {referee.name}"
            )
            
            # 奖励被推荐人贡献值（新用户通过推荐码注册奖励）
            self.user_mgr.add_contribution(
                referee_id,
                100.0,  # 通过推荐码注册奖励100贡献值
                TransactionType.TASK_REWARD,
                f"通过推荐码注册，推荐人: {referrer.name}"
            )
            
            self.commit()
            print(f"✅ 推荐关系创建成功: {referrer.name} -> {referee.name}")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 创建推荐关系失败: {str(e)}")
            return False
    
    def get_referral_by_code(self, referral_code: str) -> Optional[Referral]:
        """
        通过推荐码获取推荐关系
        
        Args:
            referral_code: 推荐码
        
        Returns:
            推荐关系对象
        """
        try:
            referral = self.session.query(Referral).filter(
                Referral.referral_code == referral_code,
                Referral.status == ReferralStatus.ACTIVE.value
            ).first()
            
            return referral
            
        except Exception as e:
            print(f"❌ 获取推荐关系失败: {str(e)}")
            return None
    
    def get_referrals_by_user(self, user_id: int) -> List[Referral]:
        """
        获取用户的推荐记录（作为推荐人）
        
        Args:
            user_id: 用户ID
        
        Returns:
            推荐关系列表
        """
        try:
            referrals = self.session.query(Referral).filter(
                Referral.referrer_id == user_id,
                Referral.status == ReferralStatus.ACTIVE.value
            ).order_by(Referral.created_at.desc()).all()
            
            return referrals
            
        except Exception as e:
            print(f"❌ 获取推荐记录失败: {str(e)}")
            return []
    
    def get_referrer_by_user(self, user_id: int) -> Optional[Referral]:
        """
        获取用户的推荐人（作为被推荐人）
        
        Args:
            user_id: 用户ID
        
        Returns:
            推荐关系对象
        """
        try:
            referral = self.session.query(Referral).filter(
                Referral.referee_id == user_id,
                Referral.status == ReferralStatus.ACTIVE.value
            ).first()
            
            return referral
            
        except Exception as e:
            print(f"❌ 获取推荐人失败: {str(e)}")
            return None
    
    # ==================== 佣金管理 ====================
    
    def calculate_commission_rate(self, referrer_id: int) -> float:
        """
        计算推荐人佣金比例
        
        Args:
            referrer_id: 推荐人ID
        
        Returns:
            佣金比例（0-1）
        """
        try:
            # 获取推荐人的会员级别
            user_level = self.user_mgr.get_member_level(referrer_id)
            if not user_level:
                return 0.05  # 默认5%
            
            # 根据会员级别返回佣金比例
            level = self.session.query(MemberLevel).filter(
                MemberLevel.id == user_level.level_id
            ).first()
            
            if level:
                return level.referral_commission_rate or 0.05
            
            return 0.05  # 默认5%
            
        except Exception as e:
            print(f"❌ 计算佣金比例失败: {str(e)}")
            return 0.05
    
    def create_referral_commission(
        self,
        referral_id: int,
        project_id: int,
        transaction_amount: Decimal
    ) -> bool:
        """
        创建推荐佣金记录
        
        Args:
            referral_id: 推荐关系ID
            project_id: 项目ID
            transaction_amount: 交易金额
        
        Returns:
            是否创建成功
        """
        try:
            # 获取推荐关系
            referral = self.session.query(Referral).filter(
                Referral.id == referral_id
            ).first()
            
            if not referral:
                print(f"❌ 推荐关系不存在: ID={referral_id}")
                return False
            
            # 计算佣金比例
            commission_rate = self.calculate_commission_rate(referral.referrer_id)
            
            # 计算佣金金额
            commission_amount = transaction_amount * Decimal(str(commission_rate))
            
            # 计算贡献给分红池的金额（5%）
            dividend_pool_contribution = commission_amount * Decimal("0.05")
            
            # 创建佣金记录
            commission = ReferralCommission(
                referral_id=referral_id,
                project_id=project_id,
                referrer_id=referral.referrer_id,
                transaction_amount=transaction_amount,
                commission_rate=commission_rate,
                commission_amount=commission_amount,
                dividend_pool_contribution=dividend_pool_contribution,
                status=ReferralCommissionStatus.PENDING.value
            )
            
            self.session.add(commission)
            
            # 记录审计日志
            from src.auth.my_user import AuditLog
            log = AuditLog(
                user_id=referral.referrer_id,
                action="create_commission",
                resource_type="referral_commission",
                resource_id=commission.id,
                description=f"创建推荐佣金: {commission_amount} 元（比例: {commission_rate*100}%）"
            )
            self.session.add(log)
            
            self.commit()
            print(f"✅ 推荐佣金创建成功: {commission_amount} 元")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 创建推荐佣金失败: {str(e)}")
            return False
    
    def pay_referral_commission(self, commission_id: int) -> bool:
        """
        支付推荐佣金
        
        Args:
            commission_id: 佣金ID
        
        Returns:
            是否支付成功
        """
        try:
            # 获取佣金记录
            commission = self.session.query(ReferralCommission).filter(
                ReferralCommission.id == commission_id
            ).first()
            
            if not commission:
                print(f"❌ 佣金记录不存在: ID={commission_id}")
                return False
            
            if commission.status == ReferralCommissionStatus.PAID.value:
                print(f"❌ 佣金已支付: ID={commission_id}")
                return False
            
            # 计算贡献值奖励（假设 1元 = 10贡献值）
            contribution_reward = float(commission.commission_amount) * 10
            
            # 奖励推荐人贡献值
            if not self.user_mgr.add_contribution(
                commission.referrer_id,
                contribution_reward,
                TransactionType.REFERRAL_COMMISSION,
                f"推荐佣金支付: {commission.commission_amount} 元"
            ):
                return False
            
            # 更新佣金状态
            commission.status = ReferralCommissionStatus.PAID.value
            commission.paid_at = datetime.now()
            
            self.commit()
            print(f"✅ 推荐佣金支付成功: {commission.commission_amount} 元 -> {contribution_reward} 贡献值")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 支付推荐佣金失败: {str(e)}")
            return False
    
    def get_pending_commissions(self, referrer_id: Optional[int] = None) -> List[ReferralCommission]:
        """
        获取待支付的佣金列表
        
        Args:
            referrer_id: 推荐人ID（可选）
        
        Returns:
            佣金列表
        """
        try:
            query = self.session.query(ReferralCommission).filter(
                ReferralCommission.status == ReferralCommissionStatus.PENDING.value
            )
            
            if referrer_id:
                query = query.filter(ReferralCommission.referrer_id == referrer_id)
            
            commissions = query.order_by(ReferralCommission.created_at.desc()).all()
            return commissions
            
        except Exception as e:
            print(f"❌ 获取待支付佣金失败: {str(e)}")
            return []
    
    def get_referral_stats(self, user_id: int) -> Dict:
        """
        获取用户推荐统计数据
        
        Args:
            user_id: 用户ID
        
        Returns:
            统计数据字典
        """
        try:
            # 获取直接推荐数量
            direct_referrals = self.session.query(Referral).filter(
                Referral.referrer_id == user_id,
                Referral.relationship_type == ReferralType.DIRECT.value,
                Referral.status == ReferralStatus.ACTIVE.value
            ).count()
            
            # 获取累计佣金
            total_commission = self.session.query(
                func.sum(ReferralCommission.commission_amount)
            ).filter(
                ReferralCommission.referrer_id == user_id,
                ReferralCommission.status == ReferralCommissionStatus.PAID.value
            ).scalar() or Decimal("0.0")
            
            # 获取待支付佣金
            pending_commission = self.session.query(
                func.sum(ReferralCommission.commission_amount)
            ).filter(
                ReferralCommission.referrer_id == user_id,
                ReferralCommission.status == ReferralCommissionStatus.PENDING.value
            ).scalar() or Decimal("0.0")
            
            stats = {
                "direct_referrals": direct_referrals,
                "total_commission": float(total_commission),
                "pending_commission": float(pending_commission),
                "commission_rate": self.calculate_commission_rate(user_id)
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ 获取推荐统计失败: {str(e)}")
            return {}
    
    # ==================== 推荐树管理 ====================
    
    def get_referral_tree(self, user_id: int, max_depth: int = 3) -> Dict:
        """
        获取推荐树结构
        
        Args:
            user_id: 用户ID
            max_depth: 最大深度
        
        Returns:
            推荐树字典
        """
        try:
            def build_tree(uid, depth):
                if depth > max_depth:
                    return None
                
                user = self.session.query(User).filter(User.id == uid).first()
                if not user:
                    return None
                
                # 获取直接推荐的用户
                referrals = self.session.query(Referral).filter(
                    Referral.referrer_id == uid,
                    Referral.relationship_type == ReferralType.DIRECT.value,
                    Referral.status == ReferralStatus.ACTIVE.value
                ).all()
                
                children = []
                for ref in referrals:
                    child = build_tree(ref.referee_id, depth + 1)
                    if child:
                        children.append(child)
                
                return {
                    "user_id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "depth": depth,
                    "children": children,
                    "children_count": len(children)
                }
            
            tree = build_tree(user_id, 0)
            return tree
            
        except Exception as e:
            print(f"❌ 获取推荐树失败: {str(e)}")
            return {}


# ==================== 工厂函数 ====================

def get_referral_manager() -> ReferralManager:
    """
    获取推荐管理器实例
    
    Returns:
        ReferralManager 实例
    """
    return ReferralManager()


# ==================== 示例使用 ====================

if __name__ == "__main__":
    # 示例：创建推荐关系和佣金
    with get_referral_manager() as ref_mgr:
        # 获取用户
        referrer = ref_mgr.session.query(User).filter(User.id == 1).first()
        referee = ref_mgr.session.query(User).filter(User.id == 2).first()
        
        if referrer and referee:
            # 创建推荐关系
            ref_mgr.create_referral_relationship(referrer.id, referee.id)
            
            # 获取推荐统计
            stats = ref_mgr.get_referral_stats(referrer.id)
            print(f"推荐统计: {stats}")
            
            # 获取推荐树
            tree = ref_mgr.get_referral_tree(referrer.id)
            print(f"推荐树: {tree}")
