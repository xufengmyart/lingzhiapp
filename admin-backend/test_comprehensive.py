#!/usr/bin/env python
"""
综合测试脚本
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_projects():
    """测试项目列表接口"""
    print("=" * 80)
    print("测试项目列表接口")
    print("=" * 80)
    
    response = requests.get(f"{BASE_URL}/api/projects", timeout=5)
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ 接口返回成功")
            print(f"  返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
            
            # 检查数据格式
            if 'data' in data and isinstance(data['data'], list):
                print("✓ 数据格式正确（数组）")
                return True
            else:
                print("✗ 数据格式错误")
                return False
        else:
            print(f"✗ 接口返回失败: {data.get('error')}")
            return False
    else:
        print(f"✗ 接口请求失败: {response.status_code}")
        return False

def test_login():
    """测试登录功能"""
    print("\n" + "=" * 80)
    print("测试登录功能")
    print("=" * 80)
    
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={
            'username': 'testuser',
            'password': 'test123'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success') and 'data' in data:
            print("✓ 登录成功")
            token = data['data'].get('token')
            print(f"  Token: {token[:50]}...")
            return token
        else:
            print(f"✗ 登录失败: {data}")
            return None
    else:
        print(f"✗ 登录请求失败: {response.status_code}")
        return None

def test_change_password(token):
    """测试修改密码功能"""
    print("\n" + "=" * 80)
    print("测试修改密码功能")
    print("=" * 80)
    
    if not token:
        print("✗ 没有有效的token，跳过测试")
        return False
    
    # 修改密码
    response = requests.post(
        f"{BASE_URL}/api/user/change-password",
        headers={
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        },
        json={
            'oldPassword': 'test123',
            'newPassword': 'temp123'
        },
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ 密码修改成功")
            
            # 使用新密码登录
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    'username': 'testuser',
                    'password': 'temp123'
                },
                timeout=5
            )
            
            if response.status_code == 200:
                print("✓ 新密码登录成功")
                new_token = response.json()['data']['token']
                
                # 恢复原密码
                response = requests.post(
                    f"{BASE_URL}/api/user/change-password",
                    headers={
                        'Authorization': f'Bearer {new_token}',
                        'Content-Type': 'application/json'
                    },
                    json={
                        'oldPassword': 'temp123',
                        'newPassword': 'test123'
                    },
                    timeout=5
                )
                
                if response.status_code == 200:
                    print("✓ 密码恢复成功")
                    return True
                else:
                    print("✗ 密码恢复失败")
                    return False
            else:
                print("✗ 新密码登录失败")
                return False
        else:
            print(f"✗ 密码修改失败: {data}")
            return False
    else:
        print(f"✗ 密码修改请求失败: {response.status_code}")
        return False

if __name__ == '__main__':
    print("\n开始综合测试...\n")
    
    results = {
        'projects': test_projects(),
        'login': test_login() is not None,
        'change_password': test_change_password(test_login())
    }
    
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"项目列表: {'✓ 通过' if results['projects'] else '✗ 失败'}")
    print(f"登录功能: {'✓ 通过' if results['login'] else '✗ 失败'}")
    print(f"修改密码: {'✓ 通过' if results['change_password'] else '✗ 失败'}")
    
    all_passed = all(results.values())
    print("\n" + ("=" * 80))
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败！")
    print("=" * 80)
