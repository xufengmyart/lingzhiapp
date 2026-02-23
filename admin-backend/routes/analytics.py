# 数据分析系统API路由
# 功能：统计各功能的使用频率
# 创建时间: 2026-02-11

from flask import Blueprint, request, jsonify
from functools import wraps
import sqlite3
from datetime import datetime, timedelta

analytics_bp = Blueprint('analytics', __name__, url_prefix='/analytics')

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

@analytics_bp.route('/track', methods=['POST'])
def track_usage():
    """记录功能使用（不需要登录）"""
    try:
        data = request.get_json()
        user_id = get_user_id_from_request()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 插入使用记录
        cursor.execute('''
            INSERT INTO feature_usage_stats (
                user_id, feature_name, feature_category, action, metadata
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('feature_name'),
            data.get('feature_category'),
            data.get('action', 'view'),
            json.dumps(data.get('metadata', {}))
        ))
        conn.commit()
        conn.close()

        return jsonify({'success': True}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/track-page-visit', methods=['POST'])
def track_page_visit():
    """记录页面访问（不需要登录）"""
    try:
        data = request.get_json()
        user_id = get_user_id_from_request()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 插入页面访问记录
        cursor.execute('''
            INSERT INTO page_visit_stats (
                user_id, page_path, page_title, visit_duration,
                referer, device_type, browser, os, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            data.get('page_path'),
            data.get('page_title'),
            data.get('visit_duration'),
            data.get('referer'),
            data.get('device_type'),
            data.get('browser'),
            data.get('os'),
            data.get('session_id')
        ))
        conn.commit()
        conn.close()

        return jsonify({'success': True}), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/dashboard', methods=['GET'])
@requires_auth
def get_analytics_dashboard():
    """获取数据分析仪表板（管理员）"""
    try:
        user_id = get_user_id_from_request()
        days = request.args.get('days', 7, type=int)

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否是管理员
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        is_admin = user and user['role'] in ['admin', 'super_admin']

        if not is_admin:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # 计算时间范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        # 1. 页面访问统计
        cursor.execute('''
            SELECT page_path, COUNT(*) as visits,
                   AVG(visit_duration) as avg_duration
            FROM page_visit_stats
            WHERE created_at >= ?
            GROUP BY page_path
            ORDER BY visits DESC
            LIMIT 10
        ''', (start_date.isoformat(),))
        top_pages = [dict(row) for row in cursor.fetchall()]

        # 2. 功能使用统计
        cursor.execute('''
            SELECT feature_name, feature_category, COUNT(*) as usage_count
            FROM feature_usage_stats
            WHERE created_at >= ?
            GROUP BY feature_name, feature_category
            ORDER BY usage_count DESC
            LIMIT 10
        ''', (start_date.isoformat(),))
        top_features = [dict(row) for row in cursor.fetchall()]

        # 3. 访问趋势（按天）
        cursor.execute('''
            SELECT DATE(created_at) as date, COUNT(*) as visits
            FROM page_visit_stats
            WHERE created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (start_date.isoformat(),))
        visit_trend = [dict(row) for row in cursor.fetchall()]

        # 4. 设备类型分布
        cursor.execute('''
            SELECT device_type, COUNT(*) as count
            FROM page_visit_stats
            WHERE created_at >= ? AND device_type IS NOT NULL
            GROUP BY device_type
        ''', (start_date.isoformat(),))
        device_distribution = [dict(row) for row in cursor.fetchall()]

        # 5. 总体统计
        cursor.execute('''
            SELECT COUNT(*) as total_visits,
                   COUNT(DISTINCT user_id) as unique_users,
                   AVG(visit_duration) as avg_visit_duration
            FROM page_visit_stats
            WHERE created_at >= ?
        ''', (start_date.isoformat(),))
        overall_stats = dict(cursor.fetchone())

        # 6. 功能分类统计
        cursor.execute('''
            SELECT feature_category, COUNT(*) as usage_count
            FROM feature_usage_stats
            WHERE created_at >= ? AND feature_category IS NOT NULL
            GROUP BY feature_category
        ''', (start_date.isoformat(),))
        category_stats = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'top_pages': top_pages,
                'top_features': top_features,
                'visit_trend': visit_trend,
                'device_distribution': device_distribution,
                'overall_stats': overall_stats,
                'category_stats': category_stats,
                'period': {
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'days': days
                }
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/feature-ranking', methods=['GET'])
@requires_auth
def get_feature_ranking():
    """获取功能排行榜（管理员）"""
    try:
        user_id = get_user_id_from_request()
        category = request.args.get('category')

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否是管理员
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        is_admin = user and user['role'] in ['admin', 'super_admin']

        if not is_admin:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # 构建查询
        query = '''
            SELECT feature_name, feature_category,
                   COUNT(*) as total_views,
                   SUM(CASE WHEN action = 'submit' THEN 1 ELSE 0 END) as submits,
                   SUM(CASE WHEN action = 'complete' THEN 1 ELSE 0 END) as completes
            FROM feature_usage_stats
        '''
        params = []

        if category:
            query += ' WHERE feature_category = ?'
            params.append(category)

        query += '''
            GROUP BY feature_name, feature_category
            ORDER BY total_views DESC
        '''

        cursor.execute(query, params)
        ranking = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': ranking
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@analytics_bp.route('/export', methods=['GET'])
@requires_auth
def export_analytics():
    """导出分析数据（管理员）"""
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

        # 导出页面访问数据
        cursor.execute('''
            SELECT page_path, page_title, COUNT(*) as visits,
                   AVG(visit_duration) as avg_duration
            FROM page_visit_stats
            GROUP BY page_path, page_title
            ORDER BY visits DESC
        ''')
        page_data = [dict(row) for row in cursor.fetchall()]

        # 导出功能使用数据
        cursor.execute('''
            SELECT feature_name, feature_category, action, COUNT(*) as count
            FROM feature_usage_stats
            GROUP BY feature_name, feature_category, action
            ORDER BY feature_name, feature_category
        ''')
        feature_data = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'page_analytics': page_data,
                'feature_analytics': feature_data,
                'export_time': datetime.now().isoformat()
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
