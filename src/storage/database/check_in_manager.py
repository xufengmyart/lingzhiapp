"""
签到管理器

管理用户签到相关操作
"""

from typing import List, Tuple, Optional
from datetime import datetime, date
import pytz

from storage.database.shared.model import Users, CheckIns


class CheckInManager:
    """签到管理器"""

    def __init__(self):
        self.timezone = pytz.timezone('Asia/Shanghai')

    def has_checked_in_today(self, db_session, user_id: int) -> bool:
        """检查用户今天是否已签到

        Args:
            db_session: 数据库会话
            user_id: 用户ID

        Returns:
            bool: 是否已签到
        """
        # 获取今天的日期（使用时区）
        today = datetime.now(self.timezone).date()

        # 查询今天是否已有签到记录
        check_in = db_session.query(CheckIns).filter(
            CheckIns.user_id == user_id,
            db_session.query(CheckIns.check_in_date).label('check_date').where(
                CheckIns.user_id == user_id
            ).subquery().c.check_date == today
        ).first()

        # 更简单的查询方式
        check_in = db_session.query(CheckIns).filter(
            CheckIns.user_id == user_id,
            CheckIns.check_in_date >= datetime.now(self.timezone).replace(hour=0, minute=0, second=0, microsecond=0)
        ).first()

        return check_in is not None

    def check_in(self, db_session, user_id: int) -> Tuple[bool, str, Optional[CheckIns]]:
        """执行签到操作

        Args:
            db_session: 数据库会话
            user_id: 用户ID

        Returns:
            Tuple[bool, str, Optional[CheckIns]]: (是否成功, 消息, 签到记录)
        """
        try:
            # 检查用户是否存在
            user = db_session.query(Users).filter(Users.id == user_id).first()
            if not user:
                return False, "用户不存在", None

            # 检查今天是否已签到
            if self.has_checked_in_today(db_session, user_id):
                return False, "今天已经签到过了", None

            # 创建签到记录
            now = datetime.now(self.timezone)
            lingzhi_reward = 10  # 默认获得10灵值

            check_in = CheckIns(
                user_id=user_id,
                check_in_date=now,
                lingzhi_reward=lingzhi_reward,
                created_at=now
            )

            db_session.add(check_in)
            db_session.commit()
            db_session.refresh(check_in)

            return True, "签到成功", check_in

        except Exception as e:
            db_session.rollback()
            return False, f"签到失败: {str(e)}", None

    def get_user_check_in_history(self, db_session, user_id: int, days: int = 30) -> List[CheckIns]:
        """获取用户签到历史

        Args:
            db_session: 数据库会话
            user_id: 用户ID
            days: 查询最近多少天的记录

        Returns:
            List[CheckIns]: 签到记录列表
        """
        # 计算查询起始时间
        start_date = datetime.now(self.timezone) - datetime.timedelta(days=days)

        # 查询签到记录
        check_ins = db_session.query(CheckIns).filter(
            CheckIns.user_id == user_id,
            CheckIns.created_at >= start_date
        ).order_by(CheckIns.created_at.desc()).all()

        return check_ins

    def get_check_in_count(self, db_session, user_id: int) -> int:
        """获取用户累计签到次数

        Args:
            db_session: 数据库会话
            user_id: 用户ID

        Returns:
            int: 累计签到次数
        """
        count = db_session.query(CheckIns).filter(
            CheckIns.user_id == user_id
        ).count()

        return count

    def get_consecutive_check_in_days(self, db_session, user_id: int) -> int:
        """获取用户连续签到天数

        Args:
            db_session: 数据库会话
            user_id: 用户ID

        Returns:
            int: 连续签到天数
        """
        # 获取所有签到记录，按日期倒序
        check_ins = db_session.query(CheckIns).filter(
            CheckIns.user_id == user_id
        ).order_by(CheckIns.check_in_date.desc()).all()

        if not check_ins:
            return 0

        # 计算连续签到天数
        consecutive_days = 0
        expected_date = datetime.now(self.timezone).date()

        for check_in in check_ins:
            check_date = check_in.check_in_date.date()

            if check_date == expected_date:
                consecutive_days += 1
                expected_date -= datetime.timedelta(days=1)
            elif check_date < expected_date:
                # 出现断签
                break
            else:
                # 未来日期，跳过
                continue

        return consecutive_days
