"""
更新用户电话号码脚本
"""

import sys
import os

# 添加项目路径到 sys.path
workspace_path = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)

from coze_coding_dev_sdk.database import get_session
from src.storage.database.shared.model import User, AuditLog
from datetime import datetime


def update_user_phone(user_id: int, phone: str):
    """更新用户电话号码"""
    
    print("="*70)
    print("用户电话号码更新")
    print("="*70)
    print()
    
    # 获取数据库会话
    db = get_session()
    
    try:
        # 查询用户
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            print(f"❌ 未找到ID为 {user_id} 的用户")
            return False
        
        print(f"📋 用户信息:")
        print(f"   ID: {user.id}")
        print(f"   姓名: {user.name}")
        print(f"   邮箱: {user.email}")
        print(f"   原电话: {user.phone if user.phone else '未填写'}")
        print()
        
        # 检查电话号码格式
        if not phone or len(phone) < 11:
            print(f"❌ 电话号码格式无效: {phone}")
            return False
        
        # 更新电话号码
        old_phone = user.phone
        user.phone = phone
        user.updated_at = datetime.now()
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("✅ 电话号码更新成功!")
        print()
        print("="*70)
        print("更新结果")
        print("="*70)
        print(f"ID: {user.id}")
        print(f"姓名: {user.name}")
        print(f"邮箱: {user.email}")
        print(f"原电话: {old_phone if old_phone else '未填写'}")
        print(f"新电话: {user.phone}")
        print(f"更新时间: {user.updated_at}")
        print()
        
        # 记录审计日志
        audit_log = AuditLog(
            user_id=user.id,
            action='update_phone',
            resource_type='user',
            resource_id=user.id,
            description=f'用户更新电话号码: {old_phone if old_phone else "未填写"} -> {phone}',
            status='success',
            created_at=datetime.now()
        )
        db.add(audit_log)
        db.commit()
        
        print("✅ 审计日志已记录")
        print()
        print("="*70)
        print("✅ 电话号码更新完成")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 电话号码更新失败: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    # 更新用户电话号码
    user_id = 1  # 超级管理员ID
    phone = "15029005772"
    
    success = update_user_phone(user_id, phone)
    exit(0 if success else 1)
