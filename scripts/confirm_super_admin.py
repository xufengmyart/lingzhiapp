"""
超级管理员确认脚本

检查并确认当前系统中的超级管理员状态
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import hashlib


def check_and_confirm_super_admin():
    """检查并确认超级管理员"""
    
    print("="*70)
    print("超级管理员确认脚本")
    print("="*70)
    print()
    
    # 数据库连接配置
    DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/lingzhi_eco"
    
    try:
        # 创建数据库连接
        engine = create_engine(DATABASE_URL)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        print("✅ 数据库连接成功")
        print()
        
        # 检查是否存在users表
        try:
            result = session.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'users'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ users表不存在，需要先创建数据库表")
                session.close()
                return False
            
            print("✅ users表存在")
            print()
        except Exception as e:
            print(f"❌ 检查users表失败: {e}")
            session.close()
            return False
        
        # 查询当前超级管理员数量
        try:
            result = session.execute(text("""
                SELECT COUNT(*) FROM users WHERE is_superuser = true
            """))
            super_admin_count = result.scalar()
            
            print(f"🔍 当前超级管理员数量: {super_admin_count}")
            print()
        except Exception as e:
            print(f"❌ 查询超级管理员失败: {e}")
            session.close()
            return False
        
        # 查询超级管理员详情
        if super_admin_count > 0:
            try:
                result = session.execute(text("""
                    SELECT id, name, email, status, created_at
                    FROM users 
                    WHERE is_superuser = true
                """))
                super_admins = result.fetchall()
                
                print("📋 超级管理员列表:")
                print("-"*70)
                for admin in super_admins:
                    print(f"ID: {admin[0]}")
                    print(f"姓名: {admin[1]}")
                    print(f"邮箱: {admin[2]}")
                    print(f"状态: {admin[3]}")
                    print(f"创建时间: {admin[4]}")
                    print("-"*70)
                print()
                
                if super_admin_count == 1:
                    print("✅ 系统中存在1个超级管理员，符合唯一性原则")
                else:
                    print(f"⚠️  系统中存在{super_admin_count}个超级管理员，超过唯一性限制（最多1个）")
                    print("   建议通过转让方式减少到1个")
                
            except Exception as e:
                print(f"❌ 查询超级管理员详情失败: {e}")
        else:
            print("⚠️  系统中不存在超级管理员")
            print()
            print("📝 需要创建超级管理员")
            
            # 创建超级管理员
            try:
                # 默认密码
                default_password = "LINGZI@2026#Super"
                password_hash = hashlib.sha256(default_password.encode()).hexdigest()
                
                # 插入超级管理员
                result = session.execute(text("""
                    INSERT INTO users (name, email, password_hash, status, is_superuser, two_factor_enabled, created_at, updated_at)
                    VALUES (:name, :email, :password_hash, :status, :is_superuser, :two_factor_enabled, :created_at, :updated_at)
                    RETURNING id, name, email
                """), {
                    "name": "系统超级管理员",
                    "email": "admin@lingzhi.eco",
                    "password_hash": password_hash,
                    "status": "active",
                    "is_superuser": True,
                    "two_factor_enabled": True,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                })
                
                new_admin = result.fetchone()
                session.commit()
                
                print()
                print("✅ 超级管理员创建成功!")
                print("-"*70)
                print(f"ID: {new_admin[0]}")
                print(f"姓名: {new_admin[1]}")
                print(f"邮箱: {new_admin[2]}")
                print(f"默认密码: {default_password}")
                print("-"*70)
                print()
                print("⚠️  重要提示:")
                print("   1. 请立即登录并修改默认密码")
                print("   2. 请立即设置双因素认证")
                print("   3. 请立即配置IP白名单")
                print()
                
            except Exception as e:
                print(f"❌ 创建超级管理员失败: {e}")
                session.rollback()
                session.close()
                return False
        
        session.close()
        
        print()
        print("="*70)
        print("✅ 超级管理员确认完成")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


if __name__ == "__main__":
    success = check_and_confirm_super_admin()
    exit(0 if success else 1)
