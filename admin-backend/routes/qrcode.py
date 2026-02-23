#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
二维码生成路由
生成用户推荐码的二维码
"""

from flask import Blueprint, request, jsonify, Response
from functools import wraps
from database import get_db
import qrcode
from io import BytesIO
import logging

# 创建蓝图
qrcode_bp = Blueprint('qrcode', __name__)

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


@qrcode_bp.route('/qrcode', methods=['GET'])
@login_required
def get_referral_qrcode():
    """
    获取用户推荐码二维码
    支持两种模式：
    1. 显示模式：返回 base64 编码的二维码图片
    2. 下载模式：直接返回 PNG 文件

    查询参数：
    - download: 是否下载（true/false），默认 false
    """
    try:
        user_id = request.user_id
        download = request.args.get('download', 'false').lower() == 'true'
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
            logger.info(f"用户 {user_id} 生成新推荐码: {referral_code}")

        # 生成推荐链接
        base_url = request.host_url.rstrip('/')
        referral_url = f"{base_url}/register?referral={referral_code}"

        # 生成二维码
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(referral_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        if download:
            # 下载模式：直接返回 PNG 文件
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)

            return Response(
                img_io.getvalue(),
                mimetype='image/png',
                headers={
                    'Content-Disposition': f'attachment; filename="推荐码_{referral_code}.png"'
                }
            )
        else:
            # 显示模式：返回 base64 编码
            img_io = BytesIO()
            img.save(img_io, 'PNG')
            img_io.seek(0)
            img_base64 = img_io.getvalue().hex()

            return jsonify({
                'success': True,
                'data': {
                    'qrcode': f'data:image/png;base64,{img_base64}',
                    'referral_code': referral_code,
                    'referral_url': referral_url
                }
            })

    except Exception as e:
        logger.error(f"生成二维码失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'生成二维码失败: {str(e)}'}), 500
