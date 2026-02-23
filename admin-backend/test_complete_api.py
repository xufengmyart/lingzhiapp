#!/usr/bin/env python
"""
测试完整的API功能
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_login(username, password):
    """测试登录并返回token"""
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            'username': username,
            'password': password
        },
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'data' in data and 'token' in data['data']:
            return data['data']['token'], data['data']['user']
    
    return None, None

def test_user_info(token):
    """测试获取用户信息"""
    response = requests.get(
        f"{BASE_URL}/api/user/info",
        headers={
            'Authorization': f'Bearer {token}'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            return data['data']['user']
    
    return None

def test_update_profile(token):
    """测试更新用户资料"""
    response = requests.put(
        f"{BASE_URL}/api/user/profile",
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={
            'email': 'updated@example.com'
        },
        timeout=5
    )
    
    return response.status_code == 200

if __name__ == '__main__':
    print("=" * 80)
    print("测试完整的API功能")
    print("=" * 80)
    
    # 测试用户
    test_cases = [
        {'username': 'admin', 'password': '123'},
        {'username': 'testuser', 'password': 'test123'},
        {'username': 'partner', 'password': 'partner123'}
    ]
    
    for test_case in test_cases:
        username = test_case['username']
        password = test_case['password']
        
        print(f"\n测试用户: {username}")
        print("-" * 80)
        
        # 测试登录
        print("1. 测试登录...")
        token, user = test_login(username, password)
        
        if not token:
            print(f"✗ 登录失败")
            continue
        
        print(f"✓ 登录成功")
        print(f"  用户ID: {user['id']}")
        print(f"  用户名: {user['username']}")
        print(f"  灵值: {user.get('totalLingzhi', 0)}")
        
        # 测试获取用户信息
        print("\n2. 测试获取用户信息...")
        user_info = test_user_info(token)
        
        if not user_info:
            print(f"✗ 获取用户信息失败")
            continue
        
        print(f"✓ 获取用户信息成功")
        print(f"  用户ID: {user_info['id']}")
        print(f"  邮箱: {user_info.get('email', 'N/A')}")
        print(f"  手机: {user_info.get('phone', 'N/A')}")
        print(f"  灵值: {user_info.get('totalLingzhi', 0)}")
        
        # 测试更新用户资料（仅testuser）
        if username == 'testuser':
            print("\n3. 测试更新用户资料...")
            if test_update_profile(token):
                print(f"✓ 更新用户资料成功")
            else:
                print(f"✗ 更新用户资料失败")
    
    # 测试错误登录
    print("\n" + "=" * 80)
    print("测试错误登录")
    print("=" * 80)
    
    print("\n测试: 错误密码")
    print("-" * 80)
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            'username': 'testuser',
            'password': 'wrongpassword'
        },
        timeout=5
    )
    
    if response.status_code == 401:
        print("✓ 错误密码登录正确被拒绝")
    else:
        print(f"✗ 错误密码登录未被正确拒绝 (状态码: {response.status_code})")
    
    print("\n测试: 不存在的用户")
    print("-" * 80)
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            'username': 'nonexistent',
            'password': 'test123'
        },
        timeout=5
    )
    
    if response.status_code == 401:
        print("✓ 不存在的用户登录正确被拒绝")
    else:
        print(f"✗ 不存在的用户登录未被正确拒绝 (状态码: {response.status_code})")
    
    print("\n" + "=" * 80)
    print("测试完成！")
    print("=" * 80)
