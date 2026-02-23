"""
推荐系统路由蓝图
包含推荐关系管理、推荐码生成、推荐统计等功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
import random
import string
from datetime import datetime, timedelta

referral_bp = Blueprint('referral', __name__)

# 导入配置
from config import config
DATABASE = config.DATABASE_PATH

# 辅助函数
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_referral_code():
    """生成推荐码"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# ============ 推荐统计 ============

@referral_bp.route('/user/referral-stats', methods=['GET'])
def get_referral_stats():
    """获取用户推荐统计"""
    try:
        # TODO: 验证JWT令牌
        # user_id = get_current_user_id()

        # 暂时使用测试用户ID
        user_id = int(request.args.get('user_id', 1))

        conn = get_db()
        cursor = conn.cursor()

        # 统计推荐人数
        cursor.execute(
            "SELECT COUNT(*) as count FROM referral_relationships WHERE referrer_id = ?",
            (user_id,)
        )
        total_referrals = cursor.fetchone()['count']

        # 统计今日推荐人数
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM referral_relationships
            WHERE referrer_id = ? AND DATE(created_at) = DATE('now')
            """,
            (user_id,)
        )
        today_referrals = cursor.fetchone()['count']

        # 统计推荐的灵值奖励
        cursor.execute(
            """
            SELECT SUM(lingzhi_reward) as total
            FROM referral_relationships
            WHERE referrer_id = ? AND reward_status = 'claimed'
            """,
            (user_id,)
        )
        total_rewards = cursor.fetchone()['total'] or 0

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'total_referrals': total_referrals,
                'today_referrals': today_referrals,
                'total_rewards': total_rewards
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取推荐统计失败: {str(e)}'
        }), 500

@referral_bp.route('/user/referrals', methods=['GET'])
def get_referrals():
    """获取用户推荐列表"""
    try:
        # TODO: 验证JWT令牌
        user_id = int(request.args.get('user_id', 1))

        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 获取推荐列表
        cursor.execute(
            """
            SELECT
                rr.id,
                rr.referred_user_id,
                rr.lingzhi_reward,
                rr.reward_status,
                rr.created_at,
                u.username,
                u.avatar_url,
                u.total_lingzhi
            FROM referral_relationships rr
            LEFT JOIN users u ON rr.referred_user_id = u.id
            WHERE rr.referrer_id = ?
            ORDER BY rr.created_at DESC
            LIMIT ? OFFSET ?
            """,
            (user_id, page_size, offset)
        )
        referrals = [dict(row) for row in cursor.fetchall()]

        # 获取总数
        cursor.execute(
            "SELECT COUNT(*) as total FROM referral_relationships WHERE referrer_id = ?",
            (user_id,)
        )
        total = cursor.fetchone()['total']

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'referrals': referrals,
                'pagination': {
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取推荐列表失败: {str(e)}'
        }), 500

# ============ 推荐码验证 ============

@referral_bp.route('/user/referral/validate', methods=['POST'])
def validate_referral_code_post():
    """验证推荐码"""
    try:
        data = request.json
        referral_code = data.get('referral_code')

        if not referral_code:
            return jsonify({
                'success': False,
                'message': '推荐码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询推荐码
        cursor.execute(
            """
            SELECT
                r.referrer_id,
                u.username,
                u.avatar_url
            FROM referral_codes r
            LEFT JOIN users u ON r.referrer_id = u.id
            WHERE r.code = ? AND r.status = 'active' AND r.expires_at > CURRENT_TIMESTAMP
            """,
            (referral_code,)
        )
        referral = cursor.fetchone()

        if not referral:
            conn.close()
            return jsonify({
                'success': False,
                'message': '推荐码无效或已过期'
            }), 400

        conn.close()

        return jsonify({
            'success': True,
            'message': '推荐码验证成功',
            'data': {
                'referrer_id': referral['referrer_id'],
                'referrer_username': referral['username'],
                'referrer_avatar': referral['avatar_url']
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证推荐码失败: {str(e)}'
        }), 500

# ============ 应用推荐码 ============

@referral_bp.route('/user/referral/apply', methods=['POST'])
def apply_referral_code():
    """应用推荐码（注册时绑定推荐关系）"""
    try:
        # TODO: 验证JWT令牌
        data = request.json
        user_id = data.get('user_id')
        referral_code = data.get('referral_code')

        if not user_id or not referral_code:
            return jsonify({
                'success': False,
                'message': '用户ID和推荐码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询推荐码
        cursor.execute(
            "SELECT referrer_id, id FROM referral_codes WHERE code = ? AND status = 'active'",
            (referral_code,)
        )
        referral = cursor.fetchone()

        if not referral:
            conn.close()
            return jsonify({
                'success': False,
                'message': '推荐码无效'
            }), 400

        referrer_id = referral['referrer_id']

        # 检查是否已经绑定过推荐关系
        cursor.execute(
            "SELECT id FROM referral_relationships WHERE referred_user_id = ?",
            (user_id,)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '您已经绑定过推荐关系'
            }), 400

        # 检查不能推荐自己
        if referrer_id == user_id:
            conn.close()
            return jsonify({
                'success': False,
                'message': '不能使用自己的推荐码'
            }), 400

        # 创建推荐关系
        cursor.execute(
            """
            INSERT INTO referral_relationships (referrer_id, referred_user_id, level)
            VALUES (?, ?, 1)
            """,
            (referrer_id, user_id)
        )

        # 奖励推荐人灵值
        reward_lingzhi = 10  # 推荐奖励10灵值
        cursor.execute(
            "UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?",
            (reward_lingzhi, referrer_id)
        )

        # 更新推荐码状态（标记为已使用）
        cursor.execute(
            "UPDATE referral_codes SET used_count = used_count + 1 WHERE id = ?",
            (referral['id'],)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '推荐码应用成功',
            'data': {
                'reward_lingzhi': reward_lingzhi
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'应用推荐码失败: {str(e)}'
        }), 500

# ============ 生成推荐码 ============

@referral_bp.route('/user/referral/code', methods=['GET'])
def get_my_referral_code():
    """获取我的推荐码（如果没有则生成）"""
    try:
        # 验证JWT令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'message': '未授权，请提供认证信息'}), 401

        # 提取 token（Bearer token）
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header

        # 验证 token
        import jwt
        from datetime import datetime
        from config import config

        try:
            payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
            # 检查是否过期
            if datetime.utcnow().timestamp() > payload.get('exp', 0):
                return jsonify({'success': False, 'message': 'Token 已过期'}), 401

            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token 已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': '无效的 Token'}), 401

        conn = get_db()
        cursor = conn.cursor()

        # 查询用户是否已有推荐码
        cursor.execute(
            "SELECT code, expires_at FROM referral_codes WHERE referrer_id = ? ORDER BY created_at DESC LIMIT 1",
            (user_id,)
        )
        existing_code = cursor.fetchone()

        # 如果有推荐码且未过期，直接返回
        if existing_code:
            expires_at = datetime.strptime(existing_code['expires_at'], '%Y-%m-%d %H:%M:%S')
            if expires_at > datetime.now() + timedelta(days=7):
                conn.close()
                return jsonify({
                    'success': True,
                    'data': {
                        'code': existing_code['code'],
                        'expires_at': existing_code['expires_at']
                    }
                })

        # 生成新的推荐码
        new_code = generate_referral_code()
        expires_at = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')

        # 检查推荐码是否已存在
        cursor.execute("SELECT id FROM referral_codes WHERE code = ?", (new_code,))
        while cursor.fetchone():
            new_code = generate_referral_code()
            cursor.execute("SELECT id FROM referral_codes WHERE code = ?", (new_code,))

        # 插入新的推荐码
        cursor.execute(
            """
            INSERT INTO referral_codes (referrer_id, code, status, expires_at, used_count, created_at)
            VALUES (?, ?, 'active', ?, 0, ?)
            """,
            (user_id, new_code, expires_at, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '推荐码生成成功',
            'data': {
                'code': new_code,
                'expires_at': expires_at
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'获取推荐码失败: {str(e)}'
        }), 500
