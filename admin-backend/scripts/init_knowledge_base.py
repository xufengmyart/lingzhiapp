#!/usr/bin/env python3
"""
灵值生态园知识库管理工具
用于导入公司文件到知识库，丰富智能体的知识储备
"""

import os
import sys
from pathlib import Path
from coze_coding_dev_sdk import KnowledgeClient, Config, KnowledgeDocument, DataSourceType, ChunkConfig
from coze_coding_utils.runtime_ctx.context import Context

# 初始化客户端
def init_knowledge_client():
    """初始化知识库客户端"""
    try:
        ctx = Context()
        config = Config()
        client = KnowledgeClient(config=config, ctx=ctx)
        print("✓ 知识库客户端初始化成功")
        return client
    except Exception as e:
        print(f"✗ 知识库客户端初始化失败: {e}")
        sys.exit(1)

# 导入单个文件
def import_file(client, file_path, dataset_name="lingzhi_knowledge"):
    """导入单个文件到知识库"""
    if not os.path.exists(file_path):
        print(f"✗ 文件不存在: {file_path}")
        return False

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        doc = KnowledgeDocument(
            source=DataSourceType.TEXT,
            raw_data=content,
            metadata={
                "filename": os.path.basename(file_path),
                "filepath": str(file_path),
                "size": len(content)
            }
        )

        # 自定义分块配置
        chunk_config = ChunkConfig(
            separator="\n\n",
            max_tokens=1500,
            remove_extra_spaces=True
        )

        response = client.add_documents(
            documents=[doc],
            table_name=dataset_name,
            chunk_config=chunk_config
        )

        if response.code == 0:
            print(f"✓ 成功导入: {os.path.basename(file_path)} (ID: {response.doc_ids[0] if response.doc_ids else 'N/A'})")
            return True
        else:
            print(f"✗ 导入失败: {os.path.basename(file_path)} - {response.msg}")
            return False

    except Exception as e:
        print(f"✗ 读取文件失败: {file_path} - {e}")
        return False

# 导入目录中的所有文件
def import_directory(client, directory_path, dataset_name="lingzhi_knowledge"):
    """导入目录中的所有文件到知识库"""
    if not os.path.isdir(directory_path):
        print(f"✗ 目录不存在: {directory_path}")
        return

    # 支持的文件扩展名
    supported_extensions = {'.md', '.txt', '.rst'}

    # 查找所有支持的文件
    files = []
    for root, dirs, filenames in os.walk(directory_path):
        for filename in filenames:
            if Path(filename).suffix.lower() in supported_extensions:
                files.append(os.path.join(root, filename))

    if not files:
        print(f"✗ 未找到支持的文件 (支持: {', '.join(supported_extensions)})")
        return

    print(f"\n找到 {len(files)} 个文件，开始导入...")
    print("=" * 60)

    success_count = 0
    for file_path in files:
        if import_file(client, file_path, dataset_name):
            success_count += 1

    print("=" * 60)
    print(f"导入完成: {success_count}/{len(files)} 文件成功")

# 搜索知识库
def search_knowledge(client, query, dataset_name="lingzhi_knowledge", top_k=5):
    """在知识库中搜索"""
    print(f"\n搜索: '{query}'")
    print("=" * 60)

    try:
        response = client.search(
            query=query,
            table_names=[dataset_name] if dataset_name else None,
            top_k=top_k,
            min_score=0.3
        )

        if response.code == 0:
            if response.chunks:
                for i, chunk in enumerate(response.chunks, 1):
                    print(f"\n[{i}] 相似度: {chunk.score:.4f}")
                    print(f"内容: {chunk.content[:200]}...")
                    print(f"文档ID: {chunk.doc_id}")
            else:
                print("未找到相关内容")
        else:
            print(f"搜索失败: {response.msg}")

    except Exception as e:
        print(f"搜索错误: {e}")

# 主函数
def main():
    print("=" * 60)
    print("灵值生态园知识库管理工具")
    print("=" * 60)

    # 初始化客户端
    client = init_knowledge_client()

    # 数据集名称
    dataset_name = "lingzhi_knowledge"

    # 定义要导入的文件列表
    files_to_import = [
        "assets/公司简介.md",
        "assets/灵值生态一体化服务总纲.md",
        "assets/西安文化关键词库.md",
        "assets/西安文化基因库.md",
        "assets/转译商业案例库.md",
    ]

    print(f"\n数据集名称: {dataset_name}")
    print(f"计划导入 {len(files_to_import)} 个文件\n")

    # 导入文件
    success_count = 0
    for file_path in files_to_import:
        if import_file(client, file_path, dataset_name):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"导入完成: {success_count}/{len(files_to_import)} 文件成功")
    print("=" * 60)

    # 演示搜索功能
    print("\n演示搜索功能:")
    print("-" * 60)

    test_queries = [
        "媄月公司的使命是什么？",
        "什么是灵值生态的核心架构？",
        "西安文化关键词有哪些？",
    ]

    for query in test_queries:
        search_knowledge(client, query, dataset_name, top_k=3)
        print()

    print("=" * 60)
    print("知识库初始化完成！")
    print("=" * 60)

if __name__ == "__main__":
    main()
