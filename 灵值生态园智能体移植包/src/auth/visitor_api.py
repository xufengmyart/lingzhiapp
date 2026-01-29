"""
访客管理的API接口
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from models import Base, User, Visitor, TeamMember, AuditLog
from api import get_db, get_current_user, create_audit_log


# Pydantic模型
class VisitorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    wechat: str = Field(..., min_length=1, max_length=50)
    phone: str = Field(..., min_length=11, max_length=20)
    referrer: Optional[str] = None
    notes: Optional[str] = None
    shipping_address: Optional[str] = None
    is_team_leader: bool = False
    willing_to_be_leader: Optional[bool] = None


class VisitorUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    notes: Optional[str] = None
    shipping_address: Optional[str] = None
    is_team_leader: Optional[bool] = None
    willing_to_be_leader: Optional[bool] = None
    status: Optional[str] = None


class VisitorResponse(BaseModel):
    id: int
    name: str
    wechat: str
    phone: str
    referrer: Optional[str]
    notes: Optional[str]
    shipping_address: Optional[str]
    is_team_leader: bool
    willing_to_be_leader: Optional[bool]
    status: str
    team_member_count: int
    can_be_team_leader: bool
    created_at: datetime

    class Config:
        from_attributes = True


class TeamMemberCreate(BaseModel):
    team_leader_id: int
    member_id: int
    role: Optional[str] = None
    notes: Optional[str] = None


# 导入FastAPI app实例
from api import app
from api import check_permission


@app.post("/api/visitors", response_model=VisitorResponse, status_code=status.HTTP_201_CREATED)
async def create_visitor(
    visitor_data: VisitorCreate,
    request: Request = None,
    current_user: User = Depends(check_permission("visitor:create")),
    db: Session = Depends(get_db)
):
    """创建访客"""
    # 检查微信是否已存在
    if db.query(Visitor).filter(Visitor.wechat == visitor_data.wechat).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="微信号已存在"
        )

    # 检查电话是否已存在
    if db.query(Visitor).filter(Visitor.phone == visitor_data.phone).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="电话号码已存在"
        )

    # 创建访客
    new_visitor = Visitor(
        name=visitor_data.name,
        wechat=visitor_data.wechat,
        phone=visitor_data.phone,
        referrer=visitor_data.referrer,
        notes=visitor_data.notes,
        shipping_address=visitor_data.shipping_address,
        is_team_leader=visitor_data.is_team_leader,
        willing_to_be_leader=visitor_data.willing_to_be_leader,
        status="active",
        created_by=current_user.id
    )
    db.add(new_visitor)
    db.commit()
    db.refresh(new_visitor)

    # 记录日志
    create_audit_log(
        db, current_user.id, "visitor:create",
        resource_type="visitor",
        resource_id=new_visitor.id,
        description=f"创建访客：{visitor_data.name}（微信：{visitor_data.wechat}）",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return new_visitor


@app.get("/api/visitors", response_model=List[VisitorResponse])
async def get_visitors(
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    is_team_leader: Optional[bool] = None,
    current_user: User = Depends(check_permission("visitor:view")),
    db: Session = Depends(get_db)
):
    """获取访客列表"""
    query = db.query(Visitor)

    if status:
        query = query.filter(Visitor.status == status)

    if is_team_leader is not None:
        query = query.filter(Visitor.is_team_leader == is_team_leader)

    visitors = query.offset(skip).limit(limit).all()
    return visitors


@app.get("/api/visitors/{visitor_id}", response_model=VisitorResponse)
async def get_visitor(
    visitor_id: int,
    current_user: User = Depends(check_permission("visitor:view")),
    db: Session = Depends(get_db)
):
    """获取访客详情"""
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )
    return visitor


@app.put("/api/visitors/{visitor_id}", response_model=VisitorResponse)
async def update_visitor(
    visitor_id: int,
    visitor_data: VisitorUpdate,
    request: Request = None,
    current_user: User = Depends(check_permission("visitor:modify")),
    db: Session = Depends(get_db)
):
    """更新访客信息"""
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )

    # 更新访客信息
    if visitor_data.name is not None:
        visitor.name = visitor_data.name
    if visitor_data.phone is not None:
        visitor.phone = visitor_data.phone
    if visitor_data.notes is not None:
        visitor.notes = visitor_data.notes
    if visitor_data.shipping_address is not None:
        visitor.shipping_address = visitor_data.shipping_address
    if visitor_data.is_team_leader is not None:
        visitor.is_team_leader = visitor_data.is_team_leader
    if visitor_data.willing_to_be_leader is not None:
        visitor.willing_to_be_leader = visitor_data.willing_to_be_leader
    if visitor_data.status is not None:
        visitor.status = visitor_data.status

    db.commit()

    # 记录日志
    create_audit_log(
        db, current_user.id, "visitor:modify",
        resource_type="visitor",
        resource_id=visitor.id,
        description=f"更新访客：{visitor.name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return visitor


@app.delete("/api/visitors/{visitor_id}")
async def delete_visitor(
    visitor_id: int,
    request: Request = None,
    current_user: User = Depends(check_permission("visitor:delete")),
    db: Session = Depends(get_db)
):
    """删除访客"""
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )

    visitor_name = visitor.name
    db.delete(visitor)
    db.commit()

    # 记录日志
    create_audit_log(
        db, current_user.id, "visitor:delete",
        resource_type="visitor",
        resource_id=visitor_id,
        description=f"删除访客：{visitor_name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return {"message": "访客删除成功"}


@app.post("/api/visitors/{visitor_id}/approve-leader")
async def approve_team_leader(
    visitor_id: int,
    request: Request = None,
    current_user: User = Depends(check_permission("visitor:approve_leader")),
    db: Session = Depends(get_db)
):
    """审批团队长申请"""
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )

    # 检查是否满足团队长条件
    team_member_count = len(visitor.team_members)
    if team_member_count < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"团队成员不足，当前只有{team_member_count}个，需要至少3个"
        )

    if not visitor.willing_to_be_leader:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="访客不愿意成为团队长"
        )

    # 批准为团队长
    visitor.is_team_leader = True
    db.commit()

    # 记录日志
    create_audit_log(
        db, current_user.id, "visitor:approve_leader",
        resource_type="visitor",
        resource_id=visitor.id,
        description=f"审批通过团队长：{visitor.name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return {
        "message": "团队长审批通过",
        "visitor_id": visitor.id,
        "name": visitor.name,
        "team_member_count": team_member_count
    }


@app.post("/api/team-members")
async def add_team_member(
    member_data: TeamMemberCreate,
    request: Request = None,
    current_user: User = Depends(check_permission("visitor:manage_team")),
    db: Session = Depends(get_db)
):
    """添加团队成员"""
    # 检查团队长是否存在
    team_leader = db.query(Visitor).filter(Visitor.id == member_data.team_leader_id).first()
    if not team_leader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队长不存在"
        )

    # 检查成员是否存在
    member = db.query(Visitor).filter(Visitor.id == member_data.member_id).first()
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="成员不存在"
        )

    # 检查是否已经是团队成员
    existing = db.query(TeamMember).filter(
        TeamMember.team_leader_id == member_data.team_leader_id,
        TeamMember.member_id == member_data.member_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该成员已在团队中"
        )

    # 创建团队成员关系
    team_member = TeamMember(
        team_leader_id=member_data.team_leader_id,
        member_id=member_data.member_id,
        role=member_data.role,
        notes=member_data.notes
    )
    db.add(team_member)
    db.commit()

    # 记录日志
    create_audit_log(
        db, current_user.id, "visitor:manage_team",
        resource_type="team_member",
        resource_id=team_member.id,
        description=f"添加团队成员：{member.name} 到 {team_leader.name} 的团队",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return {
        "message": "团队成员添加成功",
        "team_member_id": team_member.id,
        "team_leader": team_leader.name,
        "member": member.name,
        "team_member_count": len(team_leader.team_members)
    }


@app.delete("/api/team-members/{team_member_id}")
async def remove_team_member(
    team_member_id: int,
    request: Request = None,
    current_user: User = Depends(check_permission("visitor:manage_team")),
    db: Session = Depends(get_db)
):
    """移除团队成员"""
    team_member = db.query(TeamMember).filter(TeamMember.id == team_member_id).first()
    if not team_member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="团队成员关系不存在"
        )

    team_leader = team_member.team_leader
    member = team_member.member

    db.delete(team_member)
    db.commit()

    # 记录日志
    create_audit_log(
        db, current_user.id, "visitor:manage_team",
        resource_type="team_member",
        resource_id=team_member_id,
        description=f"从 {team_leader.name} 的团队移除成员：{member.name}",
        ip_address=request.client.host if request else None,
        user_agent=request.headers.get("user-agent") if request else None
    )

    return {
        "message": "团队成员移除成功",
        "team_leader": team_leader.name,
        "member": member.name
    }


@app.get("/api/visitors/{visitor_id}/team-members")
async def get_team_members(
    visitor_id: int,
    current_user: User = Depends(check_permission("visitor:view")),
    db: Session = Depends(get_db)
):
    """获取访客的团队成员"""
    visitor = db.query(Visitor).filter(Visitor.id == visitor_id).first()
    if not visitor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="访客不存在"
        )

    return {
        "team_leader": {
            "id": visitor.id,
            "name": visitor.name,
            "wechat": visitor.wechat,
            "phone": visitor.phone,
            "is_team_leader": visitor.is_team_leader,
            "can_be_team_leader": visitor.can_be_team_leader
        },
        "members": [
            {
                "id": tm.member.id,
                "name": tm.member.name,
                "wechat": tm.member.wechat,
                "phone": tm.member.phone,
                "role": tm.role,
                "joined_at": tm.joined_at,
                "notes": tm.notes
            }
            for tm in visitor.team_members
        ],
        "member_count": len(visitor.team_members)
    }


# 导入Request
from fastapi import Request
