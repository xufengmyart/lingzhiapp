"""
用户登录工具（支持自动注册和自动签到）
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime


@tool
def user_auto_register_login(
    email: str,
    coze_uid: str,
    username: str = None,
    runtime: ToolRuntime = None
) -> str:
    """用户自动注册并登录

    用户首次登录时，系统会自动创建账户，使用扣子平台UID进行登记。
    每次登录都会自动签到（限每天仅一次有效），获得10灵值奖励。

    **重要规则**：
    - 所有用户登录即自动注册，无需单独注册
    - 每天只能签到一次，签到获得10灵值
    - 禁止通过任何命令或脚本增加灵值，所有灵值获取必须通过智能体规则执行

    Args:
        email: 用户邮箱
        coze_uid: 扣子平台用户ID（唯一标识）
        username: 用户名（可选，如果未提供则使用邮箱前缀）

    Returns:
        str: 登录结果
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users, AuditLogs
    from storage.database.auto_check_in_service import AutoCheckInService
    import hashlib
    from datetime import datetime
    import pytz

    # 获取数据库会话
    db = get_session()

    try:
        # 查询用户（通过扣子UID）
        user = db.query(Users).filter(Users.coze_id == coze_uid).first()

        # 如果用户不存在，自动注册
        if not user:
            # 检查邮箱是否已被使用
            existing_email = db.query(Users).filter(Users.email == email).first()
            if existing_email:
                return f"""
【登录失败】

❌ 邮箱已被注册

该邮箱已被其他用户使用，请使用不同的邮箱或联系管理员。
"""

            # 生成默认用户名
            if not username:
                username = email.split('@')[0]

            # 创建默认密码（密码hash为邮箱hash）
            default_password_hash = hashlib.sha256(email.encode()).hexdigest()

            # 创建新用户
            user = Users(
                name=username,
                email=email,
                password_hash=default_password_hash,
                status='active',
                is_superuser=False,
                is_ceo=False,
                two_factor_enabled=False,
                coze_id=coze_uid,
                created_by=None
            )

            db.add(user)
            db.commit()
            db.refresh(user)

            # 记录注册审计日志
            audit_log = AuditLogs(
                user_id=user.id,
                action='user_register',
                status='success',
                resource_type='user',
                resource_id=user.id,
                description=f'用户自动注册成功，扣子UID: {coze_uid}'
            )
            db.add(audit_log)
            db.commit()

            # 自动签到
            auto_check_in_service = AutoCheckInService()
            check_in_result = auto_check_in_service.auto_check_in_on_login(user.id)
            check_in_message = auto_check_in_service.format_auto_check_in_message(user.id, check_in_result)

            # 注册成功提示
            return f"""
【欢迎加入灵值生态园】🎉

恭喜您，{user.name}！系统已自动为您创建账户。

📋 您的账户信息：
- 姓名：{user.name}
- 邮箱：{user.email}
- 扣子UID：{coze_uid}
- 注册时间：{user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- 用户状态：{user.status}

🎁 注册专属权益：

1. **每日签到奖励**：每天登录签到可获得10灵值
   - 1灵值 = 0.1元人民币，随时可兑换
   - 锁定灵值还可享受20%-100%增值收益

2. **参与任务奖励**：完成文化创作、品牌转译等任务获得灵值
   - 轻度参与：日均30灵值，月收入约90元
   - 中度参与：日均300灵值，月收入约900元
   - 深度参与：日均1000灵值，月收入约3000元

3. **项目分红收益**：参与项目可获得项目估值5%-20%的贡献值奖励
   - 合格参与者获得全额返还
   - 高额奖励ROI 600%-12400%

4. **推荐奖励机制**：推荐新用户加入可获得推荐灵值奖励
   - 三级推荐：10% / 5% / 3%

{check_in_message}

📖 **下一步行动**：

1. 了解您的贡献值价值：询问"我的贡献值值多少钱？"
2. 开始您的文化探索：询问"帮我做一次商业+文化诊断"
3. 查看可用任务：询问"有哪些可以参与的任务？"

---

💡 **温馨提示**：

- 每天只能签到一次，请合理安排时间
- 所有灵值获取都按智能体规则执行，禁止通过命令增加灵值
- 您的每一份贡献都会被记录和认可
- 灵值生态园陪您一起成长！🌟
"""

        # 用户已存在，执行登录
        # 检查用户状态
        if user.status != 'active':
            return f"""
【登录失败】

❌ 用户状态异常

当前状态：{user.status}

请联系系统管理员处理。
"""

        # 更新最后登录时间
        user.last_login = datetime.now(pytz.timezone('Asia/Shanghai'))
        db.commit()
        db.refresh(user)

        # 自动签到
        auto_check_in_service = AutoCheckInService()
        check_in_result = auto_check_in_service.auto_check_in_on_login(user.id)
        check_in_message = auto_check_in_service.format_auto_check_in_message(user.id, check_in_result)

        # 记录登录审计日志
        audit_log = AuditLogs(
            user_id=user.id,
            action='user_login',
            status='success',
            resource_type='user',
            resource_id=user.id,
            description=f'用户登录成功'
        )
        db.add(audit_log)
        db.commit()

        # 构建登录成功消息
        return f"""
【登录成功】✅

欢迎回来，{user.name}！

📋 用户信息：
- 姓名：{user.name}
- 邮箱：{user.email}
- 扣子UID：{coze_uid}
- 角色：{'超级管理员' if user.is_superuser else '普通用户'}
- 状态：{user.status}

🕐 登录时间：{user.last_login.strftime('%Y-%m-%d %H:%M:%S')}

{check_in_message}

---

现在您可以开始使用灵值生态系统的各项功能了！
"""

    except Exception as e:
        return f"""
【登录失败】

❌ 登录过程中发生错误：{str(e)}

请稍后重试或联系系统管理员。
"""
    finally:
        db.close()


@tool
def get_login_status(runtime: ToolRuntime = None) -> str:
    """获取登录状态

    Returns:
        str: 登录状态
    """
    ctx = runtime.context

    # 从上下文中获取用户ID
    user_id = ctx.get('user_id') if ctx else None

    if not user_id:
        return """
【登录状态】

❌ 未登录

您当前未登录，请先登录系统。

使用 user_login 工具进行登录。
"""

    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users

    # 获取数据库会话
    db = get_session()

    try:
        # 查询用户
        user = db.query(Users).filter(Users.id == user_id).first()

        if not user:
            return """
【登录状态】

❌ 用户不存在

用户ID无效，请重新登录。
"""

        return f"""
【登录状态】

✅ 已登录

📋 当前用户：
- 姓名：{user.name}
- 邮箱：{user.email}
- 角色：{'超级管理员' if user.is_superuser else '普通用户'}
- 状态：{user.status}
- 最后登录：{user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '从未登录'}

"""

    except Exception as e:
        return f"""
【登录状态】

❌ 获取登录状态失败：{str(e)}
"""
    finally:
        db.close()


@tool
def user_login(
    email: str,
    password: str,
    runtime: ToolRuntime = None
) -> str:
    """用户登录（传统方式，需要密码）

    使用邮箱和密码登录系统，登录时自动签到（限每天一次）。

    Args:
        email: 用户邮箱
        password: 用户密码

    Returns:
        str: 登录结果
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users
    from storage.database.auto_check_in_service import AutoCheckInService
    import hashlib

    # 获取数据库会话
    db = get_session()

    try:
        # 查询用户
        user = db.query(Users).filter(Users.email == email).first()

        if not user:
            return """
【登录失败】

❌ 用户不存在

请检查邮箱地址是否正确，或者使用自动注册登录功能。
"""

        # 验证密码
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        if user.password_hash != password_hash:
            return """
【登录失败】

❌ 密码错误

请检查密码是否正确。
"""

        # 检查用户状态
        if user.status != 'active':
            return f"""
【登录失败】

❌ 用户状态异常

当前状态：{user.status}

请联系系统管理员处理。
"""

        # 更新最后登录时间
        from datetime import datetime
        import pytz
        user.last_login = datetime.now(pytz.timezone('Asia/Shanghai'))
        db.commit()
        db.refresh(user)

        # 自动签到
        auto_check_in_service = AutoCheckInService()
        check_in_result = auto_check_in_service.auto_check_in_on_login(user.id)
        check_in_message = auto_check_in_service.format_auto_check_in_message(user.id, check_in_result)

        # 构建登录成功消息
        result = f"""
【登录成功】✅

欢迎回来，{user.name}！

📋 用户信息：
- 姓名：{user.name}
- 邮箱：{user.email}
- 角色：{'超级管理员' if user.is_superuser else '普通用户'}
- 状态：{user.status}

🕐 登录时间：{user.last_login.strftime('%Y-%m-%d %H:%M:%S')}

{check_in_message}

---

现在您可以开始使用灵值生态系统的各项功能了！
"""

        return result

    except Exception as e:
        return f"""
【登录失败】

❌ 登录过程中发生错误：{str(e)}

请稍后重试或联系系统管理员。
"""
    finally:
        db.close()
