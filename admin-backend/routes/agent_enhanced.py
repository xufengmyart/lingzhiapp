#!/usr/bin/env python
"""
智能体增强模块 - 集成知识库检索功能
让智能体能够从知识库中检索相关信息，提供更准确的回答
"""

import sqlite3
import os
from typing import List, Dict, Optional

def get_db_connection():
    """获取数据库连接"""
    import sys
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from config import config
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def search_knowledge_base(query: str, agent_id: int = 1, top_k: int = 5) -> List[Dict]:
    """
    从知识库中搜索相关信息
    
    Args:
        query: 用户查询
        agent_id: 智能体ID
        top_k: 返回结果数量
    
    Returns:
        匹配的知识库文档列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取智能体关联的知识库
    cursor.execute('''
        SELECT knowledge_base_id FROM agent_knowledge_bases WHERE agent_id = ?
    ''', (agent_id,))
    
    kb_relations = cursor.fetchall()
    
    if not kb_relations:
        conn.close()
        return []
    
    kb_ids = [rel['knowledge_base_id'] for rel in kb_relations]
    
    # 从知识库中搜索（简单的关键词匹配）
    results = []
    
    # 分割查询关键词
    keywords = query.strip().split()
    
    for kb_id in kb_ids:
        # 搜索 knowledge_documents
        cursor.execute('''
            SELECT id, title, content, summary
            FROM knowledge_documents
            WHERE knowledge_base_id = ?
            AND (title LIKE ? OR content LIKE ? OR summary LIKE ?)
            LIMIT ?
        ''', (kb_id, f'%{query}%', f'%{query}%', f'%{query}%', top_k))
        
        docs = cursor.fetchall()
        
        for doc in docs:
            results.append({
                'id': doc['id'],
                'title': doc['title'],
                'content': doc['content'][:1000] if doc['content'] else '',  # 限制长度
                'summary': doc['summary'] or '',
                'source': 'knowledge_documents'
            })
    
    # 如果没有找到，搜索 knowledge 表
    if len(results) < top_k:
        cursor.execute('''
            SELECT id, title, content
            FROM knowledge
            WHERE title LIKE ? OR content LIKE ?
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', top_k))
        
        kb_items = cursor.fetchall()
        
        for item in kb_items:
            results.append({
                'id': item['id'],
                'title': item['title'],
                'content': item['content'][:1000] if item['content'] else '',
                'summary': '',
                'source': 'knowledge'
            })
    
    conn.close()
    return results[:top_k]

def get_core_knowledge_base() -> str:
    """
    获取核心知识库内容
    
    Returns:
        核心知识库的完整内容
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取所有核心知识库文档
    cursor.execute('''
        SELECT title, content, summary
        FROM knowledge_documents
        WHERE knowledge_base_id = 7
        ORDER BY id
    ''')
    
    docs = cursor.fetchall()
    
    knowledge_content = ""
    for doc in docs:
        knowledge_content += f"\n## {doc['title']}\n"
        if doc['summary']:
            knowledge_content += f"{doc['summary']}\n\n"
        if doc['content']:
            knowledge_content += f"{doc['content'][:2000]}\n\n"  # 限制长度
    
    # 获取 knowledge 表的内容
    cursor.execute('''
        SELECT title, content
        FROM knowledge
        ORDER BY id
    ''')
    
    kb_items = cursor.fetchall()
    
    knowledge_content += "\n# 常见问题\n"
    for item in kb_items:
        knowledge_content += f"\n## {item['title']}\n{item['content']}\n"
    
    conn.close()
    return knowledge_content

def enhance_system_prompt_with_knowledge(system_prompt: str, query: str, agent_id: int = 1) -> str:
    """
    用知识库内容增强系统提示词
    
    Args:
        system_prompt: 原始系统提示词
        query: 用户查询
        agent_id: 智能体ID
    
    Returns:
        增强后的系统提示词
    """
    # 搜索相关知识
    relevant_knowledge = search_knowledge_base(query, agent_id, top_k=3)
    
    if not relevant_knowledge:
        # 如果没有找到相关知识，返回原始提示词
        return system_prompt
    
    # 构建知识库上下文
    knowledge_context = "\n\n# 📚 相关知识库\n\n"
    
    for i, kb in enumerate(relevant_knowledge, 1):
        knowledge_context += f"## {i}. {kb['title']}\n"
        if kb['summary']:
            knowledge_context += f"{kb['summary']}\n"
        knowledge_context += f"{kb['content'][:800]}\n\n"
    
    # 将知识库上下文添加到系统提示词之前
    enhanced_prompt = f"""{system_prompt}

{knowledge_context}

---
**重要提示**: 上面的知识库内容仅供参考，回答时请结合这些知识为用户提供准确、详细的信息。如果知识库中没有相关信息，请基于你的专业知识回答，但不要编造信息。
"""
    
    return enhanced_prompt

# 测试函数
if __name__ == "__main__":
    # 测试知识库搜索
    print("=== 测试知识库搜索 ===")
    results = search_knowledge_base("公司", agent_id=1)
    print(f"找到 {len(results)} 个相关文档")
    for result in results:
        print(f"\n标题: {result['title']}")
        print(f"来源: {result['source']}")
        print(f"内容预览: {result['content'][:100]}...")
    
    # 测试增强系统提示词
    print("\n\n=== 测试增强系统提示词 ===")
    enhanced = enhance_system_prompt_with_knowledge(
        "你是智能助手",
        "公司",
        agent_id=1
    )
    print(f"增强后的提示词长度: {len(enhanced)} 字符")
