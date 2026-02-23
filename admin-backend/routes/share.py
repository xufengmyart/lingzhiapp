#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文章分享路由
生成文章分享链接和二维码
"""

from flask import Blueprint, request, jsonify, Response
from functools import wraps
from database import get_db
import qrcode
from io import BytesIO
import logging

# 创建蓝图
share_bp = Blueprint('share', __name__)

# 日志配置
logger = logging.getLogger(__name__)


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
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token 已过期'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Token 无效: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': f'认证失败: {str(e)}'}), 401
    return decorated_function


@share_bp.route('/articles/<int:article_id>/share', methods=['GET'])
@login_required
def get_article_share_info(article_id):
    """
    获取文章分享信息
    返回分享链接、推荐码、二维码等

    查询参数：
    - type: 分享类型（wechat, weibo, qq, link）
    """
    try:
        user_id = request.user_id
        share_type = request.args.get('type', 'link')

        db = get_db()

        # 查询用户信息
        user = db.execute(
            'SELECT username, referral_code FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 如果没有推荐码，生成一个新的
        referral_code = user['referral_code']
        if not referral_code:
            from datetime import datetime, timedelta
            import uuid

            referral_code = uuid.uuid4().hex[:8].upper()
            expires_at = (datetime.now() + timedelta(days=365)).isoformat()

            db.execute(
                'UPDATE users SET referral_code = ?, referral_code_expires_at = ? WHERE id = ?',
                (referral_code, expires_at, user_id)
            )
            db.commit()

        # 查询文章信息
        article = db.execute(
            'SELECT id, title, slug FROM news_articles WHERE id = ?',
            (article_id,)
        ).fetchone()

        if not article:
            return jsonify({'error': '文章不存在'}), 404

        # 生成分享链接（包含推荐码）
        base_url = request.host_url.rstrip('/')
        share_url = f"{base_url}/article/{article['slug']}?referral={referral_code}"

        # 根据分享类型生成不同的链接
        share_data = {
            'success': True,
            'data': {
                'article_id': article_id,
                'article_title': article['title'],
                'article_slug': article['slug'],
                'referral_code': referral_code,
                'share_url': share_url,
            }
        }

        if share_type == 'wechat':
            # 微信分享
            share_data['data']['platform'] = '微信'
            share_data['data']['share_text'] = f"推荐阅读：{article['title']}\n{share_url}"
        elif share_type == 'weibo':
            # 微博分享
            share_data['data']['platform'] = '微博'
            share_data['data']['share_text'] = f"推荐阅读：{article['title']} {share_url} #灵值生态园#"
        elif share_type == 'qq':
            # QQ分享
            share_data['data']['platform'] = 'QQ'
            share_data['data']['share_text'] = f"推荐阅读：{article['title']}\n{share_url}"
        else:
            # 默认分享链接
            share_data['data']['platform'] = '链接'
            share_data['data']['share_text'] = share_url

        # 生成分享二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(share_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # 转换为 base64
        img_io = BytesIO()
        img.save(img_io, 'PNG')
        img_io.seek(0)
        img_base64 = img_io.getvalue().hex()

        share_data['data']['qrcode'] = f'data:image/png;base64,{img_base64}'

        # 记录分享统计
        try:
            # 检查是否已有该用户、该文章、该分享类型的记录
            existing_stat = db.execute(
                '''
                SELECT id, share_count
                FROM share_stats
                WHERE user_id = ? AND article_id = ? AND share_type = ?
                ''',
                (user_id, article_id, share_type)
            ).fetchone()

            if existing_stat:
                # 更新现有记录的分享次数
                db.execute(
                    '''
                    UPDATE share_stats
                    SET share_count = share_count + 1, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    ''',
                    (existing_stat['id'],)
                )
            else:
                # 创建新的分享统计记录
                db.execute(
                    '''
                    INSERT INTO share_stats
                    (user_id, article_id, share_type, share_url, referral_code, platform, share_count)
                    VALUES (?, ?, ?, ?, ?, ?, 1)
                    ''',
                    (user_id, article_id, share_type, share_url, referral_code, share_data['data']['platform'])
                )

            db.commit()
        except Exception as e:
            logger.error(f"记录分享统计失败: {str(e)}")
            # 不影响主流程，继续返回分享信息

        return jsonify(share_data)

    except Exception as e:
        logger.error(f"生成分享信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成分享信息失败: {str(e)}'}), 500
