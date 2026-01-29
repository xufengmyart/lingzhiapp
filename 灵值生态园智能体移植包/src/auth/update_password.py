"""
更新管理员密码
"""
from sqlalchemy import create_engine, text
import bcrypt
from datetime import datetime

DATABASE_URL = "sqlite:///./auth.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def update_password():
    """更新管理员密码"""
    with engine.connect() as conn:
        # 查找管理员
        result = conn.execute(text('SELECT id, name, email FROM users WHERE email=:email'), {'email': 'xufeng@meiyueart.cn'})
        user = result.fetchone()

        if not user:
            print("❌ 未找到管理员账号")
            return False

        print(f"✅ 找到管理员：{user[1]} ({user[2]})")

        # 生成新密码的哈希
        new_password = "Xf@071214"
        password_hash = bcrypt.hashpw(
            new_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

        print(f"✓ 生成密码哈希")

        # 更新密码
        conn.execute(
            text('UPDATE users SET password_hash=:pwd, updated_at=:now WHERE email=:email'),
            {'pwd': password_hash, 'now': datetime.now(), 'email': 'xufeng@meiyueart.cn'}
        )
        conn.commit()

        print(f"✓ 密码已更新")
        print(f"\n✓ 管理员密码更新成功！")
        print("\n新管理员账号信息：")
        print(f"账号：xufeng@meiyueart.cn")
        print(f"密码：{new_password}")
        print(f"\n⚠️  请妥善保管账号密码！")

        return True

if __name__ == "__main__":
    print("="*60)
    print("管理员密码更新工具")
    print("="*60)
    print()

    update_password()
