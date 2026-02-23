#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
头像上传路由
支持用户头像上传（类似微信/QQ）
"""

from flask import Blueprint, request, jsonify, send_from_directory, current_app
from functools import wraps
from database import get_db
from datetime import datetime
import logging
import jwt
import os
import uuid
from werkzeug.utils import secure_filename

# 创建蓝图
avatar_upload_bp = Blueprint('avatar_upload', __name__)

# 日志配置
logger = logging.getLogger(__name__)

# 从 config 导入 JWT 配置
from config import config
JWT_SECRET = config.JWT_SECRET_KEY
JWT_EXPIRATION = config.JWT_EXPIRATION

# 允许的图片格式
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
# 最大文件大小 (5MB)
MAX_FILE_SIZE = 5 * 1024 * 1024

# 上传目录
UPLOAD_FOLDER = 'uploads/avatars'
AVATAR_FOLDER = 'avatars'


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
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token 已过期'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': f'Token 无效: {str(e)}'}), 401
        except Exception as e:
            return jsonify({'error': f'认证失败: {str(e)}'}), 401
    return decorated_function


def allowed_file(filename):
    """检查文件扩展名是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_upload_dir():
    """确保上传目录存在"""
    # 上传到项目根目录下的 uploads/avatars
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads', 'avatars')
    os.makedirs(upload_dir, exist_ok=True)
    return upload_dir


@avatar_upload_bp.route('/upload/avatar', methods=['POST'])
@login_required
def upload_avatar():
    """
    上传用户头像
    支持格式: png, jpg, jpeg, gif, webp
    最大大小: 5MB
    """
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '请选择要上传的文件'}), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'error': '不支持的文件格式',
                'allowed_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'文件大小超过限制',
                'max_size': f'{MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # 确保上传目录存在
        upload_dir = ensure_upload_dir()
        filepath = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(filepath)
        
        # 生成访问URL
        # 访问路径: https://meiyueart.com/uploads/avatars/filename
        avatar_url = f"/uploads/avatars/{filename}"
        
        # 更新数据库中的头像URL
        user_id = request.current_user.get('user_id')
        db = get_db()
        db.execute(
            'UPDATE users SET avatar_url = ?, updated_at = ? WHERE id = ?',
            (avatar_url, datetime.now().isoformat(), user_id)
        )
        db.commit()
        db.close()
        
        logger.info(f"用户 {user_id} 上传头像成功: {avatar_url}")
        
        return jsonify({
            'success': True,
            'message': '头像上传成功',
            'data': {
                'avatar_url': avatar_url,
                'filename': filename
            }
        }), 200
        
    except Exception as e:
        logger.error(f"上传头像失败: {str(e)}")
        return jsonify({'error': f'上传头像失败: {str(e)}'}), 500


@avatar_upload_bp.route('/admin/users/<int:user_id>/avatar', methods=['POST'])
@login_required
def upload_user_avatar(user_id):
    """
    管理员上传用户头像
    """
    try:
        # 检查是否有文件
        if 'file' not in request.files:
            return jsonify({'error': '请选择要上传的文件'}), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({
                'error': '不支持的文件格式',
                'allowed_formats': list(ALLOWED_EXTENSIONS)
            }), 400
        
        # 检查文件大小
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)
        
        if file_size > MAX_FILE_SIZE:
            return jsonify({
                'error': f'文件大小超过限制',
                'max_size': f'{MAX_FILE_SIZE // (1024*1024)}MB'
            }), 400
        
        # 生成唯一文件名
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # 确保上传目录存在
        upload_dir = ensure_upload_dir()
        filepath = os.path.join(upload_dir, filename)
        
        # 保存文件
        file.save(filepath)
        
        # 生成访问URL
        avatar_url = f"/uploads/avatars/{filename}"
        
        # 更新数据库中的头像URL
        db = get_db()
        db.execute(
            'UPDATE users SET avatar_url = ?, updated_at = ? WHERE id = ?',
            (avatar_url, datetime.now().isoformat(), user_id)
        )
        db.commit()
        db.close()
        
        logger.info(f"管理员更新用户 {user_id} 头像成功: {avatar_url}")
        
        return jsonify({
            'success': True,
            'message': '头像更新成功',
            'data': {
                'avatar_url': avatar_url,
                'filename': filename
            }
        }), 200
        
    except Exception as e:
        logger.error(f"上传用户头像失败: {str(e)}")
        return jsonify({'error': f'上传用户头像失败: {str(e)}'}), 500


@avatar_upload_bp.route('/uploads/avatars/<filename>', methods=['GET'])
def get_avatar(filename):
    """
    访问上传的头像文件
    """
    try:
        upload_dir = ensure_upload_dir()
        file_path = os.path.join(upload_dir, filename)
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            logger.error(f"头像文件不存在: {file_path}")
            # 列出目录中的所有文件（用于调试）
            if os.path.exists(upload_dir):
                files = os.listdir(upload_dir)
                logger.error(f"uploads/avatars 目录中的文件: {files}")
            return jsonify({'error': '头像不存在', 'path': file_path}), 404
        
        return send_from_directory(upload_dir, filename)
    except Exception as e:
        logger.error(f"访问头像失败: {str(e)}")
        return jsonify({'error': '头像不存在'}), 404


@avatar_upload_bp.route('/debug/uploads', methods=['GET'])
@login_required
def debug_uploads():
    """
    调试：列出上传目录中的所有文件
    """
    try:
        upload_dir = ensure_upload_dir()
        if os.path.exists(upload_dir):
            files = os.listdir(upload_dir)
            return jsonify({
                'success': True,
                'upload_dir': upload_dir,
                'files': files
            })
        else:
            return jsonify({
                'success': False,
                'error': '上传目录不存在',
                'upload_dir': upload_dir
            })
    except Exception as e:
        logger.error(f"调试上传目录失败: {str(e)}")
        return jsonify({'error': f'调试失败: {str(e)}'}), 500
