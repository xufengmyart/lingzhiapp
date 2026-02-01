#!/usr/bin/env python3
"""
登录安全增强补丁
这个脚本将替换 app.py 中的登录接口，添加：
1. 手机验证码验证
2. 单点登录功能
3. 设备管理
"""

import re

def enhance_login_security():
    """增强登录安全性"""
    app_py_path = '/workspace/projects/admin-backend/app.py'

    # 读取原文件
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 新的登录接口实现
    new_login_function = '''@app.route('/api/login', methods=['POST'])
def login():
    """用户登录（增强版：支持手机验证码和单点登录）"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        phone_code = data.get('phone_code')  # 手机验证码（可选）

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE username = ?",
            (username,)
        )
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401

        if not verify_password(password, user['password_hash']):
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误'
            }), 401

        # 检查是否需要手机验证码
        require_phone_verification = user.get('require_phone_verification', 1)
        phone = user.get('phone')

        if require_phone_verification and phone and not phone_code:
            conn.close()
            return jsonify({
                'success': False,
                'need_phone_code': True,
                'message': '请输入手机验证码'
            }), 400

        # 验证手机验证码
        if require_phone_verification and phone and phone_code:
            if phone not in verification_codes:
                conn.close()
                return jsonify({
                    'success': False,
                    'need_phone_code': True,
                    'message': '验证码不存在或已过期'
                }), 400

            stored = verification_codes[phone]
            if datetime.now().timestamp() > stored['expire_at']:
                conn.close()
                return jsonify({
                    'success': False,
                    'need_phone_code': True,
                    'message': '验证码已过期'
                }), 400

            if stored['code'] != phone_code:
                conn.close()
                return jsonify({
                    'success': False,
                    'need_phone_code': True,
                    'message': '验证码错误'
                }), 400

            # 验证成功，删除验证码
            del verification_codes[phone]

        # 单点登录：检查是否启用了单点登录
        single_login_enabled = user.get('single_login_enabled', 1)
        if single_login_enabled:
            # 删除该用户的所有旧会话
            cursor.execute(
                "DELETE FROM login_sessions WHERE user_id = ?",
                (user['id'],)
            )

        # 生成token
        token = generate_token(user['id'])

        # 获取客户端信息
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        # 生成设备ID
        device_id = hashlib.md5(f"{user['id']}_{ip_address}_{user_agent}".encode()).hexdigest()[:32]

        # 记录登录会话
        expires_at = datetime.now() + timedelta(seconds=JWT_EXPIRATION)
        cursor.execute(
            """INSERT INTO login_sessions (user_id, token, device_id, ip_address, user_agent, expires_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user['id'], token, device_id, ip_address, user_agent, expires_at)
        )

        # 记录或更新设备信息
        cursor.execute(
            """SELECT id FROM user_devices WHERE user_id = ? AND device_id = ?""",
            (user['id'], device_id)
        )
        existing_device = cursor.fetchone()

        device_name = f"设备-{device_id[:8]}"
        device_type = "Unknown"

        # 简单识别设备类型
        if 'iPhone' in user_agent or 'iPad' in user_agent:
            device_type = "iOS"
            device_name = "iPhone/iPad"
        elif 'Android' in user_agent:
            device_type = "Android"
            device_name = "Android设备"
        elif 'Mac' in user_agent:
            device_type = "Mac"
            device_name = "Mac电脑"
        elif 'Windows' in user_agent:
            device_type = "Windows"
            device_name = "Windows电脑"

        if existing_device:
            # 更新现有设备
            cursor.execute(
                """UPDATE user_devices
                   SET is_current = 1, last_active_at = CURRENT_TIMESTAMP,
                       ip_address = ?, user_agent = ?, device_name = ?, device_type = ?
                   WHERE user_id = ? AND device_id = ?""",
                (ip_address, user_agent, device_name, device_type, user['id'], device_id)
            )
        else:
            # 记录新设备
            cursor.execute(
                """INSERT INTO user_devices
                   (user_id, device_id, device_name, device_type, user_agent, ip_address, is_current, last_active_at)
                   VALUES (?, ?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)""",
                (user['id'], device_id, device_name, device_type, user_agent, ip_address)
            )

        # 将其他设备标记为非当前
        cursor.execute(
            """UPDATE user_devices SET is_current = 0 WHERE user_id = ? AND device_id != ?""",
            (user['id'], device_id)
        )

        # 更新用户最后登录时间
        cursor.execute(
            "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )

        # 记录安全日志
        cursor.execute(
            """INSERT INTO security_logs (user_id, event_type, ip_address, user_agent, details)
               VALUES (?, 'login', ?, ?, ?)""",
            (user['id'], ip_address, user_agent, json.dumps({'device_id': device_id, 'device_name': device_name}))
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
                    'totalLingzhi': user['total_lingzhi']
                },
                'device': {
                    'device_id': device_id,
                    'device_name': device_name,
                    'device_type': device_type
                }
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500'''

    # 查找并替换登录函数
    pattern = r"@app\.route\('/api/login', methods=\['POST'\]\)\s+def login\(\):.*?(?=\n@app\.route|\n# ============|\Z)"
    match = re.search(pattern, content, re.DOTALL)

    if match:
        print("找到旧的登录函数，正在替换...")
        content = re.sub(pattern, new_login_function, content, flags=re.DOTALL)
        print("✅ 登录函数已替换")
    else:
        print("❌ 未找到登录函数")
        return False

    # 写回文件
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ app.py 已更新")
    return True

if __name__ == '__main__':
    if enhance_login_security():
        print("\n==========================================")
        print("✅ 登录安全增强完成！")
        print("==========================================")
        print("\n新功能:")
        print("1. 手机验证码验证（可选）")
        print("2. 单点登录（默认启用）")
        print("3. 设备管理")
        print("4. 安全日志")
    else:
        print("\n❌ 更新失败")
