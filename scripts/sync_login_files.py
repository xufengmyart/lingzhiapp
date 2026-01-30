"""
同步新增文件（登录自动签到）
"""

import os
import hashlib


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
    print("新增文件同步（登录自动签到）")
    print("="*70)
    print()
    
    # 需要同步的新增文件
    files_to_sync = [
        ("src/tools/login_tool.py", "灵值生态园智能体移植包/02_源代码/tools/login_tool.py", "登录工具"),
        ("src/storage/database/auto_check_in_service.py", "灵值生态园智能体移植包/02_源代码/storage/database/auto_check_in_service.py", "自动签到服务"),
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
        print("✅ 所有新增文件同步成功!")
    else:
        print(f"⚠️  {failed_count} 个文件同步失败")
    
    print()
    print("="*70)


if __name__ == "__main__":
    main()
