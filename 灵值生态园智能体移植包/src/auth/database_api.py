"""
媄月商业艺术 - 数据库访问接口
支持用户登录后查询数据库信息
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from models import (
    User, Role, Permission, user_roles, role_permissions
)
from init_data import SessionLocal
from api import get_current_user
from models import AuditLog
from api import create_audit_log as audit_log

router = APIRouter(prefix="/api/database", tags=["数据库访问"])


# 数据库响应模型
class DatabaseStatsResponse(BaseModel):
    """数据库统计信息"""
    users_count: int
    roles_count: int
    permissions_count: int
    user_roles_count: int
    role_permissions_count: int
    database_size: str


class UserDetailResponse(BaseModel):
    """用户详情"""
    id: int
    name: str
    email: str
    position: str
    is_ceo: bool
    wechat: Optional[str]
    created_at: datetime
    updated_at: datetime
    roles: List[str]


class RoleDetailResponse(BaseModel):
    """角色详情"""
    id: int
    name: str
    english_name: str
    level: int
    description: str
    permissions_count: int
    users_count: int
    created_at: datetime


class PermissionDetailResponse(BaseModel):
    """权限详情"""
    id: int
    code: str
    name: str
    description: str
    roles: List[str]


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/stats", response_model=DatabaseStatsResponse)
async def get_database_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取数据库统计信息
    需要权限：database:view
    """
    # 检查权限
    if not current_user.has_permission("database:view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有查看数据库统计的权限"
        )
    
    # 统计各表记录数
    users_count = db.query(User).count()
    roles_count = db.query(Role).count()
    permissions_count = db.query(Permission).count()
    user_roles_count = db.execute(user_roles.select()).rowcount
    role_permissions_count = db.execute(role_permissions.select()).rowcount
    
    # 获取数据库文件大小（SQLite）
    import os
    db_path = os.path.join(os.path.dirname(__file__), "auth.db")
    if os.path.exists(db_path):
        size_bytes = os.path.getsize(db_path)
        size_mb = size_bytes / (1024 * 1024)
        database_size = f"{size_mb:.2f} MB"
    else:
        database_size = "未知"
    
    # 记录审计日志
    audit_log(
        db=db,
        user_id=current_user.id,
        action="database_stats_view",
        resource_type="database",
        description=f"查看数据库统计信息"
    )
    
    return DatabaseStatsResponse(
        users_count=users_count,
        roles_count=roles_count,
        permissions_count=permissions_count,
        user_roles_count=user_roles_count,
        role_permissions_count=role_permissions_count,
        database_size=database_size
    )


@router.get("/users", response_model=List[UserDetailResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户列表
    需要权限：user:view
    """
    # 检查权限
    if not current_user.has_permission("user:view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有查看用户列表的权限"
        )
    
    users = db.query(User).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        # 获取用户角色
        user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
        role_ids = [ur.role_id for ur in user_roles]
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        role_names = [role.name for role in roles]
        
        result.append(UserDetailResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            position=user.position,
            is_ceo=user.is_ceo,
            wechat=user.wechat,
            created_at=user.created_at,
            updated_at=user.updated_at,
            roles=role_names
        ))
    
    # 记录审计日志
    audit_log(
        user_id=current_user.id,
        action="users_list",
        resource_type="user",
        details=f"查看用户列表，数量：{len(result)}"
    )
    
    return result


@router.get("/users/{user_id}", response_model=UserDetailResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取用户详情
    需要权限：user:view
    """
    # 检查权限
    if not current_user.has_permission("user:view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有查看用户详情的权限"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"用户ID {user_id} 不存在"
        )
    
    # 获取用户角色
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    role_names = [role.name for role in roles]
    
    return UserDetailResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        position=user.position,
        is_ceo=user.is_ceo,
        wechat=user.wechat,
        created_at=user.created_at,
        updated_at=user.updated_at,
        roles=role_names
    )


@router.get("/roles", response_model=List[RoleDetailResponse])
async def list_roles(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色列表
    需要权限：role:view
    """
    # 检查权限
    if not current_user.has_permission("role:view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有查看角色列表的权限"
        )
    
    roles = db.query(Role).order_by(Role.level).offset(skip).limit(limit).all()
    
    result = []
    for role in roles:
        # 统计权限数量
        permissions_count = db.query(RolePermission).filter(
            RolePermission.role_id == role.id
        ).count()
        
        # 统计用户数量
        users_count = db.query(UserRole).filter(UserRole.role_id == role.id).count()
        
        result.append(RoleDetailResponse(
            id=role.id,
            name=role.name,
            english_name=role.english_name,
            level=role.level,
            description=role.description,
            permissions_count=permissions_count,
            users_count=users_count,
            created_at=role.created_at
        ))
    
    # 记录审计日志
    audit_log(
        user_id=current_user.id,
        action="roles_list",
        resource_type="role",
        details=f"查看角色列表，数量：{len(result)}"
    )
    
    return result


@router.get("/roles/{role_id}", response_model=RoleDetailResponse)
async def get_role(
    role_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取角色详情
    需要权限：role:view
    """
    # 检查权限
    if not current_user.has_permission("role:view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有查看角色详情的权限"
        )
    
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"角色ID {role_id} 不存在"
        )
    
    # 统计权限数量
    permissions_count = db.query(RolePermission).filter(
        RolePermission.role_id == role.id
    ).count()
    
    # 统计用户数量
    users_count = db.query(UserRole).filter(UserRole.role_id == role.id).count()
    
    return RoleDetailResponse(
        id=role.id,
        name=role.name,
        english_name=role.english_name,
        level=role.level,
        description=role.description,
        permissions_count=permissions_count,
        users_count=users_count,
        created_at=role.created_at
    )


@router.get("/permissions", response_model=List[PermissionDetailResponse])
async def list_permissions(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取权限列表
    需要权限：permission:view
    """
    # 检查权限
    if not current_user.has_permission("permission:view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有查看权限列表的权限"
        )
    
    permissions = db.query(Permission).offset(skip).limit(limit).all()
    
    result = []
    for perm in permissions:
        # 获取拥有此权限的角色
        role_perms = db.query(RolePermission).filter(
            RolePermission.permission_id == perm.id
        ).all()
        role_ids = [rp.role_id for rp in role_perms]
        roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
        role_names = [role.name for role in roles]
        
        result.append(PermissionDetailResponse(
            id=perm.id,
            code=perm.code,
            name=perm.name,
            description=perm.description,
            roles=role_names
        ))
    
    # 记录审计日志
    audit_log(
        user_id=current_user.id,
        action="permissions_list",
        resource_type="permission",
        details=f"查看权限列表，数量：{len(result)}"
    )
    
    return result


@router.get("/permissions/{permission_id}", response_model=PermissionDetailResponse)
async def get_permission(
    permission_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取权限详情
    需要权限：permission:view
    """
    # 检查权限
    if not current_user.has_permission("permission:view"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您没有查看权限详情的权限"
        )
    
    perm = db.query(Permission).filter(Permission.id == permission_id).first()
    if not perm:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"权限ID {permission_id} 不存在"
        )
    
    # 获取拥有此权限的角色
    role_perms = db.query(RolePermission).filter(
        RolePermission.permission_id == perm.id
    ).all()
    role_ids = [rp.role_id for rp in role_perms]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    role_names = [role.name for role in roles]
    
    return PermissionDetailResponse(
        id=perm.id,
        code=perm.code,
        name=perm.name,
        description=perm.description,
        roles=role_names
    )


@router.get("/current-user")
async def get_current_user_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取当前登录用户信息
    """
    # 获取用户角色
    user_roles = db.query(UserRole).filter(UserRole.user_id == current_user.id).all()
    role_ids = [ur.role_id for ur in user_roles]
    roles = db.query(Role).filter(Role.id.in_(role_ids)).all()
    
    # 获取所有权限
    all_permissions = []
    for role in roles:
        role_perms = db.query(RolePermission).filter(RolePermission.role_id == role.id).all()
        perm_ids = [rp.permission_id for rp in role_perms]
        perms = db.query(Permission).filter(Permission.id.in_(perm_ids)).all()
        all_permissions.extend([perm.code for perm in perms])
    
    # 去重
    all_permissions = list(set(all_permissions))
    
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "position": current_user.position,
        "is_ceo": current_user.is_ceo,
        "wechat": current_user.wechat,
        "roles": [{"id": r.id, "name": r.name, "english_name": r.english_name, "level": r.level} for r in roles],
        "permissions": all_permissions,
        "created_at": current_user.created_at
    }
