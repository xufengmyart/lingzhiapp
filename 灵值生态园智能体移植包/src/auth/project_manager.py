"""
灵值生态园 - 项目参与和奖励管理系统
基于合伙人模式的项目参与与奖励机制

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
    User, Project, ProjectParticipation, ProjectProfitDistribution,
    UserMemberLevel, MemberLevel
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


class ProjectStatus(Enum):
    """项目状态枚举"""
    PLANNING = "planning"        # 规划中
    ONGOING = "ongoing"          # 进行中
    PAUSED = "paused"            # 暂停
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消


class ParticipationStatus(Enum):
    """参与状态枚举"""
    ACTIVE = "active"            # 活跃
    WITHDRAWN = "withdrawn"      # 已撤回
    COMPLETED = "completed"      # 已完成


class ProjectManager:
    """项目参与和奖励管理系统核心类"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化项目管理系统
        
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
    
    # ==================== 项目管理 ====================
    
    def create_project(
        self,
        project_name: str,
        project_code: str,
        description: str,
        project_type: str,
        total_investment: Decimal,
        profit_distribution_rate: float = 1.0,
        min_participation_amount: Optional[Decimal] = None,
        max_participants: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        created_by: Optional[int] = None
    ) -> Optional[Project]:
        """
        创建项目
        
        Args:
            project_name: 项目名称
            project_code: 项目代码
            description: 项目描述
            project_type: 项目类型
            total_investment: 总投资额
            profit_distribution_rate: 利润分配比例（0-1）
            min_participation_amount: 最低参与金额
            max_participants: 最大参与人数
            start_date: 开始日期
            end_date: 结束日期
            created_by: 创建人ID
        
        Returns:
            项目对象，创建失败返回None
        """
        try:
            # 检查项目代码是否已存在
            existing = self.session.query(Project).filter(
                Project.project_code == project_code
            ).first()
            
            if existing:
                print(f"❌ 项目代码已存在: {project_code}")
                return None
            
            # 创建项目
            project = Project(
                project_name=project_name,
                project_code=project_code,
                description=description,
                project_type=project_type,
                total_investment=total_investment,
                total_revenue=Decimal("0.0"),
                total_profit=Decimal("0.0"),
                profit_distribution_rate=profit_distribution_rate,
                min_participation_amount=min_participation_amount,
                max_participants=max_participants,
                start_date=start_date,
                end_date=end_date,
                status=ProjectStatus.PLANNING.value,
                current_participants=0,
                created_by=created_by
            )
            
            self.session.add(project)
            self.commit()
            
            print(f"✅ 项目创建成功: {project_name} (ID: {project.id})")
            return project
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 创建项目失败: {str(e)}")
            return None
    
    def get_project(self, project_id: int) -> Optional[Project]:
        """
        获取项目信息
        
        Args:
            project_id: 项目ID
        
        Returns:
            项目对象
        """
        try:
            project = self.session.query(Project).filter(Project.id == project_id).first()
            return project
        except Exception as e:
            print(f"❌ 获取项目信息失败: {str(e)}")
            return None
    
    def list_projects(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Project]:
        """
        列出项目
        
        Args:
            status: 项目状态过滤
            limit: 返回数量限制
            offset: 偏移量
        
        Returns:
            项目列表
        """
        try:
            query = self.session.query(Project)
            
            if status:
                query = query.filter(Project.status == status)
            
            projects = query.order_by(Project.created_at.desc()).limit(limit).offset(offset).all()
            return projects
            
        except Exception as e:
            print(f"❌ 列出项目失败: {str(e)}")
            return []
    
    def update_project_status(
        self,
        project_id: int,
        status: str,
        total_revenue: Optional[Decimal] = None,
        total_profit: Optional[Decimal] = None
    ) -> bool:
        """
        更新项目状态
        
        Args:
            project_id: 项目ID
            status: 新状态
            total_revenue: 总收入
            total_profit: 总利润
        
        Returns:
            是否更新成功
        """
        try:
            project = self.get_project(project_id)
            if not project:
                print(f"❌ 项目不存在: ID={project_id}")
                return False
            
            project.status = status
            project.updated_at = datetime.now()
            
            if total_revenue is not None:
                project.total_revenue = total_revenue
            
            if total_profit is not None:
                project.total_profit = total_profit
            
            # 如果项目完成，触发利润分配
            if status == ProjectStatus.COMPLETED.value and total_profit:
                self.distribute_project_profit(project_id)
            
            self.commit()
            print(f"✅ 项目状态更新成功: {project.project_name} -> {status}")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 更新项目状态失败: {str(e)}")
            return False
    
    # ==================== 项目参与管理 ====================
    
    def participate_project(
        self,
        user_id: int,
        project_id: int,
        participation_amount: Decimal,
        participant_id: Optional[str] = None
    ) -> bool:
        """
        参与项目
        
        Args:
            user_id: 用户ID
            project_id: 项目ID
            participation_amount: 参与金额
            participant_id: 参与者编号
        
        Returns:
            是否成功
        """
        try:
            # 检查项目是否存在
            project = self.get_project(project_id)
            if not project:
                print(f"❌ 项目不存在: ID={project_id}")
                return False
            
            # 检查项目状态
            if project.status not in [ProjectStatus.PLANNING.value, ProjectStatus.ONGOING.value]:
                print(f"❌ 项目状态不允许参与: {project.status}")
                return False
            
            # 检查参与金额
            if project.min_participation_amount and participation_amount < project.min_participation_amount:
                print(f"❌ 参与金额不足: 最低 {project.min_participation_amount}")
                return False
            
            # 检查是否已参与
            existing = self.session.query(ProjectParticipation).filter(
                and_(
                    ProjectParticipation.project_id == project_id,
                    ProjectParticipation.user_id == user_id,
                    ProjectParticipation.status == ParticipationStatus.ACTIVE.value
                )
            ).first()
            
            if existing:
                print(f"❌ 用户已参与此项目")
                return False
            
            # 计算贡献值消耗（假设 1元 = 10贡献值）
            required_contribution = float(participation_amount) * 10
            
            # 消耗贡献值
            if not self.user_mgr.consume_contribution(
                user_id,
                required_contribution,
                TransactionType.PROJECT_PARTICIPATION,
                f"参与项目: {project.project_name}"
            ):
                return False
            
            # 计算占股比例
            share_percentage = float(participation_amount / project.total_investment) * 100 if project.total_investment > 0 else 0
            
            # 创建项目参与记录
            participation = ProjectParticipation(
                project_id=project_id,
                user_id=user_id,
                participant_id=participant_id,
                participation_amount=participation_amount,
                share_percentage=share_percentage,
                participation_date=datetime.now(),
                status=ParticipationStatus.ACTIVE.value
            )
            
            self.session.add(participation)
            
            # 更新项目参与人数
            project.current_participants = (project.current_participants or 0) + 1
            project.updated_at = datetime.now()
            
            # 记录审计日志
            from src.auth.my_user import AuditLog
            log = AuditLog(
                user_id=user_id,
                action="participate_project",
                resource_type="project",
                resource_id=project_id,
                description=f"参与项目: {project.project_name}, 金额: {participation_amount}, 占股: {share_percentage:.2f}%"
            )
            self.session.add(log)
            
            self.commit()
            print(f"✅ 项目参与成功: 项目={project.project_name}, 金额={participation_amount}, 占股={share_percentage:.2f}%")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 参与项目失败: {str(e)}")
            return False
    
    def get_user_participations(self, user_id: int) -> List[ProjectParticipation]:
        """
        获取用户的项目参与记录
        
        Args:
            user_id: 用户ID
        
        Returns:
            参与记录列表
        """
        try:
            participations = self.session.query(ProjectParticipation).filter(
                ProjectParticipation.user_id == user_id
            ).order_by(ProjectParticipation.participation_date.desc()).all()
            
            return participations
            
        except Exception as e:
            print(f"❌ 获取项目参与记录失败: {str(e)}")
            return []
    
    def get_project_participants(self, project_id: int) -> List[ProjectParticipation]:
        """
        获取项目的参与者列表
        
        Args:
            project_id: 项目ID
        
        Returns:
            参与者列表
        """
        try:
            participants = self.session.query(ProjectParticipation).filter(
                ProjectParticipation.project_id == project_id,
                ProjectParticipation.status == ParticipationStatus.ACTIVE.value
            ).order_by(ProjectParticipation.participation_amount.desc()).all()
            
            return participants
            
        except Exception as e:
            print(f"❌ 获取项目参与者失败: {str(e)}")
            return []
    
    # ==================== 利润分配管理 ====================
    
    def distribute_project_profit(self, project_id: int) -> bool:
        """
        分配项目利润
        
        Args:
            project_id: 项目ID
        
        Returns:
            是否分配成功
        """
        try:
            project = self.get_project(project_id)
            if not project:
                print(f"❌ 项目不存在: ID={project_id}")
                return False
            
            if project.total_profit <= 0:
                print(f"❌ 项目无利润可分配")
                return False
            
            # 获取所有活跃参与者
            participations = self.get_project_participants(project_id)
            
            if not participations:
                print(f"❌ 项目无参与者")
                return False
            
            # 计算分配总额
            distribution_total = project.total_profit * Decimal(str(project.profit_distribution_rate))
            
            # 分配利润给每个参与者
            for participation in participations:
                # 计算应得利润
                share_ratio = participation.share_percentage / 100
                profit_share = distribution_total * Decimal(str(share_ratio))
                
                # 更新参与记录
                participation.profit_share = profit_share
                
                # 创建利润分配记录
                distribution = ProjectProfitDistribution(
                    project_id=project_id,
                    participation_id=participation.id,
                    profit_amount=profit_share,
                    distribution_date=datetime.now()
                )
                
                self.session.add(distribution)
                
                # 奖励贡献值（假设 1元 = 10贡献值）
                contribution_reward = float(profit_share) * 10
                
                if not self.user_mgr.add_contribution(
                    participation.user_id,
                    contribution_reward,
                    TransactionType.PROJECT_REWARD,
                    f"项目利润分配: {project.project_name}"
                ):
                    print(f"⚠️  贡献值奖励失败: 用户ID={participation.user_id}")
            
            # 记录审计日志
            from src.auth.my_user import AuditLog
            log = AuditLog(
                user_id=0,  # 系统操作
                action="distribute_profit",
                resource_type="project",
                resource_id=project_id,
                description=f"项目利润分配: {project.project_name}, 总额: {distribution_total}, 参与者: {len(participations)}人"
            )
            self.session.add(log)
            
            self.commit()
            print(f"✅ 项目利润分配成功: {project.project_name}, {len(participations)}人, 总额: {distribution_total}")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 分配项目利润失败: {str(e)}")
            return False
    
    def get_project_profit_distribution(self, project_id: int) -> List[ProjectProfitDistribution]:
        """
        获取项目的利润分配记录
        
        Args:
            project_id: 项目ID
        
        Returns:
            利润分配记录列表
        """
        try:
            distributions = self.session.query(ProjectProfitDistribution).filter(
                ProjectProfitDistribution.project_id == project_id
            ).order_by(ProjectProfitDistribution.distribution_date.desc()).all()
            
            return distributions
            
        except Exception as e:
            print(f"❌ 获取利润分配记录失败: {str(e)}")
            return []
    
    # ==================== 项目统计 ====================
    
    def get_project_stats(self, project_id: int) -> Dict:
        """
        获取项目统计数据
        
        Args:
            project_id: 项目ID
        
        Returns:
            统计数据字典
        """
        try:
            project = self.get_project(project_id)
            if not project:
                return {}
            
            participants = self.get_project_participants(project_id)
            distributions = self.get_project_profit_distribution(project_id)
            
            # 计算总参与金额
            total_participation = sum(
                p.participation_amount for p in participants
            )
            
            # 计算已分配利润
            total_distributed = sum(
                d.profit_amount for d in distributions
            )
            
            stats = {
                "project_name": project.project_name,
                "total_investment": float(project.total_investment),
                "total_revenue": float(project.total_revenue),
                "total_profit": float(project.total_profit),
                "current_participants": project.current_participants or 0,
                "total_participation": float(total_participation),
                "profit_distribution_rate": project.profit_distribution_rate,
                "total_distributed_profit": float(total_distributed),
                "progress_rate": float(total_participation / project.total_investment) if project.total_investment > 0 else 0
            }
            
            return stats
            
        except Exception as e:
            print(f"❌ 获取项目统计失败: {str(e)}")
            return {}


# ==================== 工厂函数 ====================

def get_project_manager() -> ProjectManager:
    """
    获取项目管理器实例
    
    Returns:
        ProjectManager 实例
    """
    return ProjectManager()


# ==================== 示例使用 ====================

if __name__ == "__main__":
    # 示例：创建项目和参与
    with get_project_manager() as proj_mgr:
        # 创建项目
        project = proj_mgr.create_project(
            project_name="唐风茶馆品牌IP项目",
            project_code="TFCT001",
            description="将唐代茶文化转化为现代茶馆品牌IP",
            project_type="cultural",
            total_investment=Decimal("1000000"),  # 100万元
            profit_distribution_rate=0.8,  # 80%利润分配
            min_participation_amount=Decimal("1000"),  # 最低参与1000元
            max_participants=100
        )
        
        if project:
            # 用户参与项目
            success = proj_mgr.participate_project(
                user_id=1,
                project_id=project.id,
                participation_amount=Decimal("5000")  # 参与5000元
            )
            
            if success:
                # 获取项目统计
                stats = proj_mgr.get_project_stats(project.id)
                print(f"项目统计: {stats}")
