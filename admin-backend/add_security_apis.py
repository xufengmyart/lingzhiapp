#!/usr/bin/env python3
"""
添加设备管理和安全设置API
"""

import re

def add_security_apis():
    """添加安全相关API"""
    app_py_path = '/workspace/projects/admin-backend/app.py'

    # 读取原文件
    with open(app_py_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 新的安全API
    security_apis = '''
# ============ 设备管理和安全设置 API ============

@app.route('/api/user/devices', methods=['GET'])
def get_user_devices():
    """获取用户的设备列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, device_id, device_name, device_type, ip_address,
                      location, is_current, last_active_at, created_at
               FROM user_devices WHERE user_id = ?
               ORDER BY is_current DESC, last_active_at DESC""",
            (user_id,)
        )
        devices = cursor.fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'data': [dict(d) for d in devices]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取设备列表失败: {str(e)}'}), 500

@app.route('/api/user/devices/<device_id>', methods=['DELETE'])
def remove_device(device_id):
    """移除设备"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        # 不能删除当前设备
        cursor.execute(
            "SELECT is_current FROM user_devices WHERE user_id = ? AND device_id = ?",
            (user_id, device_id)
        )
        device = cursor.fetchone()

        if not device:
            conn.close()
            return jsonify({'success': False, 'message': '设备不存在'}), 404

        if device['is_current']:
            conn.close()
            return jsonify({'success': False, 'message': '不能移除当前设备'}), 400

        # 删除设备
        cursor.execute(
            "DELETE FROM user_devices WHERE user_id = ? AND device_id = ?",
            (user_id, device_id)
        )

        # 删除该设备的登录会话
        cursor.execute(
            "DELETE FROM login_sessions WHERE user_id = ? AND device_id = ?",
            (user_id, device_id)
        )

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '设备已移除'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'移除设备失败: {str(e)}'}), 500

@app.route('/api/user/security/settings', methods=['GET'])
def get_security_settings():
    """获取用户安全设置"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT require_phone_verification, single_login_enabled FROM users WHERE id = ?",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'require_phone_verification': bool(user['require_phone_verification'] if 'require_phone_verification' in user.keys() else 1),
                'single_login_enabled': bool(user['single_login_enabled'] if 'single_login_enabled' in user.keys() else 1)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取安全设置失败: {str(e)}'}), 500

@app.route('/api/user/security/settings', methods=['PUT'])
def update_security_settings():
    """更新用户安全设置"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        data = request.json
        require_phone_verification = data.get('require_phone_verification')
        single_login_enabled = data.get('single_login_enabled')

        conn = get_db()
        cursor = conn.cursor()

        # 更新设置
        if require_phone_verification is not None:
            cursor.execute(
                "UPDATE users SET require_phone_verification = ? WHERE id = ?",
                (1 if require_phone_verification else 0, user_id)
            )

        if single_login_enabled is not None:
            cursor.execute(
                "UPDATE users SET single_login_enabled = ? WHERE id = ?",
                (1 if single_login_enabled else 0, user_id)
            )

        # 如果启用了单点登录，删除所有旧的会话
        if single_login_enabled:
            # 保留当前会话
            current_token = request.headers.get('Authorization', '').replace('Bearer ', '')
            cursor.execute(
                """DELETE FROM login_sessions WHERE user_id = ? AND token != ?""",
                (user_id, current_token)
            )

        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '安全设置已更新'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'更新安全设置失败: {str(e)}'}), 500

@app.route('/api/user/security/logs', methods=['GET'])
def get_security_logs():
    """获取用户安全日志"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id, event_type, ip_address, user_agent, details, created_at
               FROM security_logs WHERE user_id = ?
               ORDER BY created_at DESC LIMIT 50""",
            (user_id,)
        )
        logs = cursor.fetchall()

        conn.close()

        return jsonify({
            'success': True,
            'data': [dict(l) for l in logs]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取安全日志失败: {str(e)}'}), 500

@app.route('/api/user/devices/revoke-all', methods=['POST'])
def revoke_all_other_devices():
    """移除所有其他设备（仅保留当前设备）"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        conn = get_db()
        cursor = conn.cursor()

        # 获取当前设备的ID
        cursor.execute(
            "SELECT device_id FROM login_sessions WHERE token = ?",
            (token,)
        )
        session = cursor.fetchone()

        if not session:
            conn.close()
            return jsonify({'success': False, 'message': '会话不存在'}), 404

        current_device_id = session['device_id']

        # 删除所有其他设备和会话
        cursor.execute(
            """DELETE FROM login_sessions WHERE user_id = ? AND device_id != ?""",
            (user_id, current_device_id)
        )
        deleted_sessions = cursor.rowcount

        cursor.execute(
            """DELETE FROM user_devices WHERE user_id = ? AND device_id != ?""",
            (user_id, current_device_id)
        )
        deleted_devices = cursor.rowcount

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'已移除 {deleted_devices} 个设备和 {deleted_sessions} 个会话'
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'操作失败: {str(e)}'}), 500

'''

    # 在后台管理部分之前插入
    marker = "# ============ 后台管理 ============"
    if marker in content:
        content = content.replace(marker, security_apis + "\n" + marker)
        print("✅ 安全API已添加到app.py")
    else:
        print("❌ 未找到插入点")
        return False

    # 写回文件
    with open(app_py_path, 'w', encoding='utf-8') as f:
        f.write(content)

    return True

if __name__ == '__main__':
    if add_security_apis():
        print("\n==========================================")
        print("✅ 安全API添加完成！")
        print("==========================================")
        print("\n新增API:")
        print("- GET /api/user/devices - 获取设备列表")
        print("- DELETE /api/user/devices/<device_id> - 移除设备")
        print("- GET /api/user/security/settings - 获取安全设置")
        print("- PUT /api/user/security/settings - 更新安全设置")
        print("- GET /api/user/security/logs - 获取安全日志")
        print("- POST /api/user/devices/revoke-all - 移除所有其他设备")
    else:
        print("\n❌ 添加失败")
