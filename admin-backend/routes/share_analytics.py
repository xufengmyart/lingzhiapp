# -*- coding: utf-8 -*-
"""
分享系统增强功能
包含分享点击统计、转化率统计、排行榜、推荐奖励机制
"""

from flask import Blueprint, jsonify, request
from functools import wraps
import sqlite3
import os
from datetime import datetime, timedelta

share_analytics_bp = Blueprint('share_analytics', __name__)

# 数据库路径
DB_PATH = os.getenv('DATABASE_PATH', 'data/lingzhi_ecosystem.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def auth_required(f):
    """认证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        # 使用JWT验证token
        import jwt
        from config import config
        JWT_SECRET = config.JWT_SECRET_KEY
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'Token无效'}), 401
            return f(user_id=user_id, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token无效'}), 401
    return decorated

def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        # 使用JWT验证token
        import jwt
        from config import config
        JWT_SECRET = config.JWT_SECRET_KEY
        
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            user_id = payload.get('user_id')
            if not user_id:
                return jsonify({'success': False, 'message': 'Token无效'}), 401
            
            # 检查是否是管理员
            conn = get_db_connection()
            user = conn.execute('SELECT id, username FROM users WHERE id = ?', (user_id,)).fetchone()
            conn.close()
            
            if not user or user['username'] != 'admin':
                return jsonify({'success': False, 'message': '需要管理员权限'}), 403
            
            return f(user_id=user_id, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': 'Token无效'}), 401
    return decorated

@share_analytics_bp.route('/share/click', methods=['POST'])
def track_share_click():
    """记录分享点击"""
    try:
        data = request.json
        referral_code = data.get('referral_code')
        article_id = data.get('article_id')
        platform = data.get('platform', 'link')
        user_agent = request.headers.get('User-Agent', '')
        ip_address = request.remote_addr
        
        if not referral_code:
            return jsonify({'success': False, 'message': '推荐码不能为空'}), 400
        
        conn = get_db_connection()
        
        # 更新分享统计
        conn.execute('''
            UPDATE share_stats
            SET click_count = click_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE referral_code = ? AND article_id = ?
        ''', (referral_code, article_id))
        
        # 记录点击日志
        conn.execute('''
            INSERT INTO share_clicks (
                referral_code, article_id, platform, ip_address, 
                user_agent, clicked_at
            ) VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (referral_code, article_id, platform, ip_address, user_agent))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '点击记录成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@share_analytics_bp.route('/share/registration', methods=['POST'])
def track_share_registration():
    """记录分享带来的注册"""
    try:
        data = request.json
        referral_code = data.get('referral_code')
        new_user_id = data.get('new_user_id')
        
        if not referral_code or not new_user_id:
            return jsonify({'success': False, 'message': '参数不完整'}), 400
        
        conn = get_db_connection()
        
        # 获取分享信息
        share = conn.execute('''
            SELECT user_id, article_id FROM share_stats 
            WHERE referral_code = ?
        ''', (referral_code,)).fetchone()
        
        if not share:
            conn.close()
            return jsonify({'success': False, 'message': '分享不存在'}), 404
        
        # 更新注册统计
        conn.execute('''
            UPDATE share_stats
            SET registration_count = registration_count + 1,
                updated_at = CURRENT_TIMESTAMP
            WHERE referral_code = ?
        ''', (referral_code,))
        
        # 发放奖励
        reward_amount = 50  # 注册奖励积分
        conn.execute('''
            UPDATE users
            SET points = points + ?
            WHERE id = ?
        ''', (reward_amount, share['user_id']))
        
        # 记录奖励日志
        conn.execute('''
            INSERT INTO reward_logs (
                referrer_id, referee_id, reward_type, amount, created_at
            ) VALUES (?, ?, 'registration', ?, CURRENT_TIMESTAMP)
        ''', (share['user_id'], new_user_id, reward_amount))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '注册记录成功，奖励已发放'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@share_analytics_bp.route('/share/conversion', methods=['GET'])
@auth_required
def get_conversion_stats(user_id):
    """获取转化率统计"""
    try:
        days = request.args.get('days', 7, type=int)
        start_date = datetime.now() - timedelta(days=days)
        
        conn = get_db_connection()
        
        # 获取用户的分享统计
        stats = conn.execute('''
            SELECT 
                SUM(share_count) as total_shares,
                SUM(click_count) as total_clicks,
                SUM(registration_count) as total_registrations
            FROM share_stats
            WHERE user_id = ? AND created_at >= ?
        ''', (user_id, start_date.strftime('%Y-%m-%d'))).fetchone()
        
        total_shares = stats['total_shares'] or 0
        total_clicks = stats['total_clicks'] or 0
        total_registrations = stats['total_registrations'] or 0
        
        # 计算转化率
        click_rate = (total_clicks / total_shares * 100) if total_shares > 0 else 0
        registration_rate = (total_registrations / total_clicks * 100) if total_clicks > 0 else 0
        
        # 获取每日趋势
        daily_stats = conn.execute('''
            SELECT 
                DATE(created_at) as date,
                SUM(share_count) as shares,
                SUM(click_count) as clicks,
                SUM(registration_count) as registrations
            FROM share_stats
            WHERE user_id = ? AND created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date DESC
        ''', (user_id, start_date.strftime('%Y-%m-%d'))).fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'summary': {
                    'total_shares': total_shares,
                    'total_clicks': total_clicks,
                    'total_registrations': total_registrations,
                    'click_rate': round(click_rate, 2),
                    'registration_rate': round(registration_rate, 2)
                },
                'daily': [
                    {
                        'date': stat['date'],
                        'shares': stat['shares'],
                        'clicks': stat['clicks'],
                        'registrations': stat['registrations']
                    }
                    for stat in daily_stats
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@share_analytics_bp.route('/share/leaderboard', methods=['GET'])
def get_share_leaderboard():
    """获取分享排行榜"""
    try:
        period = request.args.get('period', 'week')  # week, month, all
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db_connection()
        
        # 计算日期范围
        if period == 'week':
            start_date = datetime.now() - timedelta(days=7)
        elif period == 'month':
            start_date = datetime.now() - timedelta(days=30)
        else:
            start_date = None
        
        # 构建查询
        if start_date:
            date_filter = f"AND s.created_at >= '{start_date.strftime('%Y-%m-%d')}'"
        else:
            date_filter = ""
        
        # 获取排行榜数据
        leaderboard = conn.execute(f'''
            SELECT 
                u.id,
                u.username,
                u.username as nickname,
                SUM(s.share_count) as total_shares,
                SUM(s.click_count) as total_clicks,
                SUM(s.registration_count) as total_registrations
            FROM share_stats s
            JOIN users u ON s.user_id = u.id
            WHERE 1=1 {date_filter}
            GROUP BY u.id
            ORDER BY total_registrations DESC
            LIMIT ?
        ''', (limit,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'rank': idx + 1,
                    'user_id': item['id'],
                    'username': item['username'],
                    'nickname': item['nickname'],
                    'total_shares': item['total_shares'],
                    'total_clicks': item['total_clicks'],
                    'total_registrations': item['total_registrations']
                }
                for idx, item in enumerate(leaderboard)
            ]
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@share_analytics_bp.route('/referral/tree', methods=['GET'])
@admin_required
def get_referral_tree(user_id):
    """获取推荐关系树（可视化）"""
    try:
        conn = get_db_connection()
        
        # 获取所有推荐关系
        referrals = conn.execute('''
            SELECT 
                u1.id as referrer_id,
                u1.username as referrer_username,
                u1.username as referrer_nickname,
                u2.id as referee_id,
                u2.username as referee_username,
                u2.username as referee_nickname,
                u2.created_at as registration_date,
                u2.points as referee_points
            FROM users u1
            JOIN users u2 ON u1.id = u2.referrer_id
            ORDER BY u1.id, u2.created_at
        ''').fetchall()
        
        # 构建树形结构
        tree = {}
        for ref in referrals:
            referrer_id = ref['referrer_id']
            
            if referrer_id not in tree:
                tree[referrer_id] = {
                    'id': ref['referrer_id'],
                    'username': ref['referrer_username'],
                    'nickname': ref['referrer_nickname'],
                    'referees': []
                }
            
            tree[referrer_id]['referees'].append({
                'id': ref['referee_id'],
                'username': ref['referee_username'],
                'nickname': ref['referee_nickname'],
                'registration_date': ref['registration_date'],
                'points': ref['referee_points']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': list(tree.values())
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@share_analytics_bp.route('/referral/rewards', methods=['GET'])
@admin_required
def get_referral_rewards(user_id):
    """获取推荐奖励记录"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        offset = (page - 1) * per_page
        
        conn = get_db_connection()
        
        # 获取奖励记录
        rewards = conn.execute('''
            SELECT 
                r.id,
                r.referrer_id,
                u.username as referrer_username,
                u.username as referrer_nickname,
                r.referee_id,
                u2.username as referee_username,
                r.reward_type,
                r.amount,
                r.created_at
            FROM reward_logs r
            JOIN users u ON r.referrer_id = u.id
            JOIN users u2 ON r.referee_id = u2.id
            ORDER BY r.created_at DESC
            LIMIT ? OFFSET ?
        ''', (per_page, offset)).fetchall()
        
        # 获取总数
        total = conn.execute('SELECT COUNT(*) as count FROM reward_logs').fetchone()['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': [
                {
                    'id': item['id'],
                    'referrer_id': item['referrer_id'],
                    'referrer_username': item['referrer_username'],
                    'referrer_nickname': item['referrer_nickname'],
                    'referee_id': item['referee_id'],
                    'referee_username': item['referee_username'],
                    'reward_type': item['reward_type'],
                    'amount': item['amount'],
                    'created_at': item['created_at']
                }
                for item in rewards
            ],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'total_pages': (total + per_page - 1) // per_page
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@share_analytics_bp.route('/referral/rewards/manual', methods=['POST'])
@admin_required
def grant_manual_reward(user_id):
    """手动发放奖励"""
    try:
        data = request.json
        target_user_id = data.get('target_user_id')
        amount = data.get('amount', 0)
        reason = data.get('reason', '手动奖励')
        
        if not target_user_id:
            return jsonify({'success': False, 'message': '用户ID不能为空'}), 400
        
        conn = get_db_connection()
        
        # 更新用户积分
        conn.execute('''
            UPDATE users
            SET points = points + ?
            WHERE id = ?
        ''', (amount, target_user_id))
        
        # 记录奖励日志
        conn.execute('''
            INSERT INTO reward_logs (
                referrer_id, referee_id, reward_type, amount, created_at
            ) VALUES (?, 0, 'manual', ?, CURRENT_TIMESTAMP)
        ''', (target_user_id, amount))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '奖励发放成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
