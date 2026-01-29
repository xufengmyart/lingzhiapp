"""
数据库连接和状态检查工具

提供数据库连接测试、表信息查询、数据统计等功能
"""

from langchain.tools import tool
from typing import Optional
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Base, Users, Roles, Permissions, AuditLogs, CheckIns, Sessions
from sqlalchemy import inspect, text
import datetime


@tool
def test_database_connection(runtime=None) -> str:
    """测试数据库连接

    检查数据库是否可以正常连接

    Returns:
        str: 连接测试结果
    """
    ctx = runtime.context if runtime else None

    try:
        # 尝试获取数据库会话
        db = get_session()

        try:
            # 执行简单查询测试连接
            result = db.execute(text("SELECT 1"))
            row = result.fetchone()

            if row and row[0] == 1:
                return """
【数据库连接测试】✅

数据库连接成功！

连接信息：
- 状态：正常
- 响应时间：良好
- 基础查询：成功

💡 数据库可以正常使用。
"""
            else:
                return """
【数据库连接测试】⚠️

数据库连接成功，但查询异常。

请检查数据库配置和数据完整性。
"""

        finally:
            db.close()

    except Exception as e:
        return f"""
【数据库连接测试】❌

数据库连接失败！

错误信息：{str(e)}

可能的原因：
1. 数据库服务未启动
2. 数据库连接配置错误
3. 网络连接问题
4. 数据库权限不足

请检查：
- 环境变量配置（COZE_WORKSPACE_PATH）
- 数据库服务状态
- 连接参数是否正确
"""


@tool
def get_database_status(runtime=None) -> str:
    """获取数据库状态信息

    查询数据库中的表、记录数、索引等信息

    Returns:
        str: 数据库状态信息
    """
    ctx = runtime.context if runtime else None

    try:
        db = get_session()

        try:
            # 获取数据库检查器
            inspector = inspect(db.bind)

            # 获取所有表名
            table_names = inspector.get_table_names()

            # 统计各表的记录数
            table_stats = []
            total_records = 0

            for table_name in sorted(table_names):
                try:
                    result = db.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    total_records += count

                    table_stats.append({
                        'name': table_name,
                        'count': count
                    })
                except:
                    table_stats.append({
                        'name': table_name,
                        'count': '查询失败'
                    })

            # 格式化结果
            result_text = """
【数据库状态信息】✅

数据库概览：
- 总表数：{total_tables}个
- 总记录数：{total_records}条
- 检查时间：{check_time}

表详细信息：
""".format(
                total_tables=len(table_names),
                total_records=total_records,
                check_time=datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )

            for i, stat in enumerate(table_stats, 1):
                if isinstance(stat['count'], int):
                    result_text += f"{i}. {stat['name']}: {stat['count']}条记录\n"
                else:
                    result_text += f"{i}. {stat['name']}: {stat['count']}\n"

            result_text += """
💡 数据库运行正常，所有表都可以访问。
"""

            return result_text

        finally:
            db.close()

    except Exception as e:
        return f"""
【数据库状态查询】❌

查询数据库状态失败！

错误信息：{str(e)}

请检查数据库连接是否正常。
"""


@tool
def get_user_statistics(runtime=None) -> str:
    """获取用户统计信息

    查询用户数量、状态分布、角色分布等统计信息

    Returns:
        str: 用户统计信息
    """
    ctx = runtime.context if runtime else None

    try:
        db = get_session()

        try:
            # 总用户数
            total_users = db.query(Users).count()

            # 活跃用户数
            active_users = db.query(Users).filter(Users.status == 'active').count()

            # 非活跃用户数
            inactive_users = db.query(Users).filter(Users.status == 'inactive').count()

            # 锁定用户数
            locked_users = db.query(Users).filter(Users.status == 'locked').count()

            # 超级管理员数量
            super_admin_users = db.query(Users).filter(Users.is_superuser == True).count()

            # CEO数量
            ceo_users = db.query(Users).filter(Users.is_ceo == True).count()

            # 今日登录用户数
            today = datetime.datetime.now().date()
            today_login_users = db.query(Users).filter(
                Users.last_login >= today
            ).count()

            # 最近7天活跃用户数
            seven_days_ago = datetime.datetime.now() - datetime.timedelta(days=7)
            active_7days_users = db.query(Users).filter(
                Users.last_login >= seven_days_ago
            ).count()

            result = f"""
【用户统计信息】✅

用户数量统计：
- 总用户数：{total_users}人
- 活跃用户：{active_users}人
- 非活跃用户：{inactive_users}人
- 锁定用户：{locked_users}人

特殊用户统计：
- 超级管理员：{super_admin_users}人
- CEO：{ceo_users}人

活跃度统计：
- 今日登录：{today_login_users}人
- 最近7天活跃：{active_7days_users}人
- 活跃率：{active_users/total_users*100:.1f}%（活跃用户/总用户）

状态分布：
- 活跃：{active_users/total_users*100:.1f}%
- 非活跃：{inactive_users/total_users*100:.1f}%
- 锁定：{locked_users/total_users*100:.1f}%

统计时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            return result

        finally:
            db.close()

    except Exception as e:
        return f"""
【用户统计查询】❌

查询用户统计失败！

错误信息：{str(e)}

请检查数据库连接是否正常。
"""


@tool
def get_table_structure(table_name: str, runtime=None) -> str:
    """获取表结构信息

    Args:
        table_name: 表名

    Returns:
        str: 表结构信息
    """
    ctx = runtime.context if runtime else None

    try:
        db = get_session()

        try:
            # 获取数据库检查器
            inspector = inspect(db.bind)

            # 检查表是否存在
            if table_name not in inspector.get_table_names():
                return f"""
【表结构查询】❌

表 {table_name} 不存在！

可用的表：
{', '.join(inspector.get_table_names())}
"""

            # 获取表结构
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)

            # 格式化结果
            result = f"""
【表结构信息】✅

表名：{table_name}

列信息：
"""

            for i, column in enumerate(columns, 1):
                nullable = "NULL" if column['nullable'] else "NOT NULL"
                default = f" DEFAULT {column['default']}" if column['default'] else ""
                result += f"{i}. {column['name']} ({column['type']}) {nullable}{default}\n"

            if indexes:
                result += f"\n索引信息：\n"
                for i, index in enumerate(indexes, 1):
                    result += f"{i}. {index['name']}: {', '.join(index['column_names'])}\n"

            if foreign_keys:
                result += f"\n外键信息：\n"
                for i, fk in enumerate(foreign_keys, 1):
                    result += f"{i}. {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}\n"

            return result

        finally:
            db.close()

    except Exception as e:
        return f"""
【表结构查询】❌

查询表结构失败！

错误信息：{str(e)}

请检查表名是否正确。
"""


@tool
def execute_sql_query(sql_query: str, runtime=None) -> str:
    """执行SQL查询

    Args:
        sql_query: SQL查询语句（仅支持SELECT）

    Returns:
        str: 查询结果
    """
    ctx = runtime.context if runtime else None

    try:
        # 安全检查：只允许SELECT查询
        sql_upper = sql_query.strip().upper()
        if not sql_upper.startswith('SELECT'):
            return """
【SQL查询】❌

为了安全起见，仅允许执行SELECT查询。

不允许的操作：
- INSERT、UPDATE、DELETE
- CREATE、ALTER、DROP
- 其他修改数据的操作

请使用SELECT查询只读数据。
"""

        # 执行查询
        db = get_session()

        try:
            result = db.execute(text(sql_query))
            rows = result.fetchall()
            columns = result.keys()

            # 检查是否有结果
            if not rows:
                return """
【SQL查询】✅

查询成功，但没有返回数据。
"""

            # 格式化结果
            output = """
【SQL查询结果】✅

执行的SQL：
{}
""".format(sql_query)

            # 表头
            output += "\n" + " | ".join(columns) + "\n"
            output += "-" * (len(" | ".join(columns))) + "\n"

            # 数据行
            for row in rows:
                output += " | ".join([str(cell) if cell is not None else "NULL" for cell in row]) + "\n"

            output += f"\n共返回 {len(rows)} 条记录\n"
            output += f"查询时间：{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"

            return output

        finally:
            db.close()

    except Exception as e:
        return f"""
【SQL查询】❌

查询失败！

错误信息：{str(e)}

请检查：
1. SQL语法是否正确
2. 表名和字段名是否存在
3. 数据库连接是否正常
"""


# 导出所有工具
__all__ = [
    'test_database_connection',
    'get_database_status',
    'get_user_statistics',
    'get_table_structure',
    'execute_sql_query',
]
