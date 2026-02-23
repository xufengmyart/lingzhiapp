"""
用户名称处理工具
统一处理用户名称的显示，避免显示"用户1"、"用户2"等格式
"""

def format_user_display_name(user_id=None, username=None):
    """
    格式化用户显示名称
    
    Args:
        user_id: 用户ID
        username: 用户名
    
    Returns:
        格式化后的显示名称
    """
    if not user_id:
        return "注册用户"
    
    # 如果有用户名且不是"用户X"格式，则使用原始用户名
    if username and not str(username).startswith("用户"):
        return username
    
    # 否则返回"注册用户"
    return "注册用户"


def format_author_name(author=None, author_id=None):
    """
    格式化作者名称
    
    Args:
        author: 作者名称
        author_id: 作者ID
    
    Returns:
        格式化后的作者名称
    """
    if not author:
        return "系统"
    
    # 如果是"用户X"格式，转换为"注册用户"
    if isinstance(author, str) and author.startswith("用户"):
        return "注册用户"
    
    return author


def sanitize_user_name(username):
    """
    清理用户名，移除"用户X"等格式
    
    Args:
        username: 原始用户名
    
    Returns:
        清理后的用户名
    """
    if not username:
        return "注册用户"
    
    # 如果是"用户X"格式，返回"注册用户"
    if str(username).startswith("用户"):
        return "注册用户"
    
    return username


def batch_format_user_names(user_list):
    """
    批量格式化用户名称列表
    
    Args:
        user_list: 用户列表，每个用户包含 id 和 username 字段
    
    Returns:
        格式化后的用户列表
    """
    if not user_list:
        return []
    
    formatted_list = []
    for user in user_list:
        user_id = user.get('id') or user.get('userId')
        username = user.get('username') or user.get('userName')
        
        formatted_user = user.copy()
        formatted_user['displayName'] = format_user_display_name(user_id, username)
        formatted_user['username'] = sanitize_user_name(username)
        
        formatted_list.append(formatted_user)
    
    return formatted_list


def format_news_article_user_info(article):
    """
    格式化新闻文章中的用户信息
    
    Args:
        article: 新闻文章字典
    
    Returns:
        格式化后的文章字典
    """
    if not article:
        return article
    
    # 格式化作者名称
    if 'author' in article:
        article['author'] = format_author_name(article['author'])
    
    # 格式化评论中的用户名称
    if 'comments' in article and article['comments']:
        article['comments'] = [
            {
                **comment,
                'username': sanitize_user_name(comment.get('username'))
            }
            for comment in article['comments']
        ]
    
    return article
