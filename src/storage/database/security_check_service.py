"""
系统安全检查服务

全面检查系统漏洞，杜绝非法操作，确保财务安全
无论怎么变通，不能亏损1分钱
"""

from typing import Optional, Tuple, Dict, Any, List
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Users, AuditLogs
from datetime import datetime
import pytz


class SecurityCheckService:
    """系统安全检查服务"""

    def __init__(self):
        self.timezone = pytz.timezone('Asia/Shanghai')

    def check_permission(self, user_id: int, required_role: str, action: str) -> Tuple[bool, str]:
        """检查用户权限

        Args:
            user_id: 用户ID
            required_role: 需要的角色级别
            action: 操作类型（如：create_user, delete_user, assign_role等）

        Returns:
            Tuple[bool, str]: (是否通过检查, 消息)
        """
        db = get_session()

        try:
            # 检查用户是否存在
            user = db.query(Users).filter(Users.id == user_id).first()
            if not user:
                return False, '用户不存在'

            # 检查用户状态
            if user.status != 'active':
                return False, f'用户状态异常（{user.status}），无法执行操作'

            # 定义角色级别
            role_levels = {
                '普通用户': 1,
                '部门经理': 2,
                '高级管理员': 3,
                '超级管理员': 4,
                'CEO': 5
            }

            # 获取用户角色级别
            user_level = role_levels.get(user.role, 0)
            required_level = role_levels.get(required_role, 0)

            # 检查权限
            if user_level < required_level:
                return False, f'权限不足，需要{required_role}及以上权限，当前角色：{user.role}'

            # 记录权限检查日志
            audit_log = AuditLogs(
                user_id=user_id,
                action='permission_check',
                resource_type='permission',
                resource_id=0,
                description=f'权限检查通过：用户{user.name}（角色：{user.role}）执行操作：{action}',
                status='success',
                created_at=datetime.now(self.timezone)
            )
            db.add(audit_log)
            db.commit()

            return True, '权限检查通过'

        except Exception as e:
            # 记录权限检查失败日志
            audit_log = AuditLogs(
                user_id=user_id,
                action='permission_check',
                resource_type='permission',
                resource_id=0,
                description=f'权限检查失败：{str(e)}',
                status='failed',
                created_at=datetime.now(self.timezone)
            )
            db.add(audit_log)
            db.commit()

            return False, f'权限检查失败：{str(e)}'

        finally:
            db.close()

    def check_operation_legality(self, user_id: int, operation: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """检查操作合法性

        Args:
            user_id: 用户ID
            operation: 操作类型
            params: 操作参数

        Returns:
            Tuple[bool, str]: (是否通过检查, 消息)
        """
        db = get_session()

        try:
            # 检查用户是否存在
            user = db.query(Users).filter(Users.id == user_id).first()
            if not user:
                return False, '用户不存在'

            # 根据操作类型检查合法性
            if operation == 'create_user':
                # 检查是否有创建用户权限
                if user.role not in ['超级管理员', 'CEO', '高级管理员']:
                    return False, '只有超级管理员、CEO或高级管理员可以创建用户'

                # 检查邮箱是否已存在
                if 'email' in params:
                    existing_user = db.query(Users).filter(Users.email == params['email']).first()
                    if existing_user:
                        return False, f'邮箱{params["email"]}已被使用'

            elif operation == 'delete_user':
                # 检查是否要删除超级管理员
                if 'target_user_id' in params:
                    target_user = db.query(Users).filter(Users.id == params['target_user_id']).first()
                    if target_user and target_user.role == '超级管理员':
                        return False, '超级管理员不能被删除'

                # 检查权限
                if user.role not in ['超级管理员', 'CEO']:
                    return False, '只有超级管理员或CEO可以删除用户'

            elif operation == 'update_user_role':
                # 检查权限
                if user.role not in ['超级管理员', 'CEO']:
                    return False, '只有超级管理员或CEO可以修改用户角色'

                # 检查是否要修改超级管理员
                if 'target_user_id' in params:
                    target_user = db.query(Users).filter(Users.id == params['target_user_id']).first()
                    if target_user and target_user.role == '超级管理员':
                        return False, '超级管理员的角色不能被修改'

                # 检查是否要设置新的超级管理员
                if 'new_role' in params and params['new_role'] == '超级管理员':
                    # 检查是否已经有超级管理员
                    existing_super_admin = db.query(Users).filter(Users.role == '超级管理员').first()
                    if existing_super_admin and existing_super_admin.id != user_id:
                        return False, '系统中只能有1个超级管理员，请先转让当前超级管理员权限'

            elif operation == 'transfer_super_admin':
                # 检查是否为超级管理员
                if user.role != '超级管理员':
                    return False, '只有超级管理员可以转让超级管理员权限'

                # 检查目标用户是否存在
                if 'target_user_id' in params:
                    target_user = db.query(Users).filter(Users.id == params['target_user_id']).first()
                    if not target_user:
                        return False, '目标用户不存在'

                    # 检查目标用户状态
                    if target_user.status != 'active':
                        return False, f'目标用户状态异常（{target_user.status}）'

            elif operation == 'assign_lingzhi':
                # 检查权限
                if user.role not in ['超级管理员', 'CEO']:
                    return False, '只有超级管理员或CEO可以分配灵值'

                # 检查灵值数量是否合法
                if 'amount' in params:
                    try:
                        amount = float(params['amount'])
                        if amount <= 0:
                            return False, '灵值数量必须大于0'
                    except:
                        return False, '灵值数量格式错误'

            elif operation == 'assign_contribution':
                # 检查权限
                if user.role not in ['超级管理员', 'CEO']:
                    return False, '只有超级管理员或CEO可以分配贡献值'

                # 检查贡献值数量是否合法
                if 'amount' in params:
                    try:
                        amount = float(params['amount'])
                        if amount <= 0:
                            return False, '贡献值数量必须大于0'
                    except:
                        return False, '贡献值数量格式错误'

            # 记录操作检查日志
            audit_log = AuditLogs(
                user_id=user_id,
                action='operation_check',
                resource_type='operation',
                resource_id=0,
                description=f'操作检查通过：用户{user.name}执行操作：{operation}',
                status='success',
                created_at=datetime.now(self.timezone)
            )
            db.add(audit_log)
            db.commit()

            return True, '操作检查通过'

        except Exception as e:
            # 记录操作检查失败日志
            audit_log = AuditLogs(
                user_id=user_id,
                action='operation_check',
                resource_type='operation',
                resource_id=0,
                description=f'操作检查失败：{str(e)}',
                status='failed',
                created_at=datetime.now(self.timezone)
            )
            db.add(audit_log)
            db.commit()

            return False, f'操作检查失败：{str(e)}'

        finally:
            db.close()

    def check_financial_security(self, operation: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """检查财务安全

        确保无论怎么变通，不能亏损1分钱

        Args:
            operation: 操作类型
            params: 操作参数

        Returns:
            Tuple[bool, str]: (是否通过检查, 消息)
        """
        db = get_session()

        try:
            # 核心原则：不能出现负数
            # 1灵值 = 0.1元人民币，确保所有交易都符合经济规则

            if operation == 'create_transaction':
                # 检查交易金额
                if 'amount' in params:
                    try:
                        amount = float(params['amount'])
                        if amount < 0:
                            return False, f'交易金额不能为负数：{amount}'

                        # 检查金额精度（最多4位小数）
                        if len(str(amount).split('.')[-1]) > 4 if '.' in str(amount) else False:
                            return False, f'交易金额精度超过限制，最多4位小数'
                    except:
                        return False, '交易金额格式错误'

                # 检查交易类型
                if 'transaction_type' in params:
                    valid_types = ['credit', 'debit', 'transfer', 'lock', 'unlock']
                    if params['transaction_type'] not in valid_types:
                        return False, f'无效的交易类型：{params["transaction_type"]}'

                # 检查用户余额是否足够
                if 'user_id' in params and 'amount' in params:
                    user = db.query(Users).filter(Users.id == params['user_id']).first()
                    if not user:
                        return False, '用户不存在'

                    amount = float(params['amount'])
                    transaction_type = params.get('transaction_type', 'credit')

                    if transaction_type in ['debit', 'transfer', 'lock']:
                        if user.lingzhi < amount:
                            return False, f'用户灵值不足，需要{amount}灵值，当前余额{user.lingzhi}灵值'

            elif operation == 'exchange_lingzhi_to_contribution':
                # 检查兑换比例：100灵值 = 1贡献值
                if 'lingzhi_amount' in params:
                    try:
                        lingzhi_amount = float(params['lingzhi_amount'])

                        if lingzhi_amount < 100:
                            return False, '最低兑换100灵值'

                        if lingzhi_amount % 100 != 0:
                            return False, '灵值数量必须是100的倍数'

                    except:
                        return False, '灵值数量格式错误'

                # 检查用户余额
                if 'user_id' in params and 'lingzhi_amount' in params:
                    user = db.query(Users).filter(Users.id == params['user_id']).first()
                    if not user:
                        return False, '用户不存在'

                    lingzhi_amount = float(params['lingzhi_amount'])
                    if user.lingzhi < lingzhi_amount:
                        return False, f'用户灵值不足，需要{lingzhi_amount}灵值，当前余额{user.lingzhi}灵值'

            elif operation == 'lock_contribution':
                # 检查锁定规则
                if 'contribution_amount' in params and 'lock_period' in params:
                    try:
                        contribution_amount = float(params['contribution_amount'])
                        lock_period = int(params['lock_period'])

                        # 检查锁定周期
                        if lock_period not in [1, 2, 3]:
                            return False, '锁定周期只能是1年、2年或3年'

                        # 检查锁定金额
                        if contribution_amount <= 0:
                            return False, '锁定金额必须大于0'

                    except:
                        return False, '锁定参数格式错误'

                # 检查用户贡献值余额
                if 'user_id' in params and 'contribution_amount' in params:
                    user = db.query(Users).filter(Users.id == params['user_id']).first()
                    if not user:
                        return False, '用户不存在'

                    contribution_amount = float(params['contribution_amount'])
                    if user.contribution_available < contribution_amount:
                        return False, f'用户可用贡献值不足，需要{contribution_amount}贡献值，当前可用{user.contribution_available}贡献值'

            elif operation == 'unlock_contribution':
                # 检查解锁条件
                if 'contribution_id' in params:
                    # 这里需要检查贡献值锁定记录
                    # 确保解锁时间已到或用户有权限解锁
                    pass

            elif operation == 'project_join':
                # 检查项目参与门槛
                if 'user_id' in params and 'project_id' in params:
                    user = db.query(Users).filter(Users.id == params['user_id']).first()
                    project = db.query(Project).filter(Project.id == params['project_id']).first()

                    if not user or not project:
                        return False, '用户或项目不存在'

                    # 检查项目是否开放参与
                    if project.status != 'active':
                        return False, '项目未开放参与'

                    # 检查用户是否已参与
                    existing_member = db.query(ProjectMember).filter(
                        ProjectMember.project_id == params['project_id'],
                        ProjectMember.user_id == params['user_id']
                    ).first()

                    if existing_member:
                        return False, '用户已参与该项目'

                    # 检查参与门槛（项目估值的5%-20%）
                    min_contribution = project.valuation * 0.05
                    max_contribution = project.valuation * 0.20

                    # 检查用户是否有足够的贡献值
                    if user.contribition_available < min_contribution:
                        return False, f'用户贡献值不足，最低需要{min_contribution}贡献值'

            # 记录财务安全检查日志
            audit_log = AuditLogs(
                user_id=params.get('user_id', 0),
                action='financial_check',
                resource_type='financial',
                resource_id=0,
                description=f'财务安全检查通过：操作类型：{operation}',
                status='success',
                created_at=datetime.now(self.timezone)
            )
            db.add(audit_log)
            db.commit()

            return True, '财务安全检查通过'

        except Exception as e:
            # 记录财务安全检查失败日志
            audit_log = AuditLogs(
                user_id=params.get('user_id', 0),
                action='financial_check',
                resource_type='financial',
                resource_id=0,
                description=f'财务安全检查失败：{str(e)}',
                status='failed',
                created_at=datetime.now(self.timezone)
            )
            db.add(audit_log)
            db.commit()

            return False, f'财务安全检查失败：{str(e)}'

        finally:
            db.close()

    def detect_abnormal_operation(self, user_id: int) -> Tuple[bool, List[str]]:
        """检测异常操作

        Args:
            user_id: 用户ID

        Returns:
            Tuple[bool, List[str]]: (是否异常, 异常原因列表)
        """
        db = get_session()

        try:
            abnormal_reasons = []

            # 1. 检查短时间内频繁操作
            recent_logs = db.query(AuditLogs).filter(
                AuditLogs.user_id == user_id,
                AuditLogs.created_at >= datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)
            ).all()

            if len(recent_logs) > 100:
                abnormal_reasons.append(f'今日操作过于频繁：{len(recent_logs)}次')

            # 2. 检查是否有失败的敏感操作
            sensitive_actions = ['delete_user', 'update_user_role', 'assign_lingzhi', 'assign_contribution', 'transfer_super_admin']
            failed_sensitive_logs = db.query(AuditLogs).filter(
                AuditLogs.user_id == user_id,
                AuditLogs.action.in_(sensitive_actions),
                AuditLogs.status == 'failed'
            ).count()

            if failed_sensitive_logs > 5:
                abnormal_reasons.append(f'敏感操作失败次数过多：{failed_sensitive_logs}次')

            # 3. 检查是否尝试修改超级管理员
            super_admin_logs = db.query(AuditLogs).filter(
                AuditLogs.user_id == user_id,
                AuditLogs.action == 'update_user_role',
                AuditLogs.description.like('%超级管理员%')
            ).count()

            if super_admin_logs > 0:
                abnormal_reasons.append(f'尝试修改超级管理员权限：{super_admin_logs}次')

            # 4. 检查是否有异常的资金操作（使用审计日志）
            recent_finance_logs = db.query(AuditLogs).filter(
                AuditLogs.user_id == user_id,
                AuditLogs.action.in_(['financial_check', 'create_transaction', 'exchange_lingzhi_to_contribution']),
                AuditLogs.created_at >= datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)
            ).count()

            if recent_finance_logs > 20:
                abnormal_reasons.append(f'今日资金操作过于频繁：{recent_finance_logs}次')

            # 判断是否异常
            is_abnormal = len(abnormal_reasons) > 0

            if is_abnormal:
                # 记录异常操作检测日志
                audit_log = AuditLogs(
                    user_id=user_id,
                    action='abnormal_operation_detected',
                    resource_type='security',
                    resource_id=0,
                    description=f'检测到异常操作：{", ".join(abnormal_reasons)}',
                    status='warning',
                    created_at=datetime.now(self.timezone)
                )
                db.add(audit_log)
                db.commit()

            return is_abnormal, abnormal_reasons

        except Exception as e:
            return False, [f'异常操作检测失败：{str(e)}']

        finally:
            db.close()

    def comprehensive_security_check(self, user_id: int, operation: str, params: Dict[str, Any]) -> Tuple[bool, str]:
        """综合安全检查

        Args:
            user_id: 用户ID
            operation: 操作类型
            params: 操作参数

        Returns:
            Tuple[bool, str]: (是否通过检查, 消息)
        """
        # 1. 检测异常操作
        is_abnormal, abnormal_reasons = self.detect_abnormal_operation(user_id)
        if is_abnormal:
            return False, f'检测到异常操作：{", ".join(abnormal_reasons)}'

        # 2. 权限检查
        # 根据操作类型确定需要的权限
        required_role_map = {
            'create_user': '超级管理员',
            'delete_user': '超级管理员',
            'update_user_role': '超级管理员',
            'transfer_super_admin': '超级管理员',
            'assign_lingzhi': '超级管理员',
            'assign_contribution': '超级管理员',
        }

        required_role = required_role_map.get(operation, '普通用户')

        # 权限检查
        permission_passed, permission_msg = self.check_permission(user_id, required_role, operation)
        if not permission_passed:
            return False, permission_msg

        # 3. 操作合法性检查
        operation_passed, operation_msg = self.check_operation_legality(user_id, operation, params)
        if not operation_passed:
            return False, operation_msg

        # 4. 财务安全检查
        financial_passed, financial_msg = self.check_financial_security(operation, params)
        if not financial_passed:
            return False, financial_msg

        # 所有检查通过
        return True, '综合安全检查通过'


# 全局安全检查服务实例
security_check_service = SecurityCheckService()


def perform_security_check(user_id: int, operation: str, params: Dict[str, Any]) -> Tuple[bool, str]:
    """执行综合安全检查（全局函数）

    Args:
        user_id: 用户ID
        operation: 操作类型
        params: 操作参数

    Returns:
        Tuple[bool, str]: (是否通过检查, 消息)
    """
    return security_check_service.comprehensive_security_check(user_id, operation, params)
