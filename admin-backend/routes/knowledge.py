"""
知识库 API 蓝图
提供知识库管理、文档管理、搜索等功能
"""

from flask import Blueprint, request, jsonify, send_file
import sqlite3
from datetime import datetime
import json
import os

# 导入配置
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

knowledge_bp = Blueprint('knowledge', __name__, url_prefix='/api')

DATABASE = config.DATABASE_PATH

# 测试路由 - 用于验证知识库API是否正常工作
@knowledge_bp.route('/knowledge/test', methods=['GET'])
def test_knowledge_api():
    """
    测试知识库API是否正常工作
    响应: { success: true, message: '知识库API正常' }
    """
    try:
        return jsonify({
            'success': True,
            'message': '知识库API正常',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def verify_token(token):
    """验证 JWT token"""
    try:
        import jwt
        from config import config
        payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
        return payload
    except:
        return None

def is_admin(username):
    """检查用户是否是管理员（基于用户名）"""
    try:
        # 特殊处理：admin 用户直接拥有管理员权限
        if username == 'admin':
            return True
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM admins WHERE username = ?', (username,))
        admin = cursor.fetchone()
        conn.close()
        return admin is not None
    except Exception as e:
        print(f"[权限检查] 检查管理员权限错误: {e}")
        return False


# ==================== 知识库管理 ====================

@knowledge_bp.route('/knowledge', methods=['GET'])
def list_knowledge():
    """
    获取知识库列表
    响应: { success: true, data: [...] }
    """
    print("="*60)
    print(f"[DEBUG] list_knowledge() called at {datetime.now()}")
    print("="*60)
    
    try:
        print("[DEBUG] 开始处理请求...")
        
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        print(f"[DEBUG] Token长度: {len(token) if token else 0}")
        
        user_payload = verify_token(token) if token else None
        user_id = user_payload.get('user_id') if user_payload else None
        print(f"[DEBUG] user_id: {user_id}")

        print("[DEBUG] 连接数据库...")
        conn = get_db_connection()
        print("[DEBUG] 数据库连接成功")

        # 检查表结构中是否有 is_public 字段
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(knowledge_bases)")
        columns = {col[1] for col in cursor.fetchall()}
        has_is_public = 'is_public' in columns
        print(f"[DEBUG] has_is_public: {has_is_public}")

        try:
            print("[DEBUG] 开始查询知识库...")
            # 如果有用户，获取用户的知识库（包括公开的和自己的）
            if user_id:
                if has_is_public:
                    knowledge_items = conn.execute('''
                        SELECT kb.*, COUNT(kd.id) as doc_count,
                               CASE WHEN ukb.user_id IS NOT NULL THEN 1 ELSE 0 END as is_favorite
                        FROM knowledge_bases kb
                        LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
                        LEFT JOIN user_knowledge_bases ukb ON kb.id = ukb.knowledge_base_id AND ukb.user_id = ?
                        WHERE kb.is_public = 1 OR kb.created_by = ?
                        GROUP BY kb.id
                        ORDER BY kb.created_at DESC
                        LIMIT 50
                    ''', (user_id, user_id)).fetchall()
                else:
                    # 没有 is_public 字段，返回所有知识库
                    knowledge_items = conn.execute('''
                        SELECT kb.*, COUNT(kd.id) as doc_count,
                               CASE WHEN ukb.user_id IS NOT NULL THEN 1 ELSE 0 END as is_favorite
                        FROM knowledge_bases kb
                        LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
                        LEFT JOIN user_knowledge_bases ukb ON kb.id = ukb.knowledge_base_id AND ukb.user_id = ?
                        GROUP BY kb.id
                        ORDER BY kb.created_at DESC
                        LIMIT 50
                    ''', (user_id,)).fetchall()
            else:
                # 没有用户，只获取公开的知识库
                if has_is_public:
                    knowledge_items = conn.execute('''
                        SELECT kb.*, COUNT(kd.id) as doc_count, 0 as is_favorite
                        FROM knowledge_bases kb
                        LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
                        WHERE kb.is_public = 1
                        GROUP BY kb.id
                        ORDER BY kb.created_at DESC
                        LIMIT 50
                    ''').fetchall()
                else:
                    # 没有 is_public 字段，返回前 50 个知识库
                    knowledge_items = conn.execute('''
                        SELECT kb.*, COUNT(kd.id) as doc_count, 0 as is_favorite
                        FROM knowledge_bases kb
                        LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
                        GROUP BY kb.id
                        ORDER BY kb.created_at DESC
                        LIMIT 50
                    ''').fetchall()

            print(f"[DEBUG] 查询成功，获取到 {len(knowledge_items)} 个知识库")
        except Exception as query_error:
            print(f"[DEBUG] 数据库查询错误: {query_error}")
            import traceback
            traceback.print_exc()
            raise query_error

        print("[DEBUG] 关闭数据库连接...")
        conn.close()
        print("[DEBUG] 数据库连接已关闭")

        print("[DEBUG] 开始处理知识库项...")
        items = []
        for idx, kb in enumerate(knowledge_items):
            try:
                # 安全获取字段，如果不存在则使用默认值
                kb_dict = dict(kb)
                item = {
                    'id': str(kb_dict.get('id', '')),
                    'title': str(kb_dict.get('name', '')),
                    'content': str(kb_dict.get('description', '')),
                    'category': 'culture' if kb_dict.get('name', '').startswith('西安') else 'general',
                    'tags': [],
                    'created_at': str(kb_dict.get('created_at', '')),
                    'updated_at': str(kb_dict.get('updated_at', '')),
                    'is_favorite': bool(kb_dict.get('is_favorite', 0)),
                    'document_count': int(kb_dict.get('doc_count', 0)),
                    'view_count': int(kb_dict.get('view_count', 0)),
                    'search_count': int(kb_dict.get('search_count', 0)),
                    'download_count': int(kb_dict.get('download_count', 0)),
                }
                items.append(item)
                if idx < 3:  # 只打印前3个
                    print(f"[DEBUG] 处理知识库 {idx+1}: {item['title']}")
            except Exception as item_error:
                print(f"[DEBUG] 处理知识库项 {idx+1} 错误: {item_error}")
                import traceback
                traceback.print_exc()
                continue

        print(f"[DEBUG] 成功处理 {len(items)} 个知识库项")
        print(f"[DEBUG] 准备返回响应...")
        
        response = {
            'success': True,
            'data': items
        }
        
        print(f"[DEBUG] 响应准备完成，返回...")
        print("="*60)
        return jsonify(response)

    except Exception as e:
        print(f"[DEBUG] 获取知识库列表错误: {e}")
        import traceback
        traceback.print_exc()
        print("="*60)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_bp.route('/knowledge', methods=['POST'])
def create_knowledge():
    """
    创建知识库
    请求体: { name, description, type?, icon? }
    响应: { success: true, data: { id, name, ... } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token) if token else None

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401

        user_id = user_payload.get('user_id')
        data = request.get_json()

        name = data.get('name')
        description = data['description'] if 'description' in data.keys() else ''
        kb_type = data['type'] if 'type' in data.keys() else 'general'
        icon = data['icon'] if 'icon' in data.keys() else ''

        if not name:
            return jsonify({
                'success': False,
                'error': '知识库名称不能为空'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO knowledge_bases (name, description, type, icon, created_by, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (name, description, kb_type, icon, user_id, datetime.now().isoformat(), datetime.now().isoformat()))

        kb_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': kb_id,
                'name': name,
                'description': description,
                'type': kb_type,
                'icon': icon
            }
        })

    except Exception as e:
        print(f"创建知识库错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_bp.route('/knowledge/<int:kb_id>/favorite', methods=['POST'])
def favorite_knowledge(kb_id):
    """
    收藏知识库
    响应: { success: true }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token) if token else None

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 检查是否已收藏
        existing = conn.execute(
            'SELECT * FROM user_knowledge_bases WHERE user_id = ? AND knowledge_base_id = ?',
            (user_id, kb_id)
        ).fetchone()

        if existing:
            # 已收藏，取消收藏
            conn.execute(
                'DELETE FROM user_knowledge_bases WHERE user_id = ? AND knowledge_base_id = ?',
                (user_id, kb_id)
            )
        else:
            # 未收藏，添加收藏
            conn.execute(
                'INSERT INTO user_knowledge_bases (user_id, knowledge_base_id, created_at) VALUES (?, ?, ?)',
                (user_id, kb_id, datetime.now().isoformat())
            )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True
        })

    except Exception as e:
        print(f"收藏知识库错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_bp.route('/knowledge/<int:kb_id>', methods=['DELETE'])
def delete_knowledge(kb_id):
    """
    删除知识库
    响应: { success: true }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token) if token else None

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401

        user_id = user_payload.get('user_id')

        conn = get_db_connection()

        # 检查知识库是否属于当前用户
        kb = conn.execute(
            'SELECT * FROM knowledge_bases WHERE id = ?',
            (kb_id,)
        ).fetchone()

        if not kb:
            return jsonify({
                'success': False,
                'error': '知识库不存在'
            }), 404

        if kb['created_by'] != user_id:
            return jsonify({
                'success': False,
                'error': '无权删除此知识库'
            }), 403

        # 删除知识库的所有文档
        conn.execute('DELETE FROM knowledge_documents WHERE knowledge_base_id = ?', (kb_id,))

        # 删除知识库的关联
        conn.execute('DELETE FROM user_knowledge_bases WHERE knowledge_base_id = ?', (kb_id,))
        conn.execute('DELETE FROM agent_knowledge_bases WHERE knowledge_base_id = ?', (kb_id,))

        # 删除知识库
        conn.execute('DELETE FROM knowledge_bases WHERE id = ?', (kb_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True
        })

    except Exception as e:
        print(f"删除知识库错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 知识库文档管理 ====================

@knowledge_bp.route('/knowledge/<int:kb_id>/documents', methods=['GET'])
def list_documents(kb_id):
    """
    获取知识库的文档列表
    响应: { success: true, data: { documents: [...] } }
    """
    try:
        conn = get_db_connection()
        documents = conn.execute(
            'SELECT * FROM knowledge_documents WHERE knowledge_base_id = ? ORDER BY created_at DESC',
            (kb_id,)
        ).fetchall()
        conn.close()

        doc_list = []
        for doc in documents:
            doc_list.append({
                'id': doc['id'],
                'title': doc['title'],
                'content': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                'type': doc['type'] if 'type' in doc.keys() else 'text',
                'createdAt': doc['created_at']
            })

        return jsonify({
            'success': True,
            'data': {
                'documents': doc_list
            }
        })

    except Exception as e:
        print(f"获取文档列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_bp.route('/knowledge/<int:kb_id>/documents', methods=['POST'])
def add_document(kb_id):
    """
    添加文档到知识库
    请求体: { title, content, type? }
    响应: { success: true, data: { id, title, ... } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token) if token else None

        if not user_payload:
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401

        data = request.get_json()
        title = data.get('title')
        content = data['content'] if 'content' in data.keys() else ''
        doc_type = data['type'] if 'type' in data.keys() else 'text'

        if not title:
            return jsonify({
                'success': False,
                'error': '文档标题不能为空'
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            INSERT INTO knowledge_documents (knowledge_base_id, title, content, type, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (kb_id, title, content, doc_type, datetime.now().isoformat(), datetime.now().isoformat()))

        doc_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'id': doc_id,
                'title': title,
                'content': content,
                'type': doc_type
            }
        })

    except Exception as e:
        print(f"添加文档错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 知识库搜索 ====================

@knowledge_bp.route('/knowledge/search', methods=['POST'])
def search_knowledge():
    """
    搜索知识库内容
    请求体: { query, kbId? }
    响应: { success: true, data: { results: [...] } }
    """
    try:
        data = request.get_json()
        query = data['query'] if 'query' in data.keys() else ''
        kb_id = data.get('kbId')

        if not query:
            return jsonify({
                'success': False,
                'error': '搜索查询不能为空'
            }), 400

        conn = get_db_connection()

        # 检查表结构中是否有 is_public 字段
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(knowledge_bases)")
        columns = {col[1] for col in cursor.fetchall()}
        has_is_public = 'is_public' in columns

        if kb_id:
            # 在指定知识库中搜索
            docs = conn.execute('''
                SELECT kd.*, kb.name as kb_name
                FROM knowledge_documents kd
                JOIN knowledge_bases kb ON kd.knowledge_base_id = kb.id
                WHERE kd.knowledge_base_id = ? AND (kd.title LIKE ? OR kd.content LIKE ?)
                LIMIT 10
            ''', (kb_id, f'%{query}%', f'%{query}%')).fetchall()
        else:
            # 在所有公开知识库中搜索
            if has_is_public:
                docs = conn.execute('''
                    SELECT kd.*, kb.name as kb_name
                    FROM knowledge_documents kd
                    JOIN knowledge_bases kb ON kd.knowledge_base_id = kb.id
                    WHERE kb.is_public = 1 AND (kd.title LIKE ? OR kd.content LIKE ?)
                    LIMIT 20
                ''', (f'%{query}%', f'%{query}%')).fetchall()
            else:
                # 没有 is_public 字段，在所有知识库中搜索
                docs = conn.execute('''
                    SELECT kd.*, kb.name as kb_name
                    FROM knowledge_documents kd
                    JOIN knowledge_bases kb ON kd.knowledge_base_id = kb.id
                    WHERE kd.title LIKE ? OR kd.content LIKE ?
                    LIMIT 20
                ''', (f'%{query}%', f'%{query}%')).fetchall()

        conn.close()

        results = []
        for doc in docs:
            # 提取匹配的内容片段
            content_preview = doc['content']
            if query in content_preview:
                idx = content_preview.find(query)
                start = max(0, idx - 50)
                end = min(len(content_preview), idx + len(query) + 50)
                content_preview = '...' + content_preview[start:end] + '...'

            results.append({
                'id': doc['id'],
                'title': doc['title'],
                'content': content_preview,
                'kbName': doc['kb_name'],
                'kbId': doc['knowledge_base_id']
            })

        return jsonify({
            'success': True,
            'data': {
                'results': results
            }
        })

    except Exception as e:
        print(f"搜索知识库错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== V9 API 兼容 ====================

@knowledge_bp.route('/v9/knowledge/items', methods=['GET'])
def v9_list_knowledge_items():
    """
    V9 版本的知识库条目列表 API（兼容旧版）
    响应: { success: true, data: { items: [...] } }
    """
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        user_payload = verify_token(token) if token else None

        conn = get_db_connection()

        # 检查表结构中是否有 is_public 字段
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(knowledge_bases)")
        columns = {col[1] for col in cursor.fetchall()}
        has_is_public = 'is_public' in columns

        # 获取所有知识库条目
        if user_payload:
            if has_is_public:
                items = conn.execute('''
                    SELECT kb.*, COUNT(kd.id) as doc_count,
                           CASE WHEN ukb.user_id IS NOT NULL THEN 1 ELSE 0 END as is_favorite
                    FROM knowledge_bases kb
                    LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
                    LEFT JOIN user_knowledge_bases ukb ON kb.id = ukb.knowledge_base_id AND ukb.user_id = ?
                    WHERE kb.is_public = 1 OR kb.created_by = ?
                    GROUP BY kb.id
                    ORDER BY kb.created_at DESC
                ''', (user_payload.get('user_id'), user_payload.get('user_id'))).fetchall()
            else:
                # 没有 is_public 字段，返回所有知识库
                items = conn.execute('''
                    SELECT kb.*, COUNT(kd.id) as doc_count,
                           CASE WHEN ukb.user_id IS NOT NULL THEN 1 ELSE 0 END as is_favorite
                    FROM knowledge_bases kb
                    LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
                    LEFT JOIN user_knowledge_bases ukb ON kb.id = ukb.knowledge_base_id AND ukb.user_id = ?
                    GROUP BY kb.id
                    ORDER BY kb.created_at DESC
                ''', (user_payload.get('user_id'),)).fetchall()
        else:
            if has_is_public:
                items = conn.execute('''
                    SELECT kb.*, COUNT(kd.id) as doc_count, 0 as is_favorite
                    FROM knowledge_bases kb
                    LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
                    WHERE kb.is_public = 1
                    GROUP BY kb.id
                    ORDER BY kb.created_at DESC
                ''').fetchall()
            else:
                # 没有 is_public 字段，返回所有知识库
                items = conn.execute('''
                    SELECT kb.*, COUNT(kd.id) as doc_count, 0 as is_favorite
                    FROM knowledge_bases kb
                    LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
                    GROUP BY kb.id
                    ORDER BY kb.created_at DESC
                ''').fetchall()

        conn.close()

        result_items = []
        for item in items:
            result_items.append({
                'id': item['id'],
                'name': item['name'],
                'description': item['description'] if 'description' in item.keys() else '',
                'type': item['type'] if 'type' in item.keys() else 'general',
                'docCount': item['doc_count'],
                'isFavorite': bool(item['is_favorite'])
            })

        return jsonify({
            'success': True,
            'data': {
                'items': result_items
            }
        })

    except Exception as e:
        print(f"V9 知识库列表错误: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 预设的文化知识库数据
PRESET_CULTURE_ITEMS = {
    'culture-1': {
        'id': 'culture-1',
        'title': '西安文化关键词库',
        'content': '西安文化关键词库包含了110个西安特色文化关键词，涵盖历史、建筑、美食、艺术等多个方面。每个关键词都配有详细的商业转译提示，帮助用户将文化元素转化为商业价值。',
        'category': 'culture',
        'tags': ['文化', '西安', '关键词', '商业转译'],
        'view_count': 1250,
        'document_count': 110
    },
    'culture-2': {
        'id': 'culture-2',
        'title': '西安文化基因库',
        'content': '西安文化基因库是对西安城市文化基因的系统梳理和解码，包含文化基因分类、解码方法和应用场景。帮助用户深入理解西安文化的核心价值和现代意义。',
        'category': 'culture',
        'tags': ['文化基因', '解码', '分类', '应用'],
        'view_count': 980,
        'document_count': 56
    },
    'culture-3': {
        'id': 'culture-3',
        'title': '转译商业案例库',
        'content': '转译商业案例库收录了多个成功的文化商业转译案例，展示了六大转译方法的实际应用。每个案例都包含转译思路、实施过程和商业成果，为用户提供实践参考。',
        'category': 'culture',
        'tags': ['商业案例', '转译方法', '实践参考'],
        'view_count': 1560,
        'document_count': 42
    },
    'culture-4': {
        'id': 'culture-4',
        'title': '西安文化地图',
        'content': '西安文化地图以地理空间为线索，整合了西安的历史遗址、文化地标、美食街区、艺术场馆等文化资源，为用户提供直观的文化资源导航服务。',
        'category': 'culture',
        'tags': ['文化地图', '地理空间', '资源导航'],
        'view_count': 2300,
        'document_count': 89
    },
    'culture-5': {
        'id': 'culture-5',
        'title': '文化商业模式',
        'content': '文化商业模式模块系统介绍了文化产业的六种主流商业模式，包括文创产品、文化体验、文旅融合、文化IP运营等，帮助用户理解文化产业的商业逻辑和发展趋势。',
        'category': 'culture',
        'tags': ['商业模式', '文化产业', '文创产品'],
        'view_count': 1120,
        'document_count': 67
    }
}

@knowledge_bp.route('/v9/knowledge/items/<item_id>/view', methods=['POST'])
def v9_view_knowledge_item(item_id):
    """
    V9 版本的知识库条目查看 API（兼容旧版）
    响应: { success: true, data: { item: {...} } }
    """
    try:
        print(f"[知识库查看] item_id: {item_id}, 类型: {type(item_id)}")
        
        # 检查是否为预设的文化项目
        if item_id in PRESET_CULTURE_ITEMS:
            print(f"[知识库查看] 返回预设文化项目: {item_id}")
            item_data = PRESET_CULTURE_ITEMS[item_id].copy()
            item_data['created_at'] = '2025-01-01T00:00:00'
            item_data['updated_at'] = '2025-01-01T00:00:00'
            
            return jsonify({
                'success': True,
                'data': {
                    'item': item_data
                }
            })
        
        # 查询数据库中的知识库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 尝试通过名称或ID查找知识库
        cursor.execute('''
            SELECT kb.*, COUNT(kd.id) as doc_count
            FROM knowledge_bases kb
            LEFT JOIN knowledge_documents kd ON kb.id = kd.knowledge_base_id
            WHERE kb.name = ? OR kb.id = ?
            GROUP BY kb.id
        ''', (item_id, item_id if item_id.isdigit() else None))
        
        kb = cursor.fetchone()
        conn.close()
        
        if not kb:
            print(f"[知识库查看] 未找到知识库: {item_id}")
            return jsonify({
                'success': False,
                'error': '知识库不存在'
            }), 404
        
        kb_dict = dict(kb)
        
        # 构造返回数据
        item_data = {
            'id': str(kb_dict.get('id', '')),
            'title': str(kb_dict.get('name', '')),
            'content': str(kb_dict.get('description', '')),
            'category': 'culture' if kb_dict.get('name', '').startswith('西安') else 'general',
            'tags': [],
            'created_at': str(kb_dict.get('created_at', '')),
            'updated_at': str(kb_dict.get('updated_at', '')),
            'document_count': int(kb_dict.get('doc_count', 0)),
            'view_count': int(kb_dict.get('view_count', 0)),
        }
        
        print(f"[知识库查看] 成功返回知识库: {item_data['title']}")
        
        return jsonify({
            'success': True,
            'data': {
                'item': item_data
            }
        })
    
    except Exception as e:
        print(f"V9 查看知识库条目错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ==================== 知识库管理（管理员）====================

@knowledge_bp.route('/admin/knowledge/<int:kb_id>', methods=['DELETE'])
def admin_delete_knowledge(kb_id):
    """
    管理员删除知识库
    仅管理员可访问
    响应: { success: true }
    """
    try:
        # 验证Token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401
        
        user_payload = verify_token(token)
        if not user_payload:
            return jsonify({
                'success': False,
                'error': 'Token无效'
            }), 401
        
        # 检查管理员权限
        user_id = user_payload.get('user_id')
        
        # 根据 user_id 获取用户名
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户不存在'
                }), 404
            
            username = user['username']
        except Exception as e:
            print(f"[权限检查] 获取用户信息错误: {e}")
            return jsonify({
                'success': False,
                'error': '获取用户信息失败'
            }), 500
        
        if not is_admin(username):
            return jsonify({
                'success': False,
                'error': '需要管理员权限'
            }), 403
        
        # 删除知识库
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 先删除知识库的所有文档
        cursor.execute('DELETE FROM knowledge_documents WHERE knowledge_base_id = ?', (kb_id,))
        deleted_docs = cursor.rowcount
        
        # 删除知识库
        cursor.execute('DELETE FROM knowledge_bases WHERE id = ?', (kb_id,))
        deleted_kb = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted_kb == 0:
            return jsonify({
                'success': False,
                'error': '知识库不存在'
            }), 404
        
        print(f"[管理员操作] 用户 {user_id} 删除了知识库 {kb_id}，删除了 {deleted_docs} 个文档")
        
        return jsonify({
            'success': True,
            'message': f'知识库已删除，共删除 {deleted_docs} 个文档'
        })
    
    except Exception as e:
        print(f"删除知识库错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@knowledge_bp.route('/admin/knowledge/<int:kb_id>/documents/<int:doc_id>', methods=['DELETE'])
def admin_delete_document(kb_id, doc_id):
    """
    管理员删除知识库文档
    仅管理员可访问
    响应: { success: true }
    """
    try:
        # 验证Token
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({
                'success': False,
                'error': '需要登录'
            }), 401
        
        user_payload = verify_token(token)
        if not user_payload:
            return jsonify({
                'success': False,
                'error': 'Token无效'
            }), 401
        
        # 检查管理员权限
        user_id = user_payload.get('user_id')
        
        # 根据 user_id 获取用户名
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            conn.close()
            
            if not user:
                return jsonify({
                    'success': False,
                    'error': '用户不存在'
                }), 404
            
            username = user['username']
        except Exception as e:
            print(f"[权限检查] 获取用户信息错误: {e}")
            return jsonify({
                'success': False,
                'error': '获取用户信息失败'
            }), 500
        
        if not is_admin(username):
            return jsonify({
                'success': False,
                'error': '需要管理员权限'
            }), 403
        
        # 删除文档
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 验证文档属于该知识库
        cursor.execute('SELECT * FROM knowledge_documents WHERE id = ? AND knowledge_base_id = ?', (doc_id, kb_id))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'error': '文档不存在或不属于该知识库'
            }), 404
        
        # 删除文档
        cursor.execute('DELETE FROM knowledge_documents WHERE id = ?', (doc_id,))
        deleted = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        if deleted == 0:
            return jsonify({
                'success': False,
                'error': '删除失败'
            }), 500
        
        print(f"[管理员操作] 用户 {user_id} 删除了文档 {doc_id}（知识库 {kb_id}）")
        
        return jsonify({
            'success': True,
            'message': '文档已删除'
        })
    
    except Exception as e:
        print(f"删除文档错误: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


print("✅ 知识库 API 蓝图已加载")
