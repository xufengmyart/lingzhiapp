#!/usr/bin/env python3
"""导入转译商业案例库到知识库"""
import os
from coze_coding_dev_sdk import KnowledgeClient, KnowledgeDocument
from coze_coding_utils.runtime_ctx.context import new_context


def import_case_library():
    """导入转译商业案例库"""
    ctx = new_context(method="import_knowledge")
    client = KnowledgeClient(ctx=ctx)
    
    # 读取文档内容
    workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
    doc_path = os.path.join(workspace_path, "assets", "转译商业案例库.md")
    
    with open(doc_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 创建文档对象（source=0 表示文本类型）
    doc = KnowledgeDocument(
        source=0,  # 0 表示 TEXT
        raw_data=content,
        metadata={"title": "转译商业案例库", "type": "business_case_library"}
    )
    
    # 导入到知识库
    print("正在导入转译商业案例库到知识库...")
    response = client.add_documents(
        documents=[doc],
        table_name="coze_doc_knowledge"
    )
    
    if response.code == 0:
        print(f"✅ 导入成功！文档ID: {response.doc_ids}")
        print(f"知识库现已包含转译商业案例库，Agent 可以查询相关商业转译案例。")
    else:
        print(f"❌ 导入失败: {response.msg}")


if __name__ == "__main__":
    import_case_library()
