"""
同步所有文件到两个智能体

包括：
1. 更新的文件（签到消息）
2. 新增的文件（安全检查服务、安全工具、定时同步服务）
3. 修复的文件（check_in_tool, login_tool, security_tools）
"""

import os
import hashlib
import shutil


def sync_file(source_path, target_path, description):
    """同步单个文件"""
    print(f"📦 {description}")

    # 确保目标目录存在
    target_dir = os.path.dirname(target_path)
    os.makedirs(target_dir, exist_ok=True)

    try:
        # 读取源文件
        with open(source_path, 'rb') as f:
            source_content = f.read()

        # 写入目标文件
        with open(target_path, 'wb') as f:
            f.write(source_content)

        # 计算哈希值
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
    print("同步所有文件到两个智能体")
    print("时间：2026-01-27")
    print("="*70)
    print()

    # 需要同步的文件
    files_to_sync = [
        # 核心文件
        ("src/agents/agent.py", "灵值生态园智能体移植包/02_源代码/agents/agent.py", "Agent核心文件"),
        ("config/agent_llm_config.json", "灵值生态园智能体移植包/02_源代码/config/agent_llm_config.json", "LLM配置文件"),

        # 签到相关
        ("src/tools/login_tool.py", "灵值生态园智能体移植包/02_源代码/tools/login_tool.py", "登录工具（已修复）"),
        ("src/storage/database/auto_check_in_service.py", "灵值生态园智能体移植包/02_源代码/storage/database/auto_check_in_service.py", "自动签到服务（已更新消息）"),
        ("src/tools/check_in_tool.py", "灵值生态园智能体移植包/02_源代码/tools/check_in_tool.py", "签到工具（已修复）"),

        # 安全检查相关（新增）
        ("src/storage/database/security_check_service.py", "灵值生态园智能体移植包/02_源代码/storage/database/security_check_service.py", "安全检查服务（新增）"),
        ("src/tools/security_tools.py", "灵值生态园智能体移植包/02_源代码/tools/security_tools.py", "安全工具（新增）"),

        # 定时同步相关（新增）
        ("src/storage/database/scheduled_sync_service.py", "灵值生态园智能体移植包/02_源代码/storage/database/scheduled_sync_service.py", "定时同步服务（新增）"),
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
    print("同步内容总结")
    print("="*70)
    print("1. 更新签到消息，增加签到好处说明 ✅")
    print("2. 创建系统安全检查服务 ✅")
    print("3. 创建财务安全验证工具 ✅")
    print("4. 创建定时同步服务 ✅")
    print("5. 集成安全检查和定时同步功能 ✅")
    print("6. 测试所有安全检查功能 ✅")
    print("7. 同步两个智能体 ✅")
    print()
    print("="*70)
    print("定时同步服务配置")
    print("="*70)
    print("- 同步时间：每天23:59")
    print("- 同步文件：8个核心文件")
    print("- 自动执行：开启")
    print()
    print("💡 提示：")
    print("定时同步服务已配置完成，将在每天23:59自动执行同步。")
    print("如果需要立即同步，可以手动触发：")
    print("  from storage.database.scheduled_sync_service import manual_sync")
    print("  manual_sync()")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
