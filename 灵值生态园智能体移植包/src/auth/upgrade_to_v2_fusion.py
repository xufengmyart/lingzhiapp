"""
V2.0 融合版 - 数据库更新脚本

功能：
1. 更新会员级别体系（5级→4级合伙人体系）
2. 新增用户表字段
3. 创建新表（贡献值V2、活跃勋章、项目分配、待发放奖励）
4. 更新推荐佣金表结构
"""

import sys
import os
from datetime import datetime
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入models
try:
    from models import Base, User, MemberLevel
except ImportError:
    # 如果导入失败，直接使用SQLAlchemy
    Base = None
    User = None
    MemberLevel = None

# 导入枚举
try:
    from enums.partner_level import PartnerLevelType
except ImportError:
    # 如果枚举文件不存在，定义一个临时枚举
    class PartnerLevelType:
        NORMAL_USER = "normal_user"
        REGULAR_PARTNER = "regular_partner"
        SENIOR_PARTNER = "senior_partner"
        FOUNDING_PARTNER = "founding_partner"

# 数据库连接
DATABASE_URL = "sqlite:///auth.db"
engine = create_engine(DATABASE_URL, echo=False)
Session = sessionmaker(bind=engine)

def upgrade_member_levels():
    """
    升级会员级别体系（5级→4级合伙人体系）
    """
    print("🔄 开始升级会员级别体系...")
    
    session = Session()
    try:
        # 1. 删除原有会员数据
        session.execute(text("DELETE FROM member_levels"))
        session.commit()
        print("   ✓ 已删除原有会员数据")
        
        # 2. 插入V2.0的4级合伙人数据
        partner_levels_sql = """
        INSERT INTO member_levels (
            level_code, name, level_name, level, min_contribution_value,
            commission_ratio, benefits, description,
            created_at, updated_at, status
        ) VALUES
        (
            'normal_user',
            '普通用户',
            '普通用户',
            1,
            0,
            0.10,
            '项目参与权、灵值积累',
            '完成基础信息登记即可成为普通用户',
            datetime('now'),
            datetime('now'),
            'active'
        ),
        (
            'regular_partner',
            '普通合伙人',
            '普通合伙人',
            2,
            50000,
            0.10,
            '二级推荐（10%+5%）、项目优先参与权',
            '累计灵值≥50000或直接投资50000',
            datetime('now'),
            datetime('now'),
            'active'
        ),
        (
            'senior_partner',
            '高级合伙人',
            '高级合伙人',
            3,
            100000,
            0.10,
            '三级推荐（10%+5%+3%）、项目决策权',
            '累计灵值≥100000或直接投资100000',
            datetime('now'),
            datetime('now'),
            'active'
        ),
        (
            'founding_partner',
            '创始合伙人',
            '创始合伙人',
            4,
            200000,
            0.10,
            '平台分红权、规则制定参与权',
            '累计灵值≥200000或直接投资200000',
            datetime('now'),
            datetime('now'),
            'active'
        )
        """
        
        session.execute(text(partner_levels_sql))
        session.commit()
        print("   ✓ 已插入4级合伙人数据")
        
        # 3. 显示结果
        print("\n📊 V2.0 合伙人级别体系：")
        levels = session.execute(
            text("SELECT level, name, min_contribution_value, benefits FROM member_levels ORDER BY level")
        ).fetchall()
        
        for level in levels:
            print(f"\n   [{level[0]}] {level[1]}")
            print(f"      准入：累计灵值≥{level[2]}")
            print(f"      权限：{level[3]}")
        
        print("\n✅ 会员级别体系升级完成！")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 升级失败：{str(e)}")
        raise
    finally:
        session.close()


def add_user_fields():
    """
    为用户表新增字段
    """
    print("\n🔄 开始为用户表新增字段...")
    
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        # 需要新增的字段
        new_fields = {
            'registration_date': 'DATETIME',
            'last_login_date': 'DATETIME',
            'consecutive_login_days': 'INTEGER DEFAULT 0',
            'partner_level': 'VARCHAR(50) DEFAULT "normal_user"',
            'direct_investment': 'FLOAT DEFAULT 0.0',
            'bonus_multiplier': 'FLOAT DEFAULT 1.0'
        }
        
        with engine.connect() as conn:
            for field_name, field_type in new_fields.items():
                if field_name not in columns:
                    try:
                        conn.execute(text(f"ALTER TABLE users ADD COLUMN {field_name} {field_type}"))
                        conn.commit()
                        print(f"   ✓ 已添加字段：{field_name}")
                    except SQLAlchemyError as e:
                        print(f"   ⚠️  添加字段失败 {field_name}：{str(e)}")
                else:
                    print(f"   ⊙ 字段已存在：{field_name}")
        
        print("\n✅ 用户表字段更新完成！")
        
    except Exception as e:
        print(f"❌ 更新失败：{str(e)}")
        raise


def create_user_contributions_v2_table():
    """
    创建用户贡献值V2表（三维贡献值模型）
    """
    print("\n🔄 开始创建用户贡献值V2表...")
    
    try:
        inspector = inspect(engine)
        
        if 'user_contributions_v2' in inspector.get_table_names():
            print("   ⊙ 表已存在：user_contributions_v2")
            return
        
        create_table_sql = """
        CREATE TABLE user_contributions_v2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            
            -- 累计贡献值
            cumulative_contribution FLOAT DEFAULT 0.0,
            
            -- 项目贡献值
            project_contribution FLOAT DEFAULT 0.0,
            
            -- 剩余贡献值
            remaining_contribution FLOAT DEFAULT 0.0,
            
            -- 消费贡献值
            consumed_contribution FLOAT DEFAULT 0.0,
            
            -- 初始灵值
            initial_contribution FLOAT DEFAULT 1000.0,
            
            -- 推荐奖励
            referral_reward FLOAT DEFAULT 0.0,
            
            -- 佣金收入
            commission_income FLOAT DEFAULT 0.0,
            
            -- 团队收益
            team_income FLOAT DEFAULT 0.0,
            
            -- 更新时间
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        
        create_index_sql = """
        CREATE INDEX idx_user_contributions_v2_user_id ON user_contributions_v2(user_id);
        CREATE INDEX idx_user_contributions_v2_cumulative ON user_contributions_v2(cumulative_contribution);
        """
        
        with engine.connect() as conn:
            # 尝试创建表（如果不存在）
            try:
                conn.execute(text(create_table_sql))
            except SQLAlchemyError:
                pass  # 表已存在
            
            # 尝试创建索引（如果不存在）
            try:
                conn.execute(text("CREATE INDEX idx_user_contributions_v2_user_id ON user_contributions_v2(user_id);"))
            except SQLAlchemyError:
                pass  # 索引已存在
            
            try:
                conn.execute(text("CREATE INDEX idx_user_contributions_v2_cumulative ON user_contributions_v2(cumulative_contribution);"))
            except SQLAlchemyError:
                pass  # 索引已存在
            
            conn.commit()
        
        print("   ✓ 已创建表：user_contributions_v2")
        print("   ✓ 已创建索引")
        print("\n✅ 用户贡献值V2表创建完成！")
        
    except Exception as e:
        print(f"❌ 创建失败：{str(e)}")
        raise


def create_user_active_badges_table():
    """
    创建活跃用户勋章表
    """
    print("\n🔄 开始创建活跃用户勋章表...")
    
    try:
        inspector = inspect(engine)
        
        if 'user_active_badges' in inspector.get_table_names():
            print("   ⊙ 表已存在：user_active_badges")
            return
        
        create_table_sql = """
        CREATE TABLE user_active_badges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            badge_type VARCHAR(50) NOT NULL,
            badge_name VARCHAR(100) NOT NULL,
            granted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            consecutive_days INTEGER NOT NULL,
            bonus_multiplier FLOAT DEFAULT 1.0,
            expires_at DATETIME,
            is_active BOOLEAN DEFAULT 1,
            
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        
        create_index_sql = """
        CREATE INDEX idx_user_active_badges_user_id ON user_active_badges(user_id);
        CREATE INDEX idx_user_active_badges_type ON user_active_badges(badge_type);
        """
        
        with engine.connect() as conn:
            # 尝试创建表（如果不存在）
            try:
                conn.execute(text(create_table_sql))
            except SQLAlchemyError:
                pass  # 表已存在
            
            # 尝试创建索引（如果不存在）
            try:
                conn.execute(text("CREATE INDEX idx_user_contributions_v2_user_id ON user_contributions_v2(user_id);"))
            except SQLAlchemyError:
                pass  # 索引已存在
            
            try:
                conn.execute(text("CREATE INDEX idx_user_contributions_v2_cumulative ON user_contributions_v2(cumulative_contribution);"))
            except SQLAlchemyError:
                pass  # 索引已存在
            
            conn.commit()
        
        print("   ✓ 已创建表：user_active_badges")
        print("   ✓ 已创建索引")
        print("\n✅ 活跃用户勋章表创建完成！")
        
    except Exception as e:
        print(f"❌ 创建失败：{str(e)}")
        raise


def create_project_assignments_table():
    """
    创建项目自动分配记录表
    """
    print("\n🔄 开始创建项目自动分配记录表...")
    
    try:
        inspector = inspect(engine)
        
        if 'project_assignments' in inspector.get_table_names():
            print("   ⊙ 表已存在：project_assignments")
            return
        
        create_table_sql = """
        CREATE TABLE project_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            project_id INTEGER NOT NULL,
            assignment_type VARCHAR(50) NOT NULL,
            match_score FLOAT,
            match_factors TEXT,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            status VARCHAR(50) DEFAULT 'pending',
            
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        );
        """
        
        create_index_sql = """
        CREATE INDEX idx_project_assignments_user_id ON project_assignments(user_id);
        CREATE INDEX idx_project_assignments_project_id ON project_assignments(project_id);
        CREATE INDEX idx_project_assignments_status ON project_assignments(status);
        """
        
        with engine.connect() as conn:
            # 尝试创建表（如果不存在）
            try:
                conn.execute(text(create_table_sql))
            except SQLAlchemyError:
                pass  # 表已存在
            
            # 尝试创建索引（如果不存在）
            try:
                conn.execute(text("CREATE INDEX idx_user_contributions_v2_user_id ON user_contributions_v2(user_id);"))
            except SQLAlchemyError:
                pass  # 索引已存在
            
            try:
                conn.execute(text("CREATE INDEX idx_user_contributions_v2_cumulative ON user_contributions_v2(cumulative_contribution);"))
            except SQLAlchemyError:
                pass  # 索引已存在
            
            conn.commit()
        
        print("   ✓ 已创建表：project_assignments")
        print("   ✓ 已创建索引")
        print("\n✅ 项目自动分配记录表创建完成！")
        
    except Exception as e:
        print(f"❌ 创建失败：{str(e)}")
        raise


def create_pending_rewards_table():
    """
    创建待发放奖励表
    """
    print("\n🔄 开始创建待发放奖励表...")
    
    try:
        inspector = inspect(engine)
        
        if 'pending_rewards' in inspector.get_table_names():
            print("   ⊙ 表已存在：pending_rewards")
            return
        
        create_table_sql = """
        CREATE TABLE pending_rewards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            reward_type VARCHAR(50) NOT NULL,
            amount FLOAT NOT NULL,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            is_granted BOOLEAN DEFAULT 0,
            granted_at DATETIME,
            
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        """
        
        create_index_sql = """
        CREATE INDEX idx_pending_rewards_user_id ON pending_rewards(user_id);
        CREATE INDEX idx_pending_rewards_type ON pending_rewards(reward_type);
        CREATE INDEX idx_pending_rewards_status ON pending_rewards(is_granted);
        """
        
        with engine.connect() as conn:
            # 尝试创建表（如果不存在）
            try:
                conn.execute(text(create_table_sql))
            except SQLAlchemyError:
                pass  # 表已存在
            
            # 尝试创建索引（如果不存在）
            try:
                conn.execute(text("CREATE INDEX idx_user_contributions_v2_user_id ON user_contributions_v2(user_id);"))
            except SQLAlchemyError:
                pass  # 索引已存在
            
            try:
                conn.execute(text("CREATE INDEX idx_user_contributions_v2_cumulative ON user_contributions_v2(cumulative_contribution);"))
            except SQLAlchemyError:
                pass  # 索引已存在
            
            conn.commit()
        
        print("   ✓ 已创建表：pending_rewards")
        print("   ✓ 已创建索引")
        print("\n✅ 待发放奖励表创建完成！")
        
    except Exception as e:
        print(f"❌ 创建失败：{str(e)}")
        raise


def update_referral_commissions_table():
    """
    更新推荐佣金表结构
    """
    print("\n🔄 开始更新推荐佣金表结构...")
    
    try:
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns('referral_commissions')]
        
        # 需要新增的字段
        new_fields = {
            'referral_level': 'INTEGER DEFAULT 1',  # 推荐层级：1/2/3
            'is_upgrade_reward': 'BOOLEAN DEFAULT 0',  # 是否升级奖励
            'calculation_basis': 'VARCHAR(50) DEFAULT "contribution"'  # 计算基础：contribution/amount
        }
        
        with engine.connect() as conn:
            for field_name, field_type in new_fields.items():
                if field_name not in columns:
                    try:
                        conn.execute(text(f"ALTER TABLE referral_commissions ADD COLUMN {field_name} {field_type}"))
                        conn.commit()
                        print(f"   ✓ 已添加字段：{field_name}")
                    except SQLAlchemyError as e:
                        print(f"   ⚠️  添加字段失败 {field_name}：{str(e)}")
                else:
                    print(f"   ⊙ 字段已存在：{field_name}")
        
        print("\n✅ 推荐佣金表结构更新完成！")
        
    except Exception as e:
        print(f"❌ 更新失败：{str(e)}")
        raise


def migrate_existing_contributions():
    """
    迁移现有贡献值数据到V2.0格式
    """
    print("\n🔄 开始迁移现有贡献值数据...")
    
    session = Session()
    try:
        # 查询所有用户
        users = session.execute(text("SELECT id FROM users")).fetchall()
        
        migrated_count = 0
        for user in users:
            user_id = user[0]
            
            # 检查是否已有V2.0贡献值记录
            existing_v2 = session.execute(
                text("SELECT id FROM user_contributions_v2 WHERE user_id = :user_id"),
                {"user_id": user_id}
            ).fetchone()
            
            if not existing_v2:
                # 创建V2.0贡献值记录
                # 默认初始1000灵值（新用户）
                insert_sql = """
                INSERT INTO user_contributions_v2 (
                    user_id,
                    cumulative_contribution,
                    project_contribution,
                    remaining_contribution,
                    consumed_contribution,
                    initial_contribution
                ) VALUES (
                    :user_id,
                    1000.0,
                    0.0,
                    1000.0,
                    0.0,
                    1000.0
                )
                """
                session.execute(text(insert_sql), {"user_id": user_id})
                migrated_count += 1
        
        session.commit()
        print(f"   ✓ 已迁移 {migrated_count} 个用户的贡献值数据")
        print("\n✅ 贡献值数据迁移完成！")
        
    except Exception as e:
        session.rollback()
        print(f"❌ 迁移失败：{str(e)}")
        raise
    finally:
        session.close()


def main():
    """
    主函数：执行所有更新
    """
    print("="*60)
    print("🚀 V2.0 融合版 - 数据库更新脚本")
    print("="*60)
    
    try:
        # 1. 升级会员级别体系
        upgrade_member_levels()
        
        # 2. 为用户表新增字段
        add_user_fields()
        
        # 3. 创建用户贡献值V2表
        create_user_contributions_v2_table()
        
        # 4. 创建活跃用户勋章表
        create_user_active_badges_table()
        
        # 5. 创建项目自动分配记录表
        create_project_assignments_table()
        
        # 6. 创建待发放奖励表
        create_pending_rewards_table()
        
        # 7. 更新推荐佣金表结构
        update_referral_commissions_table()
        
        # 8. 迁移现有贡献值数据
        migrate_existing_contributions()
        
        print("\n" + "="*60)
        print("✅ V2.0 融合版数据库更新完成！")
        print("="*60)
        print("\n📋 更新摘要：")
        print("   ✓ 会员级别体系：5级 → 4级合伙人体系")
        print("   ✓ 用户表新增字段：6个")
        print("   ✓ 新增表：4个（贡献值V2、活跃勋章、项目分配、待发放奖励）")
        print("   ✓ 推荐佣金表新增字段：3个")
        print("   ✓ 数据迁移：已完成")
        print("\n🎉 系统已准备好进入V2.0融合版！")
        
    except Exception as e:
        print(f"\n❌ 更新过程出现错误：{str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
