#!/usr/bin/env python3
"""
测试签到功能
验证签到后灵值是否实时更新
"""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8080"

def login(username="admin", password="admin123"):
    """登录获取token"""
    print("\n" + "="*50)
    print("1. 登录系统")
    print("="*50)

    response = requests.post(
        f"{BASE_URL}/api/login",
        json={"username": username, "password": password}
    )
    data = response.json()

    if data.get("success"):
        token = data["data"]["token"]
        user_info = data["data"]["user"]
        print(f"✓ 登录成功")
        print(f"  用户名: {user_info['username']}")
        print(f"  灵值: {user_info['totalLingzhi']}")
        return token, user_info
    else:
        print(f"✗ 登录失败: {data.get('message')}")
        return None, None

def get_user_info(token):
    """获取用户信息"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/user/info", headers=headers)
    data = response.json()
    if data.get("success"):
        return data["data"]
    return None

def get_checkin_status(token):
    """获取签到状态"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/api/checkin/status", headers=headers)
    data = response.json()
    if data.get("success"):
        return data["data"]
    return None

def check_in(token):
    """签到"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(f"{BASE_URL}/api/checkin", headers=headers)
    return response.json()

def main():
    print("\n" + "🔍 灵值生态园 - 签到功能测试".center(50))
    print("="*50)

    # 登录
    token, user_info = login()
    if not token:
        return

    # 获取初始灵值
    print("\n" + "="*50)
    print("2. 获取初始灵值")
    print("="*50)
    initial_lingzhi = user_info["totalLingzhi"]
    print(f"初始灵值: {initial_lingzhi}")

    # 获取签到状态
    print("\n" + "="*50)
    print("3. 检查签到状态")
    print("="*50)
    status = get_checkin_status(token)
    if status:
        print(f"是否已签到: {status.get('checkedIn', False)}")
        print(f"今日签到灵值: {status.get('lingzhi', 0)}")

        if status.get("checkedIn"):
            print("\n⚠️  今天已经签到过了，无法重复签到")
            print("提示：可以删除数据库中的签到记录重新测试")
            return

    # 签到
    print("\n" + "="*50)
    print("4. 执行签到")
    print("="*50)
    result = check_in(token)
    if result.get("success"):
        print(f"✓ 签到成功")
        print(f"  获得灵值: {result['data']['lingzhi']}")
    else:
        print(f"✗ 签到失败: {result.get('message')}")
        return

    # 获取签到后灵值
    print("\n" + "="*50)
    print("5. 获取签到后灵值")
    print("="*50)
    time.sleep(0.5)  # 等待一下确保数据更新
    new_user_info = get_user_info(token)
    if new_user_info:
        new_lingzhi = new_user_info["totalLingzhi"]
        print(f"签到后灵值: {new_lingzhi}")
        diff = new_lingzhi - initial_lingzhi
        print(f"灵值变化: +{diff}")

        if diff == 10:
            print("\n✅ 测试通过：签到后灵值正确更新")
        else:
            print(f"\n❌ 测试失败：预期增加10，实际增加{diff}")
    else:
        print("✗ 获取用户信息失败")

    # 再次检查签到状态
    print("\n" + "="*50)
    print("6. 检查签到状态")
    print("="*50)
    status = get_checkin_status(token)
    if status:
        print(f"是否已签到: {status.get('checkedIn', False)}")
        print(f"今日签到灵值: {status.get('lingzhi', 0)}")

        if status.get("checkedIn"):
            print("✅ 签到状态正确更新")
        else:
            print("❌ 签到状态未更新")

    print("\n" + "="*50)
    print("测试完成")
    print("="*50 + "\n")

if __name__ == "__main__":
    main()
