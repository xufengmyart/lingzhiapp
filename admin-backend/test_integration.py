#!/usr/bin/env python3
"""
集成测试脚本 - 验证新闻和通知功能
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:5000/api/v9"

def print_test(test_name, passed, details=""):
    """打印测试结果"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status} - {test_name}")
    if details:
        print(f"   {details}")

def test_news_articles_api():
    """测试新闻文章API"""
    print("\n" + "="*60)
    print("测试新闻文章 API")
    print("="*60)
    
    # 获取文章列表
    try:
        response = requests.get(f"{BASE_URL}/news/articles", timeout=10)
        data = response.json()
        print_test("获取文章列表", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200:
            articles = data.get('data', [])
            print(f"   找到 {len(articles)} 篇文章")
            
            if articles:
                article = articles[0]
                print_test("文章包含必要字段", all(k in article for k in [
                    'id', 'title', 'slug', 'summary', 'publishedAt', 
                    'viewCount', 'likeCount', 'commentCount'
                ]))
                
                # 测试搜索功能
                search_response = requests.get(
                    f"{BASE_URL}/news/articles", 
                    params={'keyword': '灵值'}, 
                    timeout=10
                )
                print_test("文章搜索功能", search_response.status_code == 200)
                
                # 测试分类筛选
                if article.get('categoryId'):
                    category_response = requests.get(
                        f"{BASE_URL}/news/articles", 
                        params={'category_id': article['categoryId']}, 
                        timeout=10
                    )
                    print_test("文章分类筛选", category_response.status_code == 200)
                
                # 测试点赞功能
                like_response = requests.post(
                    f"{BASE_URL}/news/articles/{article['id']}/like",
                    timeout=10
                )
                print_test("文章点赞功能", like_response.status_code == 200)
                
                return article
    except Exception as e:
        print_test("获取文章列表", False, str(e))
        return None

def test_comments_api(article_id):
    """测试评论API"""
    if not article_id:
        print("\n" + "="*60)
        print("跳过评论测试（无有效文章ID）")
        print("="*60)
        return
    
    print("\n" + "="*60)
    print("测试评论 API")
    print("="*60)
    
    # 获取评论列表
    try:
        response = requests.get(
            f"{BASE_URL}/news/articles/{article_id}/comments",
            timeout=10
        )
        data = response.json()
        print_test("获取评论列表", response.status_code == 200 and data.get('success'))
        
        # 创建新评论
        test_comment = {
            "content": f"这是一条测试评论 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "author_name": "测试用户",
            "author_id": 1
        }
        
        create_response = requests.post(
            f"{BASE_URL}/news/articles/{article_id}/comments",
            json=test_comment,
            timeout=10
        )
        print_test("创建评论", create_response.status_code == 200)
        
        if create_response.status_code == 200:
            comment_id = create_response.json().get('data', {}).get('id')
            
            # 验证评论数量增加
            verify_response = requests.get(
                f"{BASE_URL}/news/articles",
                timeout=10
            )
            if verify_response.status_code == 200:
                articles = verify_response.json().get('data', [])
                target_article = next((a for a in articles if a['id'] == article_id), None)
                if target_article:
                    print_test("评论计数更新", target_article.get('commentCount', 0) > 0)
            
    except Exception as e:
        print_test("评论 API 测试失败", False, str(e))

def test_notifications_api():
    """测试通知API"""
    print("\n" + "="*60)
    print("测试通知 API")
    print("="*60)
    
    try:
        # 获取通知列表
        response = requests.get(
            f"{BASE_URL}/notifications",
            params={'user_id': 1},
            timeout=10
        )
        data = response.json()
        print_test("获取通知列表", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200:
            notifications = data.get('data', [])
            print(f"   找到 {len(notifications)} 条通知")
            
            # 获取未读数量
            unread_response = requests.get(
                f"{BASE_URL}/notifications/unread/count",
                params={'user_id': 1},
                timeout=10
            )
            print_test("获取未读通知数量", unread_response.status_code == 200)
            
            # 测试分类筛选
            if notifications:
                category_response = requests.get(
                    f"{BASE_URL}/notifications",
                    params={'user_id': 1, 'category': 'system'},
                    timeout=10
                )
                print_test("通知分类筛选", category_response.status_code == 200)
                
                # 测试批量标记已读
                read_all_response = requests.put(
                    f"{BASE_URL}/notifications/read-all",
                    json={'user_id': 1},
                    timeout=10
                )
                print_test("批量标记已读", read_all_response.status_code == 200)
            
            # 测试最新通知API（实时通知）
            latest_response = requests.get(
                f"{BASE_URL}/notifications/latest",
                params={'user_id': 1},
                timeout=10
            )
            print_test("获取最新通知（实时）", latest_response.status_code == 200)
            
    except Exception as e:
        print_test("通知 API 测试失败", False, str(e))

def test_categories_api():
    """测试分类API"""
    print("\n" + "="*60)
    print("测试分类 API")
    print("="*60)
    
    try:
        response = requests.get(f"{BASE_URL}/news/categories", timeout=10)
        data = response.json()
        print_test("获取文章分类", response.status_code == 200 and data.get('success'))
        
        if response.status_code == 200:
            categories = data.get('data', [])
            print(f"   找到 {len(categories)} 个分类")
            
            if categories:
                print_test("分类包含必要字段", all(k in categories[0] for k in [
                    'id', 'name', 'slug'
                ]))
    except Exception as e:
        print_test("获取分类失败", False, str(e))

def main():
    """主测试函数"""
    print("\n" + "="*60)
    print("🚀 开始集成测试")
    print("="*60)
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   API地址: {BASE_URL}")
    print("="*60)
    
    # 检查服务是否运行
    try:
        response = requests.get(f"{BASE_URL}/news/articles", timeout=5)
        print("\n✅ 后端服务运行正常")
    except requests.exceptions.ConnectionError:
        print("\n❌ 无法连接到后端服务")
        print("   请确保后端服务正在运行: cd admin-backend && python3 app.py")
        return
    
    # 运行所有测试
    article_id = test_news_articles_api()
    test_comments_api(article_id)
    test_notifications_api()
    test_categories_api()
    
    # 打印总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print("   所有核心功能测试完成")
    print("   如有失败，请查看具体错误信息")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
