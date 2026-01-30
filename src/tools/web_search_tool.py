"""
联网搜索工具（融合统一版）

版本：v6.0 融合统一版
更新日期：2026年1月26日
功能：获取最新信息，用于查找最新的品牌营销案例、创意趋势等
"""

from langchain.tools import tool
from langchain.tools import ToolRuntime
from coze_coding_dev_sdk import SearchClient


@tool
def search_web(query: str, runtime: ToolRuntime) -> str:
    """联网搜索获取最新信息（融合统一版）
    
    用于查找最新的品牌营销案例、创意趋势、文化案例等
    
    Args:
        query: 搜索关键词，例如"2024品牌营销趋势"、"文旅创意案例"等
        runtime: 运行时上下文
    
    Returns:
        返回搜索结果的摘要和链接
    """
    ctx = runtime.context
    client = SearchClient(ctx=ctx)
    
    try:
        response = client.web_search_with_summary(
            query=query,
            count=5
        )
        
        if response.web_items:
            result_parts = []
            
            # 添加AI摘要
            if response.summary:
                result_parts.append(f"📋 AI摘要:\n{response.summary}\n")
            
            # 添加搜索结果
            result_parts.append("🔍 搜索结果:")
            for i, item in enumerate(response.web_items, 1):
                result_parts.append(
                    f"\n{i}. {item.title}\n"
                    f"   来源: {item.site_name}\n"
                    f"   摘要: {item.snippet[:150]}...\n"
                    f"   链接: {item.url}"
                )
            
            return "\n".join(result_parts)
        else:
            return f"未找到关于'{query}'的搜索结果，请尝试其他关键词。"
    except Exception as e:
        return f"联网搜索出错: {str(e)}"
