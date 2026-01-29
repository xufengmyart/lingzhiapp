"""
灵值生态园 - 用户管理系统 (my_user)
基于合伙人模式的用户核心管理模块

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

from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# 导入模型
from src.auth.models_extended import (
    User, Role, Permission, UserMemberLevel, MemberLevel,
    MemberLevelHistory, Referral, ReferralCommission,
    EquityHolding, DividendDistribution, Project, ProjectParticipation,
    AuditLog, Session as UserSession
)

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


class UserStatus(Enum):
    """用户状态枚举"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    LOCKED = "locked"
    SUSPENDED = "suspended"


class MemberLevelType(Enum):
    """会员级别枚举"""
    TRIAL = "trial"          # 试用会员
    BASIC = "basic"          # 基础会员
    STANDARD = "standard"    # 标准会员
    ADVANCED = "advanced"    # 高级会员
    EXPERT = "expert"        # 专家会员（获得分红股权）


class TransactionType(Enum):
    """交易类型枚举"""
    TASK_REWARD = "task_reward"           # 任务奖励
    TRANSLATION_SERVICE = "translation_service"  # 转译服务
    TRANSLATION_REWARD = "translation_reward"    # 转译奖励
    PROJECT_PARTICIPATION = "project_participation"  # 项目参与
    PROJECT_REWARD = "project_reward"      # 项目奖励
    REFERRAL_COMMISSION = "referral_commission"  # 推荐佣金
    DIVIDEND = "dividend"                 # 分红
    EQUITY_GRANT = "equity_grant"         # 股权授予
    LEVEL_UPGRADE = "level_upgrade"       # 级别升级
    CONTRIBUTION_CONSUME = "contribution_consume"  # 贡献值消耗


class MyUser:
    """用户管理系统核心类"""
    
    def __init__(self, db_session: Optional[Session] = None):
        """
        初始化用户管理系统
        
        Args:
            db_session: 数据库会话，如果为None则创建新会话
        """
        self.session = db_session if db_session else SessionLocal()
    
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
    
    # ==================== 用户基础管理 ====================
    
    def create_user(
        self,
        name: str,
        email: str,
        password_hash: str,
        phone: Optional[str] = None,
        wechat: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        created_by: Optional[int] = None
    ) -> Optional[User]:
        """
        创建新用户
        
        Args:
            name: 用户姓名
            email: 邮箱
            password_hash: 密码哈希
            phone: 电话
            wechat: 微信号
            department: 部门
            position: 职位
            created_by: 创建人ID
        
        Returns:
            用户对象，创建失败返回None
        """
        try:
            # 检查邮箱是否已存在
            existing_user = self.session.query(User).filter(
                User.email == email
            ).first()
            
            if existing_user:
                print(f"邮箱 {email} 已存在")
                return None
            
            # 创建用户
            user = User(
                name=name,
                email=email,
                password_hash=password_hash,
                phone=phone,
                wechat=wechat,
                department=department,
                position=position,
                status=UserStatus.ACTIVE.value,
                created_by=created_by
            )
            
            self.session.add(user)
            self.session.flush()  # 获取用户ID
            
            # 为新用户初始化会员级别
            self._init_user_member_level(user.id)
            
            # 记录审计日志
            self._create_audit_log(
                user_id=user.id,
                action="create_user",
                resource_type="user",
                resource_id=user.id,
                description=f"创建用户: {name}"
            )
            
            self.commit()
            print(f"✅ 用户创建成功: {name} (ID: {user.id})")
            return user
            
        except IntegrityError as e:
            self.session.rollback()
            print(f"❌ 创建用户失败（ IntegrityError）: {str(e)}")
            return None
        except Exception as e:
            self.session.rollback()
            print(f"❌ 创建用户失败: {str(e)}")
            return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        获取用户信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户对象，不存在返回None
        """
        try:
            user = self.session.query(User).filter(User.id == user_id).first()
            return user
        except Exception as e:
            print(f"❌ 获取用户信息失败: {str(e)}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """
        通过邮箱获取用户
        
        Args:
            email: 邮箱
        
        Returns:
            用户对象，不存在返回None
        """
        try:
            user = self.session.query(User).filter(User.email == email).first()
            return user
        except Exception as e:
            print(f"❌ 获取用户信息失败: {str(e)}")
            return None
    
    def update_user(
        self,
        user_id: int,
        name: Optional[str] = None,
        phone: Optional[str] = None,
        wechat: Optional[str] = None,
        department: Optional[str] = None,
        position: Optional[str] = None,
        status: Optional[str] = None
    ) -> bool:
        """
        更新用户信息
        
        Args:
            user_id: 用户ID
            name: 姓名
            phone: 电话
            wechat: 微信号
            department: 部门
            position: 职位
            status: 状态
        
        Returns:
            是否更新成功
        """
        try:
            user = self.get_user(user_id)
            if not user:
                print(f"❌ 用户不存在: ID={user_id}")
                return False
            
            # 更新字段
            if name:
                user.name = name
            if phone:
                user.phone = phone
            if wechat:
                user.wechat = wechat
            if department:
                user.department = department
            if position:
                user.position = position
            if status:
                user.status = status
            
            user.updated_at = datetime.now()
            
            # 记录审计日志
            self._create_audit_log(
                user_id=user_id,
                action="update_user",
                resource_type="user",
                resource_id=user_id,
                description=f"更新用户信息"
            )
            
            self.commit()
            print(f"✅ 用户信息更新成功: {user.name} (ID: {user_id})")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 更新用户信息失败: {str(e)}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """
        删除用户（软删除，设置状态为inactive）
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否删除成功
        """
        try:
            user = self.get_user(user_id)
            if not user:
                print(f"❌ 用户不存在: ID={user_id}")
                return False
            
            user.status = UserStatus.INACTIVE.value
            user.updated_at = datetime.now()
            
            # 记录审计日志
            self._create_audit_log(
                user_id=user_id,
                action="delete_user",
                resource_type="user",
                resource_id=user_id,
                description=f"删除用户: {user.name}"
            )
            
            self.commit()
            print(f"✅ 用户删除成功: {user.name} (ID: {user_id})")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 删除用户失败: {str(e)}")
            return False
    
    def list_users(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[User]:
        """
        列出用户
        
        Args:
            status: 用户状态过滤
            limit: 返回数量限制
            offset: 偏移量
        
        Returns:
            用户列表
        """
        try:
            query = self.session.query(User)
            
            if status:
                query = query.filter(User.status == status)
            
            users = query.order_by(User.created_at.desc()).limit(limit).offset(offset).all()
            return users
            
        except Exception as e:
            print(f"❌ 列出用户失败: {str(e)}")
            return []
    
    # ==================== 贡献值管理 ====================
    
    def get_contribution_value(self, user_id: int) -> float:
        """
        获取用户贡献值
        
        Args:
            user_id: 用户ID
        
        Returns:
            贡献值数量
        """
        try:
            user_level = self.session.query(UserMemberLevel).filter(
                UserMemberLevel.user_id == user_id,
                UserMemberLevel.status == "active"
            ).first()
            
            if user_level:
                return user_level.contribution_value
            return 0.0
            
        except Exception as e:
            print(f"❌ 获取贡献值失败: {str(e)}")
            return 0.0
    
    def add_contribution(
        self,
        user_id: int,
        amount: float,
        transaction_type: TransactionType,
        description: Optional[str] = None
    ) -> bool:
        """
        增加用户贡献值
        
        Args:
            user_id: 用户ID
            amount: 增加数量
            transaction_type: 交易类型
            description: 描述
        
        Returns:
            是否成功
        """
        try:
            user_level = self.session.query(UserMemberLevel).filter(
                UserMemberLevel.user_id == user_id,
                UserMemberLevel.status == "active"
            ).first()
            
            if not user_level:
                print(f"❌ 用户会员级别不存在: ID={user_id}")
                return False
            
            old_value = user_level.contribution_value
            user_level.contribution_value += amount
            user_level.updated_at = datetime.now()
            
            # 记录审计日志
            self._create_audit_log(
                user_id=user_id,
                action="add_contribution",
                resource_type="contribution",
                resource_id=user_id,
                description=f"{description or transaction_type.value}: +{amount} 贡献值 ({old_value} -> {user_level.contribution_value})"
            )
            
            self.commit()
            print(f"✅ 贡献值增加成功: +{amount} (当前: {user_level.contribution_value})")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 增加贡献值失败: {str(e)}")
            return False
    
    def consume_contribution(
        self,
        user_id: int,
        amount: float,
        transaction_type: TransactionType,
        description: Optional[str] = None
    ) -> bool:
        """
        消耗用户贡献值
        
        Args:
            user_id: 用户ID
            amount: 消耗数量
            transaction_type: 交易类型
            description: 描述
        
        Returns:
            是否成功
        """
        try:
            user_level = self.session.query(UserMemberLevel).filter(
                UserMemberLevel.user_id == user_id,
                UserMemberLevel.status == "active"
            ).first()
            
            if not user_level:
                print(f"❌ 用户会员级别不存在: ID={user_id}")
                return False
            
            # 检查贡献值是否足够
            if user_level.contribution_value < amount:
                print(f"❌ 贡献值不足: 需要 {amount}, 当前 {user_level.contribution_value}")
                return False
            
            old_value = user_level.contribution_value
            user_level.contribution_value -= amount
            user_level.updated_at = datetime.now()
            
            # 记录审计日志
            self._create_audit_log(
                user_id=user_id,
                action="consume_contribution",
                resource_type="contribution",
                resource_id=user_id,
                description=f"{description or transaction_type.value}: -{amount} 贡献值 ({old_value} -> {user_level.contribution_value})"
            )
            
            self.commit()
            print(f"✅ 贡献值消耗成功: -{amount} (当前: {user_level.contribution_value})")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 消耗贡献值失败: {str(e)}")
            return False
    
    # ==================== 会员级别管理 ====================
    
    def _init_user_member_level(self, user_id: int) -> bool:
        """
        为新用户初始化会员级别
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否成功
        """
        try:
            # 获取试用会员级别
            trial_level = self.session.query(MemberLevel).filter(
                MemberLevel.level_type == MemberLevelType.TRIAL.value
            ).first()
            
            if not trial_level:
                print("❌ 试用会员级别不存在")
                return False
            
            # 创建用户会员级别记录
            user_level = UserMemberLevel(
                user_id=user_id,
                level_id=trial_level.id,
                contribution_value=0.0,
                team_member_count=0,
                total_earned=Decimal("0.0"),
                total_dividend_earned=Decimal("0.0"),
                equity_percentage=0.0,
                level_since=datetime.now(),
                status="active"
            )
            
            self.session.add(user_level)
            print(f"✅ 用户会员级别初始化成功: ID={user_id}, 级别=试用会员")
            return True
            
        except Exception as e:
            print(f"❌ 初始化用户会员级别失败: {str(e)}")
            return False
    
    def get_member_level(self, user_id: int) -> Optional[UserMemberLevel]:
        """
        获取用户会员级别信息
        
        Args:
            user_id: 用户ID
        
        Returns:
            会员级别对象
        """
        try:
            user_level = self.session.query(UserMemberLevel).filter(
                UserMemberLevel.user_id == user_id,
                UserMemberLevel.status == "active"
            ).first()
            
            return user_level
            
        except Exception as e:
            print(f"❌ 获取会员级别失败: {str(e)}")
            return None
    
    def upgrade_member_level(
        self,
        user_id: int,
        target_level_id: int,
        approved_by: int,
        reason: Optional[str] = None
    ) -> bool:
        """
        升级用户会员级别
        
        Args:
            user_id: 用户ID
            target_level_id: 目标级别ID
            approved_by: 审批人ID
            reason: 升级原因
        
        Returns:
            是否成功
        """
        try:
            user_level = self.get_member_level(user_id)
            if not user_level:
                print(f"❌ 用户会员级别不存在: ID={user_id}")
                return False
            
            old_level_id = user_level.level_id
            
            # 检查目标级别是否存在
            target_level = self.session.query(MemberLevel).filter(
                MemberLevel.id == target_level_id
            ).first()
            
            if not target_level:
                print(f"❌ 目标级别不存在: ID={target_level_id}")
                return False
            
            # 创建升级历史记录
            history = MemberLevelHistory(
                user_id=user_id,
                from_level_id=old_level_id,
                to_level_id=target_level_id,
                reason=reason,
                approved_by=approved_by,
                status="approved"
            )
            
            self.session.add(history)
            
            # 更新用户会员级别
            user_level.level_id = target_level_id
            user_level.level_since = datetime.now()
            user_level.updated_at = datetime.now()
            
            # 如果是专家级别，授予股权
            if target_level.level_type == MemberLevelType.EXPERT.value:
                user_level.equity_percentage = target_level.dividend_percentage
            
            # 记录审计日志
            self._create_audit_log(
                user_id=user_id,
                action="upgrade_level",
                resource_type="member_level",
                resource_id=user_id,
                description=f"会员级别升级: {old_level_id} -> {target_level_id}"
            )
            
            self.commit()
            print(f"✅ 会员级别升级成功: ID={user_id}, 新级别={target_level.level_name}")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 升级会员级别失败: {str(e)}")
            return False
    
    def check_level_upgrade_eligibility(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """
        检查用户是否符合升级条件
        
        Args:
            user_id: 用户ID
        
        Returns:
            (是否符合升级条件, 原因说明)
        """
        try:
            user_level = self.get_member_level(user_id)
            if not user_level:
                return False, "用户会员级别不存在"
            
            current_level = self.session.query(MemberLevel).filter(
                MemberLevel.id == user_level.level_id
            ).first()
            
            if not current_level:
                return False, "当前级别不存在"
            
            # 获取下一级别
            next_level = self.session.query(MemberLevel).filter(
                MemberLevel.level_type.in_([
                    MemberLevelType.BASIC.value,
                    MemberLevelType.STANDARD.value,
                    MemberLevelType.ADVANCED.value,
                    MemberLevelType.EXPERT.value
                ])
            ).order_by(MemberLevel.id).first()
            
            if not next_level:
                return False, "已经是最高级别"
            
            # 检查贡献值
            if user_level.contribution_value < next_level.min_contribution_value:
                return False, f"贡献值不足: 需要 {next_level.min_contribution_value}, 当前 {user_level.contribution_value}"
            
            # 检查团队成员数
            if user_level.team_member_count < next_level.min_team_members:
                return False, f"团队成员数不足: 需要 {next_level.min_team_members}, 当前 {user_level.team_member_count}"
            
            return True, "符合升级条件"
            
        except Exception as e:
            return False, f"检查升级条件失败: {str(e)}"
    
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
            project = self.session.query(Project).filter(Project.id == project_id).first()
            if not project:
                print(f"❌ 项目不存在: ID={project_id}")
                return False
            
            # 检查参与金额
            if project.min_participation_amount and participation_amount < project.min_participation_amount:
                print(f"❌ 参与金额不足: 最低 {project.min_participation_amount}")
                return False
            
            # 计算贡献值消耗（假设 1元 = 10贡献值）
            required_contribution = float(participation_amount) * 10
            
            # 消耗贡献值
            if not self.consume_contribution(
                user_id,
                required_contribution,
                TransactionType.PROJECT_PARTICIPATION,
                f"参与项目: {project.project_name}"
            ):
                return False
            
            # 计算占股比例
            share_percentage = float(participation_amount / project.total_investment) * 100 if project.total_investment else 0
            
            # 创建项目参与记录
            participation = ProjectParticipation(
                project_id=project_id,
                user_id=user_id,
                participant_id=participant_id,
                participation_amount=participation_amount,
                share_percentage=share_percentage,
                participation_date=datetime.now(),
                status="active"
            )
            
            self.session.add(participation)
            
            # 更新项目参与人数
            project.current_participants = (project.current_participants or 0) + 1
            project.updated_at = datetime.now()
            
            # 记录审计日志
            self._create_audit_log(
                user_id=user_id,
                action="participate_project",
                resource_type="project",
                resource_id=project_id,
                description=f"参与项目: {project.project_name}, 金额: {participation_amount}"
            )
            
            self.commit()
            print(f"✅ 项目参与成功: 项目={project.project_name}, 金额={participation_amount}")
            return True
            
        except Exception as e:
            self.session.rollback()
            print(f"❌ 参与项目失败: {str(e)}")
            return False
    
    # ==================== 私有辅助方法 ====================
    
    def _create_audit_log(
        self,
        user_id: int,
        action: str,
        resource_type: Optional[str] = None,
        resource_id: Optional[int] = None,
        description: Optional[str] = None,
        status: str = "success",
        error_message: Optional[str] = None
    ) -> None:
        """
        创建审计日志
        
        Args:
            user_id: 用户ID
            action: 操作类型
            resource_type: 资源类型
            resource_id: 资源ID
            description: 描述
            status: 状态
            error_message: 错误信息
        """
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                description=description,
                status=status,
                error_message=error_message
            )
            
            self.session.add(log)
        except Exception as e:
            print(f"创建审计日志失败: {str(e)}")


# ==================== 工厂函数 ====================

def get_user_manager() -> MyUser:
    """
    获取用户管理器实例
    
    Returns:
        MyUser 实例
    """
    return MyUser()


# ==================== 示例使用 ====================

if __name__ == "__main__":
    # 示例：创建用户
    with get_user_manager() as user_mgr:
        # 创建用户
        new_user = user_mgr.create_user(
            name="测试用户",
            email="test@example.com",
            password_hash="hashed_password_here",
            phone="13800138000",
            wechat="test_wechat"
        )
        
        if new_user:
            print(f"用户创建成功: {new_user.name}")
            
            # 获取贡献值
            contribution = user_mgr.get_contribution_value(new_user.id)
            print(f"当前贡献值: {contribution}")
            
            # 增加贡献值（新手任务奖励）
            user_mgr.add_contribution(
                new_user.id,
                100.0,
                TransactionType.TASK_REWARD,
                "新手任务奖励"
            )
            
            # 查看更新后的贡献值
            contribution = user_mgr.get_contribution_value(new_user.id)
            print(f"更新后贡献值: {contribution}")
