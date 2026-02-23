"""
超级管理员管理模块
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import func
import hashlib
from datetime import datetime, timedelta

from src.storage.database.shared.model import User, Role, Permission, AuditLog


class SuperAdminCreate(BaseModel):
    """创建超级管理员请求"""
    name: str = Field(..., description="管理员姓名")
    email: str = Field(..., description="管理员邮箱")
    password: str = Field(..., min_length=8, description="密码，至少8位")
    phone: Optional[str] = Field(None, description="电话号码")
    wechat: Optional[str] = Field(None, description="微信号")


class SuperAdminUpdate(BaseModel):
    """更新超级管理员请求"""
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    phone: Optional[str] = None
    wechat: Optional[str] = None
    ip_whitelist: Optional[List[str]] = None


class SuperAdminManager:
    """超级管理员管理器"""

    def __init__(self):
        pass

    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        return hashlib.sha256(password.encode()).hexdigest()

    def get_super_admin_count(self, db: Session) -> int:
        """获取超级管理员数量"""
        return db.query(func.count(User.id)).filter(User.is_superuser == True).scalar()

    def get_super_admin(self, db: Session, user_id: int) -> Optional[User]:
        """获取超级管理员"""
        return db.query(User).filter(User.id == user_id, User.is_superuser == True).first()

    def get_all_super_admins(self, db: Session) -> List[User]:
        """获取所有超级管理员（应该最多1个）"""
        return db.query(User).filter(User.is_superuser == True).all()

    def create_super_admin(self, db: Session, admin_in: SuperAdminCreate) -> User:
        """创建超级管理员

        注意：系统中只能有1个超级管理员
        """
        # 检查是否已存在超级管理员
        existing_count = self.get_super_admin_count(db)
        if existing_count >= 1:
            raise ValueError("系统中已存在超级管理员，不能创建多个超级管理员")

        # 检查邮箱是否已被使用
        existing_user = db.query(User).filter(User.email == admin_in.email).first()
        if existing_user:
            raise ValueError(f"邮箱 {admin_in.email} 已被使用")

        # 创建超级管理员
        db_user = User(
            name=admin_in.name,
            email=admin_in.email,
            password_hash=self._hash_password(admin_in.password),
            phone=admin_in.phone,
            wechat=admin_in.wechat,
            is_superuser=True,
            two_factor_enabled=True,  # 强制启用双因素认证
            status='active',
            created_at=datetime.now()
        )

        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)

            # 记录审计日志
            audit_log = AuditLog(
                user_id=db_user.id,
                action='create_super_admin',
                resource_type='user',
                resource_id=db_user.id,
                description=f'创建超级管理员: {admin_in.name}',
                status='success',
                created_at=datetime.now()
            )
            db.add(audit_log)
            db.commit()

            return db_user
        except Exception as e:
            db.rollback()
            raise

    def update_super_admin(self, db: Session, user_id: int, admin_in: SuperAdminUpdate) -> Optional[User]:
        """更新超级管理员信息"""
        db_user = self.get_super_admin(db, user_id)
        if not db_user:
            return None

        update_data = admin_in.model_dump(exclude_unset=True)

        # 处理密码
        if 'password' in update_data:
            update_data['password_hash'] = self._hash_password(update_data.pop('password'))

        # 处理IP白名单
        if 'ip_whitelist' in update_data:
            import json
            update_data['ip_whitelist'] = json.dumps(update_data.pop('ip_whitelist'))

        # 更新字段
        for field, value in update_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)

        db.add(db_user)
        try:
            db.commit()
            db.refresh(db_user)

            # 记录审计日志
            audit_log = AuditLog(
                user_id=user_id,
                action='update_super_admin',
                resource_type='user',
                resource_id=user_id,
                description=f'更新超级管理员信息',
                status='success',
                created_at=datetime.now()
            )
            db.add(audit_log)
            db.commit()

            return db_user
        except Exception as e:
            db.rollback()
            raise

    def transfer_super_admin(self, db: Session, current_admin_id: int, new_admin_id: int) -> bool:
        """转移超级管理员权限

        将超级管理员权限从当前管理员转移到新管理员
        """
        # 验证当前管理员是超级管理员
        current_admin = self.get_super_admin(db, current_admin_id)
        if not current_admin:
            raise ValueError("当前用户不是超级管理员")

        # 验证新管理员
        new_admin = db.query(User).filter(User.id == new_admin_id).first()
        if not new_admin:
            raise ValueError("新管理员不存在")

        if new_admin.is_superuser:
            raise ValueError("新管理员已经是超级管理员")

        # 转移权限
        current_admin.is_superuser = False
        new_admin.is_superuser = True
        new_admin.two_factor_enabled = True  # 强制启用双因素认证

        try:
            db.commit()
            db.refresh(current_admin)
            db.refresh(new_admin)

            # 记录审计日志
            audit_log = AuditLog(
                user_id=current_admin_id,
                action='transfer_super_admin',
                resource_type='user',
                resource_id=new_admin_id,
                description=f'超级管理员权限从 {current_admin.name} 转移到 {new_admin.name}',
                status='success',
                created_at=datetime.now()
            )
            db.add(audit_log)
            db.commit()

            return True
        except Exception as e:
            db.rollback()
            raise

    def verify_super_admin_uniqueness(self, db: Session) -> dict:
        """验证超级管理员唯一性

        返回验证结果：
        {
            'valid': bool,  # 是否符合唯一性原则
            'count': int,   # 超级管理员数量
            'message': str  # 详细信息
        }
        """
        count = self.get_super_admin_count(db)

        if count == 0:
            return {
                'valid': False,
                'count': 0,
                'message': '系统中不存在超级管理员，需要创建超级管理员'
            }
        elif count == 1:
            return {
                'valid': True,
                'count': 1,
                'message': '系统中存在1个超级管理员，符合唯一性原则'
            }
        else:
            return {
                'valid': False,
                'count': count,
                'message': f'系统中存在{count}个超级管理员，超过唯一性限制（最多1个），需要通过转让方式减少到1个'
            }

    def initialize_default_super_admin(self, db: Session) -> User:
        """初始化默认超级管理员

        如果系统中不存在超级管理员，则创建默认超级管理员
        """
        # 检查是否已存在超级管理员
        existing_count = self.get_super_admin_count(db)
        if existing_count >= 1:
            raise ValueError("系统中已存在超级管理员，不能重复初始化")

        # 创建默认超级管理员
        default_admin = SuperAdminCreate(
            name="系统超级管理员",
            email="admin@lingzhi.eco",
            password="LINGZI@2026#Super",
            phone=None,
            wechat=None
        )

        return self.create_super_admin(db, default_admin)
