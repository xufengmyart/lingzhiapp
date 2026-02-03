#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
灵值智能体 v8.0 - 快速测试脚本
"""

import sys
import os

# 设置Python路径
sys.path.insert(0, '/workspace/projects/src')

def test_agent_build():
    """测试Agent构建"""
    print("正在测试Agent构建...")
    try:
        from agents.agent import build_agent
        agent = build_agent()
        print("✅ Agent构建成功！")
        return True
    except Exception as e:
        print(f"❌ Agent构建失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_config_load():
    """测试配置加载"""
    print("\n正在测试配置加载...")
    try:
        import json
        config_path = "/workspace/projects/config/agent_llm_config.json"
        with open(config_path, 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        
        print("✅ 配置加载成功！")
        print(f"  - 模型: {cfg['config'].get('model')}")
        print(f"  - 温度: {cfg['config'].get('temperature')}")
        print(f"  - 思考模式: {cfg['config'].get('thinking_type')}")
        print(f"  - System Prompt长度: {len(cfg.get('sp', ''))}")
        print(f"  - 工具数量: {len(cfg.get('tools', []))}")
        return True
    except Exception as e:
        print(f"❌ 配置加载失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_emotion_tools():
    """测试情绪工具"""
    print("\n正在测试情绪工具...")
    try:
        from tools.emotion_tools import detect_emotion, record_emotion
        
        # 检查工具是否存在
        print(f"  - detect_emotion: {detect_emotion}")
        print(f"  - record_emotion: {record_emotion}")
        print("✅ 情绪工具导入成功")
        
        # 注意：工具需要通过Agent调用，直接调用工具对象会失败
        print("  （工具需要通过Agent调用，此处仅验证导入）")
        
        return True
    except Exception as e:
        print(f"❌ 情绪工具测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("=" * 60)
    print("灵值智能体 v8.0 - 快速测试")
    print("=" * 60)
    
    results = []
    
    # 测试配置加载
    results.append(("配置加载", test_config_load()))
    
    # 测试Agent构建
    results.append(("Agent构建", test_agent_build()))
    
    # 测试情绪工具
    results.append(("情绪工具", test_emotion_tools()))
    
    # 汇总结果
    print("\n" + "=" * 60)
    print("测试汇总")
    print("=" * 60)
    for name, success in results:
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {name}: {status}")
    
    all_passed = all(success for _, success in results)
    print("\n" + ("✅ 所有测试通过！" if all_passed else "❌ 部分测试失败"))
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
