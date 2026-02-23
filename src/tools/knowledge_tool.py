"""
知识库查询工具
"""
from langchain.tools import tool
import sqlite3
import re
import os

@tool
def search_knowledge(query: str) -> str:
    """搜索知识库，查找与用户问题相关的内容。
    
    Args:
        query: 用户的问题或搜索关键词
        
    Returns:
        匹配的知识库内容，包括标题、分类和详细内容
    """
    db_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"), "admin-backend/lingzhi_ecosystem.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 清理查询字符串
        clean_query = re.sub(r'[^\w\s]', '', query).strip()
        keywords = clean_query.split()
        
        if not keywords:
            return "请提供搜索关键词"
        
        # 构建SQL查询 - 在标题和内容中搜索关键词
        where_clauses = []
        params = []
        
        for keyword in keywords:
            where_clauses.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f'%{keyword}%', f'%{keyword}%'])
        
        where_clause = " AND ".join(where_clauses)
        
        sql = f"""
            SELECT id, title, content, category, tags
            FROM knowledge
            WHERE is_public = 1 AND ({where_clause})
            ORDER BY 
                CASE 
                    WHEN title LIKE ? THEN 1
                    ELSE 2
                END,
                access_count DESC
            LIMIT 5
        """
        
        params.insert(0, f'%{keywords[0]}%')
        cursor.execute(sql, params)
        results = cursor.fetchall()
        
        if not results:
            return "知识库中未找到相关内容。您可以尝试其他关键词，或咨询客服获取帮助。"
        
        # 格式化结果
        output = []
        output.append(f"找到 {len(results)} 条相关内容：\n")
        
        for i, (id, title, content, category, tags) in enumerate(results, 1):
            # 获取内容摘要（前200字）
            clean_content = re.sub(r'[#*`\[\]]', '', content)
            summary = clean_content[:200] + "..." if len(clean_content) > 200 else clean_content
            
            output.append(f"## {i}. {title}")
            output.append(f"**分类**: {category}")
            if tags:
                output.append(f"**标签**: {tags}")
            output.append(f"**摘要**: {summary}")
            output.append(f"**ID**: {id}")
            output.append("")
        
        conn.close()
        return "\n".join(output)
        
    except Exception as e:
        return f"知识库查询失败：{str(e)}"

@tool
def get_knowledge_by_id(knowledge_id: int) -> str:
    """根据ID获取知识库完整内容。
    
    Args:
        knowledge_id: 知识库条目ID
        
    Returns:
        知识库条目的完整内容
    """
    db_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"), "admin-backend/lingzhi_ecosystem.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, content, category, tags, source, access_count, updated_at
            FROM knowledge
            WHERE id = ? AND is_public = 1
        """, (knowledge_id,))
        
        result = cursor.fetchone()
        
        if not result:
            return f"未找到ID为 {knowledge_id} 的知识库条目"
        
        id, title, content, category, tags, source, access_count, updated_at = result
        
        # 更新访问次数
        cursor.execute("UPDATE knowledge SET access_count = access_count + 1 WHERE id = ?", (id,))
        conn.commit()
        conn.close()
        
        output = []
        output.append(f"# {title}")
        output.append(f"**分类**: {category}")
        if tags:
            output.append(f"**标签**: {tags}")
        if source:
            output.append(f"**来源**: {source}")
        output.append(f"**更新时间**: {updated_at}")
        output.append("")
        output.append(content)
        
        return "\n".join(output)
        
    except Exception as e:
        return f"知识库查询失败：{str(e)}"

@tool
def list_knowledge_categories() -> str:
    """列出知识库所有分类及其条目数量。
    
    Returns:
        分类列表和每个分类的条目数量
    """
    db_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"), "admin-backend/lingzhi_ecosystem.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT category, COUNT(*) as count
            FROM knowledge
            WHERE is_public = 1
            GROUP BY category
            ORDER BY count DESC
        """)
        
        results = cursor.fetchall()
        
        if not results:
            return "知识库为空"
        
        output = ["知识库分类列表：\n"]
        
        for category, count in results:
            output.append(f"- {category}: {count}条")
        
        # 获取总数
        cursor.execute("SELECT COUNT(*) FROM knowledge WHERE is_public = 1")
        total = cursor.fetchone()[0]
        
        output.append(f"\n总计：{total}条")
        
        conn.close()
        return "\n".join(output)
        
    except Exception as e:
        return f"知识库查询失败：{str(e)}"

@tool
def list_knowledge_by_category(category: str) -> str:
    """列出指定分类下的所有知识库条目。
    
    Args:
        category: 分类名称
        
    Returns:
        该分类下的所有条目列表
    """
    db_path = os.path.join(os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects"), "admin-backend/lingzhi_ecosystem.db")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, title, tags, access_count, updated_at
            FROM knowledge
            WHERE category LIKE ? AND is_public = 1
            ORDER BY access_count DESC
        """, (f'%{category}%',))
        
        results = cursor.fetchall()
        
        if not results:
            return f"未找到分类 '{category}' 下的内容"
        
        output = [f"分类 '{category}' 下的内容：\n"]
        
        for id, title, tags, access_count, updated_at in results:
            output.append(f"[{id}] {title}")
            if tags:
                output.append(f"    标签: {tags}")
            output.append(f"    浏览: {access_count}次 | 更新: {updated_at}")
            output.append("")
        
        conn.close()
        return "\n".join(output)
        
    except Exception as e:
        return f"知识库查询失败：{str(e)}"
