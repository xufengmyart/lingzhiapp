"""
权限管理系统的数据库模型
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table, Float, Numeric, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

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
    level = Column(Integer, default=4, comment='权限级别：1-最高，4-普通')
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

    @property
    def can_be_team_leader(self) -> bool:
        """检查是否可以成为团队长"""
        if self.is_team_leader:
            return True
        return self.willing_to_be_leader and len(self.team_members) >= 3


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

    # 关系
    team_leader = relationship('Visitor', foreign_keys=[team_leader_id], backref='team_members')
    member = relationship('Visitor', foreign_keys=[member_id])

    def __repr__(self):
        return f"<TeamMember(id={self.id}, leader_id={self.team_leader_id}, member_id={self.member_id})>"


# ==================== 生态机制相关表 ====================

class MemberLevel(enum.Enum):
    """会员级别"""
    ORDINARY = "ordinary"  # 普通会员
    SENIOR = "senior"  # 高级会员
    EXPERT = "expert"  # 专家会员（可获分红股权）
    VIP = "vip"  # VIP会员


class PartnerStatus(enum.Enum):
    """合伙人状态"""
    PENDING = "pending"  # 待审核
    ACTIVE = "active"  # 活跃
    SUSPENDED = "suspended"  # 暂停
    TERMINATED = "terminated"  # 终止


class ProjectStatus(enum.Enum):
    """项目状态"""
    DRAFT = "draft"  # 草稿
    ONGOING = "ongoing"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class ReferralStatus(enum.Enum):
    """推荐状态"""
    PENDING = "pending"  # 待确认
    CONFIRMED = "confirmed"  # 已确认
    PAID = "paid"  # 已支付
    CANCELLED = "cancelled"  # 已取消


class MemberLevelConfig(Base):
    """会员级别配置表"""
    __tablename__ = 'member_levels'

    id = Column(Integer, primary_key=True, index=True)
    level = Column(Enum(MemberLevel), unique=True, nullable=False, comment='会员级别')
    name = Column(String(50), nullable=False, comment='级别名称')
    description = Column(Text, comment='级别描述')
    min_revenue = Column(Float, default=0, comment='最低营收要求')
    min_referrals = Column(Integer, default=0, comment='最低推荐人数')
    dividend_ratio = Column(Float, default=0, comment='分红股权比例（%）')
    commission_ratio = Column(Float, default=0, comment='推荐佣金比例（%）')
    benefits = Column(Text, comment='权益描述')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    def __repr__(self):
        return f"<MemberLevelConfig(level={self.level}, name='{self.name}', dividend_ratio={self.dividend_ratio}%)>"


class Partner(Base):
    """合伙人表"""
    __tablename__ = 'partners'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    partner_code = Column(String(20), unique=True, nullable=False, index=True, comment='合伙人代码')
    member_level = Column(Enum(MemberLevel), default=MemberLevel.ORDINARY, comment='会员级别')
    status = Column(Enum(PartnerStatus), default=PartnerStatus.PENDING, comment='合伙人状态')
    dividend_equity = Column(Float, default=0, comment='分红股权（%）')
    total_revenue = Column(Float, default=0, comment='累计营收')
    total_commission = Column(Float, default=0, comment='累计佣金')
    total_referrals = Column(Integer, default=0, comment='累计推荐人数')
    bank_account = Column(String(100), comment='银行账户')
    bank_name = Column(String(100), comment='开户行')
    account_holder = Column(String(50), comment='持卡人姓名')
    notes = Column(Text, comment='备注')
    joined_at = Column(DateTime, default=datetime.now, comment='加入时间')
    level_up_at = Column(DateTime, comment='升级时间')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    user = relationship('User')
    projects = relationship('Project', back_populates='partner')
    referrals = relationship('Referral', foreign_keys='Referral.referrer_id', back_populates='referrer')
    received_referrals = relationship('Referral', foreign_keys='Referral.referee_id', back_populates='referee')
    commissions = relationship('Commission', back_populates='partner')
    dividends = relationship('Dividend', back_populates='partner')

    def __repr__(self):
        return f"<Partner(id={self.id}, code='{self.partner_code}', level={self.member_level})>"

    @property
    def can_get_dividend(self) -> bool:
        """是否可以分红"""
        return self.member_level == MemberLevel.EXPERT and self.dividend_equity > 0


class Project(Base):
    """项目表"""
    __tablename__ = 'projects'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment='项目名称')
    code = Column(String(50), unique=True, nullable=False, comment='项目代码')
    description = Column(Text, comment='项目描述')
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='负责人合伙人ID')
    status = Column(Enum(ProjectStatus), default=ProjectStatus.DRAFT, comment='项目状态')
    total_investment = Column(Float, default=0, comment='总投资金额')
    total_revenue = Column(Float, default=0, comment='总营收')
    profit = Column(Float, default=0, comment='利润')
    profit_ratio = Column(Float, default=0, comment='利润分配比例（%）')
    commission_ratio = Column(Float, default=0, comment='推荐佣金比例（%）')
    participant_count = Column(Integer, default=0, comment='参与人数')
    start_date = Column(DateTime, comment='开始日期')
    end_date = Column(DateTime, comment='结束日期')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    partner = relationship('Partner', back_populates='projects')
    participations = relationship('ProjectParticipation', back_populates='project')
    referrals = relationship('Referral', back_populates='project')

    def __repr__(self):
        return f"<Project(id={self.id}, code='{self.code}', name='{self.name}')>"


class ProjectParticipation(Base):
    """项目参与表"""
    __tablename__ = 'project_participations'

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False, comment='项目ID')
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='合伙人ID')
    investment = Column(Float, default=0, comment='投资金额')
    revenue = Column(Float, default=0, comment='营收金额')
    profit = Column(Float, default=0, comment='利润')
    status = Column(String(20), default='active', comment='状态：active/completed/cancelled')
    joined_at = Column(DateTime, default=datetime.now, comment='加入时间')
    completed_at = Column(DateTime, comment='完成时间')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    project = relationship('Project', back_populates='participations')
    partner = relationship('Partner')

    def __repr__(self):
        return f"<ProjectParticipation(id={self.id}, project_id={self.project_id}, partner_id={self.partner_id})>"


class Referral(Base):
    """推荐关系表"""
    __tablename__ = 'referrals'

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='推荐人ID')
    referee_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='被推荐人ID')
    project_id = Column(Integer, ForeignKey('projects.id'), comment='项目ID')
    opportunity_id = Column(String(100), comment='创业机会ID')
    opportunity_name = Column(String(200), comment='创业机会名称')
    amount = Column(Float, comment='购买金额')
    commission_ratio = Column(Float, default=0, comment='佣金比例（%）')
    commission_amount = Column(Float, default=0, comment='佣金金额')
    status = Column(Enum(ReferralStatus), default=ReferralStatus.PENDING, comment='推荐状态')
    source = Column(String(50), comment='来源：share/link/qrcode/other')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    confirmed_at = Column(DateTime, comment='确认时间')
    paid_at = Column(DateTime, comment='支付时间')

    # 关系
    referrer = relationship('Partner', foreign_keys=[referrer_id], back_populates='referrals')
    referee = relationship('Partner', foreign_keys=[referee_id], back_populates='received_referrals')
    project = relationship('Project', back_populates='referrals')

    def __repr__(self):
        return f"<Referral(id={self.id}, referrer_id={self.referrer_id}, referee_id={self.referee_id})>"


class Commission(Base):
    """推荐佣金表"""
    __tablename__ = 'commissions'

    id = Column(Integer, primary_key=True, index=True)
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='合伙人ID')
    referral_id = Column(Integer, ForeignKey('referrals.id'), comment='推荐记录ID')
    amount = Column(Float, nullable=False, comment='佣金金额')
    ratio = Column(Float, comment='佣金比例（%）')
    status = Column(String(20), default='pending', comment='状态：pending/paid/cancelled')
    source = Column(String(50), comment='来源：project/opportunity')
    period = Column(String(20), comment='周期：2024-01等')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    paid_at = Column(DateTime, comment='支付时间')

    # 关系
    partner = relationship('Partner', back_populates='commissions')
    referral = relationship('Referral')

    def __repr__(self):
        return f"<Commission(id={self.id}, partner_id={self.partner_id}, amount={self.amount})>"


class DividendPool(Base):
    """分红池表"""
    __tablename__ = 'dividend_pools'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, comment='分红池名称')
    period = Column(String(20), unique=True, nullable=False, comment='周期：2024-01等')
    total_commission = Column(Float, default=0, comment='总推荐佣金')
    pool_amount = Column(Float, default=0, comment='分红池金额（佣金的5%）')
    total_equity = Column(Float, default=0, comment='总股权（%）')
    distributed_amount = Column(Float, default=0, comment='已分配金额')
    remaining_amount = Column(Float, default=0, comment='剩余金额')
    status = Column(String(20), default='active', comment='状态：active/closed/cancelled')
    calculation_date = Column(DateTime, comment='计算日期')
    distribution_date = Column(DateTime, comment='分配日期')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    dividends = relationship('Dividend', back_populates='pool')

    def __repr__(self):
        return f"<DividendPool(id={self.id}, period='{self.period}', pool_amount={self.pool_amount})>"


class Dividend(Base):
    """分红记录表"""
    __tablename__ = 'dividends'

    id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(Integer, ForeignKey('dividend_pools.id'), nullable=False, comment='分红池ID')
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='合伙人ID')
    equity = Column(Float, default=0, comment='股权（%）')
    pool_amount = Column(Float, comment='分红池总金额')
    dividend_amount = Column(Float, nullable=False, comment='分红金额')
    status = Column(String(20), default='pending', comment='状态：pending/paid/cancelled')
    period = Column(String(20), comment='周期')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    paid_at = Column(DateTime, comment='支付时间')

    # 关系
    pool = relationship('DividendPool', back_populates='dividends')
    partner = relationship('Partner', back_populates='dividends')

    def __repr__(self):
        return f"<Dividend(id={self.id}, partner_id={self.partner_id}, amount={self.dividend_amount})>"
