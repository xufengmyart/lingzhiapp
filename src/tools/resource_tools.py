"""
灵值智能体 v9.0 - 用户资源库工具
"""

from langchain.tools import tool
from typing import Optional, Dict, Any
import requests
import json


@tool
def add_user_resource(
    token: str,
    resource_type: str,
    resource_name: str,
    description: str = "",
    estimated_value: float = 0.0,
    tags: str = ""
) -> str:
    """
    添加用户资源到资源库
    
    Args:
        token: 用户访问令牌
        resource_type: 资源类型（skill:技能, asset:资产, connection:人脉, time:时间, data:数据, brand:品牌）
        resource_name: 资源名称
        description: 资源描述
        estimated_value: 估值
        tags: 标签（逗号分隔）
    
    Returns:
        JSON格式的添加结果
    """
    try:
        url = "http://localhost:8080/api/v9/resources"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'resource_type': resource_type,
            'resource_name': resource_name,
            'description': description,
            'estimated_value': estimated_value,
            'tags': tags
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get('success'):
            return json.dumps({
                'success': True,
                'data': result.get('data', {}),
                'message': f"资源添加成功！资源ID: {result.get('data', {}).get('resource_id')}"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '添加失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'添加资源失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def get_user_resources(token: str) -> str:
    """
    获取用户的资源库
    
    Args:
        token: 用户访问令牌
    
    Returns:
        JSON格式的资源列表
    """
    try:
        url = "http://localhost:8080/api/v9/resources"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get('success'):
            resources = result.get('data', [])
            return json.dumps({
                'success': True,
                'data': resources,
                'message': f"获取成功！你有 {len(resources)} 个资源"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '获取失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'获取资源库失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def analyze_user_resources(resource_list: str) -> str:
    """
    分析用户的资源库，提供价值评估和建议
    
    Args:
        resource_list: 资源列表（JSON格式字符串）
    
    Returns:
        JSON格式的资源分析结果
    """
    try:
        resources = json.loads(resource_list)
        
        # 资源类型统计
        type_stats = {}
        total_value = 0.0
        
        for resource in resources:
            rtype = resource.get('resource_type', 'unknown')
            type_stats[rtype] = type_stats.get(rtype, 0) + 1
            total_value += resource.get('estimated_value', 0.0)
        
        # 资源类型映射
        type_names = {
            'skill': '技能资源',
            'asset': '资产资源',
            'connection': '人脉资源',
            'time': '时间资源',
            'data': '数据资源',
            'brand': '品牌资源'
        }
        
        # 生成分析报告
        analysis = {
            'total_count': len(resources),
            'total_value': total_value,
            'type_distribution': [],
            'suggestions': []
        }
        
        for rtype, count in type_stats.items():
            type_name = type_names.get(rtype, rtype)
            analysis['type_distribution'].append({
                'type': type_name,
                'count': count,
                'percentage': round(count / len(resources) * 100, 2)
            })
        
        # 生成建议
        if 'skill' not in type_stats:
            analysis['suggestions'].append("建议添加技能资源，如设计、编程、写作等专业技能")
        if 'asset' not in type_stats:
            analysis['suggestions'].append("建议添加资产资源，如设备、场地、材料等")
        if 'connection' not in type_stats:
            analysis['suggestions'].append("建议添加人脉资源，扩大合作机会")
        
        analysis['suggestions'].append(f"你的资源库总估值约 {total_value:.2f} 灵值，建议积极参与项目变现")
        
        return json.dumps({
            'success': True,
            'data': analysis,
            'message': "资源分析完成！"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'分析资源失败: {str(e)}'
        }, ensure_ascii=False)
