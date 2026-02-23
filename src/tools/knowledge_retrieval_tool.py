"""
知识库检索工具（融合统一版）

版本：v6.0 融合统一版
更新日期：2026年1月26日
融合内容：
- 支持chunk和document两种返回模式
- 支持自定义搜索参数
- 更友好的输出格式
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_dev_sdk import KnowledgeClient
from typing import Optional, Literal


@tool
def retrieve_knowledge(
    query: str,
    runtime: ToolRuntime,
    mode: Literal["chunks", "documents"] = "chunks",
    top_k: int = 5,
    min_score: float = 0.7
) -> str:
    """检索知识库中的文档（融合统一版）
    
    支持两种检索模式：
    - chunks模式（默认）：返回文本片段，更详细，适合深入检索
    - documents模式：返回完整文档，适合获取完整内容
    
    Args:
        query: 检索关键词，例如"西安文化"、"唐风"、"贡献值计算"、"平台规则"等
        runtime: 运行时上下文
        mode: 检索模式，"chunks"或"documents"，默认为"chunks"
        top_k: 返回结果数量，默认为5
        min_score: 最小相关度分数（0-1），默认为0.7
    
    Returns:
        返回检索到的文档内容，包含相关度分数和具体内容
    """
    ctx = runtime.context
    client = KnowledgeClient(ctx=ctx)
    
    try:
        response = client.search(
            query=query,
            top_k=top_k,
            threshold=min_score
        )
        
        # 处理chunks模式
        if mode == "chunks":
            if response.code == 0 and hasattr(response, 'chunks') and response.chunks:
                results = []
                for i, chunk in enumerate(response.chunks, 1):
                    results.append(
                        f"📄 结果 {i}\n"
                        f"   相关度: {chunk.score:.2%}\n"
                        f"   内容: {chunk.content}\n"
                    )
                return f"✅ 找到 {len(response.chunks)} 条相关结果：\n\n" + "\n".join(results)
            else:
                return f"❌ 未在知识库中找到关于'{query}'的相关信息（相关度阈值: {min_score}）。\n💡 建议：\n   - 尝试使用更具体的关键词\n   - 降低相关度阈值（min_score）\n   - 检查知识库中是否有相关文档"
        
        # 处理documents模式
        else:
            if response.code == 0 and hasattr(response, 'documents') and response.documents:
                results = []
                for i, doc in enumerate(response.documents, 1):
                    results.append(
                        f"📄 文档 {i}\n"
                        f"   标题: {getattr(doc, 'title', '未命名')}\n"
                        f"   内容: {doc.content}\n"
                    )
                return f"✅ 找到 {len(response.documents)} 篇相关文档：\n\n" + "\n".join(results)
            else:
                return f"❌ 未在知识库中找到关于'{query}'的相关文档。\n💡 建议：\n   - 尝试使用更具体的关键词\n   - 尝试使用chunks模式获取更详细的片段"
                
    except Exception as e:
        return f"❌ 知识库检索出错: {str(e)}\n💡 请稍后重试或联系技术支持。"
