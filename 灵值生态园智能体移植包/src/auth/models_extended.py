"""
权限管理系统的数据库模型 - 扩展版（包含合伙制及项目制生态机制）
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table, Float, DECIMAL, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


# ============================================
# 原有基础表
# ============================================

# 用户-角色关联表（多对多）
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# 角色-权限关联表（多对多）
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


class User(Base):
    """用户表"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment='用户姓名')
    email = Column(String(100), unique=True, nullable=False, index=True, comment='邮箱')
    phone = Column(String(20), comment='电话')
    wechat = Column(String(50), comment='微信号')
    password_hash = Column(String(255), nullable=False, comment='密码哈希')
    department = Column(String(50), comment='部门')
    position = Column(String(50), comment='职位')
    status = Column(String(20), default='active', comment='状态：active/inactive/locked')
    is_superuser = Column(Boolean, default=False, comment='是否超级管理员')
    is_ceo = Column(Boolean, default=False, comment='是否CEO')
    two_factor_enabled = Column(Boolean, default=False, comment='是否启用双因素认证')
    two_factor_secret = Column(String(255), comment='双因素认证密钥')
    last_login = Column(DateTime, comment='最后登录时间')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(Integer, ForeignKey('users.id'), comment='创建人ID')

    # 关系
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    created_user = relationship('User', remote_side=[id])
    audit_logs = relationship('AuditLog', back_populates='user')

    def __repr__(self):
        return f"<User(id={self.id}, name='{self.name}', email='{self.email}')>"

    def has_permission(self, permission_code: str) -> bool:
        """检查用户是否有指定权限"""
        if self.is_superuser:
            return True
        for role in self.roles:
            for permission in role.permissions:
                if permission.code == permission_code:
                    return True
        return False

    def get_all_permissions(self) -> list:
        """获取用户的所有权限"""
        if self.is_superuser:
            return ['all']
        permissions = set()
        for role in self.roles:
            for permission in role.permissions:
                permissions.add(permission.code)
        return list(permissions)


class Role(Base):
    """角色表"""
    __tablename__ = 'roles'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False, comment='角色名称')
    name_en = Column(String(50), comment='英文名称')
    level = Column(Integer, default=4, comment='权限级别：0-CEO，1-超级，2-高级，3-部门，4-普通')
    description = Column(Text, comment='角色描述')
    status = Column(String(20), default='active', comment='状态')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(Integer, ForeignKey('users.id'), comment='创建人ID')

    # 关系
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', level={self.level})>"


class Permission(Base):
    """权限表"""
    __tablename__ = 'permissions'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True, comment='权限代码')
    name = Column(String(100), nullable=False, comment='权限名称')
    module = Column(String(50), comment='所属模块')
    description = Column(Text, comment='权限描述')
    status = Column(String(20), default='active', comment='状态')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')

    def __repr__(self):
        return f"<Permission(id={self.id}, code='{self.code}', name='{self.name}')>"


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    action = Column(String(50), nullable=False, comment='操作类型')
    resource_type = Column(String(50), comment='资源类型')
    resource_id = Column(Integer, comment='资源ID')
    description = Column(Text, comment='操作描述')
    ip_address = Column(String(50), comment='IP地址')
    user_agent = Column(String(255), comment='用户代理')
    status = Column(String(20), default='success', comment='状态：success/failed')
    error_message = Column(Text, comment='错误信息')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关系
    user = relationship('User', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"


class Session(Base):
    """会话表"""
    __tablename__ = 'sessions'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    token = Column(String(255), unique=True, nullable=False, index=True, comment='会话令牌')
    ip_address = Column(String(50), comment='IP地址')
    user_agent = Column(String(255), comment='用户代理')
    is_active = Column(Boolean, default=True, comment='是否活跃')
    last_activity = Column(DateTime, default=datetime.now, comment='最后活动时间')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    expires_at = Column(DateTime, comment='过期时间')

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id})>"


# ============================================
# 访客管理表
# ============================================

class Visitor(Base):
    """访客表"""
    __tablename__ = 'visitors'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment='姓名')
    wechat = Column(String(50), nullable=False, comment='微信号')
    phone = Column(String(20), nullable=False, comment='联系方式')
    referrer = Column(String(50), comment='推荐人')
    notes = Column(Text, comment='备注')
    shipping_address = Column(Text, comment='收货地址')
    is_team_leader = Column(Boolean, default=False, comment='是否为团队长')
    willing_to_be_leader = Column(Boolean, comment='是否愿意成为团队长')
    status = Column(String(20), default='pending', comment='状态：pending/active/inactive')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(Integer, ForeignKey('users.id'), comment='创建人ID')

    # 关系
    created_user = relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f"<Visitor(id={self.id}, name='{self.name}', wechat='{self.wechat}')>"


class TeamMember(Base):
    """团队成员表"""
    __tablename__ = 'team_members'

    id = Column(Integer, primary_key=True, index=True)
    team_leader_id = Column(Integer, ForeignKey('visitors.id'), nullable=False, comment='团队长ID')
    member_id = Column(Integer, ForeignKey('visitors.id'), nullable=False, comment='成员ID')
    role = Column(String(50), comment='角色')
    joined_at = Column(DateTime, default=datetime.now, comment='加入时间')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    def __repr__(self):
        return f"<TeamMember(id={self.id}, leader_id={self.team_leader_id}, member_id={self.member_id})>"


# ============================================
# 新增：会员级别系统
# ============================================

class MemberLevelType(enum.Enum):
    """会员级别枚举"""
    TRIAL = "trial"          # 试用会员
    BASIC = "basic"          # 基础会员
    STANDARD = "standard"    # 标准会员
    ADVANCED = "advanced"    # 高级会员
    EXPERT = "expert"        # 专家会员（达到此级别可获得分红股权）


class MemberLevel(Base):
    """会员级别定义表"""
    __tablename__ = 'member_levels'

    id = Column(Integer, primary_key=True, index=True)
    level_code = Column(String(50), unique=True, nullable=False, comment='级别代码')
    level_name = Column(String(50), nullable=False, comment='级别名称')
    level_type = Column(String(20), nullable=False, comment='级别类型：trial/basic/standard/advanced/expert')
    min_contribution_value = Column(Float, default=0.0, comment='最低贡献值要求')
    min_team_members = Column(Integer, default=0, comment='最低团队成员数要求')
    referral_commission_rate = Column(Float, default=0.0, comment='推荐佣金比例（0-1）')
    dividend_percentage = Column(Float, default=0.0, comment='分红股权百分比（专家级别为0.1%）')
    benefits = Column(Text, comment='会员权益描述')
    status = Column(String(20), default='active', comment='状态')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(Integer, ForeignKey('users.id'), comment='创建人ID')

    # 关系
    created_user = relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f"<MemberLevel(id={self.id}, level_name='{self.level_name}')>"


class UserMemberLevel(Base):
    """用户会员级别表"""
    __tablename__ = 'user_member_levels'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    level_id = Column(Integer, ForeignKey('member_levels.id'), nullable=False, comment='当前级别ID')
    contribution_value = Column(Float, default=0.0, comment='累计贡献值')
    team_member_count = Column(Integer, default=0, comment='团队成员数量')
    total_earned = Column(DECIMAL(20, 2), default=0.0, comment='累计收益（元）')
    total_dividend_earned = Column(DECIMAL(20, 2), default=0.0, comment='累计分红收益（元）')
    equity_percentage = Column(Float, default=0.0, comment='当前持有的股权百分比')
    level_since = Column(DateTime, default=datetime.now, comment='当前级别开始时间')
    status = Column(String(20), default='active', comment='状态：active/suspended/terminated')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    user = relationship('User', foreign_keys=[user_id])
    level = relationship('MemberLevel', foreign_keys=[level_id])

    def __repr__(self):
        return f"<UserMemberLevel(id={self.id}, user_id={self.user_id}, contribution={self.contribution_value})>"


class MemberLevelHistory(Base):
    """会员级别升级历史表"""
    __tablename__ = 'member_level_history'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    from_level_id = Column(Integer, ForeignKey('member_levels.id'), comment='原级别ID')
    to_level_id = Column(Integer, ForeignKey('member_levels.id'), nullable=False, comment='新级别ID')
    reason = Column(Text, comment='升级原因')
    approved_by = Column(Integer, ForeignKey('users.id'), comment='审批人ID')
    status = Column(String(20), default='approved', comment='状态：pending/approved/rejected')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关系
    user = relationship('User', foreign_keys=[user_id])
    from_level = relationship('MemberLevel', foreign_keys=[from_level_id])
    to_level = relationship('MemberLevel', foreign_keys=[to_level_id])
    approver = relationship('User', foreign_keys=[approved_by])

    def __repr__(self):
        return f"<MemberLevelHistory(id={self.id}, user_id={self.user_id})>"


# ============================================
# 新增：项目管理系统
# ============================================

class ProjectStatus(enum.Enum):
    """项目状态枚举"""
    PLANNING = "planning"        # 规划中
    ONGOING = "ongoing"          # 进行中
    PAUSED = "paused"            # 暂停
    COMPLETED = "completed"      # 已完成
    CANCELLED = "cancelled"      # 已取消


class Project(Base):
    """项目表"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    project_name = Column(String(100), nullable=False, comment='项目名称')
    project_code = Column(String(50), unique=True, nullable=False, comment='项目代码')
    description = Column(Text, comment='项目描述')
    project_type = Column(String(50), comment='项目类型：cultural/media/technology/etc.')
    total_investment = Column(DECIMAL(20, 2), default=0.0, comment='总投资额（元）')
    total_revenue = Column(DECIMAL(20, 2), default=0.0, comment='总收入（元）')
    total_profit = Column(DECIMAL(20, 2), default=0.0, comment='总利润（元）')
    profit_distribution_rate = Column(Float, default=1.0, comment='利润分配比例（0-1）')
    min_participation_amount = Column(DECIMAL(10, 2), comment='最低参与金额（元）')
    max_participants = Column(Integer, comment='最大参与人数')
    current_participants = Column(Integer, default=0, comment='当前参与人数')
    start_date = Column(DateTime, comment='项目开始日期')
    end_date = Column(DateTime, comment='项目结束日期')
    status = Column(String(20), default='planning', comment='状态：planning/ongoing/paused/completed/cancelled')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(Integer, ForeignKey('users.id'), comment='创建人ID')

    # 关系
    created_user = relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f"<Project(id={self.id}, name='{self.project_name}', status='{self.status}')>"


class ProjectParticipation(Base):
    """项目参与表"""
    __tablename__ = 'project_participations'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, index=True, comment='项目ID')
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='参与用户ID')
    participant_id = Column(String(50), comment='参与者编号')
    participation_amount = Column(DECIMAL(10, 2), nullable=False, comment='参与金额（元）')
    share_percentage = Column(Float, comment='占股比例')
    profit_share = Column(DECIMAL(20, 2), default=0.0, comment='应得利润份额（元）')
    profit_paid = Column(DECIMAL(20, 2), default=0.0, comment='已支付利润（元）')
    participation_date = Column(DateTime, default=datetime.now, comment='参与日期')
    status = Column(String(20), default='active', comment='状态：active/withdrawn/completed')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    project = relationship('Project', foreign_keys=[project_id])
    user = relationship('User', foreign_keys=[user_id])

    def __repr__(self):
        return f"<ProjectParticipation(id={self.id}, project_id={self.project_id}, user_id={self.user_id})>"


class ProjectProfitDistribution(Base):
    """项目利润分配表"""
    __tablename__ = 'project_profit_distributions'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, comment='项目ID')
    participation_id = Column(Integer, ForeignKey('project_participations.id'), nullable=False, comment='参与记录ID')
    distribution_round = Column(Integer, comment='分配轮次')
    profit_amount = Column(DECIMAL(20, 2), nullable=False, comment='分配利润金额（元）')
    distribution_date = Column(DateTime, default=datetime.now, comment='分配日期')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关系
    project = relationship('Project', foreign_keys=[project_id])
    participation = relationship('ProjectParticipation', foreign_keys=[participation_id])

    def __repr__(self):
        return f"<ProjectProfitDistribution(id={self.id}, profit={self.profit_amount})>"


# ============================================
# 新增：推荐佣金系统
# ============================================

class Referral(Base):
    """推荐关系表"""
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='推荐人ID')
    referee_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='被推荐人ID')
    referral_code = Column(String(50), unique=True, nullable=False, comment='推荐码')
    project_id = Column(Integer, ForeignKey('projects.id'), comment='关联项目ID')
    relationship_type = Column(String(20), default='direct', comment='关系类型：direct/indirect')
    status = Column(String(20), default='active', comment='状态：active/inactive/cancelled')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关系
    referrer = relationship('User', foreign_keys=[referrer_id])
    referee = relationship('User', foreign_keys=[referee_id])
    project = relationship('Project', foreign_keys=[project_id])

    def __repr__(self):
        return f"<Referral(id={self.id}, referrer_id={self.referrer_id}, referee_id={self.referee_id})>"


class ReferralCommission(Base):
    """推荐佣金表"""
    __tablename__ = 'referral_commissions'

    id = Column(Integer, primary_key=True, index=True)
    referral_id = Column(Integer, ForeignKey('referrals.id'), nullable=False, comment='推荐关系ID')
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, comment='项目ID')
    referrer_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='推荐人ID')
    transaction_amount = Column(DECIMAL(20, 2), nullable=False, comment='交易金额（元）')
    commission_rate = Column(Float, nullable=False, comment='佣金比例（0-1）')
    commission_amount = Column(DECIMAL(20, 2), nullable=False, comment='佣金金额（元）')
    dividend_pool_contribution = Column(DECIMAL(20, 2), default=0.0, comment='贡献给分红池的金额（5%）')
    status = Column(String(20), default='pending', comment='状态：pending/paid/cancelled')
    paid_at = Column(DateTime, comment='支付时间')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关系
    referral = relationship('Referral', foreign_keys=[referral_id])
    project = relationship('Project', foreign_keys=[project_id])
    referrer = relationship('User', foreign_keys=[referrer_id])

    def __repr__(self):
        return f"<ReferralCommission(id={self.id}, amount={self.commission_amount})>"


# ============================================
# 新增：分红股权系统
# ============================================

class DividendPool(Base):
    """分红池表"""
    __tablename__ = 'dividend_pools'

    id = Column(Integer, primary_key=True, index=True)
    pool_name = Column(String(100), nullable=False, comment='分红池名称')
    pool_type = Column(String(50), default='expert', comment='分红池类型：expert/general')
    total_pool_amount = Column(DECIMAL(20, 2), default=0.0, comment='分红池总金额（元）')
    available_amount = Column(DECIMAL(20, 2), default=0.0, comment='可用金额（元）')
    distributed_amount = Column(DECIMAL(20, 2), default=0.0, comment='已分配金额（元）')
    last_dividend_date = Column(DateTime, comment='上次分红日期')
    status = Column(String(20), default='active', comment='状态：active/suspended/closed')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<DividendPool(id={self.id}, name='{self.pool_name}', total={self.total_pool_amount})>"


class EquityHolding(Base):
    """股权持有表"""
    __tablename__ = 'equity_holdings'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    pool_id = Column(Integer, ForeignKey('dividend_pools.id'), nullable=False, comment='分红池ID')
    equity_percentage = Column(Float, nullable=False, comment='股权百分比（0-100）')
    granted_date = Column(DateTime, default=datetime.now, comment='授予日期')
    expires_date = Column(DateTime, comment='过期日期')
    status = Column(String(20), default='active', comment='状态：active/suspended/terminated')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    user = relationship('User', foreign_keys=[user_id])
    pool = relationship('DividendPool', foreign_keys=[pool_id])

    def __repr__(self):
        return f"<EquityHolding(id={self.id}, user_id={self.user_id}, equity={self.equity_percentage}%)>"


class DividendDistribution(Base):
    """分红分配表"""
    __tablename__ = 'dividend_distributions'

    id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(Integer, ForeignKey('dividend_pools.id'), nullable=False, comment='分红池ID')
    equity_holding_id = Column(Integer, ForeignKey('equity_holdings.id'), nullable=False, comment='股权持有ID')
    distribution_round = Column(Integer, comment='分配轮次')
    total_pool_amount = Column(DECIMAL(20, 2), comment='分红池总额（元）')
    user_equity_percentage = Column(Float, comment='用户股权百分比')
    dividend_amount = Column(DECIMAL(20, 2), nullable=False, comment='分红金额（元）')
    status = Column(String(20), default='pending', comment='状态：pending/paid/cancelled')
    paid_at = Column(DateTime, comment='支付时间')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')

    # 关系
    pool = relationship('DividendPool', foreign_keys=[pool_id])
    equity_holding = relationship('EquityHolding', foreign_keys=[equity_holding_id])

    def __repr__(self):
        return f"<DividendDistribution(id={self.id}, amount={self.dividend_amount})>"


# ============================================
# 新增：投资管理
# ============================================

class Investment(Base):
    """投资记录表"""
    __tablename__ = 'investments'

    id = Column(Integer, primary_key=True, index=True)
    investment_name = Column(String(100), nullable=False, comment='投资名称')
    investment_type = Column(String(50), comment='投资类型：infrastructure/marketing/research/operation/etc.')
    project_id = Column(Integer, ForeignKey('projects.id'), comment='关联项目ID')
    amount = Column(DECIMAL(20, 2), nullable=False, comment='投资金额（元）')
    description = Column(Text, comment='投资描述')
    expected_return = Column(Float, comment='预期回报率')
    actual_return = Column(Float, comment='实际回报率')
    investment_date = Column(DateTime, comment='投资日期')
    maturity_date = Column(DateTime, comment='到期日期')
    status = Column(String(20), default='active', comment='状态：planning/active/completed/cancelled')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    created_by = Column(Integer, ForeignKey('users.id'), comment='创建人ID')

    # 关系
    project = relationship('Project', foreign_keys=[project_id])
    created_user = relationship('User', foreign_keys=[created_by])

    def __repr__(self):
        return f"<Investment(id={self.id}, name='{self.investment_name}', amount={self.amount})>"
