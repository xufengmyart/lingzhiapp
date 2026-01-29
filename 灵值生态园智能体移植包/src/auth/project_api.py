"""
项目参与和团队组建API接口
支持创业机会购买、团队组建、专家聘请等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
import secrets

from models_project import (
    Opportunity, OpportunityParticipation, Expert, Team,
    TeamPartnerMember, TeamExpert, ExpertEngagement, TeamMilestone,
    OpportunityStatus, TeamRole
)
from api import get_db, get_current_user
from models import User, Partner


# 创建路由
router = APIRouter(prefix="/api/projects", tags=["项目参与和团队组建"])


# ==================== Pydantic模型 ====================

class OpportunityCreateSchema(BaseModel):
    """创建创业机会"""
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str]
    detailed_info: str = Field(..., description='详细信息（购买后可见）')
    price: float = Field(99, ge=99, description='参与价格（最低99元）')
    min_participants: int = Field(1, ge=1)
    max_participants: int = Field(100, ge=1)
    team_building_fee: float = Field(1000, ge=0, description='团队组建费用（每人）')
    profit_ratio: float = Field(30, ge=0, le=100, description='利润分配比例（%）')
    commission_ratio: float = Field(10, ge=0, le=100, description='推荐佣金比例（%）')
    tags: Optional[str]
    requirements: Optional[str]
    benefits: Optional[str]
    risk_warning: Optional[str]


class OpportunityUpdateSchema(BaseModel):
    """更新创业机会"""
    title: Optional[str]
    description: Optional[str]
    detailed_info: Optional[str]
    price: Optional[float]
    status: Optional[str]
    tags: Optional[str]
    requirements: Optional[str]
    benefits: Optional[str]
    risk_warning: Optional[str]


class OpportunityResponse(BaseModel):
    """创业机会响应"""
    id: int
    code: str
    title: str
    description: Optional[str]
    detailed_info: Optional[str] = None  # 购买后可见
    price: float
    min_participants: int
    max_participants: int
    current_participants: int
    team_building_fee: float
    profit_ratio: float
    commission_ratio: float
    status: str
    tags: Optional[str]
    requirements: Optional[str]
    benefits: Optional[str]
    risk_warning: Optional[str]
    has_access: bool = False  # 当前用户是否有权限查看详情
    can_join: bool = True  # 是否可以加入


class PurchaseOpportunitySchema(BaseModel):
    """购买创业机会"""
    opportunity_id: int
    referrer_code: Optional[str] = None  # 推荐人代码


class TeamCreateSchema(BaseModel):
    """创建团队"""
    opportunity_id: int
    name: str = Field(..., min_length=1, max_length=100)
    max_members: int = Field(10, ge=1, le=100)
    fee_per_member: float = Field(1000, ge=0)
    description: Optional[str]
    goals: Optional[str]


class TeamMemberAddSchema(BaseModel):
    """添加团队成员"""
    partner_id: int
    role: str = TeamRole.MEMBER
    contribution: float = 0


class ExpertHireSchema(BaseModel):
    """聘请专家（资源库）"""
    expert_id: int
    role: Optional[str]
    hourly_fee: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    tasks: Optional[str]
    deliverables: Optional[str]


class ExpertEngageSchema(BaseModel):
    """聘请专家（自行组建）"""
    expert_name: str = Field(..., min_length=1, max_length=50)
    expertise: Optional[str]
    contact: Optional[str]
    hourly_rate: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    tasks: Optional[str]
    deliverables: Optional[str]


# ==================== 辅助函数 ====================

def generate_code(prefix: str, length: int = 10) -> str:
    """生成代码"""
    return prefix + secrets.token_hex(length)[:length].upper()


def get_partner_by_user(db: Session, user_id: int) -> Optional[Partner]:
    """根据用户ID获取合伙人"""
    return db.query(Partner).filter(Partner.user_id == user_id).first()


# ==================== 创业机会接口 ====================

@router.post("/opportunities", response_model=OpportunityResponse)
async def create_opportunity(
    opportunity: OpportunityCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建创业机会"""
    # 获取合伙人信息
    partner = get_partner_by_user(db, current_user.id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还不是合伙人，请先成为合伙人"
        )
    
    # 创建机会
    opp = Opportunity(
        code=generate_code("OPP"),
        title=opportunity.title,
        description=opportunity.description,
        detailed_info=opportunity.detailed_info,
        price=opportunity.price,
        min_participants=opportunity.min_participants,
        max_participants=opportunity.max_participants,
        team_building_fee=opportunity.team_building_fee,
        profit_ratio=opportunity.profit_ratio,
        commission_ratio=opportunity.commission_ratio,
        status=OpportunityStatus.DRAFT,
        creator_id=partner.id,
        tags=opportunity.tags,
        requirements=opportunity.requirements,
        benefits=opportunity.benefits,
        risk_warning=opportunity.risk_warning
    )
    
    db.add(opp)
    db.commit()
    db.refresh(opp)
    
    return OpportunityResponse(
        id=opp.id,
        code=opp.code,
        title=opp.title,
        description=opp.description,
        detailed_info=None,  # 创建者也不直接返回详情
        price=opp.price,
        min_participants=opp.min_participants,
        max_participants=opp.max_participants,
        current_participants=opp.current_participants,
        team_building_fee=opp.team_building_fee,
        profit_ratio=opp.profit_ratio,
        commission_ratio=opp.commission_ratio,
        status=opp.status.value,
        tags=opp.tags,
        requirements=opp.requirements,
        benefits=opp.benefits,
        risk_warning=opp.risk_warning,
        has_access=True,  # 创建者有权限
        can_join=False  # 创建者不能加入自己的机会
    )


@router.get("/opportunities", response_model=List[OpportunityResponse])
async def list_opportunities(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取创业机会列表"""
    query = db.query(Opportunity)
    
    # 只显示已发布的机会
    query = query.filter(Opportunity.status != OpportunityStatus.DRAFT)
    
    if status:
        query = query.filter(Opportunity.status == status)
    
    opportunities = query.all()
    partner = get_partner_by_user(db, current_user.id)
    
    result = []
    for opp in opportunities:
        # 检查用户是否已购买
        has_access = False
        can_join = True
        if partner:
            participation = db.query(OpportunityParticipation).filter(
                OpportunityParticipation.opportunity_id == opp.id,
                OpportunityParticipation.partner_id == partner.id
            ).first()
            has_access = participation is not None and participation.has_access
            can_join = participation is None
        
        result.append(OpportunityResponse(
            id=opp.id,
            code=opp.code,
            title=opp.title,
            description=opp.description,
            detailed_info=opp.detailed_info if has_access else None,
            price=opp.price,
            min_participants=opp.min_participants,
            max_participants=opp.max_participants,
            current_participants=opp.current_participants,
            team_building_fee=opp.team_building_fee,
            profit_ratio=opp.profit_ratio,
            commission_ratio=opp.commission_ratio,
            status=opp.status.value,
            tags=opp.tags,
            requirements=opp.requirements,
            benefits=opp.benefits,
            risk_warning=opp.risk_warning,
            has_access=has_access,
            can_join=can_join
        ))
    
    return result


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取创业机会详情"""
    opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"创业机会ID {opportunity_id} 不存在"
        )
    
    # 检查用户是否已购买
    partner = get_partner_by_user(db, current_user.id)
    has_access = False
    can_join = True
    if partner:
        participation = db.query(OpportunityParticipation).filter(
            OpportunityParticipation.opportunity_id == opp.id,
            OpportunityParticipation.partner_id == partner.id
        ).first()
        has_access = participation is not None and participation.has_access
        can_join = participation is None
    
    return OpportunityResponse(
        id=opp.id,
        code=opp.code,
        title=opp.title,
        description=opp.description,
        detailed_info=opp.detailed_info if has_access else None,
        price=opp.price,
        min_participants=opp.min_participants,
        max_participants=opp.max_participants,
        current_participants=opp.current_participants,
        team_building_fee=opp.team_building_fee,
        profit_ratio=opp.profit_ratio,
        commission_ratio=opp.commission_ratio,
        status=opp.status.value,
        tags=opp.tags,
        requirements=opp.requirements,
        benefits=opp.benefits,
        risk_warning=opp.risk_warning,
        has_access=has_access,
        can_join=can_join
    )


@router.post("/opportunities/purchase")
async def purchase_opportunity(
    purchase: PurchaseOpportunitySchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """购买创业机会（支付参与费用）"""
    # 获取合伙人信息
    partner = get_partner_by_user(db, current_user.id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还不是合伙人，请先成为合伙人"
        )
    
    # 获取机会信息
    opp = db.query(Opportunity).filter(Opportunity.id == purchase.opportunity_id).first()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"创业机会ID {purchase.opportunity_id} 不存在"
        )
    
    # 检查是否已购买
    existing = db.query(OpportunityParticipation).filter(
        OpportunityParticipation.opportunity_id == opp.id,
        OpportunityParticipation.partner_id == partner.id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您已经购买过这个创业机会"
        )
    
    # 检查机会状态
    if opp.status != OpportunityStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"该创业机会状态为 {opp.status.value}，无法购买"
        )
    
    # 检查参与人数
    if opp.current_participants >= opp.max_participants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该创业机会参与人数已满"
        )
    
    # 处理推荐人（如果有）
    referrer = None
    if purchase.referrer_code:
        referrer = db.query(Partner).filter(Partner.partner_code == purchase.referrer_code).first()
        if not referrer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"推荐人代码 {purchase.referrer_code} 不存在"
            )
        if referrer.id == partner.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能推荐自己"
            )
    
    # 创建参与记录
    participation = OpportunityParticipation(
        opportunity_id=opp.id,
        partner_id=partner.id,
        referrer_id=referrer.id if referrer else None,
        purchase_amount=opp.price,
        status='active',
        has_access=True  # 支付后立即获得访问权限
    )
    
    db.add(participation)
    
    # 更新机会的参与人数和营收
    opp.current_participants += 1
    opp.total_revenue += opp.price
    
    # 更新合伙人累计营收
    partner.total_revenue += opp.price
    
    # 处理推荐佣金（如果有推荐人）
    if referrer:
        commission_amount = opp.price * (opp.commission_ratio / 100)
        referrer.total_commission += commission_amount
        referrer.total_referrals += 1
        participation.commission_received = commission_amount
        
        # 可以在这里创建佣金记录
    
    db.commit()
    db.refresh(participation)
    
    return {
        "message": "购买成功！您现在可以查看项目详情",
        "participation_id": participation.id,
        "has_access": True,
        "purchase_amount": opp.price
    }


# ==================== 团队组建接口 ====================

@router.post("/teams")
async def create_team(
    team: TeamCreateSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """创建团队"""
    # 获取合伙人信息
    partner = get_partner_by_user(db, current_user.id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还不是合伙人，请先成为合伙人"
        )
    
    # 检查是否已购买该机会
    participation = db.query(OpportunityParticipation).filter(
        OpportunityParticipation.opportunity_id == team.opportunity_id,
        OpportunityParticipation.partner_id == partner.id
    ).first()
    if not participation or not participation.has_access:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您需要先购买该创业机会才能创建团队"
        )
    
    # 创建团队
    new_team = Team(
        code=generate_code("TM"),
        name=team.name,
        opportunity_id=team.opportunity_id,
        leader_id=partner.id,
        max_members=team.max_members,
        fee_per_member=team.fee_per_member,
        description=team.description,
        goals=team.goals,
        current_members=1,  # 团队长自己算一个
        total_fee=team.fee_per_member  # 团队长支付自己的费用
    )
    
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    
    # 创建团队成员记录（团队长）
    team_member = TeamPartnerMember(
        team_id=new_team.id,
        partner_id=partner.id,
        role=TeamRole.LEADER,
        fee_paid=team.fee_per_member,
        status='active'
    )
    
    db.add(team_member)
    db.commit()
    
    return {
        "message": "团队创建成功",
        "team_id": new_team.id,
        "team_code": new_team.code,
        "name": new_team.name,
        "current_members": new_team.current_members,
        "max_members": new_team.max_members,
        "fee_per_member": new_team.fee_per_member
    }


@router.post("/teams/{team_id}/members")
async def add_team_member(
    team_id: int,
    member: TeamMemberAddSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """添加团队成员"""
    # 获取合伙人信息
    partner = get_partner_by_user(db, current_user.id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还不是合伙人，请先成为合伙人"
        )
    
    # 获取团队信息
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"团队ID {team_id} 不存在"
        )
    
    # 检查是否是团队长
    if team.leader_id != partner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队长才能添加成员"
        )
    
    # 检查是否已满员
    if team.current_members >= team.max_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="团队已满员"
        )
    
    # 检查被添加的合伙人是否已加入
    existing = db.query(TeamPartnerMember).filter(
        TeamPartnerMember.team_id == team_id,
        TeamPartnerMember.partner_id == member.partner_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该合伙人已经是团队成员"
        )
    
    # 创建团队成员
    team_member = TeamPartnerMember(
        team_id=team_id,
        partner_id=member.partner_id,
        role=member.role,
        contribution=member.contribution,
        fee_paid=team.fee_per_member,
        status='active'
    )
    
    db.add(team_member)
    
    # 更新团队信息
    team.current_members += 1
    team.total_fee += team.fee_per_member
    
    db.commit()
    
    return {
        "message": "成员添加成功",
        "team_member_id": team_member.id,
        "current_members": team.current_members,
        "total_fee": team.total_fee
    }


# ==================== 专家聘请接口 ====================

@router.get("/experts", response_model=List[dict])
async def list_experts(
    expertise: Optional[str] = None,
    min_rating: Optional[float] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取资源库专家列表"""
    query = db.query(Expert).filter(Expert.availability == True)
    
    if expertise:
        query = query.filter(Expert.expertise.contains(expertise))
    
    if min_rating:
        query = query.filter(Expert.rating >= min_rating)
    
    experts = query.all()
    
    return [
        {
            "id": exp.id,
            "code": exp.code,
            "name": exp.name,
            "title": exp.title,
            "expertise": exp.expertise,
            "description": exp.description,
            "hourly_rate": exp.hourly_rate,
            "daily_rate": exp.daily_rate,
            "project_rate": exp.project_rate,
            "rating": exp.rating,
            "review_count": exp.review_count,
            "avatar": exp.avatar
        }
        for exp in experts
    ]


@router.post("/teams/{team_id}/experts/hire")
async def hire_expert(
    team_id: int,
    hire: ExpertHireSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """聘请资源库专家"""
    # 获取合伙人信息
    partner = get_partner_by_user(db, current_user.id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还不是合伙人，请先成为合伙人"
        )
    
    # 获取团队信息
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"团队ID {team_id} 不存在"
        )
    
    # 检查是否是团队长
    if team.leader_id != partner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队长才能聘请专家"
        )
    
    # 获取专家信息
    expert = db.query(Expert).filter(Expert.id == hire.expert_id).first()
    if not expert:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"专家ID {hire.expert_id} 不存在"
        )
    
    if not expert.availability:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="该专家当前不可用"
        )
    
    # 创建团队专家记录
    team_expert = TeamExpert(
        team_id=team_id,
        expert_id=expert.id,
        role=hire.role,
        hourly_fee=hire.hourly_fee or expert.hourly_rate,
        status='pending',
        start_date=hire.start_date,
        end_date=hire.end_date,
        tasks=hire.tasks,
        deliverables=hire.deliverables,
        hired_by=partner.id
    )
    
    db.add(team_expert)
    db.commit()
    db.refresh(team_expert)
    
    return {
        "message": "专家聘请请求已提交",
        "team_expert_id": team_expert.id,
        "expert_name": expert.name,
        "hourly_fee": team_expert.hourly_fee
    }


@router.post("/teams/{team_id}/experts/engage")
async def engage_expert(
    team_id: int,
    engage: ExpertEngageSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """自行组建专家"""
    # 获取合伙人信息
    partner = get_partner_by_user(db, current_user.id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还不是合伙人，请先成为合伙人"
        )
    
    # 获取团队信息
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"团队ID {team_id} 不存在"
        )
    
    # 检查是否是团队长
    if team.leader_id != partner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="只有团队长才能组建专家"
        )
    
    # 创建专家参与记录
    engagement = ExpertEngagement(
        team_id=team_id,
        expert_name=engage.expert_name,
        expertise=engage.expertise,
        contact=engage.contact,
        hourly_rate=engage.hourly_rate,
        status='pending',
        start_date=engage.start_date,
        end_date=engage.end_date,
        tasks=engage.tasks,
        deliverables=engage.deliverables,
        hired_by=partner.id
    )
    
    db.add(engagement)
    db.commit()
    db.refresh(engagement)
    
    return {
        "message": "专家组建成功",
        "engagement_id": engagement.id,
        "expert_name": engagement.expert_name,
        "hourly_rate": engagement.hourly_rate
    }


@router.get("/teams/{team_id}/members")
async def get_team_members(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取团队成员列表"""
    # 获取合伙人信息
    partner = get_partner_by_user(db, current_user.id)
    if not partner:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="您还不是合伙人，请先成为合伙人"
        )
    
    # 获取团队信息
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"团队ID {team_id} 不存在"
        )
    
    # 获取团队成员
    members = db.query(TeamPartnerMember).filter(TeamPartnerMember.team_id == team_id).all()
    
    # 获取资源库专家
    team_experts = db.query(TeamExpert).filter(TeamExpert.team_id == team_id).all()
    
    # 获取自行组建专家
    engagements = db.query(ExpertEngagement).filter(ExpertEngagement.team_id == team_id).all()
    
    return {
        "team": {
            "id": team.id,
            "name": team.name,
            "current_members": team.current_members,
            "max_members": team.max_members,
            "total_fee": team.total_fee,
            "fee_per_member": team.fee_per_member
        },
        "members": [
            {
                "id": m.id,
                "partner_id": m.partner_id,
                "role": m.role.value,
                "contribution": m.contribution,
                "fee_paid": m.fee_paid,
                "status": m.status
            }
            for m in members
        ],
        "experts": [
            {
                "id": e.id,
                "expert_id": e.expert_id,
                "expert_name": e.expert.name,
                "role": e.role,
                "hourly_fee": e.hourly_fee,
                "total_hours": e.total_hours,
                "total_fee": e.total_fee,
                "status": e.status
            }
            for e in team_experts
        ],
        "engagements": [
            {
                "id": e.id,
                "expert_name": e.expert_name,
                "expertise": e.expertise,
                "hourly_rate": e.hourly_rate,
                "total_hours": e.total_hours,
                "total_fee": e.total_fee,
                "status": e.status
            }
            for e in engagements
        ]
    }
