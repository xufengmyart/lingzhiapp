"""
用户活动路由
提供用户动态、活跃度、用户详情等功能
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
import sqlite3

from config import config

user_activities_bp = Blueprint('user_activities', __name__)

DATABASE = config.DATABASE_PATH

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def mask_username(username):
    """
    脱敏用户名
    - admin: 显示为"管理员"
    - 其他用户: 显示前2位+***
    """
    if not username:
        return '用户'

    if username == 'admin':
        return '管理员'

    # 其他用户，显示前2位+***
    if len(username) > 2:
        return username[:2] + '***'
    else:
        return username[0] + '***' if username else '***'

def mask_email(email):
    """脱敏邮箱"""
    if not email or '@' not in email:
        return ''
    parts = email.split('@')
    username = parts[0]
    domain = parts[1]

    if len(username) <= 2:
        masked_username = username[0] + '***'
    else:
        masked_username = username[:2] + '***' + username[-1:]

    return f"{masked_username}@{domain}"

def mask_phone(phone):
    """脱敏手机号"""
    if not phone or len(phone) < 11:
        return ''
    return phone[:3] + '****' + phone[-4:]

@user_activities_bp.route('/company/users/activities', methods=['GET'])
def get_user_activities():
    """
    获取用户活动列表
    支持分页和筛选
    整合签到记录、充值记录、用户注册、灵值消费、贡献值、互动等数据
    返回脱敏后的用户名

    参数:
    - page: 页码（默认1）
    - page_size: 每页数量（默认20，最大100）
    - type: 活动类型筛选（register, active, achievement, upgrade, consume, contribution, interaction）
    - username: 用户名搜索（支持模糊匹配）
    """
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        activity_type = request.args.get('type', '')
        username_search = request.args.get('username', '')

        # 限制每页最多100条
        page_size = min(page_size, 100)
        page = max(page, 1)

        # 计算偏移量
        offset = (page - 1) * page_size

        conn = get_db_connection()

        activities = []

        # 构建筛选条件
        type_filter = ""
        params = []

        # 类型筛选
        if activity_type:
            # 根据类型决定查询哪些表
            if activity_type == 'register':
                type_filter = "WHERE 1=1"
            elif activity_type == 'achievement':
                type_filter = "WHERE 1=1"
            elif activity_type == 'active':
                type_filter = "WHERE 1=1"
            elif activity_type == 'consume':
                type_filter = "WHERE 1=1"
            elif activity_type == 'contribution':
                type_filter = "WHERE 1=1"
            elif activity_type == 'interaction':
                type_filter = "WHERE 1=1"
            else:
                type_filter = "WHERE 1=1"
        else:
            type_filter = "WHERE 1=1"

        # 用户名筛选
        if username_search:
            type_filter += " AND u.username LIKE ?"
            params.append(f"%{username_search}%")

        # 1. 获取最近的签到记录
        if not activity_type or activity_type == 'achievement':
            checkin_where = type_filter
            checkin_params = params.copy()

            checkin_records = conn.execute(f'''
                SELECT
                    cr.id,
                    u.username,
                    cr.checkin_date as created_at,
                    cr.lingzhi_earned as lingzhi,
                    '签到' as action,
                    '每日签到，获得' || cr.lingzhi_earned || '灵值' as description,
                    'achievement' as type
                FROM checkin_records cr
                JOIN users u ON cr.user_id = u.id
                {checkin_where}
                ORDER BY cr.checkin_date DESC
                LIMIT ? OFFSET ?
            ''', checkin_params + [page_size // 6, offset]).fetchall()

            for record in checkin_records:
                activities.append({
                    'id': record['id'],
                    'username': record['username'],
                    'action': record['action'],
                    'description': record['description'],
                    'type': record['type'],
                    'createdAt': record['created_at'],
                    'lingzhi': record['lingzhi'] or 0
                })

        # 2. 获取最近的充值记录
        if not activity_type or activity_type == 'active':
            recharge_where = type_filter
            recharge_params = params.copy()

            recharge_records = conn.execute(f'''
                SELECT
                    r.id,
                    u.username,
                    r.created_at,
                    r.amount as lingzhi,
                    '充值' as action,
                    '充值' || r.amount || '灵值' as description,
                    'active' as type
                FROM recharge_records r
                JOIN users u ON r.user_id = u.id
                {recharge_where}
                ORDER BY r.created_at DESC
                LIMIT ? OFFSET ?
            ''', recharge_params + [page_size // 6, offset]).fetchall()

            for record in recharge_records:
                activities.append({
                    'id': record['id'] + 10000,  # 避免ID冲突
                    'username': record['username'],
                    'action': record['action'],
                    'description': record['description'],
                    'type': record['type'],
                    'createdAt': record['created_at'],
                    'lingzhi': record['lingzhi'] or 0
                })

        # 3. 获取最近注册的用户
        if not activity_type or activity_type == 'register':
            register_where = type_filter.replace("WHERE 1=1", "WHERE 1=1")
            register_params = params.copy()
            register_where += " AND u.created_at >= date('now', '-30 days')"

            new_users = conn.execute(f'''
                SELECT
                    u.id,
                    u.username,
                    u.created_at,
                    100 as lingzhi,
                    '注册加入' as action,
                    '新用户注册，获得新人奖励100灵值' as description,
                    'register' as type
                FROM users u
                {register_where}
                ORDER BY u.created_at DESC
                LIMIT ? OFFSET ?
            ''', register_params + [page_size // 6, offset]).fetchall()

            for record in new_users:
                activities.append({
                    'id': record['id'] + 20000,  # 避免ID冲突
                    'username': record['username'],
                    'action': record['action'],
                    'description': record['description'],
                    'type': record['type'],
                    'createdAt': record['created_at'],
                    'lingzhi': record['lingzhi']
                })

        # 4. 获取灵值消费记录
        if not activity_type or activity_type == 'consume':
            consume_where = type_filter
            consume_params = params.copy()

            try:
                consume_records = conn.execute(f'''
                    SELECT
                        lcr.id,
                        u.username,
                        lcr.created_at,
                        lcr.lingzhi_amount as lingzhi,
                        '消费' as action,
                        lcr.description || '，消费' || lcr.lingzhi_amount || '灵值' as description,
                        'consume' as type
                    FROM lingzhi_consumption_records lcr
                    JOIN users u ON lcr.user_id = u.id
                    {consume_where}
                    ORDER BY lcr.created_at DESC
                    LIMIT ? OFFSET ?
                ''', consume_params + [page_size // 6, offset]).fetchall()

                for record in consume_records:
                    activities.append({
                        'id': record['id'] + 30000,  # 避免ID冲突
                        'username': record['username'],
                        'action': record['action'],
                        'description': record['description'],
                        'type': record['type'],
                        'createdAt': record['created_at'],
                        'lingzhi': -(record['lingzhi'] or 0)  # 消费为负数
                    })
            except Exception as e:
                print(f"获取灵值消费记录失败: {e}")

        # 5. 获取贡献值记录
        if not activity_type or activity_type == 'contribution':
            contrib_where = type_filter
            contrib_params = params.copy()

            try:
                contrib_records = conn.execute(f'''
                    SELECT
                        cr.id,
                        u.username,
                        cr.created_at,
                        cr.amount as lingzhi,
                        '贡献' as action,
                        '贡献' || cr.amount || '灵值' as description,
                        'contribution' as type
                    FROM contribution_records cr
                    JOIN users u ON cr.user_id = u.id
                    {contrib_where}
                    ORDER BY cr.created_at DESC
                    LIMIT ? OFFSET ?
                ''', contrib_params + [page_size // 6, offset]).fetchall()

                for record in contrib_records:
                    activities.append({
                        'id': record['id'] + 40000,  # 避免ID冲突
                        'username': record['username'],
                        'action': record['action'],
                        'description': record['description'],
                        'type': record['type'],
                        'createdAt': record['created_at'],
                        'lingzhi': record['lingzhi'] or 0
                    })
            except Exception as e:
                print(f"获取贡献值记录失败: {e}")

        conn.close()

        # 按时间排序（最新的在前）
        activities.sort(key=lambda x: x['createdAt'], reverse=True)

        # 按类型筛选（如果在查询时没有应用）
        if activity_type:
            activities = [a for a in activities if a['type'] == activity_type]

        # 计算总数
        total = len(activities)

        # 分页
        start_idx = offset
        end_idx = offset + page_size
        paginated_activities = activities[start_idx:end_idx]

        # 脱敏用户名
        for activity in paginated_activities:
            activity['username'] = mask_username(activity['username'])

        # 计算分页信息
        total_pages = (total + page_size - 1) // page_size

        return jsonify({
            'success': True,
            'message': '获取用户活动成功',
            'data': paginated_activities,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': total_pages,
                'has_next': page < total_pages,
                'has_prev': page > 1
            }
        })

    except Exception as e:
        print(f"获取用户活动失败: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'message': f'获取用户活动失败: {str(e)}',
            'data': [],
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': 0,
                'total_pages': 0,
                'has_next': False,
                'has_prev': False
            }
        }), 500

# ============ 用户详情 ============

@user_activities_bp.route('/company/users/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    """
    获取用户详情（脱敏）
    返回用户的基本信息和统计数据，所有敏感信息都已脱敏
    """
    try:
        conn = get_db_connection()

        # 查询用户基本信息
        user = conn.execute('''
            SELECT
                id,
                username,
                email,
                phone,
                avatar_url as avatar,
                total_lingzhi,
                status,
                created_at,
                updated_at,
                last_login_at,
                bio,
                location,
                website
            FROM users
            WHERE id = ?
        ''', (user_id,)).fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 统计签到次数
        checkin_count = conn.execute(
            'SELECT COUNT(*) as count FROM checkin_records WHERE user_id = ?',
            (user_id,)
        ).fetchone()['count']

        # 统计充值次数和总金额
        recharge_stats = conn.execute(
            'SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total FROM recharge_records WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        # 统计消费次数和总金额
        consume_stats = conn.execute(
            'SELECT COUNT(*) as count, COALESCE(SUM(lingzhi_amount), 0) as total FROM lingzhi_consumption_records WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        # 获取最近的活动
        recent_activities = conn.execute('''
            SELECT
                '签到' as action,
                checkin_date as created_at,
                lingzhi_earned as lingzhi,
                'achievement' as type
            FROM checkin_records
            WHERE user_id = ?
            UNION ALL
            SELECT
                '充值' as action,
                created_at,
                amount as lingzhi,
                'active' as type
            FROM recharge_records
            WHERE user_id = ?
            UNION ALL
            SELECT
                '消费' as action,
                created_at,
                lingzhi_amount as lingzhi,
                'consume' as type
            FROM lingzhi_consumption_records
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id, user_id, user_id)).fetchall()

        conn.close()

        # 构建脱敏的用户详情
        user_detail = {
            'id': user['id'],
            'username': mask_username(user['username']),
            'email': mask_email(user['email']),
            'phone': mask_phone(user['phone']),
            'avatar': user['avatar'] or '',
            'totalLingzhi': user['total_lingzhi'] or 0,
            'status': user['status'] or 'active',
            'createdAt': user['created_at'] or '',
            'updatedAt': user['updated_at'] or '',
            'lastLoginAt': user['last_login_at'] or '',
            'bio': user['bio'] or '',
            'location': user['location'] or '',
            'website': user['website'] or '',
            'statistics': {
                'checkinCount': checkin_count,
                'rechargeCount': recharge_stats['count'] or 0,
                'rechargeTotal': float(recharge_stats['total'] or 0),
                'consumeCount': consume_stats['count'] or 0,
                'consumeTotal': float(consume_stats['total'] or 0)
            },
            'recentActivities': [
                {
                    'action': activity['action'],
                    'createdAt': activity['created_at'],
                    'lingzhi': activity['lingzhi'],
                    'type': activity['type']
                }
                for activity in recent_activities
            ]
        }

        return jsonify({
            'success': True,
            'message': '获取用户详情成功',
            'data': user_detail
        })

    except Exception as e:
        print(f"获取用户详情失败: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'message': f'获取用户详情失败: {str(e)}'
        }), 500

@user_activities_bp.route('/company/users/summary', methods=['GET'])
def get_users_summary():
    """
    获取用户统计摘要
    返回用户总数、活跃用户数等统计信息
    """
    try:
        conn = get_db_connection()

        # 总用户数
        total_users = conn.execute(
            'SELECT COUNT(*) as count FROM users'
        ).fetchone()['count']

        # 活跃用户数（7天内登录）
        active_users = conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE last_login_at >= datetime('now', '-7 days')"
        ).fetchone()['count']

        # 今日新增
        new_users_today = conn.execute(
            "SELECT COUNT(*) as count FROM users WHERE date(created_at) = date('now')"
        ).fetchone()['count']

        # 今日签到
        checkin_today = conn.execute(
            "SELECT COUNT(*) as count FROM checkin_records WHERE checkin_date = date('now')"
        ).fetchone()['count']

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取用户统计成功',
            'data': {
                'totalUsers': total_users,
                'activeUsers': active_users,
                'newUsersToday': new_users_today,
                'checkinToday': checkin_today
            }
        })

    except Exception as e:
        print(f"获取用户统计失败: {e}")
        import traceback
        traceback.print_exc()

        return jsonify({
            'success': False,
            'message': f'获取用户统计失败: {str(e)}'
        }), 500
