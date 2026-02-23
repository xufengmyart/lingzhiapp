"""
美学侦探任务系统API
实现任务的创建、认领、提交、审核等功能
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
import json
import os
import sys
import sqlite3

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

aesthetic_bp = Blueprint('aesthetic_tasks', __name__, url_prefix='/api/aesthetic-tasks')

DB_PATH = config.DATABASE_PATH

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': '未登录'}), 401
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': '未登录'}), 401
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if not result or result[0] != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

# ==================== 任务管理 ====================

@aesthetic_bp.route('', methods=['POST'])
@admin_required
def create_task():
    """创建美学侦探任务"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO aesthetic_tasks (
                title, description, type, difficulty,
                required_skills, points, contribution_reward,
                spirit_reward, deadline, status,
                max_participants, tags, location,
                created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title'),
            data.get('description'),
            data.get('type', 'general'),
            data.get('difficulty', 'medium'),
            json.dumps(data.get('required_skills', [])),
            data.get('points', 100),
            data.get('contribution_reward', 100),
            data.get('spirit_reward', 50),
            data.get('deadline'),
            'open',
            data.get('max_participants'),
            json.dumps(data.get('tags', [])),
            data.get('location'),
            request.user_id
        ))
        
        task_id = cursor.lastrowid
        conn.commit()
        
        conn.close()
        return jsonify({'message': '任务创建成功', 'id': task_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@aesthetic_bp.route('', methods=['GET'])
def get_tasks():
    """获取任务列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    task_type = request.args.get('type')
    difficulty = request.args.get('difficulty')
    assigned_to = request.args.get('assigned_to')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM aesthetic_tasks WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if task_type:
        query += " AND type = ?"
        params.append(task_type)
    if difficulty:
        query += " AND difficulty = ?"
        params.append(difficulty)
    if assigned_to:
        query += " AND assigned_to = ?"
        params.append(assigned_to)
    
    # 获取总数
    count_query = query.replace('*', 'COUNT(*)')
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # 分页查询
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    tasks = cursor.fetchall()
    
    # 格式化结果
    result = []
    for task in tasks:
        result.append({
            'id': task[0],
            'title': task[1],
            'description': task[2],
            'type': task[3],
            'difficulty': task[4],
            'required_skills': json.loads(task[5]) if task[5] else [],
            'points': task[6],
            'contribution_reward': task[7],
            'spirit_reward': task[8],
            'status': task[9],
            'assigned_to': task[10],
            'deadline': task[11],
            'max_participants': task[12],
            'tags': json.loads(task[13]) if task[13] else [],
            'location': task[14],
            'created_at': task[15],
            'updated_at': task[16],
            'created_by': task[17],
            'completed_at': task[18]
        })
    
    conn.close()
    
    return jsonify({
        'tasks': result,
        'total': total,
        'page': page,
        'per_page': per_page
    })

@aesthetic_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    """获取任务详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM aesthetic_tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    
    if not task:
        conn.close()
        return jsonify({'error': '任务不存在'}), 404
    
    result = {
        'id': task[0],
        'title': task[1],
        'description': task[2],
        'type': task[3],
        'difficulty': task[4],
        'required_skills': json.loads(task[5]) if task[5] else [],
        'points': task[6],
        'contribution_reward': task[7],
        'spirit_reward': task[8],
        'status': task[9],
        'assigned_to': task[10],
        'deadline': task[11],
        'max_participants': task[12],
        'tags': json.loads(task[13]) if task[13] else [],
        'location': task[14],
        'created_at': task[15],
        'updated_at': task[16],
        'created_by': task[17],
        'completed_at': task[18]
    }
    
    conn.close()
    return jsonify(result)

@aesthetic_bp.route('/<int:task_id>', methods=['PUT'])
@admin_required
def update_task(task_id):
    """更新任务信息"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM aesthetic_tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '任务不存在'}), 404
    
    try:
        update_fields = []
        params = []
        
        if 'title' in data:
            update_fields.append("title = ?")
            params.append(data['title'])
        if 'description' in data:
            update_fields.append("description = ?")
            params.append(data['description'])
        if 'type' in data:
            update_fields.append("type = ?")
            params.append(data['type'])
        if 'difficulty' in data:
            update_fields.append("difficulty = ?")
            params.append(data['difficulty'])
        if 'required_skills' in data:
            update_fields.append("required_skills = ?")
            params.append(json.dumps(data['required_skills']))
        if 'points' in data:
            update_fields.append("points = ?")
            params.append(data['points'])
        if 'contribution_reward' in data:
            update_fields.append("contribution_reward = ?")
            params.append(data['contribution_reward'])
        if 'spirit_reward' in data:
            update_fields.append("spirit_reward = ?")
            params.append(data['spirit_reward'])
        if 'status' in data:
            update_fields.append("status = ?")
            params.append(data['status'])
        if 'deadline' in data:
            update_fields.append("deadline = ?")
            params.append(data['deadline'])
        if 'max_participants' in data:
            update_fields.append("max_participants = ?")
            params.append(data['max_participants'])
        if 'tags' in data:
            update_fields.append("tags = ?")
            params.append(json.dumps(data['tags']))
        if 'location' in data:
            update_fields.append("location = ?")
            params.append(data['location'])
        
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(task_id)
        
        query = f"UPDATE aesthetic_tasks SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '任务更新成功'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@aesthetic_bp.route('/<int:task_id>', methods=['DELETE'])
@admin_required
def delete_task(task_id):
    """删除任务"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM aesthetic_tasks WHERE id = ?", (task_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '任务不存在'}), 404
    
    cursor.execute("DELETE FROM aesthetic_tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '任务删除成功'})

# ==================== 任务执行 ====================

@aesthetic_bp.route('/<int:task_id>/claim', methods=['POST'])
@login_required
def claim_task(task_id):
    """认领任务"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM aesthetic_tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    
    if not task:
        conn.close()
        return jsonify({'error': '任务不存在'}), 404
    
    # 检查任务状态
    status_index = 9  # status 字段索引
    if task[status_index] != 'open':
        conn.close()
        return jsonify({'error': '任务已被认领或已完成'}), 400
    
    try:
        # 更新任务状态和认领人
        cursor.execute('''
            UPDATE aesthetic_tasks
            SET status = 'in_progress',
                assigned_to = ?,
                updated_at = ?
            WHERE id = ?
        ''', (request.user_id, datetime.now().isoformat(), task_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '任务认领成功'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@aesthetic_bp.route('/<int:task_id>/submit', methods=['POST'])
@login_required
def submit_task(task_id):
    """提交任务"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM aesthetic_tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    
    if not task:
        conn.close()
        return jsonify({'error': '任务不存在'}), 404
    
    # 检查是否是认领人
    assigned_to_index = 10
    if task[assigned_to_index] != int(request.user_id):
        conn.close()
        return jsonify({'error': '您不是该任务的认领人'}), 403
    
    # 检查任务状态
    status_index = 9
    if task[status_index] != 'in_progress':
        conn.close()
        return jsonify({'error': '任务状态不正确'}), 400
    
    try:
        # 更新任务状态为已提交
        cursor.execute('''
            UPDATE aesthetic_tasks
            SET status = 'submitted',
                updated_at = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), task_id))
        
        # 创建任务提交记录
        cursor.execute('''
            INSERT INTO task_submissions (
                task_id, user_id, content, files,
                status, submitted_at
            ) VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            task_id,
            request.user_id,
            data.get('content'),
            json.dumps(data.get('files', [])),
            'pending_review',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '任务提交成功，等待审核'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@aesthetic_bp.route('/<int:task_id>/complete', methods=['POST'])
@admin_required
def complete_task(task_id):
    """审核并完成任务"""
    data = request.json
    approved = data.get('approved', True)
    feedback = data.get('feedback', '')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM aesthetic_tasks WHERE id = ?", (task_id,))
    task = cursor.fetchone()
    
    if not task:
        conn.close()
        return jsonify({'error': '任务不存在'}), 404
    
    # 检查任务状态
    status_index = 9
    if task[status_index] != 'submitted':
        conn.close()
        return jsonify({'error': '任务尚未提交'}), 400
    
    try:
        assigned_to_index = 10
        contribution_reward_index = 7
        spirit_reward_index = 8
        
        if approved:
            # 通过：完成任务并发放奖励
            cursor.execute('''
                UPDATE aesthetic_tasks
                SET status = 'completed',
                    completed_at = ?,
                    updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), datetime.now().isoformat(), task_id))
            
            # 获取用户贡献值和灵值奖励
            contribution_reward = task[contribution_reward_index]
            spirit_reward = task[spirit_reward_index]
            
            # 查找对应的贡献值规则
            cursor.execute("SELECT id FROM contribution_rules WHERE rule_code = ?", ('aesthetic_task_complete',))
            rule_result = cursor.fetchone()
            rule_id = rule_result[0] if rule_result else None
            
            if rule_id:
                # 检查每日限制
                today = datetime.now().strftime('%Y-%m-%d')
                cursor.execute('''
                    SELECT COUNT(*) FROM contribution_transactions
                    WHERE user_id = ? AND rule_id = ? AND DATE(created_at) = ?
                ''', (task[assigned_to_index], rule_id, today))
                count = cursor.fetchone()[0]
                
                cursor.execute("SELECT daily_limit FROM contribution_rules WHERE id = ?", (rule_id,))
                daily_limit = cursor.fetchone()[0]
                
                if daily_limit and count >= daily_limit:
                    conn.close()
                    return jsonify({'error': f'今日任务完成次数已达上限（{daily_limit}次）'}), 400
                
                # 创建贡献值交易记录
                cursor.execute('''
                    INSERT INTO contribution_transactions (
                        user_id, rule_id, amount, type,
                        description, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    task[assigned_to_index],
                    rule_id,
                    contribution_reward,
                    'earned',
                    f'美学侦探任务完成：{task[1]}',
                    datetime.now().isoformat()
                ))
                
                # 更新用户贡献值
                cursor.execute('''
                    UPDATE user_balances
                    SET contribution_points = contribution_points + ?,
                        updated_at = ?
                    WHERE user_id = ?
                ''', (contribution_reward, datetime.now().isoformat(), task[assigned_to_index]))
                
                # 更新用户灵值
                cursor.execute('''
                    UPDATE user_balances
                    SET spirit_tokens = spirit_tokens + ?,
                        updated_at = ?
                    WHERE user_id = ?
                ''', (spirit_reward, datetime.now().isoformat(), task[assigned_to_index]))
            
        else:
            # 拒绝：任务退回到进行中
            cursor.execute('''
                UPDATE aesthetic_tasks
                SET status = 'in_progress',
                    updated_at = ?
                WHERE id = ?
            ''', (datetime.now().isoformat(), task_id))
        
        # 更新提交记录状态
        cursor.execute('''
            UPDATE task_submissions
            SET status = ?,
                feedback = ?,
                reviewed_at = ?
            WHERE task_id = ?
        ''', (
            'approved' if approved else 'rejected',
            feedback,
            datetime.now().isoformat(),
            task_id
        ))
        
        conn.commit()
        conn.close()
        
        if approved:
            return jsonify({'message': '任务审核通过，奖励已发放'})
        else:
            return jsonify({'message': '任务已退回，请修改后重新提交'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# ==================== 任务提交记录 ====================

@aesthetic_bp.route('/<int:task_id>/submissions', methods=['GET'])
@login_required
def get_task_submissions(task_id):
    """获取任务提交记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM task_submissions
        WHERE task_id = ?
        ORDER BY submitted_at DESC
    ''', (task_id,))
    
    submissions = cursor.fetchall()
    
    result = []
    for sub in submissions:
        result.append({
            'id': sub[0],
            'task_id': sub[1],
            'user_id': sub[2],
            'content': sub[3],
            'files': json.loads(sub[4]) if sub[4] else [],
            'status': sub[5],
            'feedback': sub[6],
            'submitted_at': sub[7],
            'reviewed_at': sub[8]
        })
    
    conn.close()
    return jsonify({'submissions': result})

# ==================== 统计接口 ====================

@aesthetic_bp.route('/stats', methods=['GET'])
@login_required
def get_user_task_stats():
    """获取用户任务统计"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取用户完成的任务数
    cursor.execute('''
        SELECT COUNT(*) FROM aesthetic_tasks
        WHERE assigned_to = ? AND status = 'completed'
    ''', (request.user_id,))
    completed_count = cursor.fetchone()[0]
    
    # 获取用户进行中的任务数
    cursor.execute('''
        SELECT COUNT(*) FROM aesthetic_tasks
        WHERE assigned_to = ? AND status = 'in_progress'
    ''', (request.user_id,))
    in_progress_count = cursor.fetchone()[0]
    
    # 获取用户提交待审核的任务数
    cursor.execute('''
        SELECT COUNT(*) FROM aesthetic_tasks
        WHERE assigned_to = ? AND status = 'submitted'
    ''', (request.user_id,))
    submitted_count = cursor.fetchone()[0]
    
    # 获取总积分
    cursor.execute('''
        SELECT SUM(points) FROM aesthetic_tasks
        WHERE assigned_to = ? AND status = 'completed'
    ''', (request.user_id,))
    total_points = cursor.fetchone()[0] or 0
    
    conn.close()
    
    return jsonify({
        'completed_count': completed_count,
        'in_progress_count': in_progress_count,
        'submitted_count': submitted_count,
        'total_points': total_points
    })
