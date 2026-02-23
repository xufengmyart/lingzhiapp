#!/usr/bin/env python3
"""
登录API改进方案
支持用户名、手机号、邮箱登录，增强错误提示
"""

def improved_login_code():
    """
    返回改进后的登录API代码
    可以直接添加到 app.py 中替换原有的 login 函数
    """
    code = '''
# ============ 改进的登录API ============
@app.route('/api/login', methods=['POST'])
def login():
    """用户登录 - 支持用户名、手机号、邮箱登录"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        # 增强输入验证
        if not username:
            return jsonify({
                'success': False,
                'message': '请输入用户名、手机号或邮箱',
                'error_code': 'MISSING_USERNAME'
            }), 400

        if not password:
            return jsonify({
                'success': False,
                'message': '请输入密码',
                'error_code': 'MISSING_PASSWORD'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 支持多种登录方式：用户名、手机号、邮箱
        # 先尝试用户名
        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()

        # 如果用户名没找到，尝试手机号
        if not user and username.isdigit() and len(username) == 11:
            cursor.execute(
                "SELECT * FROM users WHERE phone = ?",
                (username,)
            )
            user = cursor.fetchone()

        # 如果还没找到，尝试邮箱
        if not user and '@' in username:
            cursor.execute(
                "SELECT * FROM users WHERE email = ?",
                (username,)
            )
            user = cursor.fetchone()

        conn.close()

        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在，请先注册',
                'error_code': 'USER_NOT_FOUND'
            }), 401

        # 检查用户状态
        if user['status'] != 'active':
            return jsonify({
                'success': False,
                'message': '账号已被禁用，请联系管理员',
                'error_code': 'ACCOUNT_DISABLED'
            }), 403

        # 验证密码
        if not verify_password(password, user['password_hash']):
            return jsonify({
                'success': False,
                'message': '密码错误，请重试',
                'error_code': 'WRONG_PASSWORD'
            }), 401

        # 生成token
        token = generate_token(user['id'])

        # 更新最后登录时间
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET last_login_at = ? WHERE id = ?",
            (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), user['id'])
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'token': token,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'email': user['email'],
                    'phone': user['phone'],
                    'totalLingzhi': user['total_lingzhi'],
                    'realName': user['real_name'],
                    'avatarUrl': user['avatar_url'],
                    'loginType': user['login_type']
                }
            }
        })

    except Exception as e:
        print(f"登录错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '登录失败，请稍后重试',
            'error_code': 'INTERNAL_ERROR'
        }), 500


# ============ 改进的注册API ============
@app.route('/api/register', methods=['POST'])
def register():
    """用户注册 - 支持直接注册和微信关联注册"""
    try:
        data = request.json
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '').strip()
        phone = data.get('phone', '').strip()
        referrer = data.get('referrer', '').strip()
        wechat_openid = data.get('wechat_openid', '')
        wechat_unionid = data.get('wechat_unionid', '')
        wechat_nickname = data.get('wechat_nickname', '')
        wechat_avatar = data.get('wechat_avatar', '')

        # 增强输入验证
        if not username:
            return jsonify({
                'success': False,
                'message': '请输入用户名',
                'error_code': 'MISSING_USERNAME'
            }), 400

        if not email:
            return jsonify({
                'success': False,
                'message': '请输入邮箱',
                'error_code': 'MISSING_EMAIL'
            }), 400

        if not password:
            return jsonify({
                'success': False,
                'message': '请输入密码',
                'error_code': 'MISSING_PASSWORD'
            }), 400

        # 验证邮箱格式
        if '@' not in email:
            return jsonify({
                'success': False,
                'message': '邮箱格式不正确',
                'error_code': 'INVALID_EMAIL'
            }), 400

        # 验证密码长度
        if len(password) < 6:
            return jsonify({
                'success': False,
                'message': '密码长度不能少于6位',
                'error_code': 'PASSWORD_TOO_SHORT'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名已存在，请更换其他用户名',
                'error_code': 'USERNAME_EXISTS'
            }), 409

        # 检查邮箱是否已存在
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '邮箱已被注册，请直接登录',
                'error_code': 'EMAIL_EXISTS'
            }), 409

        # 检查手机号是否已存在（如果提供了手机号）
        if phone:
            cursor.execute("SELECT id FROM users WHERE phone = ?", (phone,))
            if cursor.fetchone():
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '手机号已被注册，请更换其他手机号',
                    'error_code': 'PHONE_EXISTS'
                }), 409

        # 查找推荐人
        referrer_id = None
        if referrer:
            cursor.execute("SELECT id FROM users WHERE username = ?", (referrer,))
            referrer_user = cursor.fetchone()
            if referrer_user:
                referrer_id = referrer_user['id']

        # 确定登录类型
        login_type = 'wechat' if wechat_openid else 'phone'
        if not phone:
            login_type = 'email'

        # 生成密码哈希
        password_hash = generate_password_hash(password)

        # 创建用户
        cursor.execute(
            """INSERT INTO users
            (username, email, password_hash, phone, total_lingzhi, status,
             login_type, wechat_openid, wechat_unionid, wechat_nickname, wechat_avatar,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, 'active', ?, ?, ?, ?, ?, ?, ?)""",
            (
                username, email, password_hash, phone, 0,
                login_type, wechat_openid, wechat_unionid, wechat_nickname, wechat_avatar,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            )
        )
        user_id = cursor.lastrowid

        # 创建推荐关系
        if referrer_id:
            cursor.execute(
                """INSERT INTO referral_relationships
                (referrer_id, referee_id, referral_date, status, created_at)
                VALUES (?, ?, ?, 'active', ?)""",
                (referrer_id, user_id, datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            )

        conn.commit()
        conn.close()

        # 生成token
        token = generate_token(user_id)

        # 返回成功信息
        return jsonify({
            'success': True,
            'message': '注册成功',
            'data': {
                'token': token,
                'user': {
                    'id': user_id,
                    'username': username,
                    'email': email,
                    'phone': phone,
                    'totalLingzhi': 0,
                    'realName': '',
                    'avatarUrl': wechat_avatar,
                    'loginType': login_type
                }
            }
        })

    except Exception as e:
        print(f"注册错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'注册失败: {str(e)}',
            'error_code': 'INTERNAL_ERROR'
        }), 500


# ============ 微信登录占位API（暂时禁用，给友好提示）============
@app.route('/api/wechat/login', methods=['POST', 'GET'])
def wechat_login():
    """微信登录 - 暂时禁用，给用户友好提示"""
    return jsonify({
        'success': False,
        'message': '微信登录功能正在开发中，请使用手机号登录',
        'error_code': 'WECHAT_LOGIN_DISABLED'
    }), 503


# ============ 检查用户是否存在（用于分享链接）============
@app.route('/api/user/check-exists', methods=['GET'])
def check_user_exists():
    """检查用户是否存在 - 用于分享链接"""
    try:
        username = request.args.get('username', '').strip()
        phone = request.args.get('phone', '').strip()
        email = request.args.get('email', '').strip()

        if not username and not phone and not email:
            return jsonify({
                'success': False,
                'message': '请提供用户名、手机号或邮箱',
                'error_code': 'MISSING_IDENTIFIER'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        user = None
        if username:
            cursor.execute("SELECT id, username, email, phone, avatar_url FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
        elif phone:
            cursor.execute("SELECT id, username, email, phone, avatar_url FROM users WHERE phone = ?", (phone,))
            user = cursor.fetchone()
        elif email:
            cursor.execute("SELECT id, username, email, phone, avatar_url FROM users WHERE email = ?", (email,))
            user = cursor.fetchone()

        conn.close()

        if not user:
            return jsonify({
                'success': False,
                'message': '用户不存在',
                'error_code': 'USER_NOT_FOUND'
            }), 404

        return jsonify({
            'success': True,
            'message': '用户存在',
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'avatarUrl': user['avatar_url']
            }
        })

    except Exception as e:
        print(f"检查用户错误: {str(e)}")
        return jsonify({
            'success': False,
            'message': '检查失败',
            'error_code': 'INTERNAL_ERROR'
        }), 500
'''

    return code

if __name__ == '__main__':
    print("=" * 60)
    print("改进的登录API代码")
    print("=" * 60)
    print()
    print("将以下代码添加到 app.py 中：")
    print()
    print(improved_login_code())
    print()
    print("=" * 60)
    print("主要改进：")
    print("  1. 支持用户名、手机号、邮箱登录")
    print("  2. 增强的错误提示（error_code）")
    print("  3. 检查用户状态（active/disabled）")
    print("  4. 更新最后登录时间")
    print("  5. 改进的注册API（支持推荐关系）")
    print("  6. 微信登录占位（友好提示）")
    print("  7. 检查用户存在性API（用于分享链接）")
    print("=" * 60)
