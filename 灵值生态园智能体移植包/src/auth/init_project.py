"""
项目参与和团队组建功能的初始化脚本
初始化资源库专家数据
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import secrets

from models_project import Expert
from models import Base

DATABASE_URL = "sqlite:///./auth.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def generate_code(prefix: str, length: int = 10) -> str:
    """生成代码"""
    return prefix + secrets.token_hex(length)[:length].upper()


def init_project_tables():
    """初始化项目相关表"""
    Base.metadata.create_all(bind=engine)
    print("✓ 项目相关表初始化完成")


def seed_experts():
    """填充资源库专家数据"""
    db = SessionLocal()

    try:
        # 检查是否已有数据
        if db.query(Expert).count() > 0:
            print("资源库专家数据已存在，跳过初始化")
            return

        print("开始填充资源库专家数据...")

        experts_data = [
            {
                "name": "张明",
                "title": "品牌营销专家",
                "expertise": "品牌策划,市场营销,数字营销,内容营销",
                "description": "拥有15年品牌营销经验，曾服务多家知名企业，擅长品牌定位和市场推广策略。",
                "hourly_rate": 500,
                "daily_rate": 3000,
                "project_rate": 50000,
                "rating": 4.8,
                "review_count": 120,
                "contact_info": "zhangming@example.com",
                "certifications": "品牌策划师,数字营销师",
                "portfolio": "{'projects': 50, 'brands': 30}"
            },
            {
                "name": "李华",
                "title": "产品经理",
                "expertise": "产品规划,用户研究,数据分析,项目管理",
                "description": "资深产品经理，擅长从0到1打造爆款产品，具有丰富的互联网产品经验。",
                "hourly_rate": 600,
                "daily_rate": 3500,
                "project_rate": 60000,
                "rating": 4.9,
                "review_count": 85,
                "contact_info": "lihua@example.com",
                "certifications": "PMP,高级产品经理",
                "portfolio": "{'products': 20, 'users': '100万+'}"
            },
            {
                "name": "王强",
                "title": "技术架构师",
                "expertise": "系统架构,云计算,微服务,数据库设计",
                "description": "资深技术架构师，精通各种技术栈，擅长高并发系统设计和优化。",
                "hourly_rate": 700,
                "daily_rate": 4000,
                "project_rate": 80000,
                "rating": 4.7,
                "review_count": 95,
                "contact_info": "wangqiang@example.com",
                "certifications": "AWS认证,阿里云认证",
                "portfolio": "{'projects': 30, 'concurrent_users': '1000万+'}"
            },
            {
                "name": "赵丽",
                "title": "UI/UX设计师",
                "expertise": "用户界面设计,用户体验设计,交互设计,视觉设计",
                "description": "优秀的设计师，专注于打造美观易用的产品界面，具有敏锐的设计感知力。",
                "hourly_rate": 450,
                "daily_rate": 2800,
                "project_rate": 45000,
                "rating": 4.8,
                "review_count": 110,
                "contact_info": "zhaoli@example.com",
                "certifications": "高级UI设计师,交互设计师",
                "portfolio": "{'apps': 40, 'websites': 60}"
            },
            {
                "name": "刘伟",
                "title": "运营专家",
                "expertise": "用户运营,内容运营,社群运营,活动运营",
                "description": "运营专家，擅长用户增长和社群运营，打造过多个千万级用户的社群。",
                "hourly_rate": 480,
                "daily_rate": 3000,
                "project_rate": 48000,
                "rating": 4.6,
                "review_count": 90,
                "contact_info": "liuwei@example.com",
                "certifications": "高级运营师,社群运营师",
                "portfolio": "{'communities': 20, 'users': '500万+'}"
            },
            {
                "name": "陈静",
                "title": "财务顾问",
                "expertise": "财务管理,投资分析,税务筹划,风险控制",
                "description": "资深财务顾问，具有丰富的企业财务管理经验，擅长投资分析和风险控制。",
                "hourly_rate": 550,
                "daily_rate": 3200,
                "project_rate": 55000,
                "rating": 4.9,
                "review_count": 75,
                "contact_info": "chenjing@example.com",
                "certifications": "CPA,注册税务师",
                "portfolio": "{'companies': 25, 'assets': '10亿+'}"
            },
            {
                "name": "杨帆",
                "title": "法务专家",
                "expertise": "合同法,公司法,知识产权法,劳动法",
                "description": "资深法务专家，熟悉各类商业法律，擅长合同起草和知识产权保护。",
                "hourly_rate": 650,
                "daily_rate": 3800,
                "project_rate": 70000,
                "rating": 4.7,
                "review_count": 68,
                "contact_info": "yangfan@example.com",
                "certifications": "律师资格证,知识产权代理人",
                "portfolio": "{'cases': 100+, 'contracts': 500+}"
            },
            {
                "name": "黄磊",
                "title": "品牌文化顾问",
                "expertise": "文化研究,品牌文化,内容创作,IP打造",
                "description": "品牌文化专家，深谙传统文化与现代品牌结合之道，擅长打造具有文化内涵的品牌。",
                "hourly_rate": 520,
                "daily_rate": 3100,
                "project_rate": 52000,
                "rating": 4.8,
                "review_count": 88,
                "contact_info": "huanglei@example.com",
                "certifications": "品牌策划师,文化创意师",
                "portfolio": "{'brands': 35, 'IPs': 20}"
            },
            {
                "name": "吴敏",
                "title": "视频制作专家",
                "expertise": "视频策划,拍摄剪辑,特效制作,短视频运营",
                "description": "视频制作专家，精通各类视频制作工具，擅长打造爆款短视频和宣传片。",
                "hourly_rate": 400,
                "daily_rate": 2500,
                "project_rate": 40000,
                "rating": 4.6,
                "review_count": 105,
                "contact_info": "wumin@example.com",
                "certifications": "视频剪辑师,短视频运营师",
                "portfolio": "{'videos': 200+, 'views': '1亿+'}"
            },
            {
                "name": "周涛",
                "title": "数据分析专家",
                "expertise": "数据挖掘,数据分析,机器学习,数据可视化",
                "description": "数据分析专家，精通各类数据分析工具，擅长从数据中挖掘商业价值。",
                "hourly_rate": 580,
                "daily_rate": 3400,
                "project_rate": 58000,
                "rating": 4.7,
                "review_count": 80,
                "contact_info": "zhoutao@example.com",
                "certifications": "数据分析师,机器学习工程师",
                "portfolio": "{'projects': 40, 'datasets': '100TB+'}"
            }
        ]

        experts = []
        for exp_data in experts_data:
            expert = Expert(
                code=generate_code("EXP"),
                **exp_data,
                availability=True
            )
            db.add(expert)
            experts.append(expert)
        
        db.commit()
        print(f"✓ 创建了 {len(experts)} 位资源库专家")

    except Exception as e:
        print(f"✗ 初始化专家数据失败: {str(e)}")
        db.rollback()
    finally:
        db.close()


def main():
    """主函数"""
    print("="*60)
    print("项目参与和团队组建功能初始化")
    print("="*60)
    
    # 初始化表
    init_project_tables()
    
    # 填充专家数据
    seed_experts()
    
    print("\n" + "="*60)
    print("✓ 初始化完成")
    print("="*60)
    print("\n新增功能：")
    print("1. 创业机会管理（最低参与定价99元）")
    print("2. 项目详情查看权限控制")
    print("3. 团队组建机制（每名成员1000元）")
    print("4. 资源库专家聘请")
    print("5. 自行组建专家")
    print("="*60)


if __name__ == "__main__":
    main()
