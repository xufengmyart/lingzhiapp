#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
贡献值系统路由
支持贡献值规则、交易记录、统计等
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from database import get_db
from datetime import datetime, timedelta
import json
import logging

# 创建蓝图
contribution_bp = Blueprint('contribution', __name__)

# 日志配置
logger = logging.getLogger(__name__)


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未授权'}), 401
        # TODO: 实现token验证逻辑
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未授权'}), 401
        # TODO: 实现管理员权限验证逻辑
        return f(*args, **kwargs)
    return decorated_function


# ==================== 贡献值规则API ====================

@contribution_bp.route('/admin/contribution/rules', methods=['GET'])
@login_required
def get_rules():
    """
    获取贡献值规则列表
    """
    try:
        db = get_db()

        # 获取查询参数
        rule_type = request.args.get('rule_type', '')  # earn | consume | ''
        target_role = request.args.get('target_role', '')
        status = request.args.get('status', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        # 构建查询条件
        where_clauses = []
        params = []

        if rule_type:
            where_clauses.append('rule_type = ?')
            params.append(rule_type)

        if target_role:
            where_clauses.append('target_role = ?')
            params.append(target_role)

        if status:
            where_clauses.append('status = ?')
            params.append(status)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        # 查询总数
        count_query = f"SELECT COUNT(*) FROM contribution_rules WHERE {where_sql}"
        total = db.execute(count_query, params).fetchone()[0]

        # 查询数据
        offset = (page - 1) * page_size
        query = f"""
            SELECT * FROM contribution_rules
            WHERE {where_sql}
            ORDER BY priority DESC, id ASC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        rules = db.execute(query, params).fetchall()

        return jsonify({
            'success': True,
            'rules': [dict(rule) for rule in rules],
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        logger.error(f"获取贡献值规则失败: {str(e)}")
        return jsonify({'error': f'获取贡献值规则失败: {str(e)}'}), 500


@contribution_bp.route('/admin/contribution/rules', methods=['POST'])
@admin_required
def create_rule():
    """
    创建贡献值规则
    """
    try:
        db = get_db()
        data = request.get_json()

        # 验证必填字段
        required_fields = ['rule_type', 'rule_name', 'rule_code', 'contribution_value']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 检查规则代码是否已存在
        existing = db.execute(
            'SELECT id FROM contribution_rules WHERE rule_code = ?',
            (data['rule_code'],)
        ).fetchone()

        if existing:
            return jsonify({'error': '规则代码已存在'}), 400

        # 插入规则
        db.execute(
            """INSERT INTO contribution_rules
               (rule_type, rule_name, rule_code, description, target_role,
                contribution_value, lingzhi_value, max_daily_times, max_total_times,
                conditions, rewards, status, priority, start_time, end_time, created_by)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['rule_type'],
                data['rule_name'],
                data['rule_code'],
                data.get('description', ''),
                data.get('target_role', 'all'),
                data['contribution_value'],
                data.get('lingzhi_value', 0),
                data.get('max_daily_times'),
                data.get('max_total_times'),
                json.dumps(data.get('conditions', {})),
                json.dumps(data.get('rewards', {})),
                data.get('status', 'active'),
                data.get('priority', 0),
                data.get('start_time'),
                data.get('end_time'),
                data.get('created_by')
            )
        )
        db.commit()

        logger.info(f"创建贡献值规则: {data['rule_code']}")

        return jsonify({
            'success': True,
            'message': '贡献值规则创建成功'
        }), 201

    except Exception as e:
        logger.error(f"创建贡献值规则失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'创建贡献值规则失败: {str(e)}'}), 500


@contribution_bp.route('/admin/contribution/rules/<int:rule_id>', methods=['PUT'])
@admin_required
def update_rule(rule_id):
    """
    更新贡献值规则
    """
    try:
        db = get_db()
        data = request.get_json()

        # 检查规则是否存在
        rule = db.execute('SELECT id FROM contribution_rules WHERE id = ?', (rule_id,)).fetchone()
        if not rule:
            return jsonify({'error': '规则不存在'}), 404

        # 如果更新rule_code，检查是否冲突
        if 'rule_code' in data:
            existing = db.execute(
                'SELECT id FROM contribution_rules WHERE rule_code = ? AND id != ?',
                (data['rule_code'], rule_id)
            ).fetchone()
            if existing:
                return jsonify({'error': '规则代码已存在'}), 400

        # 构建更新SQL
        update_fields = []
        update_values = []

        editable_fields = [
            'rule_name', 'rule_code', 'description', 'target_role',
            'contribution_value', 'lingzhi_value', 'max_daily_times',
            'max_total_times', 'conditions', 'rewards', 'status',
            'priority', 'start_time', 'end_time'
        ]

        for field in editable_fields:
            if field in data:
                update_fields.append(f"{field} = ?")
                if field in ['conditions', 'rewards']:
                    update_values.append(json.dumps(data[field]))
                else:
                    update_values.append(data[field])

        if not update_fields:
            return jsonify({'error': '没有要更新的字段'}), 400

        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(rule_id)

        sql = f"UPDATE contribution_rules SET {', '.join(update_fields)} WHERE id = ?"
        db.execute(sql, update_values)
        db.commit()

        logger.info(f"更新贡献值规则: {rule_id}")

        return jsonify({
            'success': True,
            'message': '贡献值规则更新成功'
        }), 200

    except Exception as e:
        logger.error(f"更新贡献值规则失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'更新贡献值规则失败: {str(e)}'}), 500


@contribution_bp.route('/admin/contribution/rules/<int:rule_id>', methods=['DELETE'])
@admin_required
def delete_rule(rule_id):
    """
    删除贡献值规则
    """
    try:
        db = get_db()

        # 检查规则是否存在
        rule = db.execute('SELECT id FROM contribution_rules WHERE id = ?', (rule_id,)).fetchone()
        if not rule:
            return jsonify({'error': '规则不存在'}), 404

        # 删除规则
        db.execute('DELETE FROM contribution_rules WHERE id = ?', (rule_id,))
        db.commit()

        logger.info(f"删除贡献值规则: {rule_id}")

        return jsonify({
            'success': True,
            'message': '贡献值规则删除成功'
        }), 200

    except Exception as e:
        logger.error(f"删除贡献值规则失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'删除贡献值规则失败: {str(e)}'}), 500


# ==================== 贡献值交易API ====================

@contribution_bp.route('/admin/contribution/transactions', methods=['GET'])
@login_required
def get_transactions():
    """
    获取贡献值交易记录列表
    """
    try:
        db = get_db()

        # 获取查询参数
        user_id = request.args.get('user_id', '')
        transaction_type = request.args.get('transaction_type', '')
        rule_code = request.args.get('rule_code', '')
        start_date = request.args.get('start_date', '')
        end_date = request.args.get('end_date', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        # 构建查询条件
        where_clauses = []
        params = []

        if user_id:
            where_clauses.append('user_id = ?')
            params.append(user_id)

        if transaction_type:
            where_clauses.append('transaction_type = ?')
            params.append(transaction_type)

        if rule_code:
            where_clauses.append('rule_code = ?')
            params.append(rule_code)

        if start_date:
            where_clauses.append('date(created_at) >= ?')
            params.append(start_date)

        if end_date:
            where_clauses.append('date(created_at) <= ?')
            params.append(end_date)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        # 查询总数
        count_query = f"SELECT COUNT(*) FROM contribution_transactions WHERE {where_sql}"
        total = db.execute(count_query, params).fetchone()[0]

        # 查询数据
        offset = (page - 1) * page_size
        query = f"""
            SELECT t.*, u.username, u.real_name
            FROM contribution_transactions t
            LEFT JOIN users u ON t.user_id = u.id
            WHERE {where_sql}
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        transactions = db.execute(query, params).fetchall()

        return jsonify({
            'success': True,
            'transactions': [dict(t) for t in transactions],
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        logger.error(f"获取交易记录失败: {str(e)}")
        return jsonify({'error': f'获取交易记录失败: {str(e)}'}), 500


@contribution_bp.route('/admin/contribution/adjust', methods=['POST'])
@admin_required
def adjust_contribution():
    """
    调整用户贡献值
    """
    try:
        db = get_db()
        data = request.get_json()

        # 验证必填字段
        required_fields = ['user_id', 'contribution_change', 'reason']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        user_id = data['user_id']
        contribution_change = data['contribution_change']
        lingzhi_change = data.get('lingzhi_change', 0)
        reason = data['reason']

        # 检查用户是否存在
        user = db.execute(
            'SELECT id, total_contribution, cumulative_contribution, total_lingzhi FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 获取当前余额
        old_contribution = user['total_contribution']
        old_lingzhi = user['total_lingzhi']

        # 计算新余额
        new_contribution = old_contribution + contribution_change
        new_lingzhi = old_lingzhi + lingzhi_change
        new_cumulative = user['cumulative_contribution'] + max(0, contribution_change)

        if new_contribution < 0:
            return jsonify({'error': '贡献值不能为负数'}), 400

        # 创建交易记录
        db.execute(
            """INSERT INTO contribution_transactions
               (user_id, rule_code, rule_name, transaction_type,
                contribution_change, balance_before, balance_after,
                lingzhi_change, lingzhi_balance_before, lingzhi_balance_after,
                description, status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                user_id,
                'admin_adjust',
                '管理员调整',
                'adjust',
                contribution_change,
                old_contribution,
                new_contribution,
                lingzhi_change,
                old_lingzhi,
                new_lingzhi,
                reason,
                'completed'
            )
        )

        # 更新用户余额
        db.execute(
            """UPDATE users
               SET total_contribution = ?,
                   cumulative_contribution = ?,
                   total_lingzhi = ?,
                   updated_at = ?
               WHERE id = ?""",
            (new_contribution, new_cumulative, new_lingzhi, datetime.now().isoformat(), user_id)
        )
        db.commit()

        logger.info(f"管理员调整用户 {user_id}: 贡献值{contribution_change:+d}, 灵值{lingzhi_change:+d}, 原因: {reason}")

        return jsonify({
            'success': True,
            'message': '贡献值调整成功',
            'new_values': {
                'total_contribution': new_contribution,
                'cumulative_contribution': new_cumulative,
                'total_lingzhi': new_lingzhi
            }
        }), 200

    except Exception as e:
        logger.error(f"调整贡献值失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'调整贡献值失败: {str(e)}'}), 500


# ==================== 贡献值统计API ====================

@contribution_bp.route('/admin/contribution/stats', methods=['GET'])
@login_required
def get_stats():
    """
    获取贡献值统计信息
    """
    try:
        db = get_db()

        # 总贡献值发放量
        total_earned = db.execute(
            "SELECT SUM(contribution_change) FROM contribution_transactions WHERE transaction_type = 'earn' AND status = 'completed'"
        ).fetchone()[0] or 0

        # 总贡献值消耗量
        total_consumed = db.execute(
            "SELECT SUM(ABS(contribution_change)) FROM contribution_transactions WHERE transaction_type = 'consume' AND status = 'completed'"
        ).fetchone()[0] or 0

        # 贡献值交易笔数
        total_transactions = db.execute(
            "SELECT COUNT(*) FROM contribution_transactions WHERE status = 'completed'"
        ).fetchone()[0] or 0

        # 活跃用户数（近30天有交易）
        active_users = db.execute(
            """SELECT COUNT(DISTINCT user_id)
               FROM contribution_transactions
               WHERE created_at >= date('now', '-30 days')
               AND status = 'completed'"""
        ).fetchone()[0] or 0

        # 今日贡献值发放
        today_earned = db.execute(
            """SELECT SUM(contribution_change)
               FROM contribution_transactions
               WHERE transaction_type = 'earn'
               AND date(created_at) = date('now')
               AND status = 'completed'"""
        ).fetchone()[0] or 0

        # 今日贡献值消耗
        today_consumed = db.execute(
            """SELECT SUM(ABS(contribution_change))
               FROM contribution_transactions
               WHERE transaction_type = 'consume'
               AND date(created_at) = date('now')
               AND status = 'completed'"""
        ).fetchone()[0] or 0

        # 贡献值排行榜Top 10
        leaderboard = db.execute(
            """SELECT u.id, u.username, u.real_name, u.total_contribution, u.cumulative_contribution, u.total_lingzhi
               FROM users u
               WHERE u.status = 'active'
               ORDER BY u.total_contribution DESC
               LIMIT 10"""
        ).fetchall()

        return jsonify({
            'success': True,
            'stats': {
                'total_earned': total_earned,
                'total_consumed': total_consumed,
                'total_balance': total_earned - total_consumed,
                'total_transactions': total_transactions,
                'active_users': active_users,
                'today_earned': today_earned,
                'today_consumed': today_consumed
            },
            'leaderboard': [dict(u) for u in leaderboard]
        }), 200

    except Exception as e:
        logger.error(f"获取统计信息失败: {str(e)}")
        return jsonify({'error': f'获取统计信息失败: {str(e)}'}), 500


@contribution_bp.route('/admin/contribution/users/<int:user_id>/stats', methods=['GET'])
@login_required
def get_user_stats(user_id):
    """
    获取用户贡献值统计
    """
    try:
        db = get_db()

        # 检查用户是否存在
        user = db.execute(
            'SELECT id, username, real_name, total_contribution, cumulative_contribution, total_lingzhi FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if not user:
            return jsonify({'error': '用户不存在'}), 404

        # 总赚取贡献值
        total_earned = db.execute(
            """SELECT SUM(contribution_change)
               FROM contribution_transactions
               WHERE user_id = ? AND transaction_type = 'earn' AND status = 'completed'""",
            (user_id,)
        ).fetchone()[0] or 0

        # 总消耗贡献值
        total_consumed = db.execute(
            """SELECT SUM(ABS(contribution_change))
               FROM contribution_transactions
               WHERE user_id = ? AND transaction_type = 'consume' AND status = 'completed'""",
            (user_id,)
        ).fetchone()[0] or 0

        # 交易笔数
        total_transactions = db.execute(
            """SELECT COUNT(*)
               FROM contribution_transactions
               WHERE user_id = ? AND status = 'completed'""",
            (user_id,)
        ).fetchone()[0] or 0

        # 今日赚取
        today_earned = db.execute(
            """SELECT SUM(contribution_change)
               FROM contribution_transactions
               WHERE user_id = ? AND transaction_type = 'earn'
               AND date(created_at) = date('now')
               AND status = 'completed'""",
            (user_id,)
        ).fetchone()[0] or 0

        # 今日消耗
        today_consumed = db.execute(
            """SELECT SUM(ABS(contribution_change))
               FROM contribution_transactions
               WHERE user_id = ? AND transaction_type = 'consume'
               AND date(created_at) = date('now')
               AND status = 'completed'""",
            (user_id,)
        ).fetchone()[0] or 0

        # 最近交易记录
        recent_transactions = db.execute(
            """SELECT *
               FROM contribution_transactions
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT 10""",
            (user_id,)
        ).fetchall()

        return jsonify({
            'success': True,
            'user': dict(user),
            'stats': {
                'total_earned': total_earned,
                'total_consumed': total_consumed,
                'total_balance': total_earned - total_consumed,
                'total_transactions': total_transactions,
                'today_earned': today_earned,
                'today_consumed': today_consumed
            },
            'recent_transactions': [dict(t) for t in recent_transactions]
        }), 200

    except Exception as e:
        logger.error(f"获取用户统计失败: {str(e)}")
        return jsonify({'error': f'获取用户统计失败: {str(e)}'}), 500
