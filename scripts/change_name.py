"""
修改超级管理员姓名脚本
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


def change_super_admin_name(old_name: str, new_name: str):
    """修改超级管理员姓名"""
    
    print("="*70)
    print("超级管理员姓名修改")
    print("="*70)
    print()
    
    # 获取数据库会话
    db = get_session()
    
    try:
        # 查询超级管理员
        super_admin = db.query(User).filter(
            User.is_superuser == True,
            User.name == old_name
        ).first()
        
        if not super_admin:
            print(f"❌ 未找到姓名为 {old_name} 的超级管理员")
            return False
        
        print(f"📋 当前超级管理员信息:")
        print(f"   ID: {super_admin.id}")
        print(f"   原姓名: {super_admin.name}")
        print(f"   邮箱: {super_admin.email}")
        print()
        
        # 更新姓名
        old_name = super_admin.name
        super_admin.name = new_name
        super_admin.updated_at = datetime.now()
        
        db.add(super_admin)
        db.commit()
        db.refresh(super_admin)
        
        print("✅ 姓名修改成功!")
        print()
        print("="*70)
        print("新姓名信息")
        print("="*70)
        print(f"ID: {super_admin.id}")
        print(f"原姓名: {old_name}")
        print(f"新姓名: {super_admin.name}")
        print(f"邮箱: {super_admin.email}")
        print(f"更新时间: {super_admin.updated_at}")
        print()
        
        # 记录审计日志
        audit_log = AuditLog(
            user_id=super_admin.id,
            action='change_name',
            resource_type='user',
            resource_id=super_admin.id,
            description=f'超级管理员修改姓名: {old_name} -> {new_name}',
            status='success',
            created_at=datetime.now()
        )
        db.add(audit_log)
        db.commit()
        
        print("✅ 审计日志已记录")
        print()
        
        # 更新配置文件中的姓名
        try:
            config_path = os.path.join(workspace_path, 'src/config/super_admin_config.py')
            
            with open(config_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 替换姓名配置
            old_config = f'SUPER_ADMIN_NAME: str = "{old_name}"'
            new_config = f'SUPER_ADMIN_NAME: str = "{new_name}"'
            
            if old_config in content:
                content = content.replace(old_config, new_config)
                
                with open(config_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                print("✅ 配置文件已同步更新")
            else:
                print("⚠️  配置文件未找到姓名配置，跳过同步")
        except Exception as e:
            print(f"⚠️  配置文件更新失败: {e}")
        
        print()
        print("="*70)
        print("✅ 姓名修改完成")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"❌ 姓名修改失败: {e}")
        import traceback
        traceback.print_exc()
        if 'db' in locals():
            db.rollback()
        return False
    finally:
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    # 修改超级管理员姓名
    old_name = "系统超级管理员"
    new_name = "许锋"
    
    success = change_super_admin_name(old_name, new_name)
    exit(0 if success else 1)
