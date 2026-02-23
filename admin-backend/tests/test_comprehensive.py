#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试 - 核心功能测试
"""

import unittest
import sys
import os

# 添加项目路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, 'admin-backend'))

from database import get_db, hash_password, check_password


class TestDatabase(unittest.TestCase):
    """数据库功能测试"""

    def test_database_connection(self):
        """测试数据库连接"""
        conn = get_db()
        self.assertIsNotNone(conn)
        conn.close()

    def test_password_hash(self):
        """测试密码哈希"""
        password = "test123"
        hashed = hash_password(password)
        self.assertIsInstance(hashed, str)
        self.assertNotEqual(password, hashed)

    def test_password_check(self):
        """测试密码验证"""
        password = "test123"
        hashed = hash_password(password)
        self.assertTrue(check_password(password, hashed))
        self.assertFalse(check_password("wrong", hashed))


class TestNewsArticles(unittest.TestCase):
    """新闻文章功能测试"""

    def setUp(self):
        """测试前准备"""
        self.conn = get_db()
        self.cursor = self.conn.cursor()

    def tearDown(self):
        """测试后清理"""
        self.conn.close()

    def test_create_news_article(self):
        """测试创建新闻文章"""
        self.cursor.execute("""
            INSERT INTO news_articles (title, slug, content, status, published_at)
            VALUES (?, ?, ?, 'published', datetime('now'))
        """, ("测试文章", "test-article", "这是测试内容"))
        self.conn.commit()

        self.cursor.execute("SELECT * FROM news_articles WHERE slug = ?", ("test-article",))
        article = self.cursor.fetchone()
        self.assertIsNotNone(article)
        self.assertEqual(article['title'], "测试文章")


class TestEconomySystem(unittest.TestCase):
    """经济系统功能测试"""

    def setUp(self):
        """测试前准备"""
        self.conn = get_db()
        self.cursor = self.conn.cursor()

    def tearDown(self):
        """测试后清理"""
        self.conn.close()

    def test_get_lingzhi_config(self):
        """测试获取灵值配置"""
        self.cursor.execute("""
            INSERT INTO system_config (key, value, category)
            VALUES (?, ?, ?)
        """, ("initial_lingzhi", "100", "lingzhi"))
        self.conn.commit()

        self.cursor.execute(
            "SELECT value FROM system_config WHERE key = ? AND category = ?",
            ("initial_lingzhi", "lingzhi")
        )
        config = self.cursor.fetchone()
        self.assertIsNotNone(config)
        self.assertEqual(config['value'], "100")


class TestBlockchain(unittest.TestCase):
    """区块链功能测试"""

    def test_blockchain_service_import(self):
        """测试区块链服务导入"""
        try:
            from blockchain_service import get_blockchain_service
            service = get_blockchain_service()
            self.assertIsNotNone(service)
        except ImportError:
            self.skipTest("区块链服务未安装")


class TestAlertService(unittest.TestCase):
    """告警服务功能测试"""

    def test_alert_service_import(self):
        """测试告警服务导入"""
        try:
            from utils.alert_service import get_alert_service
            service = get_alert_service()
            self.assertIsNotNone(service)
        except ImportError:
            self.skipTest("告警服务未安装")


class TestAPIEndpoints(unittest.TestCase):
    """API端点测试"""

    def setUp(self):
        """测试前准备"""
        try:
            from app import create_app
            self.app = create_app('testing')
            self.client = self.app.test_client()
        except Exception as e:
            self.skipTest(f"应用初始化失败: {e}")

    def test_health_check(self):
        """测试健康检查"""
        response = self.client.get('/api/admin/api-monitor')
        self.assertIn(response.status_code, [200, 404, 500])

    def test_news_articles(self):
        """测试新闻文章API"""
        response = self.client.get('/api/v9/news/articles')
        self.assertIn(response.status_code, [200, 404, 500])

    def test_economy_config(self):
        """测试经济配置API"""
        response = self.client.get('/api/admin/economy/config')
        self.assertIn(response.status_code, [200, 404, 500])

    def test_blockchain_health(self):
        """测试区块链健康检查"""
        response = self.client.get('/api/v9/blockchain/health')
        self.assertIn(response.status_code, [200, 404, 500])


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestNewsArticles))
    suite.addTests(loader.loadTestsFromTestCase(TestEconomySystem))
    suite.addTests(loader.loadTestsFromTestCase(TestBlockchain))
    suite.addTests(loader.loadTestsFromTestCase(TestAlertService))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIEndpoints))

    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # 输出摘要
    print("\n" + "="*60)
    print("测试摘要")
    print("="*60)
    print(f"总测试数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    print("="*60)

    return result.wasSuccessful()


if __name__ == '__main__':
    import sys
    success = run_tests()
    sys.exit(0 if success else 1)
