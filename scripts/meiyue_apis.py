#!/usr/bin/env python3
"""
媄月商业艺术系统 API 端点
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

def register_meiyue_apis(app):
    """注册所有媄月系统API"""

    # ==================== 圣地管理 API ====================

    @app.route('/api/sacred-sites', methods=['GET'])
    @login_required
    def get_sacred_sites(user_id):
        """获取圣地列表"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM sacred_sites
                ORDER BY created_at DESC
            ''')

            sites = cursor.fetchall()
            conn.close()

            result = []
            for site in sites:
                result.append({
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
                    'created_at': site['created_at']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取圣地列表失败: {str(e)}', 'error_code': 'GET_SACRED_SITES_ERROR'}), 500

    @app.route('/api/sacred-sites', methods=['POST'])
    @login_required
    def create_sacred_site(user_id):
        """创建圣地"""
        try:
            data = request.get_json()

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO sacred_sites (name, description, cultural_theme, location, latitude, longitude, status, image_url, total_investment, expected_returns, creator_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name'),
                data.get('description', ''),
                data.get('cultural_theme', ''),
                data.get('location', ''),
                data.get('latitude'),
                data.get('longitude'),
                data.get('status', 'planning'),
                data.get('image_url', ''),
                data.get('total_investment', 0),
                data.get('expected_returns', 0),
                user_id
            ))

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': '圣地创建成功',
                'data': {'id': cursor.lastrowid}
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'创建圣地失败: {str(e)}', 'error_code': 'CREATE_SACRED_SITE_ERROR'}), 500

    # ==================== 文化项目管理 API ====================

    @app.route('/api/cultural-projects', methods=['GET'])
    @login_required
    def get_cultural_projects(user_id):
        """获取文化项目列表"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM cultural_projects
                ORDER BY created_at DESC
            ''')

            projects = cursor.fetchall()
            conn.close()

            result = []
            for project in projects:
                result.append({
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
                    'created_at': project['created_at']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取项目列表失败: {str(e)}', 'error_code': 'GET_PROJECTS_ERROR'}), 500

    @app.route('/api/cultural-projects', methods=['POST'])
    @login_required
    def create_cultural_project(user_id):
        """创建文化项目"""
        try:
            data = request.get_json()

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO cultural_projects (name, description, site_id, project_type, status, progress, budget, actual_cost, start_date, end_date, manager_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('name'),
                data.get('description', ''),
                data.get('site_id'),
                data.get('project_type'),
                data.get('status', 'planning'),
                data.get('progress', 0),
                data.get('budget', 0),
                data.get('actual_cost', 0),
                data.get('start_date'),
                data.get('end_date'),
                user_id
            ))

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': '项目创建成功',
                'data': {'id': cursor.lastrowid}
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'创建项目失败: {str(e)}', 'error_code': 'CREATE_PROJECT_ERROR'}), 500

    # ==================== 用户修行记录 API ====================

    @app.route('/api/user/learning-records', methods=['GET'])
    @login_required
    def get_learning_records(user_id):
        """获取用户学习记录"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM user_learning_records
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            ''', (user_id,))

            records = cursor.fetchall()
            conn.close()

            result = []
            for record in records:
                result.append({
                    'id': record['id'],
                    'knowledge_title': record['knowledge_title'],
                    'learning_type': record['learning_type'],
                    'duration': record['duration'],
                    'notes': record['notes'],
                    'realization': record['realization'],
                    'reward': record['reward'],
                    'created_at': record['created_at']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取学习记录失败: {str(e)}', 'error_code': 'GET_LEARNING_RECORDS_ERROR'}), 500

    @app.route('/api/user/learning-records', methods=['POST'])
    @login_required
    def create_learning_record(user_id):
        """创建学习记录"""
        try:
            data = request.get_json()

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO user_learning_records (user_id, knowledge_id, knowledge_title, learning_type, duration, notes, realization, reward)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                data.get('knowledge_id'),
                data.get('knowledge_title'),
                data.get('learning_type'),
                data.get('duration', 0),
                data.get('notes', ''),
                data.get('realization', ''),
                data.get('reward', 0)
            ))

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': '学习记录创建成功',
                'data': {'id': cursor.lastrowid}
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'创建学习记录失败: {str(e)}', 'error_code': 'CREATE_LEARNING_RECORD_ERROR'}), 500

    # ==================== 用户贡献 API ====================

    @app.route('/api/user/contributions', methods=['GET'])
    @login_required
    def get_contributions(user_id):
        """获取用户贡献记录"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM user_contributions
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 50
            ''', (user_id,))

            contributions = cursor.fetchall()
            conn.close()

            result = []
            for contribution in contributions:
                result.append({
                    'id': contribution['id'],
                    'project_id': contribution['project_id'],
                    'contribution_type': contribution['contribution_type'],
                    'description': contribution['description'],
                    'status': contribution['status'],
                    'review_comment': contribution['review_comment'],
                    'reward': contribution['reward'],
                    'created_at': contribution['created_at']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取贡献记录失败: {str(e)}', 'error_code': 'GET_CONTRIBUTIONS_ERROR'}), 500

    @app.route('/api/user/contributions', methods=['POST'])
    @login_required
    def create_contribution(user_id):
        """提交贡献"""
        try:
            data = request.get_json()

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO user_contributions (user_id, project_id, contribution_type, description, attachments, status)
                VALUES (?, ?, ?, ?, ?, 'pending')
            ''', (
                user_id,
                data.get('project_id'),
                data.get('contribution_type'),
                data.get('description'),
                json.dumps(data.get('attachments', []))
            ))

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': '贡献提交成功',
                'data': {'id': cursor.lastrowid}
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'提交贡献失败: {str(e)}', 'error_code': 'CREATE_CONTRIBUTION_ERROR'}), 500

    # ==================== 通证管理 API ====================

    @app.route('/api/tokens', methods=['GET'])
    @login_required
    def get_tokens(user_id):
        """获取通证类型列表"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM token_types')

            tokens = cursor.fetchall()
            conn.close()

            result = []
            for token in tokens:
                result.append({
                    'id': token['id'],
                    'name': token['name'],
                    'symbol': token['symbol'],
                    'description': token['description'],
                    'token_type': token['token_type'],
                    'total_supply': token['total_supply'],
                    'circulated_supply': token['circulated_supply'],
                    'unit_price': token['unit_price'],
                    'is_transferrable': token['is_transferrable']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取通证列表失败: {str(e)}', 'error_code': 'GET_TOKENS_ERROR'}), 500

    @app.route('/api/user/tokens', methods=['GET'])
    @login_required
    def get_user_tokens(user_id):
        """获取用户通证余额"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT utb.*, tt.name, tt.symbol, tt.token_type
                FROM user_token_balances utb
                JOIN token_types tt ON utb.token_type_id = tt.id
                WHERE utb.user_id = ?
            ''', (user_id,))

            balances = cursor.fetchall()
            conn.close()

            result = []
            for balance in balances:
                result.append({
                    'token_name': balance['name'],
                    'token_symbol': balance['symbol'],
                    'token_type': balance['token_type'],
                    'balance': balance['balance'],
                    'frozen_balance': balance['frozen_balance']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取通证余额失败: {str(e)}', 'error_code': 'GET_USER_TOKENS_ERROR'}), 500

    # ==================== SBT 管理 API ====================

    @app.route('/api/sbts', methods=['GET'])
    @login_required
    def get_sbts(user_id):
        """获取SBT类型列表"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('SELECT * FROM sbt_types')

            sbts = cursor.fetchall()
            conn.close()

            result = []
            for sbt in sbts:
                result.append({
                    'id': sbt['id'],
                    'name': sbt['name'],
                    'description': sbt['description'],
                    'category': sbt['category'],
                    'rarity': sbt['rarity'],
                    'image_url': sbt['image_url']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取SBT列表失败: {str(e)}', 'error_code': 'GET_SBTS_ERROR'}), 500

    @app.route('/api/user/sbts', methods=['GET'])
    @login_required
    def get_user_sbts(user_id):
        """获取用户SBT"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT us.*, st.name, st.description, st.category, st.rarity, st.image_url
                FROM user_sbts us
                JOIN sbt_types st ON us.sbt_type_id = st.id
                WHERE us.user_id = ?
            ''', (user_id,))

            sbts = cursor.fetchall()
            conn.close()

            result = []
            for sbt in sbts:
                result.append({
                    'id': sbt['id'],
                    'name': sbt['name'],
                    'description': sbt['description'],
                    'category': sbt['category'],
                    'rarity': sbt['rarity'],
                    'image_url': sbt['image_url'],
                    'metadata': json.loads(sbt['metadata']) if sbt['metadata'] else {},
                    'issued_at': sbt['created_at']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取用户SBT失败: {str(e)}', 'error_code': 'GET_USER_SBTS_ERROR'}), 500

    # ==================== 社群活动 API ====================

    @app.route('/api/activities', methods=['GET'])
    @login_required
    def get_activities(user_id):
        """获取活动列表"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM community_activities
                WHERE status IN ('upcoming', 'ongoing')
                ORDER BY start_time ASC
            ''')

            activities = cursor.fetchall()
            conn.close()

            result = []
            for activity in activities:
                result.append({
                    'id': activity['id'],
                    'title': activity['title'],
                    'description': activity['description'],
                    'activity_type': activity['activity_type'],
                    'location': activity['location'],
                    'start_time': activity['start_time'],
                    'end_time': activity['end_time'],
                    'max_participants': activity['max_participants'],
                    'current_participants': activity['current_participants'],
                    'status': activity['status']
                })

            return jsonify({'success': True, 'data': result})

        except Exception as e:
            return jsonify({'success': False, 'message': f'获取活动列表失败: {str(e)}', 'error_code': 'GET_ACTIVITIES_ERROR'}), 500

    @app.route('/api/activities', methods=['POST'])
    @login_required
    def create_activity(user_id):
        """创建活动"""
        try:
            data = request.get_json()

            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO community_activities (title, description, activity_type, location, start_time, end_time, max_participants, organizer_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                data.get('title'),
                data.get('description', ''),
                data.get('activity_type'),
                data.get('location', ''),
                data.get('start_time'),
                data.get('end_time'),
                data.get('max_participants'),
                user_id
            ))

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': '活动创建成功',
                'data': {'id': cursor.lastrowid}
            })

        except Exception as e:
            return jsonify({'success': False, 'message': f'创建活动失败: {str(e)}', 'error_code': 'CREATE_ACTIVITY_ERROR'}), 500

    print("✅ 媄月系统API注册成功！")
