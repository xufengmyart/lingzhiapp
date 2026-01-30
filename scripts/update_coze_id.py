"""
更新用户扣子平台注册ID脚本
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


def update_user_coze_id(user_id: int, coze_id: str):
    """更新用户扣子平台注册ID"""
    
    print("="*70)
    print("用户扣子平台注册ID更新")
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
        print(f"   原扣子平台ID: {user.coze_id if user.coze_id else '未填写'}")
        print()
        
        # 检查coze_id是否已被其他用户使用
        existing_user = db.query(User).filter(User.coze_id == coze_id).first()
        if existing_user and existing_user.id != user_id:
            print(f"❌ 扣子平台ID {coze_id} 已被其他用户使用")
            print(f"   用户ID: {existing_user.id}")
            print(f"   用户姓名: {existing_user.name}")
            return False
        
        # 更新扣子平台ID
        old_coze_id = user.coze_id
        user.coze_id = coze_id
        user.updated_at = datetime.now()
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print("✅ 扣子平台注册ID更新成功!")
        print()
        print("="*70)
        print("更新结果")
        print("="*70)
        print(f"ID: {user.id}")
        print(f"姓名: {user.name}")
        print(f"邮箱: {user.email}")
        print(f"原扣子平台ID: {old_coze_id if old_coze_id else '未填写'}")
        print(f"新扣子平台ID: {user.coze_id}")
        print(f"更新时间: {user.updated_at}")
        print()
        
        # 记录审计日志
        audit_log = AuditLog(
            user_id=user.id,
            action='update_coze_id',
            resource_type='user',
            resource_id=user.id,
            description=f'用户更新扣子平台注册ID: {old_coze_id if old_coze_id else "未填写"} -> {coze_id}',
            status='success',
            created_at=datetime.now()
        )
        db.add(audit_log)
        db.commit()
        
        print("✅ 审计日志已记录")
        print()
        print("🔹 扣子平台注册ID已作为用户标识之一")
        print("🔹 可用于用户身份识别和关联")
        print()
        print("="*70)
        print("✅ 扣子平台注册ID更新完成")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 扣子平台注册ID更新失败: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    # 更新用户扣子平台注册ID
    user_id = 1  # 超级管理员ID
    coze_id = "2118934385"
    
    success = update_user_coze_id(user_id, coze_id)
    exit(0 if success else 1)
