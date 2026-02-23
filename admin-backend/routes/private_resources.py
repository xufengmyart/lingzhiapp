"""
私有资源库 API
功能：
1. 私有资源的增删改查
2. 授权管理
3. 资源自动匹配
4. 项目参与流程
5. 分润管理
6. 项目工作流
"""

import json
import sqlite3
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g

# 导入JWT认证中间件
from middleware.jwt_auth import require_auth

private_resources_bp = Blueprint('private_resources', __name__)


def get_db_connection():
    """获取数据库连接"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('/app/meiyueart-backend/data/lingzhi_ecosystem.db')
        db.row_factory = sqlite3.Row
    return db


def get_current_user_id():
    """获取当前用户ID"""
    return getattr(g, 'current_user_id', None)


# ==================== 私有资源管理 ====================

@private_resources_bp.route('/api/private-resources', methods=['GET'])
@require_auth
def get_private_resources():
    """
    获取当前用户的私有资源列表
    查询参数：status, resource_type, visibility
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        status = request.args.get('status')
        resource_type = request.args.get('resource_type')
        visibility = request.args.get('visibility')
        
        query = '''
            SELECT * FROM private_resources
            WHERE user_id = ? AND deleted_at IS NULL
        '''
        params = [user_id]
        
        if status:
            query += ' AND authorization_status = ?'
            params.append(status)
        
        if resource_type:
            query += ' AND resource_type = ?'
            params.append(resource_type)
        
        if visibility:
            query += ' AND visibility = ?'
            params.append(visibility)
        
        query += ' ORDER BY created_at DESC'
        
        resources = conn.execute(query, params).fetchall()
        
        resource_list = []
        for r in resources:
            resource_list.append({
                'id': r['id'],
                'resourceName': r['resource_name'],
                'resourceType': r['resource_type'],
                'department': r['department'],
                'contactName': r['contact_name'],
                'contactPhone': r['contact_phone'],
                'contactEmail': r['contact_email'],
                'position': r['position'],
                'description': r['description'],
                'authorizationStatus': r['authorization_status'],
                'authorizationNote': r['authorization_note'],
                'validFrom': r['valid_from'],
                'validUntil': r['valid_until'],
                'canSolve': r['can_solve'],
                'riskLevel': r['risk_level'],
                'verificationStatus': r['verification_status'],
                'visibility': r['visibility'],
                'createdAt': r['created_at'],
                'updatedAt': r['updated_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取资源列表成功',
            'data': resource_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/private-resources/<int:resource_id>', methods=['GET'])
@require_auth
def get_private_resource(resource_id):
    """获取单个私有资源详情"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        resource = conn.execute(
            'SELECT * FROM private_resources WHERE id = ? AND user_id = ? AND deleted_at IS NULL',
            (resource_id, user_id)
        ).fetchone()
        
        if not resource:
            return jsonify({'success': False, 'message': '资源不存在或无权限访问'}), 404
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取资源详情成功',
            'data': {
                'id': resource['id'],
                'resourceName': resource['resource_name'],
                'resourceType': resource['resource_type'],
                'department': resource['department'],
                'contactName': resource['contact_name'],
                'contactPhone': resource['contact_phone'],
                'contactEmail': resource['contact_email'],
                'position': resource['position'],
                'description': resource['description'],
                'authorizationStatus': resource['authorization_status'],
                'authorizationNote': resource['authorization_note'],
                'validFrom': resource['valid_from'],
                'validUntil': resource['valid_until'],
                'canSolve': resource['can_solve'],
                'riskLevel': resource['risk_level'],
                'verificationStatus': resource['verification_status'],
                'visibility': resource['visibility'],
                'createdAt': resource['created_at'],
                'updatedAt': resource['updated_at']
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/private-resources', methods=['POST'])
@require_auth
def create_private_resource():
    """创建新的私有资源"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        data = request.get_json()
        
        # 验证必填字段
        required_fields = ['resourceName', 'resourceType', 'contactName', 'contactPhone', 'canSolve']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        # 插入数据
        cursor = conn.execute(
            '''INSERT INTO private_resources 
            (user_id, resource_name, resource_type, department, contact_name, contact_phone, 
             contact_email, position, description, authorization_status, authorization_note,
             valid_from, valid_until, can_solve, risk_level, visibility)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                user_id,
                data.get('resourceName'),
                data.get('resourceType', 'other'),
                data.get('department'),
                data.get('contactName'),
                data.get('contactPhone'),
                data.get('contactEmail'),
                data.get('position'),
                data.get('description'),
                data.get('authorizationStatus', 'unauthorized'),
                data.get('authorizationNote'),
                data.get('validFrom'),
                data.get('validUntil'),
                data.get('canSolve'),
                data.get('riskLevel', 'low'),
                data.get('visibility', 'private')
            )
        )
        
        resource_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '资源创建成功',
            'data': {'id': resource_id}
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/private-resources/<int:resource_id>', methods=['PUT'])
@require_auth
def update_private_resource(resource_id):
    """更新私有资源"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        data = request.get_json()
        
        # 检查资源是否存在且属于当前用户
        resource = conn.execute(
            'SELECT * FROM private_resources WHERE id = ? AND user_id = ? AND deleted_at IS NULL',
            (resource_id, user_id)
        ).fetchone()
        
        if not resource:
            return jsonify({'success': False, 'message': '资源不存在或无权限访问'}), 404
        
        # 构建更新SQL
        update_fields = []
        update_values = []
        
        field_mapping = {
            'resourceName': 'resource_name',
            'resourceType': 'resource_type',
            'department': 'department',
            'contactName': 'contact_name',
            'contactPhone': 'contact_phone',
            'contactEmail': 'contact_email',
            'position': 'position',
            'description': 'description',
            'authorizationStatus': 'authorization_status',
            'authorizationNote': 'authorization_note',
            'validFrom': 'valid_from',
            'validUntil': 'valid_until',
            'canSolve': 'can_solve',
            'riskLevel': 'risk_level',
            'visibility': 'visibility'
        }
        
        for key, db_field in field_mapping.items():
            if key in data:
                update_fields.append(f'{db_field} = ?')
                update_values.append(data[key])
        
        if update_fields:
            update_values.append(resource_id)
            conn.execute(
                f'UPDATE private_resources SET {", ".join(update_fields)} WHERE id = ?',
                update_values
            )
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '资源更新成功'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/private-resources/<int:resource_id>', methods=['DELETE'])
@require_auth
def delete_private_resource(resource_id):
    """删除私有资源（软删除）"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 检查资源是否存在且属于当前用户
        resource = conn.execute(
            'SELECT * FROM private_resources WHERE id = ? AND user_id = ? AND deleted_at IS NULL',
            (resource_id, user_id)
        ).fetchone()
        
        if not resource:
            return jsonify({'success': False, 'message': '资源不存在或无权限访问'}), 404
        
        # 软删除
        conn.execute(
            'UPDATE private_resources SET deleted_at = ? WHERE id = ?',
            (datetime.now().isoformat(), resource_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '资源删除成功'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/private-resources/<int:resource_id>/authorize', methods=['POST'])
@require_auth
def authorize_resource(resource_id):
    """
    授权资源给项目使用
    参数：projectId, accessDuration, notes
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        data = request.get_json()
        
        # 检查资源是否存在且属于当前用户
        resource = conn.execute(
            'SELECT * FROM private_resources WHERE id = ? AND user_id = ? AND deleted_at IS NULL',
            (resource_id, user_id)
        ).fetchone()
        
        if not resource:
            return jsonify({'success': False, 'message': '资源不存在或无权限访问'}), 404
        
        project_id = data.get('projectId')
        if not project_id:
            return jsonify({'success': False, 'message': '缺少项目ID'}), 400
        
        # 更新资源授权状态
        conn.execute(
            '''UPDATE private_resources 
            SET authorization_status = 'authorized', 
                authorization_note = ?
            WHERE id = ?''',
            (data.get('notes'), resource_id)
        )
        
        # 记录访问授权日志
        access_duration = data.get('accessDuration', 'permanent')
        expiry_time = None
        if access_duration != 'permanent':
            # 计算过期时间
            duration_map = {
                '1month': 30,
                '3months': 90,
                '6months': 180,
                '1year': 365
            }
            days = duration_map.get(access_duration, 30)
            expiry_time = (datetime.now() + timedelta(days=days)).isoformat()
        
        conn.execute(
            '''INSERT INTO resource_access_logs 
            (resource_id, requester_id, request_type, request_reason, project_id,
             access_granted, granted_by, access_duration, expiry_time, notes)
            VALUES (?, ?, ?, ?, ?, 1, ?, ?, ?, ?)''',
            (resource_id, user_id, 'use', '项目授权', project_id,
             user_id, access_duration, expiry_time, data.get('notes'))
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '资源授权成功',
            'data': {
                'expiryTime': expiry_time
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 资源匹配 ====================

@private_resources_bp.route('/api/resource-matches', methods=['GET'])
@require_auth
def get_resource_matches():
    """获取当前用户的资源匹配记录"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        matches = conn.execute('''
            SELECT rm.*, pr.resource_name, p.project_name, p.status as project_status
            FROM resource_matches rm
            JOIN private_resources pr ON rm.resource_id = pr.id
            JOIN company_projects p ON rm.project_id = p.id
            WHERE pr.user_id = ?
            ORDER BY rm.match_score DESC, rm.created_at DESC
        ''', (user_id,)).fetchall()
        
        match_list = []
        for m in matches:
            match_list.append({
                'id': m['id'],
                'resourceId': m['resource_id'],
                'resourceName': m['resource_name'],
                'projectId': m['project_id'],
                'projectName': m['project_name'],
                'projectStatus': m['project_status'],
                'matchScore': m['match_score'],
                'matchReason': m['match_reason'],
                'status': m['status'],
                'createdAt': m['created_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取匹配记录成功',
            'data': match_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/resource-matches/auto-match', methods=['POST'])
@require_auth
def auto_match_resources():
    """
    自动匹配资源到项目
    系统根据资源的 can_solve 字段和项目需求自动匹配
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 获取用户已授权且可见的资源
        resources = conn.execute('''
            SELECT * FROM private_resources
            WHERE user_id = ? 
              AND authorization_status = 'authorized'
              AND visibility = 'matchable'
              AND deleted_at IS NULL
              AND (valid_until IS NULL OR valid_until >= date('now'))
        ''', (user_id,)).fetchall()
        
        match_count = 0
        
        for resource in resources:
            # 查找需要该资源的开放项目
            projects = conn.execute('''
                SELECT p.id, p.project_name, p.description, p.status
                FROM company_projects p
                LEFT JOIN resource_matches rm ON p.id = rm.project_id AND rm.resource_id = ?
                WHERE p.status IN ('recruiting', 'active')
                  AND rm.id IS NULL
                  AND (p.description LIKE ? OR ? LIKE '%' || p.project_name || '%')
            ''', (resource['id'], f'%{resource["can_solve"]}%', resource['can_solve'])).fetchall()
            
            for project in projects:
                # 计算匹配分数（简化版）
                match_score = 60.0
                if resource['verification_status'] == 'verified':
                    match_score += 20
                if resource['risk_level'] == 'low':
                    match_score += 10
                if project['status'] == 'recruiting':
                    match_score += 10
                
                # 创建匹配记录
                conn.execute('''
                    INSERT INTO resource_matches
                    (resource_id, project_id, match_score, match_reason, status, initiated_by)
                    VALUES (?, ?, ?, ?, 'pending', 'system')
                ''', (resource['id'], project['id'], match_score, 
                      f'资源可解决: {resource["can_solve"]}'))
                match_count += 1
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'自动匹配完成，创建 {match_count} 条匹配记录',
            'data': {'matchCount': match_count}
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/resource-matches/<int:match_id>/respond', methods=['POST'])
@require_auth
def respond_to_match(match_id):
    """
    响应资源匹配
    参数：action (accept/reject)
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        data = request.get_json()
        
        action = data.get('action')
        if action not in ['accept', 'reject']:
            return jsonify({'success': False, 'message': '无效的操作'}), 400
        
        # 检查匹配记录是否属于当前用户
        match = conn.execute('''
            SELECT rm.*, pr.user_id
            FROM resource_matches rm
            JOIN private_resources pr ON rm.resource_id = pr.id
            WHERE rm.id = ?
        ''', (match_id,)).fetchone()
        
        if not match or match['user_id'] != user_id:
            return jsonify({'success': False, 'message': '匹配记录不存在或无权限访问'}), 404
        
        # 更新匹配状态
        status = 'approved' if action == 'accept' else 'rejected'
        conn.execute(
            'UPDATE resource_matches SET status = ? WHERE id = ?',
            (status, match_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'匹配{status == "approved" and "已接受" or "已拒绝"}'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 项目参与 ====================

@private_resources_bp.route('/api/project-participations', methods=['GET'])
@require_auth
def get_project_participations():
    """获取当前用户的项目参与记录"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        status = request.args.get('status')
        
        query = '''
            SELECT pp.*, p.project_name, p.status as project_status
            FROM project_participations pp
            JOIN company_projects p ON pp.project_id = p.id
            WHERE pp.user_id = ?
        '''
        params = [user_id]
        
        if status:
            query += ' AND pp.status = ?'
            params.append(status)
        
        query += ' ORDER BY pp.created_at DESC'
        
        participations = conn.execute(query, params).fetchall()
        
        participation_list = []
        for p in participations:
            participation_list.append({
                'id': p['id'],
                'projectId': p['project_id'],
                'projectName': p['project_name'],
                'projectStatus': p['project_status'],
                'participationType': p['participation_type'],
                'roleName': p['role_name'],
                'status': p['status'],
                'contributionDescription': p['contribution_description'],
                'contributionShare': p['contribution_share'],
                'resourceIds': json.loads(p['resource_ids']) if p['resource_ids'] else [],
                'paymentStatus': p['payment_status'],
                'paymentAmount': p['payment_amount'],
                'paymentTime': p['payment_time'],
                'startDate': p['start_date'],
                'endDate': p['end_date'],
                'createdAt': p['created_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取参与记录成功',
            'data': participation_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/project-participations', methods=['POST'])
@require_auth
def apply_project_participation():
    """
    申请参与项目
    参数：projectId, participationType, contributionDescription, resourceIds
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        data = request.get_json()
        
        project_id = data.get('projectId')
        if not project_id:
            return jsonify({'success': False, 'message': '缺少项目ID'}), 400
        
        # 检查项目是否存在且状态为招募中
        project = conn.execute(
            'SELECT * FROM company_projects WHERE id = ? AND status IN ("recruiting", "active")',
            (project_id,)
        ).fetchone()
        
        if not project:
            return jsonify({'success': False, 'message': '项目不存在或不在招募期'}), 404
        
        # 检查是否已申请
        existing = conn.execute(
            'SELECT * FROM project_participations WHERE project_id = ? AND user_id = ? AND status != "terminated"',
            (project_id, user_id)
        ).fetchone()
        
        if existing:
            return jsonify({'success': False, 'message': '已申请或正在参与该项目'}), 400
        
        # 检查是否有参与费
        participation_fee = conn.execute(
            'SELECT participation_fee FROM company_projects WHERE id = ?',
            (project_id,)
        ).fetchone()
        
        fee_amount = participation_fee['participation_fee'] if participation_fee else 0
        
        # 创建参与申请
        cursor = conn.execute(
            '''INSERT INTO project_participations
            (project_id, user_id, participation_type, role_name, status, contribution_description,
             resource_ids, payment_status, payment_amount)
            VALUES (?, ?, ?, ?, 'applied', ?, ?, ?, ?)''',
            (
                project_id,
                user_id,
                data.get('participationType', 'resource_provider'),
                data.get('roleName'),
                data.get('contributionDescription'),
                json.dumps(data.get('resourceIds', [])),
                'paid' if fee_amount == 0 else 'unpaid',
                fee_amount
            )
        )
        
        participation_id = cursor.lastrowid
        
        # 记录工作流日志
        conn.execute(
            '''INSERT INTO project_workflow_logs
            (project_id, action_type, action_description, actor_id, actor_type)
            VALUES (?, 'user_joined', ?, ?, 'user')''',
            (project_id, f'用户 {user_id} 申请参与项目', user_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '申请成功',
            'data': {
                'participationId': participation_id,
                'paymentAmount': fee_amount,
                'needPayment': fee_amount > 0
            }
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/project-participations/<int:participation_id>/pay', methods=['POST'])
@require_auth
def pay_participation_fee(participation_id):
    """
    支付参与费
    参数：paymentMethod
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        data = request.get_json()
        
        # 检查参与记录是否属于当前用户
        participation = conn.execute(
            'SELECT * FROM project_participations WHERE id = ? AND user_id = ?',
            (participation_id, user_id)
        ).fetchone()
        
        if not participation:
            return jsonify({'success': False, 'message': '参与记录不存在'}), 404
        
        if participation['payment_status'] == 'paid':
            return jsonify({'success': False, 'message': '已支付'}), 400
        
        if participation['payment_amount'] == 0:
            return jsonify({'success': False, 'message': '无需支付'}), 400
        
        # 创建交易记录
        transaction_id = f'TXN{datetime.now().strftime("%Y%m%d%H%M%S")}{participation_id}'
        
        conn.execute(
            '''INSERT INTO project_transactions
            (project_id, transaction_type, amount, user_id, transaction_status, 
             payment_method, transaction_id, reference_id, description)
            VALUES (?, 'participation_fee', ?, ?, 'completed', ?, ?, ?, ?)''',
            (
                participation['project_id'],
                participation['payment_amount'],
                user_id,
                data.get('paymentMethod', 'unknown'),
                transaction_id,
                participation_id,
                '支付项目参与费'
            )
        )
        
        # 更新参与记录的支付状态
        conn.execute(
            '''UPDATE project_participations
            SET payment_status = 'paid',
                payment_time = ?,
                payment_method = ?,
                payment_transaction_id = ?,
                status = 'active'
            WHERE id = ?''',
            (datetime.now().isoformat(), data.get('paymentMethod'), transaction_id, participation_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '支付成功',
            'data': {
                'transactionId': transaction_id,
                'paymentAmount': participation['payment_amount']
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/project-participations/<int:participation_id>/approve', methods=['POST'])
@require_auth
def approve_participation(participation_id):
    """
    审批项目参与申请（管理员）
    参数：action (approve/reject)
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id  # 管理员ID
        data = request.get_json()
        
        action = data.get('action')
        if action not in ['approve', 'reject']:
            return jsonify({'success': False, 'message': '无效的操作'}), 400
        
        # 检查参与记录
        participation = conn.execute(
            'SELECT * FROM project_participations WHERE id = ?',
            (participation_id,)
        ).fetchone()
        
        if not participation:
            return jsonify({'success': False, 'message': '参与记录不存在'}), 404
        
        # 更新状态
        status = 'active' if action == 'approve' else 'rejected'
        conn.execute(
            '''UPDATE project_participations
            SET status = ?, approved_by = ?, approved_at = ?
            WHERE id = ?''',
            (status, user_id, datetime.now().isoformat(), participation_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'申请已{action == "approve" and "批准" or "拒绝"}'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 项目工作流 ====================

@private_resources_bp.route('/api/projects/<int:project_id>/milestones', methods=['GET'])
@require_auth
def get_project_milestones(project_id):
    """获取项目里程碑"""
    try:
        conn = get_db_connection()
        
        milestones = conn.execute(
            'SELECT * FROM project_milestones WHERE project_id = ? ORDER BY planned_date ASC',
            (project_id,)
        ).fetchall()
        
        milestone_list = []
        for m in milestones:
            milestone_list.append({
                'id': m['id'],
                'milestoneName': m['milestone_name'],
                'description': m['description'],
                'plannedDate': m['planned_date'],
                'actualDate': m['actual_date'],
                'status': m['status'],
                'progressPercentage': m['progress_percentage'],
                'responsiblePersonId': m['responsible_person_id']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取里程碑成功',
            'data': milestone_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/projects/<int:project_id>/tasks', methods=['GET'])
@require_auth
def get_project_tasks(project_id):
    """获取项目任务"""
    try:
        conn = get_db_connection()
        
        tasks = conn.execute(
            '''SELECT pt.*, u.username as assignee_name
            FROM project_tasks pt
            LEFT JOIN users u ON pt.assignee_id = u.id
            WHERE pt.project_id = ?
            ORDER BY pt.due_date ASC, pt.created_at ASC''',
            (project_id,)
        ).fetchall()
        
        task_list = []
        for t in tasks:
            task_list.append({
                'id': t['id'],
                'taskName': t['task_name'],
                'description': t['description'],
                'assigneeId': t['assignee_id'],
                'assigneeName': t['assignee_name'],
                'status': t['status'],
                'priority': t['priority'],
                'estimatedHours': t['estimated_hours'],
                'actualHours': t['actual_hours'],
                'startDate': t['start_date'],
                'dueDate': t['due_date'],
                'milestoneId': t['milestone_id']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取任务成功',
            'data': task_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/projects/<int:project_id>/tasks', methods=['POST'])
@require_auth
def create_project_task(project_id):
    """创建项目任务"""
    try:
        conn = get_db_connection()
        data = request.get_json()
        
        cursor = conn.execute(
            '''INSERT INTO project_tasks
            (project_id, milestone_id, task_name, description, assignee_id, status,
             priority, estimated_hours, due_date, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                project_id,
                data.get('milestoneId'),
                data.get('taskName'),
                data.get('description'),
                data.get('assigneeId'),
                data.get('status', 'pending'),
                data.get('priority', 'medium'),
                data.get('estimatedHours', 0),
                data.get('dueDate'),
                g.current_user_id
            )
        )
        
        task_id = cursor.lastrowid
        
        # 记录工作流日志
        conn.execute(
            '''INSERT INTO project_workflow_logs
            (project_id, action_type, action_description, actor_id, actor_type)
            VALUES (?, 'task_assigned', ?, ?, 'user')''',
            (project_id, f'创建任务: {data.get("taskName")}', g.current_user_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '任务创建成功',
            'data': {'id': task_id}
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/projects/<int:project_id>/tasks/<int:task_id>', methods=['PUT'])
@require_auth
def update_project_task(project_id, task_id):
    """更新项目任务"""
    try:
        conn = get_db_connection()
        data = request.get_json()
        
        # 构建更新SQL
        update_fields = []
        update_values = []
        
        field_mapping = {
            'taskName': 'task_name',
            'description': 'description',
            'assigneeId': 'assignee_id',
            'status': 'status',
            'priority': 'priority',
            'estimatedHours': 'estimated_hours',
            'actualHours': 'actual_hours',
            'dueDate': 'due_date'
        }
        
        for key, db_field in field_mapping.items():
            if key in data:
                update_fields.append(f'{db_field} = ?')
                update_values.append(data[key])
        
        if update_fields:
            update_values.extend([task_id, project_id])
            conn.execute(
                f'UPDATE project_tasks SET {", ".join(update_fields)} WHERE id = ? AND project_id = ?',
                update_values
            )
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '任务更新成功'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 分润管理 ====================

@private_resources_bp.route('/api/profit-sharing', methods=['GET'])
@require_auth
def get_profit_sharing():
    """获取当前用户的分润记录"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        sharing = conn.execute('''
            SELECT ps.*, p.project_name, pp.participation_type
            FROM profit_sharing ps
            JOIN company_projects p ON ps.project_id = p.id
            JOIN project_participations pp ON ps.participation_id = pp.id
            WHERE ps.user_id = ?
            ORDER BY ps.created_at DESC
        ''', (user_id,)).fetchall()
        
        sharing_list = []
        for s in sharing:
            sharing_list.append({
                'id': s['id'],
                'projectId': s['project_id'],
                'projectName': s['project_name'],
                'participationType': s['participation_type'],
                'totalProfit': s['total_profit'],
                'userShare': s['user_share'],
                'sharePercentage': s['share_percentage'],
                'status': s['status'],
                'settlementPeriod': s['settlement_period'],
                'distributedAt': s['distributed_at'],
                'createdAt': s['created_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取分润记录成功',
            'data': sharing_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/profit-sharing', methods=['POST'])
@require_auth
def create_profit_sharing():
    """
    创建分润记录（管理员或项目经理）
    参数：projectId, userId, participationId, totalProfit, sharePercentage, settlementPeriod
    """
    try:
        conn = get_db_connection()
        data = request.get_json()
        
        # 计算用户份额
        user_share = data.get('totalProfit', 0) * (data.get('sharePercentage', 0) / 100)
        
        cursor = conn.execute(
            '''INSERT INTO profit_sharing
            (project_id, user_id, participation_id, total_profit, user_share, share_percentage,
             settlement_period, status, sharing_rule)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'calculated', ?)''',
            (
                data.get('projectId'),
                data.get('userId'),
                data.get('participationId'),
                data.get('totalProfit'),
                user_share,
                data.get('sharePercentage'),
                data.get('settlementPeriod', 'upon_delivery'),
                data.get('sharingRule', f'按{data.get("sharePercentage")}%分润')
            )
        )
        
        sharing_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '分润记录创建成功',
            'data': {'id': sharing_id, 'userShare': user_share}
        }), 201
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/profit-sharing/<int:sharing_id>/distribute', methods=['POST'])
@require_auth
def distribute_profit(sharing_id):
    """
    发放分润（管理员）
    参数：distributionMethod
    """
    try:
        conn = get_db_connection()
        data = request.get_json()
        
        # 检查分润记录
        sharing = conn.execute(
            'SELECT * FROM profit_sharing WHERE id = ?',
            (sharing_id,)
        ).fetchone()
        
        if not sharing:
            return jsonify({'success': False, 'message': '分润记录不存在'}), 404
        
        if sharing['status'] == 'distributed':
            return jsonify({'success': False, 'message': '已发放'}), 400
        
        # 创建交易记录
        transaction_id = f'PRF{datetime.now().strftime("%Y%m%d%H%M%S")}{sharing_id}'
        
        conn.execute(
            '''INSERT INTO project_transactions
            (project_id, transaction_type, amount, user_id, transaction_status,
             payment_method, transaction_id, reference_id, description)
            VALUES (?, 'profit_distribution', ?, ?, 'completed', ?, ?, ?, ?)''',
            (
                sharing['project_id'],
                sharing['user_share'],
                sharing['user_id'],
                data.get('distributionMethod', 'bank_transfer'),
                transaction_id,
                sharing_id,
                '项目收益分润'
            )
        )
        
        # 更新分润状态
        conn.execute(
            '''UPDATE profit_sharing
            SET status = 'distributed',
                distribution_method = ?,
                distribution_time = ?,
                distribution_transaction_id = ?,
                verified_by = ?,
                verified_at = ?
            WHERE id = ?''',
            (data.get('distributionMethod'), datetime.now().isoformat(), 
             transaction_id, g.current_user_id, datetime.now().isoformat(), sharing_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '分润发放成功',
            'data': {'transactionId': transaction_id, 'amount': sharing['user_share']}
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 统计和推荐 ====================

@private_resources_bp.route('/api/dashboard/resource-stats', methods=['GET'])
@require_auth
def get_resource_stats():
    """获取用户资源统计"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 资源统计
        resource_stats = conn.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN authorization_status = 'authorized' THEN 1 ELSE 0 END) as authorized,
                SUM(CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END) as verified,
                SUM(CASE WHEN visibility = 'matchable' THEN 1 ELSE 0 END) as matchable
            FROM private_resources
            WHERE user_id = ? AND deleted_at IS NULL
        ''', (user_id,)).fetchone()
        
        # 匹配统计
        match_stats = conn.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM resource_matches rm
            JOIN private_resources pr ON rm.resource_id = pr.id
            WHERE pr.user_id = ?
        ''', (user_id,)).fetchone()
        
        # 项目参与统计
        participation_stats = conn.execute('''
            SELECT
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(payment_amount) as total_invested
            FROM project_participations
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        # 分润统计
        profit_stats = conn.execute('''
            SELECT
                SUM(user_share) as total_profits,
                SUM(CASE WHEN status = 'distributed' THEN user_share ELSE 0 END) as distributed
            FROM profit_sharing
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取统计成功',
            'data': {
                'resources': {
                    'total': resource_stats['total'] or 0,
                    'authorized': resource_stats['authorized'] or 0,
                    'verified': resource_stats['verified'] or 0,
                    'matchable': resource_stats['matchable'] or 0
                },
                'matches': {
                    'total': match_stats['total'] or 0,
                    'approved': match_stats['approved'] or 0,
                    'pending': match_stats['pending'] or 0
                },
                'participations': {
                    'total': participation_stats['total'] or 0,
                    'active': participation_stats['active'] or 0,
                    'completed': participation_stats['completed'] or 0,
                    'totalInvested': participation_stats['total_invested'] or 0
                },
                'profits': {
                    'total': profit_stats['total_profits'] or 0,
                    'distributed': profit_stats['distributed'] or 0,
                    'pending': (profit_stats['total_profits'] or 0) - (profit_stats['distributed'] or 0)
                }
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@private_resources_bp.route('/api/projects/recommended', methods=['GET'])
@require_auth
def get_recommended_projects():
    """
    根据用户资源获取推荐项目
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 获取用户的可匹配资源
        resources = conn.execute('''
            SELECT * FROM private_resources
            WHERE user_id = ? 
              AND authorization_status = 'authorized'
              AND visibility = 'matchable'
              AND deleted_at IS NULL
              AND (valid_until IS NULL OR valid_until >= date('now'))
        ''', (user_id,)).fetchall()
        
        # 构建搜索关键词
        keywords = []
        for r in resources:
            if r['can_solve']:
                keywords.append(f'%{r["can_solve"]}%')
        
        if not keywords:
            # 如果没有匹配资源，返回所有招募中的项目
            projects = conn.execute('''
                SELECT p.*, COUNT(DISTINCT pp.id) as participant_count
                FROM company_projects p
                LEFT JOIN project_participations pp ON p.id = pp.project_id
                WHERE p.status = 'recruiting'
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT 10
            ''').fetchall()
        else:
            # 根据关键词搜索匹配的项目
            query = '''
                SELECT p.*, COUNT(DISTINCT pp.id) as participant_count,
                       0 as match_score
                FROM company_projects p
                LEFT JOIN project_participations pp ON p.id = pp.project_id
                WHERE p.status IN ('recruiting', 'active')
            '''
            params = []
            
            for keyword in keywords:
                query += ' AND (p.description LIKE ? OR p.project_name LIKE ?)'
                params.extend([keyword, keyword])
            
            query += '''
                GROUP BY p.id
                ORDER BY p.created_at DESC
                LIMIT 10
            '''
            
            projects = conn.execute(query, params).fetchall()
        
        project_list = []
        for p in projects:
            project_list.append({
                'id': p['id'],
                'projectName': p['project_name'],
                'description': p['description'],
                'status': p['status'],
                'budget': p['budget'],
                'startDate': p['start_date'],
                'endDate': p['end_date'],
                'participantCount': p['participant_count'],
                'participationFee': p.get('participation_fee', 0)
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取推荐项目成功',
            'data': project_list
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
