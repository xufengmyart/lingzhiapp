"""
微信开放平台 OAuth2.0 登录模块
用于网页端扫码登录
"""
from flask import Blueprint, request, jsonify, redirect, url_for, session
import urllib.parse
import hashlib
import random
import string
import requests
from config import config  # 注意：导入的是Config类的实例
import json

wechat_oauth_bp = Blueprint('wechat_oauth', __name__)

# 微信开放平台配置（延迟加载）
def _get_wechat_config():
    """获取微信开放平台配置"""
    appid = getattr(config, 'WECHAT_OPEN_PLATFORM_APPID', '')
    secret = getattr(config, 'WECHAT_OPEN_PLATFORM_APPSECRET', '')

    # 检查配置是否有效（不为空且不是占位符）
    is_valid = bool(
        appid and
        appid not in ['', 'your-open-platform-appid', 'your-wechat-app-id', 'your-appid']
    )

    return {
        'appid': appid if is_valid else '',
        'secret': secret if is_valid else '',
        'redirect_uri': "https://meiyueart.com/api/wechat/oauth/callback",
        'is_valid': is_valid
    }

def get_db_connection():
    """获取数据库连接"""
    import sqlite3
    conn = sqlite3.connect(config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_state(length=32):
    """生成随机state，用于防止CSRF攻击"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@wechat_oauth_bp.route('/wechat/oauth/authorize', methods=['GET'])
def wechat_oauth_authorize():
    """
    获取微信开放平台OAuth2.0授权URL
    用户访问此URL后，会显示微信扫码页面

    注意：
    - 此功能需要配置微信开放平台网站应用的 AppID 和 AppSecret
    - 配置文件中需要设置 WECHAT_OPEN_PLATFORM_APPID 和 WECHAT_OPEN_PLATFORM_APPSECRET
    - 应用类型必须是"网站应用"，不能是"移动应用"或"小程序"
    - 需要在微信开放平台授权回调域名：meiyueart.com
    """
    try:
        # 获取微信配置
        wechat_config = _get_wechat_config()

        # 检查微信配置是否有效
        if not wechat_config['is_valid']:
            return jsonify({
                'success': False,
                'error_code': 'WECHAT_NOT_CONFIGURED',
                'message': '微信开放平台未配置或配置无效',
                'data': {
                    'hint': '微信扫码登录功能暂时不可用，请使用手机号登录',
                    'reason': '系统未配置微信开放平台网站应用',
                    'alternative': '您可以使用手机号和密码登录',
                    'contact_admin': '如需使用微信扫码登录，请联系管理员配置微信开放平台'
                }
            }), 503  # Service Unavailable

        # 生成state，防止CSRF攻击
        state = generate_state()

        # 将state存入session（生产环境建议使用Redis）
        session['wechat_state'] = state

        # 构建授权URL
        # 文档: https://developers.weixin.qq.com/doc/oplatform/Website_App/WeChat_Login/Wechat_Login.html
        params = {
            'appid': wechat_config['appid'],
            'redirect_uri': wechat_config['redirect_uri'],
            'response_type': 'code',
            'scope': 'snsapi_login',
            'state': state
        }

        auth_url = f"https://open.weixin.qq.com/connect/qrconnect?{urllib.parse.urlencode(params)}#wechat_redirect"

        return jsonify({
            'success': True,
            'data': {
                'auth_url': auth_url,
                'state': state,
                'app_type': 'website'  # 标识这是网站应用登录
            }
        })

    except Exception as e:
        print(f"Error in wechat_oauth_authorize: {str(e)}")
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': f'服务器错误: {str(e)}'
        }), 500

@wechat_oauth_bp.route('/wechat/oauth/callback', methods=['GET'])
def wechat_oauth_callback():
    """
    微信OAuth2.0回调处理
    微信扫码后，会重定向到此接口，携带code和state
    """
    try:
        # 获取微信返回的参数
        code = request.args.get('code')
        state = request.args.get('state')

        print(f"微信回调: code={code}, state={state}")

        # 验证state，防止CSRF攻击
        if not state or state != session.get('wechat_state'):
            return jsonify({
                'success': False,
                'error_code': 'INVALID_STATE',
                'message': 'State验证失败，可能存在CSRF攻击'
            }), 400

        # 清除session中的state
        session.pop('wechat_state', None)

        if not code:
            return jsonify({
                'success': False,
                'error_code': 'NO_CODE',
                'message': '微信授权失败，未返回code'
            }), 400

        # 步骤1: 使用code换取access_token
        wechat_config = _get_wechat_config()
        token_url = "https://api.weixin.qq.com/sns/oauth2/access_token"
        params = {
            'appid': wechat_config['appid'],
            'secret': wechat_config['secret'],
            'code': code,
            'grant_type': 'authorization_code'
        }

        print(f"请求微信获取access_token: {token_url}")
        response = requests.get(token_url, params=params, timeout=10)
        result = response.json()

        print(f"微信响应: {result}")

        if 'errcode' in result:
            return jsonify({
                'success': False,
                'error_code': f'WECHAT_ERROR_{result.get("errcode")}',
                'message': f'微信授权失败: {result.get("errmsg")}'
            }), 400

        access_token = result.get('access_token')
        openid = result.get('openid')
        unionid = result.get('unionid')  # 只有绑定开放平台账号的公众号才有unionid

        if not access_token or not openid:
            return jsonify({
                'success': False,
                'error_code': 'INVALID_RESPONSE',
                'message': '微信返回数据无效'
            }), 400

        # 步骤2: 使用access_token获取用户信息
        userinfo_url = "https://api.weixin.qq.com/sns/userinfo"
        params = {
            'access_token': access_token,
            'openid': openid
        }

        print(f"请求微信获取用户信息")
        response = requests.get(userinfo_url, params=params, timeout=10)
        user_info = response.json()

        print(f"用户信息: {user_info}")

        if 'errcode' in user_info:
            # 微信开放平台可能不返回unionid，使用openid
            user_info = {
                'openid': openid,
                'nickname': f'微信用户{openid[:8]}',
                'headimgurl': 'https://thirdwx.qlogo.cn/mmopen/vi_32/POgEwh4mIHO4nibH0KlMECNjjGxQUq24ZEaGT4poC6icRiccVGKSyXwibcPq4BWmiaIGuG1icwxaQX6grC9VemZoJ8rg/132'
            }

        # 步骤3: 查询或创建用户
        conn = get_db_connection()
        try:
            # 查询用户是否存在
            user = conn.execute(
                'SELECT * FROM users WHERE wechat_openid = ?',
                (openid,)
            ).fetchone()

            if user:
                # 用户已存在，更新用户信息
                conn.execute(
                    '''UPDATE users SET
                       nickname = ?,
                       avatar = ?,
                       last_login_time = CURRENT_TIMESTAMP
                       WHERE id = ?''',
                    (
                        user_info.get('nickname', ''),
                        user_info.get('headimgurl', ''),
                        user['id']
                    )
                )
                conn.commit()
                user_id = user['id']
            else:
                # 新用户，创建账号并赠送100灵值
                user_id = conn.execute(
                    '''INSERT INTO users (username, wechat_openid, nickname, avatar, totalLingzhi, totalCredits, created_at)
                       VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''',
                    (
                        f'wx_{openid[:8]}',
                        openid,
                        user_info.get('nickname', ''),
                        user_info.get('headimgurl', ''),
                        100,  # 新用户赠送100灵值
                        0
                    )
                ).lastrowid
                conn.commit()
                print(f"✅ 新用户注册成功: {user_id}, 赠送100灵值")

            # 生成JWT token
            import jwt
            import datetime
            token_payload = {
                'user_id': user_id,
                'wechat_openid': openid,
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7)
            }
            token = jwt.encode(token_payload, config.JWT_SECRET_KEY, algorithm='HS256')

            # 重定向到前端页面，携带token
            # 注意：实际项目中应该使用安全的方式传递token
            frontend_url = f"https://meiyueart.com/login/callback?token={token}"
            return redirect(frontend_url)

        finally:
            conn.close()

    except Exception as e:
        print(f"Error in wechat_oauth_callback: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': f'服务器错误: {str(e)}'
        }), 500

@wechat_oauth_bp.route('/wechat/oauth/userinfo', methods=['GET'])
def wechat_oauth_userinfo():
    """
    通过token获取用户信息
    请求头: Authorization: Bearer <token>
    """
    try:
        # 从请求头获取token
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error_code': 'NO_TOKEN',
                'message': '未提供token'
            }), 401

        token = auth_header.split(' ')[1]

        # 验证token
        import jwt
        try:
            payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'error_code': 'TOKEN_EXPIRED',
                'message': 'Token已过期'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'error_code': 'INVALID_TOKEN',
                'message': 'Token无效'
            }), 401

        # 查询用户信息
        user_id = payload.get('user_id')
        conn = get_db_connection()
        try:
            user = conn.execute(
                'SELECT id, username, nickname, avatar, totalLingzhi, totalCredits, created_at FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()

            if not user:
                return jsonify({
                    'success': False,
                    'error_code': 'USER_NOT_FOUND',
                    'message': '用户不存在'
                }), 404

            return jsonify({
                'success': True,
                'data': dict(user)
            })

        finally:
            conn.close()

    except Exception as e:
        print(f"Error in wechat_oauth_userinfo: {str(e)}")
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': f'服务器错误: {str(e)}'
        }), 500


@wechat_oauth_bp.route('/wechat/oauth/config', methods=['GET'])
def wechat_oauth_config():
    """
    检查微信开放平台配置状态
    返回配置信息和可用的登录方式
    """
    try:
        wechat_config = _get_wechat_config()

        # 检查配置是否有效
        is_configured = bool(
            wechat_config['appid'] and
            wechat_config['appid'] not in ['', 'your-open-platform-appid']
        )

        # 提供配置信息
        config_info = {
            'is_configured': is_configured,
            'app_type': 'website' if is_configured else 'none',
            'appid': wechat_config['appid'][:8] + '***' if wechat_config['appid'] else '',
            'redirect_uri': wechat_config['redirect_uri']
        }

        # 如果未配置，提供帮助信息
        if not is_configured:
            config_info['setup_guide'] = {
                'step1': '登录微信开放平台 (https://open.weixin.qq.com/)',
                'step2': '创建"网站应用"，获取 AppID 和 AppSecret',
                'step3': '在应用详情中配置授权回调域名: meiyueart.com',
                'step4': '更新 .env 文件，配置 WECHAT_OPEN_PLATFORM_APPID 和 WECHAT_OPEN_PLATFORM_APPSECRET',
                'step5': '重启后端服务'
            }

        # 提供可用的登录方式
        available_login_methods = [
            {
                'type': 'phone',
                'name': '手机号登录',
                'url': '/api/login',
                'description': '使用手机号和密码登录'
            }
        ]

        if is_configured:
            available_login_methods.append({
                'type': 'wechat',
                'name': '微信扫码登录',
                'url': '/api/wechat/oauth/authorize',
                'description': '使用微信扫码登录'
            })

        return jsonify({
            'success': True,
            'data': {
                'config': config_info,
                'available_login_methods': available_login_methods
            }
        })

    except Exception as e:
        print(f"Error in wechat_oauth_config: {str(e)}")
        return jsonify({
            'success': False,
            'error_code': 'INTERNAL_ERROR',
            'message': f'服务器错误: {str(e)}'
        }), 500
