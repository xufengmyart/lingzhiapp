"""
初始化默认超级管理员脚本
"""

import sys
import os

# 添加项目路径到 sys.path
workspace_path = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)

from coze_coding_dev_sdk.database import get_session
from src.storage.database.super_admin_manager import SuperAdminManager


def initialize_default_super_admin():
    """初始化默认超级管理员"""
    
    print("="*70)
    print("初始化默认超级管理员")
    print("="*70)
    print()
    
    # 获取数据库会话
    db = get_session()
    
    try:
        # 创建管理器
        manager = SuperAdminManager()
        
        # 验证超级管理员唯一性
        print("🔍 检查超级管理员状态...")
        verification = manager.verify_super_admin_uniqueness(db)
        print(f"   状态: {verification['message']}")
        print(f"   数量: {verification['count']}")
        print()
        
        if verification['valid']:
            # 已存在超级管理员
            super_admins = manager.get_all_super_admins(db)
            print("✅ 系统中已存在超级管理员:")
            print("-"*70)
            for admin in super_admins:
                print(f"ID: {admin.id}")
                print(f"姓名: {admin.name}")
                print(f"邮箱: {admin.email}")
                print(f"状态: {admin.status}")
                print(f"双因素认证: {'已启用' if admin.two_factor_enabled else '未启用'}")
                print(f"创建时间: {admin.created_at}")
                print("-"*70)
        else:
            if verification['count'] == 0:
                # 不存在超级管理员，创建默认超级管理员
                print("📝 创建默认超级管理员...")
                print()
                
                try:
                    super_admin = manager.initialize_default_super_admin(db)
                    
                    print("✅ 默认超级管理员创建成功!")
                    print("-"*70)
                    print(f"ID: {super_admin.id}")
                    print(f"姓名: {super_admin.name}")
                    print(f"邮箱: {super_admin.email}")
                    print(f"默认密码: LINGZI@2026#Super")
                    print(f"双因素认证: {'已启用' if super_admin.two_factor_enabled else '未启用'}")
                    print(f"创建时间: {super_admin.created_at}")
                    print("-"*70)
                    print()
                    print("⚠️  重要提示:")
                    print("   1. 请立即登录并修改默认密码")
                    print("   2. 请立即设置双因素认证")
                    print("   3. 请立即配置IP白名单")
                    print()
                    
                except Exception as e:
                    print(f"❌ 创建超级管理员失败: {e}")
                    return False
            else:
                # 存在多个超级管理员
                print("⚠️  发现多个超级管理员:")
                print("-"*70)
                super_admins = manager.get_all_super_admins(db)
                for admin in super_admins:
                    print(f"ID: {admin.id}, 姓名: {admin.name}, 邮箱: {admin.email}")
                print("-"*70)
                print()
                print("建议: 使用 transfer_super_admin 方法将权限合并到1个管理员")
                print()
        
        print("="*70)
        print("✅ 超级管理员初始化完成")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 初始化失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    success = initialize_default_super_admin()
    exit(0 if success else 1)
