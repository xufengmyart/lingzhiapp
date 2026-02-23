"""
管理员功能路由蓝图
包含所有后台管理功能：用户管理、角色权限、智能体管理等
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json
from datetime import datetime, timedelta
import bcrypt
import jwt
from functools import wraps

admin_bp = Blueprint('admin', __name__)

# 导入配置和工具函数
from config import config
DATABASE = config.DATABASE_PATH
JWT_SECRET = config.JWT_SECRET_KEY
JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION = config.JWT_EXPIRATION

# 辅助函数
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def verify_password(password, hashed):
    """验证密码"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def hash_password(password):
    """哈希密码"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def generate_token(admin_id, username, role):
    """生成JWT令牌"""
    payload = {
        'admin_id': admin_id,
        'username': username,
        'role': role,
        'exp': datetime.utcnow() + timedelta(seconds=JWT_EXPIRATION),
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token):
    """验证JWT令牌"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def require_admin(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # TODO: 添加JWT验证逻辑
        return f(*args, **kwargs)
    return decorated_function

# ============ 管理员登录 ============

@admin_bp.route('/admin/login', methods=['POST'])
def admin_login():
    """管理员登录"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询管理员
        cursor.execute(
            "SELECT id, username, password_hash, role FROM admins WHERE username = ?",
            (username,)
        )
        admin = cursor.fetchone()

        if not admin:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误',
                'error_code': 'ADMIN_NOT_FOUND'
            }), 401

        if not verify_password(password, admin['password_hash']):
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名或密码错误',
                'error_code': 'INVALID_PASSWORD'
            }), 401

        # 生成JWT令牌
        token = generate_token(admin['id'], admin['username'], admin['role'])

        conn.close()

        return jsonify({
            'success': True,
            'message': '登录成功',
            'data': {
                'token': token,
                'admin': {
                    'id': admin['id'],
                    'username': admin['username'],
                    'role': admin['role']
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'登录失败: {str(e)}'
        }), 500

# ============ 用户管理 ============

@admin_bp.route('/admin/users', methods=['GET'])
@require_admin
def admin_get_users():
    """获取所有用户列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('limit', 20))  # 改为limit以匹配前端
        offset = (page - 1) * page_size

        # 获取筛选参数
        status = request.args.get('status')
        user_type_id = request.args.get('user_type_id')
        min_lingzhi = request.args.get('min_lingzhi')
        max_lingzhi = request.args.get('max_lingzhi')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        search = request.args.get('search', '')

        # 获取排序参数
        sort_by = request.args.get('sort_by', 'created_at')
        sort_order = request.args.get('sort_order', 'DESC')

        # 验证排序字段
        valid_sort_fields = ['id', 'username', 'email', 'phone', 'total_lingzhi', 'status', 'created_at', 'last_login_at']
        if sort_by not in valid_sort_fields:
            sort_by = 'created_at'
        
        # 验证排序方向
        sort_order = 'DESC' if sort_order.upper() == 'DESC' else 'ASC'

        # 构建查询条件
        where_conditions = ['1=1']
        params = []

        if status:
            where_conditions.append("status = ?")
            params.append(status)

        if user_type_id:
            where_conditions.append("user_type_id = ?")
            params.append(user_type_id)

        if min_lingzhi:
            where_conditions.append("total_lingzhi >= ?")
            params.append(int(min_lingzhi))

        if max_lingzhi:
            where_conditions.append("total_lingzhi <= ?")
            params.append(int(max_lingzhi))

        if start_date:
            where_conditions.append("created_at >= ?")
            params.append(start_date)

        if end_date:
            where_conditions.append("created_at <= ?")
            params.append(end_date)

        if search:
            where_conditions.append("(username LIKE ? OR email LIKE ? OR phone LIKE ? OR real_name LIKE ?)")
            search_term = f'%{search}%'
            params.extend([search_term, search_term, search_term, search_term])

        where_clause = " AND ".join(where_conditions)

        # 获取总数
        cursor.execute(
            f"SELECT COUNT(*) as total FROM users WHERE {where_clause}",
            params
        )
        total = cursor.fetchone()['total']

        # 获取用户列表
        cursor.execute(
            f"""
            SELECT id, username, email, phone, total_lingzhi, status,
                   created_at, last_login_at, avatar_url, real_name, referrer_id
            FROM users
            WHERE {where_clause}
            ORDER BY {sort_by} {sort_order}
            LIMIT ? OFFSET ?
            """,
            params + [page_size, offset]
        )
        users = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'users': users,
                'pagination': {
                    'total': total,
                    'page': page,
                    'page_size': page_size,
                    'total_pages': (total + page_size - 1) // page_size
                }
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户列表失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users', methods=['POST'])
@require_admin
def admin_create_user():
    """创建用户"""
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        email = data.get('email')
        phone = data.get('phone')

        if not username or not password:
            return jsonify({
                'success': False,
                'message': '用户名和密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查用户名是否已存在
        cursor.execute(
            "SELECT id FROM users WHERE username = ?",
            (username,)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户名已存在'
            }), 400

        # 创建用户
        cursor.execute(
            """
            INSERT INTO users (username, password_hash, email, phone, total_lingzhi, status)
            VALUES (?, ?, ?, ?, 100, 'active')
            """,
            (username, hash_password(password), email, phone)
        )
        user_id = cursor.lastrowid
        
        # 记录灵值消费记录
        cursor.execute(
            """
            INSERT INTO lingzhi_consumption_records (user_id, consumption_type, consumption_item, lingzhi_amount, description)
            VALUES (?, 'admin_create', 'new_user_bonus', 100, '管理员创建用户赠送')
            """,
            (user_id,)
        )
        
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '用户创建成功',
            'data': {'user_id': user_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建用户失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['PUT'])
@require_admin
def admin_update_user(user_id):
    """更新用户信息"""
    try:
        data = request.json
        conn = get_db()
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 构建更新字段
        update_fields = []
        params = []

        for field in ['email', 'phone', 'real_name', 'status']:
            if field in data:
                update_fields.append(f"{field} = ?")
                params.append(data[field])

        if update_fields:
            params.append(user_id)
            cursor.execute(
                f"UPDATE users SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                params
            )
            conn.commit()

        conn.close()

        return jsonify({
            'success': True,
            'message': '用户信息更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新用户信息失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['DELETE'])
@require_admin
def admin_delete_user(user_id):
    """删除用户"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE id = ?", (user_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 删除用户（级联删除相关数据）
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '用户删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除用户失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users/<int:user_id>', methods=['GET'])
@require_admin
def admin_get_user_detail(user_id):
    """获取用户详情"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT * FROM users WHERE id = ?
            """,
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        conn.close()

        return jsonify({
            'success': True,
            'data': dict(user)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户详情失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users/<int:user_id>/status', methods=['PUT'])
@require_admin
def admin_update_user_status(user_id):
    """更新用户状态"""
    try:
        data = request.json
        status = data.get('status')

        if not status:
            return jsonify({
                'success': False,
                'message': '状态不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (status, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '用户状态更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新用户状态失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users/<int:user_id>/lingzhi', methods=['POST'])
@require_admin
def admin_adjust_user_lingzhi(user_id):
    """调整用户灵值"""
    try:
        data = request.json
        amount = data.get('amount')
        reason = data.get('reason', '管理员调整')

        if amount is None:
            return jsonify({
                'success': False,
                'message': '调整金额不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET total_lingzhi = total_lingzhi + ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (amount, user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '灵值调整成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'调整灵值失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users/<int:user_id>/password', methods=['PUT'])
@require_admin
def admin_change_user_password(user_id):
    """重置用户密码"""
    try:
        data = request.json
        new_password = data.get('new_password')

        if not new_password:
            return jsonify({
                'success': False,
                'message': '新密码不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE users SET password_hash = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (hash_password(new_password), user_id)
        )
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '密码重置成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'重置密码失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users/search', methods=['GET'])
@require_admin
def admin_search_users():
    """搜索用户"""
    try:
        keyword = request.args.get('keyword', '')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 20))
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 搜索用户
        cursor.execute(
            """
            SELECT id, username, email, phone, total_lingzhi, status, created_at
            FROM users
            WHERE username LIKE ? OR email LIKE ? OR phone LIKE ? OR real_name LIKE ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
            """,
            (f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', f'%{keyword}%', page_size, offset)
        )
        users = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': users
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'搜索用户失败: {str(e)}'
        }), 500

@admin_bp.route('/admin/users/export', methods=['GET'])
@require_admin
def admin_export_users():
    """导出用户数据"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT id, username, email, phone, total_lingzhi, status,
                   created_at, last_login_at, real_name
            FROM users
            ORDER BY created_at DESC
            """
        )
        users = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # TODO: 返回CSV或Excel文件
        return jsonify({
            'success': True,
            'data': users
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'导出用户数据失败: {str(e)}'
        }), 500

# ============ 统计数据 ============

@admin_bp.route('/admin/stats', methods=['GET'])
@require_admin
def admin_stats():
    """获取管理员统计数据"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 统计数据
        stats = {}

        # 用户统计
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        stats['total_users'] = cursor.fetchone()['total_users']

        cursor.execute("SELECT COUNT(*) as active_users FROM users WHERE status = 'active'")
        stats['active_users'] = cursor.fetchone()['active_users']

        # 灵值统计
        cursor.execute("SELECT SUM(total_lingzhi) as total_lingzhi FROM users")
        stats['total_lingzhi'] = cursor.fetchone()['total_lingzhi'] or 0

        # 今日新增用户
        cursor.execute("""
            SELECT COUNT(*) as today_new_users
            FROM users
            WHERE DATE(created_at) = DATE('now')
        """)
        stats['today_new_users'] = cursor.fetchone()['today_new_users']

        conn.close()

        return jsonify({
            'success': True,
            'data': stats
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取统计数据失败: {str(e)}'
        }), 500
