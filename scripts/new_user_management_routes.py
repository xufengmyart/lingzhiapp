#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 新增的用户管理接口，需要插入到app.py中

new_user_management_routes = '''
@app.route('/api/admin/users/<int:user_id>', methods=['GET'])
def admin_get_user_detail(user_id):
    """获取用户详情"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        # 获取用户详情
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 获取用户签到统计
        cursor.execute("SELECT COUNT(*) as count FROM checkin_records WHERE user_id = ?", (user_id,))
        checkin_count = cursor.fetchone()['count']

        # 获取用户充值记录
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(amount), 0) as total_amount 
            FROM recharge_records 
            WHERE user_id = ? AND payment_status = 'paid'
        """, (user_id,))
        recharge_stats = cursor.fetchone()

        # 获取用户消费记录
        cursor.execute("""
            SELECT COUNT(*) as count, COALESCE(SUM(lingzhi_amount), 0) as total_lingzhi 
            FROM lingzhi_consumption_records 
            WHERE user_id = ?
        """, (user_id,))
        consumption_stats = cursor.fetchone()

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'phone': user['phone'],
                'total_lingzhi': user['total_lingzhi'],
                'status': user.get('status', 'active'),
                'last_login_at': user.get('last_login_at'),
                'avatar_url': user.get('avatar_url'),
                'real_name': user.get('real_name'),
                'is_verified': user.get('is_verified', 0),
                'created_at': user['created_at'],
                'updated_at': user['updated_at'],
                'stats': {
                    'checkin_count': checkin_count,
                    'recharge_count': recharge_stats['count'],
                    'recharge_amount': float(recharge_stats['total_amount']),
                    'consumption_count': consumption_stats['count'],
                    'consumption_lingzhi': consumption_stats['total_lingzhi']
                }
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'获取用户详情失败: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/status', methods=['PUT'])
def admin_update_user_status(user_id):
    """更新用户状态"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        data = request.json
        status = data.get('status')

        if status not in ['active', 'inactive', 'banned']:
            return jsonify({'success': False, 'message': '无效的状态'}), 400

        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 更新用户状态
        cursor.execute(
            "UPDATE users SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({'success': True, 'message': '用户状态更新成功'})

    except Exception as e:
        return jsonify({'success': False, 'message': f'更新用户状态失败: {str(e)}'}), 500

@app.route('/api/admin/users/<int:user_id>/lingzhi', methods=['POST'])
def admin_adjust_user_lingzhi(user_id):
    """调整用户灵值"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        data = request.json
        amount = data.get('amount')
        reason = data.get('reason', '管理员调整')

        if not amount:
            return jsonify({'success': False, 'message': '调整金额不能为空'}), 400

        # 检查用户是否存在
        cursor.execute("SELECT id, total_lingzhi FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({'success': False, 'message': '用户不存在'}), 404

        # 调整灵值
        new_lingzhi = user['total_lingzhi'] + amount
        if new_lingzhi < 0:
            conn.close()
            return jsonify({'success': False, 'message': '灵值余额不足'}), 400

        cursor.execute(
            "UPDATE users SET total_lingzhi = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (new_lingzhi, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '灵值调整成功',
            'data': {
                'old_lingzhi': user['total_lingzhi'],
                'new_lingzhi': new_lingzhi,
                'adjustment': amount
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'调整灵值失败: {str(e)}'}), 500

@app.route('/api/admin/users/search', methods=['GET'])
def admin_search_users():
    """搜索用户"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        keyword = request.args.get('keyword', '')
        limit = int(request.args.get('limit', 10))

        if not keyword:
            conn.close()
            return jsonify({'success': False, 'message': '搜索关键词不能为空'}), 400

        # 搜索用户
        search_pattern = f'%{keyword}%'
        cursor.execute("""
            SELECT id, username, email, phone, total_lingzhi, status, created_at
            FROM users
            WHERE username LIKE ? OR email LIKE ? OR phone LIKE ?
            ORDER BY id DESC
            LIMIT ?
        """, (search_pattern, search_pattern, search_pattern, limit))
        users = cursor.fetchall()
        conn.close()

        return jsonify({
            'success': True,
            'data': [dict(user) for user in users]
        })

    except Exception as e:
        return jsonify({'success': False, 'message': f'搜索用户失败: {str(e)}'}), 500

@app.route('/api/admin/users/export', methods=['GET'])
def admin_export_users():
    """导出用户列表"""
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'message': '未授权'}), 401

        token = auth_header.replace('Bearer ', '')
        admin_id = verify_token(token)
        if not admin_id:
            return jsonify({'success': False, 'message': 'token无效'}), 401

        # 验证是否为管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM admins WHERE id = ?", (admin_id,))
        admin = cursor.fetchone()
        if not admin:
            conn.close()
            return jsonify({'success': False, 'message': '无权限'}), 403

        # 获取所有用户
        cursor.execute("""
            SELECT id, username, email, phone, total_lingzhi, status, created_at
            FROM users
            ORDER BY id DESC
        """)
        users = cursor.fetchall()
        conn.close()

        # 生成CSV
        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', '用户名', '邮箱', '手机', '灵值', '状态', '注册时间'])
        
        for user in users:
            writer.writerow([
                user['id'],
                user['username'],
                user.get('email', ''),
                user.get('phone', ''),
                user['total_lingzhi'],
                user.get('status', 'active'),
                user['created_at']
            ])

        # 返回CSV文件
        output.seek(0)
        from flask import Response
        response = Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={
                'Content-Disposition': 'attachment; filename=users.csv'
            }
        )
        return response

    except Exception as e:
        return jsonify({'success': False, 'message': f'导出用户列表失败: {str(e)}'}), 500
'''

print("新的用户管理接口代码已生成")
print("请手动将这些代码插入到 app.py 的删除用户接口之后，统计接口之前")
