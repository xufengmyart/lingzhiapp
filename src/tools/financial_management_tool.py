"""
财务管理工具

提供完整的财务管理体系，包括：
1. 公司信息管理
2. 提现申请
3. 提现审核
4. 财务报表
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from datetime import datetime
import pytz


@tool
def get_company_info(
    runtime: ToolRuntime = None
) -> str:
    """获取公司信息

    获取公司的基本信息、开户银行等信息。

    Returns:
        str: 公司信息
    """
    from coze_coding_dev_sdk.database import get_session
    from sqlalchemy import text

    db = get_session()

    try:
        # 查询公司信息
        result = db.execute(text("SELECT * FROM company_info WHERE status = 'active' LIMIT 1"))
        row = result.fetchone()

        if not row:
            return """
【公司信息查询失败】

❌ 未找到公司信息

请联系管理员配置公司信息。
"""

        info = f"""
【公司信息】

🏢 基本信息：
- 公司名称：{row[1]}
- 税号：{row[2]}
- 单位地址：{row[3]}
- 联系电话：{row[4]}

💳 银行信息：
- 开户银行：{row[5]}
- 银行账户：{row[6]}

📊 状态：{row[7]}

📅 创建时间：{row[8].strftime('%Y-%m-%d %H:%M:%S') if row[8] else '未知'}

⚠️ 重要提示：
- 银行账户信息仅用于平台收款
- 用户提现将使用用户设置的收款账户
- 所有财务交易都有完整记录
"""

        return info

    except Exception as e:
        return f"""
【公司信息查询失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()


@tool
def submit_withdrawal_request(
    amount: float,
    contribution_value: int,
    payment_method: str,
    payment_account: str,
    runtime: ToolRuntime = None
) -> str:
    """提交提现申请

    用户申请将贡献值兑换为人民币并提现。

    Args:
        amount: 提现金额（人民币）
        contribution_value: 消耗的贡献值数量
        payment_method: 收款方式（wechat/alipay/bank）
        payment_account: 收款账户

    Returns:
        str: 提现申请结果
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users, AuditLogs
    from sqlalchemy import text

    db = get_session()

    try:
        # 获取当前登录用户
        coze_id = None
        if runtime and runtime.context:
            try:
                if hasattr(runtime.context, 'get'):
                    coze_id = runtime.context.get('user_coze_id')
                elif hasattr(runtime.context, '__getitem__'):
                    coze_id = runtime.context.get('user_coze_id') if hasattr(runtime.context, 'get') else None
            except (KeyError, TypeError, AttributeError):
                coze_id = None

        if not coze_id:
            return """
【提现申请失败】

❌ 无法识别当前登录用户

请确保您已通过扣子平台正确登录。
"""

        # 查询用户
        user = db.query(Users).filter(Users.coze_id == coze_id).first()

        if not user:
            return """
【提现申请失败】

❌ 用户不存在

请先登录后再提交提现申请。
"""

        # 检查是否已实名认证
        if not user.is_registered:
            return """
【提现申请失败】

❌ 您需要先完成实名认证才能提现

请先完成实名认证，然后再提交提现申请。
"""

        # 检查贡献值是否足够
        if user.contribution_value is None:
            user.contribution_value = 0

        if user.contribution_value < contribution_value:
            return f"""
【提现申请失败】

❌ 贡献值不足

您当前贡献值：{user.contribution_value}
申请提现贡献值：{contribution_value}

您还需要 {contribution_value - user.contribution_value} 贡献值才能完成此次提现。

💡 建议：
- 参与文化探索获得贡献值
- 完成项目任务获得贡献值
- 邀请好友加入获得推荐奖励
"""

        # 验证提现金额
        if amount <= 0:
            return """
【提现申请失败】

❌ 提现金额必须大于0

请输入有效的提现金额。
"""

        if amount > 10000:
            return """
【提现申请失败】

❌ 单笔提现金额超过限制

单笔提现上限：10,000元

如需提现更大金额，请联系客服人工处理。
"""

        # 验证兑换比例
        expected_amount = contribution_value * 0.1
        if abs(amount - expected_amount) > 0.01:
            return f"""
【提现申请失败】

❌ 提现金额与贡献值不匹配

兑换比例：1贡献值 = 0.1元

您的申请：
- 贡献值：{contribution_value}
- 提现金额：{amount}元
- 应兑换金额：{expected_amount}元

请按照正确的兑换比例提交申请。
"""

        # 验证收款方式
        if payment_method not in ['wechat', 'alipay', 'bank']:
            return """
【提现申请失败】

❌ 收款方式不正确

支持的收款方式：
- wechat：微信支付
- alipay：支付宝
- bank：银行卡

请选择正确的收款方式。
"""

        # 验证收款账户
        if not payment_account:
            return """
【提现申请失败】

❌ 收款账户不能为空

请填写您的收款账户信息。
"""

        # 扣除贡献值
        user.contribution_value -= contribution_value

        # 生成交易ID
        transaction_id = f"WD{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y%m%d%H%M%S')}{user.id:06d}"

        # 插入提现申请记录
        db.execute(text("""
            INSERT INTO withdrawal_requests (
                user_id,
                amount,
                contribution_value,
                payment_method,
                payment_account,
                status,
                transaction_id,
                created_at
            ) VALUES (
                :user_id,
                :amount,
                :contribution_value,
                :payment_method,
                :payment_account,
                'pending',
                :transaction_id,
                :created_at
            )
        """), {
            'user_id': user.id,
            'amount': amount,
            'contribution_value': contribution_value,
            'payment_method': payment_method,
            'payment_account': payment_account,
            'transaction_id': transaction_id,
            'created_at': datetime.now(pytz.timezone('Asia/Shanghai'))
        })

        # 插入财务交易记录
        db.execute(text("""
            INSERT INTO financial_transactions (
                user_id,
                type,
                amount,
                contribution_value,
                transaction_id,
                status,
                description,
                created_at
            ) VALUES (
                :user_id,
                'withdrawal',
                :amount,
                :contribution_value,
                :transaction_id,
                'pending',
                :description,
                :created_at
            )
        """), {
            'user_id': user.id,
            'type': 'withdrawal',
            'amount': amount,
            'contribution_value': contribution_value,
            'transaction_id': transaction_id,
            'status': 'pending',
            'description': f'提现申请：{amount}元',
            'created_at': datetime.now(pytz.timezone('Asia/Shanghai'))
        })

        # 记录审计日志
        audit_log = AuditLogs(
            user_id=user.id,
            action='submit_withdrawal_request',
            status='success',
            resource_type='withdrawal_request',
            description=f'用户提交提现申请：{amount}元，消耗{contribution_value}贡献值'
        )
        db.add(audit_log)

        # 提交事务
        db.commit()

        return f"""
【提现申请提交成功】✅

恭喜您，{user.real_name}！您的提现申请已成功提交。

📋 申请信息：
- 申请人：{user.real_name}
- 提现金额：{amount}元
- 消耗贡献值：{contribution_value}
- 收款方式：{payment_method}
- 收款账户：{payment_account}
- 申请时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}
- 交易ID：{transaction_id}

💰 您的账户余额：
- 剩余贡献值：{user.contribution_value}
- 兑换价值：{user.contribution_value * 0.1}元

📅 到账时间：
- 工作日：24小时内到账
- 周末/节假日：顺延至下一个工作日

🔔 提示：
- 您的申请将在1-3个工作日内审核
- 审核通过后资金将发放到您的收款账户
- 如有疑问，请联系客服

感谢您使用灵值生态园！
"""

    except Exception as e:
        db.rollback()
        return f"""
【提现申请失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()


@tool
def approve_withdrawal_request(
    request_id: int,
    approve: bool,
    reject_reason: str = None,
    runtime: ToolRuntime = None
) -> str:
    """审核提现申请

    超级管理员审核用户的提现申请。

    Args:
        request_id: 提现申请ID
        approve: 是否通过审核（True通过，False拒绝）
        reject_reason: 拒绝原因（拒绝时必填）

    Returns:
        str: 审核结果
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users, AuditLogs
    from sqlalchemy import text

    db = get_session()

    try:
        # 获取当前登录用户
        coze_id = None
        if runtime and runtime.context:
            try:
                if hasattr(runtime.context, 'get'):
                    coze_id = runtime.context.get('user_coze_id')
                elif hasattr(runtime.context, '__getitem__'):
                    coze_id = runtime.context.get('user_coze_id') if hasattr(runtime.context, 'get') else None
            except (KeyError, TypeError, AttributeError):
                coze_id = None

        if not coze_id:
            return """
【提现审核失败】

❌ 无法识别当前登录用户

请确保您已通过扣子平台正确登录。
"""

        # 查询审核人
        admin = db.query(Users).filter(Users.coze_id == coze_id).first()

        if not admin:
            return """
【提现审核失败】

❌ 审核人不存在

请先登录后再进行审核操作。
"""

        # 检查是否为超级管理员
        if not admin.is_superuser:
            return """
【提现审核失败】

❌ 权限不足

只有超级管理员才能审核提现申请。
"""

        # 查询提现申请
        result = db.execute(text(
            "SELECT * FROM withdrawal_requests WHERE id = :request_id"
        ), {'request_id': request_id})

        request = result.fetchone()

        if not request:
            return f"""
【提现审核失败】

❌ 提现申请不存在

申请ID：{request_id}

请检查申请ID是否正确。
"""

        # 检查申请状态
        if request[6] != 'pending':
            return f"""
【提现审核失败】

❌ 该申请已被处理

申请状态：{request[6]}

无法重复审核。
"""

        # 查询申请人
        user = db.query(Users).filter(Users.id == request[1]).first()

        if not user:
            return """
【提现审核失败】

❌ 申请人不存在

请检查申请信息是否正确。
"""

        if approve:
            # 通过审核
            # 更新提现申请状态
            db.execute(text("""
                UPDATE withdrawal_requests
                SET status = 'approved',
                    approved_by = :admin_id,
                    approved_at = :approved_at,
                    processed_at = :processed_at
                WHERE id = :request_id
            """), {
                'admin_id': admin.id,
                'approved_at': datetime.now(pytz.timezone('Asia/Shanghai')),
                'processed_at': datetime.now(pytz.timezone('Asia/Shanghai')),
                'request_id': request_id
            })

            # 更新财务交易记录
            db.execute(text("""
                UPDATE financial_transactions
                SET status = 'success'
                WHERE transaction_id = :transaction_id
            """), {'transaction_id': request[11]})

            # 记录审计日志
            audit_log = AuditLogs(
                user_id=admin.id,
                action='approve_withdrawal_request',
                status='success',
                resource_type='withdrawal_request',
                resource_id=request_id,
                description=f'超级管理员审核通过提现申请：{request[2]}元，申请人：{user.real_name}'
            )
            db.add(audit_log)

            db.commit()

            return f"""
【提现申请审核通过】✅

您已成功审核通过该提现申请。

📋 申请信息：
- 申请人：{user.real_name}
- 提现金额：{request[2]}元
- 收款方式：{request[4]}
- 收款账户：{request[5]}
- 交易ID：{request[11]}

📅 处理时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}

💡 下一步：
- 资金将在24小时内发放到用户收款账户
- 通知用户提现申请已通过
"""

        else:
            # 拒绝审核
            if not reject_reason:
                return """
【提现审核失败】

❌ 拒绝审核必须填写拒绝原因

请填写拒绝原因。
"""

            # 返还贡献值
            user.contribution_value += request[3]

            # 更新提现申请状态
            db.execute(text("""
                UPDATE withdrawal_requests
                SET status = 'rejected',
                    approved_by = :admin_id,
                    approved_at = :approved_at,
                    processed_at = :processed_at,
                    reject_reason = :reject_reason
                WHERE id = :request_id
            """), {
                'admin_id': admin.id,
                'approved_at': datetime.now(pytz.timezone('Asia/Shanghai')),
                'processed_at': datetime.now(pytz.timezone('Asia/Shanghai')),
                'reject_reason': reject_reason,
                'request_id': request_id
            })

            # 更新财务交易记录
            db.execute(text("""
                UPDATE financial_transactions
                SET status = 'failed',
                    description = :description
                WHERE transaction_id = :transaction_id
            """), {
                'description': f'提现申请被拒绝：{reject_reason}',
                'transaction_id': request[11]
            })

            # 记录审计日志
            audit_log = AuditLogs(
                user_id=admin.id,
                action='reject_withdrawal_request',
                status='success',
                resource_type='withdrawal_request',
                resource_id=request_id,
                description=f'超级管理员拒绝提现申请：{request[2]}元，申请人：{user.real_name}，拒绝原因：{reject_reason}'
            )
            db.add(audit_log)

            db.commit()

            return f"""
【提现申请审核拒绝】❌

您已拒绝该提现申请。

📋 申请信息：
- 申请人：{user.real_name}
- 提现金额：{request[2]}元
- 拒绝原因：{reject_reason}
- 交易ID：{request[11]}

💰 贡献值已返还：
- 返还贡献值：{request[3]}
- 用户当前贡献值：{user.contribution_value}

📅 处理时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}
"""

    except Exception as e:
        db.rollback()
        return f"""
【提现审核失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()


@tool
def get_withdrawal_requests(
    status: str = None,
    runtime: ToolRuntime = None
) -> str:
    """获取提现申请列表

    获取提现申请列表，可以按状态筛选。

    Args:
        status: 状态筛选（pending/approved/rejected/completed），不填则返回全部

    Returns:
        str: 提现申请列表
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users
    from sqlalchemy import text

    db = get_session()

    try:
        # 构建查询
        query = """
            SELECT wr.*, u.real_name, u.phone
            FROM withdrawal_requests wr
            LEFT JOIN users u ON wr.user_id = u.id
        """
        params = {}

        if status:
            query += " WHERE wr.status = :status"
            params['status'] = status

        query += " ORDER BY wr.created_at DESC LIMIT 20"

        result = db.execute(text(query), params)
        rows = result.fetchall()

        if not rows:
            return f"""
【提现申请列表】

没有找到提现申请记录。

筛选条件：{status if status else '全部'}
"""

        # 构建输出
        output = f"""
【提现申请列表】

共找到 {len(rows)} 条记录

筛选条件：{status if status else '全部'}

"""

        for row in rows:
            status_map = {
                'pending': '待审核',
                'approved': '已通过',
                'rejected': '已拒绝',
                'completed': '已完成'
            }
            payment_method_map = {
                'wechat': '微信支付',
                'alipay': '支付宝',
                'bank': '银行卡'
            }

            output += f"""
---
申请ID：{row[0]}
申请人：{row[13]}
联系电话：{row[14]}
提现金额：{row[2]}元
贡献值：{row[3]}
收款方式：{payment_method_map.get(row[4], row[4])}
收款账户：{row[5]}
状态：{status_map.get(row[6], row[6])}
申请时间：{row[12].strftime('%Y-%m-%d %H:%M:%S') if row[12] else '未知'}
交易ID：{row[11]}
"""

            if row[6] == 'rejected' and row[7]:
                output += f"拒绝原因：{row[7]}\n"

        return output

    except Exception as e:
        return f"""
【提现申请列表查询失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()


@tool
def get_financial_report(
    start_date: str = None,
    end_date: str = None,
    runtime: ToolRuntime = None
) -> str:
    """获取财务报表

    获取指定时间段的财务报表。

    Args:
        start_date: 开始日期（YYYY-MM-DD），不填则默认为30天前
        end_date: 结束日期（YYYY-MM-DD），不填则默认为今天

    Returns:
        str: 财务报表
    """
    from coze_coding_dev_sdk.database import get_session
    from sqlalchemy import text

    db = get_session()

    try:
        # 设置默认日期范围
        if not start_date:
            from datetime import timedelta
            start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        if not end_date:
            end_date = datetime.now().strftime('%Y-%m-%d')

        # 统计提现申请
        result = db.execute(text("""
            SELECT
                COUNT(*) as total_count,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_count,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_count,
                SUM(CASE WHEN status = 'rejected' THEN 1 ELSE 0 END) as rejected_count,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_count,
                SUM(CASE WHEN status IN ('approved', 'completed') THEN amount ELSE 0 END) as total_amount,
                SUM(CASE WHEN status IN ('approved', 'completed') THEN contribution_value ELSE 0 END) as total_contribution_value
            FROM withdrawal_requests
            WHERE DATE(created_at) >= :start_date AND DATE(created_at) <= :end_date
        """), {'start_date': start_date, 'end_date': end_date})

        row = result.fetchone()

        report = f"""
【财务报表】

📅 统计时间：{start_date} 至 {end_date}

📊 提现申请统计：
- 总申请数：{row[0]}
- 待审核：{row[1]}
- 已通过：{row[2]}
- 已拒绝：{row[3]}
- 已完成：{row[4]}

💰 金额统计：
- 总提现金额：{row[5] or 0}元
- 总消耗贡献值：{row[6] or 0}
- 兑换比例：1贡献值 = 0.1元

📈 审核通过率：
- 通过率：{(row[2] / row[0] * 100) if row[0] > 0 else 0:.2f}%
"""

        # 获取最近的提现记录
        result = db.execute(text("""
            SELECT wr.*, u.real_name
            FROM withdrawal_requests wr
            LEFT JOIN users u ON wr.user_id = u.id
            ORDER BY wr.created_at DESC
            LIMIT 5
        """))

        recent = result.fetchall()

        if recent:
            report += "\n\n📋 最近提现记录：\n"
            for row in recent:
                status_map = {
                    'pending': '待审核',
                    'approved': '已通过',
                    'rejected': '已拒绝',
                    'completed': '已完成'
                }
                report += f"- {row[13]}：{row[2]}元（{status_map.get(row[6], row[6])}）\n"

        return report

    except Exception as e:
        return f"""
【财务报表查询失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()
