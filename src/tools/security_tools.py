"""
财务安全验证工具

提供财务安全验证的LangChain工具接口
"""

from langchain.tools import tool, ToolRuntime
from typing import Dict, Any
from storage.database.security_check_service import security_check_service


@tool
def financial_security_check(
    operation: str,
    params: str,
    runtime: ToolRuntime
) -> str:
    """财务安全检查工具

    确保无论怎么变通，不能亏损1分钱

    Args:
        operation: 操作类型（如：create_transaction, exchange_lingzhi_to_contribution, lock_contribution等）
        params: 操作参数（JSON字符串格式）

    Returns:
        str: 检查结果
    """
    ctx = runtime.context

    try:
        # 解析参数
        import json
        if isinstance(params, str):
            params_dict = json.loads(params)
        else:
            params_dict = params

        # 执行财务安全检查
        passed, message = security_check_service.check_financial_security(operation, params_dict)

        if passed:
            return f"""
【财务安全检查】✅

检查结果：通过

详细信息：
- 操作类型：{operation}
- 检查状态：通过
- 检查时间：{message}

💡 提示：
该操作符合财务安全规范，可以继续执行。
"""
        else:
            return f"""
【财务安全检查】❌

检查结果：未通过

详细信息：
- 操作类型：{operation}
- 检查状态：未通过
- 拒绝原因：{message}

⚠️ 警告：
该操作不符合财务安全规范，已被拒绝执行。
为确保系统财务安全，请检查操作参数后重试。
"""

    except Exception as e:
        return f"""
【财务安全检查】⚠️

检查过程发生错误：{str(e)}

请检查输入参数格式是否正确。
"""


@tool
def comprehensive_security_check(
    user_id: str,
    operation: str,
    params: str,
    runtime: ToolRuntime
) -> str:
    """综合安全检查工具

    执行全面的系统安全检查，包括：
1. 异常操作检测
2. 权限检查
3. 操作合法性检查
4. 财务安全检查

Args:
        user_id: 用户ID
        operation: 操作类型
        params: 操作参数（JSON字符串格式）

    Returns:
        str: 检查结果
    """
    ctx = runtime.context

    try:
        # 解析用户ID
        if isinstance(user_id, str):
            user_id_int = int(user_id)
        else:
            user_id_int = user_id

        # 解析参数
        import json
        if isinstance(params, str):
            params_dict = json.loads(params)
        else:
            params_dict = params

        # 执行综合安全检查
        passed, message = security_check_service.comprehensive_security_check(user_id_int, operation, params_dict)

        if passed:
            return f"""
【综合安全检查】✅

检查结果：全面通过

检查项目：
✓ 异常操作检测
✓ 权限检查
✓ 操作合法性检查
✓ 财务安全检查

详细信息：
- 用户ID：{user_id}
- 操作类型：{operation}
- 检查状态：通过
- 检查时间：{message}

💡 提示：
该操作已通过所有安全检查，可以继续执行。
"""
        else:
            return f"""
【综合安全检查】❌

检查结果：未通过

拒绝原因：{message}

⚠️ 警告：
该操作未通过安全检查，已被拒绝执行。
为确保系统安全和财务安全，请检查：
1. 用户权限是否足够
2. 操作参数是否合法
3. 财务操作是否符合规则
"""

    except Exception as e:
        return f"""
【综合安全检查】⚠️

检查过程发生错误：{str(e)}

请检查输入参数格式是否正确。
"""


@tool
def detect_abnormal_operation(
    user_id: str,
    runtime: ToolRuntime
) -> str:
    """异常操作检测工具

    检测用户的异常操作行为

    Args:
        user_id: 用户ID

    Returns:
        str: 检测结果
    """
    ctx = runtime.context

    try:
        # 解析用户ID
        if isinstance(user_id, str):
            user_id_int = int(user_id)
        else:
            user_id_int = user_id

        # 执行异常操作检测
        is_abnormal, abnormal_reasons = security_check_service.detect_abnormal_operation(user_id_int)

        if is_abnormal:
            return f"""
【异常操作检测】⚠️

检测到异常操作！

异常原因：
"""

            for reason in abnormal_reasons:
                return f"""
- {reason}

⚠️ 警告：
检测到用户存在异常操作行为，系统已记录此操作。
请及时检查并确认是否为合法操作。
"""

        else:
            return f"""
【异常操作检测】✅

检测结果：正常

详细信息：
- 用户ID：{user_id}
- 检测状态：正常
- 无异常操作

💡 提示：
用户操作行为正常，未发现异常。
"""

    except Exception as e:
        return f"""
【异常操作检测】⚠️

检测过程发生错误：{str(e)}

请检查输入参数格式是否正确。
"""


@tool
def check_permission(
    user_id: str,
    required_role: str,
    action: str,
    runtime: ToolRuntime
) -> str:
    """权限检查工具

    检查用户是否有权限执行某项操作

    Args:
        user_id: 用户ID
        required_role: 需要的角色级别（如：超级管理员、CEO、高级管理员等）
        action: 操作类型（如：create_user, delete_user, assign_role等）

    Returns:
        str: 检查结果
    """
    ctx = runtime.context

    try:
        # 解析用户ID
        if isinstance(user_id, str):
            user_id_int = int(user_id)
        else:
            user_id_int = user_id

        # 执行权限检查
        passed, message = security_check_service.check_permission(user_id_int, required_role, action)

        if passed:
            return f"""
【权限检查】✅

检查结果：通过

详细信息：
- 用户ID：{user_id}
- 需要的角色：{required_role}
- 操作类型：{action}
- 检查状态：通过
- 检查时间：{message}

💡 提示：
用户拥有足够的权限执行此操作。
"""
        else:
            return f"""
【权限检查】❌

检查结果：未通过

详细信息：
- 用户ID：{user_id}
- 需要的角色：{required_role}
- 操作类型：{action}
- 检查状态：未通过
- 拒绝原因：{message}

⚠️ 警告：
用户权限不足，无法执行此操作。
请提升用户权限或联系超级管理员。
"""

    except Exception as e:
        return f"""
【权限检查】⚠️

检查过程发生错误：{str(e)}

请检查输入参数格式是否正确。
"""


# 导出所有工具
__all__ = [
    'financial_security_check',
    'comprehensive_security_check',
    'detect_abnormal_operation',
    'check_permission',
]
