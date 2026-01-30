"""
同步快捷方式功能相关文件
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
    print("同步快捷方式功能相关文件")
    print("="*70)
    print()

    # 需要同步的文件
    files_to_sync = [
        ("src/tools/shortcut_tools.py", "灵值生态园智能体移植包/02_源代码/tools/shortcut_tools.py", "快捷方式工具（新增）"),
        ("src/agents/agent.py", "灵值生态园智能体移植包/02_源代码/agents/agent.py", "Agent核心文件（已集成）"),
        ("config/agent_llm_config.json", "灵值生态园智能体移植包/02_源代码/config/agent_llm_config.json", "LLM配置文件（已更新）"),
        ("docs/智能体快捷方式创建完整指南.md", "灵值生态园智能体移植包/02_源代码/docs/智能体快捷方式创建完整指南.md", "完整指南文档"),
        ("docs/快捷方式功能使用说明.md", "灵值生态园智能体移植包/02_源代码/docs/快捷方式功能使用说明.md", "使用说明文档"),
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
    print("✅ 创建快捷方式工具")
    print("✅ 生成各平台安装指南")
    print("✅ 创建快捷方式说明文档")
    print("✅ 在Agent中集成快捷方式工具")
    print("✅ 测试快捷方式功能")
    print("✅ 同步两个智能体")
    print()
    print("="*70)
    print("功能概述")
    print("="*70)
    print("提供的工具：")
    print("1. create_shortcut_guide - 创建快捷方式指南")
    print("2. create_desktop_shortcut_file - 创建桌面快捷方式文件")
    print("3. generate_qr_code_info - 生成二维码保存建议")
    print()
    print("支持的平台：")
    print("- iPhone/iPad")
    print("- Android")
    print("- Windows")
    print("- Mac")
    print("- Linux")
    print()
    print("用户体验提升：")
    print("- 无需每次扫码")
    print("- 无需每次找链接")
    print("- 一键直达对话界面")
    print("- 体验接近原生应用")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
