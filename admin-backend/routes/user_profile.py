#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户资料编辑路由
支持用户资料的字段级编辑
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from database import get_db
from datetime import datetime
import json
import logging
import jwt

# 创建蓝图
user_profile_bp = Blueprint('user_profile', __name__)

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
            
            # 检查是否为管理员（如果是管理员登录，token 中会有 role 字段）
            role = payload.get('role')
            if role not in ['admin', 'super_admin']:
                # 如果 token 中没有 role，从 admins 表查询
                user_id = payload.get('user_id')
                db = get_db()
                admin = db.execute(
                    'SELECT role FROM admins WHERE id = ?',
                    (user_id,)
                ).fetchone()
                db.close()
                
                if not admin:
                    return jsonify({'error': '权限不足，需要管理员权限'}), 403
                
                role = admin['role']
            
            # 将用户信息传递给被装饰的函数
            request.current_user = payload
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token 已过期'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Token 无效: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': f'认证失败: {str(e)}'}), 401
    return decorated_function


def admin_required(f):
    """管理员权限验证装饰器"""
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
            
            # 检查是否为超级管理员
            role = payload.get('role')
            if role != 'super_admin':
                # 如果 token 中没有 role，从 admins 表查询
                user_id = payload.get('user_id')
                db = get_db()
                admin = db.execute(
                    'SELECT role FROM admins WHERE id = ?',
                    (user_id,)
                ).fetchone()
                db.close()
                
                if not admin or admin['role'] != 'super_admin':
                    return jsonify({'error': '权限不足，需要超级管理员权限'}), 403
            
            # 将用户信息传递给被装饰的函数
            request.current_user = payload
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token 已过期'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Token 无效: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': f'认证失败: {str(e)}'}), 401
    return decorated_function


@user_profile_bp.route('/admin/users/<int:user_id>/profile', methods=['GET'])
@login_required
def get_user_profile(user_id):
    """
    获取用户完整资料
    """
    try:
        db = get_db()

        # 查询用户基本信息
        user = db.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 转换为字典
        user_dict = dict(user)

        # 脱敏敏感字段
        if user_dict.get('my_sfzh'):
            sfzh = user_dict['my_sfzh']
            if len(sfzh) >= 6:
                user_dict['my_sfzh_masked'] = sfzh[:3] + '*' * (len(sfzh) - 6) + sfzh[-3:]

        # 解析JSON字段
        json_fields = [
            'cultural_interests', 'participated_projects',
            'skill_tags', 'social_links', 'contribution_details',
            'achievement_badges'
        ]
        for field in json_fields:
            if user_dict.get(field):
                try:
                    user_dict[field] = json.loads(user_dict[field])
                except json.JSONDecodeError:
                    user_dict[field] = []
            else:
                user_dict[field] = []

        # 获取用户类型信息
        if user_dict.get('user_type_id'):
            user_type = db.execute(
                'SELECT * FROM user_types WHERE id = ?',
                (user_dict['user_type_id'],)
            ).fetchone()
            if user_type:
                user_dict['user_type'] = dict(user_type)

        # 获取user_profiles表的身份信息
        user_profile = db.execute(
            'SELECT * FROM user_profiles WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        if user_profile:
            profile_dict = dict(user_profile)
            # 将user_profiles的字段合并到用户信息中
            user_dict.update({
                'id_card': profile_dict.get('id_card', ''),
                'bank_account': profile_dict.get('bank_account', ''),
                'bank_name': profile_dict.get('bank_name', ''),
                'id_card_masked': '',
                'bank_account_masked': ''
            })

            # 脱敏身份证号
            if profile_dict.get('id_card') and len(profile_dict['id_card']) >= 10:
                user_dict['id_card_masked'] = profile_dict['id_card'][:6] + '*' * (len(profile_dict['id_card']) - 10) + profile_dict['id_card'][-4:]

            # 脱敏银行账号
            if profile_dict.get('bank_account') and len(profile_dict['bank_account']) >= 8:
                bank_account = profile_dict['bank_account']
                masked = ''
                for i, char in enumerate(bank_account):
                    if i > 0 and i % 4 == 0:
                        masked += ' '
                    if i >= 4 and i < len(bank_account) - 4:
                        masked += '*'
                    else:
                        masked += char
                user_dict['bank_account_masked'] = masked

        return jsonify({
            'success': True,
            'user': user_dict
        }), 200

    except Exception as e:
        logger.error(f"获取用户资料失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取用户资料失败: {str(e)}'}), 500


@user_profile_bp.route('/admin/users/<int:user_id>/profile', methods=['PUT'])
@login_required
def update_user_profile(user_id):
    """
    更新用户资料
    支持字段级更新
    """
    try:
        db = get_db()

        # 查询用户是否存在
        user = db.execute(
            'SELECT id FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400

        # 定义可编辑字段及其验证规则（实际数据库字段名）
        # 注意：只更新数据库中实际存在的字段
        editable_fields = {
            # 基本信息
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

            # 管理员字段
            'status': {'type': str, 'required': False, 'admin_only': True},
            'is_verified': {'type': (int, bool), 'required': False, 'admin_only': True},
            'login_type': {'type': str, 'required': False, 'admin_only': True},
        }

        # camelCase 到 snake_case 的映射
        field_mapping = {
            'avatarUrl': 'avatar_url',
            'realName': 'real_name',
            'wechatNickname': 'wechat_nickname',
            'wechatAvatar': 'wechat_avatar',
            'isVerified': 'is_verified',
            'loginType': 'login_type',
            # 新增：user_profiles字段的映射
            'idCard': 'id_card',
            'bankAccount': 'bank_account',
            'bankName': 'bank_name',
        }

        # 分离users表和user_profiles表的字段
        users_data = {}
        profile_data = {}

        for key, value in data.items():
            normalized_key = field_mapping.get(key, key)
            if normalized_key in editable_fields:
                users_data[normalized_key] = value
            elif normalized_key in ['id_card', 'bank_account', 'bank_name']:
                profile_data[normalized_key] = value

        # 更新users表
        users_update_fields = []
        users_update_values = []
        errors = []

        for field, rules in editable_fields.items():
            if field not in users_data:
                continue

            value = users_data[field]

            # 跳过 None 值（除非字段允许）
            if value is None and field not in ['status', 'is_verified', 'login_type']:
                continue

            # 类型验证
            expected_types = rules['type'] if isinstance(rules['type'], tuple) else (rules['type'],)
            if not isinstance(value, expected_types):
                errors.append(f"{field}类型错误，期望{rules['type']}")
                continue

            # 添加到更新列表
            users_update_fields.append(f"{field} = ?")
            users_update_values.append(value)

        if users_update_fields:
            # 添加更新时间
            users_update_fields.append("updated_at = ?")
            users_update_values.append(datetime.now().isoformat())

            # 添加用户ID
            users_update_values.append(user_id)

            # 执行更新
            sql = f"UPDATE users SET {', '.join(users_update_fields)} WHERE id = ?"
            db.execute(sql, users_update_values)
            logger.info(f"用户 {user_id} users表更新成功")

        # 更新user_profiles表
        if profile_data:
            # 检查user_profiles记录是否存在
            existing_profile = db.execute(
                'SELECT id FROM user_profiles WHERE user_id = ?',
                (user_id,)
            ).fetchone()

            if existing_profile:
                # 更新现有记录
                profile_update_fields = []
                profile_update_values = []

                for field, value in profile_data.items():
                    if value is not None:
                        profile_update_fields.append(f"{field} = ?")
                        profile_update_values.append(value)

                if profile_update_fields:
                    profile_update_values.append(datetime.now().isoformat())
                    profile_update_values.append(user_id)

                    profile_sql = f"UPDATE user_profiles SET {', '.join(profile_update_fields)}, updated_at = ? WHERE user_id = ?"
                    db.execute(profile_sql, profile_update_values)
                    logger.info(f"用户 {user_id} user_profiles表更新成功")
            else:
                # 创建新记录
                profile_insert_fields = ['user_id', 'created_at', 'updated_at']
                profile_insert_values = [user_id, datetime.now().isoformat(), datetime.now().isoformat()]

                for field, value in profile_data.items():
                    if value is not None and value != '':
                        profile_insert_fields.append(field)
                        profile_insert_values.append(value)

                profile_sql = f"INSERT INTO user_profiles ({', '.join(profile_insert_fields)}) VALUES ({', '.join(['?'] * len(profile_insert_fields))})"
                db.execute(profile_sql, profile_insert_values)
                logger.info(f"用户 {user_id} user_profiles表创建成功")

        db.commit()

        return jsonify({
            'success': True,
            'message': '用户资料更新成功'
        }), 200

    except Exception as e:
        logger.error(f"更新用户资料失败: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return jsonify({'error': f'更新用户资料失败: {str(e)}'}), 500


@user_profile_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    """
    更新用户信息（兼容接口）
    调用 update_user_profile 函数处理
    """
    # 直接调用现有的更新逻辑
    return update_user_profile(user_id)


@user_profile_bp.route('/admin/users/<int:user_id>/contribution', methods=['PUT'])
@admin_required
def update_user_contribution(user_id):
    """
    管理员调整用户贡献值和灵值
    """
    try:
        db = get_db()
        
        # 查询用户是否存在
        user = db.execute(
            'SELECT id, total_lingzhi, total_contribution, cumulative_contribution FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()
        
        if not user:
            return jsonify({'error': '用户不存在'}), 404
        
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({'error': '请求数据不能为空'}), 400
        
        # 获取调整参数
        lingzhi_change = data.get('lingzhi_change', 0)
        contribution_change = data.get('contribution_change', 0)
        reason = data.get('reason', '')
        
        if lingzhi_change == 0 and contribution_change == 0:
            return jsonify({'error': '至少需要调整灵值或贡献值'}), 400
        
        if not reason:
            return jsonify({'error': '请提供调整原因'}), 400
        
        # 执行更新
        new_lingzhi = user['total_lingzhi'] + lingzhi_change
        new_contribution = user['total_contribution'] + contribution_change
        new_cumulative = user['cumulative_contribution'] + max(0, contribution_change)
        
        db.execute(
            '''UPDATE users 
               SET total_lingzhi = ?,
                   total_contribution = ?,
                   cumulative_contribution = ?,
                   updated_at = ?
               WHERE id = ?''',
            (new_lingzhi, new_contribution, new_cumulative, datetime.now().isoformat(), user_id)
        )
        db.commit()
        
        # 记录操作日志
        db.execute(
            '''INSERT INTO security_logs (user_id, event_type, details, created_at)
               VALUES (?, ?, ?, ?)''',
            (user_id, 'contribution_adjust', 
             f"管理员调整: 灵值{lingzhi_change:+d}, 贡献值{contribution_change:+d}, 原因: {reason}",
             datetime.now().isoformat())
        )
        db.commit()
        
        logger.info(f"管理员调整用户 {user_id}: 灵值{lingzhi_change:+d}, 贡献值{contribution_change:+d}")
        
        return jsonify({
            'success': True,
            'message': '调整成功',
            'new_values': {
                'total_lingzhi': new_lingzhi,
                'total_contribution': new_contribution,
                'cumulative_contribution': new_cumulative
            }
        }), 200
        
    except Exception as e:
        logger.error(f"调整用户贡献值失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'调整用户贡献值失败: {str(e)}'}), 500


@user_profile_bp.route('/admin/users/profile/schema', methods=['GET'])
@login_required
def get_profile_schema():
    """
    获取用户资料字段定义和验证规则
    用于前端生成动态表单
    """
    try:
        schema = {
            'basic_info': {
                'title': '基本信息',
                'fields': [
                    {
                        'name': 'username',
                        'label': '用户名',
                        'type': 'text',
                        'editable': False,
                        'description': '用户登录账号'
                    },
                    {
                        'name': 'email',
                        'label': '邮箱',
                        'type': 'email',
                        'editable': True,
                        'required': False
                    },
                    {
                        'name': 'phone',
                        'label': '手机号',
                        'type': 'tel',
                        'editable': True,
                        'required': True
                    },
                    {
                        'name': 'realName',
                        'label': '真实姓名',
                        'type': 'text',
                        'editable': True,
                        'required': False
                    },
                    {
                        'name': 'avatarUrl',
                        'label': '头像',
                        'type': 'url',
                        'editable': True,
                        'required': False
                    },
                    {
                        'name': 'website',
                        'label': '个人网站',
                        'type': 'url',
                        'editable': True,
                        'required': False
                    }
                ]
            },
            'identity_info': {
                'title': '身份信息',
                'fields': [
                    {
                        'name': 'wechatNickname',
                        'label': '微信昵称',
                        'type': 'text',
                        'editable': True,
                        'required': False
                    },
                    {
                        'name': 'wechatAvatar',
                        'label': '微信头像',
                        'type': 'url',
                        'editable': True,
                        'required': False
                    }
                ]
            },
            'cultural_info': {
                'title': '文化相关信息',
                'fields': [
                    {
                        'name': 'culturalInterests',
                        'label': '文化兴趣',
                        'type': 'tags',
                        'editable': True,
                        'required': False,
                        'placeholder': '添加文化兴趣标签'
                    },
                    {
                        'name': 'participatedProjects',
                        'label': '参与项目',
                        'type': 'tags',
                        'editable': True,
                        'required': False,
                        'placeholder': '添加参与的项目'
                    },
                    {
                        'name': 'skillTags',
                        'label': '技能标签',
                        'type': 'tags',
                        'editable': True,
                        'required': False,
                        'placeholder': '添加技能标签'
                    },
                    {
                        'name': 'achievementBadges',
                        'label': '成就徽章',
                        'type': 'tags',
                        'editable': True,
                        'required': False,
                        'placeholder': '添加成就徽章'
                    },
                    {
                        'name': 'contributionDetails',
                        'label': '贡献详情',
                        'type': 'tags',
                        'editable': True,
                        'required': False,
                        'placeholder': '添加贡献详情'
                    }
                ]
            },
            'location_info': {
                'title': '位置信息',
                'fields': [
                    {
                        'name': 'location',
                        'label': '地理位置',
                        'type': 'text',
                        'editable': True,
                        'required': False,
                        'placeholder': '如：北京市朝阳区'
                    }
                ]
            },
            'social_info': {
                'title': '社交媒体',
                'fields': [
                    {
                        'name': 'socialLinks',
                        'label': '社交媒体链接',
                        'type': 'object',
                        'editable': True,
                        'required': False,
                        'fields': [
                            {'name': 'weibo', 'label': '微博', 'type': 'url'},
                            {'name': 'wechat', 'label': '微信', 'type': 'text'},
                            {'name': 'douyin', 'label': '抖音', 'type': 'url'},
                            {'name': 'other', 'label': '其他', 'type': 'url'}
                        ]
                    }
                ]
            },
            'bio_info': {
                'title': '个人简介',
                'fields': [
                    {
                        'name': 'bio',
                        'label': '个人简介',
                        'type': 'textarea',
                        'editable': True,
                        'required': False,
                        'maxLength': 500
                    }
                ]
            }
        }
        
        return jsonify({
            'success': True,
            'schema': schema
        }), 200
        
    except Exception as e:
        logger.error(f"获取资料字段定义失败: {str(e)}")
        return jsonify({'error': f'获取资料字段定义失败: {str(e)}'}), 500
