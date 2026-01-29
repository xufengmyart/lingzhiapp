"""
权限管理系统的API接口
"""
from fastapi import FastAPI, Depends, HTTPException, status, Header, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import pyotp
import secrets
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import Base, User, Role, Permission, AuditLog, Session
from init_data import engine, SessionLocal, init_database

# FastAPI应用
app = FastAPI(
    title="媄月商业艺术 - 权限管理系统",
    description="完整的权限管理API接口",
    version="1.0.0"
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT配置
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8小时

# OAuth2密码方案
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

# 数据库依赖
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# 当前用户依赖
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """获取当前登录用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="无法验证凭据",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception

    return user


# 权限检查依赖
def check_permission(permission_code: str):
    """检查用户是否有指定权限"""
    def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if not current_user.has_permission(permission_code):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"缺少权限：{permission_code}"
            )
        return current_user
    return permission_checker


def require_permission(user: User, permission_code: str):
    """检查用户是否有指定权限（非依赖注入版本）"""
    if not user.has_permission(permission_code):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"缺少权限：{permission_code}"
        )


# Pydantic模型
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    phone: Optional[str] = None
    password: str = Field(..., min_length=8)
    department: str
    position: str
    role_ids: List[int] = []


class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    role_ids: Optional[List[int]] = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    department: str
    position: str
    status: str
    is_superuser: bool
    two_factor_enabled: bool
    roles: List[dict]
    created_at: datetime

    class Config:
        from_attributes = True


class RoleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    name_en: str = Field(..., min_length=1, max_length=50)
    level: int = Field(..., ge=1, le=4)
    description: Optional[str] = None
    permission_ids: List[int] = []


class RoleResponse(BaseModel):
    id: int
    name: str
    name_en: str
    level: int
    description: Optional[str]
    permissions: List[dict]

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


class PermissionResponse(BaseModel):
    id: int
    code: str
    name: str
    module: str
    description: Optional[str]

    class Config:
        from_attributes = True


# 工具函数
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def hash_password(password: str) -> str:
    """哈希密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_audit_log(db: Session, user_id: int, action: str, resource_type: str = None,
                    resource_id: int = None, description: str = None,
                    ip_address: str = None, user_agent: str = None, status: str = "success"):
    """创建审计日志"""
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        description=description,
        ip_address=ip_address,
        user_agent=user_agent,
        status=status
    )
    db.add(log)
    db.commit()
    return log


# API路由

@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "媄月商业艺术 - 权限管理系统 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.post("/api/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    request: Request = None,
    db: Session = Depends(get_db)
):
    """用户登录"""
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        # 记录失败日志
        if user:
            create_audit_log(
                db, user.id, "login_failed",
                ip_address=request.client.host if request else None,
                user_agent=request.headers.get("user-agent") if request else None,
                status="failed",
                description="密码错误"
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"账号状态：{user.status}"
        )

    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()

    # 创建访问令牌
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    # 记录登录日志
    create_audit_log(
        db, user.id, "login_success",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None,
        description="用户登录成功"
    )

    # 获取用户角色
    roles = [{"id": r.id, "name": r.name, "level": r.level} for r in user.roles]

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse(
            id=user.id,
            name=user.name,
            email=user.email,
            phone=user.phone,
            department=user.department,
            position=user.position,
            status=user.status,
            is_superuser=user.is_superuser,
            two_factor_enabled=user.two_factor_enabled,
            roles=roles,
            created_at=user.created_at
        )
    }


@app.get("/api/users", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_permission("user:view")),
    db: Session = Depends(get_db)
):
    """获取用户列表"""
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@app.post("/api/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    request: Request = None,
    current_user: User = Depends(check_permission("user:create")),
    db: Session = Depends(get_db)
):
    """创建用户"""
    # 检查邮箱是否已存在
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已存在"
        )

    # 创建用户
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        department=user_data.department,
        position=user_data.position,
        status="active",
        two_factor_enabled=True,
        two_factor_secret=pyotp.random_base32(),
        created_by=current_user.id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 分配角色
    if user_data.role_ids:
        roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
        new_user.roles = roles
        db.commit()

    # 记录日志
    create_audit_log(
        db, current_user.id, "user:create",
        resource_type="user",
        resource_id=new_user.id,
        description=f"创建用户：{user_data.name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return new_user


@app.put("/api/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    request: Request = None,
    current_user: User = Depends(check_permission("user:modify")),
    db: Session = Depends(get_db)
):
    """更新用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 更新用户信息
    if user_data.name is not None:
        user.name = user_data.name
    if user_data.phone is not None:
        user.phone = user_data.phone
    if user_data.department is not None:
        user.department = user_data.department
    if user_data.position is not None:
        user.position = user.position
    if user_data.status is not None:
        user.status = user_data.status

    # 更新角色
    if user_data.role_ids is not None:
        roles = db.query(Role).filter(Role.id.in_(user_data.role_ids)).all()
        user.roles = roles

    db.commit()

    # 记录日志
    create_audit_log(
        db, current_user.id, "user:modify",
        resource_type="user",
        resource_id=user.id,
        description=f"更新用户：{user.name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return user


@app.delete("/api/users/{user_id}")
async def delete_user(
    user_id: int,
    request: Request = None,
    current_user: User = Depends(check_permission("user:delete")),
    db: Session = Depends(get_db)
):
    """删除用户"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )

    # 不允许删除自己
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不能删除自己"
        )

    user_name = user.name
    db.delete(user)
    db.commit()

    # 记录日志
    create_audit_log(
        db, current_user.id, "user:delete",
        resource_type="user",
        resource_id=user_id,
        description=f"删除用户：{user_name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return {"message": "用户删除成功"}


@app.get("/api/roles", response_model=List[RoleResponse])
async def get_roles(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_permission("role:view")),
    db: Session = Depends(get_db)
):
    """获取角色列表"""
    roles = db.query(Role).offset(skip).limit(limit).all()
    return roles


@app.get("/api/permissions", response_model=List[PermissionResponse])
async def get_permissions(
    module: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取权限列表"""
    query = db.query(Permission)
    if module:
        query = query.filter(Permission.module == module)
    permissions = query.all()
    return permissions


@app.get("/api/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """获取当前用户信息"""
    return current_user


@app.get("/api/me/permissions")
async def get_my_permissions(current_user: User = Depends(get_current_user)):
    """获取当前用户的权限"""
    permissions = current_user.get_all_permissions()
    return {
        "permissions": permissions,
        "is_superuser": current_user.is_superuser
    }


@app.get("/api/audit-logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(check_permission("log:view")),
    db: Session = Depends(get_db)
):
    """获取审计日志"""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs


@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据库"""
    print("正在初始化数据库...")
    init_database()

# 导入访客管理API
try:
    from visitor_api import *  # 导入访客管理相关的路由
except ImportError:
    print("警告：访客管理API模块未找到")

# 导入数据库访问API
try:
    from database_api import router as database_router  # 导入数据库访问相关的路由
    app.include_router(database_router)  # 注册数据库访问路由
    print("✓ 数据库访问API已加载")
except ImportError as e:
    print(f"警告：数据库访问API模块未找到: {str(e)}")

# 导入生态机制API
try:
    from ecosystem_api import router as ecosystem_router  # 导入生态机制相关的路由
    app.include_router(ecosystem_router)  # 注册生态机制路由
    print("✓ 生态机制API已加载")
except ImportError as e:
    print(f"警告：生态机制API模块未找到: {str(e)}")

# 导入项目参与和团队组建API
try:
    from project_api import router as project_router  # 导入项目参与和团队组建相关的路由
    app.include_router(project_router)  # 注册项目参与和团队组建路由
    print("✓ 项目参与和团队组建API已加载")
except ImportError as e:
    print(f"警告：项目参与和团队组建API模块未找到: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
