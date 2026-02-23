"""
JWT 认证中间件
JWT Authentication Middleware

处理 JWT 令牌验证和用户认证
"""

import jwt
from flask import request, g, jsonify
from functools import wraps
import logging
from datetime import datetime
import sqlite3

logger = logging.getLogger(__name__)


class JWTAuth:
    """JWT 认证处理器"""

    def __init__(self, secret_key, expiration=604800):
        self.secret_key = secret_key
        self.expiration = expiration

    def generate_token(self, user_id, username, extra_data=None):
        """生成 JWT 令牌"""
        payload = {
            'user_id': user_id,
            'username': username,
            'exp': datetime.utcnow().timestamp() + self.expiration,
            'iat': datetime.utcnow().timestamp()
        }

        if extra_data:
            payload.update(extra_data)

        token = jwt.encode(payload, self.secret_key, algorithm='HS256')
        return token

    def verify_token(self, token):
        """验证 JWT 令牌"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT 令牌已过期")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"JWT 令牌无效: {str(e)}")
            return None

    def get_current_user(self, token, database_path):
        """获取当前用户信息"""
        payload = self.verify_token(token)
        if not payload:
            return None

        try:
            conn = sqlite3.connect(database_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT id, username, email, phone, total_lingzhi,
                       status, avatar_url, real_name
                FROM users
                WHERE id = ? AND status = 'active'
                """,
                (payload['user_id'],)
            )
            user = cursor.fetchone()

            conn.close()

            return dict(user) if user else None

        except Exception as e:
            logger.error(f"获取用户信息失败: {str(e)}")
            return None


# 全局 JWT 认证实例
jwt_auth = None


def init_jwt_auth(secret_key, expiration=604800):
    """初始化 JWT 认证"""
    global jwt_auth
    jwt_auth = JWTAuth(secret_key, expiration)
    logger.info("✅ JWT 认证已初始化")


def get_jwt_auth():
    """获取 JWT 认证实例"""
    return jwt_auth


def require_auth(f):
    """认证装饰器 - 需要登录"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 获取令牌
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'success': False,
                'message': '缺少认证令牌',
                'error_code': 'MISSING_TOKEN'
            }), 401

        # 检查 Bearer 格式
        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '令牌格式错误',
                'error_code': 'INVALID_TOKEN_FORMAT'
            }), 401

        token = auth_header.split(' ')[1]

        # 验证令牌
        if not jwt_auth:
            return jsonify({
                'success': False,
                'message': '认证系统未初始化',
                'error_code': 'AUTH_NOT_INITIALIZED'
            }), 500

        payload = jwt_auth.verify_token(token)
        if not payload:
            return jsonify({
                'success': False,
                'message': '令牌无效或已过期',
                'error_code': 'INVALID_TOKEN'
            }), 401

        # 将用户信息存入 g 对象
        g.current_user_id = payload.get('user_id')
        g.current_username = payload.get('username')
        g.current_payload = payload

        return f(*args, **kwargs)

    return decorated_function


def optional_auth(f):
    """认证装饰器 - 可选登录"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 尝试获取用户信息
        auth_header = request.headers.get('Authorization')

        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]

            if jwt_auth:
                payload = jwt_auth.verify_token(token)
                if payload:
                    g.current_user_id = payload.get('user_id')
                    g.current_username = payload.get('username')
                    g.current_payload = payload

        return f(*args, **kwargs)

    return decorated_function


def require_admin(f):
    """管理员认证装饰器 - 需要管理员权限"""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 先进行认证
        auth_result = require_auth(f)(*args, **kwargs)

        # 如果认证失败，直接返回
        if hasattr(auth_result, 'status_code') and auth_result.status_code == 401:
            return auth_result

        # 检查是否为管理员（这里简化处理，实际应该检查角色）
        # TODO: 实现真正的角色检查
        # is_admin = check_admin_role(g.current_user_id)

        return f(*args, **kwargs)

    return decorated_function
