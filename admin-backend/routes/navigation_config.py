# 导航配置管理API路由
# 功能：根据实际使用情况微调分类和排序
# 创建时间: 2026-02-11

from flask import Blueprint, request, jsonify
from functools import wraps
import sqlite3
from datetime import datetime

navigation_config_bp = Blueprint('navigation_config', __name__, url_prefix='/navigation')

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

@navigation_config_bp.route('/config', methods=['GET'])
def get_navigation_config():
    """获取导航配置（公开）"""
    try:
        user_id = get_user_id_from_request()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 获取用户角色
        user_role = None
        if user_id:
            cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            user_role = user['role'] if user else None

        # 查询导航配置
        cursor.execute('''
            SELECT nav_group_id, nav_item_id, label, path, icon_name,
                   order_index, is_visible, is_highlighted, description, requires_role
            FROM navigation_config
            WHERE is_visible = 1
            ORDER BY nav_group_id, order_index
        ''')
        all_configs = [dict(row) for row in cursor.fetchall()]

        # 按组分类
        grouped = {}
        for config in all_configs:
            # 检查权限
            if config['requires_role'] and user_role not in config['requires_role'].split(','):
                continue

            group_id = config['nav_group_id']
            if group_id not in grouped:
                grouped[group_id] = []
            grouped[group_id].append(config)

        conn.close()

        return jsonify({
            'success': True,
            'data': grouped
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@navigation_config_bp.route('/config', methods=['PUT'])
@requires_auth
def update_navigation_config():
    """更新导航配置（管理员）"""
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

        # 批量更新
        updated_count = 0
        for item in data.get('items', []):
            cursor.execute('''
                UPDATE navigation_config
                SET label = ?, order_index = ?, is_visible = ?,
                    is_highlighted = ?, description = ?, updated_at = ?
                WHERE nav_item_id = ?
            ''', (
                item.get('label'),
                item.get('order_index', 0),
                1 if item.get('is_visible') else 0,
                1 if item.get('is_highlighted') else 0,
                item.get('description'),
                datetime.now().isoformat(),
                item.get('nav_item_id')
            ))
            updated_count += cursor.rowcount

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'成功更新 {updated_count} 个导航项',
            'updated_count': updated_count
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@navigation_config_bp.route('/group', methods=['GET'])
@requires_auth
def get_navigation_groups():
    """获取导航分组（管理员）"""
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

        # 查询所有分组
        cursor.execute('''
            SELECT DISTINCT nav_group_id, COUNT(*) as item_count
            FROM navigation_config
            GROUP BY nav_group_id
            ORDER BY nav_group_id
        ''')
        groups = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': groups
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@navigation_config_bp.route('/optimize-suggestions', methods=['GET'])
@requires_auth
def get_optimize_suggestions():
    """获取导航优化建议（管理员）"""
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

        suggestions = []

        # 1. 根据功能使用频率建议排序
        cursor.execute('''
            SELECT fs.feature_name, COUNT(*) as usage_count
            FROM feature_usage_stats fs
            JOIN navigation_config nc ON fs.feature_name = nc.nav_item_id
            WHERE fs.created_at >= datetime('now', '-30 days')
            GROUP BY fs.feature_name
            ORDER BY usage_count DESC
        ''')
        usage_ranking = [dict(row) for row in cursor.fetchall()]

        # 生成排序建议
        if len(usage_ranking) > 1:
            current_order = {}
            cursor.execute('''
                SELECT nav_item_id, order_index
                FROM navigation_config
                ORDER BY order_index
            ''')
            for row in cursor.fetchall():
                current_order[row['nav_item_id']] = row['order_index']

            # 找出使用率高但排序靠后的项
            for i, item in enumerate(usage_ranking):
                nav_item_id = item['feature_name']
                if nav_item_id in current_order:
                    if current_order[nav_item_id] > i + 1:
                        suggestions.append({
                            'type': 'reorder',
                            'nav_item_id': nav_item_id,
                            'message': f"'{nav_item_id}' 使用频率较高（{item['usage_count']}次），建议提升排序",
                            'current_order': current_order[nav_item_id],
                            'suggested_order': i + 1
                        })

        # 2. 根据反馈统计建议优化
        cursor.execute('''
            SELECT category, COUNT(*) as feedback_count,
                   AVG(CASE WHEN rating IS NOT NULL THEN rating END) as avg_rating
            FROM user_feedback
            WHERE feedback_type = 'navigation' AND created_at >= datetime('now', '-30 days')
            GROUP BY category
        ''')
        feedback_stats = [dict(row) for row in cursor.fetchall()]

        for stat in feedback_stats:
            if stat['avg_rating'] and stat['avg_rating'] < 3.0:
                suggestions.append({
                    'type': 'improve',
                    'category': stat['category'],
                    'message': f"'{stat['category']}' 分类评分较低（{stat['avg_rating']:.1f}星），建议优化布局或名称",
                    'feedback_count': stat['feedback_count']
                })

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'suggestions': suggestions,
                'usage_ranking': usage_ranking[:10],
                'feedback_stats': feedback_stats
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
