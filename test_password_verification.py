#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试密码验证逻辑"""

import sys
import os

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'admin-backend'))

from werkzeug.security import check_password_hash

def test_password_verification():
    """测试密码验证"""
    print("=== 测试密码验证逻辑 ===\n")

    # 测试scrypt格式的哈希
    test_hash = "scrypt:32768:8:1$byfHyATaHNfGNS1b$23a4cf12815534b2e2f779b4d4cc3a3370571f56599a09b0b73c4f9a6e7f5b3f"

    test_passwords = ["123", "123456", "admin"]

    print(f"测试哈希: {test_hash[:60]}...")
    print("\n测试密码验证:")

    for password in test_passwords:
        result = check_password_hash(test_hash, password)
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  密码 '{password}': {status}")

    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_password_verification()
