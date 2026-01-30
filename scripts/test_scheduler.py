#!/usr/bin/env python3
"""
智能体一致性验证定时任务调度器（测试模式）

用于测试调度器是否能正常工作，不启动持续运行的调度器
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    """测试导入"""
    try:
        import schedule
        print("✅ schedule库导入成功")
    except ImportError as e:
        print(f"❌ schedule库导入失败: {e}")
        return False

    try:
        from scripts.scheduler_agent_consistency import run_verification
        print("✅ run_verification函数导入成功")
    except ImportError as e:
        print(f"❌ run_verification函数导入失败: {e}")
        return False

    return True

def test_verification():
    """测试验证函数"""
    try:
        from scripts.scheduler_agent_consistency import run_verification
        print("\n开始执行验证...")
        result = run_verification()
        if result:
            print("✅ 验证执行成功")
        else:
            print("❌ 验证执行失败")
        return result
    except Exception as e:
        print(f"❌ 验证执行异常: {e}")
        return False

def main():
    print("="*70)
    print("智能体一致性验证定时任务调度器 - 测试模式")
    print("="*70)
    print()

    # 测试导入
    print("1. 测试导入...")
    if not test_imports():
        print("\n❌ 导入测试失败，请检查依赖是否安装")
        return 1

    # 测试验证
    print("\n2. 测试验证函数...")
    if not test_verification():
        print("\n❌ 验证测试失败，请检查验证脚本")
        return 1

    print("\n" + "="*70)
    print("✅ 所有测试通过！调度器可以正常工作")
    print("="*70)
    print()
    print("启动生产调度器，请运行:")
    print("  ./scripts/scheduler_manager.sh start")
    print("  或")
    print("  python scripts/scheduler_agent_consistency.py")
    print()

    return 0

if __name__ == "__main__":
    exit(main())
