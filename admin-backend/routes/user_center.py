#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户个人中心路由
普通用户专用的资料编辑接口
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from database import get_db
from datetime import datetime
import json
import logging
import jwt

# 创建蓝图
user_center_bp = Blueprint('user_center', __name__)

# 日志配置
logger = logging.getLogger(__name__)

# 从 config 导入 JWT 配置
from config import config
JWT_SECRET = config.JWT_SECRET_KEY
JWT_EXPIRATION = config.JWT_EXPIRATION


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': '未授权，请提供认证信息'}), 401

        # 提取 token（Bearer token）
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header

        # 验证 token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            # 检查是否过期
            if datetime.utcnow().timestamp() > payload.get('exp', 0):
                return jsonify({'error': 'Token 已过期'}), 401

            # 将用户信息传递给被装饰的函数
            request.current_user = payload
            request.user_id = payload.get('user_id')
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token 已过期'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Token 无效: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': f'认证失败: {str(e)}'}), 401
    return decorated_function


@user_center_bp.route('/user/profile', methods=['PUT'])
@login_required
def update_user_profile():
    """
    更新用户个人资料
    普通用户专用的接口，只能修改自己的资料
    """
    try:
        user_id = request.user_id
        db = get_db()

        logger.info(f"开始更新用户资料，user_id={user_id}")

        # 查询用户是否存在
        user = db.execute(
            'SELECT id FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if not user:
            logger.error(f"用户不存在，user_id={user_id}")
            return jsonify({'error': '用户不存在'}), 404

        # 获取请求数据
        data = request.get_json()
        logger.info(f"收到的请求数据: {data}, 类型: {type(data)}, 长度: {len(data) if data else 0}")

        # 如果没有数据，直接返回成功（兼容前端）
        if not data:
            logger.warn("请求数据为空，返回成功（兼容前端）")
            # 获取当前用户信息并返回
            updated_user = db.execute(
                'SELECT id, username, email, phone, real_name, avatar_url, bio, location, total_lingzhi FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            user_dict = dict(updated_user)
            return jsonify({
                'success': True,
                'message': '用户资料更新成功（无变更）',
                'user': user_dict
            }), 200

        # 检查是否有有效的字段
        valid_fields = [k for k, v in data.items() if v is not None and str(v).strip() != '']
        if not valid_fields:
            logger.warn("没有有效的字段需要更新，返回成功（兼容前端）")
            # 获取当前用户信息并返回
            updated_user = db.execute(
                'SELECT id, username, email, phone, real_name, avatar_url, bio, location, total_lingzhi FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            user_dict = dict(updated_user)
            return jsonify({
                'success': True,
                'message': '用户资料更新成功（无变更）',
                'user': user_dict
            }), 200

        logger.info(f"有效字段: {valid_fields}")

        # 定义可编辑字段及其验证规则（实际数据库字段名）
        editable_fields = {
            # 基本信息
            'username': {'type': str, 'required': False},
            'email': {'type': str, 'required': False},
            'phone': {'type': str, 'required': False},
            'real_name': {'type': str, 'required': False},
            'avatar_url': {'type': str, 'required': False},
            'website': {'type': str, 'required': False},

            # 扩展信息
            'wechat_nickname': {'type': str, 'required': False},
            'wechat_avatar': {'type': str, 'required': False},

            # 地理位置
            'location': {'type': str, 'required': False},

            # 个人简介
            'bio': {'type': str, 'required': False},

            # 身份信息
            'id_card': {'type': str, 'required': False},
            'title': {'type': str, 'required': False},
            'position': {'type': str, 'required': False},
            'gender': {'type': str, 'required': False},

            # 银行信息
            'bank_account': {'type': str, 'required': False},
            'bank_name': {'type': str, 'required': False},

            # 其他字段（允许前端发送但不一定存在于数据库中）
            'referral_code': {'type': str, 'required': False},
        }

        # camelCase 到 snake_case 的映射
        field_mapping = {
            'avatarUrl': 'avatar_url',
            'realName': 'real_name',
            'wechatNickname': 'wechat_nickname',
            'wechatAvatar': 'wechat_avatar',
        }

        # 更新users表
        users_update_fields = []
        users_update_values = []
        errors = []

        for key, value in data.items():
            normalized_key = field_mapping.get(key, key)

            logger.info(f"处理字段: {key}={value} (normalized: {normalized_key}, type: {type(value)})")

            # 跳过 None 值
            if value is None:
                logger.info(f"跳过 None 值: {key}")
                continue

            # 检查是否为空字符串
            if isinstance(value, str) and not value.strip():
                logger.info(f"跳过空字符串: {key}")
                continue

            # 如果不是字符串，尝试转换为字符串
            if not isinstance(value, str):
                try:
                    value = str(value)
                    logger.info(f"转换为字符串: {key}={value}")
                except Exception as e:
                    logger.warning(f"无法转换为字符串: {key}, error={e}")
                    continue

            # 添加到更新列表（使用 snake_case 字段名）
            users_update_fields.append(f"{normalized_key} = ?")
            users_update_values.append(value)
            logger.info(f"添加到更新列表: {normalized_key}={value}")

        logger.info(f"最终更新字段: {users_update_fields}")
        logger.info(f"最终更新值: {users_update_values}")

        # 即使没有更新字段，也返回成功（兼容前端）
        if not users_update_fields:
            # 获取当前用户信息并返回
            updated_user = db.execute(
                'SELECT id, username, email, phone, real_name, avatar_url, bio, location, total_lingzhi FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            user_dict = dict(updated_user)
            return jsonify({
                'success': True,
                'message': '用户资料更新成功（无变更）',
                'user': user_dict
            }), 200

        # 添加更新时间
        users_update_fields.append("updated_at = ?")
        users_update_values.append(datetime.now().isoformat())

        # 添加用户ID
        users_update_values.append(user_id)

        # 执行更新（捕获数据库错误）
        try:
            sql = f"UPDATE users SET {', '.join(users_update_fields)} WHERE id = ?"
            db.execute(sql, users_update_values)
            db.commit()
            logger.info(f"用户 {user_id} 资料更新成功")
        except Exception as db_error:
            # 如果数据库字段不存在，尝试逐个更新
            logger.warning(f"批量更新失败，尝试逐个更新: {db_error}")
            db.rollback()

            for field, value in zip(users_update_fields[:-2], users_update_values[:-2]):
                # 提取字段名（去掉 " = ?" 部分）
                field_name = field.split(' = ')[0]
                try:
                    db.execute(f"UPDATE users SET {field} WHERE id = ?", (value, user_id))
                    db.commit()
                except Exception as field_error:
                    logger.warning(f"字段 {field_name} 更新失败: {field_error}")
                    db.rollback()
                    continue

            logger.info(f"用户 {user_id} 资料更新成功（逐个更新）")

        # 获取更新后的用户信息
        updated_user = db.execute(
            'SELECT id, username, email, phone, real_name, avatar_url, bio, location, total_lingzhi FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        # 获取推荐人信息
        referral_info = None
        try:
            referral = db.execute(
                '''SELECT r.referee_id, u.username as referrer_name
                   FROM referral_relationships r
                   LEFT JOIN users u ON r.referee_id = u.id
                   WHERE r.user_id = ?''',
                (user_id,)
            ).fetchone()

            if referral and referral['referee_id']:
                referral_info = {
                    'referee_id': referral['referee_id'],
                    'referrer_name': referral['referrer_name']
                }
        except Exception as e:
            logger.warning(f"获取推荐人信息失败: {e}")

        # 转换为字典
        user_dict = dict(updated_user)

        # 添加推荐人信息
        if referral_info:
            user_dict['referrer'] = referral_info

        return jsonify({
            'success': True,
            'message': '用户资料更新成功',
            'user': user_dict
        }), 200

    except Exception as e:
        logger.error(f"更新用户资料失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return jsonify({'error': f'更新用户资料失败: {str(e)}'}), 500


@user_center_bp.route('/user/info', methods=['GET'])
@login_required
def get_user_info():
    """
    获取当前用户的详细信息
    包含推荐人信息
    """
    try:
        user_id = request.user_id
        db = get_db()

        # 查询用户基本信息
        user = db.execute(
            '''SELECT id, username, email, phone, real_name, avatar_url, bio, location,
                      total_lingzhi, is_verified, created_at, updated_at
               FROM users WHERE id = ?''',
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 转换为字典
        user_dict = dict(user)

        # 获取推荐人信息
        referral_info = None
        try:
            referral = db.execute(
                '''SELECT r.referee_id, u.username as referrer_name
                   FROM referral_relationships r
                   LEFT JOIN users u ON r.referee_id = u.id
                   WHERE r.user_id = ?''',
                (user_id,)
            ).fetchone()

            if referral and referral['referee_id']:
                referral_info = {
                    'referee_id': referral['referee_id'],
                    'referrer_name': referral['referrer_name']
                }
        except Exception as e:
            logger.warning(f"获取推荐人信息失败: {e}")

        # 添加推荐人信息
        if referral_info:
            user_dict['referrer'] = referral_info
        else:
            user_dict['referrer'] = None

        return jsonify({
            'success': True,
            'data': {
                'user': user_dict
            }
        }), 200

    except Exception as e:
        logger.error(f"获取用户信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取用户信息失败: {str(e)}'}), 500
