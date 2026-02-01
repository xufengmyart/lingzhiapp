#!/usr/bin/env python3
"""
测试用户统计和用户动态 API
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8001"

def test_public_user_recent():
    """测试前台用户动态接口（无需认证）"""
    print("=" * 60)
    print("测试 1: 前台用户动态接口")
    print("=" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/public/users/recent?limit=10", timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 接口调用成功")
            print(f"  - success: {data.get('success')}")
            print(f"  - 用户数量: {len(data.get('data', []))}")
            if data.get('data'):
                print(f"  - 最新用户: {data['data'][0]}")
        else:
            print(f"✗ 接口调用失败: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print()

def test_admin_user_stats(admin_token):
    """测试管理后台用户统计接口（需要管理员认证）"""
    print("=" * 60)
    print("测试 2: 管理后台用户统计接口")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {admin_token}'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/stats/user?days=30", headers=headers, timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 接口调用成功")
            print(f"  - success: {data.get('success')}")
            if data.get('success'):
                stats = data.get('data', {})
                print(f"  - 用户状态分布:")
                for status, count in stats.get('userStatusDistribution', {}).items():
                    print(f"    • {status}: {count}")
                print(f"  - 今日统计:")
                today_stats = stats.get('todayStats', {})
                print(f"    • 新增用户: {today_stats.get('newUsers', 0)}")
                print(f"    • 活跃用户: {today_stats.get('activeUsers', 0)}")
                print(f"  - 每日新增数据点: {len(stats.get('dailyNewUsers', []))}")
        elif response.status_code == 401:
            print(f"✗ 认证失败（需要有效的管理员 token）")
        else:
            print(f"✗ 接口调用失败: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print()

def test_admin_users_recent(admin_token):
    """测试管理后台最近用户接口（需要管理员认证）"""
    print("=" * 60)
    print("测试 3: 管理后台最近用户接口")
    print("=" * 60)
    
    headers = {
        'Authorization': f'Bearer {admin_token}'
    }
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/users/recent?limit=5", headers=headers, timeout=5)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✓ 接口调用成功")
            print(f"  - success: {data.get('success')}")
            print(f"  - 用户数量: {len(data.get('data', []))}")
            if data.get('data'):
                print(f"  - 最新用户: {data['data'][0]}")
        elif response.status_code == 401:
            print(f"✗ 认证失败（需要有效的管理员 token）")
        else:
            print(f"✗ 接口调用失败: {response.text}")
    except Exception as e:
        print(f"✗ 请求异常: {e}")
    
    print()

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("用户统计和用户动态 API 测试")
    print("=" * 60)
    print()
    
    # 测试无需认证的接口
    test_public_user_recent()
    
    # 测试需要管理员认证的接口
    # 注意：需要先登录获取有效的 admin_token
    # 可以通过调用 POST /api/admin/login 获取
    admin_token = ""  # 替换为有效的管理员 token
    
    if admin_token:
        test_admin_user_stats(admin_token)
        test_admin_users_recent(admin_token)
    else:
        print("⚠️  跳过管理员接口测试（未提供 admin_token）")
        print("   如需测试管理员接口，请先调用 POST /api/admin/login 获取 token")
    
    print()
    print("=" * 60)
    print("测试完成")
    print("=" * 60)
