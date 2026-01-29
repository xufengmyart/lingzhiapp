"""
生态机制初始化脚本
初始化合伙人、会员级别、项目、推荐佣金、分红池等生态机制
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime, date, timedelta
from models import (
    Base, User, Role, Permission, MemberLevelConfig, Partner, Project,
    MemberLevel, PartnerStatus, ProjectStatus
)
from database_manager import DatabaseManager


def init_ecosystem():
    """初始化生态机制"""
    print("=" * 60)
    print("生态机制初始化脚本")
    print("=" * 60)
    
    # 创建数据库管理器
    db_manager = DatabaseManager()
    
    # 创建表
    print("\n[1/6] 创建数据库表...")
    db_manager.create_tables()
    
    # 以许锋身份登录
    print("\n[2/6] 以许锋身份登录...")
    login_result = db_manager.login_as_xufeng()
    print(f"      ✓ {login_result['message']}")
    
    if not login_result['success']:
        print("      ✗ 登录失败，请检查数据库")
        return
    
    # 初始化会员级别
    print("\n[3/6] 初始化会员级别配置...")
    levels_result = db_manager.init_member_levels()
    if levels_result['success']:
        print(f"      ✓ {levels_result['message']}")
        
        # 显示会员级别
        levels = db_manager.get_member_levels()
        print("\n      会员级别配置：")
        for level in levels:
            print(f"        - {level['name']}")
            print(f"          最低营收: {level['min_revenue']}元")
            print(f"          最低推荐: {level['min_referrals']}人")
            print(f"          分红股权: {level['dividend_ratio']}%")
            print(f"          佣金比例: {level['commission_ratio']}%")
            print(f"          权益: {level['benefits']}")
    else:
        print(f"      ! {levels_result['message']}")
    
    # 创建示例合伙人
    print("\n[4/6] 创建示例合伙人...")
    session = db_manager.get_session()
    try:
        # 获取用户列表
        users = session.query(User).all()
        
        created_partners = []
        for user in users[:5]:  # 为前5个用户创建合伙人
            result = db_manager.create_partner(
                user_id=user.id,
                member_level=MemberLevel.ORDINARY,
                status=PartnerStatus.ACTIVE,
                notes=f"{user.name}的合伙人账号"
            )
            if result['success']:
                created_partners.append(result['partner'])
                print(f"      ✓ 创建合伙人: {result['partner']['partner_code']} ({user.name})")
        
        # 更新其中一个为专家会员
        if len(created_partners) >= 2:
            partner = session.query(Partner).filter(Partner.id == created_partners[0]['id']).first()
            partner.member_level = MemberLevel.EXPERT
            partner.dividend_equity = 0.1  # 0.1%分红股权
            partner.total_revenue = 60000  # 满足专家会员要求
            partner.total_referrals = 25
            partner.level_up_at = datetime.now()
            session.commit()
            print(f"      ✓ 升级{partner.partner_code}为专家会员（0.1%分红股权）")
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"      ✗ 创建合伙人失败: {str(e)}")
    finally:
        session.close()
    
    # 创建示例项目
    print("\n[5/6] 创建示例项目...")
    session = db_manager.get_session()
    try:
        partners = session.query(Partner).filter(Partner.status == PartnerStatus.ACTIVE).all()
        
        if partners:
            partner = partners[0]
            
            projects_data = [
                {
                    "name": "中视频文化项目",
                    "description": "通过中视频传播西安文化，吸引年轻用户参与",
                    "status": ProjectStatus.ONGOING,
                    "total_investment": 50000,
                    "profit_ratio": 30,
                    "commission_ratio": 10,
                    "start_date": datetime.now() - timedelta(days=30),
                    "end_date": datetime.now() + timedelta(days=90)
                },
                {
                    "name": "西安美学侦探计划",
                    "description": "探索西安城市美学，发现隐藏的文化瑰宝",
                    "status": ProjectStatus.ONGOING,
                    "total_investment": 80000,
                    "profit_ratio": 35,
                    "commission_ratio": 12,
                    "start_date": datetime.now() - timedelta(days=15),
                    "end_date": datetime.now() + timedelta(days=60)
                },
                {
                    "name": "数字艺术墙项目",
                    "description": "为企业打造数字化艺术展示墙，提升品牌形象",
                    "status": ProjectStatus.DRAFT,
                    "total_investment": 120000,
                    "profit_ratio": 40,
                    "commission_ratio": 15,
                    "start_date": None,
                    "end_date": None
                }
            ]
            
            for project_data in projects_data:
                result = db_manager.create_project(
                    name=project_data["name"],
                    partner_id=partner.id,
                    **project_data
                )
                if result['success']:
                    print(f"      ✓ 创建项目: {result['project']['code']} - {project_data['name']}")
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"      ✗ 创建项目失败: {str(e)}")
    finally:
        session.close()
    
    # 创建示例推荐记录
    print("\n[6/6] 创建示例推荐记录...")
    session = db_manager.get_session()
    try:
        partners = session.query(Partner).all()
        projects = session.query(Project).filter(Project.status == ProjectStatus.ONGOING).all()
        
        if len(partners) >= 2 and projects:
            # 创建5条推荐记录
            for i in range(5):
                referrer = partners[0]  # 推荐人
                referee = partners[1]   # 被推荐人
                project = projects[i % len(projects)]  # 项目
                
                result = db_manager.create_referral(
                    referrer_id=referrer.id,
                    referee_id=referee.id,
                    project_id=project.id,
                    opportunity_id=f"OPP{datetime.now().strftime('%Y%m%d%H%M%S')}{i}",
                    opportunity_name=f"{project.name}-创业机会{i+1}",
                    amount=1000 + i * 200,  # 1000-1800元
                    source="share"
                )
                
                if result['success']:
                    print(f"      ✓ 创建推荐: {result['referral']['commission_amount']}元佣金")
                    
                    # 确认前3条推荐
                    if i < 3:
                        confirm_result = db_manager.confirm_referral(result['referral']['id'])
                        if confirm_result['success']:
                            print(f"        ✓ 已确认并生成佣金")
        
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"      ✗ 创建推荐记录失败: {str(e)}")
    finally:
        session.close()
    
    # 创建分红池
    print("\n[7/7] 创建分红池...")
    period = datetime.now().strftime("%Y-%m")
    pool_result = db_manager.create_dividend_pool(period)
    if pool_result['success']:
        print(f"      ✓ {pool_result['message']}")
        print(f"        总佣金: {pool_result['pool']['total_commission']}元")
        print(f"        分红池: {pool_result['pool']['pool_amount']}元 (5%)")
        print(f"        总股权: {pool_result['pool']['total_equity']}%")
    else:
        print(f"      ! {pool_result['message']}")
    
    # 显示生态汇总
    print("\n" + "=" * 60)
    print("生态机制初始化完成")
    print("=" * 60)
    
    summary = db_manager.get_ecosystem_summary()
    if summary['success']:
        print("\n生态机制汇总：")
        print(f"  合伙人总数: {summary['summary']['partners']['total']}")
        print(f"  活跃合伙人: {summary['summary']['partners']['active']}")
        print(f"  专家会员: {summary['summary']['partners']['expert']}")
        print(f"  项目总数: {summary['summary']['projects']['total']}")
        print(f"  进行中项目: {summary['summary']['projects']['ongoing']}")
        print(f"  推荐总数: {summary['summary']['referrals']['total']}")
        print(f"  已确认推荐: {summary['summary']['referrals']['confirmed']}")
        print(f"  佣金总数: {summary['summary']['commissions']['total']}")
        print(f"  待支付佣金: {summary['summary']['commissions']['pending']}")
        print(f"  佣金总额: {summary['summary']['commissions']['total_amount']}元")
        print(f"  分红池数: {summary['summary']['dividends']['total_pools']}")
        print(f"  活跃分红池: {summary['summary']['dividends']['active_pools']}")
        print(f"  已分配分红: {summary['summary']['dividends']['total_distributed']}元")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        init_ecosystem()
        print("\n✓ 生态机制初始化成功！")
    except Exception as e:
        print(f"\n✗ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
