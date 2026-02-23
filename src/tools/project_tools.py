"""
灵值智能体 v9.0 - 项目系统工具
"""

from langchain.tools import tool
from typing import Optional, Dict, Any
import requests
import json


@tool
def create_project(
    token: str,
    title: str,
    project_type: str,
    description: str = "",
    budget: float = 0.0,
    required_skills: str = "",
    required_assets: str = "",
    duration: int = 0,
    location: str = ""
) -> str:
    """
    创建项目
    
    Args:
        token: 用户访问令牌
        title: 项目标题
        project_type: 项目类型（design:设计, development:开发, content:内容创作, consulting:咨询, marketing:营销, rental:租赁）
        description: 项目描述
        budget: 预算
        required_skills: 需要的技能（逗号分隔）
        required_assets: 需要的资产（逗号分隔）
        duration: 预计时长（天）
        location: 地点
    
    Returns:
        JSON格式的创建结果
    """
    try:
        url = "http://localhost:8080/api/v9/projects"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'title': title,
            'description': description,
            'project_type': project_type,
            'budget': budget,
            'required_skills': required_skills,
            'required_assets': required_assets,
            'duration': duration,
            'location': location
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get('success'):
            return json.dumps({
                'success': True,
                'data': result.get('data', {}),
                'message': f"项目创建成功！项目ID: {result.get('data', {}).get('project_id')}"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '创建失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'创建项目失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def get_project_list(
    token: str,
    project_type: str = "",
    status: str = "open"
) -> str:
    """
    获取项目列表
    
    Args:
        token: 用户访问令牌
        project_type: 项目类型（可选）
        status: 项目状态（默认open）
    
    Returns:
        JSON格式的项目列表
    """
    try:
        url = f"http://localhost:8080/api/v9/projects?project_type={project_type}&status={status}"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get('success'):
            projects = result.get('data', [])
            return json.dumps({
                'success': True,
                'data': projects,
                'message': f"获取成功！找到 {len(projects)} 个项目"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '获取失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'获取项目列表失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def match_project_resources(
    token: str,
    project_id: int
) -> str:
    """
    为项目智能匹配资源
    
    Args:
        token: 用户访问令牌
        project_id: 项目ID
    
    Returns:
        JSON格式的匹配结果
    """
    try:
        url = f"http://localhost:8080/api/v9/projects/{project_id}/match"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, headers=headers)
        result = response.json()
        
        if result.get('success'):
            matches = result.get('data', [])
            return json.dumps({
                'success': True,
                'data': matches,
                'message': f"匹配成功！找到 {len(matches)} 个匹配资源"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '匹配失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'匹配资源失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def join_project(
    token: str,
    project_id: int,
    resource_id: int,
    role: str = "participant"
) -> str:
    """
    参与项目
    
    Args:
        token: 用户访问令牌
        project_id: 项目ID
        resource_id: 资源ID
        role: 角色（默认participant）
    
    Returns:
        JSON格式的参与结果
    """
    try:
        url = f"http://localhost:8080/api/v9/projects/{project_id}/join"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'resource_id': resource_id,
            'role': role
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get('success'):
            return json.dumps({
                'success': True,
                'message': "参与项目成功！"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '参与失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'参与项目失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def analyze_project_opportunity(project_data: str) -> str:
    """
    分析项目机会，提供参与建议
    
    Args:
        project_data: 项目数据（JSON格式字符串）
    
    Returns:
        JSON格式的分析结果
    """
    try:
        project = json.loads(project_data)
        
        analysis = {
            'project_title': project.get('title', ''),
            'project_type': project.get('project_type', ''),
            'budget': project.get('budget', 0),
            'recommendation': '',
            'key_factors': [],
            'suggested_skills': []
        }
        
        # 项目类型映射
        type_names = {
            'design': '设计项目',
            'development': '开发项目',
            'content': '内容创作项目',
            'consulting': '咨询服务项目',
            'marketing': '营销推广项目',
            'rental': '资产租赁项目'
        }
        
        analysis['project_type'] = type_names.get(analysis['project_type'], analysis['project_type'])
        
        # 分析预算
        budget = analysis['budget']
        if budget > 1000:
            analysis['key_factors'].append(f"项目预算较高({budget}灵值)，收益潜力大")
        elif budget > 500:
            analysis['key_factors'].append(f"项目预算适中({budget}灵值)")
        else:
            analysis['key_factors'].append(f"项目预算较低({budget}灵值)，适合练手")
        
        # 分析技能需求
        required_skills = project.get('required_skills', '').split(',')
        analysis['suggested_skills'] = [skill.strip() for skill in required_skills if skill.strip()]
        
        # 生成推荐
        if analysis['suggested_skills']:
            analysis['recommendation'] = f"这是一个{analysis['project_type']}，需要以下技能：{', '.join(analysis['suggested_skills'])}。建议查看你的资源库，匹配适合的技能资源。"
        else:
            analysis['recommendation'] = f"这是一个{analysis['project_type']}，建议联系项目发起人了解更多详情。"
        
        return json.dumps({
            'success': True,
            'data': analysis,
            'message': "项目分析完成！"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'分析项目失败: {str(e)}'
        }, ensure_ascii=False)
