"""
更新管理员账号和密码
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import bcrypt
from datetime import datetime
import sys
import os

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import User

DATABASE_URL = "sqlite:///./auth.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def update_admin_account():
    """更新管理员账号和密码"""
    db = SessionLocal()

    try:
        # 查找旧账号
        old_email = "xufeng@meiyue.com"
        new_email = "xufeng@meiyueart.cn"
        new_password = "Xf@071214"

        admin = db.query(User).filter(User.email == old_email).first()

        if not admin:
            print(f"❌ 未找到管理员账号：{old_email}")
            return False

        print(f"✅ 找到管理员：{admin.name} ({admin.email})")

        # 更新邮箱
        admin.email = new_email
        print(f"✓ 邮箱已更新：{old_email} → {new_email}")

        # 生成新密码的哈希
        password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        # 更新密码（注意字段名是 password_hash）
        admin.password_hash = password_hash
        print(f"✓ 密码已更新")

        # 更新修改时间
        admin.updated_at = datetime.now()

        # 提交更改
        db.commit()
        print(f"\n✓ 管理员账号更新成功！")

        # 显示新账号信息
        print("\n" + "="*60)
        print("新管理员账号信息：")
        print("="*60)
        print(f"账号：{new_email}")
        print(f"密码：{new_password}")
        print(f"姓名：{admin.name}")
        print(f"角色：{', '.join([role.name for role in admin.roles])}")
        print("="*60)
        print("\n⚠️  请妥善保管账号密码！")

        return True

    except Exception as e:
        print(f"❌ 更新失败：{str(e)}")
        db.rollback()
        return False
    finally:
        db.close()


def verify_login():
    """验证新账号登录"""
    from api import SECRET_KEY, ALGORITHM
    import jwt
    from sqlalchemy.orm import Session

    db = SessionLocal()

    try:
        # 验证新账号存在
        new_email = "xufeng@meiyueart.cn"
        admin = db.query(User).filter(User.email == new_email).first()

        if not admin:
            print(f"❌ 新账号验证失败：未找到账号 {new_email}")
            return False

        print(f"\n✅ 新账号验证成功：{admin.name} ({admin.email})")

        # 验证密码
        new_password = "Xf@071214"
        if bcrypt.checkpw(new_password.encode('utf-8'), admin.hashed_password.encode('utf-8')):
            print(f"✅ 密码验证成功")
        else:
            print(f"❌ 密码验证失败")
            return False

        # 生成测试 token
        token = jwt.encode(
            {"sub": str(admin.id), "exp": datetime.now().timestamp() + 3600},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        print(f"✅ Token 生成成功")
        print(f"\n测试 Token (1小时有效期)：")
        print(f"{token[:50]}...")

        return True

    except Exception as e:
        print(f"❌ 验证失败：{str(e)}")
        return False
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("管理员账号更新工具")
    print("="*60)
    print()

    # 更新账号
    if update_admin_account():
        print("\n" + "="*60)
        print("验证新账号...")
        print("="*60)
        # 验证新账号
        verify_login()
        print("\n✓ 所有操作完成！")
    else:
        print("\n❌ 更新失败，请检查错误信息")
