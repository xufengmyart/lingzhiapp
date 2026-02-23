#!/usr/bin/env python
"""
测试用户活动API
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_user_activities():
    """测试用户活动API"""
    print("=" * 80)
    print("测试用户活动API")
    print("=" * 80)

    response = requests.get(
        f"{BASE_URL}/api/company/users/activities",
        timeout=5
    )

    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("✓ 获取用户活动成功")
            print(f"  总数: {data.get('total', 0)}")
            print(f"  返回数量: {len(data.get('data', []))}")
            print("\n活动列表:")
            print("-" * 80)

            for i, activity in enumerate(data.get('data', [])[:5], 1):
                print(f"{i}. 用户: {activity.get('username')}")
                print(f"   动作: {activity.get('action')}")
                print(f"   描述: {activity.get('description')}")
                print(f"   时间: {activity.get('created_at')}")
                print(f"   类型: {activity.get('type')}")
                print(f"   灵值: {activity.get('lingzhi')}")
                print()

            # 检查用户名是否已脱敏
            print("\n脱敏检查:")
            print("-" * 80)
            usernames = [a.get('username') for a in data.get('data', [])]
            has_sensitive = any('*' not in u for u in usernames if u and u != '管理员')
            has_masked = any('*' in u for u in usernames)

            if not has_sensitive and has_masked:
                print("✓ 所有用户名已正确脱敏")
            elif has_sensitive:
                print("✗ 发现未脱敏的用户名")
                for u in usernames:
                    if u and '*' not in u and u != '管理员':
                        print(f"  - {u}")
            else:
                print("⚠️  未检测到脱敏标记")

            # 检查字段名
            print("\n字段检查:")
            print("-" * 80)
            if data.get('data'):
                sample = data['data'][0]
                required_fields = ['username', 'action', 'description', 'type', 'created_at', 'lingzhi']
                missing_fields = [f for f in required_fields if f not in sample]
                if not missing_fields:
                    print("✓ 所有必需字段都存在")
                else:
                    print(f"✗ 缺少字段: {missing_fields}")

            return True
        else:
            print(f"✗ API返回失败: {data.get('message')}")
            return False
    else:
        print(f"✗ 请求失败: {response.status_code}")
        return False

if __name__ == '__main__':
    print("\n开始测试用户活动API...\n")

    success = test_user_activities()

    print("\n" + "=" * 80)
    if success:
        print("测试通过！")
    else:
        print("测试失败！")
    print("=" * 80)
