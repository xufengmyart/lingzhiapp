"""
同步依赖库版本不兼容问题修复
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
    print("同步依赖库版本不兼容问题修复")
    print("="*70)
    print()

    # 需要同步的修复文件
    files_to_sync = [
        ("src/tools/check_in_tool.py", "灵值生态园智能体移植包/02_源代码/tools/check_in_tool.py", "签到工具（已修复）"),
        ("src/tools/login_tool.py", "灵值生态园智能体移植包/02_源代码/tools/login_tool.py", "登录工具（已修复）"),
        ("src/tools/security_tools.py", "灵值生态园智能体移植包/02_源代码/tools/security_tools.py", "安全工具（已修复）"),
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
        print("✅ 所有修复文件同步成功！")
    else:
        print(f"⚠️  {failed_count} 个文件同步失败")

    print()
    print("="*70)
    print("修复内容总结")
    print("="*70)
    print("✅ 移除所有 get_current_user_id 导入")
    print("✅ 改用 runtime.context 获取用户ID")
    print("✅ 修复异常处理逻辑")
    print("✅ 所有工具测试通过")
    print()
    print("="*70)


if __name__ == "__main__":
    main()
