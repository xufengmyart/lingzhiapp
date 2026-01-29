"""
智能体一致性验证脚本（字节级比较）

验证两个智能体是否完全一致（字节级比较）
"""

import os
import hashlib

def read_file_bytes(file_path):
    """读取文件字节内容"""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except Exception as e:
        return None

def get_file_hash(file_path):
    """获取文件的MD5哈希值"""
    content = read_file_bytes(file_path)
    if content is None:
        return None
    return hashlib.md5(content).hexdigest()

def compare_files_byte(file1, file2):
    """字节级比较两个文件"""
    hash1 = get_file_hash(file1)
    hash2 = get_file_hash(file2)
    
    if hash1 is None or hash2 is None:
        return False, "文件读取失败"
    
    return hash1 == hash2, ""

def main():
    print("="*70)
    print("智能体一致性验证（字节级）")
    print("="*70)
    
    # 定义文件路径
    project_agent = "src/agents/agent.py"
    移植包_agent = "灵值生态园智能体移植包/02_源代码/agent.py"
    
    project_tools = {
        "knowledge": "src/tools/knowledge_retrieval_tool.py",
        "image": "src/tools/image_generation_tool.py",
        "web": "src/tools/web_search_tool.py",
        "lingzhi": "src/tools/lingzhi_calculator.py"
    }
    
    移植包_tools = {
        "knowledge": "灵值生态园智能体移植包/02_源代码/tools/knowledge_retrieval_tool.py",
        "image": "灵值生态园智能体移植包/02_源代码/tools/image_generation_tool.py",
        "web": "灵值生态园智能体移植包/02_源代码/tools/web_search_tool.py",
        "lingzhi": "灵值生态园智能体移植包/02_源代码/tools/lingzhi_calculator.py"
    }
    
    all_match = True
    details = []
    
    # 1. 比较agent.py
    print("\n1. 比较Agent核心文件")
    print("-"*70)
    is_equal, _ = compare_files_byte(project_agent, 移植包_agent)
    if is_equal:
        print("✅ agent.py 完全一致（字节级）")
        details.append(("agent.py", True))
    else:
        print("❌ agent.py 不一致")
        all_match = False
        details.append(("agent.py", False))
    
    # 2. 比较工具文件
    print("\n2. 比较工具文件")
    print("-"*70)
    
    for tool_name, project_path in project_tools.items():
        移植包_path = 移植包_tools[tool_name]
        
        if not os.path.exists(移植包_path):
            print(f"❌ {tool_name}: 移植包文件不存在")
            all_match = False
            details.append((tool_name, False))
            continue
        
        is_equal, _ = compare_files_byte(project_path, 移植包_path)
        if is_equal:
            print(f"✅ {tool_name}: 完全一致（字节级）")
            details.append((tool_name, True))
        else:
            print(f"❌ {tool_name}: 不一致")
            all_match = False
            details.append((tool_name, False))
    
    # 3. 检查工具数量
    print("\n3. 检查工具数量")
    print("-"*70)
    
    project_tools_count = len(project_tools)
    移植包_tools_count = len([p for p in 移植包_tools.values() if os.path.exists(p)])
    
    print(f"当前项目工具数量: {project_tools_count}")
    print(f"移植包工具数量: {移植包_tools_count}")
    
    if project_tools_count == 移植包_tools_count:
        print("✅ 工具数量一致")
    else:
        print("❌ 工具数量不一致")
        all_match = False
    
    # 4. 生成一致性报告
    print("\n4. 一致性报告")
    print("-"*70)
    
    match_count = sum(1 for _, is_match in details if is_match)
    total_count = len(details)
    
    print(f"文件总数: {total_count}")
    print(f"完全一致: {match_count}")
    print(f"不一致: {total_count - match_count}")
    
    # 5. 总结
    print("\n" + "="*70)
    print("验证结果")
    print("="*70)
    
    if all_match:
        print("✅✅✅ 两个智能体完全一致！✅✅✅")
        print("\n当前项目智能体和移植包智能体在以下方面完全一致：")
        print("- Agent核心代码（字节级100%匹配）")
        print("- 知识库检索工具（字节级100%匹配）")
        print("- 文生图工具（字节级100%匹配）")
        print("- 联网搜索工具（字节级100%匹配）")
        print("- 灵值计算工具（字节级100%匹配）")
        print("- 工具数量和结构（完全匹配）")
        print("\n✨ 两个智能体已经实现完全统一！可以放心使用！")
    else:
        print("❌ 两个智能体存在差异")
        print("\n不一致的文件：")
        for name, is_match in details:
            if not is_match:
                print(f"  - {name}")
        print("\n建议：检查上述不一致的文件并进行调整")
    
    print("="*70)
    
    return all_match

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
