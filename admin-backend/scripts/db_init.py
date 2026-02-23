#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵值生态园 - 数据库初始化脚本
Database Initialization Script

Author: Coze Coding
Version: 1.0.0
"""

import os
import sys
from datetime import datetime
import logging

# 添加项目路径到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

from app import create_app
from app.extensions import db
from app.models import (
    Admin,
    RechargeTier,
    CompanyAccount,
    Agent,
    KnowledgeBase
)


def init_database():
    """初始化数据库"""
    logger.info("开始初始化数据库...")

    # 创建应用上下文
    app = create_app(os.getenv('FLASK_ENV', 'development'))

    with app.app_context():
        # 创建所有表
        db.create_all()
        logger.info("✅ 数据库表创建成功")

        # 初始化默认管理员账户
        admin = Admin.query.filter_by(username='admin').first()
        if not admin:
            admin = Admin(username='admin', role='super_admin')
            admin.set_password('admin123')  # 默认密码，首次登录后修改
            db.session.add(admin)
            db.session.commit()
            logger.info("✅ 默认管理员账户创建成功 (username: admin, password: admin123)")
        else:
            logger.info("ℹ️  管理员账户已存在")

        # 初始化充值档位
        init_recharge_tiers()

        # 初始化公司收款账户
        init_company_accounts()

        # 初始化默认智能体
        init_default_agents()

        # 初始化默认知识库
        init_default_knowledge_bases()

        logger.info("🎉 数据库初始化完成！")


def init_recharge_tiers():
    """初始化充值档位"""
    logger.info("初始化充值档位...")

    if RechargeTier.query.count() > 0:
        logger.info("ℹ️  充值档位已存在")
        return

    tiers = [
        {
            'name': '体验档',
            'description': '新用户体验套餐',
            'price': 9.90,
            'base_lingzhi': 100,
            'bonus_lingzhi': 0,
            'bonus_percentage': 0,
            'partner_level': 0,
            'benefits': '["基础对话权限", "每日10次对话"]',
            'status': 'active',
            'sort_order': 1
        },
        {
            'name': '入门档',
            'description': '适合轻度用户',
            'price': 29.90,
            'base_lingzhi': 300,
            'bonus_lingzhi': 50,
            'bonus_percentage': 17,
            'partner_level': 1,
            'benefits': '["基础对话权限", "每日50次对话", "优先客服"]',
            'status': 'active',
            'sort_order': 2
        },
        {
            'name': '标准档',
            'description': '适合一般用户',
            'price': 99.00,
            'base_lingzhi': 1000,
            'bonus_lingzhi': 200,
            'bonus_percentage': 20,
            'partner_level': 1,
            'benefits': '["基础对话权限", "每日200次对话", "优先客服", "专属客服"]',
            'status': 'active',
            'sort_order': 3
        },
        {
            'name': '高级档',
            'description': '适合重度用户',
            'price': 199.00,
            'base_lingzhi': 2000,
            'bonus_lingzhi': 500,
            'bonus_percentage': 25,
            'partner_level': 2,
            'benefits': '["基础对话权限", "每日500次对话", "优先客服", "专属客服", "高级智能体"]',
            'status': 'active',
            'sort_order': 4
        },
        {
            'name': '尊享档',
            'description': '尊享会员特权',
            'price': 499.00,
            'base_lingzhi': 5000,
            'bonus_lingzhi': 1500,
            'bonus_percentage': 30,
            'partner_level': 3,
            'benefits': '["基础对话权限", "每日1000次对话", "优先客服", "专属客服", "高级智能体", "私有知识库"]',
            'status': 'active',
            'sort_order': 5
        },
        {
            'name': '至尊档',
            'description': '至尊会员特权',
            'price': 999.00,
            'base_lingzhi': 10000,
            'bonus_lingzhi': 3500,
            'bonus_percentage': 35,
            'partner_level': 3,
            'benefits': '["基础对话权限", "每日5000次对话", "优先客服", "专属客服", "高级智能体", "私有知识库", "定制服务"]',
            'status': 'active',
            'sort_order': 6
        }
    ]

    for tier_data in tiers:
        tier = RechargeTier(**tier_data)
        db.session.add(tier)

    db.session.commit()
    logger.info(f"✅ 创建 {len(tiers)} 个充值档位")


def init_company_accounts():
    """初始化公司收款账户"""
    logger.info("初始化公司收款账户...")

    if CompanyAccount.query.count() > 0:
        logger.info("ℹ️  公司收款账户已存在")
        return

    # 从环境变量读取配置
    accounts = []
    if os.getenv('COMPANY_ACCOUNT_NAME'):
        accounts.append({
            'account_name': os.getenv('COMPANY_ACCOUNT_NAME', ''),
            'account_number': os.getenv('COMPANY_ACCOUNT_NUMBER', ''),
            'bank_name': os.getenv('COMPANY_BANK_NAME', ''),
            'bank_branch': os.getenv('COMPANY_BANK_BRANCH', ''),
            'company_name': os.getenv('COMPANY_NAME', ''),
            'company_credit_code': os.getenv('COMPANY_CREDIT_CODE', ''),
            'account_type': 'primary',
            'is_active': True,
            'sort_order': 1
        })

    for account_data in accounts:
        account = CompanyAccount(**account_data)
        db.session.add(account)

    db.session.commit()
    if accounts:
        logger.info(f"✅ 创建 {len(accounts)} 个公司收款账户")
    else:
        logger.warning("⚠️  未配置公司收款账户，请在 .env 文件中设置")


def init_default_agents():
    """初始化默认智能体"""
    logger.info("初始化默认智能体...")

    if Agent.query.count() > 0:
        logger.info("ℹ️  智能体已存在")
        return

    agents = [
        {
            'name': '通用助手',
            'description': '全能型智能助手，可以回答各类问题',
            'system_prompt': '你是一个友好的智能助手，可以帮助用户解答各种问题。请用简洁、准确的方式回答。',
            'model_config': '{"model": "doubao-seed-1-6-251015", "temperature": 0.7}',
            'tools': '[]',
            'status': 'active',
            'avatar_url': '/static/avatars/default_agent.png',
            'created_by': 1
        },
        {
            'name': '创意写作助手',
            'description': '擅长创意写作、文章创作',
            'system_prompt': '你是一个专业的创意写作助手，擅长创作各类文章、故事、诗歌等。请根据用户需求进行创作。',
            'model_config': '{"model": "doubao-seed-1-6-251015", "temperature": 0.8}',
            'tools': '[]',
            'status': 'active',
            'avatar_url': '/static/avatars/writing_agent.png',
            'created_by': 1
        },
        {
            'name': '代码助手',
            'description': '精通编程，可以帮助编写、调试代码',
            'system_prompt': '你是一个专业的代码助手，精通多种编程语言。可以帮助用户编写、调试、优化代码。',
            'model_config': '{"model": "doubao-seed-1-6-251015", "temperature": 0.5}',
            'tools': '[]',
            'status': 'active',
            'avatar_url': '/static/avatars/code_agent.png',
            'created_by': 1
        }
    ]

    for agent_data in agents:
        agent = Agent(**agent_data)
        db.session.add(agent)

    db.session.commit()
    logger.info(f"✅ 创建 {len(agents)} 个默认智能体")


def init_default_knowledge_bases():
    """初始化默认知识库"""
    logger.info("初始化默认知识库...")

    if KnowledgeBase.query.count() > 0:
        logger.info("ℹ️  知识库已存在")
        return

    kb = KnowledgeBase(
        name='灵值生态园帮助文档',
        description='灵值生态园平台的使用帮助和常见问题',
        vector_db_id='default_kb',
        document_count=0,
        created_by=1
    )
    db.session.add(kb)
    db.session.commit()
    logger.info("✅ 创建默认知识库")


def backup_database():
    """备份数据库"""
    logger.info("开始备份数据库...")

    app = create_app(os.getenv('FLASK_ENV', 'development'))

    with app.app_context():
        db_path = app.config['DATABASE_PATH']
        if os.path.exists(db_path):
            import shutil
            backup_dir = os.path.join(os.path.dirname(db_path), 'backups')
            os.makedirs(backup_dir, exist_ok=True)

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'lingzhi_ecosystem_backup_{timestamp}.db')
            shutil.copy2(db_path, backup_path)

            logger.info(f"✅ 数据库备份成功: {backup_path}")
        else:
            logger.warning("⚠️  数据库文件不存在")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='灵值生态园数据库管理工具')
    parser.add_argument('command', choices=['init', 'backup', 'reset'], help='操作命令')
    args = parser.parse_args()

    if args.command == 'init':
        init_database()
    elif args.command == 'backup':
        backup_database()
    elif args.command == 'reset':
        logger.warning("⚠️  重置数据库将删除所有数据！")
        confirm = input("确认重置数据库？(yes/no): ")
        if confirm.lower() == 'yes':
            app = create_app(os.getenv('FLASK_ENV', 'development'))
            with app.app_context():
                db.drop_all()
                logger.info("✅ 数据库表已删除")
                init_database()
        else:
            logger.info("❌ 取消重置操作")


if __name__ == '__main__':
    main()
