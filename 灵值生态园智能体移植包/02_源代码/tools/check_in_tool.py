"""
签到工具
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from typing import Optional
from datetime import datetime


@tool
def check_in(runtime: ToolRuntime = None) -> str:
    """用户签到

    每个用户每天只能签到一次，签到成功可获得10灵值。

    Returns:
        str: 签到结果
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.check_in_manager import CheckInManager
    ctx = runtime.context

    # 从上下文中获取用户ID
    user_id = ctx.get('user_id') if ctx else None
    if not user_id:
        return """
【签到失败】

❌ 无法获取用户ID
请确保您已正确登录系统。
"""

    # 获取数据库会话
    db = get_session()

    try:
        # 创建签到管理器
        manager = CheckInManager()

        # 执行签到
        success, message, check_in = manager.check_in(db, user_id)

        if success:
            result = f"""
【签到成功】✅

{message}

🎁 奖励信息：
- 获得：{check_in.lingzhi_reward}灵值
- 签到时间：{check_in.created_at.strftime('%Y-%m-%d %H:%M:%S')}

💡 提示：
- 每天只能签到一次
- 明天记得再来签到哦！
"""
            return result
        else:
            return f"""
【签到失败】

❌ {message}
"""

    except Exception as e:
        return f"""
【签到失败】

❌ 签到过程中发生错误：{str(e)}

请稍后重试或联系系统管理员。
"""
    finally:
        db.close()


@tool
def get_check_in_history(
    days: int = 30,
    runtime: ToolRuntime = None
) -> str:
    """获取签到历史记录

    Args:
        days: 查询天数（默认30天）

    Returns:
        str: 签到历史记录
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.check_in_manager import CheckInManager
    ctx = runtime.context

    # 从上下文中获取用户ID
    user_id = ctx.get('user_id') if ctx else None
    if not user_id:
        return """
【获取签到历史失败】

❌ 无法获取用户ID
请确保您已正确登录系统。
"""

    # 获取数据库会话
    db = get_session()

    try:
        # 创建签到管理器
        manager = CheckInManager()

        # 获取签到历史
        history = manager.format_check_in_history(db, user_id, days)

        return history

    except Exception as e:
        return f"""
【获取签到历史失败】

❌ 获取签到历史时发生错误：{str(e)}

请稍后重试或联系系统管理员。
"""
    finally:
        db.close()


@tool
def get_today_check_in_status(runtime: ToolRuntime = None) -> str:
    """获取今天的签到状态

    Returns:
        str: 今天的签到状态
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.check_in_manager import CheckInManager
    ctx = runtime.context

    # 从上下文中获取用户ID
    user_id = ctx.get('user_id') if ctx else None
    if not user_id:
        return """
【获取签到状态失败】

❌ 无法获取用户ID
请确保您已正确登录系统。
"""

    # 获取数据库会话
    db = get_session()

    try:
        # 创建签到管理器
        manager = CheckInManager()

        # 检查今天是否已签到
        has_checked_in = manager.has_checked_in_today(db, user_id)

        result = f"""
【今日签到状态】

{'✅ 已签到' if has_checked_in else '❌ 未签到'}

🔹 签到规则：
- 每天只能签到一次
- 签到成功可获得10灵值
- 签到时间：每天00:00-23:59

{'🎉 您今天已经签到过了，明天再来吧！' if has_checked_in else '📢 您今天还没有签到，快去签到吧！'}
"""

        return result

    except Exception as e:
        return f"""
【获取签到状态失败】

❌ 获取签到状态时发生错误：{str(e)}

请稍后重试或联系系统管理员。
"""
    finally:
        db.close()


@tool
def get_today_check_in_statistics(runtime: ToolRuntime = None) -> str:
    """获取今天的签到统计信息

    Returns:
        str: 今天的签到统计
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.check_in_manager import CheckInManager

    # 获取数据库会话
    db = get_session()

    try:
        # 创建签到管理器
        manager = CheckInManager()

        # 获取今天的签到统计
        count = manager.get_today_check_in_count(db)

        result = f"""
【今日签到统计】

📊 数据统计：
- 今日签到人数：{count}人
- 累计发放灵值：{count * manager.daily_reward}灵值

💡 说明：
- 统计时间：{datetime.now().strftime('%Y-%m-%d')}
- 签到奖励：每人10灵值
"""

        return result

    except Exception as e:
        return f"""
【获取签到统计失败】

❌ 获取签到统计时发生错误：{str(e)}

请稍后重试或联系系统管理员。
"""
    finally:
        db.close()
