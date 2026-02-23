#!/usr/bin/env python
"""
测试认证功能
"""
import sys
sys.path.append('admin-backend')

import bcrypt
import jwt
from datetime import datetime, timedelta
from config import config

def test_bcrypt():
    """测试bcrypt密码加密和验证"""
    print("=" * 50)
    print("测试bcrypt密码加密和验证")
    print("=" * 50)
    
    # 测试密码加密
    password = "test123"
    password_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    
    print(f"原始密码: {password}")
    print(f"加密后的密码: {hashed}")
    
    # 测试正确密码验证
    try:
        check_result = bcrypt.checkpw(password_bytes, hashed)
        print(f"正确密码验证结果: {check_result}")
        assert check_result == True, "正确密码验证失败"
    except Exception as e:
        print(f"正确密码验证失败: {e}")
        return False
    
    # 测试错误密码验证
    wrong_password = "wrong123"
    wrong_password_bytes = wrong_password.encode('utf-8')
    try:
        check_result = bcrypt.checkpw(wrong_password_bytes, hashed)
        print(f"错误密码验证结果: {check_result}")
        assert check_result == False, "错误密码应该验证失败"
    except Exception as e:
        print(f"错误密码验证失败: {e}")
        return False
    
    print("✓ bcrypt测试通过")
    print()
    return True

def test_jwt():
    """测试JWT令牌生成和验证"""
    print("=" * 50)
    print("测试JWT令牌生成和验证")
    print("=" * 50)
    
    # 测试令牌生成
    user_id = 1
    username = "testuser"
    
    try:
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() + timedelta(seconds=config.JWT_EXPIRATION),
            'iat': datetime.utcnow()
        }
        token = jwt.encode(payload, config.JWT_SECRET_KEY, algorithm='HS256')
        
        print(f"生成的令牌: {token[:50]}...")
        print(f"令牌过期时间: {config.JWT_EXPIRATION}秒")
    except Exception as e:
        print(f"令牌生成失败: {e}")
        return False
    
    # 测试令牌验证
    try:
        decoded = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        print(f"解码后的令牌: {decoded}")
        assert decoded['user_id'] == user_id, "用户ID不匹配"
        assert decoded['username'] == username, "用户名不匹配"
    except Exception as e:
        print(f"令牌验证失败: {e}")
        return False
    
    # 测试过期令牌
    try:
        expired_payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow() - timedelta(seconds=1),  # 已过期
            'iat': datetime.utcnow()
        }
        expired_token = jwt.encode(expired_payload, config.JWT_SECRET_KEY, algorithm='HS256')
        decoded = jwt.decode(expired_token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        print("错误: 过期令牌应该验证失败")
        return False
    except jwt.ExpiredSignatureError:
        print("✓ 过期令牌正确地被拒绝")
    except Exception as e:
        print(f"过期令牌验证失败: {e}")
        return False
    
    print("✓ JWT测试通过")
    print()
    return True

if __name__ == '__main__':
    print("\n开始测试认证功能...\n")
    
    bcrypt_test = test_bcrypt()
    jwt_test = test_jwt()
    
    print("=" * 50)
    print("测试总结")
    print("=" * 50)
    print(f"bcrypt测试: {'通过 ✓' if bcrypt_test else '失败 ✗'}")
    print(f"JWT测试: {'通过 ✓' if jwt_test else '失败 ✗'}")
    print()
    
    if bcrypt_test and jwt_test:
        print("所有测试通过！")
        sys.exit(0)
    else:
        print("部分测试失败！")
        sys.exit(1)
