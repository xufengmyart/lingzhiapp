"""
微信小程序登录 API
实现小程序登录、用户信息更新等功能
"""

from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import requests
import jwt
import os
import sys
import hashlib
import random

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

wechat_bp = Blueprint('wechat', __name__, url_prefix='/api/wechat')

# 微信小程序配置
WECHAT_APPID = config.WECHAT_APP_ID
WECHAT_APPSECRET = config.WECHAT_APP_SECRET
WECHAT_REDIRECT_URI = config.WECHAT_REDIRECT_URI

def verify_token(token):
    """验证 JWT token"""
    try:
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

def get_db_connection():
    """获取数据库连接"""
    import sqlite3
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@wechat_bp.route('/login', methods=['GET'])
def wechat_auth_url():
    """
    获取微信登录授权URL
    查询参数: state (可选，用于防止CSRF攻击)
    响应: { success: true, data: { auth_url: string, state: string } }
    """
    try:
        # 如果未配置微信AppID，返回错误
        if not WECHAT_APPID or WECHAT_APPID == 'your-wechat-app-id':
            return jsonify({
                'success': False,
                'message': '微信登录未配置，请联系管理员'
            }), 400
        
        # 生成state用于验证回调
        import secrets
        state = secrets.token_hex(16)
        
        # 微信网页授权URL（扫码登录）
        # 使用开放平台网页授权（PC端扫码）
        auth_url = f"https://open.weixin.qq.com/connect/qrconnect?appid={WECHAT_APPID}&redirect_uri={WECHAT_REDIRECT_URI}&response_type=code&scope=snsapi_login&state={state}#wechat_redirect"
        
        return jsonify({
            'success': True,
            'data': {
                'auth_url': auth_url,
                'state': state
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'获取授权URL失败: {str(e)}'
        }), 500

@wechat_bp.route('/login', methods=['POST'])
def wechat_login():
    """
    微信小程序登录
    请求体: { code: string, userInfo?: object }
    响应: { success: true, data: { token, user } }
    """
    try:
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({
                'success': False,
                'error': '缺少 code 参数'
            }), 400
        
        # 1. 使用 code 换取 openid 和 session_key
        url = 'https://api.weixin.qq.com/sns/jscode2session'
        params = {
            'appid': WECHAT_APPID,
            'secret': WECHAT_APPSECRET,
            'js_code': code,
            'grant_type': 'authorization_code'
        }
        
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'errcode' in result:
            return jsonify({
                'success': False,
                'error': f"微信登录失败: {result.get('errmsg', '未知错误')}"
            }), 400
        
        openid = result.get('openid')
        session_key = result.get('session_key')
        unionid = result.get('unionid')  # 如果有 unionid
        
        # 2. 查询或创建用户
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询用户
        cursor.execute(
            'SELECT * FROM users WHERE wechat_openid = ?',
            (openid,)
        )
        user = cursor.fetchone()
        
        # 更新 session_key
        cursor.execute(
            'UPDATE users SET wechat_session_key = ?, updated_at = ? WHERE wechat_openid = ?',
            (session_key, datetime.now(), openid)
        )
        
        if not user:
            # 创建新用户
            username = f'wx_{openid[:8]}'
            password_hash = os.urandom(32).hex()  # 随机密码，不会使用
            
            cursor.execute(
                '''INSERT INTO users (username, password_hash, status, wechat_openid, wechat_session_key, wechat_unionid, created_at, updated_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (username, password_hash, 'active', openid, session_key, unionid, datetime.now(), datetime.now())
            )
            user_id = cursor.lastrowid
            
            # 设置初始灵值（100）
            cursor.execute(
                'UPDATE users SET total_lingzhi = 100 WHERE id = ?',
                (user_id,)
            )
            
            # 记录灵值消费记录
            cursor.execute(
                """
                INSERT INTO lingzhi_consumption_records (user_id, consumption_type, consumption_item, lingzhi_amount, description)
                VALUES (?, 'new_user_bonus', 'wechat_register_bonus', 100, '新用户微信注册赠送')
                """,
                (user_id,)
            )
            
            # 获取新创建的用户
            cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
        
        # 3. 如果有用户信息，更新用户资料
        if data.get('userInfo'):
            user_info = data.get('userInfo')
            nickname = user_info.get('nickName', '')
            avatar = user_info.get('avatarUrl', '')
            gender = user_info.get('gender', 0)  # 0:未知, 1:男, 2:女
            city = user_info.get('city', '')
            province = user_info.get('province', '')
            country = user_info.get('country', '')
            
            cursor.execute(
                '''UPDATE users SET nickname = ?, avatar_url = ?, gender = ?, 
                   city = ?, province = ?, country = ?, updated_at = ?
                   WHERE id = ?''',
                (nickname, avatar, gender, city, province, country, datetime.now(), user['id'])
            )
        
        conn.commit()
        
        # 4. 生成 JWT token
        token_payload = {
            'user_id': user['id'],
            'username': user['username'],
            'wechat_openid': openid,
            'login_type': 'wechat',
            'exp': datetime.now() + timedelta(seconds=config.JWT_EXPIRATION)
        }
        
        token = jwt.encode(token_payload, config.JWT_SECRET_KEY, algorithm='HS256')
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'nickname': user.get('nickname', ''),
                    'avatar_url': user.get('avatar_url', ''),
                    'total_lingzhi': user.get('total_lingzhi', 0),
                    'status': user.get('status', 'active')
                }
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'登录失败: {str(e)}'
        }), 500

@wechat_bp.route('/update-profile', methods=['POST'])
def update_profile():
    """
    更新用户资料
    请求头: Authorization: Bearer {token}
    请求体: { userInfo: object }
    响应: { success: true }
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': '未授权'
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'token 无效'
            }), 401
        
        user_id = payload.get('user_id')
        data = request.get_json()
        user_info = data.get('userInfo', {})
        
        # 更新用户资料
        conn = get_db_connection()
        cursor = conn.cursor()
        
        nickname = user_info.get('nickName', '')
        avatar = user_info.get('avatarUrl', '')
        gender = user_info.get('gender', 0)
        city = user_info.get('city', '')
        province = user_info.get('province', '')
        country = user_info.get('country', '')
        
        cursor.execute(
            '''UPDATE users SET nickname = ?, avatar_url = ?, gender = ?, 
               city = ?, province = ?, country = ?, updated_at = ?
               WHERE id = ?''',
            (nickname, avatar, gender, city, province, country, datetime.now(), user_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '资料更新成功'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'更新失败: {str(e)}'
        }), 500

@wechat_bp.route('/phone-number', methods=['POST'])
def get_phone_number():
    """
    获取手机号（需要云开发或微信支付）
    请求头: Authorization: Bearer {token}
    请求体: { code: string }
    响应: { success: true, data: { phoneNumber: string } }
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': '未授权'
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'token 无效'
            }), 401
        
        user_id = payload.get('user_id')
        data = request.get_json()
        code = data.get('code')
        
        if not code:
            return jsonify({
                'success': False,
                'error': '缺少 code 参数'
            }), 400
        
        # 使用 code 换取手机号（需要 access_token）
        # 这里需要先获取 access_token
        # 注意：实际使用时需要缓存 access_token
        url = 'https://api.weixin.qq.com/cgi-bin/token'
        params = {
            'grant_type': 'client_credential',
            'appid': WECHAT_APPID,
            'secret': WECHAT_APPSECRET
        }
        
        response = requests.get(url, params=params)
        result = response.json()
        
        if 'errcode' in result:
            return jsonify({
                'success': False,
                'error': f"获取 access_token 失败: {result.get('errmsg', '未知错误')}"
            }), 400
        
        access_token = result.get('access_token')
        
        # 使用 access_token 和 code 获取手机号
        phone_url = f'https://api.weixin.qq.com/wxa/business/getuserphonenumber?access_token={access_token}'
        phone_data = {
            'code': code
        }
        
        phone_response = requests.post(phone_url, json=phone_data)
        phone_result = phone_response.json()
        
        if phone_result.get('errcode', 0) != 0:
            return jsonify({
                'success': False,
                'error': f"获取手机号失败: {phone_result.get('errmsg', '未知错误')}"
            }), 400
        
        phone_info = phone_result.get('phone_info', {})
        phone_number = phone_info.get('phoneNumber', '')
        pure_phone_number = phone_info.get('purePhoneNumber', '')
        country_code = phone_info.get('countryCode', '')
        
        # 更新用户手机号
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'UPDATE users SET phone = ?, updated_at = ? WHERE id = ?',
            (phone_number, datetime.now(), user_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'phoneNumber': phone_number,
                'purePhoneNumber': pure_phone_number,
                'countryCode': country_code
            }
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'获取手机号失败: {str(e)}'
        }), 500

@wechat_bp.route('/bind-phone', methods=['POST'])
def bind_phone():
    """
    手动绑定手机号
    请求头: Authorization: Bearer {token}
    请求体: { phone: string, verify_code: string }
    响应: { success: true }
    """
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': '未授权'
            }), 401
        
        token = auth_header.replace('Bearer ', '')
        payload = verify_token(token)
        
        if not payload:
            return jsonify({
                'success': False,
                'error': 'token 无效'
            }), 401
        
        user_id = payload.get('user_id')
        data = request.get_json()
        phone = data.get('phone')
        verify_code = data.get('verify_code')
        
        if not phone or not verify_code:
            return jsonify({
                'success': False,
                'error': '缺少必要参数'
            }), 400
        
        # 验证验证码（这里需要实现验证码逻辑）
        # TODO: 实现短信验证码验证
        
        # 检查手机号是否已被绑定
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT id FROM users WHERE phone = ? AND id != ?',
            (phone, user_id)
        )
        existing_user = cursor.fetchone()
        
        if existing_user:
            conn.close()
            return jsonify({
                'success': False,
                'error': '该手机号已被其他用户绑定'
            }), 400
        
        # 绑定手机号
        cursor.execute(
            'UPDATE users SET phone = ?, updated_at = ? WHERE id = ?',
            (phone, datetime.now(), user_id)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '手机号绑定成功'
        })
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': f'绑定失败: {str(e)}'
        }), 500
