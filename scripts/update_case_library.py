#!/usr/bin/env python3
"""更新转译商业案例库到知识库"""
import os
from coze_coding_dev_sdk import KnowledgeClient, KnowledgeDocument
from coze_coding_utils.runtime_ctx.context import new_context


def update_case_library():
    """更新转译商业案例库"""
    ctx = new_context(method="import_knowledge")
    client = KnowledgeClient(ctx=ctx)
    
    # 读取更新后的文档内容
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    doc_path = os.path.join(workspace_path, "assets", "转译商业案例库.md")
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建文档对象（source=0 表示文本类型）
    doc = KnowledgeDocument(
        source=0,  # 0 表示 TEXT
        raw_data=content,
        metadata={"title": "转译商业案例库", "type": "business_case_library", "version": "v2.0", "update_date": "2026-01-22"}
    )
    
    # 导入到知识库
    print("正在更新转译商业案例库到知识库（添加2025-2026最新案例）...")
    response = client.add_documents(
        documents=[doc],
        table_name="coze_doc_knowledge"
    )
    
    if response.code == 0:
        print(f"✅ 更新成功！文档ID: {response.doc_ids}")
        print(f"知识库现已包含9个商业案例和4大转译趋势，Agent 可以查询最新的转译案例。")
    else:
        print(f"❌ 更新失败: {response.msg}")


if __name__ == "__main__":
    update_case_library()
