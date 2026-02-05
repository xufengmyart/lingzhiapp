"""
灵值智能体 v9.0 - 推荐分润系统工具
"""

from langchain.tools import tool
from typing import Optional, Dict, Any
import requests
import json


@tool
def get_user_referrals(token: str) -> str:
    """
    获取用户推荐列表和分润统计
    
    Args:
        token: 用户访问令牌
    
    Returns:
        JSON格式的推荐列表和分润统计
    """
    try:
        url = "http://localhost:8080/api/v9/referrals"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get('success'):
            return json.dumps({
                'success': True,
                'data': result.get('data', {}),
                'message': f"获取成功！你有 {result.get('data', {}).get('total_count', 0)} 个推荐，累计分润 {result.get('data', {}).get('total_commission', 0)} 灵值"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '获取失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'获取推荐列表失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def get_commission_records(token: str) -> str:
    """
    获取用户的分润记录
    
    Args:
        token: 用户访问令牌
    
    Returns:
        JSON格式的分润记录列表
    """
    try:
        url = "http://localhost:8080/api/v9/commissions"
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.get(url, headers=headers)
        result = response.json()
        
        if result.get('success'):
            return json.dumps({
                'success': True,
                'data': result.get('data', []),
                'message': f"获取到 {len(result.get('data', []))} 条分润记录"
            }, ensure_ascii=False)
        else:
            return json.dumps({
                'success': False,
                'message': result.get('message', '获取失败')
            }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'获取分润记录失败: {str(e)}'
        }, ensure_ascii=False)


@tool
def calculate_referral_benefit(referral_count: int, amount_per_referral: float = 100.0) -> str:
    """
    计算推荐收益（帮助用户了解推荐系统的价值）
    
    Args:
        referral_count: 推荐人数
        amount_per_referral: 每个推荐人的平均收益（默认100灵值）
    
    Returns:
        JSON格式的收益分析
    """
    try:
        # 一级推荐收益：5%
        level1_commission = amount_per_referral * 0.05 * referral_count
        
        # 假设50%的一级推荐人又会推荐新用户
        level2_count = int(referral_count * 0.5)
        level2_commission = amount_per_referral * 0.03 * level2_count
        
        # 假设30%的二级推荐人又会推荐新用户
        level3_count = int(level2_count * 0.3)
        level3_commission = amount_per_referral * 0.02 * level3_count
        
        total_commission = level1_commission + level2_commission + level3_commission
        
        return json.dumps({
            'success': True,
            'data': {
                'referral_count': referral_count,
                'level1_count': referral_count,
                'level1_commission': level1_commission,
                'level2_count': level2_count,
                'level2_commission': level2_commission,
                'level3_count': level3_count,
                'level3_commission': level3_commission,
                'total_commission': total_commission
            },
            'message': f"推荐{referral_count}人，预计可获得 {total_commission:.2f} 灵值的分润收益！"
        }, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            'success': False,
            'message': f'计算推荐收益失败: {str(e)}'
        }, ensure_ascii=False)
