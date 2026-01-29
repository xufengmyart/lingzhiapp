#!/usr/bin/env python3
"""
数据库迁移脚本：添加用户登记相关字段和推荐关系表

运行此脚本来添加：
1. Users表的新字段：real_name, is_registered, registration_time
2. ReferralRelations表（推荐关系表）
"""

import sys
sys.path.insert(0, '/workspace/projects/src')

from coze_coding_dev_sdk.database import get_session
from sqlalchemy import text

def migrate():
    """执行数据库迁移"""
    print("=" * 60)
    print("开始数据库迁移：添加用户登记功能")
    print("=" * 60)
    print()

    db = get_session()

    try:
        # 1. 检查并添加real_name字段
        print("1. 检查real_name字段...")
        try:
            result = db.execute(text("SELECT real_name FROM users LIMIT 1"))
            print("   ✅ real_name字段已存在")
        except Exception:
            db.rollback()  # 重置事务状态
            print("   ➕ 添加real_name字段...")
            db.execute(text("ALTER TABLE users ADD COLUMN real_name VARCHAR(50)"))
            db.execute(text("COMMENT ON COLUMN users.real_name IS '真实姓名'"))
            db.commit()
            print("   ✅ real_name字段添加成功")

        # 2. 检查并添加is_registered字段
        print()
        print("2. 检查is_registered字段...")
        try:
            result = db.execute(text("SELECT is_registered FROM users LIMIT 1"))
            print("   ✅ is_registered字段已存在")
        except Exception:
            db.rollback()  # 重置事务状态
            print("   ➕ 添加is_registered字段...")
            db.execute(text("ALTER TABLE users ADD COLUMN is_registered BOOLEAN NOT NULL DEFAULT false"))
            db.execute(text("COMMENT ON COLUMN users.is_registered IS '是否完成信息登记'"))
            db.commit()
            print("   ✅ is_registered字段添加成功")

        # 3. 检查并添加registration_time字段
        print()
        print("3. 检查registration_time字段...")
        try:
            result = db.execute(text("SELECT registration_time FROM users LIMIT 1"))
            print("   ✅ registration_time字段已存在")
        except Exception:
            db.rollback()  # 重置事务状态
            print("   ➕ 添加registration_time字段...")
            db.execute(text("ALTER TABLE users ADD COLUMN registration_time TIMESTAMP"))
            db.execute(text("COMMENT ON COLUMN users.registration_time IS '登记时间'"))
            db.commit()
            print("   ✅ registration_time字段添加成功")

        # 4. 检查并创建referral_relations表
        print()
        print("4. 检查referral_relations表...")
        try:
            result = db.execute(text("SELECT id FROM referral_relations LIMIT 1"))
            print("   ✅ referral_relations表已存在")
        except Exception:
            db.rollback()  # 重置事务状态
            print("   ➕ 创建referral_relations表...")
            db.execute(text("""
                CREATE TABLE referral_relations (
                    id SERIAL PRIMARY KEY,
                    referrer_id INTEGER NOT NULL,
                    referred_id INTEGER NOT NULL,
                    level INTEGER NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (referrer_id) REFERENCES users(id),
                    FOREIGN KEY (referred_id) REFERENCES users(id),
                    UNIQUE (referrer_id, referred_id)
                )
            """))
            db.commit()

            # 创建索引
            print("   ➕ 创建索引...")
            db.execute(text("CREATE INDEX ix_referral_relations_referrer_id ON referral_relations(referrer_id)"))
            db.execute(text("CREATE INDEX ix_referral_relations_referred_id ON referral_relations(referred_id)"))
            db.commit()

            # 添加表注释
            db.execute(text("COMMENT ON TABLE referral_relations IS '推荐关系表'"))
            db.execute(text("COMMENT ON COLUMN referral_relations.id IS '推荐关系ID'"))
            db.execute(text("COMMENT ON COLUMN referral_relations.referrer_id IS '推荐人ID'"))
            db.execute(text("COMMENT ON COLUMN referral_relations.referred_id IS '被推荐人ID'"))
            db.execute(text("COMMENT ON COLUMN referral_relations.level IS '推荐层级：1-一级，2-二级，3-三级'"))
            db.execute(text("COMMENT ON COLUMN referral_relations.status IS '状态：active/inactive'"))
            db.execute(text("COMMENT ON COLUMN referral_relations.created_at IS '创建时间'"))
            db.commit()

            print("   ✅ referral_relations表创建成功")

        # 5. 验证迁移
        print()
        print("=" * 60)
        print("5. 验证迁移结果...")
        print("=" * 60)

        # 检查users表字段
        print()
        print("Users表新字段：")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name IN ('real_name', 'is_registered', 'registration_time')
            ORDER BY ordinal_position
        """))
        for row in result:
            print(f"   - {row[0]}: {row[1]}, nullable={row[2]}, default={row[3]}")

        # 检查referral_relations表
        print()
        print("ReferralRelations表结构：")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'referral_relations'
            ORDER BY ordinal_position
        """))
        for row in result:
            print(f"   - {row[0]}: {row[1]}, nullable={row[2]}, default={row[3]}")

        print()
        print("=" * 60)
        print("✅ 数据库迁移完成！")
        print("=" * 60)
        print()
        print("迁移内容：")
        print("  1. ✅ Users表添加real_name字段")
        print("  2. ✅ Users表添加is_registered字段")
        print("  3. ✅ Users表添加registration_time字段")
        print("  4. ✅ 创建ReferralRelations表")
        print()
        print("现在可以使用用户登记功能了！")
        print()

        return 0

    except Exception as e:
        db.rollback()
        print()
        print("=" * 60)
        print("❌ 数据库迁移失败")
        print("=" * 60)
        print()
        print(f"错误信息：{str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    exit(migrate())
