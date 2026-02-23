#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
灵值生态园 - 快速登录测试脚本
用途：测试用户登录功能
作者：Coze Coding
版本：v1.0
日期：2026-02-11
"""

import requests
import json

API_URL = "http://localhost:8080"
DEFAULT_PASSWORD = "123456"

# 核心用户（7个）
core_users = [
    {"id": 1, "username": "许锋", "role": "核心用户"},
    {"id": 2, "username": "CTO（待定）", "role": "技术负责人"},
    {"id": 3, "username": "CMO（待定）", "role": "市场负责人"},
    {"id": 4, "username": "COO（待定）", "role": "运营负责人"},
    {"id": 5, "username": "CFO（待定）", "role": "财务负责人"},
    {"id": 10, "username": "admin", "role": "管理员"},
    {"id": 201, "username": "17372200593", "role": "测试用户"},
]

def test_login(username, password):
    """测试登录"""
    try:
        payload = {
            "username": username,
            "password": password
        }
        
        response = requests.post(
            f"{API_URL}/api/login",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            if result.get("success"):
                return True, "登录成功"
            else:
                return False, result.get("message", "未知错误")
        else:
            return False, f"HTTP {response.status_code}: {response.text[:100]}"
            
    except requests.exceptions.ConnectionError:
        return False, "连接失败：无法连接到服务器"
    except Exception as e:
        return False, f"错误: {e}"

def main():
    print("=" * 70)
    print("灵值生态园 - 快速登录测试")
    print("=" * 70)
    print()
    print(f"API 地址: {API_URL}")
    print(f"默认密码: {DEFAULT_PASSWORD}")
    print(f"测试用户数: {len(core_users)}")
    print()
    
    # 测试所有核心用户
    results = []
    for user in core_users:
        username = user['username']
        role = user['role']
        
        print(f"测试 {role} (用户名: {username})...")
        success, message = test_login(username, DEFAULT_PASSWORD)
        results.append((username, role, success, message))
        
        status = "✅" if success else "❌"
        print(f"  {status} {message}")
        print()
    
    # 显示结果
    print("=" * 70)
    print("测试结果汇总")
    print("=" * 70)
    
    success_count = 0
    for username, role, success, message in results:
        status = "✅ 成功" if success else "❌ 失败"
        print(f"{role} ({username}): {status}")
        if success:
            success_count += 1
    
    total_count = len(results)
    print()
    print(f"总计: {success_count}/{total_count} 通过")
    
    if success_count == total_count:
        print()
        print("🎉 所有用户都可以使用新密码 123456 登录！")
    else:
        print()
        print("⚠️  部分用户无法登录，请检查")
    
    print()

if __name__ == '__main__':
    main()
