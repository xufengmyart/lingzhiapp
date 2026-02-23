"""
角色管理路由蓝图
包含角色和权限的增删改查功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
import json

role_management_bp = Blueprint('role_management', __name__)

# 导入配置
from config import config
DATABASE = config.DATABASE_PATH

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============ 获取角色列表 ============

@role_management_bp.route('/admin/roles', methods=['GET'])
def get_roles():
    """获取角色列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT r.*
            FROM roles r
            ORDER BY r.created_at DESC
        """)
        roles = cursor.fetchall()

        result = []
        for role in roles:
            role_dict = dict(role)
            # 解析权限
            if role_dict.get('permissions'):
                role_dict['permissions'] = json.loads(role_dict['permissions'])
            else:
                role_dict['permissions'] = []
            # 添加用户数量（暂不支持统计）
            role_dict['user_count'] = 0
            result.append(role_dict)

        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取角色列表失败: {str(e)}'
        }), 500

# ============ 获取角色详情 ============

@role_management_bp.route('/admin/roles/<int:role_id>', methods=['GET'])
def get_role_detail(role_id):
    """获取角色详情"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM roles WHERE id = ?", (role_id,))
        role = cursor.fetchone()

        if not role:
            conn.close()
            return jsonify({
                'success': False,
                'message': '角色不存在'
            }), 404

        result = dict(role)
        # 解析权限
        if result.get('permissions'):
            result['permissions'] = json.loads(result['permissions'])
        else:
            result['permissions'] = []

        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取角色详情失败: {str(e)}'
        }), 500

# ============ 创建角色 ============

@role_management_bp.route('/admin/roles', methods=['POST'])
def create_role():
    """创建角色"""
    try:
        data = request.json

        if not data.get('name'):
            return jsonify({
                'success': False,
                'message': '角色名称不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查角色名是否已存在
        cursor.execute("SELECT id FROM roles WHERE name = ?", (data.get('name'),))
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '角色名称已存在'
            }), 400

        # 序列化权限
        permissions_json = json.dumps(data.get('permissions', []))

        cursor.execute("""
            INSERT INTO roles (name, description, permissions, status, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            data.get('name'),
            data.get('description', ''),
            permissions_json,
            data.get('status', 'active')
        ))

        role_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '角色创建成功',
            'data': {'id': role_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建角色失败: {str(e)}'
        }), 500

# ============ 更新角色 ============

@role_management_bp.route('/admin/roles/<int:role_id>', methods=['PUT'])
def update_role(role_id):
    """更新角色"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # 检查角色是否存在
        cursor.execute("SELECT id FROM roles WHERE id = ?", (role_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '角色不存在'
            }), 404

        # 检查角色名是否与其他角色重复
        cursor.execute(
            "SELECT id FROM roles WHERE name = ? AND id != ?",
            (data.get('name'), role_id)
        )
        if cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '角色名称已存在'
            }), 400

        # 序列化权限
        permissions_json = json.dumps(data.get('permissions', []))

        # 更新角色
        cursor.execute("""
            UPDATE roles SET
                name = ?,
                description = ?,
                permissions = ?,
                status = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data.get('name', ''),
            data.get('description', ''),
            permissions_json,
            data.get('status', ''),
            role_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '角色更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新角色失败: {str(e)}'
        }), 500

# ============ 删除角色 ============

@role_management_bp.route('/admin/roles/<int:role_id>', methods=['DELETE'])
def delete_role(role_id):
    """删除角色"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查角色是否存在
        cursor.execute("SELECT id FROM roles WHERE id = ?", (role_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '角色不存在'
            }), 404

        # 暂时不检查用户使用情况（users表没有role字段）
        # TODO: 添加role字段后启用此检查
        # cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = ?", (role['name'],))
        # user_count = cursor.fetchone()['count']
        # if user_count > 0:
        #     conn.close()
        #     return jsonify({
        #         'success': False,
        #         'message': f'该角色正在被{user_count}个用户使用，无法删除'
        #     }), 400

        # 删除角色
        cursor.execute("DELETE FROM roles WHERE id = ?", (role_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '角色删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除角色失败: {str(e)}'
        }), 500

# ============ 更新角色权限 ============

@role_management_bp.route('/admin/roles/<int:role_id>/permissions', methods=['PUT'])
def update_role_permissions(role_id):
    """更新角色权限"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # 检查角色是否存在
        cursor.execute("SELECT id FROM roles WHERE id = ?", (role_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '角色不存在'
            }), 404

        # 序列化权限
        permissions_json = json.dumps(data.get('permissions', []))

        # 更新权限
        cursor.execute("""
            UPDATE roles SET
                permissions = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (permissions_json, role_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '角色权限更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新角色权限失败: {str(e)}'
        }), 500
