"""
批量导入API
支持数据要素和资源的批量导入
"""

from flask import Blueprint, jsonify, request
from database import get_db
import csv
import io
from datetime import datetime

batch_import_bp = Blueprint('batch_import', __name__)

@batch_import_bp.route('/batch-import', methods=['POST'])
def batch_import():
    """
    批量导入数据
    支持CSV和Excel格式
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                'success': False,
                'message': '未选择文件',
                'data': None
            }), 400

        file = request.files['file']
        import_type = request.form.get('import_type', 'elements')

        if file.filename == '':
            return jsonify({
                'success': False,
                'message': '文件名为空',
                'data': None
            }), 400

        # 检查文件类型
        if not file.filename.endswith('.csv'):
            return jsonify({
                'success': False,
                'message': '仅支持CSV格式文件',
                'data': None
            }), 400

        # 读取文件内容
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))

        results = {
            'total': 0,
            'success': 0,
            'failed': 0,
            'errors': []
        }

        conn = get_db()
        cursor = conn.cursor()

        try:
            # 根据导入类型处理数据
            if import_type == 'elements':
                results = import_elements(cursor, csv_reader)
            elif import_type == 'resources':
                results = import_resources(cursor, csv_reader)
            else:
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '不支持的导入类型',
                    'data': None
                }), 400

            conn.commit()
            conn.close()

            return jsonify({
                'success': True,
                'message': '批量导入完成',
                'data': results
            })
        except Exception as e:
            conn.rollback()
            conn.close()
            raise e

    except Exception as e:
        print(f"批量导入失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'批量导入失败: {str(e)}',
            'data': None
        }), 500


def import_elements(cursor, csv_reader):
    """导入数据化要素"""
    results = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'errors': []
    }

    for row_num, row in enumerate(csv_reader, start=2):  # 从第2行开始（第1行是标题）
        results['total'] += 1

        try:
            element_name = row.get('element_name', '').strip()
            element_type = row.get('element_type', '').strip()
            description = row.get('description', '').strip()
            data_source = row.get('data_source', '').strip()
            processing_method = row.get('processing_method', '').strip()

            # 验证必填字段
            if not element_name:
                results['errors'].append({
                    'row': row_num,
                    'field': 'element_name',
                    'message': '要素名称不能为空'
                })
                results['failed'] += 1
                continue

            if not element_type:
                results['errors'].append({
                    'row': row_num,
                    'field': 'element_type',
                    'message': '要素类型不能为空'
                })
                results['failed'] += 1
                continue

            # 插入数据（使用默认project_id为1）
            cursor.execute("""
                INSERT INTO data_elements
                (project_id, element_name, element_type, description, data_source, processing_method, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, 'pending', ?)
            """, (1, element_name, element_type, description, data_source, processing_method, datetime.now()))

            results['success'] += 1

        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'row': row_num,
                'field': 'unknown',
                'message': str(e)
            })

    return results


def import_resources(cursor, csv_reader):
    """导入资源"""
    results = {
        'total': 0,
        'success': 0,
        'failed': 0,
        'errors': []
    }

    for row_num, row in enumerate(csv_reader, start=2):  # 从第2行开始（第1行是标题）
        results['total'] += 1

        try:
            resource_name = row.get('resource_name', '').strip()
            resource_type = row.get('resource_type', '').strip()
            resource_url = row.get('resource_url', '').strip()
            element_id = row.get('element_id', '').strip()

            # 验证必填字段
            if not resource_name:
                results['errors'].append({
                    'row': row_num,
                    'field': 'resource_name',
                    'message': '资源名称不能为空'
                })
                results['failed'] += 1
                continue

            if not resource_type:
                results['errors'].append({
                    'row': row_num,
                    'field': 'resource_type',
                    'message': '资源类型不能为空'
                })
                results['failed'] += 1
                continue

            if not element_id:
                results['errors'].append({
                    'row': row_num,
                    'field': 'element_id',
                    'message': '关联要素ID不能为空'
                })
                results['failed'] += 1
                continue

            # 验证element_id是否存在
            cursor.execute("SELECT id FROM data_elements WHERE id = ?", (element_id,))
            if not cursor.fetchone():
                results['errors'].append({
                    'row': row_num,
                    'field': 'element_id',
                    'message': f'关联要素ID {element_id} 不存在'
                })
                results['failed'] += 1
                continue

            # 插入数据
            cursor.execute("""
                INSERT INTO data_resources
                (element_id, resource_name, resource_type, resource_url, status, created_at)
                VALUES (?, ?, ?, ?, 'active', ?)
            """, (element_id, resource_name, resource_type, resource_url, datetime.now()))

            results['success'] += 1

        except Exception as e:
            results['failed'] += 1
            results['errors'].append({
                'row': row_num,
                'field': 'unknown',
                'message': str(e)
            })

    return results


# ============ 批量导入模板下载 ============

@batch_import_bp.route('/batch-import/template', methods=['GET'])
def download_template():
    """下载批量导入模板"""
    try:
        import_type = request.args.get('type', 'elements')

        if import_type == 'elements':
            template = """element_name,element_type,description,data_source,processing_method
示例数据要素1,文本类型,这是一个示例描述,数据来源1,处理方法1
示例数据要素2,图片类型,这是另一个示例,数据来源2,处理方法2"""
            filename = 'data_elements_template.csv'
        elif import_type == 'resources':
            template = """resource_name,resource_type,resource_url,element_id
示例资源1,图片类型,https://example.com/image.jpg,1
示例资源2,文档类型,https://example.com/doc.pdf,2"""
            filename = 'data_resources_template.csv'
        else:
            return jsonify({
                'success': False,
                'message': '不支持的模板类型'
            }), 400

        from flask import Response
        return Response(
            template,
            mimetype='text/csv',
            headers={'Content-Disposition': f'attachment; filename={filename}'}
        )

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'下载模板失败: {str(e)}'
        }), 500


# ============ 批量导入历史记录 ============

@batch_import_bp.route('/batch-import/history', methods=['GET'])
def get_import_history():
    """获取批量导入历史记录"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 获取总数
        cursor.execute("SELECT COUNT(*) as total FROM batch_import_history")
        total = cursor.fetchone()['total']

        # 获取历史记录
        cursor.execute("""
            SELECT
                id, import_type, file_name, total_count,
                success_count, failed_count, created_at
            FROM batch_import_history
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (page_size, offset))

        history = []
        for row in cursor.fetchall():
            history.append({
                'id': row['id'],
                'importType': row['import_type'],
                'fileName': row['file_name'],
                'totalCount': row['total_count'],
                'successCount': row['success_count'],
                'failedCount': row['failed_count'],
                'createdAt': row['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取历史记录成功',
            'data': history,
            'total': total,
            'page': page,
            'page_size': page_size
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取历史记录失败: {str(e)}'
        }), 500
