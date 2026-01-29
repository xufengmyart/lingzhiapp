"""
两个智能体完整同步脚本

同步当前项目和移植包的所有文件
"""

import os
import shutil
import hashlib
from pathlib import Path


def get_file_hash(file_path):
    """获取文件的MD5哈希值"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception:
        return None


def sync_files():
    """同步两个智能体的文件"""
    
    print("="*70)
    print("两个智能体完整同步")
    print("="*70)
    print()
    
    # 定义需要同步的文件
    sync_files_list = [
        # Agent核心文件
        ("src/agents/agent.py", "灵值生态园智能体移植包/02_源代码/agent.py"),
        
        # 配置文件
        ("config/agent_llm_config.json", "灵值生态园智能体移植包/02_源代码/config/agent_llm_config.json"),
        
        # 经济模型配置
        ("src/config/economic_model.py", "灵值生态园智能体移植包/02_源代码/config/economic_model.py"),
        
        # 超级管理员配置
        ("src/config/super_admin_config.py", "灵值生态园智能体移植包/02_源代码/config/super_admin_config.py"),
        
        # 工具文件
        ("src/tools/knowledge_retrieval_tool.py", "灵值生态园智能体移植包/02_源代码/tools/knowledge_retrieval_tool.py"),
        ("src/tools/image_generation_tool.py", "灵值生态园智能体移植包/02_源代码/tools/image_generation_tool.py"),
        ("src/tools/web_search_tool.py", "灵值生态园智能体移植包/02_源代码/tools/web_search_tool.py"),
        ("src/tools/lingzhi_calculator.py", "灵值生态园智能体移植包/02_源代码/tools/lingzhi_calculator.py"),
        ("src/tools/super_admin_manager.py", "灵值生态园智能体移植包/02_源代码/tools/super_admin_manager.py"),
        
        # 验证脚本
        ("scripts/verify_agent_consistency.py", "灵值生态园智能体移植包/02_源代码/scripts/verify_agent_consistency.py"),
    ]
    
    # 确保目标目录存在
    target_dirs = [
        "灵值生态园智能体移植包/02_源代码/config",
        "灵值生态园智能体移植包/02_源代码/tools",
        "灵值生态园智能体移植包/02_源代码/scripts",
    ]
    
    for target_dir in target_dirs:
        os.makedirs(target_dir, exist_ok=True)
    
    # 同步文件
    print("开始同步文件...")
    print()
    
    sync_results = []
    for source_path, target_path in sync_files_list:
        if not os.path.exists(source_path):
            print(f"❌ 源文件不存在: {source_path}")
            sync_results.append((source_path, "源文件不存在"))
            continue
        
        # 读取源文件
        try:
            with open(source_path, 'rb') as f:
                source_content = f.read()
            
            # 写入目标文件
            with open(target_path, 'wb') as f:
                f.write(source_content)
            
            # 计算哈希值
            source_hash = hashlib.md5(source_content).hexdigest()
            
            print(f"✅ {source_path}")
            print(f"   → {target_path}")
            print(f"   MD5: {source_hash}")
            sync_results.append((source_path, "成功"))
            
        except Exception as e:
            print(f"❌ 同步失败: {source_path}")
            print(f"   错误: {e}")
            sync_results.append((source_path, f"失败: {e}"))
        
        print()
    
    # 统计结果
    success_count = sum(1 for _, result in sync_results if result == "成功")
    failed_count = sum(1 for _, result in sync_results if result != "成功")
    total_count = len(sync_results)
    
    print("="*70)
    print("同步结果统计")
    print("="*70)
    print(f"总文件数: {total_count}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print()
    
    if failed_count > 0:
        print("失败的文件:")
        for file_path, result in sync_results:
            if result != "成功":
                print(f"  - {file_path}: {result}")
        print()
    
    if failed_count == 0:
        print("✅ 所有文件同步成功!")
    else:
        print(f"⚠️  {failed_count} 个文件同步失败")
    
    print()
    print("="*70)
    
    return failed_count == 0


if __name__ == "__main__":
    success = sync_files()
    exit(0 if success else 1)
