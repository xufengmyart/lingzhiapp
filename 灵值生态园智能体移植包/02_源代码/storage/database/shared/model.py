"""
灵值生态系统数据库模型
基于 SQLAlchemy 2.0 规范
"""

from coze_coding_dev_sdk.database import Base
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Table, Float, Enum, func
from sqlalchemy.orm import relationship, mapped_column, Mapped
from typing import Optional, List
from datetime import datetime
import enum


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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='用户ID')
    name: Mapped[str] = mapped_column(String(50), nullable=False, comment='用户姓名')
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True, comment='邮箱')
    phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True, comment='电话')
    wechat: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='微信号')
    coze_id: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, unique=True, index=True, comment='扣子平台注册ID')
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, comment='密码哈希')
    department: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='部门')
    position: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='职位')
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False, comment='状态：active/inactive/locked')
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment='是否超级管理员')
    is_ceo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment='是否CEO')
    two_factor_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, comment='是否启用双因素认证')
    two_factor_secret: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment='双因素认证密钥')
    ip_whitelist: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='IP白名单（JSON数组）')
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment='最后登录时间')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True, comment='更新时间')
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True, comment='创建人ID')

    # 关系
    roles: Mapped[List["Role"]] = relationship('Role', secondary=user_roles, back_populates='users')
    created_user: Mapped[Optional["User"]] = relationship('User', remote_side=[id])
    audit_logs: Mapped[List["AuditLog"]] = relationship('AuditLog', back_populates='user')

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

    def get_all_permissions(self) -> List[str]:
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

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='角色ID')
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, comment='角色名称')
    name_en: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='英文名称')
    level: Mapped[int] = mapped_column(Integer, default=4, nullable=False, comment='权限级别：1-最高，4-普通')
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='角色描述')
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False, comment='状态')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True, comment='更新时间')
    created_by: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey('users.id'), nullable=True, comment='创建人ID')

    # 关系
    users: Mapped[List["User"]] = relationship('User', secondary=user_roles, back_populates='roles')
    permissions: Mapped[List["Permission"]] = relationship('Permission', secondary=role_permissions, back_populates='roles')

    def __repr__(self):
        return f"<Role(id={self.id}, name='{self.name}', level={self.level})>"


class Permission(Base):
    """权限表"""
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='权限ID')
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True, comment='权限代码')
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment='权限名称')
    module: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='所属模块')
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='权限描述')
    status: Mapped[str] = mapped_column(String(20), default='active', nullable=False, comment='状态')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment='创建时间')
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True, comment='更新时间')

    # 关系
    roles: Mapped[List["Role"]] = relationship('Role', secondary=role_permissions, back_populates='permissions')

    def __repr__(self):
        return f"<Permission(id={self.id}, code='{self.code}', name='{self.name}')>"


class AuditLog(Base):
    """审计日志表"""
    __tablename__ = 'audit_logs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='日志ID')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    action: Mapped[str] = mapped_column(String(50), nullable=False, comment='操作类型')
    resource_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='资源类型')
    resource_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment='资源ID')
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='操作描述')
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='IP地址')
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment='用户代理')
    status: Mapped[str] = mapped_column(String(20), default='success', nullable=False, comment='状态：success/failed')
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment='错误信息')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment='创建时间')

    # 关系
    user: Mapped["User"] = relationship('User', back_populates='audit_logs')

    def __repr__(self):
        return f"<AuditLog(id={self.id}, user_id={self.user_id}, action='{self.action}')>"


class CheckIn(Base):
    """签到表"""
    __tablename__ = 'check_ins'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='签到ID')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, index=True, comment='用户ID')
    check_in_date: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True, comment='签到日期')
    lingzhi_reward: Mapped[int] = mapped_column(Integer, nullable=False, default=10, comment='获得灵值')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment='创建时间')

    # 关系
    user: Mapped["User"] = relationship('User', backref='check_ins')

    def __repr__(self):
        return f"<CheckIn(id={self.id}, user_id={self.user_id}, date={self.check_in_date}, reward={self.lingzhi_reward})>"


class Session(Base):
    """会话表"""
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, comment='会话ID')
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False, comment='用户ID')
    session_token: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True, comment='会话令牌')
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, comment='IP地址')
    user_agent: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, comment='用户代理')
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, comment='是否活跃')
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, comment='过期时间')
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), nullable=False, comment='创建时间')

    def __repr__(self):
        return f"<Session(id={self.id}, user_id={self.user_id}, is_active={self.is_active})>"
