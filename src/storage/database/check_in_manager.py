"""
签到管理模块
"""
from typing import Optional, List
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from datetime import datetime, date, timedelta
import pytz

from storage.database.shared.model import Users, CheckIns, AuditLogs


class CheckInsCreate(BaseModel):
    """签到请求"""
    user_id: int


class CheckInManager:
    """签到管理器"""

    def __init__(self):
        # 设置时区为东八区（北京时间）
        self.timezone = pytz.timezone('Asia/Shanghai')
        # 每日签到奖励灵值
        self.daily_reward = 10

    def get_today_start(self) -> datetime:
        """获取今天开始时间（00:00:00）"""
        now = datetime.now(self.timezone)
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        return today_start

    def get_today_end(self) -> datetime:
        """获取今天结束时间（23:59:59）"""
        now = datetime.now(self.timezone)
        today_end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return today_end

    def has_checked_in_today(self, db: Session, user_id: int) -> bool:
        """检查用户今天是否已签到

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            bool: 今天是否已签到
        """
        today_start = self.get_today_start()
        today_end = self.get_today_end()

        # 查询今天是否有签到记录
        check_in = db.query(CheckIns).filter(
            and_(
                CheckIns.user_id == user_id,
                CheckIns.created_at >= today_start,
                CheckIns.created_at <= today_end
            )
        ).first()

        return check_in is not None

    def check_in(self, db: Session, user_id: int) -> tuple[bool, str, Optional[CheckIns]]:
        """用户签到

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            tuple: (是否成功, 消息, 签到记录)
        """
        # 检查用户是否存在
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return False, f"用户不存在（ID: {user_id}）", None

        # 检查用户状态
        if user.status != 'active':
            return False, f"用户状态异常（{user.status}），无法签到", None

        # 检查今天是否已签到
        if self.has_checked_in_today(db, user_id):
            return False, f"您今天已经签到过了，明天再来吧！", None

        # 创建签到记录
        check_in = CheckIns(
            user_id=user_id,
            check_in_date=datetime.now(self.timezone),
            lingzhi_reward=self.daily_reward,
            created_at=datetime.now(self.timezone)
        )

        db.add(check_in)
        
        try:
            db.commit()
            db.refresh(check_in)

            # 记录审计日志
            audit_log = AuditLogs(
                user_id=user_id,
                action='check_in',
                resource_type='check_in',
                resource_id=check_in.id,
                description=f'用户签到成功，获得{self.daily_reward}灵值',
                status='success',
                created_at=datetime.now(self.timezone)
            )
            db.add(audit_log)
            db.commit()

            return True, f"签到成功！获得{self.daily_reward}灵值", check_in

        except Exception as e:
            db.rollback()
            return False, f"签到失败：{str(e)}", None

    def get_user_check_in_history(self, db: Session, user_id: int, days: int = 30) -> List[CheckIns]:
        """获取用户签到历史记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数（默认30天）

        Returns:
            List[CheckIns]: 签到记录列表
        """
        # 计算查询起始时间
        start_date = datetime.now(self.timezone) - timedelta(days=days)

        # 查询签到记录
        check_ins = db.query(CheckIns).filter(
            and_(
                CheckIns.user_id == user_id,
                CheckIns.created_at >= start_date
            )
        ).order_by(CheckIns.created_at.desc()).all()

        return check_ins

    def get_user_check_in_count(self, db: Session, user_id: int, days: int = 30) -> int:
        """获取用户签到次数

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数（默认30天）

        Returns:
            int: 签到次数
        """
        return len(self.get_user_check_in_history(db, user_id, days))

    def get_user_total_lingzhi_from_check_in(self, db: Session, user_id: int) -> int:
        """获取用户签到获得的灵值总数

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            int: 灵值总数
        """
        check_ins = db.query(CheckIns).filter(CheckIns.user_id == user_id).all()
        total = sum(check_in.lingzhi_reward for check_in in check_ins)
        return total

    def get_today_check_in_users(self, db: Session) -> List[Users]:
        """获取今天已签到的用户列表

        Args:
            db: 数据库会话

        Returns:
            List[Users]: 已签到用户列表
        """
        today_start = self.get_today_start()
        today_end = self.get_today_end()

        # 查询今天的签到记录
        check_ins = db.query(CheckIns).filter(
            and_(
                CheckIns.created_at >= today_start,
                CheckIns.created_at <= today_end
            )
        ).all()

        # 获取用户列表
        user_ids = [check_in.user_id for check_in in check_ins]
        users = db.query(Users).filter(Users.id.in_(user_ids)).all()

        return users

    def get_today_check_in_count(self, db: Session) -> int:
        """获取今天签到总人数

        Args:
            db: 数据库会话

        Returns:
            int: 签到总人数
        """
        return len(self.get_today_check_in_users(db))

    def format_check_in_history(self, db: Session, user_id: int, days: int = 30) -> str:
        """格式化签到历史记录

        Args:
            db: 数据库会话
            user_id: 用户ID
            days: 查询天数（默认30天）

        Returns:
            str: 格式化的签到历史
        """
        check_ins = self.get_user_check_in_history(db, user_id, days)
        total_count = self.get_user_check_in_count(db, user_id)
        total_lingzhi = self.get_user_total_lingzhi_from_check_in(db, user_id)

        result = f"""
【签到历史记录】

📊 统计信息：
- 累计签到：{total_count}次
- 累计获得灵值：{total_lingzhi}灵值
- 查询范围：最近{days}天

📅 签到记录：
"""

        if not check_ins:
            result += "暂无签到记录"
        else:
            for check_in in check_ins:
                date_str = check_in.created_at.strftime('%Y-%m-%d %H:%M:%S')
                result += f"- {date_str}：获得{check_in.lingzhi_reward}灵值\n"

        # 检查今天是否已签到
        if self.has_checked_in_today(db, user_id):
            result += "\n✅ 今天已签到"
        else:
            result += "\n❌ 今天未签到"

        return result
