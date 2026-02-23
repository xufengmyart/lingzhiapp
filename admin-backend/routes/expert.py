#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
专家功能路由
支持任务系统、AIGC作品管理
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from database import get_db
from datetime import datetime, timedelta
import json
import logging

# 创建蓝图
expert_bp = Blueprint('expert', __name__)

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


def expert_required(f):
    """专家权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': '未授权'}), 401
        # TODO: 实现专家权限验证逻辑
        return f(*args, **kwargs)
    return decorated_function


# ==================== 专家任务系统 ====================

# 首先需要在数据库中创建任务相关表
# 注意：这些表的创建应该放在 database_init.py 中

@expert_bp.route('/expert/tasks', methods=['GET'])
@login_required
def get_tasks():
    """
    获取任务列表
    """
    try:
        db = get_db()

        expert_id = request.args.get('expert_id', '')
        status = request.args.get('status', '')
        task_type = request.args.get('task_type', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        where_clauses = []
        params = []

        if expert_id:
            where_clauses.append('assigned_expert_id = ?')
            params.append(expert_id)

        if status:
            where_clauses.append('status = ?')
            params.append(status)

        if task_type:
            where_clauses.append('task_type = ?')
            params.append(task_type)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        count_query = f"SELECT COUNT(*) FROM aesthetic_tasks WHERE {where_sql}"
        total = db.execute(count_query, params).fetchone()[0]

        offset = (page - 1) * page_size
        query = f"""
            SELECT t.*,
                   u.username as expert_name,
                   u.real_name as expert_real_name
            FROM aesthetic_tasks t
            LEFT JOIN users u ON t.assigned_expert_id = u.id
            WHERE {where_sql}
            ORDER BY t.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        tasks = db.execute(query, params).fetchall()

        return jsonify({
            'success': True,
            'tasks': [dict(t) for t in tasks],
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        logger.error(f"获取任务列表失败: {str(e)}")
        return jsonify({'error': f'获取任务列表失败: {str(e)}'}), 500


@expert_bp.route('/expert/tasks/<int:task_id>', methods=['GET'])
@login_required
def get_task_detail(task_id):
    """
    获取任务详情
    """
    try:
        db = get_db()

        task = db.execute(
            """SELECT t.*,
                   u.username as expert_name,
                   u.real_name as expert_real_name,
                   c.username as creator_name,
                   c.real_name as creator_real_name
            FROM aesthetic_tasks t
            LEFT JOIN users u ON t.assigned_expert_id = u.id
            LEFT JOIN users c ON t.created_by = c.id
            WHERE t.id = ?""",
            (task_id,)
        ).fetchone()

        if not task:
            return jsonify({'error': '任务不存在'}), 404

        return jsonify({
            'success': True,
            'task': dict(task)
        }), 200

    except Exception as e:
        logger.error(f"获取任务详情失败: {str(e)}")
        return jsonify({'error': f'获取任务详情失败: {str(e)}'}), 500


@expert_bp.route('/expert/tasks/<int:task_id>/claim', methods=['POST'])
@expert_required
def claim_task(task_id):
    """
    专家承接任务
    """
    try:
        db = get_db()
        data = request.get_json()

        expert_id = data.get('expert_id')

        if not expert_id:
            return jsonify({'error': '缺少专家ID'}), 400

        # 检查任务是否存在
        task = db.execute(
            "SELECT id, status, assigned_expert_id FROM aesthetic_tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if not task:
            return jsonify({'error': '任务不存在'}), 404

        if task['status'] != 'open':
            return jsonify({'error': '任务已被承接或关闭'}), 400

        # 更新任务状态
        db.execute(
            """UPDATE aesthetic_tasks
               SET assigned_expert_id = ?, status = 'in_progress', claimed_at = ?
               WHERE id = ?""",
            (expert_id, datetime.now().isoformat(), task_id)
        )
        db.commit()

        logger.info(f"专家 {expert_id} 承接任务 {task_id}")

        return jsonify({
            'success': True,
            'message': '任务承接成功'
        }), 200

    except Exception as e:
        logger.error(f"承接任务失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'承接任务失败: {str(e)}'}), 500


@expert_bp.route('/expert/tasks/<int:task_id>/submit', methods=['POST'])
@expert_required
def submit_task(task_id):
    """
    专家提交任务
    """
    try:
        db = get_db()
        data = request.get_json()

        # 验证必填字段
        required_fields = ['submission_content', 'submission_files']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 检查任务是否存在
        task = db.execute(
            "SELECT id, status, assigned_expert_id, task_title, reward_contribution FROM aesthetic_tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if not task:
            return jsonify({'error': '任务不存在'}), 404

        if task['status'] != 'in_progress':
            return jsonify({'error': '任务状态不允许提交'}), 400

        # 更新任务状态
        db.execute(
            """UPDATE aesthetic_tasks
               SET status = 'submitted',
                   submission_content = ?,
                   submission_files = ?,
                   submitted_at = ?
               WHERE id = ?""",
            (
                data['submission_content'],
                json.dumps(data['submission_files']),
                datetime.now().isoformat(),
                task_id
            )
        )

        # 创建贡献值交易记录（待审核通过后发放）
        # 这里只记录提交，实际奖励在审核通过后发放

        db.commit()

        logger.info(f"专家 {task['assigned_expert_id']} 提交任务 {task_id}")

        return jsonify({
            'success': True,
            'message': '任务提交成功，等待审核'
        }), 200

    except Exception as e:
        logger.error(f"提交任务失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'提交任务失败: {str(e)}'}), 500


@expert_bp.route('/expert/tasks/<int:task_id>/complete', methods=['POST'])
@login_required
def complete_task(task_id):
    """
    管理员审核通过任务，发放奖励
    """
    try:
        db = get_db()
        data = request.get_json()

        expert_id = data.get('expert_id')
        review_result = data.get('review_result')  # approved | rejected
        review_comment = data.get('review_comment', '')

        if not expert_id or not review_result:
            return jsonify({'error': '缺少必填字段'}), 400

        # 检查任务是否存在
        task = db.execute(
            "SELECT id, status, assigned_expert_id, reward_contribution, reward_lingzhi FROM aesthetic_tasks WHERE id = ?",
            (task_id,)
        ).fetchone()

        if not task:
            return jsonify({'error': '任务不存在'}), 404

        if task['status'] != 'submitted':
            return jsonify({'error': '任务状态不允许审核'}), 400

        if review_result == 'approved':
            # 更新任务状态为已完成
            db.execute(
                """UPDATE aesthetic_tasks
                   SET status = 'completed',
                       review_result = ?,
                       review_comment = ?,
                       reviewed_at = ?
                   WHERE id = ?""",
                (review_result, review_comment, datetime.now().isoformat(), task_id)
            )

            # 查找赚取规则
            rule = db.execute(
                "SELECT id, contribution_value, lingzhi_value FROM contribution_rules WHERE rule_code = 'expert_complete_task' AND status = 'active'"
            ).fetchone()

            if rule:
                # 创建贡献值交易记录
                expert = db.execute(
                    "SELECT id, total_contribution, total_lingzhi FROM users WHERE id = ?",
                    (expert_id,)
                ).fetchone()

                if expert:
                    old_contribution = expert['total_contribution']
                    old_lingzhi = expert['total_lingzhi']
                    new_contribution = old_contribution + rule['contribution_value']
                    new_lingzhi = old_lingzhi + rule['lingzhi_value']

                    db.execute(
                        """INSERT INTO contribution_transactions
                           (user_id, rule_id, rule_code, rule_name, transaction_type,
                            contribution_change, balance_before, balance_after,
                            lingzhi_change, lingzhi_balance_before, lingzhi_balance_after,
                            related_entity_type, related_entity_id, description, status)
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (
                            expert_id,
                            rule['id'],
                            'expert_complete_task',
                            '专家完成任务',
                            'earn',
                            rule['contribution_value'],
                            old_contribution,
                            new_contribution,
                            rule['lingzhi_value'],
                            old_lingzhi,
                            new_lingzhi,
                            'task',
                            task_id,
                            f'完成任务: {task_id}',
                            'completed'
                        )
                    )

                    # 更新专家贡献值和灵值
                    db.execute(
                        """UPDATE users
                           SET total_contribution = ?,
                               cumulative_contribution = cumulative_contribution + ?,
                               total_lingzhi = ?,
                               updated_at = ?
                           WHERE id = ?""",
                        (new_contribution, max(0, rule['contribution_value']), new_lingzhi,
                         datetime.now().isoformat(), expert_id)
                    )

            message = f'任务审核通过，获得 {rule["contribution_value"] if rule else 0} 贡献值和 {rule["lingzhi_value"] if rule else 0} 灵值'

        else:
            # 审核未通过，任务状态改为重新提交
            db.execute(
                """UPDATE aesthetic_tasks
                   SET status = 'needs_revision',
                       review_result = ?,
                       review_comment = ?,
                       reviewed_at = ?
                   WHERE id = ?""",
                (review_result, review_comment, datetime.now().isoformat(), task_id)
            )
            message = '任务审核未通过，请修改后重新提交'

        db.commit()

        logger.info(f"任务 {task_id} 审核: {review_result}")

        return jsonify({
            'success': True,
            'message': message
        }), 200

    except Exception as e:
        logger.error(f"审核任务失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'审核任务失败: {str(e)}'}), 500


# ==================== 专家AIGC作品管理 ====================

@expert_bp.route('/expert/aigc-works', methods=['POST'])
@expert_required
def create_aigc_work():
    """
    专家上传AIGC作品
    """
    try:
        db = get_db()
        data = request.get_json()

        # 验证必填字段
        required_fields = ['expert_id', 'work_title', 'work_type', 'file_urls']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'缺少必填字段: {field}'}), 400

        # 查找赚取规则
        rule = db.execute(
            "SELECT id, contribution_value, lingzhi_value FROM contribution_rules WHERE rule_code = 'expert_aigc_work' AND status = 'active'"
        ).fetchone()

        if not rule:
            return jsonify({'error': '相关规则不存在'}), 400

        # 检查每日限制
        if rule['contribution_value'] > 0:
            today_count = db.execute(
                """SELECT COUNT(*) FROM aigc_works
                   WHERE expert_id = ? AND date(created_at) = date('now')""",
                (data['expert_id'],)
            ).fetchone()[0]

            max_daily = db.execute(
                "SELECT max_daily_times FROM contribution_rules WHERE rule_code = 'expert_aigc_work'"
            ).fetchone()[0]

            if max_daily and today_count >= max_daily:
                return jsonify({'error': f'今日上传作品数已达上限（{max_daily}个）'}), 400

        # 插入AIGC作品
        db.execute(
            """INSERT INTO aigc_works
               (expert_id, work_title, work_type, file_urls, description,
                tags, status, verification_status)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                data['expert_id'],
                data['work_title'],
                data['work_type'],
                json.dumps(data['file_urls']),
                data.get('description', ''),
                json.dumps(data.get('tags', [])),
                'active',
                'pending'
            )
        )

        work_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]

        # 创建贡献值交易记录（待审核通过后发放）
        expert = db.execute(
            "SELECT id, total_contribution, total_lingzhi FROM users WHERE id = ?",
            (data['expert_id'],)
        ).fetchone()

        if expert and rule:
            old_contribution = expert['total_contribution']
            old_lingzhi = expert['total_lingzhi']
            new_contribution = old_contribution + rule['contribution_value']
            new_lingzhi = old_lingzhi + rule['lingzhi_value']

            db.execute(
                """INSERT INTO contribution_transactions
                   (user_id, rule_id, rule_code, rule_name, transaction_type,
                    contribution_change, balance_before, balance_after,
                    lingzhi_change, lingzhi_balance_before, lingzhi_balance_after,
                    related_entity_type, related_entity_id, description, status)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    data['expert_id'],
                    rule['id'],
                    'expert_aigc_work',
                    '专家AIGC作品',
                    'earn',
                    rule['contribution_value'],
                    old_contribution,
                    new_contribution,
                    rule['lingzhi_value'],
                    old_lingzhi,
                    new_lingzhi,
                    'aigc_work',
                    work_id,
                    f'上传AIGC作品: {data["work_title"]}',
                    'completed'
                )
            )

            # 更新专家贡献值和灵值
            db.execute(
                """UPDATE users
                   SET total_contribution = ?,
                       cumulative_contribution = cumulative_contribution + ?,
                       total_lingzhi = ?,
                       updated_at = ?
                   WHERE id = ?""",
                (new_contribution, max(0, rule['contribution_value']), new_lingzhi,
                 datetime.now().isoformat(), data['expert_id'])
            )

        db.commit()

        logger.info(f"专家 {data['expert_id']} 上传AIGC作品: {data['work_title']}")

        return jsonify({
            'success': True,
            'message': f'作品上传成功，获得 {rule["contribution_value"] if rule else 0} 贡献值和 {rule["lingzhi_value"] if rule else 0} 灵值',
            'work_id': work_id,
            'reward': {
                'contribution': rule['contribution_value'] if rule else 0,
                'lingzhi': rule['lingzhi_value'] if rule else 0
            }
        }), 201

    except Exception as e:
        logger.error(f"上传AIGC作品失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'上传AIGC作品失败: {str(e)}'}), 500


@expert_bp.route('/expert/aigc-works', methods=['GET'])
@login_required
def get_aigc_works():
    """
    获取AIGC作品列表
    """
    try:
        db = get_db()

        expert_id = request.args.get('expert_id', '')
        status = request.args.get('status', '')
        work_type = request.args.get('work_type', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))

        where_clauses = []
        params = []

        if expert_id:
            where_clauses.append('expert_id = ?')
            params.append(expert_id)

        if status:
            where_clauses.append('status = ?')
            params.append(status)

        if work_type:
            where_clauses.append('work_type = ?')
            params.append(work_type)

        where_sql = ' AND '.join(where_clauses) if where_clauses else '1=1'

        count_query = f"SELECT COUNT(*) FROM aigc_works WHERE {where_sql}"
        total = db.execute(count_query, params).fetchone()[0]

        offset = (page - 1) * page_size
        query = f"""
            SELECT w.*,
                   u.username as expert_name,
                   u.real_name as expert_real_name
            FROM aigc_works w
            LEFT JOIN users u ON w.expert_id = u.id
            WHERE {where_sql}
            ORDER BY w.created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([page_size, offset])

        works = db.execute(query, params).fetchall()

        return jsonify({
            'success': True,
            'works': [dict(w) for w in works],
            'total': total,
            'page': page,
            'page_size': page_size
        }), 200

    except Exception as e:
        logger.error(f"获取AIGC作品列表失败: {str(e)}")
        return jsonify({'error': f'获取AIGC作品列表失败: {str(e)}'}), 500


@expert_bp.route('/expert/aigc-works/<int:work_id>', methods=['PUT'])
@login_required
def update_aigc_work(work_id):
    """
    更新AIGC作品信息
    """
    try:
        db = get_db()
        data = request.get_json()

        # 检查作品是否存在
        work = db.execute(
            "SELECT id, verification_status FROM aigc_works WHERE id = ?",
            (work_id,)
        ).fetchone()

        if not work:
            return jsonify({'error': '作品不存在'}), 404

        if work['verification_status'] == 'approved':
            return jsonify({'error': '已审核通过的作品不能修改'}), 400

        # 构建更新SQL
        update_fields = []
        update_values = []

        editable_fields = ['work_title', 'description', 'tags', 'file_urls']

        for field in editable_fields:
            if field in data:
                if field in ['tags', 'file_urls']:
                    update_fields.append(f"{field} = ?")
                    update_values.append(json.dumps(data[field]))
                else:
                    update_fields.append(f"{field} = ?")
                    update_values.append(data[field])

        if not update_fields:
            return jsonify({'error': '没有要更新的字段'}), 400

        update_fields.append("updated_at = ?")
        update_values.append(datetime.now().isoformat())
        update_values.append(work_id)

        sql = f"UPDATE aigc_works SET {', '.join(update_fields)} WHERE id = ?"
        db.execute(sql, update_values)
        db.commit()

        return jsonify({
            'success': True,
            'message': '作品信息更新成功'
        }), 200

    except Exception as e:
        logger.error(f"更新AIGC作品失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'更新AIGC作品失败: {str(e)}'}), 500


@expert_bp.route('/expert/aigc-works/<int:work_id>', methods=['DELETE'])
@login_required
def delete_aigc_work(work_id):
    """
    删除AIGC作品
    """
    try:
        db = get_db()

        # 检查作品是否存在
        work = db.execute(
            "SELECT id, verification_status FROM aigc_works WHERE id = ?",
            (work_id,)
        ).fetchone()

        if not work:
            return jsonify({'error': '作品不存在'}), 404

        if work['verification_status'] == 'approved':
            return jsonify({'error': '已审核通过的作品不能删除'}), 400

        # 删除作品
        db.execute('DELETE FROM aigc_works WHERE id = ?', (work_id,))
        db.commit()

        logger.info(f"删除AIGC作品: {work_id}")

        return jsonify({
            'success': True,
            'message': '作品删除成功'
        }), 200

    except Exception as e:
        logger.error(f"删除AIGC作品失败: {str(e)}")
        db.rollback()
        return jsonify({'error': f'删除AIGC作品失败: {str(e)}'}), 500
