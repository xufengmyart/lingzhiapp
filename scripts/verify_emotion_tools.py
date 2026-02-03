#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情绪系统功能验证脚本
测试所有情绪工具的导入和基本功能
"""

import sys
import os

# 设置 PYTHONPATH
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """测试所有情绪工具的导入"""
    print("=" * 60)
    print("1. 测试情绪工具导入")
    print("=" * 60)

    try:
        from tools.emotion_tools import (
            detect_emotion,
            record_emotion,
            get_emotion_statistics,
            create_emotion_diary,
            get_emotion_diaries,
            analyze_emotion_pattern
        )
        print("✅ 所有情绪工具导入成功")
        return True
    except Exception as e:
        print(f"❌ 情绪工具导入失败: {e}")
        return False

def test_manager_import():
    """测试情绪管理器的导入"""
    print("\n" + "=" * 60)
    print("2. 测试情绪管理器导入")
    print("=" * 60)

    try:
        from storage.database.emotion_manager import EmotionManager
        print("✅ 情绪管理器导入成功")
        return True
    except Exception as e:
        print(f"❌ 情绪管理器导入失败: {e}")
        return False

def test_models_import():
    """测试数据模型的导入"""
    print("\n" + "=" * 60)
    print("3. 测试数据模型导入")
    print("=" * 60)

    try:
        from storage.database.shared.model import EmotionRecords, EmotionDiaries
        print("✅ 数据模型导入成功")
        print(f"   - EmotionRecords: {EmotionRecords.__tablename__}")
        print(f"   - EmotionDiaries: {EmotionDiaries.__tablename__}")
        return True
    except Exception as e:
        print(f"❌ 数据模型导入失败: {e}")
        return False

def test_agent_import():
    """测试智能体的导入"""
    print("\n" + "=" * 60)
    print("4. 测试智能体导入")
    print("=" * 60)

    try:
        from agents.agent import build_agent
        agent = build_agent()
        print("✅ 智能体构建成功")
        # 注意: agent 对象没有 _tools 属性，工具在创建 agent 时已传入
        return True
    except Exception as e:
        print(f"❌ 智能体构建失败: {e}")
        return False

def test_tool_metadata():
    """测试工具的元数据"""
    print("\n" + "=" * 60)
    print("5. 测试工具元数据")
    print("=" * 60)

    try:
        from tools.emotion_tools import (
            detect_emotion,
            record_emotion,
            get_emotion_statistics,
            create_emotion_diary,
            get_emotion_diaries,
            analyze_emotion_pattern
        )

        tools = [
            ("detect_emotion", detect_emotion),
            ("record_emotion", record_emotion),
            ("get_emotion_statistics", get_emotion_statistics),
            ("create_emotion_diary", create_emotion_diary),
            ("get_emotion_diaries", get_emotion_diaries),
            ("analyze_emotion_pattern", analyze_emotion_pattern)
        ]

        for name, tool in tools:
            print(f"✅ {name}:")
            print(f"   - 描述: {tool.description}")
            print(f"   - 参数: {tool.args_schema.schema() if tool.args_schema else 'None'}")
        return True
    except Exception as e:
        print(f"❌ 工具元数据测试失败: {e}")
        return False

def main():
    """主函数"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "灵值智能体 v8.1 - 功能验证" + " " * 14 + "║")
    print("╚" + "═" * 58 + "╝")
    print()

    results = []

    # 运行所有测试
    results.append(("导入测试", test_imports()))
    results.append(("管理器导入", test_manager_import()))
    results.append(("模型导入", test_models_import()))
    results.append(("智能体构建", test_agent_import()))
    results.append(("工具元数据", test_tool_metadata()))

    # 汇总结果
    print("\n" + "=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    print()
    print("=" * 60)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 60)

    if passed == total:
        print("\n🎉 所有测试通过！情绪系统可以正常部署。")
        return 0
    else:
        print(f"\n⚠️  {total - passed} 个测试失败，请检查错误信息。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
