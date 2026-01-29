#!/usr/bin/env python3
"""
灵值生态园智能体移植包 - 快速测试脚本
用于快速验证智能体功能是否正常
"""

import sys
import os

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.agents.agent import build_agent
from langchain_core.messages import HumanMessage


def test_agent():
    """测试智能体"""
    print("="*80)
    print("灵值生态园智能体 - 快速测试")
    print("="*80)
    
    # 构建 Agent
    print("\n🔄 正在构建智能体...")
    try:
        agent = build_agent()
        print("✓ 智能体构建成功")
    except Exception as e:
        print(f"✗ 智能体构建失败: {str(e)}")
        return False
    
    # 测试对话
    print("\n🔄 正在测试对话能力...")
    try:
        test_message = HumanMessage(content="请简要介绍一下灵值生态的核心价值体系")
        config = {"configurable": {"thread_id": "test-session"}}
        
        response = agent.invoke({"messages": [test_message]}, config)
        
        print("✓ 智能体响应成功")
        print("\n智能体回复:")
        print("-" * 80)
        print(response["messages"][-1].content)
        print("-" * 80)
    except Exception as e:
        print(f"✗ 智能体对话测试失败: {str(e)}")
        return False
    
    print("\n✅ 所有测试通过")
    return True


def test_database():
    """测试数据库"""
    print("\n" + "="*80)
    print("数据库连接测试")
    print("="*80)
    
    import sqlite3
    
    db_path = os.path.join(project_root, "src/auth/auth.db")
    
    if not os.path.exists(db_path):
        print(f"✗ 数据库文件不存在: {db_path}")
        return False
    
    print(f"\n🔄 正在连接数据库...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 查询表数量
        cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='table'")
        table_count = cursor.fetchone()[0]
        
        # 查询用户数量
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        print(f"✓ 数据库连接成功")
        print(f"  - 数据库包含 {table_count} 个表")
        print(f"  - 数据库包含 {user_count} 个用户")
        
        conn.close()
        return True
    except Exception as e:
        print(f"✗ 数据库连接失败: {str(e)}")
        return False


def test_tools():
    """测试工具"""
    print("\n" + "="*80)
    print("工具测试")
    print("="*80)
    
    tools = {
        "知识库检索": "knowledge_base_tool",
        "联网搜索": "web_search_tool",
        "文生图": "image_generation_tool",
    }
    
    print("\n工具注册情况:")
    for tool_name, tool_file in tools.items():
        tool_path = os.path.join(project_root, "src/tools", f"{tool_file}.py")
        if os.path.exists(tool_path):
            print(f"✓ {tool_name:<15} - 已注册")
        else:
            print(f"✗ {tool_name:<15} - 未找到")
    
    return True


def main():
    """主函数"""
    print("\n🚀 开始测试...\n")
    
    results = {}
    
    # 测试数据库
    results["数据库"] = test_database()
    
    # 测试工具
    results["工具"] = test_tools()
    
    # 测试智能体
    results["智能体"] = test_agent()
    
    # 汇总结果
    print("\n" + "="*80)
    print("测试结果汇总")
    print("="*80)
    
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:<15} {status}")
    
    print("\n" + "="*80)
    if passed == total:
        print(f"✅ 所有测试通过 ({passed}/{total})")
        print("="*80)
        return 0
    else:
        print(f"⚠️  部分测试失败 ({passed}/{total})")
        print("="*80)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
