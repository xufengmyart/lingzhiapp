"""
生态机制API接口
提供合伙人、项目、推荐、佣金、分红池等生态机制的管理接口
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date
from sqlalchemy.orm import Session

from models import (
    Partner, Project, ProjectParticipation, Referral, Commission,
    DividendPool, Dividend, MemberLevelConfig,
    MemberLevel, PartnerStatus, ProjectStatus, ReferralStatus
)
from database_manager import DatabaseManager
from api import get_db, get_current_user, require_permission
from models import User


# 创建路由
router = APIRouter(prefix="/api/ecosystem", tags=["生态机制"])

# 获取数据库管理器实例
db_manager = DatabaseManager()


# ==================== Pydantic模型 ====================

class MemberLevelConfigSchema(BaseModel):
    """会员级别配置"""
    level: str
    name: str
    description: Optional[str]
    min_revenue: float
    min_referrals: int
    dividend_ratio: float
    commission_ratio: float
    benefits: Optional[str]


class PartnerCreateSchema(BaseModel):
    """创建合伙人"""
    user_id: int
    member_level: str = MemberLevel.ORDINARY
    bank_account: Optional[str]
    bank_name: Optional[str]
    account_holder: Optional[str]
    notes: Optional[str]


class PartnerUpdateSchema(BaseModel):
    """更新合伙人"""
    member_level: Optional[str]
    status: Optional[str]
    bank_account: Optional[str]
    bank_name: Optional[str]
    account_holder: Optional[str]
    notes: Optional[str]


class PartnerSchema(BaseModel):
    """合伙人"""
    id: int
    partner_code: str
    user_id: int
    member_level: str
    status: str
    dividend_equity: float
    total_revenue: float
    total_commission: float
    total_referrals: int
    bank_account: Optional[str]
    joined_at: datetime


class ProjectCreateSchema(BaseModel):
    """创建项目"""
    name: str
    partner_id: int
    description: Optional[str]
    status: str = ProjectStatus.DRAFT
    total_investment: float = 0
    profit_ratio: float = 30
    commission_ratio: float = 10
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    notes: Optional[str]


class ProjectUpdateSchema(BaseModel):
    """更新项目"""
    name: Optional[str]
    description: Optional[str]
    status: Optional[str]
    total_investment: Optional[float]
    total_revenue: Optional[float]
    profit_ratio: Optional[float]
    commission_ratio: Optional[float]
    start_date: Optional[datetime]
    end_date: Optional[datetime]
    notes: Optional[str]


class ProjectSchema(BaseModel):
    """项目"""
    id: int
    code: str
    name: str
    partner_id: int
    status: str
    total_investment: float
    total_revenue: float
    profit: float
    profit_ratio: float
    commission_ratio: float
    participant_count: int
    start_date: Optional[datetime]
    end_date: Optional[datetime]


class ReferralCreateSchema(BaseModel):
    """创建推荐"""
    referrer_id: int
    referee_id: int
    project_id: int
    opportunity_id: str
    opportunity_name: str
    amount: float
    source: str = "share"
    notes: Optional[str]


class ReferralUpdateSchema(BaseModel):
    """更新推荐"""
    status: Optional[str]
    notes: Optional[str]


class ReferralSchema(BaseModel):
    """推荐"""
    id: int
    referrer_id: int
    referee_id: int
    project_id: int
    opportunity_id: str
    opportunity_name: str
    amount: float
    commission_ratio: float
    commission_amount: float
    status: str
    source: str
    created_at: datetime


class CommissionUpdateSchema(BaseModel):
    """更新佣金"""
    status: Optional[str]
    notes: Optional[str]


class CommissionSchema(BaseModel):
    """佣金"""
    id: int
    partner_id: int
    referral_id: Optional[int]
    amount: float
    ratio: float
    status: str
    source: str
    period: str
    created_at: datetime


class DividendPoolCreateSchema(BaseModel):
    """创建分红池"""
    period: str


class DividendPoolSchema(BaseModel):
    """分红池"""
    id: int
    name: str
    period: str
    total_commission: float
    pool_amount: float
    total_equity: float
    distributed_amount: float
    remaining_amount: float
    status: str
    calculation_date: Optional[datetime]
    distribution_date: Optional[datetime]


class DividendSchema(BaseModel):
    """分红"""
    id: int
    pool_id: int
    partner_id: int
    equity: float
    pool_amount: float
    dividend_amount: float
    status: str
    period: str


# ==================== 会员级别接口 ====================

@router.get("/member-levels", response_model=List[MemberLevelConfigSchema])
async def get_member_levels(
    current_user: User = Depends(get_current_user)
):
    """
    获取所有会员级别配置
    
    权限要求: ecosystem:view
    """
    require_permission(current_user, "ecosystem:view")
    
    try:
        levels = db_manager.get_member_levels()
        return [MemberLevelConfigSchema(**level) for level in levels]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会员级别失败: {str(e)}")


@router.post("/member-levels/init")
async def init_member_levels(
    current_user: User = Depends(get_current_user)
):
    """
    初始化会员级别配置
    
    权限要求: ecosystem:manage
    """
    require_permission(current_user, "ecosystem:manage")
    
    try:
        result = db_manager.init_member_levels()
        return {"success": result['success'], "message": result['message']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"初始化会员级别失败: {str(e)}")


# ==================== 合伙人接口 ====================

@router.post("/partners", response_model=PartnerSchema)
async def create_partner(
    partner_data: PartnerCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    创建合伙人
    
    权限要求: partner:create
    """
    require_permission(current_user, "partner:create")
    
    try:
        result = db_manager.create_partner(**partner_data.dict())
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        
        partner = db.query(Partner).filter(Partner.id == result['partner']['id']).first()
        return PartnerSchema.from_orm(partner)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建合伙人失败: {str(e)}")


@router.get("/partners", response_model=List[PartnerSchema])
async def get_partners(
    status: Optional[str] = None,
    member_level: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取合伙人列表
    
    权限要求: partner:view
    """
    require_permission(current_user, "partner:view")
    
    db = get_db()
    try:
        query = db.query(Partner)
        
        if status:
            query = query.filter(Partner.status == PartnerStatus(status))
        if member_level:
            query = query.filter(Partner.member_level == MemberLevel(member_level))
        
        partners = query.order_by(Partner.created_at.desc()).all()
        return [PartnerSchema.from_orm(p) for p in partners]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取合伙人列表失败: {str(e)}")


@router.get("/partners/{partner_id}", response_model=PartnerSchema)
async def get_partner(
    partner_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    获取合伙人详情
    
    权限要求: partner:view
    """
    require_permission(current_user, "partner:view")
    
    db = get_db()
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            raise HTTPException(status_code=404, detail="合伙人不存在")
        return PartnerSchema.from_orm(partner)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取合伙人详情失败: {str(e)}")


@router.put("/partners/{partner_id}")
async def update_partner(
    partner_id: int,
    partner_data: PartnerUpdateSchema,
    current_user: User = Depends(get_current_user)
):
    """
    更新合伙人信息
    
    权限要求: partner:modify
    """
    require_permission(current_user, "partner:modify")
    
    db = get_db()
    try:
        partner = db.query(Partner).filter(Partner.id == partner_id).first()
        if not partner:
            raise HTTPException(status_code=404, detail="合伙人不存在")
        
        update_data = partner_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(partner, key, value)
        
        partner.updated_at = datetime.now()
        db.commit()
        
        return {"success": True, "message": "更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新合伙人失败: {str(e)}")


# ==================== 项目接口 ====================

@router.post("/projects", response_model=ProjectSchema)
async def create_project(
    project_data: ProjectCreateSchema,
    current_user: User = Depends(get_current_user)
):
    """
    创建项目
    
    权限要求: project:create
    """
    require_permission(current_user, "project:create")
    
    try:
        result = db_manager.create_project(**project_data.dict())
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        
        db = get_db()
        project = db.query(Project).filter(Project.id == result['project']['id']).first()
        return ProjectSchema.from_orm(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建项目失败: {str(e)}")


@router.get("/projects", response_model=List[ProjectSchema])
async def get_projects(
    status: Optional[str] = None,
    partner_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取项目列表
    
    权限要求: project:view
    """
    require_permission(current_user, "project:view")
    
    db = get_db()
    try:
        query = db.query(Project)
        
        if status:
            query = query.filter(Project.status == ProjectStatus(status))
        if partner_id:
            query = query.filter(Project.partner_id == partner_id)
        
        projects = query.order_by(Project.created_at.desc()).all()
        return [ProjectSchema.from_orm(p) for p in projects]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目列表失败: {str(e)}")


@router.get("/projects/{project_id}", response_model=ProjectSchema)
async def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    获取项目详情
    
    权限要求: project:view
    """
    require_permission(current_user, "project:view")
    
    db = get_db()
    try:
        project = db.query(Project).filter(Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="项目不存在")
        return ProjectSchema.from_orm(project)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目详情失败: {str(e)}")


# ==================== 推荐接口 ====================

@router.post("/referrals", response_model=ReferralSchema)
async def create_referral(
    referral_data: ReferralCreateSchema,
    current_user: User = Depends(get_current_user)
):
    """
    创建推荐记录
    
    权限要求: referral:create
    """
    require_permission(current_user, "referral:create")
    
    try:
        result = db_manager.create_referral(**referral_data.dict())
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        
        db = get_db()
        referral = db.query(Referral).filter(Referral.id == result['referral']['id']).first()
        return ReferralSchema.from_orm(referral)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建推荐记录失败: {str(e)}")


@router.get("/referrals", response_model=List[ReferralSchema])
async def get_referrals(
    status: Optional[str] = None,
    referrer_id: Optional[int] = None,
    project_id: Optional[int] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取推荐记录列表
    
    权限要求: referral:view
    """
    require_permission(current_user, "referral:view")
    
    db = get_db()
    try:
        query = db.query(Referral)
        
        if status:
            query = query.filter(Referral.status == ReferralStatus(status))
        if referrer_id:
            query = query.filter(Referral.referrer_id == referrer_id)
        if project_id:
            query = query.filter(Referral.project_id == project_id)
        
        referrals = query.order_by(Referral.created_at.desc()).all()
        return [ReferralSchema.from_orm(r) for r in referrals]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐记录列表失败: {str(e)}")


@router.post("/referrals/{referral_id}/confirm")
async def confirm_referral(
    referral_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    确认推荐并生成佣金
    
    权限要求: referral:confirm
    """
    require_permission(current_user, "referral:confirm")
    
    try:
        result = db_manager.confirm_referral(referral_id)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"确认推荐失败: {str(e)}")


# ==================== 佣金接口 ====================

@router.get("/commissions", response_model=List[CommissionSchema])
async def get_commissions(
    status: Optional[str] = None,
    partner_id: Optional[int] = None,
    period: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取佣金列表
    
    权限要求: commission:view
    """
    require_permission(current_user, "commission:view")
    
    db = get_db()
    try:
        query = db.query(Commission)
        
        if status:
            query = query.filter(Commission.status == status)
        if partner_id:
            query = query.filter(Commission.partner_id == partner_id)
        if period:
            query = query.filter(Commission.period == period)
        
        commissions = query.order_by(Commission.created_at.desc()).all()
        return [CommissionSchema.from_orm(c) for c in commissions]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取佣金列表失败: {str(e)}")


@router.put("/commissions/{commission_id}")
async def update_commission(
    commission_id: int,
    commission_data: CommissionUpdateSchema,
    current_user: User = Depends(get_current_user)
):
    """
    更新佣金状态（如支付）
    
    权限要求: commission:modify
    """
    require_permission(current_user, "commission:modify")
    
    db = get_db()
    try:
        commission = db.query(Commission).filter(Commission.id == commission_id).first()
        if not commission:
            raise HTTPException(status_code=404, detail="佣金记录不存在")
        
        update_data = commission_data.dict(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(commission, key, value)
        
        if commission.status == "paid":
            commission.paid_at = datetime.now()
        
        commission.updated_at = datetime.now()
        db.commit()
        
        return {"success": True, "message": "更新成功"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"更新佣金失败: {str(e)}")


# ==================== 分红池接口 ====================

@router.post("/dividend-pools", response_model=DividendPoolSchema)
async def create_dividend_pool(
    pool_data: DividendPoolCreateSchema,
    current_user: User = Depends(get_current_user)
):
    """
    创建分红池
    
    权限要求: dividend:create_pool
    """
    require_permission(current_user, "dividend:create_pool")
    
    try:
        result = db_manager.create_dividend_pool(pool_data.period)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        
        db = get_db()
        pool = db.query(DividendPool).filter(DividendPool.id == result['pool']['id']).first()
        return DividendPoolSchema.from_orm(pool)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建分红池失败: {str(e)}")


@router.get("/dividend-pools", response_model=List[DividendPoolSchema])
async def get_dividend_pools(
    status: Optional[str] = None,
    period: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取分红池列表
    
    权限要求: dividend:view
    """
    require_permission(current_user, "dividend:view")
    
    db = get_db()
    try:
        query = db.query(DividendPool)
        
        if status:
            query = query.filter(DividendPool.status == status)
        if period:
            query = query.filter(DividendPool.period == period)
        
        pools = query.order_by(DividendPool.created_at.desc()).all()
        return [DividendPoolSchema.from_orm(p) for p in pools]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分红池列表失败: {str(e)}")


@router.post("/dividend-pools/{pool_id}/distribute")
async def distribute_dividends(
    pool_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    分配分红
    
    权限要求: dividend:distribute
    """
    require_permission(current_user, "dividend:distribute")
    
    try:
        result = db_manager.distribute_dividends(pool_id)
        if not result['success']:
            raise HTTPException(status_code=400, detail=result['message'])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分配分红失败: {str(e)}")


@router.get("/dividends", response_model=List[DividendSchema])
async def get_dividends(
    pool_id: Optional[int] = None,
    partner_id: Optional[int] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """
    获取分红记录列表
    
    权限要求: dividend:view
    """
    require_permission(current_user, "dividend:view")
    
    db = get_db()
    try:
        query = db.query(Dividend)
        
        if pool_id:
            query = query.filter(Dividend.pool_id == pool_id)
        if partner_id:
            query = query.filter(Dividend.partner_id == partner_id)
        if status:
            query = query.filter(Dividend.status == status)
        
        dividends = query.order_by(Dividend.created_at.desc()).all()
        return [DividendSchema.from_orm(d) for d in dividends]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分红记录列表失败: {str(e)}")


# ==================== 综合查询接口 ====================

@router.get("/summary")
async def get_ecosystem_summary(
    current_user: User = Depends(get_current_user)
):
    """
    获取生态机制汇总信息
    
    权限要求: ecosystem:view
    """
    require_permission(current_user, "ecosystem:view")
    
    try:
        summary = db_manager.get_ecosystem_summary()
        return summary
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取汇总信息失败: {str(e)}")
