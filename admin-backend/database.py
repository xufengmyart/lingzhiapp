#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块
提供数据库连接和常用操作函数
"""

import sqlite3
import bcrypt
from config import config

# 数据库配置
DATABASE = config.DATABASE_PATH

def get_db():
    """
    获取数据库连接
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    """
    密码哈希（统一使用bcrypt）
    Args:
        password: 明文密码
    Returns:
        str: bcrypt 哈希后的密码
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def check_password(password, password_hash):
    """
    验证密码
    Args:
        password: 明文密码
        password_hash: 哈希密码
    Returns:
        bool: 密码是否匹配
    """
    try:
        # 尝试 bcrypt 验证
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    except Exception as e:
        # 如果验证失败，尝试其他方式（兼容旧数据）
        print(f"[密码验证] bcrypt验证失败: {e}")
        try:
            from werkzeug.security import check_password_hash as werkzeug_check
            result = werkzeug_check(password_hash, password)
            print(f"[密码验证] werkzeug验证结果: {result}")
            return result
        except:
            # 如果都失败，尝试 sha256
            sha256_hash = hashlib.sha256(password.encode()).hexdigest()
            return sha256_hash == password_hash

# 保留旧函数名以兼容，实际使用hash_password
def hash_password_bcrypt(password):
    """密码哈希（bcrypt）- 兼容函数"""
    return hash_password(password)

def hash_password_sha256(password):
    """密码哈希（SHA256）- 兼容函数"""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()

def verify_token(token):
    """
    验证 JWT token
    Args:
        token: JWT token 字符串
    Returns:
        dict: 包含用户信息的字典，验证失败返回 None
    """
    try:
        import jwt
        from config import config
        
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        
        # 检查 token 是否过期
        if datetime.datetime.utcnow().timestamp() > payload.get('exp', 0):
            return None
            
        return payload
    except jwt.ExpiredSignatureError:
        print("[Token验证] Token 已过期")
        return None
    except jwt.InvalidTokenError as e:
        print(f"[Token验证] Token 无效: {e}")
        return None
    except Exception as e:
        print(f"[Token验证] 验证失败: {e}")
        return None
