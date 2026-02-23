"""
综合 API 蓝图
包含签到、资产、资源、分红池、项目、商家等所有剩余功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime, timedelta
import jwt
import random
import json

# 导入配置
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

complete_bp = Blueprint('complete', __name__, url_prefix='/api')

DATABASE = config.DATABASE_PATH

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def verify_token(token):
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None


# ==================== 签到系统 ====================

@complete_bp.route('/checkin/status', methods=['GET'])
def get_checkin_status():
    """
    获取签到状态
    响应: { success: true, data: { today: bool, streak: int, ... } }
    """
    try:
        print(f"[DEBUG] 获取签到状态请求开始")
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        print(f"[DEBUG] Token: {token[:20] if token else 'None'}...")
        user_payload = verify_token(token) if token else None

        if not user_payload:
            print(f"[DEBUG] Token验证失败")
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')
        print(f"[DEBUG] 用户ID: {user_id}")
        today = datetime.now().strftime('%Y-%m-%d')

        conn = get_db_connection()
        print(f"[DEBUG] 数据库连接成功")

        # 检查今天是否已签到
        today_checkin = conn.execute(
            'SELECT * FROM checkin_records WHERE user_id = ? AND DATE(checkin_date) = ?',
            (user_id, today)
        ).fetchone()

        # 获取连续签到天数
        streak = 0
        if today_checkin:
            # 计算连续签到
            date = datetime.now().date()
            for i in range(30):  # 最多检查30天
                check_date = (date - timedelta(days=i)).strftime('%Y-%m-%d')
                record = conn.execute(
                    'SELECT * FROM checkin_records WHERE user_id = ? AND DATE(checkin_date) = ?',
                    (user_id, check_date)
                ).fetchone()
                if record:
                    streak += 1
                else:
                    break

        # 获取今日灵值（如果今天已签到）
        today_lingzhi = 0
        if today_checkin:
            today_lingzhi = today_checkin['lingzhi_earned'] if today_checkin['lingzhi_earned'] else 0

        # 获取用户总灵值
        user_data = conn.execute('SELECT total_lingzhi FROM users WHERE id = ?', (user_id,)).fetchone()
        total_lingzhi = user_data['total_lingzhi'] if user_data else 0

        conn.close()

        # 计算连续签到的奖励
        rewards_list = [1, 2, 3, 5, 8, 13, 21, 34]

        # 计算下一次签到奖励（streak+1 天）
        next_streak = streak + 1
        rewards_index = min(next_streak - 1, len(rewards_list) - 1)
        next_rewards = rewards_list[rewards_index]

        # 生成奖励说明
        reward_tips = []
        for i in range(len(rewards_list)):
            day = i + 1
            reward = rewards_list[i]
            if not today_checkin and day == streak + 1:
                reward_tips.append(f"第{day}天: {reward}灵值 ✨")
            elif today_checkin and day == streak:
                reward_tips.append(f"第{day}天: {reward}灵值 ✓")
            else:
                reward_tips.append(f"第{day}天: {reward}灵值")

        # 构建消息
        if today_checkin:
            message = f"今日已签到，连续 {streak} 天，获得 {today_lingzhi} 灵值"
        else:
            message = f"今日尚未签到，签到可获得 {next_rewards} 灵值（连续{streak + 1}天）"

        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'checkedIn': today_checkin is not None,  # 是否已签到（前端使用）
                'today': today_checkin is not None,  # 兼容旧字段
                'streak': streak,
                'canCheckIn': today_checkin is None,
                'rewards': rewards_list,  # 连续签到奖励列表
                'total_lingzhi': total_lingzhi,  # 总灵值
                'todayLingzhi': today_lingzhi,  # 今日获得的灵值
                'nextRewards': next_rewards,  # 下一次签到奖励
                'rewardSchedule': reward_tips,  # 奖励说明
                'rewardTip': f"连续签到奖励：{', '.join(reward_tips[:min(7, len(reward_tips))])}"
            }
        })

    except Exception as e:
        print(f"获取签到状态错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/checkin', methods=['POST'])
def do_checkin():
    """
    执行签到
    响应: { success: true, data: { streak, rewards } }
    """
    try:
        print(f"[DEBUG] 签到请求开始")
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        print(f"[DEBUG] Token: {token[:20] if token else 'None'}...")
        user_payload = verify_token(token) if token else None

        if not user_payload:
            print(f"[DEBUG] Token验证失败")
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')
        print(f"[DEBUG] 用户ID: {user_id}")
        today = datetime.now().strftime('%Y-%m-%d')

        conn = get_db_connection()
        cursor = conn.cursor()
        print(f"[DEBUG] 数据库连接成功")

        # 检查是否已签到
        existing = conn.execute(
            'SELECT * FROM checkin_records WHERE user_id = ? AND DATE(checkin_date) = ?',
            (user_id, today)
        ).fetchone()

        if existing:
            conn.close()
            return jsonify({
                'success': False,
                'error': '今天已经签到过了'
            }), 400

        # 先计算连续签到天数和奖励（斐波那契数列）
        streak = 1
        rewards_list = [1, 2, 3, 5, 8, 13, 21, 34]  # 斐波那契数列

        for i in range(1, 8):  # 检查前7天
            check_date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            record = conn.execute(
                'SELECT * FROM checkin_records WHERE user_id = ? AND DATE(checkin_date) = ?',
                (user_id, check_date)
            ).fetchone()
            if record:
                streak += 1
            else:
                break

        # 连续签到天数对应的奖励（天数-1作为索引）
        rewards_index = min(streak - 1, len(rewards_list) - 1)
        rewards = rewards_list[rewards_index]

        # 计算下一次签到奖励
        next_streak = streak + 1
        next_rewards_index = min(next_streak - 1, len(rewards_list) - 1)
        next_rewards = rewards_list[next_rewards_index]

        # 生成奖励说明
        reward_tips = []
        for i in range(len(rewards_list)):
            day = i + 1
            reward = rewards_list[i]
            if day == streak:
                reward_tips.append(f"第{day}天: {reward}灵值 ✨")
            else:
                reward_tips.append(f"第{day}天: {reward}灵值")

        # 执行签到
        today_date = datetime.now().strftime('%Y-%m-%d')
        cursor.execute(
            'INSERT INTO checkin_records (user_id, checkin_date, lingzhi_earned) VALUES (?, ?, ?)',
            (user_id, today_date, rewards)
        )

        # 更新用户总灵值
        cursor.execute(
            'UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?',
            (rewards, user_id)
        )

        # 获取用户更新后的总灵值
        user_data = conn.execute('SELECT total_lingzhi FROM users WHERE id = ?', (user_id,)).fetchone()
        total_lingzhi = user_data['total_lingzhi'] if user_data else 0

        conn.commit()
        conn.close()

        # 构建详细消息
        message = f"🎉 签到成功！已连续签到 {streak} 天，获得 {rewards} 灵值"
        if next_streak <= len(rewards_list):
            message += f"\n💡 明日签到可获得 {next_rewards} 灵值，记得继续哦~"

        return jsonify({
            'success': True,
            'message': message,
            'data': {
                'streak': streak,
                'rewards': rewards,  # 本次获得的灵值
                'total_lingzhi': total_lingzhi,  # 总灵值
                'todayLingzhi': rewards,  # 今日获得的灵值（本次）
                'nextRewards': next_rewards,  # 下一次签到奖励
                'rewardSchedule': reward_tips,  # 奖励说明
                'rewardTip': f"连续签到奖励：{', '.join(reward_tips[:min(7, len(reward_tips))])}"
            }
        })

    except Exception as e:
        print(f"签到错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 资产系统 ====================

@complete_bp.route('/assets/tokens', methods=['GET'])
def get_tokens():
    """
    获取通证列表
    响应: { success: true, data: { tokens: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token) if token else None

        user_id = user_payload.get('user_id') if user_payload else None

        conn = get_db_connection()

        # 查询用户的数字资产
        assets = conn.execute('''
            SELECT da.*
            FROM digital_assets da
            WHERE da.user_id = ?
            ORDER BY da.created_at DESC
        ''', (user_id,)).fetchall()

        conn.close()

        token_list = []
        for asset in assets:
            token_list.append({
                'id': asset['id'],
                'name': asset['asset_name'] if 'asset_name' in asset.keys() else '',
                'symbol': asset['asset_type'] if 'asset_type' in asset.keys() else '',
                'description': asset['description'] if 'description' in asset.keys() else '',
                'balance': 1,  # 数字资产数量，暂时固定为1
                'icon': asset['image_url'] if 'image_url' in asset.keys() else '',
                'price': asset['value'] if 'value' in asset.keys() else 0,
                'rarity': asset['rarity'] if 'rarity' in asset.keys() else 'common',
                'is_transferable': asset['is_transferable'] if 'is_transferable' in asset.keys() else True
            })

        return jsonify({
            'success': True,
            'data': {
                'tokens': token_list
            }
        })

    except Exception as e:
        print(f"获取通证列表错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/assets/sbt', methods=['GET'])
def get_sbt_templates():
    """
    获取 SBT 模板列表
    响应: { success: true, data: { templates: [...] } }
    """
    try:
        conn = get_db_connection()

        templates = conn.execute(
            'SELECT * FROM sbt_templates WHERE is_active = 1 ORDER BY created_at'
        ).fetchall()

        conn.close()

        template_list = []
        for tmpl in templates:
            template_list.append({
                'id': tmpl['id'],
                'name': tmpl['name'],
                'description': tmpl['description'] if 'description' in tmpl.keys() else '',
                'image': tmpl['image'] if 'image' in tmpl.keys() else '',
                'requirements': json.loads(tmpl['requirements']) if tmpl.get('requirements') else [],
                'benefits': json.loads(tmpl['benefits']) if tmpl.get('benefits') else []
            })

        return jsonify({
            'success': True,
            'data': {
                'templates': template_list
            }
        })

    except Exception as e:
        print(f"获取 SBT 模板错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/assets/sbt/my-sbt', methods=['GET'])
def get_my_sbt():
    """
    获取我的 SBT
    响应: { success: true, data: { sbts: [...] } }
    """
    try:
        token = request.headers['Authorization'] if 'Authorization' in headers.keys() else ''.replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        sbts = conn.execute('''
            SELECT st.*, usbt.minted_at, usbt.metadata
            FROM sbt_templates st
            JOIN user_sbt usbt ON st.id = usbt.template_id
            WHERE usbt.user_id = ?
            ORDER BY usbt.minted_at DESC
        ''', (user_id,)).fetchall()

        conn.close()

        sbt_list = []
        for sbt in sbts:
            sbt_list.append({
                'id': sbt['id'],
                'name': sbt['name'],
                'description': sbt['description'] if 'description' in sbt.keys() else '',
                'image': sbt['image'] if 'image' in sbt.keys() else '',
                'mintedAt': sbt['minted_at'],
                'metadata': json.loads(sbt['metadata']) if sbt.get('metadata') else {}
            })

        return jsonify({
            'success': True,
            'data': {
                'sbts': sbt_list
            }
        })

    except Exception as e:
        print(f"获取我的 SBT 错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/assets/sbt/<int:template_id>/mint', methods=['POST'])
def mint_sbt(template_id):
    """
    铸造 SBT
    响应: { success: true, data: { sbt: {...} } }
    """
    try:
        token = request.headers['Authorization'] if 'Authorization' in headers.keys() else ''.replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否已铸造
        existing = conn.execute(
            'SELECT * FROM user_sbt WHERE user_id = ? AND template_id = ?',
            (user_id, template_id)
        ).fetchone()

        if existing:
            conn.close()
            return jsonify({
                'success': False,
                'error': '已铸造过此 SBT'
            }), 400

        # 铸造 SBT
        cursor.execute('''
            INSERT INTO user_sbt (user_id, template_id, minted_at, metadata)
            VALUES (?, ?, ?, ?)
        ''', (user_id, template_id, datetime.now().isoformat(), '{}'))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'message': 'SBT 铸造成功'
            }
        })

    except Exception as e:
        print(f"铸造 SBT 错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/assets/stats', methods=['GET'])
def get_assets_stats():
    """
    获取资产统计
    响应: { success: true, data: { stats: {...} } }
    """
    try:
        token = request.headers['Authorization'] if 'Authorization' in headers.keys() else ''.replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 获取总资产
        total_balance = conn.execute(
            'SELECT COALESCE(SUM(balance), 0) as total FROM user_token_balances WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        # 获取 SBT 数量
        sbt_count = conn.execute(
            'SELECT COUNT(*) as count FROM user_sbt WHERE user_id = ?',
            (user_id,)
        ).fetchone

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'stats': {
                    'totalBalance': total_balance['total'] or 0,
                    'sbtCount': sbt_count['count'] or 0
                }
            }
        })

    except Exception as e:
        print(f"获取资产统计错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 项目系统 ====================

@complete_bp.route('/projects', methods=['GET'])
def get_projects():
    """
    获取项目列表
    响应: { success: true, data: [...] }
    """
    try:
        conn = get_db_connection()

        # 检查是否有 project_participants 表
        has_participants = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='project_participants'"
        ).fetchone()

        if has_participants:
            # 如果有参与者表，使用 LEFT JOIN
            projects = conn.execute('''
                SELECT p.*, COUNT(pp.user_id) as participant_count
                FROM projects p
                LEFT JOIN project_participants pp ON p.id = pp.project_id
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT 50
            ''').fetchall()
        else:
            # 如果没有参与者表，直接查询
            projects = conn.execute('''
                SELECT *
                FROM projects
                ORDER BY created_at DESC
                LIMIT 50
            ''').fetchall()

        conn.close()

        project_list = []
        for proj in projects:
            project_list.append({
                'id': proj['id'],
                'name': proj.get('title', ''),
                'description': proj.get('description', ''),
                'category': proj.get('project_type', 'other'),
                'status': proj.get('status', 'active'),
                'budget': float(proj.get('budget', 0) or 0),
                'progress': 0,  # 计算进度
                'priority': 'medium',  # 默认优先级
                'startDate': proj.get('created_at', ''),
                'endDate': proj.get('updated_at', ''),
                'userId': proj.get('creator_id', 0) or 0,
                'userName': '',
                'createdAt': proj.get('created_at', ''),
                'updatedAt': proj.get('updated_at', ''),
                'requiredSkills': proj.get('required_skills', '') or '',
                'requiredAssets': proj.get('required_assets', '') or '',
                'duration': proj.get('duration', 0) or 0,
                'location': proj.get('location', '') or '',
                'deadline': proj.get('deadline', '') or ''
            })

        return jsonify({
            'success': True,
            'data': project_list
        })

    except Exception as e:
        print(f"获取项目列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e),
            'data': []
        }), 500


# ==================== 商家系统 ====================

@complete_bp.route('/merchants', methods=['GET'])
def get_merchants():
    """
    获取商家列表
    响应: { success: true, data: { merchants: [...] } }
    """
    try:
        conn = get_db_connection()

        merchants = conn.execute('''
            SELECT m.*, COUNT(mr.id) as review_count
            FROM merchants m
            LEFT JOIN merchant_reviews mr ON m.id = mr.merchant_id
            WHERE m.status = 'active'
            GROUP BY m.id
            ORDER BY m.created_at DESC
            LIMIT 50
        ''').fetchall()

        conn.close()

        merchant_list = []
        for merchant in merchants:
            merchant_list.append({
                'id': merchant['id'],
                'merchantCode': merchant['merchant_code'],
                'merchantName': merchant['merchant_name'],
                'description': merchant['description'] if 'description' in merchant.keys() else '',
                'logoUrl': merchant['logo_url'] if 'logo_url' in merchant.keys() else '',
                'category': merchant['category'] if 'category' in merchant.keys() else '',
                'contactPerson': merchant['contact_person'] if 'contact_person' in merchant.keys() else '',
                'contactPhone': merchant['contact_phone'] if 'contact_phone' in merchant.keys() else '',
                'contactEmail': merchant['contact_email'] if 'contact_email' in merchant.keys() else '',
                'address': merchant['address'] if 'address' in merchant.keys() else '',
                'status': merchant['status'] if 'status' in merchant.keys() else '',
                'commissionRate': merchant['commission_rate'] if 'commission_rate' in merchant.keys() else 0,
                'totalOrders': merchant['total_orders'] if 'total_orders' in merchant.keys() else 0,
                'totalRevenue': merchant['total_revenue'] if 'total_revenue' in merchant.keys() else 0,
                'rating': merchant['rating'] if 'rating' in merchant.keys() else 0,
                'reviewCount': merchant['review_count']
            })

        return jsonify({
            'success': True,
            'data': {
                'merchants': merchant_list
            }
        })

    except Exception as e:
        print(f"获取商家列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 分红池系统 ====================

@complete_bp.route('/dividend-pool/summary', methods=['GET'])
def get_dividend_summary():
    """
    获取分红池汇总
    响应: { success: true, data: { summary: {...} } }
    """
    try:
        conn = get_db_connection()

        # 获取分红池信息
        pool = conn.execute(
            'SELECT * FROM dividend_pool ORDER BY id DESC LIMIT 1'
        ).fetchone()

        if not pool:
            # 创建默认分红池
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO dividend_pool (total_amount, distributed_amount, created_at, updated_at)
                VALUES (0, 0, ?, ?)
            ''', (datetime.now().isoformat(), datetime.now().isoformat()))
            pool = conn.execute(
                'SELECT * FROM dividend_pool WHERE id = ?',
                (cursor.lastrowid,)
            ).fetchone()
            conn.commit()

        conn.close()

        summary = {
            'totalAmount': pool['total_amount'] or 0,
            'distributedAmount': pool['distributed_amount'] or 0,
            'remainingAmount': (pool['total_amount'] or 0) - (pool['distributed_amount'] or 0),
            'lastDistributed': pool['last_distributed_at'] if 'last_distributed_at' in pool.keys() else None,
            'totalUsers': 1000,  # 模拟数据
            'activeUsers': 500  # 模拟数据
        }

        return jsonify({
            'success': True,
            'data': {
                'summary': summary
            }
        })

    except Exception as e:
        print(f"获取分红池汇总错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/dividend-pool/eligibility', methods=['GET'])
def get_dividend_eligibility():
    """
    获取分红资格
    响应: { success: true, data: { eligible, amount, ... } }
    """
    try:
        token = request.headers['Authorization'] if 'Authorization' in headers.keys() else ''.replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = request.args.get('user_id') or user_payload.get('user_id')

        conn = get_db_connection()

        # 检查分红资格
        eligibility = conn.execute(
            'SELECT * FROM dividend_pool_eligibility WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        conn.close()

        if eligibility:
            return jsonify({
                'success': True,
                'data': {
                    'eligible': True,
                    'eligibilityAmount': eligibility['eligibility_amount'] or 0,
                    'accumulatedContribution': eligibility['accumulated_contribution'] or 0,
                    'lastUpdated': eligibility['updated_at']
                }
            })
        else:
            return jsonify({
                'success': True,
                'data': {
                    'eligible': False,
                    'eligibilityAmount': 0,
                    'accumulatedContribution': 0,
                    'message': '暂无分红资格'
                }
            })

    except Exception as e:
        print(f"获取分红资格错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 赏金任务系统 ====================

@complete_bp.route('/bounty/tasks', methods=['GET'])
def get_bounty_tasks():
    """
    获取赏金任务列表
    响应: { success: true, data: { tasks: [...] } }
    """
    try:
        conn = get_db_connection()

        tasks = conn.execute('''
            SELECT * FROM bounty_hunter_earnings
            WHERE status = 'open'
            ORDER BY created_at DESC
            LIMIT 20
        ''').fetchall()

        conn.close()

        task_list = []
        for task in tasks:
            task_list.append({
                'id': task['id'],
                'title': task['title'] if 'title' in task.keys() else '赏金任务',
                'description': task['description'] if 'description' in task.keys() else '',
                'reward': task['reward'] if 'reward' in task.keys() else 0,
                'status': task['status'] if 'status' in task.keys() else 'open',
                'createdAt': task['created_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'tasks': task_list
            }
        })

    except Exception as e:
        print(f"获取赏金任务错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/bounty/<int:bounty_id>/claim', methods=['POST'])
def claim_bounty(bounty_id):
    """
    领取赏金任务
    响应: { success: true, data: { ... } }
    """
    try:
        token = request.headers['Authorization'] if 'Authorization' in headers.keys() else ''.replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()
        cursor = conn.cursor()

        # 更新任务状态
        cursor.execute(
            'UPDATE bounty_hunter_earnings SET status = "claimed", claimed_by = ?, claimed_at = ? WHERE id = ?',
            (user_id, datetime.now().isoformat(), bounty_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'message': '任务领取成功'
            }
        })

    except Exception as e:
        print(f"领取赏金任务错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 其他辅助 API ====================

@complete_bp.route('/sacred-sites', methods=['GET'])
def get_sacred_sites():
    """
    获取圣地列表
    响应: { success: true, data: { sites: [...] } }
    """
    try:
        conn = get_db_connection()

        sites = conn.execute(
            'SELECT * FROM sacred_sites WHERE is_active = 1 ORDER BY created_at'
        ).fetchall()

        conn.close()

        site_list = []
        for site in sites:
            site_list.append({
                'id': site['id'],
                'name': site['name'],
                'description': site['description'] if 'description' in site.keys() else '',
                'location': site['location'] if 'location' in site.keys() else '',
                'image': site['image'] if 'image' in site.keys() else '',
                'coordinates': json.loads(site['coordinates']) if site.get('coordinates') else {}
            })

        return jsonify({
            'success': True,
            'data': {
                'sites': site_list
            }
        })

    except Exception as e:
        print(f"获取圣地列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/aesthetic-tasks', methods=['GET'])
def get_aesthetic_tasks():
    """
    获取美学任务列表
    响应: { success: true, data: { tasks: [...] } }
    """
    try:
        status = request.args['status'] if 'status' in args.keys() else 'open'
        conn = get_db_connection()

        tasks = conn.execute(
            'SELECT * FROM aesthetic_tasks WHERE status = ? ORDER BY created_at DESC',
            (status,)
        ).fetchall()

        conn.close()

        task_list = []
        for task in tasks:
            task_list.append({
                'id': task['id'],
                'title': task['title'],
                'description': task['description'] if 'description' in task.keys() else '',
                'location': task['location'] if 'location' in task.keys() else '',
                'reward': task['reward'] if 'reward' in task.keys() else 0,
                'status': task['status'],
                'createdAt': task['created_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'tasks': task_list
            }
        })

    except Exception as e:
        print(f"获取美学任务错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/aesthetic-tasks/stats', methods=['GET'])
def get_aesthetic_stats():
    """
    获取美学任务统计
    响应: { success: true, data: { stats: {...} } }
    """
    try:
        conn = get_db_connection()

        stats = {
            'totalTasks': 0,
            'completedTasks': 0,
            'openTasks': 0,
            'inProgressTasks': 0
        }

        total = conn.execute(
            'SELECT COUNT(*) as count FROM aesthetic_tasks'
        ).fetchone()
        stats['totalTasks'] = total['count']

        completed = conn.execute(
            'SELECT COUNT(*) as count FROM aesthetic_tasks WHERE status = "completed"'
        ).fetchone()
        stats['completedTasks'] = completed['count']

        open_tasks = conn.execute(
            'SELECT COUNT(*) as count FROM aesthetic_tasks WHERE status = "open"'
        ).fetchone()
        stats['openTasks'] = open_tasks['count']

        in_progress = conn.execute(
            'SELECT COUNT(*) as count FROM aesthetic_tasks WHERE status = "in_progress"'
        ).fetchone()
        stats['inProgressTasks'] = in_progress['count']

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'stats': stats
            }
        })

    except Exception as e:
        print(f"获取美学任务统计错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/company/news', methods=['GET'])
def get_company_news():
    """
    获取公司新闻
    响应: { success: true, data: { news: [...] } }
    """
    try:
        conn = get_db_connection()

        news = conn.execute(
            'SELECT * FROM company_news ORDER BY created_at DESC LIMIT 10'
        ).fetchall()

        conn.close()

        news_list = []
        for item in news:
            news_list.append({
                'id': item['id'],
                'title': item['title'],
                'content': item['content'] if 'content' in item.keys() else '',
                'coverImage': item['cover_image'] if 'cover_image' in item.keys() else '',
                'createdAt': item['created_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'news': news_list
            }
        })

    except Exception as e:
        print(f"获取公司新闻错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/docs', methods=['GET'])
def get_docs():
    """
    获取文档列表
    响应: { success: true, data: { docs: [...] } }
    """
    try:
        conn = get_db_connection()

        docs = conn.execute(
            'SELECT * FROM documents WHERE is_published = 1 ORDER BY created_at DESC'
        ).fetchall()

        conn.close()

        doc_list = []
        for doc in docs:
            doc_list.append({
                'id': doc['id'],
                'title': doc['title'],
                'slug': doc['slug'] if 'slug' in doc.keys() else '',
                'content': doc['content'] if 'content' in doc.keys() else '',
                'category': doc['category'] if 'category' in doc.keys() else '',
                'createdAt': doc['created_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'docs': doc_list
            }
        })

    except Exception as e:
        print(f"获取文档列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/recharge/tiers', methods=['GET'])
def get_recharge_tiers():
    """
    获取充值档位
    响应: { success: true, data: { tiers: [...] } }
    """
    try:
        conn = get_db_connection()

        tiers = conn.execute(
            'SELECT * FROM recharge_tiers WHERE is_active = 1 ORDER BY amount ASC'
        ).fetchall()

        conn.close()

        tier_list = []
        for tier in tiers:
            tier_list.append({
                'id': tier['id'],
                'name': tier['name'],
                'amount': tier['amount'],
                'bonus': tier['bonus'] if 'bonus' in tier.keys() else 0,
                'bonusPercentage': tier['bonus_percentage'] if 'bonus_percentage' in tier.keys() else 0,
                'description': tier['description'] if 'description' in tier.keys() else ''
            })

        return jsonify({
            'success': True,
            'data': {
                'tiers': tier_list
            }
        })

    except Exception as e:
        print(f"获取充值档位错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@complete_bp.route('/public/users/recent', methods=['GET'])
def get_recent_users():
    """
    获取最近活跃用户
    响应: { success: true, data: { users: [...] } }
    """
    try:
        limit = int(request.args.get('limit', 20))
        conn = get_db_connection()

        users = conn.execute('''
            SELECT u.id, u.username, u.avatar_url, u.created_at
            FROM users u
            ORDER BY u.created_at DESC
            LIMIT ?
        ''', (limit,)).fetchall()

        conn.close()

        user_list = []
        for user in users:
            user_list.append({
                'id': user['id'],
                'username': user['username'],
                'avatar': user['avatar_url'] if user['avatar_url'] else '',
                'createdAt': user['created_at']
            })

        return jsonify({
            'success': True,
            'data': user_list
        })

    except Exception as e:
        print(f"获取最近用户错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


print("✅ 综合功能 API 蓝图已加载")
