"""
公司项目管理路由蓝图
包含项目管理的增删改查功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime

company_projects_bp = Blueprint('company_projects', __name__)

# 导入配置
from config import config
DATABASE = config.DATABASE_PATH

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============ 获取项目列表 ============

@company_projects_bp.route('/admin/projects', methods=['GET'])
def get_projects():
    """获取项目列表"""
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
        status = request.args.get('status', '')

        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 构建查询条件
        where_clause = ""
        params = []
        if status:
            where_clause = "WHERE status = ?"
            params.append(status)

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM company_projects {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # 查询项目列表
        sql = f"""
            SELECT * FROM company_projects
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [page_size, offset])
        projects = cursor.fetchall()

        result = [dict(project) for project in projects]

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
            'message': f'获取项目列表失败: {str(e)}'
        }), 500

# ============ 获取项目详情 ============

@company_projects_bp.route('/admin/projects/<int:project_id>', methods=['GET'])
def get_project_detail(project_id):
    """获取项目详情"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM company_projects WHERE id = ?", (project_id,))
        project = cursor.fetchone()

        if not project:
            conn.close()
            return jsonify({
                'success': False,
                'message': '项目不存在'
            }), 404

        result = dict(project)
        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取项目详情失败: {str(e)}'
        }), 500

# ============ 创建项目 ============

@company_projects_bp.route('/admin/projects', methods=['POST'])
def create_project():
    """创建项目"""
    try:
        data = request.json

        required_fields = ['name', 'description']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field}不能为空'
                }), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO company_projects (
                name, description, category, cover_image, budget,
                start_date, end_date, status, priority, progress,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (
            data.get('name'),
            data.get('description'),
            data.get('category', ''),
            data.get('cover_image', ''),
            data.get('budget', 0),
            data.get('start_date', ''),
            data.get('end_date', ''),
            data.get('status', 'planning'),
            data.get('priority', 'medium'),
            data.get('progress', 0)
        ))

        project_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '项目创建成功',
            'data': {'id': project_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建项目失败: {str(e)}'
        }), 500

# ============ 更新项目 ============

@company_projects_bp.route('/admin/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    """更新项目"""
    try:
        data = request.json

        conn = get_db()
        cursor = conn.cursor()

        # 检查项目是否存在
        cursor.execute("SELECT id FROM company_projects WHERE id = ?", (project_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '项目不存在'
            }), 404

        # 更新项目
        cursor.execute("""
            UPDATE company_projects SET
                name = ?,
                description = ?,
                category = ?,
                cover_image = ?,
                budget = ?,
                start_date = ?,
                end_date = ?,
                status = ?,
                priority = ?,
                progress = ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (
            data.get('name', ''),
            data.get('description', ''),
            data.get('category', ''),
            data.get('cover_image', ''),
            data.get('budget', 0),
            data.get('start_date', ''),
            data.get('end_date', ''),
            data.get('status', ''),
            data.get('priority', ''),
            data.get('progress', 0),
            project_id
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '项目更新成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新项目失败: {str(e)}'
        }), 500

# ============ 删除项目 ============

@company_projects_bp.route('/admin/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    """删除项目"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查项目是否存在
        cursor.execute("SELECT id FROM company_projects WHERE id = ?", (project_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '项目不存在'
            }), 404

        # 删除项目
        cursor.execute("DELETE FROM company_projects WHERE id = ?", (project_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '项目删除成功'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除项目失败: {str(e)}'
        }), 500
