"""
认证系统路由蓝图
包含用户注册、登录、验证码、密码重置等功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
import random
import string
import bcrypt
import jwt
from werkzeug.security import check_password_hash, generate_password_hash
from datetime import datetime, timedelta
import os

auth_bp = Blueprint('auth', __name__)

# 导入配置
from config import config
# 导入数据库管理器
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_manager import get_db_context

# 优先使用测试数据库（如果设置了环境变量）
DATABASE = os.getenv('TEST_DATABASE_PATH', config.DATABASE_PATH)
JWT_SECRET = config.JWT_SECRET_KEY
JWT_EXPIRATION = config.JWT_EXPIRATION

# 验证码存储（模拟短信验证码）
verification_codes = {}

# 辅助函数
def get_db():
    """获取数据库连接（已弃用，建议使用get_db_context）"""
    from db_manager import get_db
    return get_db()

def verify_password(password, hashed):
    """验证密码 - 支持bcrypt和scrypt格式"""
    try:
        # 如果哈希已经是 bytes，转换为字符串
        if isinstance(hashed, bytes):
            hashed_str = hashed.decode('utf-8')
        else:
            hashed_str = str(hashed)
        
        # 检查是否是scrypt格式
        if hashed_str.startswith('scrypt:'):
            return check_password_hash(hashed_str, password)
        
        # 检查是否是bcrypt格式
        if hashed_str.startswith('$2b$') or hashed_str.startswith('$2a$'):
            password_bytes = password.encode('utf-8')
            hashed_bytes = hashed_str.encode('utf-8')
            return bcrypt.checkpw(password_bytes, hashed_bytes)
        
        # 其他格式，尝试用check_password_hash
        return check_password_hash(hashed_str, password)
    except Exception as e:
        # 如果验证失败，返回 False
        return False

def hash_password(password):
    """哈希密码 - 使用scrypt格式"""
    return generate_password_hash(password, method='scrypt')

def generate_jwt_token(user_id, username):
    """生成JWT令牌"""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        'iat': datetime.utcnow()
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm='HS256')
    return token

def generate_code(length=6):
    """生成验证码"""
    return ''.join(random.choices(string.digits, k=length))

# ============ 用户注册 ============

@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        # 使用 force=True 忽略 Content-Type 检查，避免415错误
        data = request.get_json(force=True, silent=True)
        
        if not data:
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
            
        username = data.get('username')
        password = data.get('password')
        phone = data.get('phone')
        email = data.get('email')
        verification_code = data.get('verification_code')
        referral = data.get('referral')  # 推荐码

        # 基本验证
        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        if phone:
            # 验证手机验证码
            if not verification_code:
                return jsonify({
                    'success': False,
                    'message': '验证码不能为空'
                }), 400

            code_data = verification_codes.get(phone)
            if not code_data:
                return jsonify({
                    'success': False,
                    'message': '验证码无效或已过期'
                }), 400

            if code_data['code'] != verification_code:
                return jsonify({
                    'success': False,
                    'message': '验证码错误'
                }), 400

            if datetime.now().timestamp() > code_data['expire_at']:
                del verification_codes[phone]
                return jsonify({
                    'success': False,
                    'message': '验证码已过期'
                }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400

        # 检查手机号是否已存在
        if phone:
            cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
            if cursor.fetchone():
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '手机号已被注册'
                }), 400

        # 创建用户
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, phone, email, total_lingzhi, status)
            VALUES (?, ?, ?, ?, 100, 'active')
            """,
            (username, hash_password(password), phone, email)
        )
        user_id = cursor.lastrowid
        
        # 处理推荐关系绑定
        referrer_id = None
        if referral:
            # 通过推荐码查找推荐人
            cursor.execute("SELECT id FROM users WHERE referral_code = ?", (referral,))
            referrer = cursor.fetchone()
            if referrer:
                referrer_id = referrer['id']
                cursor.execute(
                    "UPDATE users SET referrer_id = ? WHERE id = ?",
                    (referrer_id, user_id)
                )
                print(f"✅ 用户 {username} 已绑定推荐人 ID: {referrer_id}")
        
        # 记录灵值消费记录
        cursor.execute(
            """
            INSERT INTO lingzhi_consumption_records (user_id, consumption_type, consumption_item, lingzhi_amount, description)
            VALUES (?, 'register', 'new_user_bonus', 100, '新用户注册赠送')
            """,
            (user_id,)
        )
        
        conn.commit()
        conn.close()

        # 清除验证码
        if phone:
            del verification_codes[phone]

        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {'user_id': user_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}'
        }), 500

# ============ 用户登录 ============

@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        # 使用 force=True 忽略 Content-Type 检查，避免415错误
        # 添加 debug 日志
        print(f"[LOGIN] Request received")
        print(f"[LOGIN] Content-Type: {request.content_type}")
        print(f"[LOGIN] Raw data: {request.get_data(as_text=True)[:500]}")
        
        data = request.get_json(force=True, silent=True)
        
        if not data:
            print(f"[LOGIN] No JSON data parsed")
            return jsonify({
                'success': False,
                'message': '请求数据格式错误'
            }), 400
            
        username = data.get('username')
        password = data.get('password')
        
        print(f"[LOGIN] Username: {username}, Password length: {len(password) if password else 0}")

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询用户
        cursor.execute(
            """
            SELECT id, username, password_hash, status, total_lingzhi, avatar_url, real_name, created_at, referrer_id
            FROM users
            WHERE username = ? OR phone = ?
            """,
            (username, username)
        )
        user = cursor.fetchone()
        
        print(f"[LOGIN] User found: {user is not None}")

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401

        print(f"[LOGIN] Password hash: {user['password_hash'][:20] if user['password_hash'] else None}...")

        if not verify_password(password, user['password_hash']):
            print(f"[LOGIN] Password verification failed")
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401

        # 检查用户状态
        if user['status'] != 'active':
            conn.close()
            return jsonify({
                'success': False,
                'message': '账户已被禁用'
            }), 403

        # 更新最后登录时间
        cursor.execute(
            "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        conn.commit()
        conn.close()

        # 生成JWT令牌
        token = generate_jwt_token(user['id'], user['username'])
        
        # 检查是否是新用户（24小时内注册）
        is_new_user = False
        bonus_message = None
        if user['created_at']:
            try:
                created_at = datetime.strptime(user['created_at'], '%Y-%m-%d %H:%M:%S')
                hours_since_creation = (datetime.utcnow() - created_at).total_seconds() / 3600
                if hours_since_creation < 24:
                    is_new_user = True
                    bonus_message = f"欢迎注册！系统已赠送您100灵值，可在【我的】-【个人中心】查看"
            except:
                pass
        
        print(f"[LOGIN] Login successful for user: {user['username']}")

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'total_lingzhi': user['total_lingzhi'],
                    'avatarUrl': user['avatar_url'],
                    'realName': user['real_name'],
                    'referrerId': user['referrer_id'] if 'referrer_id' in user.keys() else None
                },
                'is_new_user': is_new_user,
                'bonus_message': bonus_message
            }
        })

    except Exception as e:
        print(f"[LOGIN] Exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

# ============ 验证码 ============

@auth_bp.route('/send-code', methods=['POST'])
def send_code():
    """发送验证码（模拟短信）"""
    try:
        data = request.json
        phone = data.get('phone')

        if not phone:
            return jsonify({
                'success': False,
                'message': '手机号不能为空'
            }), 400

        # 生成验证码
        code = generate_code(6)
        expire_at = datetime.now().timestamp() + 300  # 5分钟后过期

        # 存储验证码（生产环境应该使用Redis）
        verification_codes[phone] = {
            'code': code,
            'expire_at': expire_at
        }

        # TODO: 实际发送短信
        # send_sms(phone, code)

        return jsonify({
            'success': True,
            'message': '验证码已发送',
            'data': {
                'code': code  # 测试环境返回验证码，生产环境应该移除
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送验证码失败: {str(e)}'
        }), 500

@auth_bp.route('/verify-code', methods=['POST'])
def verify_code():
    """验证验证码"""
    try:
        data = request.json
        phone = data.get('phone')
        code = data.get('code')

        if not phone or not code:
            return jsonify({
                'success': False,
                'message': '手机号和验证码不能为空'
            }), 400

        code_data = verification_codes.get(phone)
        if not code_data:
            return jsonify({
                'success': False,
                'message': '验证码无效或已过期'
            }), 400

        if code_data['code'] != code:
            return jsonify({
                'success': False,
                'message': '验证码错误'
            }), 400

        if datetime.now().timestamp() > code_data['expire_at']:
            del verification_codes[phone]
            return jsonify({
                'success': False,
                'message': '验证码已过期'
            }), 400

        return jsonify({
            'success': True,
            'message': '验证码验证成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证验证码失败: {str(e)}'
        }), 500

# ============ 用户验证 ============

@auth_bp.route('/verify-user', methods=['POST'])
def verify_user():
    """验证用户信息"""
    try:
        data = request.json
        phone = data.get('phone')
        verification_code = data.get('verification_code')

        if not phone or not verification_code:
            return jsonify({
                'success': False,
                'message': '手机号和验证码不能为空'
            }), 400

        # 验证验证码
        code_data = verification_codes.get(phone)
        if not code_data:
            return jsonify({
                'success': False,
                'message': '验证码无效或已过期'
            }), 400

        if code_data['code'] != verification_code:
            return jsonify({
                'success': False,
                'message': '验证码错误'
            }), 400

        if datetime.now().timestamp() > code_data['expire_at']:
            del verification_codes[phone]
            return jsonify({
                'success': False,
                'message': '验证码已过期'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查手机号是否已注册
        cursor.execute("SELECT id, username FROM users WHERE phone = ?", (phone,))
        user = cursor.fetchone()

        conn.close()

        if user:
            return jsonify({
                'success': True,
                'message': '手机号已注册',
                'data': {
                    'exists': True,
                    'username': user['username']
                }
            })
        else:
            return jsonify({
                'success': True,
                'message': '手机号未注册',
                'data': {
                    'exists': False
                }
            })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'验证用户失败: {str(e)}'
        }), 500

@auth_bp.route('/send-verify-code', methods=['POST'])
def send_verify_code():
    """发送验证码（用于用户验证）"""
    try:
        data = request.json
        phone = data.get('phone')

        if not phone:
            return jsonify({
                'success': False,
                'message': '手机号不能为空'
            }), 400

        # 生成验证码
        code = generate_code(6)
        expire_at = datetime.now().timestamp() + 300  # 5分钟后过期

        # 存储验证码
        verification_codes[phone] = {
            'code': code,
            'expire_at': expire_at
        }

        # TODO: 实际发送短信
        # send_sms(phone, code)

        return jsonify({
            'success': True,
            'message': '验证码已发送',
            'data': {
                'code': code  # 测试环境返回验证码，生产环境应该移除
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送验证码失败: {str(e)}'
        }), 500

# ============ 密码重置 ============

@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """重置密码（通过验证码）"""
    try:
        data = request.json
        phone = data.get('phone')
        verification_code = data.get('verification_code')
        new_password = data.get('new_password')

        if not phone or not verification_code or not new_password:
            return jsonify({
                'success': False,
                'message': '手机号、验证码和新密码不能为空'
            }), 400

        # 验证验证码
        code_data = verification_codes.get(phone)
        if not code_data:
            return jsonify({
                'success': False,
                'message': '验证码无效或已过期'
            }), 400

        if code_data['code'] != verification_code:
            return jsonify({
                'success': False,
                'message': '验证码错误'
            }), 400

        if datetime.now().timestamp() > code_data['expire_at']:
            del verification_codes[phone]
            return jsonify({
                'success': False,
                'message': '验证码已过期'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询用户
        cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 更新密码
        cursor.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (hash_password(new_password), user['id'])
        )
        conn.commit()
        conn.close()

        # 清除验证码
        del verification_codes[phone]

        return jsonify({
            'success': True,
            'message': '密码重置成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重置密码失败: {str(e)}'
        }), 500

# ============ 获取推荐人信息 ============

@auth_bp.route('/referrer', methods=['GET'])
def get_referrer():
    """获取当前用户的推荐人信息"""
    try:
        # 验证JWT令牌
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'success': False, 'message': '未授权，请提供认证信息'}), 401

        # 提取 token（Bearer token）
        if auth_header.startswith('Bearer '):
            token = auth_header[7:]
        else:
            token = auth_header

        # 验证 token
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            # 检查是否过期
            if datetime.utcnow().timestamp() > payload.get('exp', 0):
                return jsonify({'success': False, 'message': 'Token 已过期'}), 401

            user_id = payload.get('user_id')
        except jwt.ExpiredSignatureError:
            return jsonify({'success': False, 'message': 'Token 已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'success': False, 'message': '无效的 Token'}), 401

        # 查询推荐人信息
        conn = get_db()
        cursor = conn.cursor()

        # 查询推荐关系
        cursor.execute(
            """
            SELECT r.referrer_id, u.username, u.real_name
            FROM referral_relationships r
            LEFT JOIN users u ON r.referrer_id = u.id
            WHERE r.referee_id = ? AND r.status = 'active'
            ORDER BY r.created_at DESC
            LIMIT 1
            """,
            (user_id,)
        )
        referrer_info = cursor.fetchone()
        conn.close()

        if not referrer_info:
            return jsonify({
                'success': True,
                'data': {
                    'referrer': None,
                    'message': '您还没有推荐人'
                }
            })

        return jsonify({
            'success': True,
            'data': {
                'referrer': {
                    'id': referrer_info['referrer_id'],
                    'username': referrer_info['username'],
                    'realName': referrer_info['real_name']
                }
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'获取推荐人信息失败: {str(e)}'
        }), 500

@auth_bp.route('/reset-password-by-username', methods=['POST'])
def reset_password_by_username():
    """重置密码（通过用户名）"""
    try:
        data = request.json
        username = data.get('username')
        verification_code = data.get('verification_code')
        new_password = data.get('new_password')

        if not username or not verification_code or not new_password:
            return jsonify({
                'success': False,
                'message': '用户名、验证码和新密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询用户
        cursor.execute("SELECT id, phone FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        phone = user['phone']

        # 验证验证码
        if phone:
            code_data = verification_codes.get(phone)
            if not code_data:
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '验证码无效或已过期'
                }), 400

            if code_data['code'] != verification_code:
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '验证码错误'
                }), 400

            if datetime.now().timestamp() > code_data['expire_at']:
                del verification_codes[phone]
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '验证码已过期'
                }), 400

        # 更新密码
        cursor.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (hash_password(new_password), user['id'])
        )
        conn.commit()
        conn.close()

        # 清除验证码
        if phone and phone in verification_codes:
            del verification_codes[phone]

        return jsonify({
            'success': True,
            'message': '密码重置成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重置密码失败: {str(e)}'
        }), 500
