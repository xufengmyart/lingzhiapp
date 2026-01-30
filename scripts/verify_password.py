"""
验证密码修改脚本
"""

import sys
import os
import hashlib

# 添加项目路径到 sys.path
workspace_path = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)

from coze_coding_dev_sdk.database import get_session
from src.storage.database.shared.model import User


def _hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password_change():
    """验证密码修改"""
    
    print("="*70)
    print("密码修改验证")
    print("="*70)
    print()
    
    # 获取数据库会话
    db = get_session()
    
    try:
        # 查询超级管理员
        super_admin = db.query(User).filter(User.is_superuser == True).first()
        
        if not super_admin:
            print("❌ 系统中不存在超级管理员")
            return False
        
        print("📋 超级管理员信息:")
        print(f"   ID: {super_admin.id}")
        print(f"   姓名: {super_admin.name}")
        print(f"   邮箱: {super_admin.email}")
        print(f"   更新时间: {super_admin.updated_at}")
        print()
        
        # 验证新密码
        new_password = "xf.071214"
        new_password_hash = _hash_password(new_password)
        
        print("🔐 密码验证:")
        print(f"   新密码: {new_password}")
        print(f"   密码哈希: {new_password_hash}")
        print(f"   数据库哈希: {super_admin.password_hash}")
        print()
        
        if super_admin.password_hash == new_password_hash:
            print("✅ 新密码验证成功!")
            print("   密码修改已生效")
        else:
            print("❌ 新密码验证失败!")
            print("   密码修改可能未生效")
            return False
        
        print()
        
        # 验证旧密码不再有效
        old_password = "LINGZI@2026#Super"
        old_password_hash = _hash_password(old_password)
        
        print("🔐 旧密码验证:")
        print(f"   旧密码: {old_password}")
        print(f"   密码哈希: {old_password_hash}")
        print()
        
        if super_admin.password_hash != old_password_hash:
            print("✅ 旧密码已失效!")
            print("   旧密码无法再使用")
        else:
            print("❌ 旧密码仍然有效!")
            print("   密码修改未生效")
            return False
        
        print()
        print("="*70)
        print("✅ 密码修改验证完成")
        print("="*70)
        print()
        print("📝 当前登录信息:")
        print(f"   邮箱: {super_admin.email}")
        print(f"   密码: {new_password}")
        print(f"   双因素认证: {'已启用' if super_admin.two_factor_enabled else '未启用'}")
        print(f"   IP白名单: {'已配置' if super_admin.ip_whitelist else '未配置'}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    success = verify_password_change()
    exit(0 if success else 1)
