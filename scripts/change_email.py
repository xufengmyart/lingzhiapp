"""
修改超级管理员邮箱脚本
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


def change_super_admin_email(old_email: str, new_email: str):
    """修改超级管理员邮箱"""
    
    print("="*70)
    print("超级管理员邮箱修改")
    print("="*70)
    print()
    
    # 获取数据库会话
    db = get_session()
    
    try:
        # 查询超级管理员
        super_admin = db.query(User).filter(
            User.is_superuser == True,
            User.email == old_email
        ).first()
        
        if not super_admin:
            print(f"❌ 未找到邮箱为 {old_email} 的超级管理员")
            return False
        
        print(f"📋 当前超级管理员信息:")
        print(f"   ID: {super_admin.id}")
        print(f"   姓名: {super_admin.name}")
        print(f"   原邮箱: {super_admin.email}")
        print()
        
        # 检查新邮箱是否已被使用
        existing_user = db.query(User).filter(User.email == new_email).first()
        if existing_user:
            print(f"❌ 邮箱 {new_email} 已被其他用户使用")
            print(f"   用户ID: {existing_user.id}")
            print(f"   用户姓名: {existing_user.name}")
            return False
        
        print("✅ 新邮箱可用")
        print()
        
        # 更新邮箱
        old_email = super_admin.email
        super_admin.email = new_email
        super_admin.updated_at = datetime.now()
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print("✅ 邮箱修改成功!")
        print()
        print("="*70)
        print("新邮箱信息")
        print("="*70)
        print(f"姓名: {super_admin.name}")
        print(f"原邮箱: {old_email}")
        print(f"新邮箱: {super_admin.email}")
        print(f"更新时间: {super_admin.updated_at}")
        print()
        
        # 记录审计日志
        audit_log = AuditLog(
            user_id=super_admin.id,
            action='change_email',
            resource_type='user',
            resource_id=super_admin.id,
            description=f'超级管理员修改邮箱: {old_email} -> {new_email}',
            status='success',
            created_at=datetime.now()
        )
        db.add(audit_log)
        db.commit()
        
        print("✅ 审计日志已记录")
        print()
        
        # 更新配置文件中的邮箱
        try:
            import json
            config_path = os.path.join(workspace_path, 'src/config/super_admin_config.py')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换邮箱配置
            old_config = f'SUPER_ADMIN_EMAIL: str = "{old_email}"'
            new_config = f'SUPER_ADMIN_EMAIL: str = "{new_email}"'
            
            if old_config in content:
                content = content.replace(old_config, new_config)
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ 配置文件已同步更新")
            else:
                print("⚠️  配置文件未找到邮箱配置，跳过同步")
        except Exception as e:
            print(f"⚠️  配置文件更新失败: {e}")
        
        print()
        print("="*70)
        print("⚠️  重要提醒")
        print("="*70)
        print("1. 请使用新邮箱登录系统")
        print("2. 如有第三方绑定，请及时更新邮箱信息")
        print("3. 请确保新邮箱地址可以正常接收邮件")
        print("4. 建议定期更换密码（建议每90天）")
        print()
        print("="*70)
        print("✅ 邮箱修改完成")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 邮箱修改失败: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    # 修改超级管理员邮箱
    old_email = "admin@lingzhi.eco"
    new_email = "xufeng@meiyueart.cn"
    
    success = change_super_admin_email(old_email, new_email)
    exit(0 if success else 1)
