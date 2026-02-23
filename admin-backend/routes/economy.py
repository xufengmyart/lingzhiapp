"""
经济系统路由
提供灵值配置、充值档位、分红池等功能
"""

from flask import Blueprint, jsonify, request
from database import get_db
from datetime import datetime

economy_bp = Blueprint('economy', __name__)


# ============ 获取灵值配置 ============

@economy_bp.route('/admin/economy/config', methods=['GET'])
def get_lingzhi_config():
    """获取灵值配置"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 默认灵值配置
        default_config = {
            # 基础配置
            'initial_lingzhi': 100,           # 新用户初始灵值
            'daily_limit': 500,               # 每日灵值上限

            # 签到奖励
            'checkin_reward': 10,             # 每日签到奖励
            'checkin_consecutive_reward': 50, # 连续签到奖励
            'max_consecutive_days': 7,        # 最大连续签到天数

            # 对话消耗
            'conversation_cost': 1,           # 每次对话消耗
            'premium_conversation_cost': 2,   # 高级对话消耗

            # 分红比例
            'dividend_rate': 0.1,             # 分红比例（10%）
            'dividend_threshold': 1000,       # 分红门槛

            # 推荐奖励
            'referral_reward': 50,            # 推荐奖励
            'referral_consume_reward': 10,    # 被推荐人首次消费奖励

            # 任务奖励
            'task_completion_reward': 20,     # 任务完成奖励
            'task_upload_reward': 15,         # 上传任务奖励
        }

        # 尝试从系统配置表获取自定义配置
        try:
            cursor.execute("""
                SELECT key, value FROM system_config
                WHERE category = 'lingzhi'
            """)
            rows = cursor.fetchall()
            for row in rows:
                if row['key'] in default_config:
                    value = row['value']
                    # 转换类型
                    if isinstance(default_config[row['key']], (int, float)):
                        value = float(value) if '.' in str(value) else int(value)
                    default_config[row['key']] = value
        except:
            pass  # 如果系统配置表不存在，使用默认配置

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取灵值配置成功',
            'data': default_config
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取灵值配置失败: {str(e)}',
            'data': None
        }), 500


# ============ 更新灵值配置 ============

@economy_bp.route('/admin/economy/config', methods=['PUT'])
def update_lingzhi_config():
    """更新灵值配置（仅管理员）"""
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'message': '配置数据不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 确保系统配置表存在
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_config (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(100) NOT NULL,
                value TEXT,
                category VARCHAR(50),
                description TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(key, category)
            )
        """)

        # 更新配置
        updated_count = 0
        for key, value in data.items():
            cursor.execute("""
                INSERT INTO system_config (key, value, category, description)
                VALUES (?, ?, 'lingzhi', ?)
                ON CONFLICT(key, category) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, str(value), f'灵值配置: {key}'))
            updated_count += 1

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'成功更新 {updated_count} 项配置',
            'data': {'updated_count': updated_count}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新灵值配置失败: {str(e)}'
        }), 500


# ============ 获取充值档位 ============

@economy_bp.route('/admin/economy/recharge-tiers', methods=['GET'])
def get_recharge_tiers():
    """获取充值档位列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, name, description, price,
                base_lingzhi, bonus_lingzhi, bonus_percentage,
                partner_level, benefits, status, sort_order
            FROM recharge_tiers
            WHERE status = 'active'
            ORDER BY sort_order ASC
        """)

        tiers = []
        for row in cursor.fetchall():
            tiers.append({
                'id': row['id'],
                'name': row['name'],
                'description': row['description'],
                'price': float(row['price']),
                'baseLingzhi': row['base_lingzhi'],
                'bonusLingzhi': row['bonus_lingzhi'],
                'bonusPercentage': row['bonus_percentage'],
                'partnerLevel': row['partner_level'],
                'benefits': eval(row['benefits']) if row['benefits'] else [],
                'status': row['status'],
                'sortOrder': row['sort_order']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取充值档位成功',
            'data': tiers
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取充值档位失败: {str(e)}',
            'data': []
        }), 500


# ============ 获取分红池信息 ============

@economy_bp.route('/admin/economy/dividend-pool', methods=['GET'])
def get_dividend_pool():
    """获取分红池信息"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 获取分红池总额
        cursor.execute("SELECT SUM(amount) as total FROM dividend_pool")
        total_pool = cursor.fetchone()['total'] or 0

        # 获取今日分红
        today = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("""
            SELECT SUM(amount) as today_total
            FROM dividend_records
            WHERE DATE(created_at) = ?
        """, (today,))
        today_dividend = cursor.fetchone()['today_total'] or 0

        # 获取用户总数
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE status = 'active'")
        user_count = cursor.fetchone()['count'] or 0

        # 获取分红记录
        cursor.execute("""
            SELECT
                dr.id, dr.user_id, u.username, dr.amount, dr.created_at
            FROM dividend_records dr
            LEFT JOIN users u ON dr.user_id = u.id
            ORDER BY dr.created_at DESC
            LIMIT 10
        """)

        recent_records = []
        for row in cursor.fetchall():
            recent_records.append({
                'id': row['id'],
                'userId': row['user_id'],
                'username': row['username'],
                'amount': float(row['amount']),
                'createdAt': row['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取分红池信息成功',
            'data': {
                'totalPool': float(total_pool),
                'todayDividend': float(today_dividend),
                'userCount': user_count,
                'recentRecords': recent_records
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分红池信息失败: {str(e)}',
            'data': None
        }), 500


# ============ 获取用户灵值记录 ============

@economy_bp.route('/admin/economy/user/<int:user_id>/records', methods=['GET'])
def get_user_lingzhi_records(user_id):
    """获取用户灵值消费记录"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 获取用户信息
        cursor.execute("SELECT id, username, total_lingzhi FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 获取总数
        cursor.execute(
            "SELECT COUNT(*) as total FROM lingzhi_consumption_records WHERE user_id = ?",
            (user_id,)
        )
        total = cursor.fetchone()['total']

        # 获取记录
        cursor.execute("""
            SELECT
                id, consumption_type, consumption_item, lingzhi_amount,
                description, created_at
            FROM lingzhi_consumption_records
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, page_size, offset))

        records = []
        for row in cursor.fetchall():
            records.append({
                'id': row['id'],
                'type': row['consumption_type'],
                'item': row['consumption_item'],
                'amount': float(row['lingzhi_amount']),
                'description': row['description'],
                'createdAt': row['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取灵值记录成功',
            'data': {
                'userInfo': {
                    'id': user['id'],
                    'username': user['username'],
                    'totalLingzhi': user['total_lingzhi']
                },
                'records': records,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取灵值记录失败: {str(e)}'
        }), 500
