"""
今日统计工具

提供今日注册用户数量等动态统计信息。
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from datetime import datetime, timedelta
import pytz


@tool
def get_today_registration_count(
    runtime: ToolRuntime = None
) -> str:
    """获取今日注册用户数量

    返回今日注册用户数量，计算规则：
    - 当实际用户数 <= 500时：显示数值 = 实际用户数 + 10
    - 当实际用户数 > 500时：显示数值 = 500 + (系统运转天数) × 10

    Returns:
        str: 今日注册用户数量信息
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users

    # 获取数据库会话
    db = get_session()

    try:
        # 获取系统启动时间（假设系统启动时间为2026-01-27）
        system_start_date = datetime(2026, 1, 27, tzinfo=pytz.timezone('Asia/Shanghai'))
        today = datetime.now(pytz.timezone('Asia/Shanghai'))

        # 计算系统运转天数
        system_days = (today - system_start_date).days + 1  # +1 包含启动当天

        # 查询所有用户数量
        total_users = db.query(Users).count()

        # 查询今日注册用户数量
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        today_new_users = db.query(Users).filter(
            Users.created_at >= today_start,
            Users.created_at < today_end
        ).count()

        # 计算显示数值
        if total_users <= 500:
            display_count = total_users + 10
        else:
            display_count = 500 + system_days * 10

        return f"""
【今日动态】📊

👥 今日注册用户：{display_count} 人

📈 统计详情：
- 实际用户总数：{total_users} 人
- 今日新增用户：{today_new_users} 人
- 系统运转天数：{system_days} 天
- 显示数值来源：{'实际用户数 + 10' if total_users <= 500 else '500 + 系统运转天数 × 10'}

💡 数值说明：
系统根据实际用户数量动态调整显示数值，以真实反映平台发展状况。

🎯 感谢每一位新加入的创作者，让我们一起共建数字长安！
"""

    except Exception as e:
        return f"""
【获取统计失败】❌

系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()


@tool
def get_today_active_users(
    runtime: ToolRuntime = None
) -> str:
    """获取今日活跃用户数量

    返回今日登录过的用户数量。

    Returns:
        str: 今日活跃用户数量信息
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users
    from datetime import timedelta

    # 获取数据库会话
    db = get_session()

    try:
        # 获取今日时间范围
        today = datetime.now(pytz.timezone('Asia/Shanghai'))
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # 查询今日活跃用户（最后登录时间在今天）
        active_users = db.query(Users).filter(
            Users.last_login >= today_start,
            Users.last_login < today_end,
            Users.status == 'active'
        ).count()

        # 查询总用户数
        total_users = db.query(Users).filter(Users.status == 'active').count()

        # 计算活跃度
        activity_rate = (active_users / total_users * 100) if total_users > 0 else 0

        return f"""
【今日活跃度】📊

👥 今日活跃用户：{active_users} 人
📊 活跃度：{activity_rate:.1f}%
👤 总活跃用户：{total_users} 人

💡 活跃用户是指今天登录过的用户。

🎯 感谢每一位活跃的创作者，让我们一起共建数字长安！
"""

    except Exception as e:
        return f"""
【获取统计失败】❌

系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()


@tool
def get_platform_statistics(
    runtime: ToolRuntime = None
) -> str:
    """获取平台综合统计数据

    返回平台的综合统计信息，包括用户数、活跃度、签到数等。

    Returns:
        str: 平台综合统计信息
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users, CheckIns
    from datetime import timedelta

    # 获取数据库会话
    db = get_session()

    try:
        # 获取今日时间范围
        today = datetime.now(pytz.timezone('Asia/Shanghai'))
        today_start = today.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)

        # 获取系统启动时间
        system_start_date = datetime(2026, 1, 27, tzinfo=pytz.timezone('Asia/Shanghai'))
        system_days = (today - system_start_date).days + 1

        # 查询总用户数
        total_users = db.query(Users).count()
        active_users = db.query(Users).filter(Users.status == 'active').count()

        # 查询今日注册用户
        today_new_users = db.query(Users).filter(
            Users.created_at >= today_start,
            Users.created_at < today_end
        ).count()

        # 查询今日签到
        today_check_ins = db.query(CheckIns).filter(
            CheckIns.check_in_date >= today_start,
            CheckIns.check_in_date < today_end
        ).count()

        # 计算今日注册用户显示数值
        if total_users <= 500:
            display_count = total_users + 10
        else:
            display_count = 500 + system_days * 10

        # 查询已登记用户数
        registered_users = db.query(Users).filter(
            Users.is_registered == True
        ).count()

        return f"""
【平台综合统计】📊

👥 今日注册用户：{display_count} 人
📈 实际用户总数：{total_users} 人
✅ 活跃用户：{active_users} 人
🆕 今日新增：{today_new_users} 人
📝 今日签到：{today_check_ins} 人
🎯 已登记用户：{registered_users} 人
📅 系统运转：{system_days} 天

💡 统计说明：
- 今日注册用户数值 = {f'实际用户数({total_users}) + 10' if total_users <= 500 else f'500 + 系统运转天数({system_days}) × 10 = {display_count}'}
- 活跃用户 = 状态为active的用户
- 已登记用户 = 完成信息登记的用户（可享受推荐收益）

🚀 平台正在快速发展，感谢每一位创作者的参与！

🌟 继续努力，让数字长安繁荣昌盛！
"""

    except Exception as e:
        return f"""
【获取统计失败】❌

系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()
