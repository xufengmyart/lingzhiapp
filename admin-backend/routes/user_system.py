"""
用户系统 API 蓝图
提供用户信息、资源、资产、旅程、学习记录等功能
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

user_bp = Blueprint('user', __name__, url_prefix='/api/user')

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


# ==================== 用户信息管理 ====================

@user_bp.route('/info', methods=['GET'])
def get_user_info():
    """
    获取用户信息
    响应: { success: true, data: { user: {...} } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 获取用户基本信息（包含扩展信息）
        user = conn.execute(
            'SELECT id, username, email, phone, avatar_url, created_at, bio, location, website FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404

        # 获取用户完善信息（user_profiles表用于存储真实姓名、身份证等）
        user_profile = conn.execute(
            'SELECT * FROM user_profiles WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        # 获取用户会员等级（member_levels表暂未实现，返回None）
        member_level = None

        # 获取用户灵值余额（从 users 表）
        user_balance = conn.execute(
            'SELECT total_lingzhi FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        # 获取用户推荐人信息
        print(f"[DEBUG] user_id: {user_id}, 获取推荐人信息...")
        referral_info = conn.execute(
            '''
            SELECT
                rr.referrer_id,
                u.username as referrer_username,
                u.avatar_url as referrer_avatar
            FROM referral_relationships rr
            LEFT JOIN users u ON rr.referrer_id = u.id
            WHERE rr.referee_id = ?
            LIMIT 1
            ''',
            (user_id,)
        ).fetchone()
        print(f"[DEBUG] referral_info: {referral_info}")

        conn.close()

        user_dict = dict(user)
        user_data = {
            'id': user_dict['id'],
            'username': user_dict['username'],
            'email': user_dict['email'],
            'phone': user_dict.get('phone', ''),
            'avatarUrl': user_dict.get('avatar_url', ''),
            'createdAt': user_dict['created_at']
        }

        # 添加扩展信息（从users表获取）
        user_data.update({
            'bio': user_dict.get('bio', ''),
            'location': user_dict.get('location', ''),
            'website': user_dict.get('website', ''),
            'interests': json.loads(user_dict.get('interests', '[]')) if user_dict.get('interests') else []
        })

        # 添加完善信息（从user_profiles表获取）
        if user_profile:
            profile_dict = dict(user_profile)
            user_data.update({
                'realName': profile_dict.get('real_name', ''),
                'idCard': profile_dict.get('id_card', ''),
                'bankName': profile_dict.get('bank_name', ''),
                'bankAccount': profile_dict.get('bank_account', ''),
                'isCompleted': profile_dict.get('is_completed', False)
            })

        # 添加推荐人信息
        if referral_info:
            referral_dict = dict(referral_info)
            user_data['referrer'] = {
                'id': referral_dict.get('referrer_id'),
                'username': referral_dict.get('referrer_username', ''),
                'avatarUrl': referral_dict.get('referrer_avatar', '')
            }
        else:
            user_data['referrer'] = None

        # 添加会员信息
        if member_level:
            member_level_dict = dict(member_level)
            user_data['memberLevel'] = {
                'id': member_level_dict.get('id'),
                'name': member_level_dict.get('name'),
                'level': member_level_dict.get('level_order'),
                'benefits': json.loads(member_level_dict.get('benefits', '[]')) if member_level_dict.get('benefits') else [],
                'levelSince': member_level_dict.get('level_since'),
                'status': member_level_dict.get('status')
            }

        # 添加灵值余额
        if user_balance:
            balance_dict = dict(user_balance)
            user_data['balance'] = balance_dict.get('total_lingzhi', 0)
            user_data['total_lingzhi'] = balance_dict.get('total_lingzhi', 0)
        else:
            user_data['balance'] = 0
            user_data['total_lingzhi'] = 0

        return jsonify({
            'success': True,
            'data': {
                'user': user_data
            }
        })

    except Exception as e:
        print(f"获取用户信息错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 用户资料更新 ====================

@user_bp.route('/profile', methods=['PUT'])
def update_user_profile():
    """
    更新用户资料（普通用户接口）
    支持字段级更新，仅允许用户更新自己的资料
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')
        data = request.get_json()

        if not data:
            return jsonify({
                'success': False,
                'error': '请求数据不能为空'
            }), 400

        conn = get_db_connection()

        # 检查用户是否存在
        user = conn.execute(
            'SELECT id FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'error': '用户不存在'
            }), 404

        # 定义可编辑字段（仅普通字段，不包含管理员专用字段）
        editable_fields = {
            'email': str,
            'phone': str,
            'real_name': str,
            'avatar_url': str,
            'bio': str,
            'location': str,
            'website': str,
            'title': str,
            'position': str,
            'gender': str,
        }

        # 定义user_profiles表的可编辑字段
        profile_fields = {
            'id_card': str,
            'bank_account': str,
            'bank_name': str,
        }

        # camelCase 到 snake_case 的映射
        field_mapping = {
            'avatarUrl': 'avatar_url',
            'realName': 'real_name',
            'wechatNickname': 'wechat_nickname',
            'wechatAvatar': 'wechat_avatar',
            'fullName': 'real_name',
            # 新增：user_profiles字段的映射
            'idCard': 'id_card',
            'bankAccount': 'bank_account',
            'bankName': 'bank_name',
        }

        # 转换字段名
        normalized_data = {}
        profile_data = {}

        for key, value in data.items():
            # 首先尝试从映射中查找
            normalized_key = field_mapping.get(key, key)

            # 检查是否属于users表字段
            if normalized_key in editable_fields:
                normalized_data[normalized_key] = value
            # 检查是否属于user_profiles表字段
            elif normalized_key in profile_fields:
                profile_data[normalized_key] = value
            # 如果是camelCase但不在映射中，尝试转换为snake_case
            elif key not in editable_fields:
                # 简单的camelCase转snake_case
                import re
                snake_key = re.sub('([A-Z])', r'_\1', key).lower()
                if snake_key in editable_fields:
                    normalized_data[snake_key] = value
                elif snake_key in profile_fields:
                    profile_data[snake_key] = value

        if not normalized_data and not profile_data:
            conn.close()
            return jsonify({
                'success': False,
                'error': '没有可更新的字段'
            }), 400

        # 构建 SQL 更新语句
        set_clauses = []
        params = []

        for field, value in normalized_data.items():
            if value is not None:  # 只更新非空字段
                set_clauses.append(f"{field} = ?")
                params.append(value)

        # 如果有users表字段需要更新
        if set_clauses:
            params.append(user_id)
            update_sql = f"""
                UPDATE users
                SET {', '.join(set_clauses)}
                WHERE id = ?
            """
            conn.execute(update_sql, params)

        # 更新user_profiles表
        profile_result = None
        if profile_data:
            # 检查是否已存在profile记录
            existing_profile = conn.execute(
                'SELECT * FROM user_profiles WHERE user_id = ?',
                (user_id,)
            ).fetchone()

            profile_set_clauses = []
            profile_params = []

            for field, value in profile_data.items():
                if value is not None:
                    profile_set_clauses.append(f"{field} = ?")
                    profile_params.append(value)

            if existing_profile and profile_set_clauses:
                # 更新现有记录
                profile_params.append(user_id)
                profile_update_sql = f"""
                    UPDATE user_profiles
                    SET {', '.join(profile_set_clauses)}, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = ?
                """
                conn.execute(profile_update_sql, profile_params)
            elif profile_set_clauses:
                # 创建新记录
                all_profile_fields = ['user_id'] + list(profile_data.keys())
                all_profile_values = [user_id] + [profile_data[field] for field in profile_data.keys()]

                profile_insert_sql = f"""
                    INSERT INTO user_profiles ({', '.join(all_profile_fields)})
                    VALUES ({', '.join(['?'] * len(all_profile_fields))})
                """
                conn.execute(profile_insert_sql, all_profile_values)

        conn.commit()

        # 获取更新后的用户信息
        updated_user = conn.execute(
            'SELECT * FROM users WHERE id = ?',
            (user_id,)
        ).fetchone()

        # 获取profile信息
        profile_info = conn.execute(
            'SELECT id_card, bank_account, bank_name FROM user_profiles WHERE user_id = ?',
            (user_id,)
        ).fetchone()

        conn.close()

        user_dict = dict(updated_user)
        profile_dict = dict(profile_info) if profile_info else {}

        # 转换为前端期望的格式
        response_user = {
            'id': user_dict['id'],
            'username': user_dict['username'],
            'email': user_dict.get('email', ''),
            'phone': user_dict.get('phone', ''),
            'avatarUrl': user_dict.get('avatar_url', ''),
            'realName': user_dict.get('real_name', ''),
            'bio': user_dict.get('bio', ''),
            'location': user_dict.get('location', ''),
            'website': user_dict.get('website', ''),
            'title': user_dict.get('title', ''),
            'position': user_dict.get('position', ''),
            'gender': user_dict.get('gender', ''),
            'totalLingzhi': user_dict.get('total_lingzhi', 0),
            # 添加profile字段
            'idCard': profile_dict.get('id_card', ''),
            'bankAccount': profile_dict.get('bank_account', ''),
            'bankName': profile_dict.get('bank_name', ''),
        }

        return jsonify({
            'success': True,
            'data': response_user
        }), 200

    except Exception as e:
        print(f"更新用户资料错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 用户资源管理 ====================

@user_bp.route('/resources', methods=['GET'])
def get_user_resources():
    """
    获取用户资源
    响应: { success: true, data: { resources: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 获取用户的资源（根据实际表结构）
        resources = conn.execute('''
            SELECT *
            FROM user_resources
            WHERE user_id = ?
            ORDER BY created_at DESC
        ''', (user_id,)).fetchall()

        conn.close()

        resource_list = []
        for res in resources:
            # 将 Row 对象转换为字典
            res_dict = dict(res)
            resource_list.append({
                'id': res_dict['id'],
                'name': res_dict['resource_name'],
                'type': res_dict.get('resource_type', 'general'),
                'description': res_dict.get('description', ''),
                'icon': res_dict.get('icon', ''),
                'status': res_dict['status'],
                'availability': res_dict.get('availability'),
                'estimatedValue': res_dict.get('estimated_value'),
                'tags': res_dict.get('tags'),
                'createdAt': res_dict['created_at'],
                'updatedAt': res_dict['updated_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'resources': resource_list
            }
        })

    except Exception as e:
        print(f"获取用户资源错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 用户资产管理 ====================

@user_bp.route('/assets', methods=['GET'])
def get_user_assets():
    """
    获取用户资产
    响应: { success: true, data: { assets: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 获取用户的数字资产
        digital_assets = conn.execute('''
            SELECT da.*, balance
            FROM digital_assets da
            LEFT JOIN user_balances ub ON da.id = ub.asset_id AND ub.user_id = ?
            WHERE da.is_active = 1
            ORDER BY da.created_at
        ''', (user_id,)).fetchall()

        # 获取用户的 SBT
        sbts = conn.execute('''
            SELECT st.*, usbt.minted_at, usbt.metadata
            FROM sbt_templates st
            LEFT JOIN user_sbt usbt ON st.id = usbt.template_id AND usbt.user_id = ?
            WHERE st.is_active = 1
        ''', (user_id,)).fetchall()

        conn.close()

        asset_list = []
        for asset in digital_assets:
            asset_list.append({
                'id': asset['id'],
                'name': asset['name'],
                'symbol': asset.get('symbol', ''),
                'balance': asset['balance'] or 0,
                'type': asset.get('type', 'token'),
                'icon': asset.get('icon', '')
            })

        sbt_list = []
        for sbt in sbts:
            sbt_list.append({
                'id': sbt['id'],
                'name': sbt['name'],
                'description': sbt.get('description', ''),
                'image': sbt.get('image', ''),
                'mintedAt': sbt.get('minted_at'),
                'metadata': json.loads(sbt['metadata']) if sbt.get('metadata') else {}
            })

        return jsonify({
            'success': True,
            'data': {
                'tokens': asset_list,
                'sbts': sbt_list
            }
        })

    except Exception as e:
        print(f"获取用户资产错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/tokens', methods=['GET'])
def get_user_tokens():
    """
    获取用户通证（兼容旧版）
    响应: { success: true, data: { tokens: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 获取用户的通证
        tokens = conn.execute('''
            SELECT dt.*, balance
            FROM digital_tokens dt
            LEFT JOIN user_token_balances utb ON dt.id = utb.token_id AND utb.user_id = ?
            WHERE dt.is_active = 1
            ORDER BY dt.created_at
        ''', (user_id,)).fetchall()

        conn.close()

        token_list = []
        for tok in tokens:
            token_list.append({
                'id': tok['id'],
                'name': tok['name'],
                'symbol': tok.get('symbol', ''),
                'balance': tok['balance'] or 0,
                'icon': tok.get('icon', '')
            })

        return jsonify({
            'success': True,
            'data': {
                'tokens': token_list
            }
        })

    except Exception as e:
        print(f"获取用户通证错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/sbts', methods=['GET'])
def get_user_sbts():
    """
    获取用户 SBT（兼容旧版）
    响应: { success: true, data: { sbts: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 获取用户的 SBT
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
                'description': sbt.get('description', ''),
                'image': sbt.get('image', ''),
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
        print(f"获取用户 SBT 错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 用户旅程管理 ====================

@user_bp.route('/journey', methods=['GET'])
def get_user_journey():
    """
    获取用户旅程
    响应: { success: true, data: { journey: {...} } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 获取用户的当前旅程阶段
        current_stage = conn.execute('''
            SELECT ujs.*, js.name, js.description, js.level, js.privileges
            FROM user_journey_stages ujs
            JOIN user_journey_stages js ON ujs.stage_id = js.id
            WHERE ujs.user_id = ?
            ORDER BY ujs.achieved_at DESC
            LIMIT 1
        ''', (user_id,)).fetchone()

        # 获取所有旅程阶段
        all_stages = conn.execute('''
            SELECT * FROM user_journey_stages
            ORDER BY level
        ''').fetchall()

        conn.close()

        journey = {
            'currentStage': None,
            'progress': 0,
            'totalStages': len(all_stages)
        }

        if current_stage:
            journey['currentStage'] = {
                'id': current_stage['id'],
                'name': current_stage['name'],
                'description': current_stage.get('description', ''),
                'level': current_stage['level'],
                'achievedAt': current_stage['achieved_at'],
                'privileges': json.loads(current_stage['privileges']) if current_stage.get('privileges') else []
            }
            journey['progress'] = (current_stage['level'] / len(all_stages)) * 100

        return jsonify({
            'success': True,
            'data': {
                'journey': journey
            }
        })

    except Exception as e:
        print(f"获取用户旅程错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/journey/upgrade', methods=['POST'])
def upgrade_journey():
    """
    升级用户旅程
    请求体: { stageId }
    响应: { success: true, data: { journey: {...} } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')
        data = request.get_json()
        stage_id = data.get('stageId')

        if not stage_id:
            return jsonify({
                'success': False,
                'error': '阶段 ID 不能为空'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否已经达到该阶段
        existing = conn.execute(
            'SELECT * FROM user_journey_stages WHERE user_id = ? AND stage_id = ?',
            (user_id, stage_id)
        ).fetchone()

        if existing:
            conn.close()
            return jsonify({
                'success': False,
                'error': '已达到该阶段'
            }), 400

        # 获取阶段信息
        stage = conn.execute(
            'SELECT * FROM user_journey_stages WHERE id = ?',
            (stage_id,)
        ).fetchone()

        if not stage:
            conn.close()
            return jsonify({
                'success': False,
                'error': '阶段不存在'
            }), 404

        # 记录达到新阶段
        cursor.execute('''
            INSERT INTO user_journey_stages (user_id, stage_id, achieved_at)
            VALUES (?, ?, ?)
        ''', (user_id, stage_id, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        # 返回更新后的旅程信息
        return get_user_journey()

    except Exception as e:
        print(f"升级旅程错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 用户学习记录 ====================

@user_bp.route('/learning-records', methods=['GET'])
def get_learning_records():
    """
    获取用户学习记录
    响应: { success: true, data: { records: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 获取用户的学习记录（这里使用 user_journey_stages 作为学习记录）
        records = conn.execute('''
            SELECT ujs.*, js.name, js.description
            FROM user_journey_stages ujs
            JOIN user_journey_stages js ON ujs.stage_id = js.id
            WHERE ujs.user_id = ?
            ORDER BY ujs.achieved_at DESC
            LIMIT 20
        ''', (user_id,)).fetchall()

        conn.close()

        record_list = []
        for record in records:
            record_list.append({
                'id': record['id'],
                'stageName': record['name'],
                'description': record.get('description', ''),
                'achievedAt': record['achieved_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'records': record_list
            }
        })

    except Exception as e:
        print(f"获取学习记录错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@user_bp.route('/journey-stages', methods=['GET'])
def get_journey_stages():
    """
    获取旅程阶段列表
    响应: { success: true, data: { stages: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        conn = get_db_connection()

        # 获取所有旅程阶段
        stages = conn.execute('''
            SELECT * FROM user_journey_stages
            ORDER BY level
        ''').fetchall()

        conn.close()

        stage_list = []
        for stage in stages:
            stage_list.append({
                'id': stage['id'],
                'name': stage['name'],
                'description': stage.get('description', ''),
                'level': stage['level'],
                'privileges': json.loads(stage['privileges']) if stage.get('privileges') else []
            })

        return jsonify({
            'success': True,
            'data': {
                'stages': stage_list
            }
        })

    except Exception as e:
        print(f"获取旅程阶段错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 设备管理 ====================

@user_bp.route('/devices', methods=['GET'])
def get_devices():
    """
    获取用户设备列表
    响应: { success: true, data: { devices: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token)

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '未登录或 token 无效'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        devices = conn.execute(
            'SELECT * FROM user_devices WHERE user_id = ? ORDER BY last_seen DESC',
            (user_id,)
        ).fetchall()

        conn.close()

        device_list = []
        for device in devices:
            device_list.append({
                'id': device['id'],
                'deviceName': device.get('device_name', '未知设备'),
                'deviceType': device.get('device_type', 'web'),
                'browser': device.get('browser', ''),
                'os': device.get('os', ''),
                'ip': device.get('ip', ''),
                'lastSeen': device['last_seen'],
                'isCurrent': device.get('is_current', False)
            })

        return jsonify({
            'success': True,
            'data': {
                'devices': device_list
            }
        })

    except Exception as e:
        print(f"获取设备列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


print("✅ 用户系统 API 蓝图已加载")
