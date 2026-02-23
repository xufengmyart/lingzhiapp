#!/usr/bin/env python
"""
测试用户活动功能的完整性
"""
import requests
import json

BASE_URL = "http://localhost:5000"

def test_user_activities_api():
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
            print("✓ API返回成功")
            print(f"  总数: {data.get('total', 0)}")
            print(f"  返回数量: {len(data.get('data', []))}")

            activities = data.get('data', [])

            # 检查用户名脱敏
            print("\n检查用户名脱敏:")
            print("-" * 80)
            all_masked = True
            for activity in activities[:10]:
                username = activity.get('username', '')
                has_mask = '*' in username
                is_admin = username == '管理员'
                is_empty = not username

                if has_mask or is_admin or is_empty:
                    print(f"✓ {username}")
                else:
                    print(f"✗ {username} (未脱敏)")
                    all_masked = False

            if all_masked:
                print("\n✓ 所有用户名都已正确脱敏")
            else:
                print("\n✗ 发现未脱敏的用户名")

            # 检查字段完整性
            print("\n检查字段完整性:")
            print("-" * 80)
            required_fields = ['id', 'username', 'action', 'description', 'type', 'createdAt', 'lingzhi']
            if activities:
                sample = activities[0]
                missing = [f for f in required_fields if f not in sample]
                if missing:
                    print(f"✗ 缺少字段: {missing}")
                    return False
                else:
                    print("✓ 所有必需字段都存在")
            else:
                print("⚠️  没有活动数据")

            # 显示前5条数据
            print("\n前5条活动数据:")
            print("-" * 80)
            for i, activity in enumerate(activities[:5], 1):
                print(f"{i}. {activity.get('username')} - {activity.get('action')}")
                print(f"   {activity.get('description')}")
                print(f"   时间: {activity.get('createdAt')}")
                print(f"   类型: {activity.get('type')}, 灵值: {activity.get('lingzhi')}")
                print()

            return True
        else:
            print(f"✗ API返回失败: {data.get('message')}")
            return False
    else:
        print(f"✗ 请求失败: {response.status_code}")
        return False

def check_privacy():
    """检查隐私保护"""
    print("\n" + "=" * 80)
    print("检查隐私保护")
    print("=" * 80)

    response = requests.get(
        f"{BASE_URL}/api/company/users/activities",
        timeout=5
    )

    if response.status_code == 200:
        data = response.json()
        activities = data.get('data', [])

        # 检查没有返回敏感信息
        print("\n敏感信息检查:")
        print("-" * 80)

        sensitive_fields = ['email', 'phone', 'password', 'password_hash', 'real_name', 'id_number']
        has_sensitive = False

        for activity in activities:
            for field in sensitive_fields:
                if field in activity and activity[field]:
                    print(f"✗ 发现敏感字段: {field}")
                    has_sensitive = True

        if not has_sensitive:
            print("✓ 没有返回敏感信息")

        # 检查用户名长度（脱敏后应该很短）
        print("\n用户名长度检查:")
        print("-" * 80)

        long_usernames = []
        for activity in activities:
            username = activity.get('username', '')
            if username and len(username) > 5 and username != '管理员':
                long_usernames.append(username)

        if long_usernames:
            print(f"✗ 发现长用户名: {long_usernames[:5]}")
            return False
        else:
            print("✓ 用户名长度合理（已脱敏）")

        return True
    else:
        print(f"✗ 请求失败: {response.status_code}")
        return False

if __name__ == '__main__':
    print("\n开始测试用户活动功能...\n")

    test1 = test_user_activities_api()
    test2 = check_privacy()

    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"API功能: {'✓ 通过' if test1 else '✗ 失败'}")
    print(f"隐私保护: {'✓ 通过' if test2 else '✗ 失败'}")

    all_passed = test1 and test2
    print("\n" + "=" * 80)
    if all_passed:
        print("所有测试通过！")
    else:
        print("部分测试失败！")
    print("=" * 80)
