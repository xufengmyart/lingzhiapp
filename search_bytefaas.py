#!/usr/bin/env python3
"""
搜索ByteFaaS环境配置文档
"""

from coze_coding_dev_sdk import SearchClient
from coze_coding_utils.runtime_ctx.context import new_context
import json

ctx = new_context(method="search.bytefaas")
client = SearchClient(ctx=ctx)

print("=" * 80)
print("正在搜索 ByteFaaS 环境配置文档...")
print("=" * 80)

# 搜索1: ByteFaaS环境访问配置
print("\n【搜索1】ByteFaaS环境访问配置...")
response1 = client.web_search_with_summary(
    query="ByteFaaS环境访问配置 端口 公网访问",
    count=5
)

if response1.summary:
    print(f"\nAI摘要:\n{response1.summary}\n")

for i, item in enumerate(response1.web_items[:3], 1):
    print(f"{i}. {item.title}")
    print(f"   URL: {item.url}")
    print(f"   摘要: {item.snippet[:150]}...\n")

# 搜索2: Coze平台FaaS配置
print("=" * 80)
print("【搜索2】Coze平台FaaS配置...")
response2 = client.web_search_with_summary(
    query="Coze平台 FaaS服务 配置 域名访问",
    count=5
)

if response2.summary:
    print(f"\nAI摘要:\n{response2.summary}\n")

for i, item in enumerate(response2.web_items[:3], 1):
    print(f"{i}. {item.title}")
    print(f"   URL: {item.url}")
    print(f"   摘要: {item.snippet[:150]}...\n")

# 搜索3: FaaS服务403 Forbidden问题
print("=" * 80)
print("【搜索3】FaaS服务403 Forbidden解决...")
response3 = client.web_search_with_summary(
    query="FaaS服务 403 Forbidden nginx 解决方案",
    count=5
)

if response3.summary:
    print(f"\nAI摘要:\n{response3.summary}\n")

for i, item in enumerate(response3.web_items[:3], 1):
    print(f"{i}. {item.title}")
    print(f"   URL: {item.url}")
    print(f"   摘要: {item.snippet[:150]}...\n")

# 保存结果
results = {
    "bytefaas_config": {
        "summary": response1.summary,
        "items": [
            {
                "title": item.title,
                "url": item.url,
                "snippet": item.snippet
            }
            for item in response1.web_items
        ]
    },
    "coze_faaS_config": {
        "summary": response2.summary,
        "items": [
            {
                "title": item.title,
                "url": item.url,
                "snippet": item.snippet
            }
            for item in response2.web_items
        ]
    },
    "403_solution": {
        "summary": response3.summary,
        "items": [
            {
                "title": item.title,
                "url": item.url,
                "snippet": item.snippet
            }
            for item in response3.web_items
        ]
    }
}

output_file = "/workspace/projects/public/BYTEFAAS_SEARCH_RESULT.json"
with open(output_file, "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("=" * 80)
print(f"\n搜索结果已保存到: {output_file}")
print("=" * 80)
