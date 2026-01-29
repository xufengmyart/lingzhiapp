"""
查询用户登记信息脚本
"""

import sys
import os

# 添加项目路径到 sys.path
workspace_path = os.getenv('COZE_WORKSPACE_PATH', '/workspace/projects')
if workspace_path not in sys.path:
    sys.path.insert(0, workspace_path)

from coze_coding_dev_sdk.database import get_session
from src.storage.database.shared.model import User, Role, Permission


def query_user_info():
    """查询用户登记信息"""
    
    print("="*70)
    print("用户登记信息查询")
    print("="*70)
    print()
    
    # 获取数据库会话
    db = get_session()
    
    try:
        # 查询所有用户
        users = db.query(User).all()
        
        if not users:
            print("⚠️  系统中暂无用户登记信息")
            return
        
        print(f"📋 用户总数: {len(users)}")
        print()
        
        # 显示每个用户的信息
        for i, user in enumerate(users, 1):
            print("="*70)
            print(f"用户 #{i}")
            print("="*70)
            print(f"ID: {user.id}")
            print(f"姓名: {user.name}")
            print(f"邮箱: {user.email}")
            print(f"电话: {user.phone if user.phone else '未填写'}")
            print(f"微信号: {user.wechat if user.wechat else '未填写'}")
            print(f"扣子平台ID: {user.coze_id if user.coze_id else '未填写'}")
            print(f"部门: {user.department if user.department else '未填写'}")
            print(f"职位: {user.position if user.position else '未填写'}")
            print(f"状态: {user.status}")
            print(f"超级管理员: {'是' if user.is_superuser else '否'}")
            print(f"CEO: {'是' if user.is_ceo else '否'}")
            print(f"双因素认证: {'已启用' if user.two_factor_enabled else '未启用'}")
            print(f"IP白名单: {'已配置' if user.ip_whitelist else '未配置'}")
            print(f"最后登录: {user.last_login if user.last_login else '从未登录'}")
            print(f"创建时间: {user.created_at}")
            print(f"更新时间: {user.updated_at}")
            
            # 查询用户角色
            if user.roles:
                print(f"角色: {', '.join([role.name for role in user.roles])}")
            else:
                print(f"角色: 未分配")
            
            # 查询创建人
            if user.created_user:
                print(f"创建人: {user.created_user.name} (ID: {user.created_user.id})")
            else:
                print(f"创建人: 系统")
            
            print()
        
        # 统计信息
        print("="*70)
        print("统计信息")
        print("="*70)
        super_admin_count = sum(1 for user in users if user.is_superuser)
        ceo_count = sum(1 for user in users if user.is_ceo)
        active_count = sum(1 for user in users if user.status == 'active')
        
        print(f"超级管理员: {super_admin_count}人")
        print(f"CEO: {ceo_count}人")
        print(f"活跃用户: {active_count}人")
        print()
        
        # 超级管理员详细信息
        super_admins = [user for user in users if user.is_superuser]
        if super_admins:
            print("="*70)
            print("超级管理员详细信息")
            print("="*70)
            for admin in super_admins:
                print(f"姓名: {admin.name}")
                print(f"邮箱: {admin.email}")
                print(f"创建时间: {admin.created_at}")
                print(f"最后登录: {admin.last_login if admin.last_login else '从未登录'}")
                print(f"双因素认证: {'✅ 已启用' if admin.two_factor_enabled else '❌ 未启用'}")
                print(f"IP白名单: {'✅ 已配置' if admin.ip_whitelist else '❌ 未配置'}")
                
                # 显示权限
                permissions = admin.get_all_permissions()
                print(f"权限: {'所有权限' if permissions == ['all'] else f'{len(permissions)}个权限'}")
                print()
        
        print("="*70)
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    query_user_info()
