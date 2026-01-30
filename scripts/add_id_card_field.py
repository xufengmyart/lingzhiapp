#!/usr/bin/env python3
"""
数据库迁移脚本：添加身份证号字段

运行此脚本来添加：
1. Users表的id_card字段（身份证号）
"""

import sys
sys.path.insert(0, '/workspace/projects/src')

from coze_coding_dev_sdk.database import get_session
from sqlalchemy import text

def migrate():
    """执行数据库迁移"""
    print("=" * 60)
    print("开始数据库迁移：添加身份证号字段")
    print("=" * 60)
    print()

    db = get_session()

    try:
        # 检查并添加id_card字段
        print("1. 检查id_card字段...")
        try:
            result = db.execute(text("SELECT id_card FROM users LIMIT 1"))
            print("   ✅ id_card字段已存在")
        except Exception:
            db.rollback()
            print("   ➕ 添加id_card字段...")
            db.execute(text("ALTER TABLE users ADD COLUMN id_card VARCHAR(18)"))
            db.execute(text("COMMENT ON COLUMN users.id_card IS '身份证号码'"))
            db.commit()
            print("   ✅ id_card字段添加成功")

        # 验证迁移
        print()
        print("=" * 60)
        print("2. 验证迁移结果...")
        print("=" * 60)

        # 检查users表字段
        print()
        print("Users表身份证号字段：")
        result = db.execute(text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_name = 'users'
            AND column_name = 'id_card'
        """))
        for row in result:
            print(f"   - {row[0]}: {row[1]}, nullable={row[2]}, default={row[3]}")

        print()
        print("=" * 60)
        print("✅ 数据库迁移完成！")
        print("=" * 60)
        print()
        print("迁移内容：")
        print("  1. ✅ Users表添加id_card字段")
        print()
        print("现在可以使用身份证号实名认证功能了！")
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
