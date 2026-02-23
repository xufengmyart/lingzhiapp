"""
签到系统路由蓝图
包含每日签到、签到统计、签到奖励等功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime, date, timedelta
import jwt

# 导入配置
import sys
sys.path.append('..')
from config import config

checkin_bp = Blueprint('checkin', __name__)

# 导入配置
DATABASE = config.DATABASE_PATH
JWT_SECRET = config.JWT_SECRET_KEY

# 辅助函数
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def verify_token(token):
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except:
        return None

# ============ 每日签到 ============

@checkin_bp.route('/checkin', methods=['POST'])
def checkin():
    """每日签到"""
    try:
        # 从 JWT token 中获取用户 ID
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            # 验证 token 并获取 user_id
            payload = verify_token(token)
            if payload:
                user_id = payload.get('user_id')
            else:
                # token 无效，尝试从请求体获取（兼容旧版本）
                data = request.get_json(force=True, silent=True)
                if not data:
                    return jsonify({
                        'success': False,
                        'message': '请求数据格式错误'
                    }), 400
                user_id = data.get('user_id')
        else:
            # 没有 token，从请求体获取
            data = request.get_json(force=True, silent=True)
            if not data:
                return jsonify({
                    'success': False,
                    'message': '请求数据格式错误'
                }), 400
            user_id = data.get('user_id')

        if not user_id:
            return jsonify({
                'success': False,
                'message': '用户ID不能为空'
            }), 400

        today = date.today().isoformat()

        conn = get_db()
        cursor = conn.cursor()

        # 检查今天是否已经签到
        cursor.execute(
            "SELECT id FROM checkin_records WHERE user_id = ? AND checkin_date = ?",
            (user_id, today)
        )
        if cursor.fetchone():
            conn.close()
            # 返回200而不是400，因为这是一个成功的查询结果
            return jsonify({
                'success': True,  # 改为True
                'message': '🎉 太棒了！您今天已经签到过了，记得明天再来哦~',
                'data': {
                    'already_checked': True,
                    'tip': '保持每日签到，积累更多灵值，探索灵值生态园的精彩内容！'
                }
            }), 200  # 改为200

        # 查询连续签到天数
        cursor.execute(
            """
            SELECT checkin_date
            FROM checkin_records
            WHERE user_id = ?
            ORDER BY checkin_date DESC
            LIMIT 1
            """,
            (user_id,)
        )
        last_checkin = cursor.fetchone()

        consecutive_days = 1
        if last_checkin:
            last_date = datetime.fromisoformat(last_checkin['checkin_date']).date()
            yesterday = date.today() - timedelta(days=1)
            if last_date == yesterday:
                # 连续签到，计算连续天数
                cursor.execute(
                    """
                    SELECT COUNT(*) as days
                    FROM checkin_records
                    WHERE user_id = ? AND checkin_date >= date('now', '-6 days')
                    """,
                    (user_id,)
                )
                consecutive_days = cursor.fetchone()['days'] + 1

        # 计算奖励灵值（连续签到奖励递增）
        base_reward = 10
        bonus_reward = min(consecutive_days - 1, 6) * 5  # 最多额外奖励30灵值
        total_reward = base_reward + bonus_reward

        # 创建签到记录
        cursor.execute(
            """
            INSERT INTO checkin_records (user_id, checkin_date, lingzhi_earned)
            VALUES (?, ?, ?)
            """,
            (user_id, today, total_reward)
        )

        # 增加用户灵值
        cursor.execute(
            "UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?",
            (total_reward, user_id)
        )

        # 查询更新后的用户信息
        cursor.execute(
            "SELECT total_lingzhi FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        new_total_lingzhi = user['total_lingzhi'] if user else 0

        conn.commit()
        conn.close()

        # 计算明日奖励
        tomorrow_consecutive = consecutive_days + 1
        tomorrow_base = 10
        tomorrow_bonus = min(tomorrow_consecutive - 1, 6) * 5  # 最多额外奖励30灵值
        tomorrow_reward = tomorrow_base + tomorrow_bonus

        # 构造有情绪价值的成功消息，包含明日奖励信息
        if consecutive_days == 1:
            success_message = f'✨ 签到成功！获得{total_reward}灵值，开启美好的一天~ 🔥 连续签到第{tomorrow_consecutive}天，明天可获得{tomorrow_reward}灵值！'
        elif consecutive_days < 7:
            success_message = f'🔥 连续签到{consecutive_days}天！获得{total_reward}灵值，继续保持！🎁 连续签到第{tomorrow_consecutive}天，明天可获得{tomorrow_reward}灵值！'
        else:
            success_message = f'🏆 哇！连续签到{consecutive_days}天！获得{total_reward}灵值，您真是太棒了！✨ 连续签到第{tomorrow_consecutive}天，明天可获得{tomorrow_reward}灵值！'

        # 计算下一个里程碑
        next_milestone = ((new_total_lingzhi // 100) + 1) * 100
        progress = (new_total_lingzhi % 100)

        return jsonify({
            'success': True,
            'message': success_message,
            'data': {
                'rewards': total_reward,
                'total_lingzhi': new_total_lingzhi,  # 签到后的总灵值
                'todayLingzhi': total_reward,  # 今日获得的灵值
                'streak': consecutive_days,  # 连续签到天数（前端期望的字段名）
                'tomorrow_reward': min(10 + (consecutive_days) * 5, 40),
                'next_milestone': next_milestone,
                'progress': progress,
                'motivational_tip': '每日签到，积少成多。在灵值生态园，每一份坚持都有回报！'
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'签到失败: {str(e)}'
        }), 500

@checkin_bp.route('/checkin/status', methods=['GET'])
def checkin_status():
    """获取签到状态"""
    try:
        # 从 JWT token 中获取用户 ID
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if token:
            # 验证 token 并获取 user_id
            payload = verify_token(token)
            if payload:
                user_id = payload.get('user_id')
            else:
                # token 无效，尝试从查询参数获取（兼容旧版本）
                user_id = int(request.args.get('user_id', 1))
        else:
            # 没有 token，从查询参数获取
            user_id = int(request.args.get('user_id', 1))

        today = date.today().isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()

        conn = get_db()
        cursor = conn.cursor()

        # 查询用户总灵值
        cursor.execute(
            "SELECT total_lingzhi FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()
        total_lingzhi = user['total_lingzhi'] if user else 0

        # 检查今天是否签到
        cursor.execute(
            "SELECT lingzhi_earned FROM checkin_records WHERE user_id = ? AND checkin_date = ?",
            (user_id, today)
        )
        today_record = cursor.fetchone()
        checked_today = today_record is not None
        today_lingzhi = today_record['lingzhi_earned'] if today_record else 0

        # 检查昨天是否签到
        cursor.execute(
            "SELECT lingzhi_earned FROM checkin_records WHERE user_id = ? AND checkin_date = ?",
            (user_id, yesterday)
        )
        yesterday_record = cursor.fetchone()
        checked_yesterday = yesterday_record is not None
        yesterday_lingzhi = yesterday_record['lingzhi_earned'] if yesterday_record else 0

        # 查询连续签到天数
        cursor.execute(
            """
            SELECT checkin_date, lingzhi_earned
            FROM checkin_records
            WHERE user_id = ?
            ORDER BY checkin_date DESC
            LIMIT 7
            """,
            (user_id,)
        )
        checkins = cursor.fetchall()

        consecutive_days = 0
        recent_rewards = []
        
        if checkins:
            # 计算连续签到天数
            current_date = date.today()
            for record in checkins:
                record_date = datetime.fromisoformat(record['checkin_date']).date()
                if record_date == current_date or record_date == (current_date - timedelta(days=1)):
                    consecutive_days += 1
                    recent_rewards.append({
                        'date': record['checkin_date'],
                        'lingzhi': record['lingzhi_earned']
                    })
                    if record_date == current_date:
                        current_date -= timedelta(days=1)
                else:
                    break

        # 查询本月签到天数
        cursor.execute(
            """
            SELECT COUNT(*) as count
            FROM checkin_records
            WHERE user_id = ? AND strftime('%Y-%m', checkin_date) = strftime('%Y-%m', 'now')
            """,
            (user_id,)
        )
        month_checkin_count = cursor.fetchone()['count']

        # 查询累计签到天数
        cursor.execute(
            "SELECT COUNT(*) as count FROM checkin_records WHERE user_id = ?",
            (user_id,)
        )
        total_checkin_count = cursor.fetchone()['count']

        # 计算下次签到奖励
        next_reward = min(10 + consecutive_days * 5, 40)
        
        # 计算下一个里程碑
        next_milestone = ((total_lingzhi // 100) + 1) * 100
        progress = (total_lingzhi % 100)

        # 构造明日奖励信息（情绪价值）
        tomorrow_consecutive_days = consecutive_days + 1
        tomorrow_bonus = min(tomorrow_consecutive_days - 1, 6) * 5  # 最多额外奖励30灵值
        tomorrow_total_reward = 10 + tomorrow_bonus
        
        # 生成明日奖励提示
        if checked_today:
            if tomorrow_consecutive_days == 1:
                tomorrow_tip = f"🌟 明天是新的开始，签到可获得 {tomorrow_total_reward} 灵值"
            elif tomorrow_consecutive_days <= 3:
                tomorrow_tip = f"🔥 连续签到第 {tomorrow_consecutive_days} 天，明天可获得 {tomorrow_total_reward} 灵值！"
            elif tomorrow_consecutive_days <= 7:
                tomorrow_tip = f"💪 连续签到第 {tomorrow_consecutive_days} 天，明天可获得 {tomorrow_total_reward} 灵值，坚持就是胜利！"
            else:
                tomorrow_tip = f"🎉 您已经连续签到 {tomorrow_consecutive_days} 天，明天可获得 {tomorrow_total_reward} 灵值！"
        else:
            tomorrow_tip = f"🎁 今日签到可获得 {next_reward} 灵值，快来签到吧！"

        conn.close()

        # 构造奖励数据（前端期望的格式）
        rewards = []
        if checked_today:
            rewards.append({
                'id': 1,
                'name': '今日签到奖励',
                'amount': today_lingzhi,
                'received': True
            })
        if consecutive_days >= 7:
            rewards.append({
                'id': 2,
                'name': '连续7天奖励',
                'amount': 35,
                'received': True
            })

        return jsonify({
            'success': True,
            'data': {
                'todayLingzhi': today_lingzhi,  # 今日获得的灵值
                'checkedIn': checked_today,      # 今天是否签到
                'totalLingzhi': total_lingzhi,    # 总灵值
                'streak': consecutive_days,  # 连续签到天数（前端期望的字段名）
                'monthCheckinCount': month_checkin_count,  # 本月签到天数
                'totalCheckinCount': total_checkin_count,  # 累计签到天数
                'nextReward': next_reward,        # 下次签到奖励
                'nextMilestone': next_milestone,  # 下一个里程碑
                'progress': progress,             # 当前进度
                'rewards': rewards,               # 奖励列表
                'yesterday': {                    # 昨天签到状态
                    'checkedIn': checked_yesterday,
                    'lingzhi': yesterday_lingzhi
                },
                # 新增：明日奖励信息（情绪价值）
                'tomorrow': {
                    'reward': tomorrow_total_reward,  # 明日奖励总数
                    'baseReward': 10,                 # 基础奖励
                    'bonus': tomorrow_bonus,          # 连续签到额外奖励
                    'consecutiveDays': tomorrow_consecutive_days,  # 明日连续天数
                    'tip': tomorrow_tip,              # 友好提示
                    'description': f'明日签到可获得 {tomorrow_total_reward} 灵值（基础10 + 连续奖励{tomorrow_bonus}）'
                },
                # 新增：签到提示（情绪价值）
                'checkinTip': tomorrow_tip if not checked_today else f"✨ 今日已签到，获得 {today_lingzhi} 灵值！{tomorrow_tip}",
                # 新增：连续签到里程碑提示
                'milestoneTip': f'连续签到 {consecutive_days} 天，再签到 {7 - consecutive_days % 7 if consecutive_days % 7 != 0 else 0} 天可获得连续7天奖励！' if consecutive_days < 7 else f'🏆 恭喜！您已连续签到 {consecutive_days} 天！'
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'获取签到状态失败: {str(e)}'
        }), 500
