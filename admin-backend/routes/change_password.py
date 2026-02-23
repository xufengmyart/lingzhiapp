"""
修改密码功能路由
支持前台、后台用户修改密码
"""

from flask import Blueprint, request, jsonify
import bcrypt
import jwt
from datetime import datetime

# 导入配置
from config import config
from database import get_db

password_bp = Blueprint('password', __name__)

# JWT配置
JWT_SECRET = config.JWT_SECRET_KEY

def verify_password(password, hashed):
    """验证密码 - 使用bcrypt"""
    try:
        password_bytes = password.encode('utf-8')
        if isinstance(hashed, bytes):
            hashed_bytes = hashed
        else:
            hashed_bytes = hashed.encode('utf-8') if isinstance(hashed, str) else hashed
        
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        print(f"密码验证失败: {e}")
        return False

def get_current_user_id():
    """从请求头中获取当前用户ID"""
    try:
        token = request.headers.get('Authorization')
        if not token:
            return None
        
        # 移除 "Bearer " 前缀
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        if payload:
            return payload.get('user_id')
        return None
    except Exception as e:
        print(f"获取用户ID失败: {e}")
        return None

@password_bp.route('/user/change-password', methods=['POST'])
def user_change_password():
    """
    用户修改密码
    请求体: { oldPassword: string, newPassword: string }
    响应: { success: true, message: string }
    """
    try:
        user_id = get_current_user_id()
        if not user_id:
            return jsonify({
                'success': False,
                'message': '未登录或登录已过期'
            }), 401

        data = request.get_json()
        old_password = data.get('oldPassword')
        new_password = data.get('newPassword')

        if not old_password or not new_password:
            return jsonify({
                'success': False,
                'message': '旧密码和新密码不能为空'
            }), 400

        # 密码长度校验
        if len(new_password) < 6:
            return jsonify({
                'success': False,
                'message': '新密码长度不能少于6位'
            }), 400

        # 旧密码和新密码不能相同
        if old_password == new_password:
            return jsonify({
                'success': False,
                'message': '新密码不能与旧密码相同'
            }), 400

        conn = get_db()
        user = conn.execute(
            "SELECT id, password_hash FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 验证旧密码
        if not verify_password(old_password, user['password_hash']):
            conn.close()
            return jsonify({
                'success': False,
                'message': '旧密码错误'
            }), 400

        # 生成新密码的哈希
        new_password_bytes = new_password.encode('utf-8')
        new_password_hash = bcrypt.hashpw(new_password_bytes, bcrypt.gensalt()).decode('utf-8')

        # 更新密码
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_password_hash, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '密码修改成功'
        })
    except Exception as e:
        print(f"修改密码失败: {e}")
        return jsonify({
            'success': False,
            'message': f'修改密码失败: {str(e)}'
        }), 500

@password_bp.route('/admin/users/<int:user_id>/password', methods=['PUT'])
def admin_reset_password(user_id):
    """
    管理员重置用户密码
    需要管理员权限
    请求体: { password: string }
    响应: { success: true, message: string }
    """
    try:
        # 验证管理员权限
        admin_user_id = get_current_user_id()
        if not admin_user_id:
            return jsonify({
                'success': False,
                'message': '未登录或登录已过期'
            }), 401

        # 检查是否为管理员
        conn = get_db()
        admin = conn.execute(
            "SELECT role FROM admins WHERE id = ?",
            (admin_user_id,)
        ).fetchone()

        if not admin:
            conn.close()
            return jsonify({
                'success': False,
                'message': '权限不足，需要管理员权限'
            }), 403

        data = request.get_json()
        new_password = data.get('password')

        if not new_password:
            conn.close()
            return jsonify({
                'success': False,
                'message': '密码不能为空'
            }), 400

        # 密码长度校验
        if len(new_password) < 6:
            conn.close()
            return jsonify({
                'success': False,
                'message': '密码长度不能少于6位'
            }), 400

        # 检查目标用户是否存在
        user = conn.execute(
            "SELECT id FROM users WHERE id = ?",
            (user_id,)
        ).fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 生成新密码的哈希
        new_password_bytes = new_password.encode('utf-8')
        new_password_hash = bcrypt.hashpw(new_password_bytes, bcrypt.gensalt()).decode('utf-8')

        # 更新密码
        conn.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_password_hash, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '密码重置成功'
        })
    except Exception as e:
        print(f"重置密码失败: {e}")
        return jsonify({
            'success': False,
            'message': f'重置密码失败: {str(e)}'
        }), 500
