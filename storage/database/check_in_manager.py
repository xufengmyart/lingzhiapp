"""
Check In Manager
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, session
from datetime import datetime, date

Base = declarative_base()

class CheckIn(Base):
    """签到记录表"""
    __tablename__ = 'checkin_records'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    check_in_date = Column(DateTime, nullable=False, default=datetime.now)
    lingzhi_earned = Column(Integer, default=0)  # 获取的灵值
    created_at = Column(DateTime, default=datetime.now)

class CheckInManager:
    """签到管理器"""
    
    def has_checked_in_today(self, db_session: session, user_id: int) -> bool:
        """检查用户今天是否已签到"""
        today = date.today()
        start_of_day = datetime.combine(today, datetime.min.time())
        end_of_day = datetime.combine(today, datetime.max.time())
        
        result = db_session.query(CheckIn).filter(
            CheckIn.user_id == user_id,
            CheckIn.check_in_date >= start_of_day,
            CheckIn.check_in_date <= end_of_day
        ).first()
        
        return result is not None
