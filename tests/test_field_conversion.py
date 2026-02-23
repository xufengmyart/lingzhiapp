#!/usr/bin/env python3
"""
测试字段名转换功能
Test Field Name Conversion

验证snake_case到camelCase的转换是否正确
"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'admin-backend'))

try:
    from utils.response_utils import (
        snake_to_camel,
        camel_to_snake,
        transform_dict_keys
    )
    print("✅ response_utils模块导入成功\n")
except ImportError as e:
    print(f"❌ 无法导入response_utils模块: {e}")
    sys.exit(1)


def test_single_field_conversion():
    """测试单个字段名转换"""
    print("=" * 60)
    print("测试1: 单个字段名转换")
    print("=" * 60)

    test_cases = [
        ('agent_id', 'agentId'),
        ('conversation_id', 'conversationId'),
        ('total_lingzhi', 'totalLingzhi'),
        ('avatar_url', 'avatarUrl'),
        ('real_name', 'realName'),
        ('referee_id', 'refereeId'),
        ('created_at', 'createdAt'),
        ('updated_at', 'updatedAt'),
        ('user_name', 'userName'),
        ('phone_number', 'phoneNumber'),
    ]

    all_passed = True
    for snake, expected_camel in test_cases:
        result = snake_to_camel(snake)
        passed = result == expected_camel
        status = "✅" if passed else "❌"
        print(f"{status} {snake:20s} -> {result:20s} (期望: {expected_camel})")
        if not passed:
            all_passed = False

    print(f"\n结果: {'全部通过' if all_passed else '部分失败'}\n")
    return all_passed


def test_dict_conversion():
    """测试字典转换"""
    print("=" * 60)
    print("测试2: 字典转换")
    print("=" * 60)

    test_data = {
        'agent_id': 1,
        'conversation_id': 123,
        'total_lingzhi': 100,
        'avatar_url': 'https://example.com/avatar.jpg',
        'real_name': '张三',
        'referee_id': 456,
        'created_at': '2026-02-18T00:00:00Z',
    }

    print("\n原始数据 (snake_case):")
    for key, value in test_data.items():
        print(f"  {key:20s}: {value}")

    converted_data = transform_dict_keys(test_data, to_camel=True)

    print("\n转换后数据 (camelCase):")
    for key, value in converted_data.items():
        print(f"  {key:20s}: {value}")

    # 验证转换
    expected_keys = ['agentId', 'conversationId', 'totalLingzhi', 'avatarUrl',
                     'realName', 'refereeId', 'createdAt']
    actual_keys = list(converted_data.keys())

    all_correct = all(key in expected_keys for key in actual_keys)
    print(f"\n结果: {'✅ 转换正确' if all_correct else '❌ 转换错误'}\n")
    return all_correct


def test_nested_dict_conversion():
    """测试嵌套字典转换"""
    print("=" * 60)
    print("测试3: 嵌套字典转换")
    print("=" * 60)

    test_data = {
        'success': True,
        'data': {
            'user_id': 10,
            'user_name': 'admin',
            'avatar_url': 'https://example.com/avatar.jpg',
            'total_lingzhi': 100,
            'profile': {
                'real_name': '管理员',
                'bio': '系统管理员',
                'created_at': '2026-01-01T00:00:00Z'
            }
        }
    }

    print("\n原始嵌套数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))

    converted_data = transform_dict_keys(test_data, to_camel=True)

    print("\n转换后数据:")
    print(json.dumps(converted_data, indent=2, ensure_ascii=False))

    # 验证嵌套转换
    has_user_id = 'userId' in converted_data['data']
    has_real_name = 'realName' in converted_data['data']['profile']
    all_correct = has_user_id and has_real_name

    print(f"\n验证:")
    print(f"  {'✅' if has_user_id else '❌'} data.userId 存在")
    print(f"  {'✅' if has_real_name else '❌'} data.profile.realName 存在")
    print(f"\n结果: {'✅ 嵌套转换正确' if all_correct else '❌ 嵌套转换错误'}\n")
    return all_correct


def test_list_conversion():
    """测试列表转换"""
    print("=" * 60)
    print("测试4: 列表转换")
    print("=" * 60)

    test_data = {
        'success': True,
        'data': {
            'users': [
                {'user_id': 1, 'user_name': '用户1', 'total_lingzhi': 100},
                {'user_id': 2, 'user_name': '用户2', 'total_lingzhi': 200},
            ]
        }
    }

    print("\n原始列表数据:")
    print(json.dumps(test_data, indent=2, ensure_ascii=False))

    converted_data = transform_dict_keys(test_data, to_camel=True)

    print("\n转换后数据:")
    print(json.dumps(converted_data, indent=2, ensure_ascii=False))

    # 验证列表转换
    user1_correct = all(key in converted_data['data']['users'][0] for key in ['userId', 'userName', 'totalLingzhi'])
    user2_correct = all(key in converted_data['data']['users'][1] for key in ['userId', 'userName', 'totalLingzhi'])
    all_correct = user1_correct and user2_correct

    print(f"\n验证:")
    print(f"  {'✅' if user1_correct else '❌'} 用户1字段转换正确")
    print(f"  {'✅' if user2_correct else '❌'} 用户2字段转换正确")
    print(f"\n结果: {'✅ 列表转换正确' if all_correct else '❌ 列表转换错误'}\n")
    return all_correct


def test_api_response_conversion():
    """测试API响应转换"""
    print("=" * 60)
    print("测试5: API响应转换（实际场景）")
    print("=" * 60)

    # 模拟智能对话API响应
    api_response = {
        'success': True,
        'message': '对话成功',
        'data': {
            'agent_id': 1,
            'conversation_id': 'conv-123',
            'reply': '你好！我是灵值生态园的智能向导',
            'response': '你好！我是灵值生态园的智能向导',
            'message': '你好',
            'agent_info': {
                'agent_id': 1,
                'agent_name': '文化助手',
                'description': '帮助您了解中华文化',
                'avatar_url': '🎭',
                'status': 'active',
            }
        }
    }

    print("\n原始API响应:")
    print(json.dumps(api_response, indent=2, ensure_ascii=False))

    converted_response = transform_dict_keys(api_response, to_camel=True)

    print("\n转换后API响应:")
    print(json.dumps(converted_response, indent=2, ensure_ascii=False))

    # 验证API响应转换
    checks = [
        ('agentId' in converted_response['data'], 'data.agentId'),
        ('conversationId' in converted_response['data'], 'data.conversationId'),
        ('agentInfo' in converted_response['data'], 'data.agentInfo'),
        ('agentName' in converted_response['data']['agentInfo'], 'data.agentInfo.agentName'),
        ('avatarUrl' in converted_response['data']['agentInfo'], 'data.agentInfo.avatarUrl'),
    ]

    all_correct = all(check[0] for check in checks)

    print(f"\n验证:")
    for passed, desc in checks:
        print(f"  {'✅' if passed else '❌'} {desc} 存在")
    print(f"\n结果: {'✅ API响应转换正确' if all_correct else '❌ API响应转换错误'}\n")
    return all_correct


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("开始测试字段名转换功能")
    print("=" * 60 + "\n")

    # 导入json用于美化输出
    import json

    # 运行所有测试
    results = []
    results.append(("单个字段名转换", test_single_field_conversion()))
    results.append(("字典转换", test_dict_conversion()))
    results.append(("嵌套字典转换", test_nested_dict_conversion()))
    results.append(("列表转换", test_list_conversion()))
    results.append(("API响应转换", test_api_response_conversion()))

    # 汇总结果
    print("=" * 60)
    print("测试结果汇总")
    print("=" * 60)

    all_passed = True
    for test_name, passed in results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{status} - {test_name}")
        if not passed:
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅ 所有测试通过！")
    else:
        print("❌ 部分测试失败，请检查！")
    print("=" * 60 + "\n")

    sys.exit(0 if all_passed else 1)
