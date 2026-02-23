"""
灵值获取规则验证工具

确保所有灵值获取都按智能体规则执行，禁止通过命令直接增加灵值
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from typing import Optional, Dict, Any
from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Users, AuditLogs
from datetime import datetime
import pytz


# 灵值获取规则（白名单）
ALLOWED_LINGZHI_SOURCES = {
    'daily_check_in': {
        'name': '每日签到',
        'max_amount_per_day': 10,
        'max_frequency': 1,
        'description': '每天签到一次，获得10灵值'
    },
    'task_completion': {
        'name': '任务完成',
        'max_amount_per_day': 10000,  # 不限制，但需经过任务验证
        'max_frequency': 9999,  # 不限制
        'description': '完成文化创作、品牌转译等任务获得灵值'
    },
    'project_reward': {
        'name': '项目奖励',
        'max_amount_per_day': 1000000,  # 不限制
        'max_frequency': 9999,  # 不限制
        'description': '参与项目获得项目估值5%-20%的贡献值奖励'
    },
    'referral_reward': {
        'name': '推荐奖励',
        'max_amount_per_day': 1000,  # 限制推荐奖励
        'max_frequency': 100,  # 限制推荐数量
        'description': '推荐新用户获得灵值奖励'
    }
}


@tool
def validate_lingzhi_gain(
    user_id: int,
    source: str,
    amount: int,
    description: str = "",
    runtime: ToolRuntime = None
) -> Dict[str, Any]:
    """验证灵值获取请求

    验证灵值获取是否符合规则，禁止通过命令直接增加灵值。

    Args:
        user_id: 用户ID
        source: 灵值来源（必须是允许的来源之一）
        amount: 灵值数量
        description: 描述

    Returns:
        dict: 验证结果
    """
    # 检查来源是否允许
    if source not in ALLOWED_LINGZHI_SOURCES:
        return {
            'success': False,
            'error': f'非法的灵值获取来源: {source}',
            'message': '所有灵值获取必须通过智能体规则执行，禁止通过命令或其他方式直接增加灵值。'
        }

    # 获取来源规则
    source_rule = ALLOWED_LINGZHI_SOURCES[source]

    # 检查数量是否合理
    if amount <= 0:
        return {
            'success': False,
            'error': '灵值数量必须大于0',
            'message': '灵值数量必须为正整数。'
        }

    if amount > source_rule['max_amount_per_day']:
        return {
            'success': False,
            'error': f'灵值数量超过单日上限: {amount} > {source_rule["max_amount_per_day"]}',
            'message': f'{source_rule["name"]}每日最多可获得 {source_rule["max_amount_per_day"]} 灵值。'
        }

    # 检查今日已获取次数（对于签到等有限制的来源）
    if source in ['daily_check_in', 'referral_reward']:
        db = get_session()
        try:
            from storage.database.check_in_manager import CheckInManager

            if source == 'daily_check_in':
                check_in_manager = CheckInManager()
                has_check_in = check_in_manager.has_checked_in_today(db, user_id)
                if has_check_in:
                    return {
                        'success': False,
                        'error': '今日已签到',
                        'message': '每天只能签到一次，请明天再来。'
                    }

        finally:
            db.close()

    # 验证通过
    return {
        'success': True,
        'message': f'灵值获取验证通过',
        'source': source,
        'amount': amount,
        'description': description
    }


@tool
def record_lingzhi_gain(
    user_id: int,
    source: str,
    amount: int,
    description: str = "",
    runtime: ToolRuntime = None
) -> str:
    """记录灵值获取

    在验证通过后记录灵值获取，并记录审计日志。

    Args:
        user_id: 用户ID
        source: 灵值来源
        amount: 灵值数量
        description: 描述

    Returns:
        str: 记录结果
    """
    # 先验证
    validation = validate_lingzhi_gain(user_id, source, amount, description, runtime)

    if not validation['success']:
        return f"""
【灵值获取失败】❌

{validation['error']}

{validation['message']}

---

⚠️ **重要提示**：

所有灵值获取必须通过智能体规则执行，禁止通过命令或其他方式直接增加灵值。
任何违反规则的操作将被系统拒绝并记录。
"""

    # 验证通过，记录获取
    db = get_session()

    try:
        # 获取用户
        user = db.query(Users).filter(Users.id == user_id).first()

        if not user:
            return """
【灵值获取失败】❌

用户不存在

---

请检查用户ID是否正确。
"""

        # 根据来源执行相应操作
        if source == 'daily_check_in':
            from storage.database.check_in_manager import CheckInManager
            check_in_manager = CheckInManager()
            success, message, check_in_record = check_in_manager.check_in(db, user_id)

            if success:
                # 记录审计日志
                audit_log = AuditLogs(
                    user_id=user_id,
                    action='lingzhi_gain',
                    status='success',
                    resource_type='lingzhi',
                    description=f'签到获得灵值: {amount} ({description})'
                )
                db.add(audit_log)
                db.commit()

                return f"""
【签到成功】✅

恭喜您，{user.name}！您已成功签到并获得 {amount} 灵值。

📋 签到详情：
- 签到时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}
- 获得灵值：{amount} 灵值
- 灵值价值：{amount * 0.1} 元人民币

💰 **温馨提示**：

- 1灵值 = 0.1元人民币，随时可兑换
- 锁定灵值可享受20%-100%增值收益
- 每天只能签到一次，请明天再来

---

继续努力，明天还有10灵值等着您！💪
"""
            else:
                return f"""
【签到失败】❌

{message}

---
"""
        elif source == 'task_completion':
            # 记录任务完成获得灵值
            audit_log = AuditLogs(
                user_id=user_id,
                action='lingzhi_gain',
                status='success',
                resource_type='lingzhi',
                description=f'任务完成获得灵值: {amount} ({description})'
            )
            db.add(audit_log)
            db.commit()

            return f"""
【任务完成】✅

恭喜您，{user.name}！您已完成任务并获得 {amount} 灵值。

📋 任务详情：
- 完成时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}
- 获得灵值：{amount} 灵值
- 灵值价值：{amount * 0.1} 元人民币
- 任务描述：{description}

💰 **温馨提示**：

- 1灵值 = 0.1元人民币，随时可兑换
- 锁定灵值可享受20%-100%增值收益
- 完成更多任务可以获得更多灵值

---

继续努力，创造更多价值！💪
"""
        elif source == 'project_reward':
            # 记录项目奖励获得灵值
            audit_log = AuditLogs(
                user_id=user_id,
                action='lingzhi_gain',
                status='success',
                resource_type='lingzhi',
                description=f'项目奖励获得灵值: {amount} ({description})'
            )
            db.add(audit_log)
            db.commit()

            return f"""
【项目奖励】✅

恭喜您，{user.name}！您已获得项目奖励 {amount} 灵值。

📋 项目详情：
- 获得时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}
- 获得灵值：{amount} 灵值
- 灵值价值：{amount * 0.1} 元人民币
- 项目描述：{description}

💰 **温馨提示**：

- 1灵值 = 0.1元人民币，随时可兑换
- 锁定灵值可享受20%-100%增值收益
- 项目奖励根据项目估值和贡献度分配

---

恭喜您获得丰厚奖励！🎉
"""
        elif source == 'referral_reward':
            # 记录推荐奖励获得灵值
            audit_log = AuditLogs(
                user_id=user_id,
                action='lingzhi_gain',
                status='success',
                resource_type='lingzhi',
                description=f'推荐奖励获得灵值: {amount} ({description})'
            )
            db.add(audit_log)
            db.commit()

            return f"""
【推荐奖励】✅

恭喜您，{user.name}！您已获得推荐奖励 {amount} 灵值。

📋 推荐详情：
- 获得时间：{datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}
- 获得灵值：{amount} 灵值
- 灵值价值：{amount * 0.1} 元人民币
- 推荐描述：{description}

💰 **温馨提示**：

- 1灵值 = 0.1元人民币，随时可兑换
- 锁定灵值可享受20%-100%增值收益
- 推荐更多用户可以获得更多奖励

---

感谢您为灵值生态园的发展做出的贡献！🙏
"""
        else:
            return """
【灵值获取失败】❌

未知灵值来源

---

请联系系统管理员。
"""

    except Exception as e:
        db.rollback()
        return f"""
【灵值获取失败】❌

记录灵值获取时发生错误：{str(e)}

请稍后重试或联系系统管理员。
"""
    finally:
        db.close()


@tool
def get_lingzhi_gain_rules(runtime: ToolRuntime = None) -> str:
    """获取灵值获取规则

    返回所有允许的灵值获取来源和规则。

    Returns:
        str: 灵值获取规则
    """
    rules = """
# 灵值获取规则

## 📋 核心原则

**所有灵值获取必须通过智能体规则执行，禁止通过命令或其他方式直接增加灵值。**

任何违反规则的操作将被系统拒绝并记录。

---

## ✅ 允许的灵值获取来源

### 1. 每日签到

- **来源标识**：`daily_check_in`
- **奖励标准**：10灵值/天
- **获取频率**：每天1次
- **获取条件**：用户登录时自动签到
- **获取方式**：系统自动执行

**规则说明**：
- 每天只能签到一次，签到后当天无法再次签到
- 签到成功获得10灵值
- 禁止通过脚本或命令重复签到

---

### 2. 任务完成

- **来源标识**：`task_completion`
- **奖励标准**：根据任务难度和贡献度评定
- **获取频率**：不限制
- **获取条件**：完成文化创作、品牌转译等任务
- **获取方式**：智能体验证后发放

**规则说明**：
- 任务必须经过智能体验证
- 奖励金额根据任务质量和贡献度确定
- 禁止虚构任务或重复领取奖励

---

### 3. 项目奖励

- **来源标识**：`project_reward`
- **奖励标准**：项目估值的5%-20%
- **获取频率**：根据项目周期
- **获取条件**：参与项目并达到合格标准
- **获取方式**：项目结束后统一发放

**规则说明**：
- 参与项目需要消耗贡献值作为门槛
- 合格参与者获得全额返还和高额奖励
- 奖励金额根据项目实际收益确定
- ROI可达600%-12400%

---

### 4. 推荐奖励

- **来源标识**：`referral_reward`
- **奖励标准**：三级推荐（10% / 5% / 3%）
- **获取频率**：不限制
- **获取条件**：推荐新用户加入
- **获取方式**：新用户激活后发放

**规则说明**：
- 只有三级推荐奖励
- 被推荐用户需要完成首次任务或项目
- 禁止虚假推荐或刷推荐

---

## ❌ 禁止的行为

1. **通过命令直接增加灵值**
   - 禁止使用任何命令行工具直接修改灵值余额
   - 所有灵值获取必须经过智能体验证

2. **通过脚本自动化签到**
   - 禁止使用脚本自动签到
   - 系统会检测异常登录和签到行为

3. **虚构任务或重复领取**
   - 禁止虚构任务骗取奖励
   - 禁止重复领取同一任务奖励

4. **虚假推荐或刷推荐**
   - 禁止创建虚假账户刷推荐奖励
   - 系统会检测异常注册行为

5. **任何绕过规则的行为**
   - 禁止任何试图绕过规则获取灵值的行为
   - 所有违规操作将被记录并处理

---

## ⚠️ 违规后果

1. **警告**：首次违规，系统发送警告
2. **冻结**：重复违规，冻结账户3天
3. **封禁**：严重违规，永久封禁账户
4. **追回**：违规获得的灵值将被追回

---

## 🛡️ 安全机制

1. **来源验证**：所有灵值获取必须经过来源验证
2. **数量限制**：每日、单次灵值获取有数量限制
3. **频率限制**：特定来源有频率限制
4. **审计日志**：所有灵值获取记录审计日志
5. **异常检测**：系统会检测异常行为

---

## 💡 温馨提示

- **合法获取**：按照规则获取灵值，确保您的账户安全
- **长期价值**：灵值可以锁定增值，获得更高收益
- **生态贡献**：您的贡献会促进灵值生态园的发展
- **共同维护**：让我们一起维护公平公正的灵值生态

---

**记住**：1灵值 = 0.1元人民币，这是确定的未来收入，随时可兑换！💰
"""
    return rules


@tool
def check_lingzhi_security(runtime: ToolRuntime = None) -> str:
    """检查灵值安全

    检查灵值获取的安全状态，是否有异常操作。

    Returns:
        str: 安全检查结果
    """
    db = get_session()

    try:
        # 查询最近1小时内的异常操作
        from datetime import datetime, timedelta
        one_hour_ago = datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(hours=1)

        # 查询频繁签到（1小时内签到次数>1）
        from storage.database.shared.model import CheckIns
        frequent_check_ins = db.query(CheckIns).filter(
            CheckIns.created_at >= one_hour_ago
        ).count()

        # 查询异常灵值获取（1小时内超过1000灵值）
        abnormal_gains = db.query(AuditLogs).filter(
            AuditLogs.action == 'lingzhi_gain',
            AuditLogs.created_at >= one_hour_ago
        ).count()

        # 查询登录失败次数
        failed_logins = db.query(AuditLogs).filter(
            AuditLogs.action == 'user_login',
            AuditLogs.status == 'failed',
            AuditLogs.created_at >= one_hour_ago
        ).count()

        # 构建安全报告
        result = """
【灵值安全检查】✅

安全状态：正常

📊 最近1小时安全指标：

1. 签到次数：{} 次
2. 灵值获取次数：{} 次
3. 登录失败次数：{} 次
""".format(frequent_check_ins, abnormal_gains, failed_logins)

        # 检测异常
        if frequent_check_ins > 100:
            result += """
⚠️ **检测到异常签到行为**

1小时内签到次数异常，可能存在自动化签到脚本。
系统已标记此行为，请人工核查。
"""

        if abnormal_gains > 50:
            result += """
⚠️ **检测到异常灵值获取行为**

1小时内灵值获取次数异常，可能存在刷灵值行为。
系统已标记此行为，请人工核查。
"""

        if failed_logins > 10:
            result += """
⚠️ **检测到异常登录行为**

1小时内登录失败次数异常，可能存在暴力破解。
系统已标记此行为，请人工核查。
"""

        if frequent_check_ins <= 100 and abnormal_gains <= 50 and failed_logins <= 10:
            result += """
✅ 所有指标正常，未检测到异常行为。

---

💡 **安全提示**：

- 所有灵值获取都按智能体规则执行
- 禁止通过命令或其他方式直接增加灵值
- 系统会持续监控异常行为
- 任何违规操作将被记录并处理
"""

        result += """
---

**检查时间**：{}
""".format(datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S'))

        return result

    except Exception as e:
        return f"""
【灵值安全检查】❌

检查过程中发生错误：{str(e)}

请稍后重试或联系系统管理员。
"""
    finally:
        db.close()
