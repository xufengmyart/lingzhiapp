"""
统一安全框架

提供统一的输入验证、错误处理、权限控制、审计日志等功能
"""

import re
import json
import logging
from datetime import datetime
from typing import Callable, Any, Dict, List, Optional
from functools import wraps
from collections import defaultdict
import hashlib

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/app/work/logs/bypass/security.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class SecurityError(Exception):
    """安全异常"""
    pass


class ValidationError(Exception):
    """验证异常"""
    pass


class PermissionError(Exception):
    """权限异常"""
    pass


# ========== 输入验证系统 ==========

class InputValidator:
    """输入验证器"""
    
    # 手机号验证
    PHONE_PATTERN = re.compile(r'^1[3-9]\d{9}$')
    
    # 身份证验证
    ID_CARD_PATTERN = re.compile(r'^\d{17}[\dXx]$')
    
    # 邮箱验证
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """验证手机号"""
        return bool(InputValidator.PHONE_PATTERN.match(phone))
    
    @staticmethod
    def validate_id_card(id_card: str) -> bool:
        """验证身份证号"""
        if not InputValidator.ID_CARD_PATTERN.match(id_card):
            return False
        
        # 验证校验位
        weights = [7, 9, 10, 5, 8, 4, 2, 1, 6, 3, 7, 9, 10, 5, 8, 4, 2]
        check_codes = ['1', '0', 'X', '9', '8', '7', '6', '5', '4', '3', '2']
        
        total = sum(int(id_card[i]) * weights[i] for i in range(17))
        return id_card[-1].upper() == check_codes[total % 11]
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """验证邮箱"""
        return bool(InputValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_positive_int(value: Any) -> bool:
        """验证正整数"""
        return isinstance(value, int) and value > 0
    
    @staticmethod
    def validate_amount(amount: Any, min_val: float = 0, max_val: float = 1000000) -> bool:
        """验证金额"""
        if not isinstance(amount, (int, float)):
            return False
        return min_val <= amount <= max_val
    
    @staticmethod
    def validate_password(password: str) -> bool:
        """验证密码强度"""
        if len(password) < 8:
            return False
        if not re.search(r'[a-z]', password):
            return False
        if not re.search(r'[A-Z]', password):
            return False
        if not re.search(r'\d', password):
            return False
        return True
    
    @staticmethod
    def validate_sql_keywords(sql: str, allowed_keywords: List[str]) -> bool:
        """验证SQL关键词"""
        sql_upper = sql.upper()
        # 只允许SELECT、INSERT、UPDATE、DELETE等关键词
        for keyword in ['DROP', 'TRUNCATE', 'ALTER', 'CREATE', 'GRANT', 'REVOKE']:
            if keyword in sql_upper:
                return False
        
        # 验证是否包含允许的关键词
        return any(keyword in sql_upper for keyword in allowed_keywords)


# ========== SQL安全系统 ==========

class SQLSecurity:
    """SQL安全防护"""
    
    # 允许的SQL关键词
    ALLOWED_KEYWORDS = ['SELECT', 'FROM', 'WHERE', 'LIMIT', 'ORDER BY', 'GROUP BY']
    
    # 危险的SQL模式
    DANGEROUS_PATTERNS = [
        r'\bDROP\b',
        r'\bTRUNCATE\b',
        r'\bALTER\b',
        r'\bCREATE\b',
        r'\bGRANT\b',
        r'\bREVOKE\b',
        r';\s*(DROP|TRUNCATE|DELETE)',  # 多语句注入
        r'--\s*DROP',  # 注释注入
        r'/\*.*DROP.*\*/',  # 注释块注入
    ]
    
    @staticmethod
    def validate_sql(sql: str) -> bool:
        """验证SQL安全性"""
        if not sql:
            return False
        
        sql_upper = sql.upper()
        
        # 检查危险模式
        for pattern in SQLSecurity.DANGEROUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                logger.warning(f"检测到危险SQL模式: {sql}")
                return False
        
        # 检查是否只包含允许的关键词
        if not any(keyword in sql_upper for keyword in SQLSecurity.ALLOWED_KEYWORDS):
            logger.warning(f"SQL包含不允许的关键词: {sql}")
            return False
        
        return True
    
    @staticmethod
    def escape_sql_value(value: Any) -> str:
        """转义SQL值"""
        if value is None:
            return 'NULL'
        if isinstance(value, str):
            return f"'{value.replace("'", "''")}'"
        if isinstance(value, (int, float)):
            return str(value)
        if isinstance(value, bool):
            return '1' if value else '0'
        return f"'{str(value)}'"


# ========== 权限控制系统 ==========

class PermissionManager:
    """权限管理器"""
    
    # 权限定义
    PERMISSIONS = {
        'user': [
            'view_own_profile',
            'edit_own_profile',
            'view_own_lingzhi',
            'view_own_journey',
            'submit_withdrawal',
        ],
        'admin': [
            'view_all_users',
            'edit_all_users',
            'view_all_lingzhi',
            'approve_withdrawal',
            'view_financial_reports',
            'manage_partners',
        ],
        'super_admin': [
            'transfer_super_admin',
            'force_change_password',
            'manage_all',
        ]
    }
    
    @staticmethod
    def has_permission(user_role: str, permission: str) -> bool:
        """检查用户是否有权限"""
        if user_role not in PermissionManager.PERMISSIONS:
            return False
        return permission in PermissionManager.PERMISSIONS[user_role]
    
    @staticmethod
    def check_permission(user_id: int, permission: str, runtime=None) -> bool:
        """检查权限（完整版本）"""
        # TODO: 从数据库获取用户角色
        user_role = 'user'  # 临时，实际应从数据库获取
        
        # 特殊权限检查
        if permission == 'force_change_password':
            # 只有超级管理员可以强制修改密码
            return user_role == 'super_admin'
        
        return PermissionManager.has_permission(user_role, permission)


# ========== 审计日志系统 ==========

class AuditLogger:
    """审计日志记录器"""
    
    def __init__(self):
        self.operation_log = defaultdict(list)
    
    def log_operation(
        self,
        action: str,
        user_id: Optional[int],
        target_id: Optional[int] = None,
        params: Optional[Dict] = None,
        result: Optional[str] = None,
        status: str = 'success',
        error: Optional[str] = None
    ):
        """记录操作日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'user_id': user_id,
            'target_id': target_id,
            'params': params,
            'result': result,
            'status': status,
            'error': error
        }
        
        # 记录到内存
        self.operation_log[action].append(log_entry)
        
        # 记录到文件
        logger.info(f"Audit: {json.dumps(log_entry, ensure_ascii=False)}")
        
        # 记录到数据库（如果需要）
        # TODO: 实现数据库日志记录
    
    def get_operation_history(
        self,
        action: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 100
    ) -> List[Dict]:
        """获取操作历史"""
        logs = []
        
        if action:
            logs = self.operation_log.get(action, [])
        else:
            for action_logs in self.operation_log.values():
                logs.extend(action_logs)
        
        # 过滤用户
        if user_id:
            logs = [log for log in logs if log.get('user_id') == user_id]
        
        # 限制数量
        return logs[-limit:]


# ========== 限流系统 ==========

class RateLimiter:
    """请求限流器"""
    
    def __init__(self):
        self.request_counts = defaultdict(list)
    
    def check_rate_limit(
        self,
        identifier: str,
        max_calls: int = 10,
        period: int = 60
    ) -> bool:
        """
        检查是否超过限流
        
        Args:
            identifier: 标识符（用户ID、IP等）
            max_calls: 最大调用次数
            period: 时间周期（秒）
        
        Returns:
            bool: True表示允许调用，False表示超过限流
        """
        now = datetime.now()
        timestamps = self.request_counts[identifier]
        
        # 清理过期记录
        self.request_counts[identifier] = [
            ts for ts in timestamps
            if (now - ts).total_seconds() <= period
        ]
        
        # 检查是否超过限制
        if len(self.request_counts[identifier]) >= max_calls:
            logger.warning(f"限流触发: {identifier}, 当前请求数: {len(self.request_counts[identifier])}")
            return False
        
        # 记录请求
        self.request_counts[identifier].append(now)
        return True
    
    def get_remaining_calls(
        self,
        identifier: str,
        max_calls: int = 10,
        period: int = 60
    ) -> int:
        """获取剩余调用次数"""
        return max_calls - len(self.request_counts[identifier])


# ========== 全局实例 ==========

input_validator = InputValidator()
sql_security = SQLSecurity()
permission_manager = PermissionManager()
audit_logger = AuditLogger()
rate_limiter = RateLimiter()


# ========== 装饰器 ==========

def validate_input(**validators):
    """
    输入验证装饰器
    
    Args:
        **validators: 参数名 -> 验证函数的映射
    
    Usage:
        @validate_input(
            user_id=lambda x: isinstance(x, int) and x > 0,
            amount=lambda x: isinstance(x, (int, float)) and x > 0
        )
        def add_lingzhi(user_id: int, amount: int):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 验证每个参数
            for param_name, validator in validators.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    try:
                        if not validator(value):
                            logger.error(f"参数验证失败: {param_name}={value}")
                            return f"❌ 参数 {param_name} 验证失败，请检查输入"
                    except Exception as e:
                        logger.error(f"验证异常: {param_name}={value}, error={str(e)}")
                        return f"❌ 参数验证异常"
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def handle_errors(func):
    """统一错误处理装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.error(f"验证错误: {str(e)}", exc_info=True)
            return f"❌ 输入验证失败: {str(e)}"
        except PermissionError as e:
            logger.error(f"权限错误: {str(e)}", exc_info=True)
            return f"❌ 权限不足，您无权执行此操作"
        except SecurityError as e:
            logger.error(f"安全错误: {str(e)}", exc_info=True)
            return f"❌ 安全错误: {str(e)}"
        except Exception as e:
            logger.error(f"未知错误: {str(e)}", exc_info=True)
            return f"❌ 系统错误，请稍后重试或联系管理员"
    return wrapper


def audit_log(action: str):
    """
    审计日志装饰器
    
    Args:
        action: 操作类型
    
    Usage:
        @audit_log('withdrawal_request')
        def submit_withdrawal_request(...):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            target_id = kwargs.get('target_id')
            
            # 记录操作开始
            audit_logger.log_operation(
                action=action,
                user_id=user_id,
                target_id=target_id,
                params=kwargs,
                status='started'
            )
            
            try:
                result = func(*args, **kwargs)
                
                # 记录操作成功
                audit_logger.log_operation(
                    action=action,
                    user_id=user_id,
                    target_id=target_id,
                    params=kwargs,
                    result=result,
                    status='success'
                )
                
                return result
            except Exception as e:
                # 记录操作失败
                audit_logger.log_operation(
                    action=action,
                    user_id=user_id,
                    target_id=target_id,
                    params=kwargs,
                    status='failure',
                    error=str(e)
                )
                raise
        return wrapper
    return decorator


def rate_limit(max_calls: int = 10, period: int = 60):
    """
    限流装饰器
    
    Args:
        max_calls: 最大调用次数
        period: 时间周期（秒）
    
    Usage:
        @rate_limit(max_calls=10, period=60)
        def withdraw_money(user_id: int, amount: int):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 获取标识符
            user_id = kwargs.get('user_id')
            identifier = str(user_id) if user_id else 'unknown'
            
            # 检查限流
            if not rate_limiter.check_rate_limit(identifier, max_calls, period):
                remaining = rate_limiter.get_remaining_calls(identifier, max_calls, period)
                logger.warning(f"限流触发: {identifier}, 剩余次数: {remaining}")
                return f"❌ 请求过于频繁，请{period}秒后再试"
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def check_permission_required(permission: str):
    """
    权限检查装饰器
    
    Args:
        permission: 需要的权限
    
    Usage:
        @check_permission_required('approve_withdrawal')
        def approve_withdrawal_request(...):
            pass
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_id = kwargs.get('user_id')
            
            if not user_id:
                return "❌ 未提供用户ID"
            
            # 检查权限
            if not permission_manager.check_permission(user_id, permission):
                logger.warning(f"权限不足: user_id={user_id}, permission={permission}")
                return f"❌ 权限不足，您无权执行此操作"
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


if __name__ == "__main__":
    # 测试安全框架
    print("=" * 60)
    print("安全框架测试")
    print("=" * 60)
    
    # 测试输入验证
    print("\n1. 输入验证测试:")
    print(f"手机号验证: {input_validator.validate_phone('13800138000')}")
    print(f"身份证验证: {input_validator.validate_id_card('110101199001011234')}")
    print(f"邮箱验证: {input_validator.validate_email('test@example.com')}")
    print(f"密码强度: {input_validator.validate_password('Test1234')}")
    
    # 测试SQL安全
    print("\n2. SQL安全测试:")
    safe_sql = "SELECT * FROM users WHERE id = 1"
    dangerous_sql = "DROP TABLE users"
    print(f"安全SQL: {sql_security.validate_sql(safe_sql)}")
    print(f"危险SQL: {sql_security.validate_sql(dangerous_sql)}")
    
    # 测试限流
    print("\n3. 限流测试:")
    for i in range(12):
        result = rate_limiter.check_rate_limit('test_user', 10, 60)
        print(f"请求{i+1}: {'✅' if result else '❌'}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
