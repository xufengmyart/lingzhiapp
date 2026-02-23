"""
情绪管理器 - 处理情绪记录和日记的数据库操作
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from storage.database.shared.model import EmotionRecords, EmotionDiaries


# --- Pydantic Models for Validation ---

class EmotionRecordCreate(BaseModel):
    """创建情绪记录的请求模型"""
    user_id: int = Field(..., description="用户ID")
    emotion: str = Field(..., description="情绪类型：happy/sad/angry/anxious/surprised/calm")
    emotion_name: str = Field(..., description="情绪名称：开心/悲伤/愤怒/焦虑/惊讶/平静")
    intensity: float = Field(..., ge=0.0, le=1.0, description="情绪强度：0.0-1.0")
    context: Optional[str] = Field(None, description="情绪上下文描述")


class EmotionDiaryCreate(BaseModel):
    """创建情绪日记的请求模型"""
    user_id: int = Field(..., description="用户ID")
    content: str = Field(..., description="日记内容")
    emotion: str = Field(..., description="情绪类型：happy/sad/angry/anxious/surprised/calm")
    emotion_name: str = Field(..., description="情绪名称：开心/悲伤/愤怒/焦虑/惊讶/平静")
    intensity: float = Field(..., ge=0.0, le=1.0, description="情绪强度：0.0-1.0")
    tags: Optional[List[str]] = Field(None, description="标签列表")


class EmotionRecordResponse(BaseModel):
    """情绪记录响应模型"""
    id: int
    user_id: int
    emotion: str
    emotion_name: str
    intensity: float
    context: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class EmotionDiaryResponse(BaseModel):
    """情绪日记响应模型"""
    id: int
    user_id: int
    content: str
    emotion: str
    emotion_name: str
    intensity: float
    tags: Optional[List[str]]
    created_at: datetime

    class Config:
        from_attributes = True


# --- Manager Class ---

class EmotionManager:
    """情绪管理器 - 处理情绪相关的数据库操作"""

    def create_emotion_record(self, db: Session, record_in: EmotionRecordCreate) -> EmotionRecordResponse:
        """
        创建情绪记录

        Args:
            db: 数据库会话
            record_in: 情绪记录创建数据

        Returns:
            创建的情绪记录
        """
        db_record = EmotionRecords(**record_in.model_dump())
        db.add(db_record)
        try:
            db.commit()
            db.refresh(db_record)
            return EmotionRecordResponse.model_validate(db_record)
        except Exception as e:
            db.rollback()
            raise e

    def get_emotion_records(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[EmotionRecordResponse]:
        """
        获取用户的情绪记录列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            情绪记录列表
        """
        records = db.query(EmotionRecords).filter(
            EmotionRecords.user_id == user_id
        ).order_by(EmotionRecords.created_at.desc()).offset(skip).limit(limit).all()
        return [EmotionRecordResponse.model_validate(r) for r in records]

    def get_emotion_statistics(self, db: Session, user_id: int, period: str = "day") -> Dict[str, Any]:
        """
        获取情绪统计数据

        Args:
            db: 数据库会话
            user_id: 用户ID
            period: 统计周期：day/week/month

        Returns:
            情绪统计数据
        """
        # 计算时间范围
        now = datetime.now()
        if period == "day":
            start_time = now - timedelta(days=1)
        elif period == "week":
            start_time = now - timedelta(weeks=1)
        elif period == "month":
            start_time = now - timedelta(days=30)
        else:
            start_time = now - timedelta(days=1)

        # 查询指定时间范围内的记录
        records = db.query(EmotionRecords).filter(
            and_(
                EmotionRecords.user_id == user_id,
                EmotionRecords.created_at >= start_time
            )
        ).all()

        # 统计情绪分布
        emotion_distribution = {}
        emotion_distribution_with_names = {}
        total_records = len(records)

        for record in records:
            emotion = record.emotion
            emotion_name = record.emotion_name

            if emotion not in emotion_distribution:
                emotion_distribution[emotion] = 0
            if emotion_name not in emotion_distribution_with_names:
                emotion_distribution_with_names[emotion_name] = 0

            emotion_distribution[emotion] += 1
            emotion_distribution_with_names[emotion_name] += 1

        return {
            "period": period,
            "total_records": total_records,
            "emotion_distribution": emotion_distribution,
            "emotion_distribution_with_names": emotion_distribution_with_names
        }

    def create_emotion_diary(self, db: Session, diary_in: EmotionDiaryCreate) -> EmotionDiaryResponse:
        """
        创建情绪日记

        Args:
            db: 数据库会话
            diary_in: 情绪日记创建数据

        Returns:
            创建的情绪日记
        """
        db_diary = EmotionDiaries(
            user_id=diary_in.user_id,
            content=diary_in.content,
            emotion=diary_in.emotion,
            emotion_name=diary_in.emotion_name,
            intensity=diary_in.intensity,
            tags=diary_in.tags
        )
        db.add(db_diary)
        try:
            db.commit()
            db.refresh(db_diary)
            return EmotionDiaryResponse.model_validate(db_diary)
        except Exception as e:
            db.rollback()
            raise e

    def get_emotion_diaries(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        获取用户的情绪日记列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过记录数
            limit: 限制记录数

        Returns:
            情绪日记列表
        """
        diaries = db.query(EmotionDiaries).filter(
            EmotionDiaries.user_id == user_id
        ).order_by(EmotionDiaries.created_at.desc()).offset(skip).limit(limit).all()

        return {
            "total_diaries": len(diaries),
            "diaries": [
                {
                    "id": d.id,
                    "content": d.content,
                    "emotion": d.emotion,
                    "emotion_name": d.emotion_name,
                    "intensity": d.intensity,
                    "tags": d.tags,
                    "timestamp": d.created_at.isoformat() if d.created_at else None
                }
                for d in diaries
            ]
        }

    def analyze_emotion_pattern(self, db: Session, user_id: int) -> Dict[str, Any]:
        """
        分析用户的情绪模式

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            情绪模式分析结果
        """
        # 获取所有情绪记录
        records = db.query(EmotionRecords).filter(
            EmotionRecords.user_id == user_id
        ).all()

        if not records:
            return {
                "total_records": 0,
                "most_common_emotion": None,
                "most_common_emotion_name": None,
                "average_intensity": 0.0
            }

        # 统计最常见情绪
        emotion_counts = {}
        total_intensity = 0.0

        for record in records:
            emotion = record.emotion
            if emotion not in emotion_counts:
                emotion_counts[emotion] = 0
            emotion_counts[emotion] += 1
            total_intensity += record.intensity

        # 找到最常见情绪
        most_common_emotion = max(emotion_counts, key=emotion_counts.get)
        most_common_emotion_name = records[0].emotion_name  # 使用第一条记录的情绪名称
        for r in records:
            if r.emotion == most_common_emotion:
                most_common_emotion_name = r.emotion_name
                break

        # 计算平均强度
        average_intensity = total_intensity / len(records)

        return {
            "total_records": len(records),
            "most_common_emotion": most_common_emotion,
            "most_common_emotion_name": most_common_emotion_name,
            "average_intensity": round(average_intensity, 2)
        }

    def get_user_emotion_count(self, db: Session, user_id: int) -> int:
        """
        获取用户的情绪记录总数

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            情绪记录总数
        """
        return db.query(EmotionRecords).filter(
            EmotionRecords.user_id == user_id
        ).count()

    def get_user_diary_count(self, db: Session, user_id: int) -> int:
        """
        获取用户的日记总数

        Args:
            db: 数据库会话
            user_id: 用户ID

        Returns:
            日记总数
        """
        return db.query(EmotionDiaries).filter(
            EmotionDiaries.user_id == user_id
        ).count()
