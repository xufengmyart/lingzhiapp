#!/usr/bin/env python3
"""
API字段命名规范测试
API Field Naming Convention Test

测试所有API端点是否返回camelCase格式的字段名
"""

import requests
import json
import re
from typing import Dict, List, Any, Tuple


class FieldNamingTest:
    """字段命名测试类"""

    def __init__(self, base_url: str = "http://127.0.0.1:5000"):
        self.base_url = base_url
        self.results = []

    def is_camel_case(self, key: str) -> bool:
        """检查字段名是否为camelCase格式"""
        # 允许：小写字母开头，可以包含数字，其他部分可以是驼峰
        # 不允许：下划线、连续大写（除非是缩写）
        pattern = r'^[a-z][a-zA-Z0-9]*$'
        return bool(re.match(pattern, key))

    def is_snake_case(self, key: str) -> bool:
        """检查字段名是否为snake_case格式"""
        return '_' in key

    def check_dict_keys(self, data: Dict, path: str = "") -> List[Tuple[str, bool, str]]:
        """
        递归检查字典的所有键名

        返回: [(路径, 是否符合camelCase, 键名)]
        """
        issues = []

        if not isinstance(data, dict):
            return issues

        for key, value in data.items():
            current_path = f"{path}.{key}" if path else key

            # 检查键名是否符合camelCase规范
            is_camel = self.is_camel_case(key)
            is_snake = self.is_snake_case(key)

            if is_snake and not is_camel:
                issues.append((current_path, False, f"发现snake_case字段: {key}"))

            # 递归检查嵌套字典和列表
            if isinstance(value, dict):
                issues.extend(self.check_dict_keys(value, current_path))
            elif isinstance(value, list) and value and isinstance(value[0], dict):
                for idx, item in enumerate(value):
                    item_path = f"{current_path}[{idx}]"
                    issues.extend(self.check_dict_keys(item, item_path))

        return issues

    def test_api_endpoint(self, method: str, endpoint: str, data: Dict = None,
                         params: Dict = None, headers: Dict = None) -> Dict:
        """
        测试单个API端点

        返回: {
            'endpoint': 'API端点',
            'status_code': 200,
            'success': True,
            'issues': [],
            'response_data': {}
        }
        """
        url = f"{self.base_url}{endpoint}"

        try:
            if method.upper() == 'GET':
                response = requests.get(url, params=params, headers=headers, timeout=10)
            elif method.upper() == 'POST':
                response = requests.post(url, json=data, params=params, headers=headers, timeout=10)
            else:
                return {
                    'endpoint': endpoint,
                    'status_code': None,
                    'success': False,
                    'error': f"不支持的HTTP方法: {method}",
                    'issues': []
                }

            # 检查响应
            if response.status_code >= 400:
                return {
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'success': False,
                    'error': f"HTTP错误: {response.status_code}",
                    'issues': []
                }

            # 解析JSON
            try:
                response_data = response.json()
            except json.JSONDecodeError:
                return {
                    'endpoint': endpoint,
                    'status_code': response.status_code,
                    'success': False,
                    'error': "响应不是有效的JSON",
                    'issues': []
                }

            # 检查字段命名
            issues = self.check_dict_keys(response_data)

            return {
                'endpoint': endpoint,
                'status_code': response.status_code,
                'success': True,
                'issues': issues,
                'response_data': response_data
            }

        except requests.exceptions.RequestException as e:
            return {
                'endpoint': endpoint,
                'status_code': None,
                'success': False,
                'error': f"请求失败: {str(e)}",
                'issues': []
            }

    def run_all_tests(self) -> bool:
        """运行所有API测试"""
        print("\n" + "=" * 80)
        print("开始API字段命名规范测试")
        print("=" * 80 + "\n")

        # 定义要测试的API端点
        test_cases = [
            # 认证相关
            ('POST', '/login', {'username': 'admin', 'password': '123456'}),

            # 用户信息
            ('GET', '/user/info', None, None, {'Authorization': 'Bearer test-token'}),

            # 签到相关
            ('GET', '/checkin/status', None, None, {'Authorization': 'Bearer test-token'}),
            ('POST', '/checkin', None, None, {'Authorization': 'Bearer test-token'}),

            # 智能对话
            ('POST', '/agent/chat', {'message': 'test', 'agentId': 1}),

            # 智能体列表
            ('GET', '/admin/agents', None, None, {'Authorization': 'Bearer test-token'}),
        ]

        all_passed = True
        total_issues = 0

        for test_case in test_cases:
            method = test_case[0]
            endpoint = test_case[1]
            data = test_case[2] if len(test_case) > 2 else None
            params = test_case[3] if len(test_case) > 3 else None
            headers = test_case[4] if len(test_case) > 4 else None

            print(f"测试: {method} {endpoint}")

            result = self.test_api_endpoint(method, endpoint, data, params, headers)
            self.results.append(result)

            if result['success']:
                if result['issues']:
                    print(f"  ❌ 发现 {len(result['issues'])} 个问题")
                    for issue in result['issues']:
                        print(f"     - {issue[2]}")
                    all_passed = False
                    total_issues += len(result['issues'])
                else:
                    print(f"  ✅ 所有字段符合camelCase规范")
            else:
                print(f"  ⚠️  测试失败: {result.get('error', '未知错误')}")

            print()

        # 汇总结果
        print("=" * 80)
        print("测试结果汇总")
        print("=" * 80)

        passed_count = sum(1 for r in self.results if r['success'] and not r['issues'])
        failed_count = sum(1 for r in self.results if r['success'] and r['issues'])
        error_count = sum(1 for r in self.results if not r['success'])

        print(f"✅ 通过: {passed_count}")
        print(f"❌ 失败: {failed_count}")
        print(f"⚠️  错误: {error_count}")
        print(f"📊 总问题数: {total_issues}")

        if all_passed and total_issues == 0:
            print("\n✅ 所有API端点字段命名规范正确！")
        else:
            print("\n❌ 部分API端点存在字段命名问题！")

        print("=" * 80 + "\n")

        return all_passed and total_issues == 0

    def print_detailed_report(self):
        """打印详细的测试报告"""
        print("\n" + "=" * 80)
        print("详细测试报告")
        print("=" * 80 + "\n")

        for result in self.results:
            print(f"端点: {result['endpoint']}")
            print(f"状态码: {result['status_code']}")

            if result['success']:
                print(f"状态: ✅ 成功")

                if result['issues']:
                    print(f"问题数量: {len(result['issues'])}")
                    print("\n问题列表:")
                    for issue in result['issues']:
                        print(f"  - {issue[2]}")
                else:
                    print("问题数量: 0")

                # 显示响应数据结构（前3层）
                print("\n响应数据结构:")
                self.print_data_structure(result['response_data'], max_depth=3)
            else:
                print(f"状态: ❌ 失败")
                print(f"错误: {result.get('error', '未知错误')}")

            print("-" * 80 + "\n")

    def print_data_structure(self, data, depth=0, max_depth=3):
        """打印数据结构"""
        indent = "  " * depth

        if depth > max_depth:
            print(f"{indent}...")
            return

        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    print(f"{indent}{key}:")
                    self.print_data_structure(value, depth + 1, max_depth)
                else:
                    print(f"{indent}{key}: {type(value).__name__}")
        elif isinstance(data, list) and data:
            print(f"{indent}[列表, 长度={len(data)}]")
            if isinstance(data[0], dict):
                self.print_data_structure(data[0], depth + 1, max_depth)
        else:
            print(f"{indent}{type(data).__name__}")


if __name__ == '__main__':
    import sys

    # 检查是否提供了base_url参数
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:5000"

    print(f"测试目标: {base_url}\n")

    tester = FieldNamingTest(base_url)

    # 运行测试
    all_passed = tester.run_all_tests()

    # 打印详细报告
    tester.print_detailed_report()

    sys.exit(0 if all_passed else 1)
