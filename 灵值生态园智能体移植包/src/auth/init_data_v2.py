"""
权限管理系统的初始化数据脚本 v2.0
添加CEO角色、黄爱莉账号、访客管理功能
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base, User, Role, Permission, AuditLog
from datetime import datetime, timedelta
import bcrypt
import pyotp

DATABASE_URL = "sqlite:///./auth.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_database():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)
    print("数据库初始化完成")


def seed_default_data():
    """填充默认数据"""
    db = SessionLocal()

    try:
        # 检查是否已有数据
        if db.query(User).count() > 0:
            print("数据库已有数据，跳过初始化")
            return

        print("开始填充默认数据...")

        # 1. 创建权限
        permissions_data = [
            # 用户管理权限
            {"code": "user:create", "name": "创建用户", "module": "user_management", "description": "创建新用户"},
            {"code": "user:delete", "name": "删除用户", "module": "user_management", "description": "删除用户"},
            {"code": "user:modify", "name": "修改用户", "module": "user_management", "description": "修改用户信息"},
            {"code": "user:view", "name": "查看用户", "module": "user_management", "description": "查看用户信息"},
            {"code": "user:assign_role", "name": "分配角色", "module": "user_management", "description": "为用户分配角色"},
            {"code": "user:reset_password", "name": "重置密码", "module": "user_management", "description": "重置用户密码"},

            # 角色管理权限
            {"code": "role:create", "name": "创建角色", "module": "role_management", "description": "创建新角色"},
            {"code": "role:delete", "name": "删除角色", "module": "role_management", "description": "删除角色"},
            {"code": "role:modify", "name": "修改角色", "module": "role_management", "description": "修改角色信息"},
            {"code": "role:view", "name": "查看角色", "module": "role_management", "description": "查看角色信息"},
            {"code": "role:assign_permission", "name": "分配权限", "module": "role_management", "description": "为角色分配权限"},

            # 权限管理权限
            {"code": "permission:grant", "name": "授予权限", "module": "permission_management", "description": "授予权限"},
            {"code": "permission:revoke", "name": "撤销权限", "module": "permission_management", "description": "撤销权限"},
            {"code": "permission:view", "name": "查看权限", "module": "permission_management", "description": "查看权限信息"},
            {"code": "permission:modify", "name": "修改权限", "module": "permission_management", "description": "修改权限信息"},

            # 系统配置权限
            {"code": "system:modify_config", "name": "修改系统配置", "module": "system_config", "description": "修改系统配置"},
            {"code": "system:view_config", "name": "查看系统配置", "module": "system_config", "description": "查看系统配置"},

            # 数据管理权限
            {"code": "data:view", "name": "查看数据", "module": "data_management", "description": "查看数据"},
            {"code": "data:modify", "name": "修改数据", "module": "data_management", "description": "修改数据"},
            {"code": "data:delete", "name": "删除数据", "module": "data_management", "description": "删除数据"},
            {"code": "data:export", "name": "导出数据", "module": "data_management", "description": "导出数据"},

            # 审批管理权限
            {"code": "approval:submit", "name": "提交审批", "module": "approval_management", "description": "提交审批申请"},
            {"code": "approval:approve", "name": "审批通过", "module": "approval_management", "description": "审批通过"},
            {"code": "approval:view", "name": "查看审批", "module": "approval_management", "description": "查看审批信息"},

            # 财务管理权限
            {"code": "finance:view", "name": "查看财务", "module": "financial_management", "description": "查看财务信息"},
            {"code": "finance:modify", "name": "修改财务", "module": "financial_management", "description": "修改财务信息"},
            {"code": "finance:approve_budget", "name": "审批预算", "module": "financial_management", "description": "审批预算"},

            # 合同管理权限
            {"code": "contract:create", "name": "创建合同", "module": "contract_management", "description": "创建合同"},
            {"code": "contract:view", "name": "查看合同", "module": "contract_management", "description": "查看合同信息"},
            {"code": "contract:sign", "name": "签署合同", "module": "contract_management", "description": "签署合同"},

            # 产品管理权限
            {"code": "product:create", "name": "创建产品", "module": "product_management", "description": "创建产品"},
            {"code": "product:modify", "name": "修改产品", "module": "product_management", "description": "修改产品信息"},
            {"code": "product:view", "name": "查看产品", "module": "product_management", "description": "查看产品信息"},

            # 营销管理权限
            {"code": "marketing:create", "name": "创建营销", "module": "marketing_management", "description": "创建营销活动"},
            {"code": "marketing:modify", "name": "修改营销", "module": "marketing_management", "description": "修改营销活动"},
            {"code": "marketing:view", "name": "查看营销", "module": "marketing_management", "description": "查看营销信息"},

            # 运营管理权限
            {"code": "operation:manage", "name": "运营管理", "module": "operation_management", "description": "运营管理"},
            {"code": "operation:view", "name": "查看运营", "module": "operation_management", "description": "查看运营信息"},

            # 文档管理权限
            {"code": "document:create", "name": "创建文档", "module": "document_management", "description": "创建文档"},
            {"code": "document:modify", "name": "修改文档", "module": "document_management", "description": "修改文档"},
            {"code": "document:view", "name": "查看文档", "module": "document_management", "description": "查看文档信息"},

            # 日志管理权限
            {"code": "log:view", "name": "查看日志", "module": "log_management", "description": "查看系统日志"},
            {"code": "log:export", "name": "导出日志", "module": "log_management", "description": "导出系统日志"},

            # 访客管理权限（新增）
            {"code": "visitor:create", "name": "创建访客", "module": "visitor_management", "description": "创建访客记录"},
            {"code": "visitor:delete", "name": "删除访客", "module": "visitor_management", "description": "删除访客记录"},
            {"code": "visitor:modify", "name": "修改访客", "module": "visitor_management", "description": "修改访客信息"},
            {"code": "visitor:view", "name": "查看访客", "module": "visitor_management", "description": "查看访客信息"},
            {"code": "visitor:approve_leader", "name": "审批团队长", "module": "visitor_management", "description": "审批团队长申请"},
            {"code": "visitor:manage_team", "name": "管理团队", "module": "visitor_management", "description": "管理团队成员"},

            # 数据库访问权限（新增）
            {"code": "database:view", "name": "查看数据库", "module": "database_management", "description": "查看数据库信息"},
            {"code": "database:stats", "name": "查看数据库统计", "module": "database_management", "description": "查看数据库统计信息"},
        ]

        permissions = []
        for perm_data in permissions_data:
            perm = Permission(**perm_data)
            db.add(perm)
            permissions.append(perm)
        db.commit()
        print(f"创建了 {len(permissions)} 个权限")

        # 2. 创建角色（添加CEO角色）
        roles_data = [
            {
                "name": "超级管理员",
                "name_en": "super_admin",
                "level": 1,
                "description": "拥有所有系统权限"
            },
            {
                "name": "CEO",
                "name_en": "ceo",
                "level": 0,  # CEO级别为0，比超级管理员还高
                "description": "公司首席执行官，拥有所有权限"
            },
            {
                "name": "CTO管理员",
                "name_en": "cto_admin",
                "level": 2,
                "description": "技术部门高级管理员"
            },
            {
                "name": "CMO管理员",
                "name_en": "cmo_admin",
                "level": 2,
                "description": "市场部门高级管理员"
            },
            {
                "name": "COO管理员",
                "name_en": "coo_admin",
                "level": 2,
                "description": "运营部门高级管理员"
            },
            {
                "name": "CFO管理员",
                "name_en": "cfo_admin",
                "level": 2,
                "description": "财务部门高级管理员"
            },
            {
                "name": "部门经理",
                "name_en": "manager",
                "level": 3,
                "description": "部门级别权限"
            },
            {
                "name": "普通员工",
                "name_en": "staff",
                "level": 4,
                "description": "普通员工权限"
            },
        ]

        roles = []
        for role_data in roles_data:
            role = Role(**role_data)
            db.add(role)
            roles.append(role)
        db.commit()
        print(f"创建了 {len(roles)} 个角色")

        # 3. 为角色分配权限
        # CEO拥有所有权限
        ceo_role = db.query(Role).filter_by(name_en="ceo").first()
        ceo_role.permissions = permissions

        # 超级管理员拥有所有权限
        super_admin_role = db.query(Role).filter_by(name_en="super_admin").first()
        super_admin_role.permissions = permissions

        # CTO管理员权限
        cto_role = db.query(Role).filter_by(name_en="cto_admin").first()
        cto_permissions = [
            "user:create", "user:modify", "user:view", "user:reset_password",
            "role:create", "role:modify", "role:view", "role:assign_permission",
            "permission:grant", "permission:revoke", "permission:view",
            "system:modify_config", "system:view_config",
            "data:view", "data:modify", "data:export",
            "approval:submit", "approval:approve", "approval:view",
            "product:create", "product:modify", "product:view",
            "document:create", "document:modify", "document:view",
            "log:view", "log:export"
        ]
        cto_role.permissions = [p for p in permissions if p.code in cto_permissions]

        # 其他角色权限（简化）
        admin_permissions = [
            "user:create", "user:modify", "user:view",
            "role:view",
            "permission:view",
            "system:view_config",
            "data:view", "data:modify", "data:export",
            "approval:submit", "approval:approve", "approval:view",
            "document:create", "document:modify", "document:view",
            "log:view", "log:export"
        ]
        for role_en in ["cmo_admin", "coo_admin", "cfo_admin"]:
            role = db.query(Role).filter_by(name_en=role_en).first()
            role.permissions = [p for p in permissions if p.code in admin_permissions]

        # 部门经理权限
        manager_role = db.query(Role).filter_by(name_en="manager").first()
        manager_permissions = [
            "user:view",
            "role:view",
            "permission:view",
            "system:view_config",
            "data:view", "data:modify", "data:export",
            "approval:submit", "approval:view",
            "document:create", "document:modify", "document:view",
            "log:view"
        ]
        manager_role.permissions = [p for p in permissions if p.code in manager_permissions]

        # 普通员工权限
        staff_role = db.query(Role).filter_by(name_en="staff").first()
        staff_permissions = [
            "data:view", "data:export",
            "approval:submit", "approval:view",
            "document:create", "document:modify", "document:view"
        ]
        staff_role.permissions = [p for p in permissions if p.code in staff_permissions]

        db.commit()
        print("为角色分配了权限")

        # 4. 创建初始用户
        # 创建黄爱莉CEO账号
        password = "Huang@2026"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        huang_aili = User(
            name="黄爱莉",
            email="huangaili@meiyue.com",
            phone="",
            wechat="huangaili_wx",
            password_hash=password_hash,
            department="董事会",
            position="CEO",
            status="active",
            is_ceo=True,
            is_superuser=False,
            two_factor_enabled=True,
            two_factor_secret=pyotp.random_base32()
        )
        db.add(huang_aili)
        db.commit()
        print("创建了CEO：黄爱莉")

        # 为黄爱莉分配CEO角色
        ceo_role = db.query(Role).filter_by(name_en="ceo").first()
        huang_aili.roles.append(ceo_role)
        db.commit()

        # 创建许锋超级管理员账号
        password = "Xu@2026"
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        xu_feng = User(
            name="许锋",
            email="xufeng@meiyue.com",
            phone="",
            wechat="xufeng_wx",
            password_hash=password_hash,
            department="董事会",
            position="董事长/创始人",
            status="active",
            is_ceo=False,
            is_superuser=True,
            two_factor_enabled=True,
            two_factor_secret=pyotp.random_base32()
        )
        db.add(xu_feng)
        db.commit()
        print("创建了超级管理员：许锋")

        # 为许锋分配超级管理员角色
        super_admin_role = db.query(Role).filter_by(name_en="super_admin").first()
        xu_feng.roles.append(super_admin_role)
        db.commit()

        # 5. 创建其他管理员账号
        admin_users = [
            {
                "name": "CTO（待定）",
                "email": "cto@meiyue.com",
                "department": "产品技术部",
                "position": "首席技术官",
                "role_name_en": "cto_admin"
            },
            {
                "name": "CMO（待定）",
                "email": "cmo@meiyue.com",
                "department": "市场营销部",
                "position": "首席营销官",
                "role_name_en": "cmo_admin"
            },
            {
                "name": "COO（待定）",
                "email": "coo@meiyue.com",
                "department": "运营管理部",
                "position": "首席运营官",
                "role_name_en": "coo_admin"
            },
            {
                "name": "CFO（待定）",
                "email": "cfo@meiyue.com",
                "department": "财务管理部",
                "position": "首席财务官",
                "role_name_en": "cfo_admin"
            },
        ]

        for admin_data in admin_users:
            password_hash = bcrypt.hashpw("Temp@2026".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            admin_user = User(
                name=admin_data["name"],
                email=admin_data["email"],
                password_hash=password_hash,
                department=admin_data["department"],
                position=admin_data["position"],
                status="pending",
                two_factor_enabled=True,
                two_factor_secret=pyotp.random_base32()
            )
            db.add(admin_user)
            db.commit()

            role = db.query(Role).filter_by(name_en=admin_data["role_name_en"]).first()
            admin_user.roles.append(role)
            db.commit()

        print("创建了其他管理员账号（待定）")

        # 6. 创建审计日志
        audit_log = AuditLog(
            user_id=xu_feng.id,
            action="system_init_v2",
            description="系统初始化v2.0，添加CEO角色和访客管理功能",
            status="success"
        )
        db.add(audit_log)
        db.commit()

        print("默认数据填充完成！")
        print("\n" + "="*50)
        print("初始账号信息：")
        print("="*50)
        print("CEO账号：")
        print("  邮箱：huangaili@meiyue.com")
        print("  密码：Huang@2026")
        print("  双因素认证密钥：", huang_aili.two_factor_secret)
        print()
        print("超级管理员账号：")
        print("  邮箱：xufeng@meiyue.com")
        print("  密码：Xu@2026")
        print("  双因素认证密钥：", xu_feng.two_factor_secret)
        print("="*50)
        print("\n请在首次登录后立即修改密码！")

    except Exception as e:
        db.rollback()
        print(f"填充数据失败：{str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    init_database()
    seed_default_data()
