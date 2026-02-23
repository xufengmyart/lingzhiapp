# 用户引导文档API路由
# 功能：创建使用指南，帮助用户快速上手
# 创建时间: 2026-02-11

from flask import Blueprint, request, jsonify
from functools import wraps
import sqlite3
from datetime import datetime
import jwt
import sys
import os

# 导入配置
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

user_guide_bp = Blueprint('user_guide', __name__, url_prefix='/user-guide')

# 数据库路径
DB_PATH = config.DATABASE_PATH
JWT_SECRET = config.JWT_SECRET_KEY

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_user_id_from_request():
    """从请求中获取用户ID"""
    # 优先从 X-User-ID 头获取（兼容旧版）
    user_id = request.headers.get('X-User-ID')
    if user_id:
        return int(user_id)
    
    # 从 JWT token 获取用户ID
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header[7:]
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return payload.get('user_id')
        except:
            pass
    
    return None

def requires_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_user_id_from_request()
        if not user_id:
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ==================== /api/docs 兼容路由 ====================
# 这些路由是为了兼容前端的 /api/docs 调用

@user_guide_bp.route('/docs', methods=['GET'])
def get_docs_list():
    """
    获取文档列表（兼容前端调用）
    对应前端: /api/docs
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有已发布的文章
        cursor.execute('''
            SELECT id, title, slug, category, content,
                   view_count, created_at, updated_at, order_index
            FROM user_guide_articles
            WHERE is_published = 1
            ORDER BY order_index, created_at DESC
        ''')
        articles = cursor.fetchall()
        conn.close()
        
        # 构建响应数据
        docs_list = []
        for article in articles:
            doc = dict(article)
            # 提取描述（从内容中获取第一行或第一段）
            lines = doc.get('content', '').split('\n')
            description = lines[0] if lines else ''
            if description.startswith('#'):
                description = ' '.join(description.split(' ')[1:]) if len(description.split(' ')) > 1 else ''
            
            docs_list.append({
                'id': doc['id'],
                'title': doc['title'],
                'slug': doc['slug'],
                'category': doc['category'],
                'description': description[:200] + '...' if len(description) > 200 else description,
                'icon': '📖',  # 默认图标，可以根据分类设置
                'is_published': True,
                'created_at': doc['created_at'],
                'updated_at': doc['updated_at']
            })
        
        return jsonify({
            'success': True,
            'data': docs_list
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'加载文档列表失败: {str(e)}'
        }), 500

@user_guide_bp.route('/docs/<slug>', methods=['GET'])
def get_doc_detail(slug):
    """
    获取文档详情（兼容前端调用）
    对应前端: /api/docs/<slug>
    """
    try:
        user_id = get_user_id_from_request()
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 查询文章
        cursor.execute('''
            SELECT * FROM user_guide_articles
            WHERE slug = ? AND is_published = 1
        ''', (slug,))
        article = cursor.fetchone()
        
        if not article:
            conn.close()
            return jsonify({
                'success': False,
                'message': '文档不存在'
            }), 404
        
        article_dict = dict(article)
        
        # 如果用户已登录，记录阅读
        if user_id:
            cursor.execute('''
                SELECT id FROM user_guide_reads
                WHERE user_id = ? AND article_id = ?
            ''', (user_id, article_dict['id']))
            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO user_guide_reads (user_id, article_id)
                    VALUES (?, ?)
                ''', (user_id, article_dict['id']))
            
            # 更新阅读次数
            cursor.execute('''
                UPDATE user_guide_articles
                SET view_count = view_count + 1
                WHERE id = ?
            ''', (article_dict['id'],))
            conn.commit()
        
        conn.close()
        
        # 提取描述（从内容中获取第一行或第一段）
        lines = article_dict.get('content', '').split('\n')
        description = lines[0] if lines else ''
        if description.startswith('#'):
            description = ' '.join(description.split(' ')[1:]) if len(description.split(' ')) > 1 else ''
        
        return jsonify({
            'success': True,
            'data': {
                'id': article_dict['id'],
                'title': article_dict['title'],
                'slug': article_dict['slug'],
                'category': article_dict['category'],
                'description': description[:200] + '...' if len(description) > 200 else description,
                'content': article_dict['content'],
                'icon': '📖',
                'is_published': True,
                'view_count': article_dict.get('view_count', 0),
                'created_at': article_dict['created_at'],
                'updated_at': article_dict['updated_at']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'加载文档失败: {str(e)}'
        }), 500

# ==================== 原有的 /api/user-guide 路由 ====================

@user_guide_bp.route('/articles', methods=['GET'])
def get_articles():
    """获取引导文章列表（公开）"""
    try:
        category = request.args.get('category')
        limit = request.args.get('limit', 10, type=int)

        conn = get_db_connection()
        cursor = conn.cursor()

        # 构建查询
        query = '''
            SELECT id, title, slug, category, order_index,
                   view_count, created_at
            FROM user_guide_articles
            WHERE is_published = 1
        '''
        params = []

        if category:
            query += ' AND category = ?'
            params.append(category)

        query += ' ORDER BY order_index, created_at DESC LIMIT ?'
        params.append(limit)

        cursor.execute(query, params)
        articles = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': articles
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_guide_bp.route('/article/<slug>', methods=['GET'])
def get_article(slug):
    """获取文章详情（公开）"""
    try:
        user_id = get_user_id_from_request()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询文章
        cursor.execute('''
            SELECT * FROM user_guide_articles
            WHERE slug = ? AND is_published = 1
        ''', (slug,))
        article = cursor.fetchone()

        if not article:
            conn.close()
            return jsonify({'error': 'Article not found'}), 404

        article_dict = dict(article)

        # 如果用户已登录，记录阅读
        if user_id:
            cursor.execute('''
                SELECT id FROM user_guide_reads
                WHERE user_id = ? AND article_id = ?
            ''', (user_id, article['id']))

            if not cursor.fetchone():
                cursor.execute('''
                    INSERT INTO user_guide_reads (user_id, article_id)
                    VALUES (?, ?)
                ''', (user_id, article['id']))

            # 更新阅读次数
            cursor.execute('''
                UPDATE user_guide_articles
                SET view_count = view_count + 1
                WHERE id = ?
            ''', (article['id'],))

            conn.commit()

        conn.close()

        return jsonify({
            'success': True,
            'data': article_dict
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_guide_bp.route('/categories', methods=['GET'])
def get_categories():
    """获取文章分类列表（公开）"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT category, COUNT(*) as count
            FROM user_guide_articles
            WHERE is_published = 1
            GROUP BY category
            ORDER BY category
        ''')
        categories = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': categories
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_guide_bp.route('/my-progress', methods=['GET'])
@requires_auth
def get_my_progress():
    """获取我的阅读进度"""
    try:
        user_id = get_user_id_from_request()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 查询已读文章
        cursor.execute('''
            SELECTuga.*, ugr.completed, ugr.read_time
            FROM user_guide_articles uga
            LEFT JOIN user_guide_reads ugr ON uga.id = ugr.article_id AND ugr.user_id = ?
            WHERE uga.is_published = 1
            ORDER BY uga.order_index
        ''', (user_id,))
        articles = [dict(row) for row in cursor.fetchall()]

        # 计算进度
        total_articles = len(articles)
        completed_articles = sum(1 for a in articles if a.get('completed') == 1)
        progress = (completed_articles / total_articles * 100) if total_articles > 0 else 0

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'total_articles': total_articles,
                'completed_articles': completed_articles,
                'progress': round(progress, 2),
                'articles': articles
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_guide_bp.route('/articles', methods=['POST'])
@requires_auth
def create_article():
    """创建文章（管理员）"""
    try:
        user_id = get_user_id_from_request()
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否是管理员
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        is_admin = user and user['role'] in ['admin', 'super_admin']

        if not is_admin:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # 检查slug是否已存在
        cursor.execute('SELECT id FROM user_guide_articles WHERE slug = ?', (data.get('slug'),))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Slug already exists'}), 400

        # 插入文章
        cursor.execute('''
            INSERT INTO user_guide_articles (
                title, slug, category, content, order_index,
                is_published, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('title'),
            data.get('slug'),
            data.get('category'),
            data.get('content'),
            data.get('order_index', 0),
            1 if data.get('is_published') else 0,
            user_id
        ))
        conn.commit()

        article_id = cursor.lastrowid
        conn.close()

        return jsonify({
            'success': True,
            'message': '文章创建成功',
            'article_id': article_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_guide_bp.route('/article/<int:article_id>', methods=['PUT'])
@requires_auth
def update_article(article_id):
    """更新文章（管理员）"""
    try:
        user_id = get_user_id_from_request()
        data = request.get_json()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否是管理员
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        is_admin = user and user['role'] in ['admin', 'super_admin']

        if not is_admin:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # 更新文章
        cursor.execute('''
            UPDATE user_guide_articles
            SET title = ?, category = ?, content = ?,
                order_index = ?, is_published = ?, updated_by = ?, updated_at = ?
            WHERE id = ?
        ''', (
            data.get('title'),
            data.get('category'),
            data.get('content'),
            data.get('order_index', 0),
            1 if data.get('is_published') else 0,
            user_id,
            datetime.now().isoformat(),
            article_id
        ))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '文章更新成功'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_guide_bp.route('/article/<int:article_id>', methods=['DELETE'])
@requires_auth
def delete_article(article_id):
    """删除文章（管理员）"""
    try:
        user_id = get_user_id_from_request()

        conn = get_db_connection()
        cursor = conn.cursor()

        # 检查是否是管理员
        cursor.execute('SELECT role FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        is_admin = user and user['role'] in ['admin', 'super_admin']

        if not is_admin:
            conn.close()
            return jsonify({'error': 'Unauthorized'}), 403

        # 删除文章
        cursor.execute('DELETE FROM user_guide_articles WHERE id = ?', (article_id,))
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '文章删除成功'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
