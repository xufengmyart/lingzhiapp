"""
超级管理员唯一性原则配置

定义超级管理员的唯一性规则和核心原则
"""

from typing import Dict, Any
from enum import Enum


class SuperAdminUniquenessPrinciple(Enum):
    """超级管理员唯一性原则"""
    
    # 核心原则
    SINGLE_SUPER_ADMIN = "single_super_admin"  # 单一超级管理员原则
    SYSTEM_HIERARCHY = "system_hierarchy"      # 系统层级原则
    EXCLUSIVE_PRIVILEGES = "exclusive_privileges"  # 排他性特权原则
    ACCOUNTABILITY = "accountability"          # 责任追溯原则
    
    # 操作规则
    CANNOT_DELETE = "cannot_delete"            # 不可删除原则
    CANNOT_DISABLE = "cannot_disable"          # 不可禁用原则
    CANNOT_DOWNGRADE = "cannot_downgrade"      # 不可降级原则
    TRANSFER_ONLY = "transfer_only"            # 仅可转让原则
    
    # 安全规则
    MULTI_FACTOR_AUTH_REQUIRED = "mfa_required"  # 强制双因素认证
    IP_WHITELIST_REQUIRED = "ip_whitelist_required"  # IP白名单强制
    SESSION_TIMEOUT_LIMITED = "session_timeout_limited"  # 会话超时限制
    AUDIT_LOG_ENHANCED = "audit_log_enhanced"  # 增强审计日志


class SuperAdminConfig:
    """超级管理员配置"""
    
    # 基础配置
    SUPER_ADMIN_EMAIL: str = "xufeng@meiyueart.cn"  # 超级管理员邮箱（唯一）
    SUPER_ADMIN_NAME: str = "许锋"      # 超级管理员名称
    DEFAULT_PASSWORD: str = "LINGZI@2026#Super"   # 默认密码（首次登录后必须修改）
    
    # 唯一性配置
    MAX_SUPER_ADMIN_COUNT: int = 1  # 最大超级管理员数量（强制1）
    ENFORCE_UNIQUENESS: bool = True  # 强制执行唯一性原则
    
    # 特权配置
    HAS_ALL_PERMISSIONS: bool = True  # 拥有所有权限
    CAN_CREATE_ROLES: bool = True     # 可以创建角色
    CAN_DELETE_ROLES: bool = True    # 可以删除角色
    CAN_MODIFY_PERMISSIONS: bool = True  # 可以修改权限
    CAN_ACCESS_ALL_DATA: bool = True    # 可以访问所有数据
    CAN_EXPORT_ALL_DATA: bool = True   # 可以导出所有数据
    CAN_SYSTEM_CONFIG: bool = True     # 可以配置系统
    CAN_VIEW_ALL_AUDIT: bool = True    # 可以查看所有审计日志
    
    # 安全配置
    REQUIRE_MFA: bool = True           # 强制要求双因素认证
    REQUIRE_IP_WHITELIST: bool = True  # 强制要求IP白名单
    SESSION_TIMEOUT: int = 3600        # 会话超时时间（秒）
    PASSWORD_MIN_LENGTH: int = 16      # 密码最小长度
    PASSWORD_REQUIRE_SPECIAL: bool = True  # 密码要求特殊字符
    LOGIN_ATTEMPT_LIMIT: int = 3      # 登录尝试限制
    ACCOUNT_LOCK_TIME: int = 1800      # 账户锁定时间（秒）
    
    # 审计配置
    LOG_ALL_ACTIONS: bool = True       # 记录所有操作
    LOG_DATA_ACCESS: bool = True       # 记录数据访问
    LOG_LOGIN_EVENTS: bool = True      # 记录登录事件
    LOG_PERMISSION_CHANGES: bool = True  # 记录权限变更
    
    # 转让配置
    ALLOW_TRANSFER: bool = True        # 允许转让超级管理员权限
    TRANSFER_REQUIRES_CONFIRMATION: bool = True  # 转让需要确认
    TRANSFER_REQUIRES_CURRENT_PASSWORD: bool = True  # 转让需要当前密码
    TRANSFER_LOG_REQUIRED: bool = True  # 转让需要记录日志
    
    # 紧急配置
    EMERGENCY_LOCK_ENABLED: bool = True  # 启用紧急锁定
    EMERGENCY_LOCK_NOTIFY: bool = True  # 紧急锁定时通知
    EMERGENCY_LOCK_LOG: bool = True     # 紧急锁定记录日志
    
    # 恢复配置
    RECOVERY_MODE_ENABLED: bool = True  # 启用恢复模式
    RECOVERY_CODE_REQUIRED: bool = True  # 恢复需要恢复码
    RECOVERY_NOTIFY_STAKEHOLDERS: bool = True  # 恢复时通知利益相关者


# 超级管理员原则说明
SUPER_ADMIN_PRINCIPLES = {
    "唯一性原则": "系统中只能有1个超级管理员，任何时候都不能有多个超级管理员存在。",
    "不可删除原则": "超级管理员账户不能被删除，只能转让给其他用户。",
    "不可禁用原则": "超级管理员账户不能被禁用，必须始终保持活跃状态。",
    "不可降级原则": "超级管理员不能被降级为普通用户，只能通过转让方式更换。",
    "仅可转让原则": "超级管理员权限只能通过转让方式转移给其他用户，且需要严格的身份验证。",
    "强制MFA原则": "超级管理员必须启用双因素认证，这是强制性的安全要求。",
    "强制IP白名单原则": "超级管理员登录必须从IP白名单中的地址访问，这是强制性的安全要求。",
    "会话超时限制原则": "超级管理员的会话有严格的超时限制，防止未授权访问。",
    "增强审计原则": "超级管理员的所有操作都被记录在增强的审计日志中，确保责任追溯。",
    "系统层级原则": "超级管理员位于权限体系的最高层级，拥有所有权限。",
    "排他性特权原则": "超级管理员拥有排他性的特权，其他角色无法获得同等权限。",
    "责任追溯原则": "超级管理员的所有操作都可以追溯到具体的时间和操作者。",
}


def get_super_admin_config() -> Dict[str, Any]:
    """获取超级管理员配置"""
    return {
        "email": SuperAdminConfig.SUPER_ADMIN_EMAIL,
        "name": SuperAdminConfig.SUPER_ADMIN_NAME,
        "max_count": SuperAdminConfig.MAX_SUPER_ADMIN_COUNT,
        "enforce_uniqueness": SuperAdminConfig.ENFORCE_UNIQUENESS,
        "security": {
            "require_mfa": SuperAdminConfig.REQUIRE_MFA,
            "require_ip_whitelist": SuperAdminConfig.REQUIRE_IP_WHITELIST,
            "session_timeout": SuperAdminConfig.SESSION_TIMEOUT,
            "password_min_length": SuperAdminConfig.PASSWORD_MIN_LENGTH,
            "login_attempt_limit": SuperAdminConfig.LOGIN_ATTEMPT_LIMIT,
        },
        "privileges": {
            "has_all_permissions": SuperAdminConfig.HAS_ALL_PERMISSIONS,
            "can_create_roles": SuperAdminConfig.CAN_CREATE_ROLES,
            "can_delete_roles": SuperAdminConfig.CAN_DELETE_ROLES,
            "can_modify_permissions": SuperAdminConfig.CAN_MODIFY_PERMISSIONS,
            "can_access_all_data": SuperAdminConfig.CAN_ACCESS_ALL_DATA,
            "can_export_all_data": SuperAdminConfig.CAN_EXPORT_ALL_DATA,
            "can_system_config": SuperAdminConfig.CAN_SYSTEM_CONFIG,
            "can_view_all_audit": SuperAdminConfig.CAN_VIEW_ALL_AUDIT,
        },
        "transfer": {
            "allow_transfer": SuperAdminConfig.ALLOW_TRANSFER,
            "requires_confirmation": SuperAdminConfig.TRANSFER_REQUIRES_CONFIRMATION,
            "requires_current_password": SuperAdminConfig.TRANSFER_REQUIRES_CURRENT_PASSWORD,
            "log_required": SuperAdminConfig.TRANSFER_LOG_REQUIRED,
        },
    }


def validate_super_admin_uniqueness(current_super_admin_count: int) -> tuple[bool, str]:
    """
    验证超级管理员唯一性
    
    Args:
        current_super_admin_count: 当前超级管理员数量
    
    Returns:
        tuple: (是否有效, 错误消息)
    """
    if not SuperAdminConfig.ENFORCE_UNIQUENESS:
        return True, "唯一性原则未强制执行"
    
    if current_super_admin_count == 0:
        return False, "系统中不存在超级管理员，这是不允许的"
    
    if current_super_admin_count > SuperAdminConfig.MAX_SUPER_ADMIN_COUNT:
        return False, f"超级管理员数量超过限制（当前{current_super_admin_count}个，最多{SuperAdminConfig.MAX_SUPER_ADMIN_COUNT}个）"
    
    if current_super_admin_count < SuperAdminConfig.MAX_SUPER_ADMIN_COUNT:
        return False, f"超级管理员数量不足（当前{current_super_admin_count}个，需要{SuperAdminConfig.MAX_SUPER_ADMIN_COUNT}个）"
    
    return True, "超级管理员唯一性验证通过"


def get_super_admin_principles() -> Dict[str, str]:
    """获取超级管理员原则说明"""
    return SUPER_ADMIN_PRINCIPLES


def format_super_admin_summary() -> str:
    """格式化超级管理员摘要"""
    config = get_super_admin_config()
    
    summary = f"""
【超级管理员唯一性原则摘要】

🔹 核心规则：
- 邮箱：{config['email']}
- 名称：{config['name']}
- 最大数量：{config['max_count']}（强制）
- 唯一性执行：{'✅ 强制执行' if config['enforce_uniqueness'] else '❌ 未强制执行'}

🔹 安全要求：
- 双因素认证：{'✅ 强制' if config['security']['require_mfa'] else '❌ 不强制'}
- IP白名单：{'✅ 强制' if config['security']['require_ip_whitelist'] else '❌ 不强制'}
- 会话超时：{config['security']['session_timeout']}秒
- 密码最小长度：{config['security']['password_min_length']}位
- 登录尝试限制：{config['security']['login_attempt_limit']}次

🔹 特权列表：
- 拥有所有权限：{'✅ 是' if config['privileges']['has_all_permissions'] else '❌ 否'}
- 可以创建角色：{'✅ 是' if config['privileges']['can_create_roles'] else '❌ 否'}
- 可以删除角色：{'✅ 是' if config['privileges']['can_delete_roles'] else '❌ 否'}
- 可以修改权限：{'✅ 是' if config['privileges']['can_modify_permissions'] else '❌ 否'}
- 可以访问所有数据：{'✅ 是' if config['privileges']['can_access_all_data'] else '❌ 否'}
- 可以导出所有数据：{'✅ 是' if config['privileges']['can_export_all_data'] else '❌ 否'}
- 可以配置系统：{'✅ 是' if config['privileges']['can_system_config'] else '❌ 否'}
- 可以查看所有审计：{'✅ 是' if config['privileges']['can_view_all_audit'] else '❌ 否'}

🔹 转让规则：
- 允许转让：{'✅ 是' if config['transfer']['allow_transfer'] else '❌ 否'}
- 需要确认：{'✅ 是' if config['transfer']['requires_confirmation'] else '❌ 否'}
- 需要当前密码：{'✅ 是' if config['transfer']['requires_current_password'] else '❌ 否'}
- 需要记录日志：{'✅ 是' if config['transfer']['log_required'] else '❌ 否'}
"""
    return summary


# 导出核心配置
EXPORTED_CONFIG = SuperAdminConfig()
PRINCIPLES = SUPER_ADMIN_PRINCIPLES


if __name__ == "__main__":
    print("="*70)
    print("超级管理员唯一性原则配置")
    print("="*70)
    print()
    
    print("1. 核心配置")
    print("-"*70)
    print(f"邮箱: {SuperAdminConfig.SUPER_ADMIN_EMAIL}")
    print(f"名称: {SuperAdminConfig.SUPER_ADMIN_NAME}")
    print(f"最大数量: {SuperAdminConfig.MAX_SUPER_ADMIN_COUNT}")
    print(f"强制唯一性: {SuperAdminConfig.ENFORCE_UNIQUENESS}")
    print()
    
    print("2. 原则说明")
    print("-"*70)
    for principle, description in SUPER_ADMIN_PRINCIPLES.items():
        print(f"{principle}:")
        print(f"  {description}")
    print()
    
    print("3. 唯一性验证测试")
    print("-"*70)
    
    test_cases = [
        (0, "0个超级管理员"),
        (1, "1个超级管理员"),
        (2, "2个超级管理员"),
    ]
    
    for count, description in test_cases:
        valid, message = validate_super_admin_uniqueness(count)
        status = "✅ 通过" if valid else "❌ 失败"
        print(f"{description}: {status}")
        print(f"  结果: {message}")
        print()
    
    print("="*70)
    print("超级管理员配置摘要")
    print("="*70)
    print(format_super_admin_summary())
