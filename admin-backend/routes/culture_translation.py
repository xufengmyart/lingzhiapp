"""
文化转译 API 蓝图
提供文化转译项目的开始转译、开始转译流程等功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime
import json
from functools import wraps
import sys
import os
import jwt

# 导入 LLM 客户端
try:
    from coze_coding_dev_sdk import LLMClient
    from coze_coding_utils.runtime_ctx.context import new_context
    from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("⚠️  coze_coding_dev_sdk 未安装，文化转译功能将不可用")

# 导入配置
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

culture_translation_bp = Blueprint('culture_translation', __name__, url_prefix='/api/culture/translation')

DATABASE = config.DATABASE_PATH
JWT_SECRET_KEY = config.JWT_SECRET_KEY

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def get_text_content(content):
    """安全提取文本内容"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        if content and isinstance(content[0], str):
            return " ".join(content)
        else:
            text_parts = [item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"]
            return " ".join(text_parts)
    return str(content)

# ==================== 认证中间件 ====================

def require_auth(f):
    """需要登录认证的装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')

        if not auth_header:
            return jsonify({
                'success': False,
                'message': '未提供认证信息'
            }), 401

        if not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'message': '认证格式错误'
            }), 401

        token = auth_header[7:]  # 去掉 'Bearer ' 前缀

        try:
            # 使用 JWT 验证 token
            payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('user_id')
            
            if not user_id:
                return jsonify({
                    'success': False,
                    'message': 'Token中缺少用户ID'
                }), 401

            # 验证用户是否存在
            conn = get_db_connection()
            user = conn.execute(
                'SELECT id, username, email FROM users WHERE id = ?',
                (user_id,)
            ).fetchone()
            conn.close()

            if not user:
                return jsonify({
                    'success': False,
                    'message': '用户不存在'
                }), 401

            # 将用户信息添加到request中
            request.current_user = dict(user)

        except jwt.ExpiredSignatureError:
            return jsonify({
                'success': False,
                'message': 'Token已过期'
            }), 401
        except jwt.InvalidTokenError:
            return jsonify({
                'success': False,
                'message': 'Token无效'
            }), 401
        except Exception as e:
            return jsonify({
                'success': False,
                'message': '认证失败'
            }), 401

        return f(*args, **kwargs)

    return decorated_function

# ==================== 转译项目相关接口 ====================

@culture_translation_bp.route('/projects', methods=['GET'])
def get_translation_projects():
    """获取所有转译项目列表"""
    try:
        conn = get_db_connection()

        projects = conn.execute(
            '''SELECT id, project_code, title, description, project_type, category,
                      difficulty_level, status, base_reward, created_at
               FROM translation_projects
               WHERE status = 'active'
               ORDER BY created_at DESC'''
        ).fetchall()

        conn.close()

        project_list = []
        for project in projects:
            project_list.append({
                'id': project['id'],
                'project_code': project['project_code'],
                'title': project['title'],
                'description': project['description'],
                'project_type': project['project_type'],
                'category': project['category'],
                'difficulty_level': project['difficulty_level'],
                'status': project['status'],
                'base_reward': project['base_reward'],
                'created_at': project['created_at']
            })

        return jsonify({
            'success': True,
            'data': project_list,
            'count': len(project_list)
        })

    except Exception as e:
        print(f"获取转译项目失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取转译项目失败: {str(e)}'
        }), 500

@culture_translation_bp.route('/projects/<project_code>', methods=['GET'])
def get_translation_project_detail(project_code):
    """获取转译项目详情"""
    try:
        conn = get_db_connection()

        project = conn.execute(
            '''SELECT * FROM translation_projects
               WHERE project_code = ? AND status = 'active' ''',
            (project_code,)
        ).fetchone()

        if not project:
            conn.close()
            return jsonify({
                'success': False,
                'message': '项目不存在或已下架'
            }), 404

        # 获取项目的相关任务数量
        task_count = conn.execute(
            'SELECT COUNT(*) as count FROM translation_tasks WHERE project_id = ?',
            (project['id'],)
        ).fetchone()

        conn.close()

        project_data = dict(project)
        project_data['requirements'] = json.loads(project_data['requirements']) if project_data.get('requirements') else {}
        project_data['task_count'] = task_count['count']

        return jsonify({
            'success': True,
            'data': project_data
        })

    except Exception as e:
        print(f"获取项目详情失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取项目详情失败: {str(e)}'
        }), 500

# ==================== 转译任务相关接口 ====================

@culture_translation_bp.route('/tasks', methods=['GET'])
def get_translation_tasks():
    """获取转译任务列表"""
    try:
        project_code = request.args.get('project_code')
        status = request.args.get('status', 'available')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        conn = get_db_connection()

        # 构建查询条件
        conditions = ['t.status = ?']
        params = [status]

        if project_code:
            conditions.append('t.project_id = (SELECT id FROM translation_projects WHERE project_code = ?)')
            params.append(project_code)

        where_clause = ' AND '.join(conditions)

        # 获取总数
        total_count = conn.execute(
            f'''SELECT COUNT(*) as count FROM translation_tasks t WHERE {where_clause}''',
            params
        ).fetchone()

        # 获取任务列表
        tasks = conn.execute(
            f'''SELECT t.id, t.task_code, t.title, t.description, t.source_type, t.target_type,
                      t.reward, t.status as task_status, t.created_at,
                      p.title as project_title, p.project_type
               FROM translation_tasks t
               LEFT JOIN translation_projects p ON t.project_id = p.id
               WHERE {where_clause}
               ORDER BY t.created_at DESC
               LIMIT ? OFFSET ?''',
            params + [page_size, (page - 1) * page_size]
        ).fetchall()

        conn.close()

        task_list = []
        for task in tasks:
            task_list.append({
                'id': task['id'],
                'task_code': task['task_code'],
                'title': task['title'],
                'description': task['description'],
                'source_type': task['source_type'],
                'target_type': task['target_type'],
                'project_title': task['project_title'],
                'project_type': task['project_type'],
                'reward': task['reward'],
                'status': task['task_status'],
                'created_at': task['created_at']
            })

        return jsonify({
            'success': True,
            'data': task_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total_count['count'],
                'total_pages': (total_count['count'] + page_size - 1) // page_size
            }
        })

    except Exception as e:
        print(f"获取转译任务失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取转译任务失败: {str(e)}'
        }), 500

@culture_translation_bp.route('/tasks/<int:task_id>', methods=['GET'])
def get_translation_task_detail(task_id):
    """获取转译任务详情"""
    try:
        conn = get_db_connection()

        task = conn.execute(
            '''SELECT t.*, p.title as project_title, p.project_code,
                      p.project_type, p.requirements as project_requirements
               FROM translation_tasks t
               LEFT JOIN translation_projects p ON t.project_id = p.id
               WHERE t.id = ?''',
            (task_id,)
        ).fetchone()

        if not task:
            conn.close()
            return jsonify({
                'success': False,
                'message': '任务不存在'
            }), 404

        conn.close()

        task_data = dict(task)
        if task_data.get('project_requirements'):
            try:
                task_data['project_requirements'] = json.loads(task_data['project_requirements'])
            except:
                task_data['project_requirements'] = {}

        return jsonify({
            'success': True,
            'data': task_data
        })

    except Exception as e:
        print(f"获取任务详情失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取任务详情失败: {str(e)}'
        }), 500

# ==================== 开始转译接口 ====================

@culture_translation_bp.route('/start', methods=['POST'])
@require_auth
def start_translation():
    """开始转译 - 创建转译作品记录"""
    try:
        data = request.get_json()

        task_id = data.get('task_id')
        original_content = data.get('original_content')

        if not task_id:
            return jsonify({
                'success': False,
                'message': '缺少任务ID'
            }), 400

        user_id = request.current_user['id']

        conn = get_db_connection()

        # 验证任务是否存在且可用
        task = conn.execute(
            'SELECT * FROM translation_tasks WHERE id = ? AND status = ?',
            (task_id, 'available')
        ).fetchone()

        if not task:
            conn.close()
            return jsonify({
                'success': False,
                'message': '任务不存在或已被领取'
            }), 404

        # 更新任务状态
        conn.execute(
            'UPDATE translation_tasks SET status = ? WHERE id = ?',
            ('in_progress', task_id)
        )

        # 创建转译作品记录
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO translation_works
               (task_id, user_id, username, original_content, content_type, status)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (task_id, user_id, request.current_user['username'],
             original_content or '', task['source_type'], 'pending')
        )
        work_id = cursor.lastrowid

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '转译任务已领取，请开始创作',
            'data': {
                'work_id': work_id,
                'task_id': task_id,
                'task_title': task['title'],
                'task_description': task['description'],
                'source_content': task['source_content'],
                'source_type': task['source_type'],
                'target_type': task['target_type'],
                'translation_prompt': task['translation_prompt'],
                'reward': task['reward']
            }
        })

    except Exception as e:
        print(f"开始转译失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'开始转译失败: {str(e)}'
        }), 500

# ==================== 开始转译流程接口 ====================

@culture_translation_bp.route('/process/start', methods=['POST'])
@require_auth
def start_translation_process():
    """开始转译流程 - 创建转译流程并执行AI辅助转译"""
    try:
        if not LLM_AVAILABLE:
            return jsonify({
                'success': False,
                'message': 'AI转译功能暂不可用，请联系管理员'
            }), 503

        data = request.get_json()

        work_id = data.get('work_id')
        use_ai_assist = data.get('use_ai_assist', True)

        if not work_id:
            return jsonify({
                'success': False,
                'message': '缺少作品ID'
            }), 400

        user_id = request.current_user['id']

        conn = get_db_connection()

        # 验证作品是否存在
        work = conn.execute(
            '''SELECT w.*, t.source_content, t.translation_prompt,
                      t.target_type, p.title as project_title
               FROM translation_works w
               LEFT JOIN translation_tasks t ON w.task_id = t.id
               LEFT JOIN translation_projects p ON t.project_id = p.id
               WHERE w.id = ? AND w.user_id = ? AND w.status = ?''',
            (work_id, user_id, 'pending')
        ).fetchone()

        if not work:
            conn.close()
            return jsonify({
                'success': False,
                'message': '作品不存在或状态不正确'
            }), 404

        # 创建转译流程记录
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO translation_processes
               (work_id, process_type, current_step, steps_pending, status, progress)
               VALUES (?, ?, ?, ?, ?, ?)''',
            (work_id, 'translate', 'input', '["input", "ai_process", "output"]', 'pending', 0)
        )
        process_id = cursor.lastrowid

        # 定义流程步骤
        steps = [
            {
                'step_name': 'input_analysis',
                'step_type': 'input',
                'step_order': 1,
                'input_data': {
                    'source_content': work['original_content'] or work['source_content'],
                    'translation_prompt': work['translation_prompt'],
                    'target_type': work['target_type']
                }
            },
            {
                'step_name': 'ai_translation',
                'step_type': 'ai_process',
                'step_order': 2,
                'input_data': {}
            },
            {
                'step_name': 'output_generation',
                'step_type': 'output',
                'step_order': 3,
                'input_data': {}
            }
        ]

        # 更新流程状态为进行中
        conn.execute(
            'UPDATE translation_processes SET status = ?, current_step = ? WHERE id = ?',
            ('in_progress', 'input_analysis', process_id)
        )

        # 插入步骤记录
        for step in steps:
            conn.execute(
                '''INSERT INTO translation_process_steps
                   (process_id, step_name, step_type, step_order, input_data, step_status)
                   VALUES (?, ?, ?, ?, ?, ?)''',
                (process_id, step['step_name'], step['step_type'],
                 step['step_order'], json.dumps(step['input_data']), 'pending')
            )

        conn.commit()

        # 如果使用AI辅助，执行AI转译
        ai_translation_result = None
        ai_model = None

        if use_ai_assist and work['original_content']:
            try:
                # 构建AI转译提示
                system_prompt = f"""你是专业的文化转译专家，擅长将传统文化内容转译为现代形式。

你的任务是：
1. 深入理解传统文化的内涵和精神
2. 保持文化的原真性和韵味
3. 用现代语言和形式重新表达
4. 确保转译内容具有传播价值和艺术性

项目类型：{work['target_type']}
项目：{work['project_title']}

请根据以上要求，对用户提供的原始内容进行专业转译。"""

                user_message = f"""原始内容：
{work['original_content']}

{work['translation_prompt'] or ''}

请提供转译后的内容。"""

                # 调用AI模型
                ctx = new_context(method="translate")
                client = LLMClient(ctx=ctx)

                messages = [
                    SystemMessage(content=system_prompt),
                    HumanMessage(content=user_message)
                ]

                # 使用多模态模型，支持文本、图像等
                response = client.invoke(
                    messages=messages,
                    model="doubao-seed-1-8-251228",
                    temperature=0.8,
                    max_completion_tokens=4096
                )

                ai_translation_result = get_text_content(response.content)
                ai_model = "doubao-seed-1-8-251228"

                # 更新AI转译步骤
                conn.execute(
                    '''UPDATE translation_process_steps
                       SET step_status = ?, output_data = ?, ai_model = ?
                       WHERE process_id = ? AND step_name = ?''',
                    ('completed', json.dumps({'translation': ai_translation_result}), ai_model,
                     process_id, 'ai_translation')
                )

                # 标记作品为AI辅助
                conn.execute(
                    'UPDATE translation_works SET ai_assisted = ?, ai_model = ? WHERE id = ?',
                    (1, ai_model, work_id)
                )

            except Exception as ai_error:
                print(f"AI转译失败: {ai_error}")
                # AI转译失败不影响流程继续
                ai_translation_result = None

        # 更新作品状态
        if ai_translation_result:
            conn.execute(
                '''UPDATE translation_works
                   SET translated_content = ?, status = ?
                   WHERE id = ?''',
                (ai_translation_result, 'under_review', work_id)
            )
        else:
            conn.execute(
                'UPDATE translation_works SET status = ? WHERE id = ?',
                ('under_review', work_id)
            )

        # 更新流程状态为完成
        conn.execute(
            '''UPDATE translation_processes
               SET status = ?, current_step = ?, progress = ?,
                   steps_completed = ?, steps_pending = ?,
                   step_data = ?
               WHERE id = ?''',
            ('completed', 'output_generation', 100,
             json.dumps(['input_analysis', 'ai_translation']),
             json.dumps([]),
             json.dumps({
                 'input_analysis': {'status': 'completed'},
                 'ai_translation': {
                     'status': 'completed' if ai_translation_result else 'failed',
                     'result': ai_translation_result,
                     'model': ai_model
                 },
                 'output_generation': {'status': 'completed'}
             }),
             process_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '转译流程已完成',
            'data': {
                'work_id': work_id,
                'process_id': process_id,
                'ai_assisted': use_ai_assist,
                'ai_translation': ai_translation_result,
                'ai_model': ai_model,
                'status': 'completed',
                'next_step': 'review'
            }
        })

    except Exception as e:
        print(f"转译流程失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'转译流程失败: {str(e)}'
        }), 500

# ==================== 提交转译作品接口 ====================

@culture_translation_bp.route('/works/<int:work_id>/submit', methods=['POST'])
@require_auth
def submit_translation_work(work_id):
    """提交转译作品"""
    try:
        data = request.get_json()

        translated_content = data.get('translated_content')
        submission_notes = data.get('submission_notes', '')

        if not translated_content:
            return jsonify({
                'success': False,
                'message': '请提供转译内容'
            }), 400

        user_id = request.current_user['id']

        conn = get_db_connection()

        # 验证作品是否存在且属于该用户
        work = conn.execute(
            'SELECT * FROM translation_works WHERE id = ? AND user_id = ?',
            (work_id, user_id)
        ).fetchone()

        if not work:
            conn.close()
            return jsonify({
                'success': False,
                'message': '作品不存在'
            }), 404

        # 更新作品信息
        conn.execute(
            '''UPDATE translation_works
               SET translated_content = ?, submission_notes = ?, status = ?
               WHERE id = ?''',
            (translated_content, submission_notes, 'under_review', work_id)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '作品已提交，等待审核',
            'data': {
                'work_id': work_id,
                'status': 'under_review'
            }
        })

    except Exception as e:
        print(f"提交作品失败: {e}")
        return jsonify({
            'success': False,
            'message': f'提交作品失败: {str(e)}'
        }), 500

# ==================== 获取转译记录接口 ====================

@culture_translation_bp.route('/works', methods=['GET'])
@require_auth
def get_translation_works():
    """获取用户的转译作品列表"""
    try:
        user_id = request.current_user['id']
        status = request.args.get('status')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))

        conn = get_db_connection()

        # 构建查询条件
        conditions = ['w.user_id = ?']
        params = [user_id]

        if status:
            conditions.append('w.status = ?')
            params.append(status)

        where_clause = ' AND '.join(conditions)

        # 获取总数
        total_count = conn.execute(
            f'''SELECT COUNT(*) as count
               FROM translation_works w
               WHERE {where_clause}''',
            params
        ).fetchone()

        # 获取作品列表
        works = conn.execute(
            f'''SELECT w.*, t.title as task_title, p.title as project_title, p.project_code
               FROM translation_works w
               LEFT JOIN translation_tasks t ON w.task_id = t.id
               LEFT JOIN translation_projects p ON t.project_id = p.id
               WHERE {where_clause}
               ORDER BY w.created_at DESC
               LIMIT ? OFFSET ?''',
            params + [page_size, (page - 1) * page_size]
        ).fetchall()

        conn.close()

        work_list = []
        for work in works:
            work_list.append({
                'id': work['id'],
                'task_title': work['task_title'],
                'project_title': work['project_title'],
                'project_code': work['project_code'],
                'original_content': work['original_content'],
                'translated_content': work['translated_content'],
                'content_type': work['content_type'],
                'ai_assisted': bool(work['ai_assisted']),
                'ai_model': work['ai_model'],
                'status': work['status'],
                'review_score': work['review_score'],
                'lingzhi_reward': work['lingzhi_reward'],
                'created_at': work['created_at'],
                'updated_at': work['updated_at']
            })

        return jsonify({
            'success': True,
            'data': work_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total_count['count'],
                'total_pages': (total_count['count'] + page_size - 1) // page_size
            }
        })

    except Exception as e:
        print(f"获取转译作品失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取转译作品失败: {str(e)}'
        }), 500

# ==================== 获取转译进度接口 ====================

@culture_translation_bp.route('/processes/<int:process_id>/status', methods=['GET'])
@require_auth
def get_translation_process_status(process_id):
    """获取转译流程状态"""
    try:
        user_id = request.current_user['id']

        conn = get_db_connection()

        # 验证流程是否存在
        process = conn.execute(
            '''SELECT p.*, w.user_id
               FROM translation_processes p
               LEFT JOIN translation_works w ON p.work_id = w.id
               WHERE p.id = ? AND w.user_id = ?''',
            (process_id, user_id)
        ).fetchone()

        if not process:
            conn.close()
            return jsonify({
                'success': False,
                'message': '流程不存在'
            }), 404

        # 获取步骤详情
        steps = conn.execute(
            '''SELECT step_name, step_type, step_status, step_order, error_message
               FROM translation_process_steps
               WHERE process_id = ?
               ORDER BY step_order''',
            (process_id,)
        ).fetchall()

        conn.close()

        step_list = []
        for step in steps:
            step_list.append({
                'step_name': step['step_name'],
                'step_type': step['step_type'],
                'step_status': step['step_status'],
                'step_order': step['step_order'],
                'error_message': step['error_message']
            })

        return jsonify({
            'success': True,
            'data': {
                'process_id': process['id'],
                'work_id': process['work_id'],
                'process_type': process['process_type'],
                'current_step': process['current_step'],
                'status': process['status'],
                'progress': process['progress'],
                'steps': step_list,
                'error_message': process['error_message'],
                'created_at': process['created_at'],
                'updated_at': process['updated_at']
            }
        })

    except Exception as e:
        print(f"获取流程状态失败: {e}")
        return jsonify({
            'success': False,
            'message': f'获取流程状态失败: {str(e)}'
        }), 500
