"""
修改超级管理员密码脚本
"""

import sys
import os
import hashlib

# 添加项目路径到 sys.path
workspace_path = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)

from coze_coding_dev_sdk.database import get_session
from src.storage.database.shared.model import User, AuditLog
from datetime import datetime


def _hash_password(password: str) -> str:
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def change_super_admin_password(old_password: str, new_password: str):
    """修改超级管理员密码"""
    
    print("="*70)
    print("超级管理员密码修改")
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
        
        print(f"📋 超级管理员信息:")
        print(f"   ID: {super_admin.id}")
        print(f"   姓名: {super_admin.name}")
        print(f"   邮箱: {super_admin.email}")
        print()
        
        # 验证旧密码
        old_password_hash = _hash_password(old_password)
        if super_admin.password_hash != old_password_hash:
            print("❌ 旧密码验证失败")
            print("   请检查旧密码是否正确")
            return False
        
        print("✅ 旧密码验证通过")
        print()
        
        # 生成新密码哈希
        new_password_hash = _hash_password(new_password)
        
        # 更新密码
        super_admin.password_hash = new_password_hash
        super_admin.updated_at = datetime.now()
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print("✅ 密码修改成功!")
        print()
        print("="*70)
        print("新密码信息")
        print("="*70)
        print(f"邮箱: {super_admin.email}")
        print(f"密码: {new_password}")
        print(f"更新时间: {super_admin.updated_at}")
        print()
        
        # 记录审计日志
        audit_log = AuditLog(
            user_id=super_admin.id,
            action='change_password',
            resource_type='user',
            resource_id=super_admin.id,
            description='超级管理员修改密码',
            status='success',
            created_at=datetime.now()
        )
        db.add(audit_log)
        db.commit()
        
        print("✅ 审计日志已记录")
        print()
        print("="*70)
        print("⚠️  安全提醒")
        print("="*70)
        print("1. 请妥善保管新密码，不要泄露给他人")
        print("2. 建议定期更换密码（建议每90天）")
        print("3. 请确保已配置双因素认证")
        print("4. 请配置IP白名单以增强安全性")
        print()
        
        # 检查安全配置
        warnings = []
        if not super_admin.two_factor_enabled:
            warnings.append("双因素认证未启用")
        if not super_admin.ip_whitelist:
            warnings.append("IP白名单未配置")
        
        if warnings:
            print("⚠️  待完善的安全配置:")
            for warning in warnings:
                print(f"   - {warning}")
            print()
        
        print("="*70)
        print("✅ 密码修改完成")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 密码修改失败: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    # 修改超级管理员密码
    old_password = "LINGZI@2026#Super"
    new_password = "xf.071214"
    
    success = change_super_admin_password(old_password, new_password)
    exit(0 if success else 1)
