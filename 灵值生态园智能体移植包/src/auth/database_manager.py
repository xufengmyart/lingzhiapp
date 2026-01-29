"""
数据库连接管理工具
支持以许锋身份连接数据库并管理生态机制
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, date
import os
from typing import List, Optional, Dict, Any
from models import (
    Base, User, Role, Permission, AuditLog, Session as UserSession,
    MemberLevelConfig, Partner, Project, ProjectParticipation,
    Referral, Commission, DividendPool, Dividend,
    MemberLevel, PartnerStatus, ProjectStatus, ReferralStatus
)


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, db_url: str = "sqlite:///./auth.db"):
        """
        初始化数据库管理器
        
        Args:
            db_url: 数据库连接URL
        """
        self.db_url = db_url
        self.engine = create_engine(db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine, autocommit=False, autoflush=False)
        self.current_user = None  # 当前登录用户
        
    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(bind=self.engine)
        print("✓ 数据库表创建成功")
    
    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()
    
    def login_as_xufeng(self) -> Dict[str, Any]:
        """
        以许锋身份登录
        
        Returns:
            登录结果字典
        """
        session = self.get_session()
        try:
            # 查找许锋账号
            user = session.query(User).filter(
                User.email == "xufeng@meiyue.com"
            ).first()
            
            if not user:
                return {
                    "success": False,
                    "message": "许锋账号不存在",
                    "user": None
                }
            
            self.current_user = user
            
            # 记录登录日志
            audit_log = AuditLog(
                user_id=user.id,
                action="login",
                description="许锋登录数据库",
                status="success"
            )
            session.add(audit_log)
            session.commit()
            
            return {
                "success": True,
                "message": "许锋登录成功",
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "position": user.position,
                    "roles": [role.name for role in user.roles],
                    "permissions": user.get_all_permissions()
                }
            }
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"登录失败: {str(e)}",
                "user": None
            }
        finally:
            session.close()
    
    def get_database_info(self) -> Dict[str, Any]:
        """
        获取数据库信息
        
        Returns:
            数据库信息字典
        """
        if not self.current_user:
            return {
                "success": False,
                "message": "未登录，请先登录"
            }
        
        session = self.get_session()
        try:
            info = {
                "success": True,
                "current_user": {
                    "id": self.current_user.id,
                    "name": self.current_user.name,
                    "email": self.current_user.email,
                    "position": self.current_user.position
                },
                "statistics": {
                    "users": session.query(User).count(),
                    "roles": session.query(Role).count(),
                    "permissions": session.query(Permission).count(),
                    "partners": session.query(Partner).count(),
                    "projects": session.query(Project).count(),
                    "referrals": session.query(Referral).count(),
                    "commissions": session.query(Commission).count(),
                    "dividend_pools": session.query(DividendPool).count()
                }
            }
            return info
        except SQLAlchemyError as e:
            return {
                "success": False,
                "message": f"获取数据库信息失败: {str(e)}"
            }
        finally:
            session.close()
    
    # ==================== 会员级别管理 ====================
    
    def init_member_levels(self) -> Dict[str, Any]:
        """
        初始化会员级别配置
        
        Returns:
            初始化结果
        """
        if not self.current_user:
            return {"success": False, "message": "未登录"}
        
        session = self.get_session()
        try:
            # 检查是否已初始化
            existing = session.query(MemberLevelConfig).count()
            if existing > 0:
                return {
                    "success": False,
                    "message": f"会员级别已存在({existing}条)，无需重复初始化"
                }
            
            # 创建会员级别配置
            levels = [
                {
                    "level": MemberLevel.ORDINARY,
                    "name": "普通会员",
                    "description": "基础会员，享受基本权益",
                    "min_revenue": 0,
                    "min_referrals": 0,
                    "dividend_ratio": 0,
                    "commission_ratio": 5,
                    "benefits": "参与项目、获得项目利润"
                },
                {
                    "level": MemberLevel.SENIOR,
                    "name": "高级会员",
                    "description": "活跃会员，享受更多权益",
                    "min_revenue": 10000,
                    "min_referrals": 5,
                    "dividend_ratio": 0,
                    "commission_ratio": 8,
                    "benefits": "参与项目、获得项目利润、获得推荐佣金"
                },
                {
                    "level": MemberLevel.EXPERT,
                    "name": "专家会员",
                    "description": "核心会员，享受分红股权",
                    "min_revenue": 50000,
                    "min_referrals": 20,
                    "dividend_ratio": 0.1,  # 0.1%分红股权
                    "commission_ratio": 10,
                    "benefits": "参与项目、获得项目利润、获得推荐佣金、获得分红股权（0.1%）"
                },
                {
                    "level": MemberLevel.VIP,
                    "name": "VIP会员",
                    "description": "顶级会员，享受最高权益",
                    "min_revenue": 100000,
                    "min_referrals": 50,
                    "dividend_ratio": 0.2,  # 0.2%分红股权
                    "commission_ratio": 12,
                    "benefits": "参与项目、获得项目利润、获得推荐佣金、获得分红股权（0.2%）、VIP专属服务"
                }
            ]
            
            for level_data in levels:
                level = MemberLevelConfig(**level_data)
                session.add(level)
            
            session.commit()
            
            # 记录操作日志
            audit_log = AuditLog(
                user_id=self.current_user.id,
                action="init_member_levels",
                resource_type="MemberLevelConfig",
                description=f"初始化{len(levels)}个会员级别",
                status="success"
            )
            session.add(audit_log)
            session.commit()
            
            return {
                "success": True,
                "message": f"成功初始化{len(levels)}个会员级别",
                "levels": [level["name"] for level in levels]
            }
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"初始化失败: {str(e)}"
            }
        finally:
            session.close()
    
    def get_member_levels(self) -> List[Dict[str, Any]]:
        """
        获取所有会员级别
        
        Returns:
            会员级别列表
        """
        session = self.get_session()
        try:
            levels = session.query(MemberLevelConfig).all()
            return [
                {
                    "id": level.id,
                    "level": level.level.value,
                    "name": level.name,
                    "description": level.description,
                    "min_revenue": level.min_revenue,
                    "min_referrals": level.min_referrals,
                    "dividend_ratio": level.dividend_ratio,
                    "commission_ratio": level.commission_ratio,
                    "benefits": level.benefits
                }
                for level in levels
            ]
        except SQLAlchemyError as e:
            print(f"获取会员级别失败: {str(e)}")
            return []
        finally:
            session.close()
    
    # ==================== 合伙人管理 ====================
    
    def create_partner(self, user_id: int, **kwargs) -> Dict[str, Any]:
        """
        创建合伙人
        
        Args:
            user_id: 用户ID
            **kwargs: 其他参数
            
        Returns:
            创建结果
        """
        if not self.current_user:
            return {"success": False, "message": "未登录"}
        
        session = self.get_session()
        try:
            # 检查用户是否已是合伙人
            existing = session.query(Partner).filter(Partner.user_id == user_id).first()
            if existing:
                return {
                    "success": False,
                    "message": f"该用户已是合伙人(ID: {existing.id})"
                }
            
            # 生成合伙人代码
            partner_code = f"P{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            partner = Partner(
                user_id=user_id,
                partner_code=partner_code,
                member_level=kwargs.get('member_level', MemberLevel.ORDINARY),
                status=kwargs.get('status', PartnerStatus.PENDING),
                bank_account=kwargs.get('bank_account'),
                bank_name=kwargs.get('bank_name'),
                account_holder=kwargs.get('account_holder'),
                notes=kwargs.get('notes')
            )
            
            session.add(partner)
            session.commit()
            
            # 记录操作日志
            audit_log = AuditLog(
                user_id=self.current_user.id,
                action="create_partner",
                resource_type="Partner",
                resource_id=partner.id,
                description=f"创建合伙人: {partner_code}",
                status="success"
            )
            session.add(audit_log)
            session.commit()
            
            return {
                "success": True,
                "message": f"成功创建合伙人: {partner_code}",
                "partner": {
                    "id": partner.id,
                    "partner_code": partner.partner_code,
                    "member_level": partner.member_level.value
                }
            }
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"创建合伙人失败: {str(e)}"
            }
        finally:
            session.close()
    
    # ==================== 项目管理 ====================
    
    def create_project(self, name: str, partner_id: int, **kwargs) -> Dict[str, Any]:
        """
        创建项目
        
        Args:
            name: 项目名称
            partner_id: 合伙人ID
            **kwargs: 其他参数
            
        Returns:
            创建结果
        """
        if not self.current_user:
            return {"success": False, "message": "未登录"}
        
        session = self.get_session()
        try:
            # 生成项目代码
            project_code = f"PRJ{datetime.now().strftime('%Y%m%d%H%M%S')}"
            
            project = Project(
                name=name,
                code=project_code,
                partner_id=partner_id,
                description=kwargs.get('description'),
                status=kwargs.get('status', ProjectStatus.DRAFT),
                total_investment=kwargs.get('total_investment', 0),
                profit_ratio=kwargs.get('profit_ratio', 30),  # 默认30%利润分配
                commission_ratio=kwargs.get('commission_ratio', 10),  # 默认10%推荐佣金
                start_date=kwargs.get('start_date'),
                end_date=kwargs.get('end_date'),
                notes=kwargs.get('notes')
            )
            
            session.add(project)
            session.commit()
            
            # 记录操作日志
            audit_log = AuditLog(
                user_id=self.current_user.id,
                action="create_project",
                resource_type="Project",
                resource_id=project.id,
                description=f"创建项目: {name}",
                status="success"
            )
            session.add(audit_log)
            session.commit()
            
            return {
                "success": True,
                "message": f"成功创建项目: {project_code}",
                "project": {
                    "id": project.id,
                    "code": project.code,
                    "name": project.name
                }
            }
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"创建项目失败: {str(e)}"
            }
        finally:
            session.close()
    
    # ==================== 推荐关系管理 ====================
    
    def create_referral(
        self,
        referrer_id: int,
        referee_id: int,
        project_id: int,
        opportunity_id: str,
        opportunity_name: str,
        amount: float,
        source: str = "share"
    ) -> Dict[str, Any]:
        """
        创建推荐记录
        
        Args:
            referrer_id: 推荐人ID
            referee_id: 被推荐人ID
            project_id: 项目ID
            opportunity_id: 创业机会ID
            opportunity_name: 创业机会名称
            amount: 购买金额
            source: 来源
            
        Returns:
            创建结果
        """
        if not self.current_user:
            return {"success": False, "message": "未登录"}
        
        session = self.get_session()
        try:
            # 获取项目信息
            project = session.query(Project).filter(Project.id == project_id).first()
            if not project:
                return {"success": False, "message": "项目不存在"}
            
            # 获取推荐人信息
            referrer = session.query(Partner).filter(Partner.id == referrer_id).first()
            if not referrer:
                return {"success": False, "message": "推荐人不存在"}
            
            # 计算佣金金额
            commission_ratio = project.commission_ratio
            commission_amount = amount * (commission_ratio / 100)
            
            # 创建推荐记录
            referral = Referral(
                referrer_id=referrer_id,
                referee_id=referee_id,
                project_id=project_id,
                opportunity_id=opportunity_id,
                opportunity_name=opportunity_name,
                amount=amount,
                commission_ratio=commission_ratio,
                commission_amount=commission_amount,
                status=ReferralStatus.PENDING,
                source=source
            )
            
            session.add(referral)
            session.commit()
            
            # 记录操作日志
            audit_log = AuditLog(
                user_id=self.current_user.id,
                action="create_referral",
                resource_type="Referral",
                resource_id=referral.id,
                description=f"创建推荐记录: {referrer.partner_code} -> {opportunity_name}",
                status="success"
            )
            session.add(audit_log)
            session.commit()
            
            return {
                "success": True,
                "message": "成功创建推荐记录",
                "referral": {
                    "id": referral.id,
                    "commission_amount": commission_amount,
                    "status": referral.status.value
                }
            }
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"创建推荐记录失败: {str(e)}"
            }
        finally:
            session.close()
    
    # ==================== 推荐佣金管理 ====================
    
    def confirm_referral(self, referral_id: int) -> Dict[str, Any]:
        """
        确认推荐并生成佣金
        
        Args:
            referral_id: 推荐记录ID
            
        Returns:
            确认结果
        """
        if not self.current_user:
            return {"success": False, "message": "未登录"}
        
        session = self.get_session()
        try:
            # 获取推荐记录
            referral = session.query(Referral).filter(Referral.id == referral_id).first()
            if not referral:
                return {"success": False, "message": "推荐记录不存在"}
            
            if referral.status != ReferralStatus.PENDING:
                return {"success": False, "message": "推荐记录状态不正确"}
            
            # 更新推荐状态
            referral.status = ReferralStatus.CONFIRMED
            referral.confirmed_at = datetime.now()
            
            # 创建佣金记录
            commission = Commission(
                partner_id=referral.referrer_id,
                referral_id=referral.id,
                amount=referral.commission_amount,
                ratio=referral.commission_ratio,
                status="pending",
                source="project",
                period=datetime.now().strftime("%Y-%m")
            )
            
            session.add(commission)
            session.commit()
            
            # 更新合伙人累计数据
            referrer = session.query(Partner).filter(Partner.id == referral.referrer_id).first()
            referrer.total_commission += referral.commission_amount
            referrer.total_referrals += 1
            session.commit()
            
            # 记录操作日志
            audit_log = AuditLog(
                user_id=self.current_user.id,
                action="confirm_referral",
                resource_type="Referral",
                resource_id=referral.id,
                description=f"确认推荐并生成佣金: {referral.commission_amount}元",
                status="success"
            )
            session.add(audit_log)
            session.commit()
            
            return {
                "success": True,
                "message": f"成功确认推荐，生成佣金: {referral.commission_amount}元",
                "commission": {
                    "id": commission.id,
                    "amount": commission.amount
                }
            }
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"确认推荐失败: {str(e)}"
            }
        finally:
            session.close()
    
    # ==================== 分红池管理 ====================
    
    def create_dividend_pool(self, period: str) -> Dict[str, Any]:
        """
        创建分红池
        
        Args:
            period: 周期（如：2024-01）
            
        Returns:
            创建结果
        """
        if not self.current_user:
            return {"success": False, "message": "未登录"}
        
        session = self.get_session()
        try:
            # 检查分红池是否已存在
            existing = session.query(DividendPool).filter(DividendPool.period == period).first()
            if existing:
                return {
                    "success": False,
                    "message": f"分红池{period}已存在"
                }
            
            # 计算本期总推荐佣金
            total_commission = session.query(Commission).filter(
                Commission.period == period,
                Commission.status == "pending"
            ).all()
            
            total_commission_amount = sum(c.amount for c in total_commission)
            
            # 分红池金额为总佣金的5%
            pool_amount = total_commission_amount * 0.05
            
            # 计算总股权（专家会员）
            expert_partners = session.query(Partner).filter(
                Partner.member_level == MemberLevel.EXPERT,
                Partner.status == PartnerStatus.ACTIVE
            ).all()
            
            total_equity = sum(p.dividend_equity for p in expert_partners)
            
            # 创建分红池
            dividend_pool = DividendPool(
                name=f"{period}分红池",
                period=period,
                total_commission=total_commission_amount,
                pool_amount=pool_amount,
                total_equity=total_equity,
                remaining_amount=pool_amount,
                status="active",
                calculation_date=datetime.now()
            )
            
            session.add(dividend_pool)
            session.commit()
            
            # 记录操作日志
            audit_log = AuditLog(
                user_id=self.current_user.id,
                action="create_dividend_pool",
                resource_type="DividendPool",
                resource_id=dividend_pool.id,
                description=f"创建分红池: {period}, 金额: {pool_amount}元",
                status="success"
            )
            session.add(audit_log)
            session.commit()
            
            return {
                "success": True,
                "message": f"成功创建分红池: {period}",
                "pool": {
                    "id": dividend_pool.id,
                    "period": period,
                    "total_commission": total_commission_amount,
                    "pool_amount": pool_amount,
                    "total_equity": total_equity
                }
            }
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"创建分红池失败: {str(e)}"
            }
        finally:
            session.close()
    
    def distribute_dividends(self, pool_id: int) -> Dict[str, Any]:
        """
        分配分红
        
        Args:
            pool_id: 分红池ID
            
        Returns:
            分配结果
        """
        if not self.current_user:
            return {"success": False, "message": "未登录"}
        
        session = self.get_session()
        try:
            # 获取分红池
            pool = session.query(DividendPool).filter(DividendPool.id == pool_id).first()
            if not pool:
                return {"success": False, "message": "分红池不存在"}
            
            if pool.status != "active":
                return {"success": False, "message": "分红池状态不正确"}
            
            # 获取所有专家会员
            expert_partners = session.query(Partner).filter(
                Partner.member_level == MemberLevel.EXPERT,
                Partner.status == PartnerStatus.ACTIVE
            ).all()
            
            if not expert_partners:
                return {"success": False, "message": "没有专家会员"}
            
            # 分配分红
            dividends_created = []
            for partner in expert_partners:
                if partner.dividend_equity <= 0:
                    continue
                
                # 计算分红金额
                dividend_amount = pool.pool_amount * (partner.dividend_equity / pool.total_equity)
                
                # 创建分红记录
                dividend = Dividend(
                    pool_id=pool_id,
                    partner_id=partner.id,
                    equity=partner.dividend_equity,
                    pool_amount=pool.pool_amount,
                    dividend_amount=dividend_amount,
                    status="pending",
                    period=pool.period
                )
                
                session.add(dividend)
                dividends_created.append(dividend.dividend_amount)
                
                # 更新分红池
                pool.distributed_amount += dividend_amount
                pool.remaining_amount -= dividend_amount
            
            pool.status = "closed"
            pool.distribution_date = datetime.now()
            session.commit()
            
            # 记录操作日志
            audit_log = AuditLog(
                user_id=self.current_user.id,
                action="distribute_dividends",
                resource_type="DividendPool",
                resource_id=pool_id,
                description=f"分配分红: {pool.period}, {len(dividends_created)}人, 总金额: {pool.distributed_amount}元",
                status="success"
            )
            session.add(audit_log)
            session.commit()
            
            return {
                "success": True,
                "message": f"成功分配分红给{len(dividends_created)}位专家会员",
                "summary": {
                    "period": pool.period,
                    "total_amount": pool.distributed_amount,
                    "partner_count": len(dividends_created)
                }
            }
        except SQLAlchemyError as e:
            session.rollback()
            return {
                "success": False,
                "message": f"分配分红失败: {str(e)}"
            }
        finally:
            session.close()
    
    # ==================== 综合查询 ====================
    
    def get_ecosystem_summary(self) -> Dict[str, Any]:
        """
        获取生态机制汇总信息
        
        Returns:
            汇总信息
        """
        if not self.current_user:
            return {"success": False, "message": "未登录"}
        
        session = self.get_session()
        try:
            # 基础统计
            total_partners = session.query(Partner).count()
            active_partners = session.query(Partner).filter(Partner.status == PartnerStatus.ACTIVE).count()
            expert_partners = session.query(Partner).filter(Partner.member_level == MemberLevel.EXPERT).count()
            
            # 项目统计
            total_projects = session.query(Project).count()
            ongoing_projects = session.query(Project).filter(Project.status == ProjectStatus.ONGOING).count()
            
            # 推荐统计
            total_referrals = session.query(Referral).count()
            confirmed_referrals = session.query(Referral).filter(Referral.status == ReferralStatus.CONFIRMED).count()
            
            # 佣金统计
            total_commissions = session.query(Commission).count()
            pending_commissions = session.query(Commission).filter(Commission.status == "pending").count()
            total_commission_amount = session.query(Commission).all()
            sum_commission_amount = sum(c.amount for c in total_commission_amount)
            
            # 分红统计
            total_pools = session.query(DividendPool).count()
            active_pools = session.query(DividendPool).filter(DividendPool.status == "active").count()
            total_dividend_amount = session.query(Dividend).all()
            sum_dividend_amount = sum(d.dividend_amount for d in total_dividend_amount)
            
            return {
                "success": True,
                "summary": {
                    "partners": {
                        "total": total_partners,
                        "active": active_partners,
                        "expert": expert_partners
                    },
                    "projects": {
                        "total": total_projects,
                        "ongoing": ongoing_projects
                    },
                    "referrals": {
                        "total": total_referrals,
                        "confirmed": confirmed_referrals
                    },
                    "commissions": {
                        "total": total_commissions,
                        "pending": pending_commissions,
                        "total_amount": round(sum_commission_amount, 2)
                    },
                    "dividends": {
                        "total_pools": total_pools,
                        "active_pools": active_pools,
                        "total_distributed": round(sum_dividend_amount, 2)
                    }
                },
                "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except SQLAlchemyError as e:
            return {
                "success": False,
                "message": f"获取汇总信息失败: {str(e)}"
            }
        finally:
            session.close()


# ==================== 便捷函数 ====================

def get_db_manager() -> DatabaseManager:
    """
    获取数据库管理器实例
    
    Returns:
        DatabaseManager实例
    """
    return DatabaseManager()


if __name__ == "__main__":
    # 测试代码
    print("=== 数据库管理器测试 ===")
    
    # 创建管理器
    db_manager = DatabaseManager()
    
    # 创建表
    print("\n1. 创建数据库表...")
    db_manager.create_tables()
    
    # 以许锋身份登录
    print("\n2. 以许锋身份登录...")
    login_result = db_manager.login_as_xufeng()
    print(f"   {login_result['message']}")
    
    # 获取数据库信息
    print("\n3. 获取数据库信息...")
    db_info = db_manager.get_database_info()
    print(f"   用户: {db_info['summary']['users']}, 角色: {db_info['summary']['roles']}")
    
    # 初始化会员级别
    print("\n4. 初始化会员级别...")
    levels_result = db_manager.init_member_levels()
    print(f"   {levels_result['message']}")
    
    # 获取会员级别
    print("\n5. 获取会员级别配置...")
    levels = db_manager.get_member_levels()
    for level in levels:
        print(f"   - {level['name']}: 分红股权{level['dividend_ratio']}%, 佣金比例{level['commission_ratio']}%")
    
    # 获取生态汇总
    print("\n6. 获取生态机制汇总...")
    summary = db_manager.get_ecosystem_summary()
    print(f"   合伙人: {summary['summary']['partners']['total']}")
    print(f"   项目: {summary['summary']['projects']['total']}")
    
    print("\n=== 测试完成 ===")
