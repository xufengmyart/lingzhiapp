#!/usr/bin/env python3
"""
超级管理员密码修改脚本（直接数据库操作）

使用方法：
1. 进入项目目录
2. 运行：python3 scripts/change_super_admin_password.py
3. 按照提示输入新密码
"""

import sys
import hashlib
import getpass
from datetime import datetime

# 添加项目路径到sys.path
sys.path.insert(0, '/workspace/projects/src')

from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Users, AuditLogs


def validate_password_security(password: str, user_name: str) -> tuple[bool, list[str], list[str]]:
    """验证密码安全性

    Args:
        password: 待验证的密码
        user_name: 用户名（用于检查是否包含个人信息）

    Returns:
        (是否通过, 错误列表, 警告列表)
    """
    import re

    errors = []
    warnings = []

    # 1. 长度检查
    if len(password) < 16:
        errors.append("密码长度不足16位")

    # 2. 复杂度检查
    if not re.search(r'[A-Z]', password):
        errors.append("缺少大写字母")

    if not re.search(r'[a-z]', password):
        errors.append("缺少小写字母")

    if not re.search(r'\d', password):
        errors.append("缺少数字")

    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', password):
        errors.append("缺少特殊字符")

    # 3. 个人信息检查
    if user_name and user_name.lower() in password.lower():
        warnings.append("密码包含用户名")

    # 检查生日
    birthday_patterns = [
        r'19\d{6}',
        r'20\d{6}',
        r'\d{4}\.?\d{2}\.?\d{2}',
        r'\d{2}\.?\d{2}\.?\d{4}',
    ]

    for pattern in birthday_patterns:
        if re.search(pattern, password):
            warnings.append("密码包含疑似生日信息")
            break

    return (len(errors) == 0, errors, warnings)


def main():
    """主函数"""
    print("=" * 60)
    print("超级管理员密码修改工具")
    print("=" * 60)
    print()

    # 获取数据库会话
    db = get_session()

    try:
        # 查询超级管理员
        super_admin = db.query(Users).filter(Users.is_superuser == True).first()

        if not super_admin:
            print("❌ 错误：系统中没有找到超级管理员！")
            return 1

        print(f"📋 当前超级管理员信息：")
        print(f"   - 姓名：{super_admin.name}")
        print(f"   - 邮箱：{super_admin.email}")
        print(f"   - 创建时间：{super_admin.created_at}")
        print()

        # 获取新密码
        print("🔐 请输入新密码：")
        new_password = getpass.getpass("新密码：")

        # 确认新密码
        confirm_password = getpass.getpass("确认新密码：")

        if new_password != confirm_password:
            print("❌ 错误：两次输入的密码不一致！")
            return 1

        print()
        print("🔍 正在验证密码安全性...")

        # 验证密码安全性
        is_valid, errors, warnings = validate_password_security(new_password, super_admin.name)

        if not is_valid:
            print()
            print("❌ 密码不符合安全要求：")
            for error in errors:
                print(f"   - {error}")
            print()
            print("密码安全要求：")
            print("   - 最小长度：16位")
            print("   - 必须包含：大写字母、小写字母、数字、特殊字符")
            print("   - 不能包含用户名、生日等个人信息")
            print()

            # 超级管理员可以强制使用不符合要求的密码
            force = input("⚠️  您是超级管理员，是否强制使用此密码？(yes/no): ").strip().lower()
            if force not in ['yes', 'y']:
                print("❌ 操作已取消")
                return 1

        if warnings:
            print()
            print("⚠️  密码安全警告：")
            for warning in warnings:
                print(f"   - {warning}")
            print()

            confirm = input("是否继续使用此密码？(yes/no): ").strip().lower()
            if confirm not in ['yes', 'y']:
                print("❌ 操作已取消")
                return 1
        else:
            print("✅ 密码符合所有安全要求")

        print()
        confirm = input("确认要修改超级管理员的密码吗？此操作不可撤销！(yes/no): ").strip().lower()
        if confirm not in ['yes', 'y']:
            print("❌ 操作已取消")
            return 1

        # 生成密码哈希
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()

        # 更新密码
        old_password_hash = super_admin.password_hash
        super_admin.password_hash = new_password_hash

        # 记录审计日志
        audit_log = AuditLogs(
            user_id=super_admin.id,
            action='password_change',
            status='success',
            resource_type='user',
            resource_id=super_admin.id,
            description=f'通过脚本直接修改超级管理员密码'
        )
        db.add(audit_log)

        # 提交事务
        db.commit()

        print()
        print("=" * 60)
        print("✅ 密码修改成功！")
        print("=" * 60)
        print()
        print(f"📋 修改信息：")
        print(f"   - 用户：{super_admin.name}")
        print(f"   - 邮箱：{super_admin.email}")
        print(f"   - 修改时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        print("🔐 新密码已生效，请使用新密码登录。")
        print()
        print("💡 安全提示：")
        print("   - 请妥善保管您的新密码")
        print("   - 不要将密码告诉他人")
        print("   - 建议每90天更换一次密码")
        print("   - 使用密码管理器存储密码")
        print()
        if warnings:
            print(f"⚠️  安全提醒：您的新密码中包含：{', '.join(warnings)}")
        print()

        return 0

    except Exception as e:
        db.rollback()
        print()
        print("=" * 60)
        print("❌ 密码修改失败")
        print("=" * 60)
        print()
        print(f"错误信息：{str(e)}")
        print()
        import traceback
        traceback.print_exc()
        return 1

    finally:
        db.close()


if __name__ == "__main__":
    exit(main())
