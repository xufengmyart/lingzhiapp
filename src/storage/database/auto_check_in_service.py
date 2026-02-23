"""
自动签到服务

用户登录时自动触发签到功能
"""

from typing import Optional
from coze_coding_dev_sdk.database import get_session
from storage.database.check_in_manager import CheckInManager
from storage.database.shared.model import Users, AuditLogs
from datetime import datetime
import pytz


class AutoCheckInService:
    """自动签到服务"""

    def __init__(self):
        self.check_in_manager = CheckInManager()
        self.timezone = pytz.timezone('Asia/Shanghai')

    def auto_check_in_on_login(self, user_id: int) -> dict:
        """用户登录时自动签到

        Args:
            user_id: 用户ID

        Returns:
            dict: 签到结果
                - success: 是否成功
                - message: 消息
                - check_in: 签到记录（如果签到成功）
                - already_checked: 是否已经签到
        """
        # 获取数据库会话
        db = get_session()

        try:
            # 检查用户是否存在
            user = db.query(Users).filter(Users.id == user_id).first()
            if not user:
                return {
                    'success': False,
                    'message': '用户不存在',
                    'check_in': None,
                    'already_checked': False
                }

            # 检查用户状态
            if user.status != 'active':
                return {
                    'success': False,
                    'message': f'用户状态异常（{user.status}），无法签到',
                    'check_in': None,
                    'already_checked': False
                }

            # 检查今天是否已签到
            has_checked_in = self.check_in_manager.has_checked_in_today(db, user_id)

            if has_checked_in:
                # 今天已经签到过了
                return {
                    'success': True,
                    'message': '今天已经签到过了',
                    'check_in': None,
                    'already_checked': True
                }
            else:
                # 今天还没签到，自动签到
                success, message, check_in = self.check_in_manager.check_in(db, user_id)

                if success:
                    # 记录自动签到审计日志
                    audit_log = AuditLogs(
                        user_id=user_id,
                        action='auto_check_in',
                        resource_type='check_in',
                        resource_id=check_in.id,
                        description=f'用户登录自动签到成功，获得{check_in.lingzhi_reward}灵值',
                        status='success',
                        created_at=datetime.now(self.timezone)
                    )
                    db.add(audit_log)
                    db.commit()

                    return {
                        'success': True,
                        'message': f'登录自动签到成功！获得{check_in.lingzhi_reward}灵值',
                        'check_in': check_in,
                        'already_checked': False
                    }
                else:
                    return {
                        'success': False,
                        'message': f'自动签到失败：{message}',
                        'check_in': None,
                        'already_checked': False
                    }

        except Exception as e:
            return {
                'success': False,
                'message': f'自动签到过程中发生错误：{str(e)}',
                'check_in': None,
                'already_checked': False
            }
        finally:
            db.close()

    def format_auto_check_in_message(self, user_id: int, result: dict) -> str:
        """格式化自动签到消息

        Args:
            user_id: 用户ID
            result: 签到结果

        Returns:
            str: 格式化的消息
        """
        from coze_coding_dev_sdk.database import get_session

        if not result['success']:
            # 签到失败
            return f"""
【自动签到】⚠️

{result['message']}
"""

        if result['already_checked']:
            # 今天已经签到过了
            db = get_session()
            try:
                check_ins = self.check_in_manager.get_user_check_in_history(db, user_id, days=1)
                if check_ins:
                    last_check_in = check_ins[0]
                    return f"""
【自动签到】✅

今天已经签到过了

📅 上次签到时间：{last_check_in.created_at.strftime('%H:%M:%S')}
🎁 已获得：{last_check_in.lingzhi_reward}灵值

明天再来签到吧！

💡 签到的好处：
💰 每日签到可获得10灵值（=1元人民币）
📈 累计灵值可参与项目投资，获得高额回报
🎯 连续签到可获得额外奖励
🌟 灵值可兑换为贡献值，享受增值收益
🎁 参与平台活动可获得更多灵值奖励

💎 价值说明：
- 1灵值 = 0.1元人民币（100%确定）
- 100灵值可兑换1贡献值
- 贡献值可锁定增值：1年+20%，2年+50%，3年+100%
- 项目参与合格后可获得600%-12400%的超高回报

🚀 开启您的灵值生态之旅吧！
"""
            finally:
                db.close()

            return """
【自动签到】✅

今天已经签到过了

明天再来签到吧！
"""

        # 自动签到成功
        check_in = result['check_in']
        return f"""
【自动签到】🎉

欢迎回来！系统已为您自动签到成功！

🎁 获得奖励：{check_in.lingzhi_reward}灵值
📅 签到时间：{check_in.created_at.strftime('%Y-%m-%d %H:%M:%S')}

💡 提示：
- 每天登录都会自动签到
- 明天记得再来登录签到哦！

✨ 签到的好处：
💰 每日签到可获得10灵值（=1元人民币）
📈 累计灵值可参与项目投资，获得高额回报
🎯 连续签到可获得额外奖励
🌟 灵值可兑换为贡献值，享受增值收益
🎁 参与平台活动可获得更多灵值奖励

💎 价值说明：
- 1灵值 = 0.1元人民币（100%确定）
- 100灵值可兑换1贡献值
- 贡献值可锁定增值：1年+20%，2年+50%，3年+100%
- 项目参与合格后可获得600%-12400%的超高回报

🚀 开始您的灵值生态之旅吧！
"""


# 全局自动签到服务实例
auto_check_in_service = AutoCheckInService()


def trigger_auto_check_in_on_login(user_id: int) -> dict:
    """触发登录自动签到（全局函数）

    Args:
        user_id: 用户ID

    Returns:
        dict: 签到结果
    """
    return auto_check_in_service.auto_check_in_on_login(user_id)
