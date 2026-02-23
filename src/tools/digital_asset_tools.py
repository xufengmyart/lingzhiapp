"""
灵值智能体 v9.0 - 数字资产系统工具
"""

from langchain.tools import tool
from typing import Optional, Dict, Any
import requests
import json


@tool
def create_digital_asset(
    token: str,
    asset_type: str,
    asset_name: str,
    description: str = "",
    image_url: str = "",
    metadata: str = "{}",
    rarity: str = "common",
    value: float = 0.0
) -> str:
    """
    创建数字资产（NFT）
    
    Args:
        token: 用户访问令牌
        asset_type: 资产类型（membership:会员NFT, skill:技能NFT, achievement:成就NFT, resource:资源NFT, income:收益NFT）
        asset_name: 资产名称
        description: 资产描述
        image_url: 资产图片URL
        metadata: 元数据（JSON格式字符串）
        rarity: 稀有度（common:普通, rare:稀有, epic:史诗, legendary:传说）
        value: 资产价值
    
    Returns:
        JSON格式的创建结果
    """
    try:
        url = "http://localhost:8080/api/v9/assets"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'asset_type': asset_type,
            'asset_name': asset_name,
            'description': description,
            'image_url': image_url,
            'metadata': metadata,
            'rarity': rarity,
            'value': value
        }
        
        response = requests.post(url, headers=headers, json=data)
        result = response.json()
        
        if result.get('success'):
            return json.dumps({
                'success': True,
                'data': result.get('data', {}),
                'message': f"数字资产创建成功！资产ID: {result.get('data', {}).get('asset_id')}"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '创建失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'创建数字资产失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def get_user_assets(token: str) -> str:
    """
    获取用户的数字资产列表
    
    Args:
        token: 用户访问令牌
    
    Returns:
        JSON格式的资产列表
    """
    try:
        url = "http://localhost:8080/api/v9/assets"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get('success'):
            assets = result.get('data', [])
            return json.dumps({
                'success': True,
                'data': assets,
                'message': f"获取成功！你有 {len(assets)} 个数字资产"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '获取失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'获取数字资产失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def analyze_asset_portfolio(asset_list: str) -> str:
    """
    分析用户的数字资产组合
    
    Args:
        asset_list: 资产列表（JSON格式字符串）
    
    Returns:
        JSON格式的分析结果
    """
    try:
        assets = json.loads(asset_list)
        
        # 资产类型统计
        type_stats = {}
        rarity_stats = {}
        total_value = 0.0
        
        for asset in assets:
            atype = asset.get('asset_type', 'unknown')
            rarity = asset.get('rarity', 'common')
            
            type_stats[atype] = type_stats.get(atype, 0) + 1
            rarity_stats[rarity] = rarity_stats.get(rarity, 0) + 1
            total_value += asset.get('value', 0.0)
        
        # 资产类型映射
        type_names = {
            'membership': '会员NFT',
            'skill': '技能NFT',
            'achievement': '成就NFT',
            'resource': '资源NFT',
            'income': '收益NFT'
        }
        
        # 稀有度映射
        rarity_names = {
            'common': '普通',
            'rare': '稀有',
            'epic': '史诗',
            'legendary': '传说'
        }
        
        # 生成分析报告
        analysis = {
            'total_count': len(assets),
            'total_value': total_value,
            'type_distribution': [],
            'rarity_distribution': [],
            'suggestions': []
        }
        
        # 类型分布
        for atype, count in type_stats.items():
            type_name = type_names.get(atype, atype)
            analysis['type_distribution'].append({
                'type': type_name,
                'count': count,
                'percentage': round(count / len(assets) * 100, 2)
            })
        
        # 稀有度分布
        for rarity, count in rarity_stats.items():
            rarity_name = rarity_names.get(rarity, rarity)
            analysis['rarity_distribution'].append({
                'rarity': rarity_name,
                'count': count,
                'percentage': round(count / len(assets) * 100, 2)
            })
        
        # 生成建议
        if 'achievement' not in type_stats:
            analysis['suggestions'].append("建议参与项目获得成就NFT，提升信誉度")
        if 'income' not in type_stats:
            analysis['suggestions'].append("建议投资收益NFT，获得被动收入")
        if rarity_stats.get('legendary', 0) == 0:
            analysis['suggestions'].append("建议挑战高难度项目，获取传说级NFT")
        
        analysis['suggestions'].append(f"你的资产组合总价值约 {total_value:.2f} 灵值，建议合理配置资产")
        
        return json.dumps({
            'success': True,
            'data': analysis,
            'message': "资产分析完成！"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'分析资产失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def calculate_asset_return(investment: float, annual_return_rate: float, years: int = 1) -> str:
    """
    计算资产投资回报
    
    Args:
        investment: 投资金额
        annual_return_rate: 年化收益率（如0.15表示15%）
        years: 投资年限（默认1年）
    
    Returns:
        JSON格式的回报分析
    """
    try:
        # 计算复利
        final_value = investment * ((1 + annual_return_rate) ** years)
        total_return = final_value - investment
        return_percentage = round(total_return / investment * 100, 2)
        
        return json.dumps({
            'success': True,
            'data': {
                'investment': investment,
                'annual_return_rate': annual_return_rate,
                'years': years,
                'final_value': final_value,
                'total_return': total_return,
                'return_percentage': return_percentage
            },
            'message': f"投资{investment}灵值，{years}年后可获得{total_return:.2f}灵值的回报（总收益率{return_percentage:.2f}%）"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'计算回报失败: {str(e)}'
        }, ensure_ascii=False)
