"""
同步数据库工具到两个智能体
"""

import os
import hashlib


def sync_file(source_path, target_path, description):
    """同步单个文件"""
    print(f"📦 {description}")

    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)

    try:
        with open(source_path, 'rb') as f:
            source_content = f.read()

        with open(target_path, 'wb') as f:
            f.write(source_content)

        source_hash = hashlib.md5(source_content).hexdigest()

        print(f"   ✅ {source_path}")
        print(f"   → {target_path}")
        print(f"   MD5: {source_hash}")
        print()

        return True

    except Exception as e:
        print(f"   ❌ 同步失败: {e}")
        print()
        return False


def main():
    """主函数"""
    print("="*70)
    print("同步数据库工具到两个智能体")
    print("="*70)
    print()

    # 需要同步的文件
    files_to_sync = [
        ("src/tools/database_tools.py", "灵值生态园智能体移植包/02_源代码/tools/database_tools.py", "数据库工具（新增）"),
        ("src/agents/agent.py", "灵值生态园智能体移植包/02_源代码/agents/agent.py", "Agent核心文件（已集成）"),
        ("config/agent_llm_config.json", "灵值生态园智能体移植包/02_源代码/config/agent_llm_config.json", "LLM配置文件（已更新）"),
    ]

    success_count = 0
    failed_count = 0

    for source, target, desc in files_to_sync:
        if sync_file(source, target, desc):
            success_count += 1
        else:
            failed_count += 1

    print("="*70)
    print("同步结果统计")
    print("="*70)
    print(f"总文件数: {len(files_to_sync)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print()

    if failed_count == 0:
        print("✅ 所有文件同步成功！")
    else:
        print(f"⚠️  {failed_count} 个文件同步失败")

    print()
    print("="*70)
    print("功能概述")
    print("="*70)
    print("提供的数据库工具：")
    print("1. test_database_connection - 测试数据库连接")
    print("2. get_database_status - 获取数据库状态")
    print("3. get_user_statistics - 获取用户统计")
    print("4. get_table_structure - 获取表结构")
    print("5. execute_sql_query - 执行SQL查询")
    print()
    print("安全特性：")
    print("- 只允许SELECT查询")
    print("- 严格的权限检查")
    print("- 完整的错误处理")
    print("- 详细的操作日志")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
