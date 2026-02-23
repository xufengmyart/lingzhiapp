# 用户反馈系统API路由
# 功能：收集用户对新导航的反馈
# 创建时间: 2026-02-11

from flask import Blueprint, request, jsonify
from functools import wraps
import sqlite3
import json
from datetime import datetime

feedback_bp = Blueprint('feedback', __name__, url_prefix='/feedback')

# 数据库路径
DB_PATH = './lingzhi_ecosystem.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_id_from_request():
    """从请求中获取用户ID"""
    user_id = request.headers.get('X-User-ID')
    return int(user_id) if user_id else None

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

@feedback_bp.route('', methods=['POST'])
@requires_auth
def create_feedback():
    """提交用户反馈"""
    try:
        data = request.get_json()
        user_id = get_user_id_from_request()

        # 获取用户名
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        username = user['username'] if user else 'Unknown'

        # 插入反馈
        cursor.execute('''
            INSERT INTO user_feedback (
                user_id, username, feedback_type, category, rating,
                content, page, screenshot_url, status, priority
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            username,
            data.get('feedback_type', 'navigation'),
            data.get('category'),
            data.get('rating'),
            data.get('content'),
            data.get('page'),
            data.get('screenshot_url'),
            data.get('status', 'pending'),
            data.get('priority', 'medium')
        ))
        conn.commit()

        feedback_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'message': '反馈提交成功，感谢您的意见！',
            'feedback_id': feedback_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('', methods=['GET'])
@requires_auth
def get_feedback_list():
    """获取反馈列表（管理员）"""
    try:
        user_id = get_user_id_from_request()
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        feedback_type = request.args.get('feedback_type')
        status = request.args.get('status')
        offset = (page - 1) * page_size

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否是管理员
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        is_admin = user and user['role'] in ['admin', 'super_admin']

        if not is_admin:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # 构建查询条件
        query = 'SELECT * FROM user_feedback WHERE 1=1'
        params = []

        if feedback_type:
            query += ' AND feedback_type = ?'
            params.append(feedback_type)

        if status:
            query += ' AND status = ?'
            params.append(status)

        # 查询总数
        count_query = query.replace('*', 'COUNT(*) as total')
        cursor.execute(count_query, params)
        total = cursor.fetchone()['total']

        # 查询列表
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([page_size, offset])
        cursor.execute(query, params)
        feedback_list = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': feedback_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/<int:feedback_id>', methods=['PUT'])
@requires_auth
def update_feedback_status(feedback_id):
    """更新反馈状态（管理员）"""
    try:
        user_id = get_user_id_from_request()
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否是管理员
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        is_admin = user and user['role'] in ['admin', 'super_admin']

        if not is_admin:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # 更新反馈状态
        cursor.execute('''
            UPDATE user_feedback
            SET status = ?, priority = ?, admin_notes = ?, updated_at = ?
            WHERE id = ?
        ''', (
            data.get('status'),
            data.get('priority'),
            data.get('admin_notes'),
            datetime.now().isoformat(),
            feedback_id
        ))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '反馈状态更新成功'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/stats', methods=['GET'])
@requires_auth
def get_feedback_stats():
    """获取反馈统计（管理员）"""
    try:
        user_id = get_user_id_from_request()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否是管理员
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        is_admin = user and user['role'] in ['admin', 'super_admin']

        if not is_admin:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # 按类型统计
        cursor.execute('''
            SELECT feedback_type, COUNT(*) as count,
                   AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating
            FROM user_feedback
            GROUP BY feedback_type
        ''')
        by_type = [dict(row) for row in cursor.fetchall()]

        # 按状态统计
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM user_feedback
            GROUP BY status
        ''')
        by_status = [dict(row) for row in cursor.fetchall()]

        # 按优先级统计
        cursor.execute('''
            SELECT priority, COUNT(*) as count
            FROM user_feedback
            GROUP BY priority
        ''')
        by_priority = [dict(row) for row in cursor.fetchall()]

        # 总体统计
        cursor.execute('SELECT COUNT(*) as total FROM user_feedback')
        total_feedback = cursor.fetchone()['total']

        conn.close()

        return jsonify({
            'success': True,
            'stats': {
                'total_feedback': total_feedback,
                'by_type': by_type,
                'by_status': by_status,
                'by_priority': by_priority
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feedback_bp.route('/my', methods=['GET'])
@requires_auth
def get_my_feedback():
    """获取我的反馈"""
    try:
        user_id = get_user_id_from_request()

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM user_feedback
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,))
        feedback_list = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': feedback_list
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
