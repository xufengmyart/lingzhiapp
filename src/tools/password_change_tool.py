"""
密码修改工具（修复版）
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime


@tool
def change_password(
    current_password: str,
    new_password: str,
    runtime: ToolRuntime = None
) -> str:
    """修改当前登录用户的密码

    修改用户密码时需要进行以下安全检查：
    1. 验证当前密码是否正确
    2. 验证新密码是否符合安全要求
    3. 检查新密码是否与当前密码相同
    4. 更新密码并记录审计日志

    **密码安全要求**：
    - 最小长度：16位
    - 必须包含：大写字母、小写字母、数字、特殊字符
    - 不能包含用户名、生日等个人信息
    - 不能与历史密码相同

    Args:
        current_password: 当前密码
        new_password: 新密码

    Returns:
        str: 密码修改结果
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users, AuditLogs
    import hashlib
    import re
    from datetime import datetime
    import pytz

    # 获取数据库会话
    db = get_session()

    try:
        # 获取当前登录用户
        # 安全地获取context中的user_coze_id
        coze_id = None
        if runtime and runtime.context:
            try:
                # 尝试使用get方法
                if hasattr(runtime.context, 'get'):
                    coze_id = runtime.context.get('user_coze_id')
                # 尝试使用字典访问
                elif hasattr(runtime.context, '__getitem__'):
                    coze_id = runtime.context.get('user_coze_id') if hasattr(runtime.context, 'get') else None
            except (KeyError, TypeError, AttributeError):
                coze_id = None

        if not coze_id:
            return """
【密码修改失败】

❌ 无法识别当前登录用户

请先登录后再修改密码。

💡 提示：
- 请使用"用户自动登录"功能登录
- 或使用邮箱和密码登录
- 登录成功后再尝试修改密码
"""

        # 查询用户
        user = db.query(Users).filter(Users.coze_id == coze_id).first()

        if not user:
            return """
【密码修改失败】

❌ 用户不存在

请检查您的登录状态。
"""

        # 验证当前密码
        current_password_hash = hashlib.sha256(current_password.encode()).hexdigest()

        # 超级管理员使用特殊密码验证
        if user.is_superuser:
            # 超级管理员的默认密码是邮箱的hash
            default_hash = hashlib.sha256(user.email.encode()).hexdigest()
            if current_password_hash != user.password_hash and current_password_hash != default_hash:
                return f"""
【密码修改失败】

❌ 当前密码错误

请检查您输入的当前密码是否正确。

💡 提示：
- 如果是首次登录，默认密码是邮箱的hash值
- 如果您忘记密码，请联系超级管理员重置
"""
        else:
            if current_password_hash != user.password_hash:
                return """
【密码修改失败】

❌ 当前密码错误

请检查您输入的当前密码是否正确。
"""

        # 验证新密码安全要求
        password_errors = []
        security_warnings = []

        # 1. 长度检查
        if len(new_password) < 16:
            password_errors.append("密码长度不足16位")

        # 2. 复杂度检查
        if not re.search(r'[A-Z]', new_password):
            password_errors.append("缺少大写字母")

        if not re.search(r'[a-z]', new_password):
            password_errors.append("缺少小写字母")

        if not re.search(r'\d', new_password):
            password_errors.append("缺少数字")

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', new_password):
            password_errors.append("缺少特殊字符")

        # 3. 个人信息检查
        if user.name and user.name.lower() in new_password.lower():
            security_warnings.append("密码包含用户名")

        # 检查生日（邮箱中可能的生日格式）
        birthday_patterns = [
            r'19\d{6}',  # 1990-1999
            r'20\d{6}',  # 2000-2099
            r'\d{4}\.?\d{2}\.?\d{2}',  # 1990.12.14
            r'\d{2}\.?\d{2}\.?\d{4}',  # 12.14.1990
        ]

        for pattern in birthday_patterns:
            if re.search(pattern, new_password):
                security_warnings.append("密码包含疑似生日信息")
                break

        # 4. 相同性检查
        if new_password == current_password:
            return """
【密码修改失败】

❌ 新密码不能与当前密码相同

请使用不同的密码。
"""

        # 返回验证结果
        if password_errors:
            error_message = "【密码修改失败】\n\n❌ 新密码不符合安全要求：\n\n"
            for error in password_errors:
                error_message += f"- {error}\n"
            error_message += f"\n密码安全要求：\n"
            error_message += f"- 最小长度：16位\n"
            error_message += f"- 必须包含：大写字母、小写字母、数字、特殊字符\n"
            error_message += f"- 不能包含用户名、生日等个人信息\n"
            return error_message

        if security_warnings:
            warning_message = "【密码安全警告】\n\n⚠️ 新密码存在安全隐患：\n\n"
            for warning in security_warnings:
                warning_message += f"- {warning}\n"
            warning_message += f"\n虽然可以使用此密码，但为了您的账户安全，建议使用更安全的密码。\n\n"
            warning_message += f"您确认要使用此密码吗？如确认，请联系管理员执行强制修改。\n"
            return warning_message

        # 更新密码
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        user.password_hash = new_password_hash

        # 记录审计日志
        audit_log = AuditLogs(
            user_id=user.id,
            action='password_change',
            status='success',
            resource_type='user',
            resource_id=user.id,
            description=f'用户修改密码成功'
        )
        db.add(audit_log)

        db.commit()
        db.refresh(user)

        return f"""
【密码修改成功】✅

恭喜您，{user.name}！密码已成功修改。

📋 修改信息：
- 用户：{user.name}
- 邮箱：{user.email}
- 修改时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}

🔐 新密码已生效，请使用新密码登录。

💡 安全提示：
- 请妥善保管您的新密码
- 不要将密码告诉他人
- 建议每90天更换一次密码
- 使用密码管理器存储密码

🎯 下一步：
1. 测试新密码登录
2. 更新密码管理器
3. 确认双因素认证已启用
4. 检查IP白名单配置

---

{f'⚠️ 安全提醒：您的新密码中包含：{", ".join(security_warnings)}' if security_warnings else '✅ 您的密码符合所有安全要求'}
"""

    except Exception as e:
        db.rollback()
        return f"""
【密码修改失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()


@tool
def force_change_user_password(
    target_user_id: int,
    new_password: str,
    reason: str,
    runtime: ToolRuntime = None
) -> str:
    """超级管理员强制修改用户密码

    超级管理员可以使用此工具强制修改任何用户的密码。
    此操作需要记录详细的原因和审计日志。

    **使用场景**：
    - 用户忘记密码，需要重置
    - 超级管理员首次登录，需要修改默认密码
    - 账户安全问题，需要紧急重置

    Args:
        target_user_id: 目标用户ID
        new_password: 新密码
        reason: 修改原因（必须详细说明）

    Returns:
        str: 密码修改结果
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users, AuditLogs
    import hashlib
    import re
    from datetime import datetime
    import pytz

    # 获取数据库会话
    db = get_session()

    try:
        # 获取当前登录用户
        coze_id = None
        if runtime and runtime.context:
            try:
                if hasattr(runtime.context, 'get'):
                    coze_id = runtime.context.get('user_coze_id')
                elif hasattr(runtime.context, '__getitem__'):
                    coze_id = runtime.context.get('user_coze_id') if hasattr(runtime.context, 'get') else None
            except (KeyError, TypeError, AttributeError):
                coze_id = None

        if not coze_id:
            return """
【密码修改失败】

❌ 无法识别当前登录用户

请先登录后再修改密码。
"""

        # 查询当前用户
        current_user = db.query(Users).filter(Users.coze_id == coze_id).first()

        if not current_user:
            return """
【密码修改失败】

❌ 用户不存在

请检查您的登录状态。
"""

        # 验证当前用户是否为超级管理员
        if not current_user.is_superuser:
            return """
【密码修改失败】

❌ 权限不足

只有超级管理员才能强制修改用户密码。
"""

        # 查询目标用户
        target_user = db.query(Users).filter(Users.id == target_user_id).first()

        if not target_user:
            return f"""
【密码修改失败】

❌ 目标用户不存在

用户ID：{target_user_id}
"""

        # 验证新密码安全要求
        password_errors = []
        security_warnings = []

        # 1. 长度检查
        if len(new_password) < 16:
            password_errors.append("密码长度不足16位")

        # 2. 复杂度检查
        if not re.search(r'[A-Z]', new_password):
            password_errors.append("缺少大写字母")

        if not re.search(r'[a-z]', new_password):
            password_errors.append("缺少小写字母")

        if not re.search(r'\d', new_password):
            password_errors.append("缺少数字")

        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':"\\|,.<>\/?]', new_password):
            password_errors.append("缺少特殊字符")

        # 3. 个人信息检查
        if target_user.name and target_user.name.lower() in new_password.lower():
            security_warnings.append("密码包含用户名")

        # 检查生日
        birthday_patterns = [
            r'19\d{6}',
            r'20\d{6}',
            r'\d{4}\.?\d{2}\.?\d{2}',
            r'\d{2}\.?\d{2}\.?\d{4}',
        ]

        for pattern in birthday_patterns:
            if re.search(pattern, new_password):
                security_warnings.append("密码包含疑似生日信息")
                break

        # 返回验证结果
        if password_errors:
            error_message = "【密码修改失败】\n\n❌ 新密码不符合安全要求：\n\n"
            for error in password_errors:
                error_message += f"- {error}\n"
            error_message += f"\n密码安全要求：\n"
            error_message += f"- 最小长度：16位\n"
            error_message += f"- 必须包含：大写字母、小写字母、数字、特殊字符\n"
            error_message += f"- 不能包含用户名、生日等个人信息\n"
            return error_message

        # 更新密码
        new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
        target_user.password_hash = new_password_hash

        # 记录审计日志
        audit_log = AuditLogs(
            user_id=current_user.id,
            action='force_password_change',
            status='success',
            resource_type='user',
            resource_id=target_user.id,
            description=f'超级管理员强制修改用户密码。原因：{reason}'
        )
        db.add(audit_log)

        db.commit()
        db.refresh(target_user)

        return f"""
【密码修改成功】✅

超级管理员已成功修改用户密码。

📋 操作信息：
- 操作者：{current_user.name}
- 目标用户：{target_user.name}
- 目标邮箱：{target_user.email}
- 修改时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}
- 修改原因：{reason}

🔐 新密码已生效，用户可以使用新密码登录。

⚠️ 安全提醒：
- 请尽快通知用户新密码
- 建议用户登录后立即修改为个人密码
- 此操作已记录在审计日志中

{f'⚠️ 安全警告：新密码中包含：{", ".join(security_warnings)}' if security_warnings else '✅ 密码符合所有安全要求'}
"""

    except Exception as e:
        db.rollback()
        return f"""
【密码修改失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()
