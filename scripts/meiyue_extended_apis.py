#!/usr/bin/env python3
"""
媄月商业艺术系统 API 端点（补充版本）
补充 SYSTEM_UPGRADE_PLAN.md 中定义但未实现的 API 端点
"""

from flask import request, jsonify
from functools import wraps
import sqlite3
import json
import jwt
import os

# 导入 app.py 中的工具函数
DATABASE = 'lingzhi_ecosystem.db'

# JWT 配置（与 app.py 保持一致）
JWT_SECRET = os.getenv('JWT_SECRET', 'lingzhi-jwt-secret-key')

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def verify_token(token):
    """验证JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权，请先登录', 'error_code': 'UNAUTHORIZED'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效', 'error_code': 'INVALID_TOKEN'}), 401

        return f(user_id, *args, **kwargs)
    return decorated_function

def register_meiyue_extended_apis(app):
    """注册媄月系统补充 API"""

    # ==================== 圣地管理 API（补充） ====================

    @app.route('/api/sacred-sites/<int:site_id>', methods=['GET'])
    @login_required
    def get_sacred_site_detail(user_id, site_id):
        """获取圣地详情"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM sacred_sites WHERE id = ?
            ''', (site_id,))

            site = cursor.fetchone()
            conn.close()

            if not site:
                return jsonify({'success': False, 'message': '圣地不存在', 'error_code': 'SITE_NOT_FOUND'}), 404

            return jsonify({
                'success': True,
                'data': {
                    'id': site['id'],
                    'name': site['name'],
                    'description': site['description'],
                    'cultural_theme': site['cultural_theme'],
                    'location': site['location'],
                    'latitude': site['latitude'],
                    'longitude': site['longitude'],
                    'status': site['status'],
                    'image_url': site['image_url'],
                    'total_investment': site['total_investment'],
                    'expected_returns': site['expected_returns'],
                    'current_value': site['current_value'],
                    'creator_id': site['creator_id'],
                    'created_at': site['created_at'],
                    'updated_at': site['updated_at']
                }
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取圣地详情失败: {str(e)}', 'error_code': 'GET_SACRED_SITE_ERROR'}), 500

    @app.route('/api/sacred-sites/<int:site_id>', methods=['PUT'])
    @login_required
    def update_sacred_site(user_id, site_id):
        """更新圣地信息"""
        try:
            data = request.get_json()

            conn = get_db()
            cursor = conn.cursor()

            # 检查圣地是否存在
            cursor.execute('SELECT * FROM sacred_sites WHERE id = ?', (site_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '圣地不存在', 'error_code': 'SITE_NOT_FOUND'}), 404

            # 更新圣地
            update_fields = []
            update_values = []

            allowed_fields = [
                'name', 'description', 'cultural_theme', 'location',
                'latitude', 'longitude', 'status', 'image_url',
                'total_investment', 'expected_returns', 'current_value'
            ]

            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    update_values.append(data[field])

            if update_fields:
                update_values.append(site_id)
                cursor.execute(f'''
                    UPDATE sacred_sites
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', update_values)

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '圣地更新成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'更新圣地失败: {str(e)}', 'error_code': 'UPDATE_SACRED_SITE_ERROR'}), 500

    @app.route('/api/sacred-sites/<int:site_id>', methods=['DELETE'])
    @login_required
    def delete_sacred_site(user_id, site_id):
        """删除圣地"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 检查圣地是否存在
            cursor.execute('SELECT * FROM sacred_sites WHERE id = ?', (site_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '圣地不存在', 'error_code': 'SITE_NOT_FOUND'}), 404

            # 删除圣地
            cursor.execute('DELETE FROM sacred_sites WHERE id = ?', (site_id,))
            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '圣地删除成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'删除圣地失败: {str(e)}', 'error_code': 'DELETE_SACRED_SITE_ERROR'}), 500

    @app.route('/api/sacred-sites/<int:site_id>/resources', methods=['GET'])
    @login_required
    def get_sacred_site_resources(user_id, site_id):
        """获取圣地资源"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM sacred_site_resources
                WHERE site_id = ?
                ORDER BY created_at DESC
            ''', (site_id,))

            resources = cursor.fetchall()
            conn.close()

            result = []
            for resource in resources:
                result.append({
                    'id': resource['id'],
                    'site_id': resource['site_id'],
                    'resource_type': resource['resource_type'],
                    'name': resource['name'],
                    'description': resource['description'],
                    'value': resource['value'],
                    'status': resource['status'],
                    'created_at': resource['created_at']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取圣地资源失败: {str(e)}', 'error_code': 'GET_SACRED_SITE_RESOURCES_ERROR'}), 500

    # ==================== 文化项目管理 API（补充） ====================

    @app.route('/api/cultural-projects/<int:project_id>', methods=['GET'])
    @login_required
    def get_cultural_project_detail(user_id, project_id):
        """获取项目详情"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM cultural_projects WHERE id = ?
            ''', (project_id,))

            project = cursor.fetchone()
            conn.close()

            if not project:
                return jsonify({'success': False, 'message': '项目不存在', 'error_code': 'PROJECT_NOT_FOUND'}), 404

            return jsonify({
                'success': True,
                'data': {
                    'id': project['id'],
                    'name': project['name'],
                    'description': project['description'],
                    'site_id': project['site_id'],
                    'project_type': project['project_type'],
                    'status': project['status'],
                    'progress': project['progress'],
                    'budget': project['budget'],
                    'actual_cost': project['actual_cost'],
                    'start_date': project['start_date'],
                    'end_date': project['end_date'],
                    'manager_id': project['manager_id'],
                    'created_at': project['created_at'],
                    'updated_at': project['updated_at']
                }
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取项目详情失败: {str(e)}', 'error_code': 'GET_PROJECT_ERROR'}), 500

    @app.route('/api/cultural-projects/<int:project_id>', methods=['PUT'])
    @login_required
    def update_cultural_project(user_id, project_id):
        """更新项目"""
        try:
            data = request.get_json()

            conn = get_db()
            cursor = conn.cursor()

            # 检查项目是否存在
            cursor.execute('SELECT * FROM cultural_projects WHERE id = ?', (project_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '项目不存在', 'error_code': 'PROJECT_NOT_FOUND'}), 404

            # 更新项目
            update_fields = []
            update_values = []

            allowed_fields = [
                'name', 'description', 'site_id', 'project_type',
                'status', 'progress', 'budget', 'actual_cost',
                'start_date', 'end_date', 'manager_id'
            ]

            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    update_values.append(data[field])

            if update_fields:
                update_values.append(project_id)
                cursor.execute(f'''
                    UPDATE cultural_projects
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', update_values)

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '项目更新成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'更新项目失败: {str(e)}', 'error_code': 'UPDATE_PROJECT_ERROR'}), 500

    @app.route('/api/cultural-projects/<int:project_id>/participants', methods=['POST'])
    @login_required
    def add_project_participant(user_id, project_id):
        """添加项目参与者"""
        try:
            data = request.get_json()

            required_fields = ['user_id', 'role']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'message': f'缺少必填字段: {field}', 'error_code': 'MISSING_FIELD'}), 400

            conn = get_db()
            cursor = conn.cursor()

            # 检查项目是否存在
            cursor.execute('SELECT * FROM cultural_projects WHERE id = ?', (project_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '项目不存在', 'error_code': 'PROJECT_NOT_FOUND'}), 404

            # 添加参与者
            cursor.execute('''
                INSERT INTO project_participants
                (project_id, user_id, role, contribution, reward)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                project_id,
                data['user_id'],
                data['role'],
                data.get('contribution', ''),
                data.get('reward', 0)
            ))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '参与者添加成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'添加参与者失败: {str(e)}', 'error_code': 'ADD_PARTICIPANT_ERROR'}), 500

    # ==================== 用户修行记录 API（补充） ====================

    @app.route('/api/user/journey-stages', methods=['GET'])
    @login_required
    def get_user_journey_stages(user_id):
        """获取修行阶段"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM user_journey_stages
                WHERE user_id = ?
                ORDER BY stage_level ASC
            ''', (user_id,))

            stages = cursor.fetchall()
            conn.close()

            result = []
            for stage in stages:
                result.append({
                    'id': stage['id'],
                    'stage_name': stage['stage_name'],
                    'stage_level': stage['stage_level'],
                    'description': stage['description'],
                    'requirements': stage['requirements'],
                    'progress': stage['progress'],
                    'is_completed': stage['is_completed'],
                    'completed_at': stage['completed_at'],
                    'created_at': stage['created_at'],
                    'updated_at': stage['updated_at']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取修行阶段失败: {str(e)}', 'error_code': 'GET_JOURNEY_STAGES_ERROR'}), 500

    @app.route('/api/user/journey-stages', methods=['POST'])
    @login_required
    def update_user_journey_stage(user_id):
        """更新修行阶段"""
        try:
            data = request.get_json()

            required_fields = ['stage_name', 'stage_level']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'message': f'缺少必填字段: {field}', 'error_code': 'MISSING_FIELD'}), 400

            conn = get_db()
            cursor = conn.cursor()

            # 检查是否已存在该阶段
            cursor.execute('''
                SELECT * FROM user_journey_stages
                WHERE user_id = ? AND stage_name = ?
            ''', (user_id, data['stage_name']))

            existing_stage = cursor.fetchone()

            if existing_stage:
                # 更新
                update_fields = []
                update_values = []

                allowed_fields = ['description', 'requirements', 'progress', 'is_completed']
                for field in allowed_fields:
                    if field in data:
                        update_fields.append(f"{field} = ?")
                        update_values.append(data[field])

                if update_fields:
                    update_values.extend([user_id, data['stage_name']])
                    cursor.execute(f'''
                        UPDATE user_journey_stages
                        SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND stage_name = ?
                    ''', update_values)

                # 如果完成，设置完成时间
                if data.get('is_completed') and not existing_stage['is_completed']:
                    cursor.execute('''
                        UPDATE user_journey_stages
                        SET completed_at = CURRENT_TIMESTAMP
                        WHERE user_id = ? AND stage_name = ?
                    ''', (user_id, data['stage_name']))
            else:
                # 插入新阶段
                cursor.execute('''
                    INSERT INTO user_journey_stages
                    (user_id, stage_name, stage_level, description, requirements, progress, is_completed)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    user_id,
                    data['stage_name'],
                    data['stage_level'],
                    data.get('description', ''),
                    data.get('requirements', ''),
                    data.get('progress', 0),
                    data.get('is_completed', 0)
                ))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '修行阶段更新成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'更新修行阶段失败: {str(e)}', 'error_code': 'UPDATE_JOURNEY_STAGE_ERROR'}), 500

    # ==================== 用户贡献 API（补充） ====================

    @app.route('/api/user/contributions/<int:contribution_id>/review', methods=['PUT'])
    @login_required
    def review_user_contribution(user_id, contribution_id):
        """审核贡献"""
        try:
            data = request.get_json()

            required_fields = ['status', 'review_comment']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'message': f'缺少必填字段: {field}', 'error_code': 'MISSING_FIELD'}), 400

            if data['status'] not in ['approved', 'rejected']:
                return jsonify({'success': False, 'message': '状态无效', 'error_code': 'INVALID_STATUS'}), 400

            conn = get_db()
            cursor = conn.cursor()

            # 检查贡献是否存在
            cursor.execute('SELECT * FROM user_contributions WHERE id = ?', (contribution_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '贡献不存在', 'error_code': 'CONTRIBUTION_NOT_FOUND'}), 404

            # 更新审核状态
            cursor.execute('''
                UPDATE user_contributions
                SET status = ?, review_comment = ?, reviewer_id = ?, reviewed_at = CURRENT_TIMESTAMP, reward = ?
                WHERE id = ?
            ''', (
                data['status'],
                data['review_comment'],
                user_id,
                data.get('reward', 0) if data['status'] == 'approved' else 0,
                contribution_id
            ))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '审核成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'审核失败: {str(e)}', 'error_code': 'REVIEW_CONTRIBUTION_ERROR'}), 500

    # ==================== 通证管理 API（补充） ====================

    @app.route('/api/tokens/transfer', methods=['POST'])
    @login_required
    def transfer_tokens(user_id):
        """转让通证"""
        try:
            data = request.get_json()

            required_fields = ['to_user_id', 'token_type_id', 'amount']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'message': f'缺少必填字段: {field}', 'error_code': 'MISSING_FIELD'}), 400

            if data['to_user_id'] == user_id:
                return jsonify({'success': False, 'message': '不能转让给自己', 'error_code': 'INVALID_RECIPIENT'}), 400

            conn = get_db()
            cursor = conn.cursor()

            # 检查转出用户余额
            cursor.execute('''
                SELECT balance FROM user_token_balances
                WHERE user_id = ? AND token_type_id = ?
            ''', (user_id, data['token_type_id']))

            from_balance = cursor.fetchone()
            if not from_balance or from_balance['balance'] < data['amount']:
                conn.close()
                return jsonify({'success': False, 'message': '余额不足', 'error_code': 'INSUFFICIENT_BALANCE'}), 400

            # 检查通证类型是否可转让
            cursor.execute('''
                SELECT is_transferrable FROM token_types
                WHERE id = ?
            ''', (data['token_type_id'],))

            token_type = cursor.fetchone()
            if not token_type or not token_type['is_transferrable']:
                conn.close()
                return jsonify({'success': False, 'message': '该通证不可转让', 'error_code': 'TOKEN_NOT_TRANSFERRABLE'}), 400

            # 执行转让
            cursor.execute('''
                UPDATE user_token_balances
                SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP
                WHERE user_id = ? AND token_type_id = ?
            ''', (data['amount'], user_id, data['token_type_id']))

            cursor.execute('''
                INSERT INTO user_token_balances (user_id, token_type_id, balance)
                VALUES (?, ?, ?)
                ON CONFLICT(user_id, token_type_id) DO UPDATE SET
                balance = balance + ?, updated_at = CURRENT_TIMESTAMP
            ''', (data['to_user_id'], data['token_type_id'], data['amount'], data['amount']))

            # 记录交易
            cursor.execute('''
                INSERT INTO token_transactions
                (from_user_id, to_user_id, token_type_id, amount, transaction_type, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data['to_user_id'],
                data['token_type_id'],
                data['amount'],
                'transfer',
                data.get('description', '用户转账')
            ))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '转让成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'转让失败: {str(e)}', 'error_code': 'TRANSFER_ERROR'}), 500

    @app.route('/api/tokens/transactions', methods=['GET'])
    @login_required
    def get_token_transactions(user_id):
        """获取交易记录"""
        try:
            page = request.args.get('page', 1, type=int)
            limit = request.args.get('limit', 20, type=int)
            offset = (page - 1) * limit

            conn = get_db()
            cursor = conn.cursor()

            # 获取用户相关的交易
            cursor.execute('''
                SELECT * FROM token_transactions
                WHERE from_user_id = ? OR to_user_id = ?
                ORDER BY created_at DESC
                LIMIT ? OFFSET ?
            ''', (user_id, user_id, limit, offset))

            transactions = cursor.fetchall()

            # 获取总数
            cursor.execute('''
                SELECT COUNT(*) as total FROM token_transactions
                WHERE from_user_id = ? OR to_user_id = ?
            ''', (user_id, user_id))

            total = cursor.fetchone()['total']
            conn.close()

            result = []
            for transaction in transactions:
                result.append({
                    'id': transaction['id'],
                    'from_user_id': transaction['from_user_id'],
                    'to_user_id': transaction['to_user_id'],
                    'token_type_id': transaction['token_type_id'],
                    'amount': transaction['amount'],
                    'transaction_type': transaction['transaction_type'],
                    'related_id': transaction['related_id'],
                    'description': transaction['description'],
                    'created_at': transaction['created_at']
                })

            return jsonify({
                'success': True,
                'data': {
                    'transactions': result,
                    'total': total,
                    'page': page,
                    'limit': limit,
                    'pages': (total + limit - 1) // limit
                }
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取交易记录失败: {str(e)}', 'error_code': 'GET_TRANSACTIONS_ERROR'}), 500

    # ==================== SBT 管理 API（补充） ====================

    @app.route('/api/sbts/issue', methods=['POST'])
    @login_required
    def issue_sbt(user_id):
        """颁发 SBT"""
        try:
            data = request.get_json()

            required_fields = ['user_id', 'sbt_type_id', 'issued_reason']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'message': f'缺少必填字段: {field}', 'error_code': 'MISSING_FIELD'}), 400

            conn = get_db()
            cursor = conn.cursor()

            # 检查 SBT 类型是否存在
            cursor.execute('SELECT * FROM sbt_types WHERE id = ?', (data['sbt_type_id'],))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': 'SBT 类型不存在', 'error_code': 'SBT_TYPE_NOT_FOUND'}), 404

            # 颁发 SBT
            cursor.execute('''
                INSERT INTO user_sbts (user_id, sbt_type_id, metadata, issued_by, issued_reason)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(user_id, sbt_type_id) DO UPDATE SET
                metadata = ?, issued_by = ?, issued_reason = ?
            ''', (
                data['user_id'],
                data['sbt_type_id'],
                json.dumps(data.get('metadata', {})),
                user_id,
                data['issued_reason'],
                json.dumps(data.get('metadata', {})),
                user_id,
                data['issued_reason']
            ))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': 'SBT 颁发成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'颁发 SBT 失败: {str(e)}', 'error_code': 'ISSUE_SBT_ERROR'}), 500

    # ==================== 社群活动 API（补充） ====================

    @app.route('/api/activities/<int:activity_id>/register', methods=['POST'])
    @login_required
    def register_activity(user_id, activity_id):
        """报名活动"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 检查活动是否存在
            cursor.execute('SELECT * FROM community_activities WHERE id = ?', (activity_id,))
            activity = cursor.fetchone()

            if not activity:
                conn.close()
                return jsonify({'success': False, 'message': '活动不存在', 'error_code': 'ACTIVITY_NOT_FOUND'}), 404

            # 检查是否已报名
            cursor.execute('''
                SELECT * FROM activity_participants
                WHERE activity_id = ? AND user_id = ?
            ''', (activity_id, user_id))

            if cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '已报名该活动', 'error_code': 'ALREADY_REGISTERED'}), 400

            # 检查人数限制
            if activity['max_participants'] and activity['current_participants'] >= activity['max_participants']:
                conn.close()
                return jsonify({'success': False, 'message': '活动名额已满', 'error_code': 'ACTIVITY_FULL'}), 400

            # 报名
            cursor.execute('''
                INSERT INTO activity_participants (activity_id, user_id)
                VALUES (?, ?)
            ''', (activity_id, user_id))

            # 更新参与人数
            cursor.execute('''
                UPDATE community_activities
                SET current_participants = current_participants + 1
                WHERE id = ?
            ''', (activity_id,))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '报名成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'报名失败: {str(e)}', 'error_code': 'REGISTER_ACTIVITY_ERROR'}), 500

    @app.route('/api/activities/<int:activity_id>/check-in', methods=['PUT'])
    @login_required
    def check_in_activity(user_id, activity_id):
        """签到活动"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 检查活动是否存在
            cursor.execute('SELECT * FROM community_activities WHERE id = ?', (activity_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '活动不存在', 'error_code': 'ACTIVITY_NOT_FOUND'}), 404

            # 检查是否已报名
            cursor.execute('''
                SELECT * FROM activity_participants
                WHERE activity_id = ? AND user_id = ?
            ''', (activity_id, user_id))

            participant = cursor.fetchone()
            if not participant:
                conn.close()
                return jsonify({'success': False, 'message': '未报名该活动', 'error_code': 'NOT_REGISTERED'}), 400

            # 更新签到状态
            cursor.execute('''
                UPDATE activity_participants
                SET status = 'checked_in', check_in_time = CURRENT_TIMESTAMP
                WHERE activity_id = ? AND user_id = ?
            ''', (activity_id, user_id))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '签到成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'签到失败: {str(e)}', 'error_code': 'CHECK_IN_ERROR'}), 500

    # ==================== 公司动态 API（新增） ====================

    @app.route('/api/company-news', methods=['POST'])
    @login_required
    def create_company_news(user_id):
        """创建新闻"""
        try:
            data = request.get_json()

            required_fields = ['title', 'content']
            for field in required_fields:
                if field not in data:
                    return jsonify({'success': False, 'message': f'缺少必填字段: {field}', 'error_code': 'MISSING_FIELD'}), 400

            conn = get_db()
            cursor = conn.cursor()

            is_published = data.get('is_published', 0)
            published_at = None

            if is_published:
                published_at = datetime.now()

            cursor.execute('''
                INSERT INTO company_news
                (title, content, category, image_url, author_id, is_published, published_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                data['title'],
                data['content'],
                data.get('category', 'update'),
                data.get('image_url', ''),
                user_id,
                is_published,
                published_at
            ))

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '新闻创建成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'创建新闻失败: {str(e)}', 'error_code': 'CREATE_NEWS_ERROR'}), 500

    @app.route('/api/company-news/<int:news_id>', methods=['PUT'])
    @login_required
    def update_company_news(user_id, news_id):
        """更新新闻"""
        try:
            data = request.get_json()

            conn = get_db()
            cursor = conn.cursor()

            # 检查新闻是否存在
            cursor.execute('SELECT * FROM company_news WHERE id = ?', (news_id,))
            news = cursor.fetchone()

            if not news:
                conn.close()
                return jsonify({'success': False, 'message': '新闻不存在', 'error_code': 'NEWS_NOT_FOUND'}), 404

            # 更新新闻
            update_fields = []
            update_values = []

            allowed_fields = ['title', 'content', 'category', 'image_url', 'is_published']
            for field in allowed_fields:
                if field in data:
                    update_fields.append(f"{field} = ?")
                    update_values.append(data[field])

            if update_fields:
                update_values.append(news_id)

                # 如果首次发布，设置发布时间
                if data.get('is_published') and not news['is_published']:
                    update_fields.append('published_at = ?')
                    update_values.insert(len(update_values) - 1, datetime.now())

                cursor.execute(f'''
                    UPDATE company_news
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', update_values)

            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '新闻更新成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'更新新闻失败: {str(e)}', 'error_code': 'UPDATE_NEWS_ERROR'}), 500

    @app.route('/api/company-news/<int:news_id>', methods=['DELETE'])
    @login_required
    def delete_company_news(user_id, news_id):
        """删除新闻"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            # 检查新闻是否存在
            cursor.execute('SELECT * FROM company_news WHERE id = ?', (news_id,))
            if not cursor.fetchone():
                conn.close()
                return jsonify({'success': False, 'message': '新闻不存在', 'error_code': 'NEWS_NOT_FOUND'}), 404

            # 删除新闻
            cursor.execute('DELETE FROM company_news WHERE id = ?', (news_id,))
            conn.commit()
            conn.close()

            return jsonify({'success': True, 'message': '新闻删除成功'})

        except Exception as e:
            return jsonify({'success': False, 'message': f'删除新闻失败: {str(e)}', 'error_code': 'DELETE_NEWS_ERROR'}), 500

    print("✅ 媄月商业艺术系统补充API已注册")
