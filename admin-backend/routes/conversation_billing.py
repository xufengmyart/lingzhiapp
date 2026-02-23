#!/usr/bin/env python3
"""
对话计费路由

功能：
1. 对话结束时计算时长并扣费
2. 处理用户反馈并给予奖励
3. 记录对话消耗和获得情况

版本：v1.0.0
创建日期：2024-12-14
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import sqlite3
import os

# 创建蓝图
conversation_billing_bp = Blueprint('conversation_billing', __name__)

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'lingzhi_ecosystem.db')


def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@conversation_billing_bp.route('/conversation/<conversation_id>/end', methods=['POST'])
def end_conversation(conversation_id):
    """
    结束对话，计算消耗和奖励

    Request Body:
        - duration: 对话时长（秒）
        - feedback_score: 反馈评分（1-5，可选）

    Returns:
        - success: 是否成功
        - duration: 对话时长（秒）
        - duration_minutes: 对话时长（分钟）
        - cost: 消耗灵值
        - feedback_lingzhi_reward: 反馈获得的灵值奖励
        - total_lingzhi_change: 总灵值变化（负数表示消耗，正数表示获得）
        - current_balance: 当前灵值余额
        - message: 提示消息
    """
    try:
        data = request.json
        duration = data.get('duration', 0)  # 对话时长（秒）
        feedback_score = data.get('feedback_score')  # 反馈评分

        # 验证对话ID
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查对话是否存在
        cursor.execute(
            "SELECT id, user_id, status FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        conversation = cursor.fetchone()

        if not conversation:
            conn.close()
            return jsonify({
                'success': False,
                'message': '对话不存在'
            }), 404

        # 检查对话是否已结束
        if conversation['status'] == 'completed':
            conn.close()
            return jsonify({
                'success': False,
                'message': '对话已结束'
            }), 400

        user_id = conversation['user_id']

        # 计算消耗（5分钟/灵值，不足5分钟按5分钟计算）
        duration_minutes = duration / 60
        cost_units = max(1, int(duration_minutes / 5))  # 至少1个单位
        cost = cost_units  # 1个单位 = 1灵值

        # 计算反馈奖励
        feedback_lingzhi_reward = 0
        if feedback_score:
            if feedback_score >= 4:
                feedback_lingzhi_reward = 2  # 满意/非常满意奖励2灵值
            elif feedback_score >= 3:
                feedback_lingzhi_reward = 1  # 一般奖励1灵值

        # 计算总灵值变化
        total_lingzhi_change = feedback_lingzhi_reward - cost

        # 更新对话信息
        cursor.execute("""
            UPDATE conversations 
            SET duration = ?,
                cost = ?,
                status = 'completed',
                feedback_given = ?,
                feedback_score = ?,
                feedback_lingzhi_reward = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            duration,
            cost,
            1 if feedback_score else 0,
            feedback_score,
            feedback_lingzhi_reward,
            datetime.now(),
            conversation['id']
        ))

        # 更新用户灵值余额
        cursor.execute(
            "UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?",
            (total_lingzhi_change, user_id)
        )

        # 获取当前灵值余额
        cursor.execute("SELECT total_lingzhi FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        current_balance = user['total_lingzhi']

        # 提交事务
        conn.commit()
        conn.close()

        # 生成提示消息
        duration_str = f"{int(duration_minutes)}分钟{int(duration_minutes * 60) % 60}秒" if duration_minutes >= 1 else "不足1分钟"

        if feedback_score:
            if feedback_lingzhi_reward > 0:
                message = f"本次对话时长 {duration_str}，消耗 {cost} 灵值。感谢您的反馈！您获得 {feedback_lingzhi_reward} 灵值奖励。当前余额：{current_balance} 灵值。"
            else:
                message = f"本次对话时长 {duration_str}，消耗 {cost} 灵值。感谢您的反馈！当前余额：{current_balance} 灵值。"
        else:
            message = f"本次对话时长 {duration_str}，消耗 {cost} 灵值。当前余额：{current_balance} 灵值。"

        return jsonify({
            'success': True,
            'duration': duration,
            'duration_minutes': duration_minutes,
            'cost': cost,
            'feedback_lingzhi_reward': feedback_lingzhi_reward,
            'total_lingzhi_change': total_lingzhi_change,
            'current_balance': current_balance,
            'message': message
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}'
        }), 500


@conversation_billing_bp.route('/conversation/<conversation_id>/feedback', methods=['POST'])
def submit_feedback(conversation_id):
    """
    提交反馈（可在对话结束后单独调用）

    Request Body:
        - feedback_score: 反馈评分（1-5）

    Returns:
        - success: 是否成功
        - feedback_lingzhi_reward: 获得的灵值奖励
        - current_balance: 当前灵值余额
        - message: 提示消息
    """
    try:
        data = request.json
        feedback_score = data.get('feedback_score')

        if not feedback_score:
            return jsonify({
                'success': False,
                'message': '请提供反馈评分'
            }), 400

        # 验证反馈评分
        if not 1 <= feedback_score <= 5:
            return jsonify({
                'success': False,
                'message': '反馈评分必须在1-5之间'
            }), 400

        # 连接数据库
        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查对话是否存在
        cursor.execute(
            "SELECT id, user_id, feedback_given FROM conversations WHERE conversation_id = ?",
            (conversation_id,)
        )
        conversation = cursor.fetchone()

        if not conversation:
            conn.close()
            return jsonify({
                'success': False,
                'message': '对话不存在'
            }), 404

        # 检查是否已提交过反馈
        if conversation['feedback_given']:
            conn.close()
            return jsonify({
                'success': False,
                'message': '已提交过反馈'
            }), 400

        user_id = conversation['user_id']

        # 计算反馈奖励
        feedback_lingzhi_reward = 0
        if feedback_score >= 4:
            feedback_lingzhi_reward = 2  # 满意/非常满意奖励2灵值
        elif feedback_score >= 3:
            feedback_lingzhi_reward = 1  # 一般奖励1灵值

        # 更新对话信息
        cursor.execute("""
            UPDATE conversations 
            SET feedback_given = 1,
                feedback_score = ?,
                feedback_lingzhi_reward = ?,
                updated_at = ?
            WHERE id = ?
        """, (
            feedback_score,
            feedback_lingzhi_reward,
            datetime.now(),
            conversation['id']
        ))

        # 更新用户灵值余额
        cursor.execute(
            "UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?",
            (feedback_lingzhi_reward, user_id)
        )

        # 获取当前灵值余额
        cursor.execute("SELECT total_lingzhi FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        current_balance = user['total_lingzhi']

        # 提交事务
        conn.commit()
        conn.close()

        # 生成提示消息
        if feedback_lingzhi_reward > 0:
            message = f"感谢您的反馈！您获得 {feedback_lingzhi_reward} 灵值奖励。当前余额：{current_balance} 灵值。"
        else:
            message = f"感谢您的反馈！我们会继续改进服务。当前余额：{current_balance} 灵值。"

        return jsonify({
            'success': True,
            'feedback_lingzhi_reward': feedback_lingzhi_reward,
            'current_balance': current_balance,
            'message': message
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}'
        }), 500


@conversation_billing_bp.route('/conversation/<conversation_id>/billing-info', methods=['GET'])
def get_billing_info(conversation_id):
    """
    获取对话计费信息

    Returns:
        - success: 是否成功
        - conversation_id: 对话ID
        - duration: 对话时长（秒）
        - duration_minutes: 对话时长（分钟）
        - cost: 消耗灵值
        - status: 对话状态
        - feedback_given: 是否已提交反馈
        - feedback_score: 反馈评分
        - feedback_lingzhi_reward: 反馈获得的灵值奖励
        - total_lingzhi_change: 总灵值变化
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                conversation_id,
                duration,
                cost,
                status,
                feedback_given,
                feedback_score,
                feedback_lingzhi_reward,
                created_at,
                updated_at
            FROM conversations 
            WHERE conversation_id = ?
        """, (conversation_id,))

        conversation = cursor.fetchone()
        conn.close()

        if not conversation:
            return jsonify({
                'success': False,
                'message': '对话不存在'
            }), 404

        # 计算总灵值变化
        total_lingzhi_change = (conversation['feedback_lingzhi_reward'] or 0) - (conversation['cost'] or 0)

        # 计算分钟数
        duration_minutes = (conversation['duration'] or 0) / 60

        return jsonify({
            'success': True,
            'conversation_id': conversation['conversation_id'],
            'duration': conversation['duration'] or 0,
            'duration_minutes': duration_minutes,
            'cost': conversation['cost'] or 0,
            'status': conversation['status'],
            'feedback_given': conversation['feedback_given'] or 0,
            'feedback_score': conversation['feedback_score'],
            'feedback_lingzhi_reward': conversation['feedback_lingzhi_reward'] or 0,
            'total_lingzhi_change': total_lingzhi_change,
            'created_at': conversation['created_at'],
            'updated_at': conversation['updated_at']
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'处理失败: {str(e)}'
        }), 500
