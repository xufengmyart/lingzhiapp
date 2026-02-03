from coze_coding_dev_sdk.database import Base

from sqlalchemy import Boolean, Column, DateTime, ForeignKeyConstraint, Index, Integer, Numeric, PrimaryKeyConstraint, String, Table, Text, UniqueConstraint, text, JSON, Float
from typing import Optional
import datetime
import decimal

from sqlalchemy.orm import Mapped, mapped_column, relationship

class CompanyInfo(Base):
    __tablename__ = 'company_info'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='company_info_pkey'),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String(200), nullable=False)
    tax_number: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(500))
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    bank_name: Mapped[Optional[str]] = mapped_column(String(200))
    bank_account: Mapped[Optional[str]] = mapped_column(String(50))
    status: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'active'::character varying"))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)


class Permissions(Base):
    __tablename__ = 'permissions'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='permissions_pkey'),
        Index('ix_permissions_code', 'code', unique=True),
        Index('ix_permissions_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='权限ID')
    code: Mapped[str] = mapped_column(String(100), nullable=False, comment='权限代码')
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment='权限名称')
    status: Mapped[str] = mapped_column(String(20), nullable=False, comment='状态')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='创建时间')
    module: Mapped[Optional[str]] = mapped_column(String(50), comment='所属模块')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='权限描述')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')

    role: Mapped[list['Roles']] = relationship('Roles', secondary='role_permissions', back_populates='permission')


class Users(Base):
    __tablename__ = 'users'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='users_created_by_fkey'),
        PrimaryKeyConstraint('id', name='users_pkey'),
        Index('ix_users_coze_id', 'coze_id', unique=True),
        Index('ix_users_email', 'email', unique=True),
        Index('ix_users_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='用户ID')
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment='用户姓名')
    email: Mapped[str] = mapped_column(String(100), nullable=False, comment='邮箱')
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment='密码哈希')
    status: Mapped[str] = mapped_column(String(20), nullable=False, comment='状态：active/inactive/locked')
    is_superuser: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否超级管理员')
    is_ceo: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否CEO')
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否启用双因素认证')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='创建时间')
    is_registered: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default=text('false'), comment='是否完成信息登记')
    phone: Mapped[Optional[str]] = mapped_column(String(20), comment='电话')
    wechat: Mapped[Optional[str]] = mapped_column(String(50), comment='微信号')
    department: Mapped[Optional[str]] = mapped_column(String(50), comment='部门')
    position: Mapped[Optional[str]] = mapped_column(String(50), comment='职位')
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String(255), comment='双因素认证密钥')
    ip_whitelist: Mapped[Optional[str]] = mapped_column(Text, comment='IP白名单（JSON数组）')
    last_login: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='最后登录时间')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')
    created_by: Mapped[Optional[int]] = mapped_column(Integer, comment='创建人ID')
    coze_id: Mapped[Optional[str]] = mapped_column(String(50), comment='扣子平台注册ID')
    real_name: Mapped[Optional[str]] = mapped_column(String(50), comment='真实姓名')
    registration_time: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='登记时间')
    id_card: Mapped[Optional[str]] = mapped_column(String(18), comment='身份证号码')
    wechat_account: Mapped[Optional[str]] = mapped_column(String(50))
    wechat_qrcode: Mapped[Optional[str]] = mapped_column(String(500))
    alipay_account: Mapped[Optional[str]] = mapped_column(String(100))
    alipay_qrcode: Mapped[Optional[str]] = mapped_column(String(500))
    bank_card_number: Mapped[Optional[str]] = mapped_column(String(20))
    bank_name: Mapped[Optional[str]] = mapped_column(String(100))
    bank_account_name: Mapped[Optional[str]] = mapped_column(String(50))
    preferred_payment_method: Mapped[Optional[str]] = mapped_column(String(20))
    spirit_value: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    contribution_value: Mapped[Optional[int]] = mapped_column(Integer, server_default=text('0'))
    last_checkin_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    users: Mapped[Optional['Users']] = relationship('Users', remote_side=[id], back_populates='users_reverse')
    users_reverse: Mapped[list['Users']] = relationship('Users', remote_side=[created_by], back_populates='users')
    audit_logs: Mapped[list['AuditLogs']] = relationship('AuditLogs', back_populates='user')
    check_ins: Mapped[list['CheckIns']] = relationship('CheckIns', back_populates='user')
    financial_transactions: Mapped[list['FinancialTransactions']] = relationship('FinancialTransactions', back_populates='user')
    referral_relations: Mapped[list['ReferralRelations']] = relationship('ReferralRelations', foreign_keys='[ReferralRelations.referred_id]', back_populates='referred')
    referral_relations_: Mapped[list['ReferralRelations']] = relationship('ReferralRelations', foreign_keys='[ReferralRelations.referrer_id]', back_populates='referrer')
    roles: Mapped[list['Roles']] = relationship('Roles', back_populates='users')
    role: Mapped[list['Roles']] = relationship('Roles', secondary='user_roles', back_populates='user')
    sessions: Mapped[list['Sessions']] = relationship('Sessions', back_populates='user')
    withdrawal_requests: Mapped[list['WithdrawalRequests']] = relationship('WithdrawalRequests', foreign_keys='[WithdrawalRequests.approved_by]', back_populates='users')
    withdrawal_requests_: Mapped[list['WithdrawalRequests']] = relationship('WithdrawalRequests', foreign_keys='[WithdrawalRequests.user_id]', back_populates='user')
    contribution_value_exchanges: Mapped[list['ContributionValueExchanges']] = relationship('ContributionValueExchanges', back_populates='user')


class AuditLogs(Base):
    __tablename__ = 'audit_logs'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='audit_logs_user_id_fkey'),
        PrimaryKeyConstraint('id', name='audit_logs_pkey'),
        Index('ix_audit_logs_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='日志ID')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='用户ID')
    action: Mapped[str] = mapped_column(String(50), nullable=False, comment='操作类型')
    status: Mapped[str] = mapped_column(String(20), nullable=False, comment='状态：success/failed')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='创建时间')
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), comment='资源类型')
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, comment='资源ID')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='操作描述')
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), comment='IP地址')
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), comment='用户代理')
    error_message: Mapped[Optional[str]] = mapped_column(Text, comment='错误信息')

    user: Mapped['Users'] = relationship('Users', back_populates='audit_logs')


class CheckIns(Base):
    __tablename__ = 'check_ins'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='check_ins_user_id_fkey'),
        PrimaryKeyConstraint('id', name='check_ins_pkey'),
        Index('ix_check_ins_check_in_date', 'check_in_date'),
        Index('ix_check_ins_id', 'id'),
        Index('ix_check_ins_user_id', 'user_id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='签到ID')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='用户ID')
    check_in_date: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, comment='签到日期')
    lingzhi_reward: Mapped[int] = mapped_column(Integer, nullable=False, comment='获得灵值')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='创建时间')

    user: Mapped['Users'] = relationship('Users', back_populates='check_ins')


class FinancialTransactions(Base):
    __tablename__ = 'financial_transactions'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='financial_transactions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='financial_transactions_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    contribution_value: Mapped[Optional[int]] = mapped_column(Integer)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    status: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'success'::character varying"))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    user: Mapped['Users'] = relationship('Users', back_populates='financial_transactions')


class ReferralRelations(Base):
    __tablename__ = 'referral_relations'
    __table_args__ = (
        ForeignKeyConstraint(['referred_id'], ['users.id'], name='referral_relations_referred_id_fkey'),
        ForeignKeyConstraint(['referrer_id'], ['users.id'], name='referral_relations_referrer_id_fkey'),
        PrimaryKeyConstraint('id', name='referral_relations_pkey'),
        UniqueConstraint('referrer_id', 'referred_id', name='referral_relations_referrer_id_referred_id_key'),
        Index('ix_referral_relations_referred_id', 'referred_id'),
        Index('ix_referral_relations_referrer_id', 'referrer_id'),
        {'comment': '推荐关系表'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='推荐关系ID')
    referrer_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='推荐人ID')
    referred_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='被推荐人ID')
    level: Mapped[int] = mapped_column(Integer, nullable=False, comment='推荐层级：1-一级，2-二级，3-三级')
    status: Mapped[str] = mapped_column(String(20), nullable=False, server_default=text("'active'::character varying"), comment='状态：active/inactive')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('CURRENT_TIMESTAMP'), comment='创建时间')

    referred: Mapped['Users'] = relationship('Users', foreign_keys=[referred_id], back_populates='referral_relations')
    referrer: Mapped['Users'] = relationship('Users', foreign_keys=[referrer_id], back_populates='referral_relations_')


class Roles(Base):
    __tablename__ = 'roles'
    __table_args__ = (
        ForeignKeyConstraint(['created_by'], ['users.id'], name='roles_created_by_fkey'),
        PrimaryKeyConstraint('id', name='roles_pkey'),
        UniqueConstraint('name', name='roles_name_key'),
        Index('ix_roles_id', 'id')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='角色ID')
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment='角色名称')
    level: Mapped[int] = mapped_column(Integer, nullable=False, comment='权限级别：1-最高，4-普通')
    status: Mapped[str] = mapped_column(String(20), nullable=False, comment='状态')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='创建时间')
    name_en: Mapped[Optional[str]] = mapped_column(String(50), comment='英文名称')
    description: Mapped[Optional[str]] = mapped_column(Text, comment='角色描述')
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, comment='更新时间')
    created_by: Mapped[Optional[int]] = mapped_column(Integer, comment='创建人ID')

    permission: Mapped[list['Permissions']] = relationship('Permissions', secondary='role_permissions', back_populates='role')
    users: Mapped[Optional['Users']] = relationship('Users', back_populates='roles')
    user: Mapped[list['Users']] = relationship('Users', secondary='user_roles', back_populates='role')


class Sessions(Base):
    __tablename__ = 'sessions'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='sessions_user_id_fkey'),
        PrimaryKeyConstraint('id', name='sessions_pkey'),
        Index('ix_sessions_id', 'id'),
        Index('ix_sessions_session_token', 'session_token', unique=True)
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='会话ID')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='用户ID')
    session_token: Mapped[str] = mapped_column(String(255), nullable=False, comment='会话令牌')
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, comment='是否活跃')
    expires_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, comment='过期时间')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='创建时间')
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), comment='IP地址')
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), comment='用户代理')

    user: Mapped['Users'] = relationship('Users', back_populates='sessions')


class WithdrawalRequests(Base):
    __tablename__ = 'withdrawal_requests'
    __table_args__ = (
        ForeignKeyConstraint(['approved_by'], ['users.id'], name='withdrawal_requests_approved_by_fkey'),
        ForeignKeyConstraint(['user_id'], ['users.id'], name='withdrawal_requests_user_id_fkey'),
        PrimaryKeyConstraint('id', name='withdrawal_requests_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    contribution_value: Mapped[int] = mapped_column(Integer, nullable=False)
    payment_method: Mapped[str] = mapped_column(String(20), nullable=False)
    payment_account: Mapped[str] = mapped_column(String(200), nullable=False)
    status: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'pending'::character varying"))
    reject_reason: Mapped[Optional[str]] = mapped_column(Text)
    approved_by: Mapped[Optional[int]] = mapped_column(Integer)
    approved_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    processed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    users: Mapped[Optional['Users']] = relationship('Users', foreign_keys=[approved_by], back_populates='withdrawal_requests')
    user: Mapped['Users'] = relationship('Users', foreign_keys=[user_id], back_populates='withdrawal_requests_')
    contribution_value_exchanges: Mapped[list['ContributionValueExchanges']] = relationship('ContributionValueExchanges', back_populates='withdrawal_request')


class ContributionValueExchanges(Base):
    __tablename__ = 'contribution_value_exchanges'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='contribution_value_exchanges_user_id_fkey'),
        ForeignKeyConstraint(['withdrawal_request_id'], ['withdrawal_requests.id'], name='contribution_value_exchanges_withdrawal_request_id_fkey'),
        PrimaryKeyConstraint('id', name='contribution_value_exchanges_pkey')
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    contribution_value: Mapped[int] = mapped_column(Integer, nullable=False)
    exchange_amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    exchange_rate: Mapped[Optional[decimal.Decimal]] = mapped_column(Numeric(10, 4), server_default=text('0.1'))
    status: Mapped[Optional[str]] = mapped_column(String(20), server_default=text("'pending'::character varying"))
    withdrawal_request_id: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    processed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)

    user: Mapped['Users'] = relationship('Users', back_populates='contribution_value_exchanges')
    withdrawal_request: Mapped[Optional['WithdrawalRequests']] = relationship('WithdrawalRequests', back_populates='contribution_value_exchanges')


t_role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, primary_key=True),
    Column('permission_id', Integer, primary_key=True),
    ForeignKeyConstraint(['permission_id'], ['permissions.id'], name='role_permissions_permission_id_fkey'),
    ForeignKeyConstraint(['role_id'], ['roles.id'], name='role_permissions_role_id_fkey'),
    PrimaryKeyConstraint('role_id', 'permission_id', name='role_permissions_pkey')
)


t_user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, primary_key=True),
    Column('role_id', Integer, primary_key=True),
    ForeignKeyConstraint(['role_id'], ['roles.id'], name='user_roles_role_id_fkey'),
    ForeignKeyConstraint(['user_id'], ['users.id'], name='user_roles_user_id_fkey'),
    PrimaryKeyConstraint('user_id', 'role_id', name='user_roles_pkey')
)


class EmotionRecords(Base):
    """情绪记录表 - 存储用户的情绪记录"""
    __tablename__ = 'emotion_records'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='emotion_records_user_id_fkey'),
        PrimaryKeyConstraint('id', name='emotion_records_pkey'),
        Index('ix_emotion_records_user_id', 'user_id'),
        Index('ix_emotion_records_created_at', 'created_at'),
        Index('ix_emotion_records_emotion', 'emotion'),
        {'comment': '情绪记录表'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='记录ID')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='用户ID')
    emotion: Mapped[str] = mapped_column(String(20), nullable=False, comment='情绪类型：happy/sad/angry/anxious/surprised/calm')
    emotion_name: Mapped[str] = mapped_column(String(20), nullable=False, comment='情绪名称：开心/悲伤/愤怒/焦虑/惊讶/平静')
    intensity: Mapped[float] = mapped_column(Float, nullable=False, comment='情绪强度：0.0-1.0')
    context: Mapped[Optional[str]] = mapped_column(Text, comment='情绪上下文描述')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='创建时间')

    user: Mapped['Users'] = relationship('Users', backref='emotion_records')


class EmotionDiaries(Base):
    """情绪日记表 - 存储用户的情绪日记"""
    __tablename__ = 'emotion_diaries'
    __table_args__ = (
        ForeignKeyConstraint(['user_id'], ['users.id'], name='emotion_diaries_user_id_fkey'),
        PrimaryKeyConstraint('id', name='emotion_diaries_pkey'),
        Index('ix_emotion_diaries_user_id', 'user_id'),
        Index('ix_emotion_diaries_created_at', 'created_at'),
        {'comment': '情绪日记表'}
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, comment='日记ID')
    user_id: Mapped[int] = mapped_column(Integer, nullable=False, comment='用户ID')
    content: Mapped[str] = mapped_column(Text, nullable=False, comment='日记内容')
    emotion: Mapped[str] = mapped_column(String(20), nullable=False, comment='情绪类型：happy/sad/angry/anxious/surprised/calm')
    emotion_name: Mapped[str] = mapped_column(String(20), nullable=False, comment='情绪名称：开心/悲伤/愤怒/焦虑/惊讶/平静')
    intensity: Mapped[float] = mapped_column(Float, nullable=False, comment='情绪强度：0.0-1.0')
    tags: Mapped[Optional[dict]] = mapped_column(JSON, comment='标签（JSON数组）')
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, nullable=False, server_default=text('now()'), comment='创建时间')

    user: Mapped['Users'] = relationship('Users', backref='emotion_diaries')
