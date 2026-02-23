"""
管理员统计API
补充管理员后台统计接口
"""

from flask import Blueprint, jsonify
import sqlite3

admin_stats_bp = Blueprint('admin_stats', __name__)

from config import config
DATABASE = config.DATABASE_PATH

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============ 用户统计 ============

@admin_stats_bp.route('/admin/stats/user', methods=['GET'])
def get_user_stats():
    """获取用户统计数据"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 总用户数
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total_users = cursor.fetchone()['total']

        # 今日新增用户
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE DATE(created_at) = DATE('now', 'localtime')")
        today_new = cursor.fetchone()['count']

        # 本月新增用户
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now', 'localtime')")
        month_new = cursor.fetchone()['count']

        # 活跃用户（最近7天登录）
        cursor.execute("SELECT COUNT(*) as count FROM users WHERE last_login_at >= DATE('now', '-7 days', 'localtime')")
        active_users = cursor.fetchone()['count']

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'totalUsers': total_users,
                'todayNew': today_new,
                'monthNew': month_new,
                'activeUsers': active_users
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户统计失败: {str(e)}'
        }), 500

# ============ 权限列表 ============

@admin_stats_bp.route('/admin/permissions', methods=['GET'])
def get_permissions():
    """获取权限列表"""
    try:
        # 返回预定义的权限列表
        permissions = [
            {
                'id': 'user.view',
                'name': '查看用户',
                'category': '用户管理'
            },
            {
                'id': 'user.edit',
                'name': '编辑用户',
                'category': '用户管理'
            },
            {
                'id': 'user.delete',
                'name': '删除用户',
                'category': '用户管理'
            },
            {
                'id': 'content.view',
                'name': '查看内容',
                'category': '内容管理'
            },
            {
                'id': 'content.edit',
                'name': '编辑内容',
                'category': '内容管理'
            },
            {
                'id': 'content.delete',
                'name': '删除内容',
                'category': '内容管理'
            },
            {
                'id': 'system.view',
                'name': '查看系统设置',
                'category': '系统管理'
            },
            {
                'id': 'system.edit',
                'name': '编辑系统设置',
                'category': '系统管理'
            }
        ]

        return jsonify({
            'success': True,
            'data': permissions
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取权限列表失败: {str(e)}'
        }), 500

# ============ 用户类型列表 ============

@admin_stats_bp.route('/admin/user-types', methods=['GET'])
def get_user_types():
    """获取用户类型列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 按登录类型统计用户
        cursor.execute("""
            SELECT login_type as type,
                   COUNT(*) as count,
                   MIN(created_at) as first_created_at
            FROM users
            WHERE login_type IS NOT NULL
            GROUP BY login_type
        """)
        user_types = cursor.fetchall()

        result = []
        for item in user_types:
            result.append({
                'type': item['type'],
                'name': {
                    'phone': '手机号',
                    'wechat': '微信',
                    'email': '邮箱'
                }.get(item['type'], item['type']),
                'count': item['count'],
                'createdAt': item['first_created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户类型列表失败: {str(e)}'
        }), 500

# ============ 智能体列表（管理员） ============

@admin_stats_bp.route('/admin/agents', methods=['GET'])
def get_admin_agents():
    """获取智能体列表（管理员视角）"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 查询智能体
        cursor.execute("""
            SELECT id, name, description, status, created_at
            FROM agents
            ORDER BY created_at DESC
        """)
        agents = cursor.fetchall()

        result = [dict(agent) for agent in agents]

        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取智能体列表失败: {str(e)}'
        }), 500

# ============ 知识库列表（管理员） ============

@admin_stats_bp.route('/admin/knowledge-bases', methods=['GET'])
def get_admin_knowledge_bases():
    """获取知识库列表（管理员视角）"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 查询知识库
        cursor.execute("""
            SELECT id, name, description, created_at
            FROM knowledge_bases
            ORDER BY created_at DESC
        """)
        kb_list = cursor.fetchall()

        result = [dict(kb) for kb in kb_list]

        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取知识库列表失败: {str(e)}'
        }), 500

# ============ 用户资料（管理员） ============

@admin_stats_bp.route('/admin/users/<int:user_id>/profile', methods=['GET'])
def get_user_profile_admin(user_id):
    """获取用户资料（管理员视角）"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, username, email, phone, real_name, avatar_url, bio, location, website,
                   total_lingzhi, status, created_at, updated_at
            FROM users
            WHERE id = ?
        """, (user_id,))
        user = cursor.fetchone()

        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        result = dict(user)

        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取用户资料失败: {str(e)}'
        }), 500

# ============ 用户资料字段定义 ============

@admin_stats_bp.route('/admin/users/<int:user_id>/profile/schema', methods=['GET'])
def get_user_profile_schema(user_id):
    """获取用户资料字段定义"""
    try:
        schema = {
            'fields': [
                {
                    'key': 'username',
                    'label': '用户名',
                    'type': 'text',
                    'required': True,
                    'editable': True
                },
                {
                    'key': 'real_name',
                    'label': '真实姓名',
                    'type': 'text',
                    'required': False,
                    'editable': True
                },
                {
                    'key': 'email',
                    'label': '邮箱',
                    'type': 'email',
                    'required': False,
                    'editable': True
                },
                {
                    'key': 'phone',
                    'label': '手机号',
                    'type': 'tel',
                    'required': False,
                    'editable': True
                },
                {
                    'key': 'avatar_url',
                    'label': '头像',
                    'type': 'image',
                    'required': False,
                    'editable': True
                },
                {
                    'key': 'bio',
                    'label': '个人简介',
                    'type': 'textarea',
                    'required': False,
                    'editable': True
                },
                {
                    'key': 'location',
                    'label': '位置',
                    'type': 'text',
                    'required': False,
                    'editable': True
                },
                {
                    'key': 'website',
                    'label': '网站',
                    'type': 'url',
                    'required': False,
                    'editable': True
                },
                {
                    'key': 'total_lingzhi',
                    'label': '灵值',
                    'type': 'number',
                    'required': False,
                    'editable': False
                },
                {
                    'key': 'status',
                    'label': '状态',
                    'type': 'select',
                    'options': ['active', 'inactive', 'banned'],
                    'required': True,
                    'editable': True
                }
            ]
        }

        return jsonify({
            'success': True,
            'data': schema
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取字段定义失败: {str(e)}'
        }), 500
