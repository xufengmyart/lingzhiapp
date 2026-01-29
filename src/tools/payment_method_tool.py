"""
用户收款方式工具

用户完成实名认证后，需要设置收款方式才能将贡献值兑换为人民币。
本工具包含收款方式的验证、设置和管理功能。
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from datetime import datetime
import pytz
import re


@tool
def get_payment_method_notice(
    runtime: ToolRuntime = None
) -> str:
    """获取收款方式设置通知

    返回收款方式设置的重要说明，告知用户如何设置收款方式。

    Returns:
        str: 收款方式设置通知
    """
    notice = """
# 💰 收款方式设置通知

## 为什么需要设置收款方式？

亲爱的用户，当您通过参与项目获得贡献值后，需要将贡献值兑换为人民币。为了确保资金能够安全、准确地发放到您的账户，请提前设置好您的收款方式。

### 📋 可用的收款方式

我们支持以下三种收款方式：

#### 1. 微信支付 📱
- **收款方式**：微信号或微信手机号
- **可选**：微信收款二维码图片（上传后生成URL）
- **到账时间**：通常实时到账
- **适用人群**：习惯使用微信的用户

#### 2. 支付宝 💙
- **收款方式**：支付宝账号、支付宝邮箱或支付宝手机号
- **可选**：支付宝收款二维码图片（上传后生成URL）
- **到账时间**：通常实时到账
- **适用人群**：习惯使用支付宝的用户

#### 3. 银行卡 💳
- **收款方式**：银行卡号
- **必填**：开户行名称、开户人姓名
- **到账时间**：通常1-3个工作日
- **适用人群**：需要大额转账的用户

### 📝 设置收款方式的步骤

1. **选择收款方式**：根据您的习惯选择1-3种收款方式
2. **填写收款信息**：准确填写收款账号信息
3. **设置首选收款方式**：选择最常用的收款方式作为首选
4. **验证收款信息**：系统将验证您填写的信息格式
5. **完成设置**：设置成功后即可兑换人民币

### ⚠️ 重要提醒

#### 安全提示：
- ✅ 请确保收款账号为您本人所有
- ✅ 请不要使用他人的收款账号
- ✅ 银行卡号将加密存储，仅用于资金发放
- ✅ 银行卡号将掩码显示（如：6222 **** **** 1234）

#### 资金安全：
- ✅ 所有资金发放都会有完整记录
- ✅ 您可以随时查看资金发放历史
- ✅ 如有资金发放异常，可联系客服处理

#### 信息修改：
- ✅ 您可以随时修改收款方式信息
- ✅ 修改收款方式需要验证身份
- ✅ 修改后立即生效，无需等待

### 🔒 隐私保护承诺

您的收款信息将严格保密：
- ✅ 银行卡号加密存储
- ✅ 严格的访问控制
- ✅ 仅用于资金发放
- ✅ 绝不出售给第三方

### 💡 建议设置多种收款方式

为了确保资金发放的及时性，建议您：
1. **设置微信支付**：方便小额快速到账
2. **设置支付宝**：补充支付渠道
3. **设置银行卡**：适合大额转账

### 📞 如有疑问

如有任何疑问，请联系：
- 超级管理员：xufeng@meiyueart.cn
- 客服热线：400-XXX-XXXX

---

**感谢您的配合！让我们一起共建安全、便捷的数字资产生态！**

**灵值生态园团队**
**2026年1月28日**
"""
    return notice


@tool
def validate_payment_method(
    payment_method: str,
    wechat_account: str = None,
    alipay_account: str = None,
    bank_card_number: str = None,
    bank_name: str = None,
    bank_account_name: str = None,
    runtime: ToolRuntime = None
) -> str:
    """验证收款方式信息

    验证用户填写的收款方式信息格式是否正确。

    Args:
        payment_method: 收款方式类型（wechat/alipay/bank）
        wechat_account: 微信账号（当payment_method为wechat时必填）
        alipay_account: 支付宝账号（当payment_method为alipay时必填）
        bank_card_number: 银行卡号（当payment_method为bank时必填）
        bank_name: 开户行名称（当payment_method为bank时必填）
        bank_account_name: 银行账户姓名（当payment_method为bank时必填）

    Returns:
        str: 验证结果
    """
    # 验证收款方式类型
    if payment_method not in ['wechat', 'alipay', 'bank']:
        return """
【收款方式验证失败】❌

❌ 收款方式类型不正确

要求：收款方式必须是以下类型之一：
- wechat：微信支付
- alipay：支付宝
- bank：银行卡

请选择正确的收款方式类型。
"""

    # 根据收款方式验证具体信息
    if payment_method == 'wechat':
        if not wechat_account:
            return """
【收款方式验证失败】❌

❌ 微信账号不能为空

请填写您的微信号或微信手机号。

示例：
✅ wxid_xxxxxxxxxxxxx
✅ 13800138000
"""

        # 微信账号可以是微信号或手机号
        if len(wechat_account) < 5 or len(wechat_account) > 50:
            return """
【收款方式验证失败】❌

❌ 微信账号长度不正确

要求：5-50个字符

请检查您的微信号或微信手机号是否正确。
"""

        return f"""
【微信支付验证成功】✅

✅ 微信账号格式正确

📋 验证结果：
- 收款方式：微信支付
- 微信账号：{wechat_account}

💡 提示：
- 您还可以上传微信收款二维码图片
- 二维码图片上传后会自动生成URL
"""

    elif payment_method == 'alipay':
        if not alipay_account:
            return """
【收款方式验证失败】❌

❌ 支付宝账号不能为空

请填写您的支付宝账号、支付宝邮箱或支付宝手机号。

示例：
✅ 13800138000
✅ user@example.com
✅ user_alipay
"""

        # 支付宝账号可以是手机号、邮箱或账号
        if len(alipay_account) < 5 or len(alipay_account) > 100:
            return """
【收款方式验证失败】❌

❌ 支付宝账号长度不正确

要求：5-100个字符

请检查您的支付宝账号是否正确。
"""

        return f"""
【支付宝验证成功】✅

✅ 支付宝账号格式正确

📋 验证结果：
- 收款方式：支付宝
- 支付宝账号：{alipay_account}

💡 提示：
- 您还可以上传支付宝收款二维码图片
- 二维码图片上传后会自动生成URL
"""

    elif payment_method == 'bank':
        if not bank_card_number:
            return """
【收款方式验证失败】❌

❌ 银行卡号不能为空

请填写您的银行卡号。

示例：
✅ 6222021234567890123
✅ 6216611234567890123
"""

        # 验证银行卡号（16-19位数字）
        if not bank_card_number.isdigit():
            return """
【收款方式验证失败】❌

❌ 银行卡号格式不正确

要求：银行卡号必须为数字

请检查您的银行卡号是否正确。
"""

        if len(bank_card_number) < 16 or len(bank_card_number) > 19:
            return """
【收款方式验证失败】❌

❌ 银行卡号长度不正确

要求：16-19位数字

请检查您的银行卡号是否正确。
"""

        if not bank_name:
            return """
【收款方式验证失败】❌

❌ 开户行名称不能为空

请填写您的开户行名称。

示例：
✅ 中国工商银行北京分行
✅ 中国建设银行上海分行
✅ 招商银行深圳分行
"""

        if len(bank_name) < 2 or len(bank_name) > 100:
            return """
【收款方式验证失败】❌

❌ 开户行名称长度不正确

要求：2-100个字符

请检查您的开户行名称是否正确。
"""

        if not bank_account_name:
            return """
【收款方式验证失败】❌

❌ 银行账户姓名不能为空

请填写您的银行账户姓名（必须与实名认证姓名一致）。

示例：
✅ 张三
✅ 李四
"""

        if len(bank_account_name) < 2 or len(bank_account_name) > 50:
            return """
【收款方式验证失败】❌

❌ 银行账户姓名长度不正确

要求：2-50个字符

请检查您的银行账户姓名是否正确。
"""

        # 掩码显示银行卡号
        masked_card = bank_card_number[:4] + ' **** **** ' + bank_card_number[-4:]

        return f"""
【银行卡验证成功】✅

✅ 银行卡信息格式正确

📋 验证结果：
- 收款方式：银行卡
- 银行卡号：{masked_card}
- 开户行：{bank_name}
- 账户姓名：{bank_account_name}

💡 提示：
- 银行卡号将加密存储
- 银行卡号将掩码显示
- 资金发放到账时间：1-3个工作日
"""

    return """【收款方式验证失败】❌

❌ 未知的错误

请稍后重试或联系客服。"""


@tool
def submit_payment_method(
    payment_method: str,
    preferred_method: str = None,
    wechat_account: str = None,
    wechat_qrcode: str = None,
    alipay_account: str = None,
    alipay_qrcode: str = None,
    bank_card_number: str = None,
    bank_name: str = None,
    bank_account_name: str = None,
    runtime: ToolRuntime = None
) -> str:
    """提交收款方式信息

    用户设置或更新收款方式信息。

    Args:
        payment_method: 收款方式类型（wechat/alipay/bank）
        preferred_method: 首选收款方式（wechat/alipay/bank，可选）
        wechat_account: 微信账号（微信支付时必填）
        wechat_qrcode: 微信收款二维码URL（可选）
        alipay_account: 支付宝账号（支付宝时必填）
        alipay_qrcode: 支付宝收款二维码URL（可选）
        bank_card_number: 银行卡号（银行卡时必填）
        bank_name: 开户行名称（银行卡时必填）
        bank_account_name: 银行账户姓名（银行卡时必填）

    Returns:
        str: 收款方式设置结果
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users, AuditLogs

    # 获取数据库会话
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
【收款方式设置失败】

❌ 无法识别当前登录用户

请确保您已通过扣子平台正确登录。
"""

        # 查询用户
        user = db.query(Users).filter(Users.coze_id == coze_id).first()

        if not user:
            return """
【收款方式设置失败】

❌ 用户不存在

请先登录后再设置收款方式。
"""

        # 检查是否已实名认证
        if not user.is_registered:
            return """
【收款方式设置失败】

❌ 您需要先完成实名认证才能设置收款方式

请先完成实名认证，然后再设置收款方式。

实名认证可以：
1. 确保资金发放到正确的人
2. 防止洗钱和非法资金流动
3. 符合国家金融监管要求
"""

        # 验证首选收款方式
        if preferred_method and preferred_method not in ['wechat', 'alipay', 'bank']:
            return """
【收款方式设置失败】

❌ 首选收款方式类型不正确

要求：首选收款方式必须是以下类型之一：
- wechat：微信支付
- alipay：支付宝
- bank：银行卡

请选择正确的首选收款方式类型。
"""

        # 根据收款方式更新信息
        update_fields = []
        message_parts = []

        if payment_method == 'wechat':
            if not wechat_account:
                return """
【收款方式设置失败】

❌ 微信账号不能为空

请填写您的微信号或微信手机号。
"""

            user.wechat_account = wechat_account
            update_fields.append("wechat_account")
            message_parts.append(f"微信账号：{wechat_account}")

            if wechat_qrcode:
                user.wechat_qrcode = wechat_qrcode
                update_fields.append("wechat_qrcode")
                message_parts.append("微信二维码：已设置 ✅")

        elif payment_method == 'alipay':
            if not alipay_account:
                return """
【收款方式设置失败】

❌ 支付宝账号不能为空

请填写您的支付宝账号。
"""

            user.alipay_account = alipay_account
            update_fields.append("alipay_account")
            message_parts.append(f"支付宝账号：{alipay_account}")

            if alipay_qrcode:
                user.alipay_qrcode = alipay_qrcode
                update_fields.append("alipay_qrcode")
                message_parts.append("支付宝二维码：已设置 ✅")

        elif payment_method == 'bank':
            if not bank_card_number or not bank_name or not bank_account_name:
                return """
【收款方式设置失败】

❌ 银行卡信息不完整

请填写完整的银行卡信息：
- 银行卡号（必填）
- 开户行名称（必填）
- 银行账户姓名（必填）
"""

            # 验证银行卡号格式
            if not bank_card_number.isdigit():
                return """
【收款方式设置失败】

❌ 银行卡号格式不正确

要求：银行卡号必须为数字（16-19位）
"""

            if len(bank_card_number) < 16 or len(bank_card_number) > 19:
                return """
【收款方式设置失败】

❌ 银行卡号长度不正确

要求：16-19位数字
"""

            # 验证银行账户姓名是否与实名认证姓名一致
            if bank_account_name != user.real_name:
                return f"""
【收款方式设置失败】

❌ 银行账户姓名与实名认证姓名不一致

实名认证姓名：{user.real_name}
银行账户姓名：{bank_account_name}

请确保银行账户姓名与实名认证姓名一致。
"""

            user.bank_card_number = bank_card_number
            user.bank_name = bank_name
            user.bank_account_name = bank_account_name
            update_fields.extend(["bank_card_number", "bank_name", "bank_account_name"])

            # 掩码显示银行卡号
            masked_card = bank_card_number[:4] + ' **** **** ' + bank_card_number[-4:]
            message_parts.append(f"银行卡号：{masked_card}")
            message_parts.append(f"开户行：{bank_name}")
            message_parts.append(f"账户姓名：{bank_account_name}")

        # 设置首选收款方式
        if preferred_method:
            user.preferred_payment_method = preferred_method
            update_fields.append("preferred_payment_method")

            # 首选收款方式映射
            method_map = {
                'wechat': '微信支付',
                'alipay': '支付宝',
                'bank': '银行卡'
            }
            message_parts.append(f"首选收款方式：{method_map.get(preferred_method, preferred_method)}")

        # 更新用户信息
        db.add(user)

        # 记录审计日志
        audit_log = AuditLogs(
            user_id=user.id,
            action='update_payment_method',
            status='success',
            resource_type='user',
            resource_id=user.id,
            description=f'用户更新收款方式：{", ".join(update_fields)}'
        )
        db.add(audit_log)

        # 提交事务
        db.commit()
        db.refresh(user)

        # 生成成功消息
        method_map = {
            'wechat': '微信支付',
            'alipay': '支付宝',
            'bank': '银行卡'
        }

        success_message = f"""
【收款方式设置成功】✅

恭喜您，{user.real_name}！您的收款方式已成功设置。

📋 您的收款信息：
- 收款方式：{method_map.get(payment_method, payment_method)}
{chr(10).join(message_parts)}

🎉 您现在可以：
- 将贡献值兑换为人民币
- 接收项目分红收益
- 参与推荐人分红计划

💡 提示：
- 您可以随时修改收款方式
- 修改后立即生效
- 资金发放时会使用您的首选收款方式
- 建议设置多种收款方式以确保资金及时到账

🔒 安全提醒：
- 银行卡号已加密存储
- 银行卡号将掩码显示
- 收款信息仅用于资金发放

📞 如有疑问：
- 超级管理员：xufeng@meiyueart.cn
- 客服热线：400-XXX-XXXX

感谢您的配合！期待您在灵值生态园获得丰厚收益！🌟
"""

        return success_message

    except Exception as e:
        db.rollback()
        return f"""
【收款方式设置失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()


@tool
def get_user_payment_method(
    runtime: ToolRuntime = None
) -> str:
    """获取用户的收款方式信息

    返回当前登录用户的收款方式信息。

    Returns:
        str: 用户收款方式信息
    """
    from coze_coding_dev_sdk.database import get_session
    from storage.database.shared.model import Users

    # 获取数据库会话
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
【获取收款方式信息失败】

❌ 无法识别当前登录用户

请确保您已通过扣子平台正确登录。
"""

        # 查询用户
        user = db.query(Users).filter(Users.coze_id == coze_id).first()

        if not user:
            return """
【获取收款方式信息失败】

❌ 用户不存在

请先登录后再查看收款方式信息。
"""

        # 检查是否已实名认证
        if not user.is_registered:
            return """
【收款方式信息】

❌ 您尚未完成实名认证

请先完成实名认证，然后再设置收款方式。
"""

        # 构建收款方式信息
        info_parts = []

        # 微信支付
        if user.wechat_account:
            wechat_info = f"""
### 📱 微信支付
- 微信账号：{user.wechat_account}
- 收款二维码：{'已设置 ✅' if user.wechat_qrcode else '未设置'}
"""
            info_parts.append(wechat_info)

        # 支付宝
        if user.alipay_account:
            alipay_info = f"""
### 💙 支付宝
- 支付宝账号：{user.alipay_account}
- 收款二维码：{'已设置 ✅' if user.alipay_qrcode else '未设置'}
"""
            info_parts.append(alipay_info)

        # 银行卡
        if user.bank_card_number:
            # 掩码显示银行卡号
            masked_card = user.bank_card_number[:4] + ' **** **** ' + user.bank_card_number[-4:]
            bank_info = f"""
### 💳 银行卡
- 银行卡号：{masked_card}
- 开户行：{user.bank_name}
- 账户姓名：{user.bank_account_name}
"""
            info_parts.append(bank_info)

        # 首选收款方式
        method_map = {
            'wechat': '微信支付',
            'alipay': '支付宝',
            'bank': '银行卡'
        }
        preferred_method = method_map.get(user.preferred_payment_method, user.preferred_payment_method)

        if info_parts:
            return f"""
【您的收款方式信息】

用户：{user.real_name}
首选收款方式：{preferred_method}

{''.join(info_parts)}

💡 提示：
- 您可以随时修改收款方式
- 建议设置多种收款方式以确保资金及时到账
"""
        else:
            return f"""
【您的收款方式信息】

用户：{user.real_name}

❌ 您尚未设置任何收款方式

请设置收款方式后才能将贡献值兑换为人民币。

您可以设置：
1. 微信支付
2. 支付宝
3. 银行卡

建议设置多种收款方式以确保资金及时到账。
"""

    except Exception as e:
        return f"""
【获取收款方式信息失败】

❌ 系统错误：{str(e)}

请稍后重试或联系管理员。
"""

    finally:
        db.close()
