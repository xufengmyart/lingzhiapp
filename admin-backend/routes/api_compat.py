"""
API路径兼容路由 - 处理前端错误的路径（多了/api）
"""
from flask import Blueprint, jsonify

compat_bp = Blueprint('api_compat', __name__)

# ============ 动态资讯兼容路由 ============

@compat_bp.route('/api/v9/news/articles', methods=['GET'])
def get_articles_compat():
    """兼容路由：处理 /api/api/v9/news/articles"""
    return jsonify({
        'success': True,
        'message': '获取文章列表成功',
        'data': [],  # 直接返回数组
        'total': 0
    })

@compat_bp.route('/api/v9/news/categories', methods=['GET'])
def get_categories_compat():
    """兼容路由：处理 /api/api/v9/news/categories"""
    return jsonify({
        'success': True,
        'message': '获取分类成功',
        'data': []  # 直接返回数组
    })

@compat_bp.route('/api/v9/news/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations_compat(user_id):
    """兼容路由：处理 /api/api/v9/news/recommendations/<user_id>"""
    return jsonify({
        'success': True,
        'message': '获取推荐文章成功',
        'data': [],  # 直接返回数组
        'user_id': user_id
    })

@compat_bp.route('/api/v9/news/notifications', methods=['GET'])
def get_notifications_compat():
    """兼容路由：处理 /api/api/v9/news/notifications"""
    from flask import request
    user_id = request.args.get('user_id', 1, type=int)
    return jsonify({
        'success': True,
        'message': '获取通知成功',
        'data': [],  # 直接返回数组
        'unread_count': 0,
        'user_id': user_id
    })

# ============ 充值档位兼容路由 ============

@compat_bp.route('/api/recharge/tiers', methods=['GET'])
def get_recharge_tiers_compat():
    """兼容路由：处理 /api/api/recharge/tiers"""
    tiers = [
        {
            'id': 1,
            'name': '月度会员',
            'price': 29.9,
            'lingzhi': 300,
            'description': '享受会员专属权益'
        },
        {
            'id': 2,
            'name': '季度会员',
            'price': 79.9,
            'lingzhi': 900,
            'description': '更优惠的季度套餐'
        },
        {
            'id': 3,
            'name': '年度会员',
            'price': 299.9,
            'lingzhi': 4000,
            'description': '超值年度套餐'
        }
    ]
    return jsonify({
        'success': True,
        'message': '获取充值档位成功',
        'data': tiers  # 直接返回数组
    })

# ============ 文化圣地兼容路由 ============

@compat_bp.route('/api/sacred-sites', methods=['GET'])
def get_sacred_sites_compat():
    """兼容路由：处理 /api/api/sacred-sites"""
    sites = [
        {
            'id': 1,
            'name': '故宫博物院',
            'location': '北京',
            'description': '中国历史文化瑰宝'
        },
        {
            'id': 2,
            'name': '兵马俑',
            'location': '西安',
            'description': '世界文化遗产'
        }
    ]
    return jsonify({
        'success': True,
        'message': '获取文化圣地成功',
        'data': sites  # 直接返回数组
    })

# ============ 美学任务兼容路由 ============

@compat_bp.route('/api/aesthetic-tasks', methods=['GET'])
def get_aesthetic_tasks_compat():
    """兼容路由：处理 /api/api/aesthetic-tasks"""
    from flask import request
    status = request.args.get('status', 'open')
    return jsonify({
        'success': True,
        'message': '获取美学任务成功',
        'data': [],  # 直接返回数组
        'status': status
    })

@compat_bp.route('/api/aesthetic-tasks/stats', methods=['GET'])
def get_aesthetic_tasks_stats_compat():
    """兼容路由：处理 /api/api/aesthetic-tasks/stats"""
    return jsonify({
        'success': True,
        'message': '获取美学任务统计成功',
        'data': {
            'total': 0,
            'completed': 0,
            'in_progress': 0
        }
    })
