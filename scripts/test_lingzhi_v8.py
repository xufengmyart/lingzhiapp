#!/usr/bin/env python3
"""
灵值智能体 v8.0 测试脚本

功能：
- 测试情绪识别功能
- 测试情绪记录功能
- 测试情绪统计分析功能
- 测试情绪日记功能
"""

import sys
import json
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.tools.emotion_tools import (
    detect_emotion,
    record_emotion,
    get_emotion_statistics,
    create_emotion_diary,
    get_emotion_diaries,
    analyze_emotion_pattern
)

def print_test(test_name):
    """打印测试标题"""
    print(f"\n{'='*60}")
    print(f"测试: {test_name}")
    print('='*60)

def print_result(result):
    """打印结果"""
    print("\n结果:")
    print(json.dumps(json.loads(result), indent=2, ensure_ascii=False))

def test_emotion_detection():
    """测试情绪识别"""
    print_test("情绪识别")
    
    test_cases = [
        ("今天工作好累，感觉好丧", "sad"),
        ("我升职了！太开心了！", "happy"),
        ("这件事让我很生气！", "angry"),
        ("我有点担心明天的考试", "anxious"),
        ("哇！这太令人惊讶了！", "surprised"),
        ("我现在感觉很平静", "calm")
    ]
    
    for text, expected in test_cases:
        print(f"\n输入: {text}")
        print(f"预期: {expected}")
        result = detect_emotion(text)
        print_result(result)

def test_emotion_recording():
    """测试情绪记录"""
    print_test("情绪记录")
    
    user_id = "test_user_001"
    
    # 记录多个情绪
    emotions = [
        ("happy", 0.8, "今天和朋友出去玩，很开心"),
        ("sad", 0.6, "晚上有点想家"),
        ("calm", 0.7, "现在工作感觉很平静")
    ]
    
    for emotion, intensity, context in emotions:
        result = record_emotion(user_id, emotion, intensity, context)
        print(f"\n记录情绪: {emotion}")
        print_result(result)

def test_emotion_statistics():
    """测试情绪统计"""
    print_test("情绪统计分析")
    
    user_id = "test_user_001"
    
    # 测试不同周期的统计
    for period in ["day", "week", "month"]:
        print(f"\n周期: {period}")
        result = get_emotion_statistics(user_id, period)
        print_result(result)

def test_emotion_diary():
    """测试情绪日记"""
    print_test("情绪日记")
    
    user_id = "test_user_001"
    
    # 创建日记
    diary_content = "今天心情不错，完成了项目的主要部分，感觉很有成就感。"
    result = create_emotion_diary(
        user_id=user_id,
        content=diary_content,
        emotion="happy",
        intensity=0.8,
        tags=["工作", "成就感"]
    )
    print("\n创建日记:")
    print_result(result)
    
    # 获取日记列表
    print("\n获取日记列表:")
    result = get_emotion_diaries(user_id, limit=5)
    print_result(result)

def test_emotion_pattern():
    """测试情绪模式分析"""
    print_test("情绪模式分析")
    
    user_id = "test_user_001"
    
    # 先记录足够的数据
    for i in range(5):
        emotions = ["happy", "sad", "calm", "anxious", "happy"]
        record_emotion(user_id, emotions[i], 0.5 + i * 0.1, f"测试记录{i+1}")
    
    result = analyze_emotion_pattern(user_id)
    print_result(result)

def main():
    """主函数"""
    print("\n" + "="*60)
    print("灵值智能体 v8.0 - 情绪功能测试")
    print("="*60)
    
    try:
        # 运行所有测试
        test_emotion_detection()
        test_emotion_recording()
        test_emotion_statistics()
        test_emotion_diary()
        test_emotion_pattern()
        
        print("\n" + "="*60)
        print("✅ 所有测试完成！")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
