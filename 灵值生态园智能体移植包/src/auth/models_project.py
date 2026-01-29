"""
项目参与和团队组建模型扩展
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from models import Base


class OpportunityStatus(enum.Enum):
    """创业机会状态"""
    DRAFT = "draft"  # 草稿
    PUBLISHED = "published"  # 已发布
    ACTIVE = "active"  # 活跃
    CLOSED = "closed"  # 已关闭
    CANCELLED = "cancelled"  # 已取消


class TeamRole(enum.Enum):
    """团队角色"""
    LEADER = "leader"  # 团队长
    MEMBER = "member"  # 成员
    EXPERT = "expert"  # 专家
    MANAGER = "manager"  # 管理员


# ==================== 创业机会表 ====================

class Opportunity(Base):
    """创业机会表（项目机会）"""
    __tablename__ = 'opportunities'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment='机会代码')
    title = Column(String(200), nullable=False, comment='机会标题')
    description = Column(Text, comment='机会描述')
    detailed_info = Column(Text, comment='详细信息（购买后可见）')
    price = Column(Float, default=99, nullable=False, comment='参与价格（最低99元）')
    min_participants = Column(Integer, default=1, comment='最少参与人数')
    max_participants = Column(Integer, default=100, comment='最多参与人数')
    current_participants = Column(Integer, default=0, comment='当前参与人数')
    team_building_fee = Column(Float, default=1000, comment='团队组建费用（每人1000元）')
    profit_ratio = Column(Float, default=30, comment='利润分配比例（%）')
    commission_ratio = Column(Float, default=10, comment='推荐佣金比例（%）')
    status = Column(Enum(OpportunityStatus), default=OpportunityStatus.DRAFT, comment='状态')
    creator_id = Column(Integer, ForeignKey('partners.id'), comment='创建者ID')
    start_date = Column(DateTime, comment='开始日期')
    end_date = Column(DateTime, comment='结束日期')
    total_revenue = Column(Float, default=0, comment='总营收')
    tags = Column(String(200), comment='标签（逗号分隔）')
    requirements = Column(Text, comment='参与要求')
    benefits = Column(Text, comment='参与收益')
    risk_warning = Column(Text, comment='风险提示')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    creator = relationship('Partner')
    participations = relationship('OpportunityParticipation', back_populates='opportunity')
    teams = relationship('Team', back_populates='opportunity')

    def __repr__(self):
        return f"<Opportunity(id={self.id}, code='{self.code}', title='{self.title}', price={self.price})>"


class OpportunityParticipation(Base):
    """创业机会参与表"""
    __tablename__ = 'opportunity_participations'

    id = Column(Integer, primary_key=True, index=True)
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False, comment='机会ID')
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='合伙人ID')
    referrer_id = Column(Integer, ForeignKey('partners.id'), comment='推荐人ID')
    purchase_amount = Column(Float, nullable=False, comment='购买金额')
    status = Column(String(20), default='active', comment='状态：active/completed/cancelled/refunded')
    has_access = Column(Boolean, default=False, comment='是否有权限查看详情')
    viewed_at = Column(DateTime, comment='首次查看详情时间')
    profit_share = Column(Float, default=0, comment='利润分配金额')
    commission_received = Column(Float, default=0, comment='已接收佣金')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    opportunity = relationship('Opportunity', back_populates='participations')
    partner = relationship('Partner', foreign_keys=[partner_id])
    referrer = relationship('Partner', foreign_keys=[referrer_id])

    def __repr__(self):
        return f"<OpportunityParticipation(id={self.id}, opportunity_id={self.opportunity_id}, partner_id={self.partner_id})>"


# ==================== 资源库专家表 ====================

class Expert(Base):
    """资源库专家表"""
    __tablename__ = 'experts'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True, comment='专家代码')
    name = Column(String(50), nullable=False, comment='姓名')
    title = Column(String(100), comment='职称')
    expertise = Column(String(200), comment='专业领域（逗号分隔）')
    description = Column(Text, comment='专家介绍')
    hourly_rate = Column(Float, default=0, comment='时薪（元/小时）')
    daily_rate = Column(Float, default=0, comment='日薪（元/天）')
    project_rate = Column(Float, default=0, comment='项目费（元/项目）')
    availability = Column(Boolean, default=True, comment='是否可用')
    rating = Column(Float, default=0, comment='评分（0-5）')
    review_count = Column(Integer, default=0, comment='评价数量')
    contact_info = Column(String(100), comment='联系方式')
    avatar = Column(String(200), comment='头像URL')
    certifications = Column(Text, comment='资质认证（JSON）')
    portfolio = Column(Text, comment='作品集（JSON）')
    status = Column(String(20), default='active', comment='状态：active/inactive/suspended')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    team_experts = relationship('TeamExpert', back_populates='expert')

    def __repr__(self):
        return f"<Expert(id={self.id}, code='{self.code}', name='{self.name}', expertise='{self.expertise}')>"


# ==================== 团队相关表 ====================

class Team(Base):
    """团队表"""
    __tablename__ = 'teams'

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), unique=True, nullable=False, index=True, comment='团队代码')
    name = Column(String(100), nullable=False, comment='团队名称')
    opportunity_id = Column(Integer, ForeignKey('opportunities.id'), nullable=False, comment='关联机会ID')
    leader_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='团队长ID')
    max_members = Column(Integer, default=10, comment='最大成员数')
    current_members = Column(Integer, default=0, comment='当前成员数')
    total_fee = Column(Float, default=0, comment='总费用')
    fee_per_member = Column(Float, default=1000, comment='每人费用（1000元）')
    budget = Column(Float, default=0, comment='预算')
    spent = Column(Float, default=0, comment='已支出')
    description = Column(Text, comment='团队描述')
    goals = Column(Text, comment='团队目标')
    status = Column(String(20), default='forming', comment='状态：forming/active/completed/dissolved')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    started_at = Column(DateTime, comment='开始时间')
    completed_at = Column(DateTime, comment='完成时间')

    # 关系
    opportunity = relationship('Opportunity', back_populates='teams')
    leader = relationship('Partner')
    members = relationship('TeamPartnerMember', back_populates='team')
    team_experts = relationship('TeamExpert', back_populates='team')
    milestones = relationship('TeamMilestone', back_populates='team')

    def __repr__(self):
        return f"<Team(id={self.id}, code='{self.code}', name='{self.name}', members={self.current_members}/{self.max_members})>"


class TeamPartnerMember(Base):
    """团队成员表（合伙人）"""
    __tablename__ = 'team_partner_members'

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, comment='团队ID')
    partner_id = Column(Integer, ForeignKey('partners.id'), nullable=False, comment='合伙人ID')
    role = Column(Enum(TeamRole), default=TeamRole.MEMBER, comment='角色')
    contribution = Column(Float, default=0, comment='贡献值')
    fee_paid = Column(Float, default=0, comment='已支付费用')
    status = Column(String(20), default='active', comment='状态：active/inactive/removed')
    responsibilities = Column(Text, comment='职责描述')
    skills = Column(String(200), comment='技能（逗号分隔）')
    joined_at = Column(DateTime, default=datetime.now, comment='加入时间')
    left_at = Column(DateTime, comment='离开时间')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    team = relationship('Team', back_populates='members')
    partner = relationship('Partner')

    def __repr__(self):
        return f"<TeamPartnerMember(id={self.id}, team_id={self.team_id}, partner_id={self.partner_id}, role={self.role})>"


class TeamExpert(Base):
    """团队专家表（聘请的资源库专家）"""
    __tablename__ = 'team_experts'

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, comment='团队ID')
    expert_id = Column(Integer, ForeignKey('experts.id'), nullable=False, comment='专家ID')
    role = Column(String(50), comment='角色')
    hourly_fee = Column(Float, comment='时薪费用')
    total_hours = Column(Float, default=0, comment='总工时')
    total_fee = Column(Float, default=0, comment='总费用')
    status = Column(String(20), default='pending', comment='状态：pending/active/completed/cancelled')
    start_date = Column(DateTime, comment='开始日期')
    end_date = Column(DateTime, comment='结束日期')
    tasks = Column(Text, comment='任务描述')
    deliverables = Column(Text, comment='交付物')
    rating = Column(Float, comment='评分（0-5）')
    review = Column(Text, comment='评价')
    hired_by = Column(Integer, ForeignKey('partners.id'), comment='招聘人ID')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    hired_at = Column(DateTime, comment='雇佣时间')
    completed_at = Column(DateTime, comment='完成时间')

    # 关系
    team = relationship('Team', back_populates='team_experts')
    expert = relationship('Expert', back_populates='team_experts')
    hirer = relationship('Partner', foreign_keys=[hired_by])

    def __repr__(self):
        return f"<TeamExpert(id={self.id}, team_id={self.team_id}, expert_id={self.expert_id}, total_fee={self.total_fee})>"


class ExpertEngagement(Base):
    """专家参与记录表（自行组建的专家）"""
    __tablename__ = 'expert_engagements'

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, comment='团队ID')
    expert_name = Column(String(50), nullable=False, comment='专家姓名')
    expertise = Column(String(200), comment='专业领域')
    contact = Column(String(100), comment='联系方式')
    hourly_rate = Column(Float, comment='时薪')
    total_hours = Column(Float, default=0, comment='总工时')
    total_fee = Column(Float, default=0, comment='总费用')
    status = Column(String(20), default='pending', comment='状态：pending/active/completed/cancelled')
    source = Column(String(50), default='self', comment='来源：self/referral/platform')
    start_date = Column(DateTime, comment='开始日期')
    end_date = Column(DateTime, comment='结束日期')
    tasks = Column(Text, comment='任务描述')
    deliverables = Column(Text, comment='交付物')
    hired_by = Column(Integer, ForeignKey('partners.id'), comment='招聘人ID')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    hired_at = Column(DateTime, comment='雇佣时间')
    completed_at = Column(DateTime, comment='完成时间')

    # 关系
    team = relationship('Team')
    hirer = relationship('Partner', foreign_keys=[hired_by])

    def __repr__(self):
        return f"<ExpertEngagement(id={self.id}, team_id={self.team_id}, expert_name='{self.expert_name}', total_fee={self.total_fee})>"


class TeamMilestone(Base):
    """团队里程碑表"""
    __tablename__ = 'team_milestones'

    id = Column(Integer, primary_key=True, index=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False, comment='团队ID')
    title = Column(String(200), nullable=False, comment='里程碑标题')
    description = Column(Text, comment='描述')
    target_date = Column(DateTime, comment='目标日期')
    completed_date = Column(DateTime, comment='完成日期')
    status = Column(String(20), default='pending', comment='状态：pending/in_progress/completed/delayed')
    priority = Column(String(20), default='medium', comment='优先级：low/medium/high')
    assignee_id = Column(Integer, ForeignKey('partners.id'), comment='负责人ID')
    budget = Column(Float, default=0, comment='预算')
    actual_cost = Column(Float, default=0, comment='实际成本')
    deliverables = Column(Text, comment='交付物')
    notes = Column(Text, comment='备注')
    created_at = Column(DateTime, default=datetime.now, comment='创建时间')
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')

    # 关系
    team = relationship('Team', back_populates='milestones')
    assignee = relationship('Partner')

    def __repr__(self):
        return f"<TeamMilestone(id={self.id}, team_id={self.team_id}, title='{self.title}', status={self.status})>"
