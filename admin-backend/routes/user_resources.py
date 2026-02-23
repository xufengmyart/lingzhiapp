"""
用户资源管理路由蓝图
包含用户资源的增删改查功能
"""

from flask import Blueprint, request, jsonify
import sqlite3

user_resources_bp = Blueprint('user_resources', __name__)

# 导入配置
from config import config
DATABASE = config.DATABASE_PATH

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============ 获取资源列表 ============

@user_resources_bp.route('/admin/user-resources', methods=['GET'])
def get_resources():
    """获取资源列表"""
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
        category = request.args.get('category', '')
        user_id = request.args.get('userId', '')
        status = request.args.get('status', '')

        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 构建查询条件
        where_conditions = []
        params = []

        if category:
            where_conditions.append("category = ?")
            params.append(category)

        if user_id:
            where_conditions.append("user_id = ?")
            params.append(user_id)

        if status:
            where_conditions.append("status = ?")
            params.append(status)

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM user_resources {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # 查询资源列表
        sql = f"""
            SELECT ur.*, u.username as user_name
            FROM user_resources ur
            LEFT JOIN users u ON ur.user_id = u.id
            {where_clause}
            ORDER BY ur.created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [page_size, offset])
        resources = cursor.fetchall()

        result = [dict(resource) for resource in resources]

        conn.close()

        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'total': total,
                'totalPages': (total + page_size - 1) // page_size
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取资源列表失败: {str(e)}'
        }), 500

# ============ 获取资源详情 ============

@user_resources_bp.route('/admin/user-resources/<int:resource_id>', methods=['GET'])
def get_resource_detail(resource_id):
    """获取资源详情"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT ur.*, u.username as user_name
            FROM user_resources ur
            LEFT JOIN users u ON ur.user_id = u.id
            WHERE ur.id = ?
        """, (resource_id,))
        resource = cursor.fetchone()

        if not resource:
            conn.close()
            return jsonify({
                'success': False,
                'message': '资源不存在'
            }), 404

        result = dict(resource)
        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取资源详情失败: {str(e)}'
        }), 500

# ============ 创建资源 ============

@user_resources_bp.route('/admin/user-resources', methods=['POST'])
def create_resource():
    """创建资源"""
    try:
        data = request.json

        required_fields = ['title', 'content', 'user_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field}不能为空'
                }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT id FROM users WHERE id = ?", (data.get('user_id'),))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        cursor.execute("""
            INSERT INTO user_resources (
                user_id, title, content, category, cover_image,
                file_url, file_type, file_size, tags, price,
                status, is_public, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            data.get('user_id'),
            data.get('title'),
            data.get('content'),
            data.get('category', ''),
            data.get('cover_image', ''),
            data.get('file_url', ''),
            data.get('file_type', ''),
            data.get('file_size', 0),
            data.get('tags', ''),
            data.get('price', 0),
            data.get('status', 'draft'),
            data.get('is_public', 0)
        ))

        resource_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '资源创建成功',
            'data': {'id': resource_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建资源失败: {str(e)}'
        }), 500

# ============ 更新资源 ============

@user_resources_bp.route('/admin/user-resources/<int:resource_id>', methods=['PUT'])
def update_resource(resource_id):
    """更新资源"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # 检查资源是否存在
        cursor.execute("SELECT id FROM user_resources WHERE id = ?", (resource_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '资源不存在'
            }), 404

        # 更新资源
        cursor.execute("""
            UPDATE user_resources SET
                title = ?,
                content = ?,
                category = ?,
                cover_image = ?,
                file_url = ?,
                file_type = ?,
                file_size = ?,
                tags = ?,
                price = ?,
                status = ?,
                is_public = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data.get('title', ''),
            data.get('content', ''),
            data.get('category', ''),
            data.get('cover_image', ''),
            data.get('file_url', ''),
            data.get('file_type', ''),
            data.get('file_size', 0),
            data.get('tags', ''),
            data.get('price', 0),
            data.get('status', ''),
            data.get('is_public', 0),
            resource_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '资源更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新资源失败: {str(e)}'
        }), 500

# ============ 删除资源 ============

@user_resources_bp.route('/admin/user-resources/<int:resource_id>', methods=['DELETE'])
def delete_resource(resource_id):
    """删除资源"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查资源是否存在
        cursor.execute("SELECT id FROM user_resources WHERE id = ?", (resource_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '资源不存在'
            }), 404

        # 删除资源
        cursor.execute("DELETE FROM user_resources WHERE id = ?", (resource_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '资源删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除资源失败: {str(e)}'
        }), 500

# ============ 批量审核资源 ============

@user_resources_bp.route('/admin/user-resources/batch-approve', methods=['POST'])
def batch_approve_resources():
    """批量审核资源"""
    try:
        data = request.json
        resource_ids = data.get('resourceIds', [])
        action = data.get('action', 'approve')  # approve 或 reject

        if not resource_ids:
            return jsonify({
                'success': False,
                'message': '请选择要审核的资源'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 批量更新状态
        if action == 'approve':
            status = 'approved'
        else:
            status = 'rejected'

        placeholders = ','.join(['?'] * len(resource_ids))
        cursor.execute(
            f"UPDATE user_resources SET status = ? WHERE id IN ({placeholders})",
            [status] + resource_ids
        )

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'已{action} {affected_rows} 个资源'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'批量审核失败: {str(e)}'
        }), 500
