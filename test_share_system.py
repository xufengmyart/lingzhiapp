#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试分享系统和推荐关系管理功能
"""

import requests
import json
from datetime import datetime

# 配置
BASE_URL = "https://meiyueart.com"
USERNAME = "admin"
PASSWORD = "123"

# 测试结果
test_results = []

def log_test(test_name, success, message=""):
    """记录测试结果"""
    status = "✅ 成功" if success else "❌ 失败"
    test_results.append({
        "test": test_name,
        "status": status,
        "message": message,
        "timestamp": datetime.now().isoformat()
    })
    print(f"{status} - {test_name}")
    if message:
        print(f"  {message}")

def login():
    """登录获取token"""
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"username": USERNAME, "password": PASSWORD},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data['data']['token']
        return None
    except Exception as e:
        print(f"登录失败: {str(e)}")
        return None

def test_share_stats_table():
    """测试分享统计表是否存在"""
    import sqlite3
    try:
        conn = sqlite3.connect('/workspace/projects/admin-backend/data/lingzhi_ecosystem.db')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='share_stats'"
        )
        result = cursor.fetchone()
        
        if result:
            log_test("分享统计表检查", True, "share_stats 表已存在")
            
            # 查看表结构
            columns = cursor.execute("PRAGMA table_info(share_stats)").fetchall()
            print("  表结构:")
            for col in columns:
                print(f"    - {col[1]}: {col[2]}")
        else:
            log_test("分享统计表检查", False, "share_stats 表不存在")
        
        conn.close()
    except Exception as e:
        log_test("分享统计表检查", False, str(e))

def test_referral_management():
    """测试推荐关系管理接口"""
    token = login()
    if not token:
        log_test("推荐关系管理接口", False, "登录失败")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 测试获取所有推荐关系
        response = requests.get(
            f"{BASE_URL}/api/admin/referral/relationships",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                log_test("获取推荐关系", True, f"共找到 {data['data']['pagination']['total']} 条推荐关系")
            else:
                log_test("获取推荐关系", False, data.get('message', '未知错误'))
        else:
            log_test("获取推荐关系", False, f"HTTP {response.status_code}")
        
        # 测试获取分享统计摘要
        response = requests.get(
            f"{BASE_URL}/api/admin/share/summary",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                summary = data['data']['summary']
                log_test("获取分享统计摘要", True, 
                        f"总分享: {summary['total_shares']}, 总点击: {summary['total_clicks']}")
            else:
                log_test("获取分享统计摘要", False, data.get('message', '未知错误'))
        else:
            log_test("获取分享统计摘要", False, f"HTTP {response.status_code}")
        
    except Exception as e:
        log_test("推荐关系管理接口", False, str(e))

def test_share_article():
    """测试文章分享接口"""
    token = login()
    if not token:
        log_test("文章分享接口", False, "登录失败")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 测试获取分享信息
        response = requests.get(
            f"{BASE_URL}/api/articles/1/share?type=wechat",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                share_data = data['data']
                log_test("文章分享接口", True, 
                        f"分享链接: {share_data['share_url'][:50]}..., 推荐码: {share_data['referral_code']}")
            else:
                log_test("文章分享接口", False, data.get('message', '未知错误'))
        else:
            log_test("文章分享接口", False, f"HTTP {response.status_code}")
        
    except Exception as e:
        log_test("文章分享接口", False, str(e))

def test_article_approval_notification():
    """测试文章审核通知功能"""
    token = login()
    if not token:
        log_test("文章审核通知", False, "登录失败")
        return
    
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 创建一个测试文章
        create_response = requests.post(
            f"{BASE_URL}/admin/news/articles",
            headers=headers,
            json={
                "title": "测试审核通知",
                "content": "这是一个测试文章，用于验证审核通知功能",
                "author_id": 1,
                "category_id": 1,
                "summary": "测试文章",
                "status": "draft"
            }
        )
        
        if create_response.status_code == 200:
            article_data = create_response.json()
            if article_data.get('success'):
                article_id = article_data['data']['id']
                
                # 审核通过文章
                approve_response = requests.put(
                    f"{BASE_URL}/admin/news/articles/{article_id}/approve",
                    headers=headers
                )
                
                if approve_response.status_code == 200:
                    log_test("文章审核通知", True, f"文章 {article_id} 审核通过，已发送通知")
                else:
                    log_test("文章审核通知", False, f"审核失败: HTTP {approve_response.status_code}")
            else:
                log_test("文章审核通知", False, article_data.get('message', '创建文章失败'))
        else:
            log_test("文章审核通知", False, f"创建文章失败: HTTP {create_response.status_code}")
        
    except Exception as e:
        log_test("文章审核通知", False, str(e))

def main():
    """运行所有测试"""
    print("=" * 80)
    print("分享系统和推荐关系管理功能测试")
    print("=" * 80)
    print()
    
    # 运行测试
    test_share_stats_table()
    print()
    test_referral_management()
    print()
    test_share_article()
    print()
    test_article_approval_notification()
    
    # 输出测试结果汇总
    print()
    print("=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    passed = sum(1 for r in test_results if "成功" in r["status"])
    failed = sum(1 for r in test_results if "失败" in r["status"])
    
    print(f"总测试数: {len(test_results)}")
    print(f"通过: {passed}")
    print(f"失败: {failed}")
    
    print()
    print("详细结果:")
    for result in test_results:
        print(f"  {result['status']} - {result['test']}")
        if result['message']:
            print(f"    {result['message']}")
    
    # 保存测试结果到文件
    with open('/workspace/projects/test_share_system_results.json', 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)
    
    print()
    print(f"测试结果已保存到: /workspace/projects/test_share_system_results.json")

if __name__ == '__main__':
    main()
