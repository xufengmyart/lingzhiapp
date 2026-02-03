"""
灵值智能体 - 情绪识别与分析工具

版本：v1.0
创建日期：2025年1月15日
功能：
- 情绪识别（6种基础情绪 + 复杂情绪）
- 情绪记录（保存到用户档案）
- 情绪统计分析（情绪分布、趋势、关键词）
- 情绪日记管理
"""

from typing import Optional
import json
from datetime import datetime, timedelta
from langchain.tools import tool

# 情绪类型定义
EMOTION_TYPES = {
    'happy': {'name': '开心', 'icon': '😊', 'color': '#FFD700'},
    'sad': {'name': '悲伤', 'icon': '😢', 'color': '#87CEEB'},
    'angry': {'name': '愤怒', 'icon': '😠', 'color': '#FF6347'},
    'anxious': {'name': '焦虑', 'icon': '😰', 'color': '#DDA0DD'},
    'surprised': {'name': '惊讶', 'icon': '😲', 'color': '#FFA500'},
    'calm': {'name': '平静', 'icon': '😌', 'color': '#98FB98'}
}

# 模拟用户情绪数据库
_user_emotion_records = {}
_user_emotion_diaries = {}


# 内部函数：记录情绪（供其他工具调用）
def _record_emotion_internal(user_id: str, emotion: str, intensity: float, context: Optional[str] = None):
    """内部函数：记录情绪"""
    if user_id not in _user_emotion_records:
        _user_emotion_records[user_id] = []
    record = {
        "emotion": emotion,
        "emotion_name": EMOTION_TYPES.get(emotion, {}).get('name', emotion),
        "intensity": intensity,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }
    _user_emotion_records[user_id].append(record)
    return {
        "success": True,
        "message": "情绪记录成功",
        "emotion": EMOTION_TYPES.get(emotion, {}).get('name', emotion),
        "total_records": len(_user_emotion_records[user_id])
    }


@tool
def detect_emotion(text: str, user_id: Optional[str] = None) -> str:
    """识别用户文本中的情绪"""
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
    """记录用户情绪到档案"""
    if user_id not in _user_emotion_records:
        _user_emotion_records[user_id] = []
    record = {
        "emotion": emotion,
        "emotion_name": EMOTION_TYPES.get(emotion, {}).get('name', emotion),
        "intensity": intensity,
        "context": context,
        "timestamp": datetime.now().isoformat()
    }
    _user_emotion_records[user_id].append(record)
    result = {
        "success": True,
        "message": "情绪记录成功",
        "emotion": EMOTION_TYPES.get(emotion, {}).get('name', emotion),
        "total_records": len(_user_emotion_records[user_id])
    }
    return json.dumps(result, ensure_ascii=False)


@tool
def get_emotion_statistics(user_id: str, period: str = "week") -> str:
    """获取用户情绪统计分析"""
    if user_id not in _user_emotion_records:
        return json.dumps({"message": "暂无情绪记录", "suggestion": "开始记录你的情绪吧 💚"}, ensure_ascii=False)
    
    records = _user_emotion_records[user_id]
    now = datetime.now()
    if period == "day":
        start_time = now - timedelta(days=1)
    elif period == "month":
        start_time = now - timedelta(days=30)
    else:
        start_time = now - timedelta(weeks=1)
    
    filtered_records = [r for r in records if datetime.fromisoformat(r['timestamp']) >= start_time]
    if not filtered_records:
        return json.dumps({"message": f"最近{period}暂无情绪记录"}, ensure_ascii=False)
    
    emotion_distribution = {}
    for r in filtered_records:
        e = r['emotion']
        emotion_distribution[e] = emotion_distribution.get(e, 0) + 1
    
    result = {
        "period": period,
        "total_records": len(filtered_records),
        "emotion_distribution": emotion_distribution,
        "emotion_distribution_with_names": {
            EMOTION_TYPES.get(k, {}).get('name', k): v for k, v in emotion_distribution.items()
        }
    }
    return json.dumps(result, ensure_ascii=False)


@tool
def create_emotion_diary(user_id: str, content: str, emotion: str, intensity: float, tags: Optional[list] = None) -> str:
    """创建情绪日记"""
    if user_id not in _user_emotion_diaries:
        _user_emotion_diaries[user_id] = []
    diary = {
        "content": content,
        "emotion": emotion,
        "emotion_name": EMOTION_TYPES.get(emotion, {}).get('name', emotion),
        "intensity": intensity,
        "tags": tags or [],
        "timestamp": datetime.now().isoformat()
    }
    _user_emotion_diaries[user_id].append(diary)
    # 使用内部函数记录情绪
    _record_emotion_internal(user_id, emotion, intensity, content)
    return json.dumps({"success": True, "message": "情绪日记创建成功", "total_diaries": len(_user_emotion_diaries[user_id])}, ensure_ascii=False)


@tool  
def get_emotion_diaries(user_id: str, limit: int = 10) -> str:
    """获取用户的情绪日记列表"""
    if user_id not in _user_emotion_diaries:
        return json.dumps({"message": "暂无情绪日记"}, ensure_ascii=False)
    diaries = sorted(_user_emotion_diaries[user_id], key=lambda x: x['timestamp'], reverse=True)[:limit]
    return json.dumps({"total_diaries": len(_user_emotion_diaries[user_id]), "diaries": diaries}, ensure_ascii=False)


@tool
def analyze_emotion_pattern(user_id: str) -> str:
    """分析用户的情绪模式"""
    if user_id not in _user_emotion_records or len(_user_emotion_records[user_id]) < 3:
        return json.dumps({"message": "情绪记录不足，无法分析模式"}, ensure_ascii=False)
    
    records = _user_emotion_records[user_id]
    emotions = [r['emotion'] for r in records]
    intensities = [r['intensity'] for r in records]
    from collections import Counter
    most_common = Counter(emotions).most_common(1)[0]
    
    return json.dumps({
        "total_records": len(records),
        "most_common_emotion": most_common[0],
        "most_common_emotion_name": EMOTION_TYPES.get(most_common[0], {}).get('name'),
        "average_intensity": round(sum(intensities) / len(intensities), 2)
    }, ensure_ascii=False)
