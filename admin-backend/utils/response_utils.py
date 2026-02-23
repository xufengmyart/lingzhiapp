"""
响应工具模块
提供统一的响应格式转换和字段名转换功能
"""

import re
from typing import Any, Dict, List, Union


def snake_to_camel(name: str) -> str:
    """
    将snake_case转换为camelCase
    
    示例:
        snake_to_camel('agent_id') -> 'agentId'
        snake_to_camel('conversation_id') -> 'conversationId'
        snake_to_camel('total_lingzhi') -> 'totalLingzhi'
    """
    if not name:
        return name
    
    # 分割字符串
    components = name.split('_')
    
    # 第一个单词保持小写，后续单词首字母大写
    return components[0] + ''.join(x.title() for x in components[1:])


def camel_to_snake(name: str) -> str:
    """
    将camelCase转换为snake_case
    
    示例:
        camel_to_snake('agentId') -> 'agent_id'
        camel_to_snake('conversationId') -> 'conversation_id'
        camel_to_snake('totalLingzhi') -> 'total_lingzhi'
    """
    if not name:
        return name
    
    # 在大写字母前插入下划线
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # 转换为小写
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def transform_dict_keys(data: Dict[str, Any], to_camel: bool = True) -> Dict[str, Any]:
    """
    转换字典的键名
    
    Args:
        data: 原始字典
        to_camel: True表示转换为camelCase，False表示转换为snake_case
    
    Returns:
        转换后的字典
    """
    if not isinstance(data, dict):
        return data
    
    result = {}
    for key, value in data.items():
        # 转换键名
        new_key = snake_to_camel(key) if to_camel else camel_to_snake(key)
        
        # 递归处理嵌套字典
        if isinstance(value, dict):
            result[new_key] = transform_dict_keys(value, to_camel)
        # 递归处理嵌套列表
        elif isinstance(value, list):
            result[new_key] = [
                transform_dict_keys(item, to_camel) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[new_key] = value
    
    return result


def success_response(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
    """
    生成标准成功响应
    
    Args:
        data: 响应数据
        message: 成功消息
    
    Returns:
        标准格式的成功响应字典（字段名使用camelCase）
    """
    response = {
        "success": True,
        "message": message
    }
    
    if data is not None:
        # 将数据字段名转换为camelCase
        response["data"] = transform_dict_keys(data, to_camel=True)
    
    return response


def error_response(error: str, code: int = 500) -> Dict[str, Any]:
    """
    生成标准错误响应
    
    Args:
        error: 错误信息
        code: 错误代码
    
    Returns:
        标准格式的错误响应字典
    """
    return {
        "success": False,
        "error": error
    }


# 保留常用的转换函数，方便其他模块直接导入
__all__ = [
    'snake_to_camel',
    'camel_to_snake',
    'transform_dict_keys',
    'success_response',
    'error_response'
]
