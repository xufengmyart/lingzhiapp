#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
推荐关系管理路由（仅超级管理员）
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from database import get_db
import logging

# 创建蓝图
referral_management_bp = Blueprint('referral_management', __name__)

# 日志配置
logger = logging.getLogger(__name__)


def super_admin_required(f):
    """超级管理员权限验证装饰器"""
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
        import jwt
        from config import config
        JWT_SECRET = config.JWT_SECRET_KEY

        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            # 检查是否过期
            from datetime import datetime
            if datetime.utcnow().timestamp() > payload.get('exp', 0):
                return jsonify({'error': 'Token 已过期'}), 401

            # 将用户信息传递给被装饰的函数
            request.current_user = payload
            request.user_id = payload.get('user_id')

            # 验证是否为超级管理员
            db = get_db()
            admin = db.execute(
                'SELECT * FROM admins WHERE username = ?',
                (request.current_user.get('username'),)
            ).fetchone()

            if not admin:
                return jsonify({'error': '权限不足：仅超级管理员可操作'}), 403

            if admin.get('role') != 'super_admin':
                return jsonify({'error': '权限不足：仅超级管理员可操作'}), 403

            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token 已过期'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Token 无效: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': f'认证失败: {str(e)}'}), 401
    return decorated_function


@referral_management_bp.route('/referral/relationships', methods=['GET'])
@super_admin_required
def get_all_referral_relationships():
    """
    获取所有推荐关系
    查询参数：
    - page: 页码（默认1）
    - limit: 每页数量（默认20）
    - referrer_id: 推荐人ID（可选）
    - referee_id: 被推荐人ID（可选）
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit

        referrer_id = request.args.get('referrer_id')
        referee_id = request.args.get('referee_id')

        db = get_db()

        # 构建查询条件
        where_clause = ""
        params = []

        if referrer_id:
            where_clause += " AND r.referrer_id = ?"
            params.append(referrer_id)

        if referee_id:
            where_clause += " AND r.referee_id = ?"
            params.append(referee_id)

        # 查询推荐关系
        query = f'''
            SELECT
                r.id,
                r.referrer_id,
                r.referee_id,
                r.level,
                r.status,
                r.created_at,
                ru.username as referrer_username,
                reu.username as referee_username
            FROM referral_relationships r
            LEFT JOIN users ru ON r.referrer_id = ru.id
            LEFT JOIN users reu ON r.referee_id = reu.id
            WHERE 1=1 {where_clause}
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])

        relationships = db.execute(query, params).fetchall()

        # 查询总数
        count_query = f'''
            SELECT COUNT(*) as total
            FROM referral_relationships
            WHERE 1=1 {where_clause}
        '''
        total = db.execute(count_query, params[:-2]).fetchone()['total']

        result = {
            'success': True,
            'data': {
                'relationships': [dict(rel) for rel in relationships],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': (total + limit - 1) // limit
                }
            }
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"获取推荐关系失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取推荐关系失败: {str(e)}'}), 500


@referral_management_bp.route('/referral/relationships/<int:relationship_id>', methods=['PUT'])
@super_admin_required
def update_referral_relationship(relationship_id):
    """
    修改推荐关系
    请求体：
    - referrer_id: 新的推荐人ID
    - status: 状态（active, inactive）
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': '请求数据格式错误'}), 400

        new_referrer_id = data.get('referrer_id')
        status = data.get('status')

        if not new_referrer_id and not status:
            return jsonify({'error': '请提供至少一个要修改的字段'}), 400

        db = get_db()

        # 检查推荐关系是否存在
        relationship = db.execute(
            'SELECT * FROM referral_relationships WHERE id = ?',
            (relationship_id,)
        ).fetchone()

        if not relationship:
            return jsonify({'error': '推荐关系不存在'}), 404

        # 构建更新语句
        update_fields = []
        params = []

        if new_referrer_id:
            # 验证新的推荐人是否存在
            referrer = db.execute(
                'SELECT id FROM users WHERE id = ?',
                (new_referrer_id,)
            ).fetchone()

            if not referrer:
                return jsonify({'error': '新的推荐人不存在'}), 404

            update_fields.append('referrer_id = ?')
            params.append(new_referrer_id)

        if status:
            if status not in ['active', 'inactive']:
                return jsonify({'error': '状态无效，必须是 active 或 inactive'}), 400
            update_fields.append('status = ?')
            params.append(status)

        params.append(relationship_id)

        # 更新推荐关系
        db.execute(
            f'''
            UPDATE referral_relationships
            SET {', '.join(update_fields)}
            WHERE id = ?
            ''',
            params
        )

        # 更新用户表中的推荐人ID
        if new_referrer_id:
            db.execute(
                'UPDATE users SET referrer_id = ? WHERE id = ?',
                (new_referrer_id, relationship['referee_id'])
            )

        db.commit()

        return jsonify({
            'success': True,
            'message': '推荐关系修改成功'
        })

    except Exception as e:
        logger.error(f"修改推荐关系失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'修改推荐关系失败: {str(e)}'}), 500


@referral_management_bp.route('/referral/relationships/<int:relationship_id>', methods=['DELETE'])
@super_admin_required
def delete_referral_relationship(relationship_id):
    """
    删除推荐关系
    """
    try:
        db = get_db()

        # 检查推荐关系是否存在
        relationship = db.execute(
            'SELECT * FROM referral_relationships WHERE id = ?',
            (relationship_id,)
        ).fetchone()

        if not relationship:
            return jsonify({'error': '推荐关系不存在'}), 404

        # 删除推荐关系
        db.execute(
            'DELETE FROM referral_relationships WHERE id = ?',
            (relationship_id,)
        )

        # 清除用户表中的推荐人ID
        db.execute(
            'UPDATE users SET referrer_id = NULL WHERE id = ?',
            (relationship['referee_id'],)
        )

        db.commit()

        return jsonify({
            'success': True,
            'message': '推荐关系删除成功'
        })

    except Exception as e:
        logger.error(f"删除推荐关系失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'删除推荐关系失败: {str(e)}'}), 500


@referral_management_bp.route('/share/stats', methods=['GET'])
@super_admin_required
def get_share_stats():
    """
    获取分享统计数据
    查询参数：
    - page: 页码（默认1）
    - limit: 每页数量（默认20）
    - user_id: 用户ID（可选）
    - article_id: 文章ID（可选）
    - share_type: 分享类型（可选）
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 20))
        offset = (page - 1) * limit

        user_id = request.args.get('user_id')
        article_id = request.args.get('article_id')
        share_type = request.args.get('share_type')

        db = get_db()

        # 构建查询条件
        where_clause = ""
        params = []

        if user_id:
            where_clause += " AND s.user_id = ?"
            params.append(user_id)

        if article_id:
            where_clause += " AND s.article_id = ?"
            params.append(article_id)

        if share_type:
            where_clause += " AND s.share_type = ?"
            params.append(share_type)

        # 查询分享统计
        query = f'''
            SELECT
                s.id,
                s.user_id,
                s.article_id,
                s.share_type,
                s.platform,
                s.share_url,
                s.referral_code,
                s.share_count,
                s.click_count,
                s.registration_count,
                s.created_at,
                s.updated_at,
                u.username as user_username,
                a.title as article_title
            FROM share_stats s
            LEFT JOIN users u ON s.user_id = u.id
            LEFT JOIN news_articles a ON s.article_id = a.id
            WHERE 1=1 {where_clause}
            ORDER BY s.created_at DESC
            LIMIT ? OFFSET ?
        '''
        params.extend([limit, offset])

        stats = db.execute(query, params).fetchall()

        # 查询总数
        count_query = f'''
            SELECT COUNT(*) as total
            FROM share_stats
            WHERE 1=1 {where_clause}
        '''
        total = db.execute(count_query, params[:-2]).fetchone()['total']

        result = {
            'success': True,
            'data': {
                'stats': [dict(stat) for stat in stats],
                'pagination': {
                    'page': page,
                    'limit': limit,
                    'total': total,
                    'total_pages': (total + limit - 1) // limit
                }
            }
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"获取分享统计失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取分享统计失败: {str(e)}'}), 500


@referral_management_bp.route('/share/summary', methods=['GET'])
@super_admin_required
def get_share_summary():
    """
    获取分享统计摘要
    """
    try:
        db = get_db()

        # 总分享次数
        total_shares = db.execute('''
            SELECT SUM(share_count) as total
            FROM share_stats
        ''').fetchone()['total'] or 0

        # 总点击次数
        total_clicks = db.execute('''
            SELECT SUM(click_count) as total
            FROM share_stats
        ''').fetchone()['total'] or 0

        # 总注册次数
        total_registrations = db.execute('''
            SELECT SUM(registration_count) as total
            FROM share_stats
        ''').fetchone()['total'] or 0

        # 各平台分享次数
        platform_stats = db.execute('''
            SELECT platform, SUM(share_count) as total
            FROM share_stats
            GROUP BY platform
        ''').fetchall()

        # 最受欢迎的文章
        top_articles = db.execute('''
            SELECT a.id, a.title, COUNT(*) as share_count
            FROM share_stats s
            LEFT JOIN news_articles a ON s.article_id = a.id
            GROUP BY a.id, a.title
            ORDER BY share_count DESC
            LIMIT 5
        ''').fetchall()

        # 最活跃的分享用户
        top_users = db.execute('''
            SELECT u.id, u.username, SUM(s.share_count) as total_shares
            FROM share_stats s
            LEFT JOIN users u ON s.user_id = u.id
            GROUP BY u.id, u.username
            ORDER BY total_shares DESC
            LIMIT 5
        ''').fetchall()

        result = {
            'success': True,
            'data': {
                'summary': {
                    'total_shares': total_shares,
                    'total_clicks': total_clicks,
                    'total_registrations': total_registrations
                },
                'platform_stats': [dict(stat) for stat in platform_stats],
                'top_articles': [dict(article) for article in top_articles],
                'top_users': [dict(user) for user in top_users]
            }
        }

        return jsonify(result)

    except Exception as e:
        logger.error(f"获取分享统计摘要失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'获取分享统计摘要失败: {str(e)}'}), 500
