"""
灵值智能体 - 情绪识别与分析工具（数据库持久化版）

版本：v2.0
创建日期：2025年1月15日
更新日期：2025年1月15日
功能：
- 情绪识别（6种基础情绪 + 复杂情绪）
- 情绪记录（保存到数据库）
- 情绪统计分析（情绪分布、趋势、关键词）
- 情绪日记管理
"""

from typing import Optional
import json
from datetime import datetime, timedelta
from langchain.tools import tool

# 导入数据库相关模块
from coze_coding_dev_sdk.database import get_session
from storage.database.emotion_manager import EmotionManager, EmotionRecordCreate, EmotionDiaryCreate

# 情绪类型定义
EMOTION_TYPES = {
    'happy': {'name': '开心', 'icon': '😊', 'color': '#FFD700'},
    'sad': {'name': '悲伤', 'icon': '😢', 'color': '#87CEEB'},
    'angry': {'name': '愤怒', 'icon': '😠', 'color': '#FF6347'},
    'anxious': {'name': '焦虑', 'icon': '😰', 'color': '#DDA0DD'},
    'surprised': {'name': '惊讶', 'icon': '😲', 'color': '#FFA500'},
    'calm': {'name': '平静', 'icon': '😌', 'color': '#98FB98'}
}


@tool
def detect_emotion(text: str, user_id: Optional[str] = None) -> str:
    """
    识别用户文本中的情绪

    Args:
        text: 用户输入的文本
        user_id: 用户ID（可选）

    Returns:
        情绪识别结果的JSON字符串
    """
    emotion_scores = {
        'happy': 0.0, 'sad': 0.0, 'angry': 0.0,
        'anxious': 0.0, 'surprised': 0.0, 'calm': 0.0
    }

    happy_keywords = ['开心', '高兴', '快乐', '兴奋', '幸福', '棒', '赞', '哈哈', '笑']
    sad_keywords = ['难过', '悲伤', '伤心', '哭', '丧', '难受', '痛苦', '失落', '沮丧']
    angry_keywords = ['生气', '愤怒', '讨厌', '烦', '恨', '气死', '烦死']
    anxious_keywords = ['担心', '焦虑', '害怕', '紧张', '不安', '慌', '怕']
    surprised_keywords = ['惊讶', '哇', '天啊', '什么', '不敢相信', '意外']
    calm_keywords = ['平静', '安静', '舒服', '放松', '宁静']

    text_lower = text.lower()
    for kw in happy_keywords:
        if kw in text_lower: emotion_scores['happy'] += 0.2
    for kw in sad_keywords:
        if kw in text_lower: emotion_scores['sad'] += 0.2
    for kw in angry_keywords:
        if kw in text_lower: emotion_scores['angry'] += 0.2
    for kw in anxious_keywords:
        if kw in text_lower: emotion_scores['anxious'] += 0.2
    for kw in surprised_keywords:
        if kw in text_lower: emotion_scores['surprised'] += 0.2
    for kw in calm_keywords:
        if kw in text_lower: emotion_scores['calm'] += 0.2

    max_score = max(emotion_scores.values())
    primary_emotion = [k for k, v in emotion_scores.items() if v == max_score][0]
    total_score = sum(emotion_scores.values())
    confidence = (max_score / total_score) if total_score > 0 else 0.5
    intensity = min(1.0, max_score * 2)

    result = {
        "primary_emotion": {
            "type": primary_emotion,
            "name": EMOTION_TYPES[primary_emotion]['name'],
            "confidence": round(confidence, 2),
            "intensity": round(intensity, 2)
        },
        "all_emotions": emotion_scores,
        "timestamp": datetime.now().isoformat()
    }
    return json.dumps(result, ensure_ascii=False)


@tool
def record_emotion(user_id: str, emotion: str, intensity: float, context: Optional[str] = None) -> str:
    """
    记录用户情绪到数据库

    Args:
        user_id: 用户ID（字符串或整数）
        emotion: 情绪类型
        intensity: 情绪强度（0.0-1.0）
        context: 情绪上下文描述

    Returns:
        记录结果的JSON字符串
    """
    db = get_session()
    try:
        mgr = EmotionManager()

        # 转换user_id为整数
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            # 如果无法转换为整数，使用默认用户ID（1）
            user_id_int = 1

        # 创建情绪记录
        record = EmotionRecordCreate(
            user_id=user_id_int,
            emotion=emotion,
            emotion_name=EMOTION_TYPES.get(emotion, {}).get('name', emotion),
            intensity=float(intensity),
            context=context
        )

        result = mgr.create_emotion_record(db, record)
        total_count = mgr.get_user_emotion_count(db, user_id_int)

        return json.dumps({
            "success": True,
            "message": "情绪记录成功",
            "emotion": result.emotion_name,
            "total_records": total_count
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"情绪记录失败: {str(e)}"
        }, ensure_ascii=False)
    finally:
        db.close()


@tool
def get_emotion_statistics(user_id: str, period: str = "week") -> str:
    """
    获取用户情绪统计分析

    Args:
        user_id: 用户ID（字符串或整数）
        period: 统计周期：day/week/month

    Returns:
        统计结果的JSON字符串
    """
    db = get_session()
    try:
        mgr = EmotionManager()

        # 转换user_id为整数
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            user_id_int = 1

        result = mgr.get_emotion_statistics(db, user_id_int, period)

        # 添加中文名称映射
        result["emotion_distribution_with_names"] = {
            EMOTION_TYPES.get(k, {}).get('name', k): v
            for k, v in result.get("emotion_distribution", {}).items()
        }

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"获取统计失败: {str(e)}"
        }, ensure_ascii=False)
    finally:
        db.close()


@tool
def create_emotion_diary(user_id: str, content: str, emotion: str, intensity: float, tags: Optional[list] = None) -> str:
    """
    创建情绪日记

    Args:
        user_id: 用户ID（字符串或整数）
        content: 日记内容
        emotion: 情绪类型
        intensity: 情绪强度（0.0-1.0）
        tags: 标签列表

    Returns:
        创建结果的JSON字符串
    """
    db = get_session()
    try:
        mgr = EmotionManager()

        # 转换user_id为整数
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            user_id_int = 1

        # 创建情绪日记
        diary = EmotionDiaryCreate(
            user_id=user_id_int,
            content=content,
            emotion=emotion,
            emotion_name=EMOTION_TYPES.get(emotion, {}).get('name', emotion),
            intensity=float(intensity),
            tags=tags or []
        )

        result = mgr.create_emotion_diary(db, diary)

        # 同时记录情绪
        record = EmotionRecordCreate(
            user_id=user_id_int,
            emotion=emotion,
            emotion_name=EMOTION_TYPES.get(emotion, {}).get('name', emotion),
            intensity=float(intensity),
            context=content
        )
        mgr.create_emotion_record(db, record)

        total_diaries = mgr.get_user_diary_count(db, user_id_int)

        return json.dumps({
            "success": True,
            "message": "情绪日记创建成功",
            "total_diaries": total_diaries
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"创建日记失败: {str(e)}"
        }, ensure_ascii=False)
    finally:
        db.close()


@tool
def get_emotion_diaries(user_id: str, limit: int = 10) -> str:
    """
    获取用户的情绪日记列表

    Args:
        user_id: 用户ID（字符串或整数）
        limit: 返回数量限制

    Returns:
        日记列表的JSON字符串
    """
    db = get_session()
    try:
        mgr = EmotionManager()

        # 转换user_id为整数
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            user_id_int = 1

        result = mgr.get_emotion_diaries(db, user_id_int, limit=limit)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"获取日记失败: {str(e)}"
        }, ensure_ascii=False)
    finally:
        db.close()


@tool
def analyze_emotion_pattern(user_id: str) -> str:
    """
    分析用户的情绪模式

    Args:
        user_id: 用户ID（字符串或整数）

    Returns:
        情绪模式分析结果的JSON字符串
    """
    db = get_session()
    try:
        mgr = EmotionManager()

        # 转换user_id为整数
        try:
            user_id_int = int(user_id)
        except (ValueError, TypeError):
            user_id_int = 1

        result = mgr.analyze_emotion_pattern(db, user_id_int)

        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "message": f"分析失败: {str(e)}"
        }, ensure_ascii=False)
    finally:
        db.close()
