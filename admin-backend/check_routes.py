#!/usr/bin/env python3
"""
检查Flask应用中的所有路由
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

try:
    from app import app

    print("=== Flask 路由检查 ===\n")

    # 获取所有路由
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'rule': str(rule),
            'methods': ','.join(rule.methods - {'HEAD', 'OPTIONS'}),
            'endpoint': rule.endpoint
        })

    # 按路径排序
    routes.sort(key=lambda x: x['rule'])

    # 查找特定路由
    target_routes = ['user', 'admin', 'culture', 'merchants']

    print("=== 目标路由 ===\n")
    for route_data in routes:
        rule = route_data['rule']
        methods = route_data['methods']
        endpoint = route_data['endpoint']

        # 检查是否包含目标关键词
        for target in target_routes:
            if target in rule.lower():
                print(f"{methods:10} {rule:50} [{endpoint}]")
                break

    print("\n=== 统计信息 ===")
    print(f"总路由数: {len(routes)}")

    # 统计各前缀的路由数量
    prefix_counts = {}
    for route_data in routes:
        rule = route_data['rule']
        # 提取一级路径前缀
        parts = rule.strip('/').split('/')
        if parts:
            prefix = parts[0]
            prefix_counts[prefix] = prefix_counts.get(prefix, 0) + 1

    print("\n各前缀路由数:")
    for prefix, count in sorted(prefix_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"  /{prefix}: {count}")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
