"""
用户查询工具

提供查询用户信息的功能
"""

from langchain.tools import tool
from typing import Optional
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Users


@tool
def get_all_users(
    limit: Optional[str] = "100",
    status_filter: Optional[str] = "",
    runtime = None
) -> str:
    """获取所有用户信息

    Args:
        limit: 返回的最大用户数量（默认100）
        status_filter: 状态过滤（active/inactive/locked，不填则返回所有）

    Returns:
        str: 用户信息列表
    """
    ctx = runtime.context if runtime else None

    try:
        # 解析参数
        limit_int = int(limit) if limit else 100
        status = status_filter.strip() if status_filter else ""

        # 获取数据库会话
        db = get_session()

        try:
            # 构建查询
            query = db.query(Users)

            # 状态过滤
            if status:
                query = query.filter(Users.status == status)

            # 限制数量
            query = query.limit(limit_int)

            # 查询用户
            users = query.all()

            # 检查是否有用户
            if not users:
                return f"""
【查询用户信息】ℹ️

没有找到用户信息。

查询条件：
- 状态过滤：{status if status else "无"}
- 数量限制：{limit_int}
"""

            # 格式化用户信息
            user_list = []
            for i, user in enumerate(users, 1):
                user_info = f"""
用户 {i}：
- ID：{user.id}
- 姓名：{user.name}
- 邮箱：{user.email}
- 电话：{user.phone or '未设置'}
- 微信：{user.wechat or '未设置'}
- 部门：{user.department or '未设置'}
- 职位：{user.position or '未设置'}
- 角色：{', '.join([role.name for role in user.roles]) if user.roles else '普通用户'}
- 状态：{user.status}
- 超级管理员：{'是' if user.is_superuser else '否'}
- CEO：{'是' if user.is_ceo else '否'}
- 双因素认证：{'已启用' if user.two_factor_enabled else '未启用'}
- 最后登录：{user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '从未登录'}
- 创建时间：{user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
"""
                user_list.append(user_info)

            # 统计信息
            total_count = len(users)
            active_count = sum(1 for u in users if u.status == 'active')
            inactive_count = sum(1 for u in users if u.status == 'inactive')
            locked_count = sum(1 for u in users if u.status == 'locked')

            result = f"""
【查询用户信息】✅

查询结果：
- 总用户数：{total_count}人
- 活跃用户：{active_count}人
- 非活跃用户：{inactive_count}人
- 锁定用户：{locked_count}人

查询条件：
- 状态过滤：{status if status else "无"}
- 数量限制：{limit_int}

{'='*70}
{''.join(user_list)}
{'='*70}
"""

            return result

        finally:
            db.close()

    except Exception as e:
        return f"""
【查询用户信息】❌

查询失败：{str(e)}

请检查：
1. 数据库连接是否正常
2. 参数格式是否正确
"""


@tool
def get_user_by_id(
    user_id: str,
    runtime = None
) -> str:
    """根据用户ID获取用户信息

    Args:
        user_id: 用户ID

    Returns:
        str: 用户信息
    """
    ctx = runtime.context if runtime else None

    try:
        # 解析用户ID
        user_id_int = int(user_id)

        # 获取数据库会话
        db = get_session()

        try:
            # 查询用户
            user = db.query(Users).filter(Users.id == user_id_int).first()

            # 检查用户是否存在
            if not user:
                return f"""
【查询用户信息】❌

未找到ID为 {user_id_int} 的用户
"""

            # 格式化用户信息
            result = f"""
【用户详细信息】✅

基本信息：
- ID：{user.id}
- 姓名：{user.name}
- 邮箱：{user.email}
- 电话：{user.phone or '未设置'}
- 微信：{user.wechat or '未设置'}
- 部门：{user.department or '未设置'}
- 职位：{user.position or '未设置'}

角色信息：
- 角色：{', '.join([role.name for role in user.roles]) if user.roles else '普通用户'}
- 状态：{user.status}
- 超级管理员：{'是' if user.is_superuser else '否'}
- CEO：{'是' if user.is_ceo else '否'}

安全设置：
- 双因素认证：{'已启用' if user.two_factor_enabled else '未启用'}
- IP白名单：{'已设置' if user.ip_whitelist else '未设置'}

时间信息：
- 最后登录：{user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '从未登录'}
- 创建时间：{user.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- 更新时间：{user.updated_at.strftime('%Y-%m-%d %H:%M:%S') if user.updated_at else '未更新'}
- 创建人ID：{user.created_by if user.created_by else '无'}
"""

            return result

        finally:
            db.close()

    except ValueError:
        return """
【查询用户信息】❌

用户ID格式错误，请输入有效的数字ID。
"""
    except Exception as e:
        return f"""
【查询用户信息】❌

查询失败：{str(e)}

请检查：
1. 用户ID是否正确
2. 数据库连接是否正常
"""


@tool
def search_users(
    keyword: str,
    limit: Optional[str] = "50",
    runtime = None
) -> str:
    """搜索用户

    根据关键词搜索用户（姓名、邮箱、电话、微信）

    Args:
        keyword: 搜索关键词
        limit: 返回的最大用户数量（默认50）

    Returns:
        str: 搜索结果
    """
    ctx = runtime.context if runtime else None

    try:
        # 解析参数
        limit_int = int(limit) if limit else 50
        search_keyword = keyword.strip() if keyword else ""

        if not search_keyword:
            return """
【搜索用户】⚠️

请提供搜索关键词。
"""

        # 获取数据库会话
        db = get_session()

        try:
            # 构建搜索查询（搜索姓名、邮箱、电话、微信）
            users = db.query(Users).filter(
                (Users.name.like(f"%{search_keyword}%")) |
                (Users.email.like(f"%{search_keyword}%")) |
                (Users.phone.like(f"%{search_keyword}%")) |
                (Users.wechat.like(f"%{search_keyword}%"))
            ).limit(limit_int).all()

            # 检查是否有结果
            if not users:
                return f"""
【搜索用户】ℹ️

没有找到匹配的用户。

搜索关键词：{search_keyword}
"""

            # 格式化搜索结果
            result = f"""
【搜索用户】✅

搜索关键词：{search_keyword}
找到 {len(users)} 个匹配用户：

{'='*70}
"""

            for i, user in enumerate(users, 1):
                result += f"""
用户 {i}：
- ID：{user.id}
- 姓名：{user.name}
- 邮箱：{user.email}
- 电话：{user.phone or '未设置'}
- 微信：{user.wechat or '未设置'}
- 角色：{', '.join([role.name for role in user.roles]) if user.roles else '普通用户'}
- 状态：{user.status}
"""
                if i < len(users):
                    result += "-" * 50

            result += f"""
{'='*70}
"""

            return result

        finally:
            db.close()

    except Exception as e:
        return f"""
【搜索用户】❌

搜索失败：{str(e)}

请检查：
1. 关键词格式是否正确
2. 数据库连接是否正常
"""


# 导出所有工具
__all__ = [
    'get_all_users',
    'get_user_by_id',
    'search_users',
]
