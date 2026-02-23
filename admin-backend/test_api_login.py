#!/usr/bin/env python
"""
测试API登录功能
"""
import sys
sys.path.append('admin-backend')

import requests
import json

BASE_URL = "http://localhost:5000"

def test_login():
    """测试登录功能"""
    print("=" * 80)
    print("测试登录功能")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        {
            'name': '正确密码登录',
            'username': 'testuser',
            'password': 'test123',
            'expected_status': 200
        },
        {
            'name': '错误密码登录',
            'username': 'testuser',
            'password': 'wrong123',
            'expected_status': 401
        },
        {
            'name': 'admin登录',
            'username': 'admin',
            'password': '123',
            'expected_status': 200
        },
        {
            'name': '不存在的用户登录',
            'username': 'nonexistent',
            'password': 'test123',
            'expected_status': 401
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试: {test_case['name']}")
        print("-" * 80)
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/comprehensive/auth/login",
                json={
                    'username': test_case['username'],
                    'password': test_case['password']
                },
                timeout=5
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == test_case['expected_status']:
                print(f"✓ 测试通过")
                
                # 如果登录成功，显示返回的数据
                if response.status_code == 200:
                    data = response.json()
                    print(f"返回数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
                    
                    # 测试token是否有效
                    if 'data' in data and 'token' in data['data']:
                        token = data['data']['token']
                        print(f"\nToken (前50字符): {token[:50]}...")
                        
                        # 测试获取用户信息
                        print("\n测试获取用户信息...")
                        user_response = requests.get(
                            f"{BASE_URL}/api/comprehensive/user/info",
                            headers={
                                'Authorization': f'Bearer {token}'
                            },
                            timeout=5
                        )
                        
                        print(f"用户信息状态码: {user_response.status_code}")
                        if user_response.status_code == 200:
                            print("✓ Token验证成功")
                            user_data = user_response.json()
                            print(f"用户信息: {json.dumps(user_data, indent=2, ensure_ascii=False)}")
                        else:
                            print(f"✗ Token验证失败: {user_response.text}")
            else:
                print(f"✗ 测试失败: 期望状态码 {test_case['expected_status']}, 实际得到 {response.status_code}")
                print(f"响应内容: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print(f"✗ 无法连接到服务器，请确保后端服务正在运行")
            print(f"提示: 运行 'cd admin-backend && python app.py' 启动服务")
            return False
        except Exception as e:
            print(f"✗ 测试失败: {e}")
            return False
    
    return True

if __name__ == '__main__':
    print("\n开始测试API登录功能...\n")
    
    success = test_login()
    
    print("\n" + "=" * 80)
    if success:
        print("测试完成！")
    else:
        print("测试失败！")
    print("=" * 80)
