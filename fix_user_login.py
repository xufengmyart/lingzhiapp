#!/usr/bin/env python3
"""
修复用户登录问题 - 禁用手机验证码要求
"""
import sqlite3
import os

# 数据库路径
db_path = '/workspace/projects/admin-backend/lingzhi_ecosystem.db'

# 检查并添加 require_phone_verification 字段（如果不存在）
def fix_user_login():
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        return False

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 检查字段是否存在
        cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in cursor.fetchall()]

        if 'require_phone_verification' not in columns:
            # 添加字段，默认值为0（不需要手机验证码）
            cursor.execute("ALTER TABLE users ADD COLUMN require_phone_verification INTEGER DEFAULT 0")
            print("✅ 添加 require_phone_verification 字段")
        else:
            print("✅ require_phone_verification 字段已存在")

        # 更新所有用户的 require_phone_verification 为 0
        cursor.execute("UPDATE users SET require_phone_verification = 0")
        affected_rows = cursor.rowcount
        print(f"✅ 更新 {affected_rows} 个用户的登录设置")

        # 验证更新
        cursor.execute("SELECT COUNT(*) FROM users WHERE require_phone_verification = 0")
        count = cursor.fetchone()[0]
        print(f"✅ 当前有 {count} 个用户不需要手机验证码即可登录")

        conn.commit()
        return True

    except Exception as e:
        print(f"❌ 错误: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

if __name__ == '__main__':
    print("🔧 修复用户登录问题...")
    success = fix_user_login()
    if success:
        print("✅ 修复完成！现在用户可以直接使用用户名和密码登录")
    else:
        print("❌ 修复失败")
