#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵值生态园 - 修改管理员密码脚本
Change Admin Password Script

Author: Coze Coding
Version: 1.0.0
"""

import os
import sys
import getpass

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app
from app.extensions import db
from app.models import Admin


def change_admin_password():
    """修改管理员密码"""

    print("=" * 50)
    print("灵值生态园 - 修改管理员密码")
    print("=" * 50)
    print()

    # 创建应用上下文
    app = create_app('production')

    with app.app_context():
        # 查询所有管理员
        admins = Admin.query.all()

        if not admins:
            print("❌ 未找到管理员账户")
            return False

        print(f"找到 {len(admins)} 个管理员账户:")
        for admin in admins:
            print(f"  - ID: {admin.id}, 用户名: {admin.username}, 角色: {admin.role}")
        print()

        # 选择管理员
        username = input("请输入要修改密码的管理员用户名: ").strip()

        admin = Admin.query.filter_by(username=username).first()

        if not admin:
            print(f"❌ 未找到用户名为 '{username}' 的管理员")
            return False

        # 输入新密码
        print(f"\n为管理员 '{username}' 设置新密码")

        while True:
            new_password = getpass.getpass("请输入新密码（至少 6 位）: ")
            if len(new_password) < 6:
                print("❌ 密码长度不能少于 6 位")
                continue

            confirm_password = getpass.getpass("请再次输入新密码: ")

            if new_password != confirm_password:
                print("❌ 两次输入的密码不一致")
                continue

            break

        # 更新密码
        admin.set_password(new_password)
        db.session.commit()

        print()
        print("✅ 密码修改成功！")
        print(f"用户名: {admin.username}")
        print(f"角色: {admin.role}")
        print(f"修改时间: {admin.updated_at}")
        print()
        print("⚠️  请妥善保管新密码！")

        return True


def main():
    """主函数"""
    try:
        success = change_admin_password()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ 操作已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
