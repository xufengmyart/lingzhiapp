"""
超级管理员配置

定义超级管理员的唯一性原则、安全要求和操作规则
"""

from typing import Dict, List, Optional
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Users


# 超级管理员唯一性原则
SUPER_ADMIN_PRINCIPLES: Dict[str, str] = {
    "唯一性原则": "系统中只能有1个超级管理员，任何时候都不能有多个超级管理员存在",
    "不可删除原则": "超级管理员不能被删除，这是为了防止系统失去最高权限管理者",
    "不可禁用原则": "超级管理员不能被禁用或锁定，确保系统始终有最高权限管理者",
    "不可降级原则": "超级管理员不能被降级为普通用户或其它角色",
    "转让机制": "超级管理员权限只能通过合法的转让流程转移给另一个用户",
    "安全要求": "超级管理员必须启用双因素认证和IP白名单",
    "审计追踪": "超级管理员的所有操作都会被记录在增强的审计日志中",
    "责任归属": "超级管理员对系统安全负全部责任",
}


# 超级管理员安全要求
SUPER_ADMIN_SECURITY_REQUIREMENTS: Dict[str, str] = {
    "双因素认证": "超级管理员必须启用双因素认证（2FA），使用TOTP或硬件密钥",
    "IP白名单": "超级管理员必须设置IP白名单，只允许特定IP地址登录",
    "定期密码更新": "超级管理员密码必须至少每90天更新一次",
    "复杂密码要求": "密码长度至少12位，包含大小写字母、数字和特殊字符",
    "会话管理": "超级管理员会话最长24小时，超时需要重新登录",
    "操作验证": "关键操作需要二次验证（如密码验证或2FA验证）",
    "异地登录提醒": "超级管理员从新设备或新IP登录时，立即发送告警",
}


# 超级管理员特权说明
SUPER_ADMIN_PRIVILEGES: List[str] = [
    "用户管理：可以创建、修改、删除用户账户",
    "角色管理：可以创建、修改、删除角色和权限",
    "系统配置：可以修改系统配置和参数",
    "数据访问：可以访问所有系统数据",
    "审计日志：可以查看和管理所有审计日志",
    "安全管理：可以配置和管理安全策略",
    "超级管理员转让：可以将超级管理员权限转让给其他用户",
]


def validate_super_admin_uniqueness(current_count: int) -> tuple[bool, str]:
    """验证超级管理员数量是否符合唯一性原则

    Args:
        current_count: 当前超级管理员数量

    Returns:
        tuple: (是否有效, 消息)
    """
    if current_count == 0:
        return False, "系统中没有超级管理员，这是不允许的"
    elif current_count == 1:
        return True, "超级管理员数量符合唯一性原则"
    elif current_count > 1:
        return False, f"系统中存在{current_count}个超级管理员，违反唯一性原则"
    else:
        return False, "超级管理员数量无效"


def get_super_admin_principles() -> Dict[str, str]:
    """获取超级管理员原则

    Returns:
        dict: 超级管理员原则
    """
    return SUPER_ADMIN_PRINCIPLES


def get_super_admin_security_requirements() -> Dict[str, str]:
    """获取超级管理员安全要求

    Returns:
        dict: 超级管理员安全要求
    """
    return SUPER_ADMIN_SECURITY_REQUIREMENTS


def get_super_admin_privileges() -> List[str]:
    """获取超级管理员特权

    Returns:
        list: 超级管理员特权列表
    """
    return SUPER_ADMIN_PRIVILEGES


def get_current_super_admin() -> Optional[Users]:
    """获取当前超级管理员

    Returns:
        Users: 当前超级管理员对象，如果没有则返回None
    """
    db = get_session()
    try:
        super_admin = db.query(Users).filter(Users.is_superuser == True).first()
        return super_admin
    finally:
        db.close()


def validate_super_admin_uniqueness_in_db() -> tuple[bool, str, Optional[int]]:
    """验证数据库中超级管理员的唯一性

    Returns:
        tuple: (是否有效, 消息, 当前数量)
    """
    db = get_session()
    try:
        count = db.query(Users).filter(Users.is_superuser == True).count()
        valid, message = validate_super_admin_uniqueness(count)
        return valid, message, count
    finally:
        db.close()


def format_super_admin_summary() -> str:
    """格式化超级管理员摘要

    Returns:
        str: 超级管理员摘要信息
    """
    super_admin = get_current_super_admin()

    if not super_admin:
        return """
⚠️  当前系统中没有超级管理员

这是一个异常状态，请立即处理。
"""

    return f"""
📋 当前超级管理员信息：
- 姓名：{super_admin.name}
- 邮箱：{super_admin.email}
- 扣子UID：{super_admin.coze_id if super_admin.coze_id else '未设置'}
- 状态：{super_admin.status}
- 双因素认证：{'已启用' if super_admin.two_factor_enabled else '未启用'}
- 创建时间：{super_admin.created_at.strftime('%Y-%m-%d %H:%M:%S')}
- 最后登录：{super_admin.last_login.strftime('%Y-%m-%d %H:%M:%S') if super_admin.last_login else '从未登录'}
"""


def check_super_admin_security_compliance(super_admin: Users) -> tuple[bool, List[str]]:
    """检查超级管理员安全合规性

    Args:
        super_admin: 超级管理员对象

    Returns:
        tuple: (是否合规, 不合规项列表)
    """
    issues = []

    # 检查双因素认证
    if not super_admin.two_factor_enabled:
        issues.append("未启用双因素认证")

    # 检查IP白名单
    if not super_admin.ip_whitelist:
        issues.append("未设置IP白名单")

    # 检查状态
    if super_admin.status != 'active':
        issues.append(f"状态异常：{super_admin.status}")

    return len(issues) == 0, issues
