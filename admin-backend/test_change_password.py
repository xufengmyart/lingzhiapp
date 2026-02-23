#!/usr/bin/env python
"""
测试修改密码功能
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def login(username, password):
    """登录并返回token"""
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
            return data['data']['token']
    
    return None

def test_user_change_password():
    """测试用户修改密码"""
    print("=" * 80)
    print("测试用户修改密码功能")
    print("=" * 80)
    
    # 1. 登录获取token
    print("\n1. 登录获取token...")
    token = login('testuser', 'test123')
    
    if not token:
        print("✗ 登录失败")
        return False
    
    print("✓ 登录成功")
    
    # 2. 修改密码
    print("\n2. 修改密码 (test123 -> newpassword123)...")
    response = requests.post(
        f"{BASE_URL}/api/user/change-password",
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={
            'oldPassword': 'test123',
            'newPassword': 'newpassword123'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ 密码修改成功")
        else:
            print(f"✗ 密码修改失败: {data.get('message')}")
            return False
    else:
        print(f"✗ 密码修改失败: {response.status_code}")
        return False
    
    # 3. 使用旧密码登录（应该失败）
    print("\n3. 使用旧密码登录 (应该失败)...")
    old_token = login('testuser', 'test123')
    
    if old_token:
        print("✗ 旧密码仍然可以登录（错误）")
        return False
    else:
        print("✓ 旧密码无法登录（正确）")
    
    # 4. 使用新密码登录（应该成功）
    print("\n4. 使用新密码登录 (应该成功)...")
    new_token = login('testuser', 'newpassword123')
    
    if not new_token:
        print("✗ 新密码无法登录（错误）")
        return False
    else:
        print("✓ 新密码登录成功")
    
    # 5. 恢复原密码
    print("\n5. 恢复原密码...")
    response = requests.post(
        f"{BASE_URL}/api/user/change-password",
        headers={
            'Authorization': f'Bearer {new_token}',
            'Content-Type': 'application/json'
        },
        json={
            'oldPassword': 'newpassword123',
            'newPassword': 'test123'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ 密码恢复成功")
        else:
            print(f"⚠️  密码恢复失败: {data.get('message')}")
    
    # 6. 测试错误场景
    print("\n6. 测试错误场景...")
    
    # 6.1 新密码太短
    print("  6.1 新密码太短...")
    response = requests.post(
        f"{BASE_URL}/api/user/change-password",
        headers={
            'Authorization': f'Bearer {new_token}',
            'Content-Type': 'application/json'
        },
        json={
            'oldPassword': 'test123',
            'newPassword': '123'
        },
        timeout=5
    )
    
    if response.status_code == 400:
        print("  ✓ 新密码太短被正确拒绝")
    else:
        print("  ✗ 新密码太短未被正确拒绝")
    
    # 6.2 旧密码错误
    print("  6.2 旧密码错误...")
    response = requests.post(
        f"{BASE_URL}/api/user/change-password",
        headers={
            'Authorization': f'Bearer {new_token}',
            'Content-Type': 'application/json'
        },
        json={
            'oldPassword': 'wrongpassword',
            'newPassword': 'newpassword123'
        },
        timeout=5
    )
    
    if response.status_code == 400:
        print("  ✓ 旧密码错误被正确拒绝")
    else:
        print("  ✗ 旧密码错误未被正确拒绝")
    
    return True

if __name__ == '__main__':
    print("\n开始测试修改密码功能...\n")
    
    success = test_user_change_password()
    
    print("\n" + "=" * 80)
    if success:
        print("所有测试通过！")
    else:
        print("部分测试失败！")
    print("=" * 80)
