#!/usr/bin/env python3
"""
测试文化转译功能
"""

import sys
import os
import requests

# API 基础URL
BASE_URL = "http://localhost:5000"

def test_get_projects():
    """测试获取转译项目列表"""
    print("\n📋 测试1: 获取转译项目列表")
    try:
        response = requests.get(f"{BASE_URL}/api/culture/translation/projects")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功获取 {data.get('count', 0)} 个项目")
            for project in data.get('data', [])[:2]:
                title = project.get('title', '未知')
                code = project.get('project_code', '未知')
                print(f"      - {title} ({code})")
            return True
        else:
            print(f"   ❌ 失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_get_project_detail():
    """测试获取项目详情"""
    print("\n📋 测试2: 获取项目详情")
    try:
        response = requests.get(f"{BASE_URL}/api/culture/translation/projects/aesthetic_detective")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功获取项目: {data['data']['title']}")
            print(f"      描述: {data['data']['description'][:50]}...")
            return True
        else:
            print(f"   ❌ 失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_get_tasks():
    """测试获取转译任务列表"""
    print("\n📋 测试3: 获取转译任务列表")
    try:
        response = requests.get(f"{BASE_URL}/api/culture/translation/tasks")
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功获取 {data['pagination']['total']} 个任务")
            return True
        else:
            print(f"   ❌ 失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_start_translation():
    """测试开始转译（需要登录）"""
    print("\n📋 测试4: 开始转译（需要登录）")
    try:
        # 先获取第一个可用的任务ID
        tasks_response = requests.get(f"{BASE_URL}/api/culture/translation/tasks")
        if tasks_response.status_code == 200:
            tasks_data = tasks_response.json()
            if tasks_data.get('data') and len(tasks_data['data']) > 0:
                task_id = tasks_data['data'][0]['id']
            else:
                print("   ❌ 没有可用的任务")
                return False, None
        else:
            print(f"   ❌ 获取任务列表失败")
            return False, None

        response = requests.post(
            f"{BASE_URL}/api/culture/translation/start",
            json={"task_id": task_id, "original_content": "测试原始内容"},
            headers={"Authorization": "Bearer 1"}  # 使用用户ID=1
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功创建转译作品")
            work_id = data.get('data', {}).get('workId', None)
            if work_id:
                print(f"      作品ID: {work_id}")
            else:
                print(f"      ⚠️  未返回workId")
            return True, work_id
        else:
            print(f"   ❌ 失败: {response.text}")
            return False, None
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False, None

def test_start_translation_process(work_id):
    """测试开始转译流程（需要登录）"""
    print(f"\n📋 测试5: 开始转译流程 (workId={work_id})")
    try:
        response = requests.post(
            f"{BASE_URL}/api/culture/translation/process/start",
            json={"work_id": work_id, "use_ai_assist": False},
            headers={"Authorization": "Bearer 1"}  # 使用用户ID=1
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功启动转译流程")
            status = data.get('data', {}).get('status', '未知')
            print(f"      流程状态: {status}")
            return True
        else:
            print(f"   ❌ 失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def test_get_works():
    """测试获取转译作品列表（需要登录）"""
    print("\n📋 测试6: 获取转译作品列表")
    try:
        response = requests.get(
            f"{BASE_URL}/api/culture/translation/works",
            headers={"Authorization": "Bearer 1"}
        )
        print(f"   状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 成功获取 {data['pagination']['total']} 个作品")
            return True
        else:
            print(f"   ❌ 失败: {response.text}")
            return False
    except Exception as e:
        print(f"   ❌ 异常: {e}")
        return False

def main():
    print("="*60)
    print("🧪 文化转译功能测试")
    print("="*60)

    results = []

    # 运行测试
    results.append(("获取项目列表", test_get_projects()))
    results.append(("获取项目详情", test_get_project_detail()))
    results.append(("获取任务列表", test_get_tasks()))

    # 需要登录的测试
    start_result, work_id = test_start_translation()
    results.append(("开始转译", start_result))

    if work_id:
        results.append(("开始转译流程", test_start_translation_process(work_id)))
        results.append(("获取作品列表", test_get_works()))
    else:
        results.append(("开始转译流程", False))
        results.append(("获取作品列表", False))

    # 打印总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)

    success_count = sum(1 for _, result in results if result)
    total_count = len(results)

    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {status} - {test_name}")

    print(f"\n总计: {success_count}/{total_count} 个测试通过")

    if success_count == total_count:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠️  {total_count - success_count} 个测试失败")

    return success_count == total_count

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
