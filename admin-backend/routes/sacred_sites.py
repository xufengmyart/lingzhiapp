"""
文化圣地管理API
实现圣地的CRUD操作、体验管理、评分评论等功能
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime, timedelta
import sqlite3
import os
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

sacred_bp = Blueprint('sacred_sites', __name__, url_prefix='/api/sacred-sites')

# 数据库路径
DB_PATH = config.DATABASE_PATH

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': '未登录'}), 401
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if not result or result[0] != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': '未登录'}), 401
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

# ==================== 圣地管理 ====================

@sacred_bp.route('', methods=['POST'])
@admin_required
def create_site():
    """创建文化圣地"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO sacred_sites (
                site_name, site_type, location, coordinates,
                description, cultural_significance, historical_background,
                images, videos, opening_hours, admission_fee, contact_info,
                website, created_by, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('type'),
            data.get('location'),
            json.dumps(data.get('coordinates', {})),
            data.get('description'),
            data.get('cultural_significance'),
            data.get('historical_background'),
            json.dumps(data.get('images', [])),
            json.dumps(data.get('videos', [])),
            data.get('opening_hours'),
            data.get('admission_fee', 0),
            data.get('contact_info'),
            data.get('website'),
            request.user_id,
            data.get('status', 'active')
        ))
        
        site_id = cursor.lastrowid
        conn.commit()
        
        conn.close()
        return jsonify({'message': '圣地创建成功', 'id': site_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@sacred_bp.route('', methods=['GET'])
def get_sites():
    """获取圣地列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    status = request.args.get('status')
    site_type = request.args.get('type')
    location = request.args.get('location')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM sacred_sites WHERE 1=1"
    params = []
    
    if status:
        query += " AND status = ?"
        params.append(status)
    if site_type:
        query += " AND type = ?"
        params.append(site_type)
    if location:
        query += " AND location LIKE ?"
        params.append(f'%{location}%')
    
    # 获取总数
    count_query = query.replace('*', 'COUNT(*)')
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # 分页查询
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    sites = cursor.fetchall()
    
    # 格式化结果
    result = []
    for site in sites:
        result.append({
            'id': site[0],
            'name': site[1],  # site_name
            'type': site[2],  # site_type
            'location': site[3],
            'coordinates': json.loads(site[4]) if site[4] else {},
            'description': site[5],
            'cultural_significance': site[6],
            'historical_background': site[7],
            'images': json.loads(site[9]) if site[9] else [],
            'videos': json.loads(site[10]) if site[10] else [],
            'opening_hours': site[11],
            'admission_fee': site[12],
            'contact_info': site[13],
            'website': site[14],
            'rating': site[15],
            'total_reviews': site[16],  # review_count
            'visit_count': site[17],  # visitor_count
            'status': site[18],
            'verification_status': site[19],
            'created_at': site[22],
            'updated_at': site[23],
            'created_by': site[24]
        })
    
    conn.close()
    
    return jsonify({
        'sites': result,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page
    })

@sacred_bp.route('/<int:site_id>', methods=['GET'])
def get_site(site_id):
    """获取圣地详情"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM sacred_sites WHERE id = ?", (site_id,))
    site = cursor.fetchone()
    
    if not site:
        conn.close()
        return jsonify({'error': '圣地不存在'}), 404
    
    result = {
        'id': site[0],
        'name': site[1],  # site_name
        'type': site[2],  # site_type
        'location': site[3],
        'coordinates': json.loads(site[4]) if site[4] else {},
        'description': site[5],
        'cultural_significance': site[6],
        'historical_background': site[7],
        'images': json.loads(site[9]) if site[9] else [],
        'videos': json.loads(site[10]) if site[10] else [],
        'opening_hours': site[11],
        'admission_fee': site[12],
        'contact_info': site[13],
        'website': site[14],
        'rating': site[15],
        'total_reviews': site[16],  # review_count
        'visit_count': site[17],  # visitor_count
        'status': site[18],
        'verification_status': site[19],
        'created_at': site[22],
        'updated_at': site[23],
        'created_by': site[24]
    }
    
    conn.close()
    return jsonify(result)

@sacred_bp.route('/<int:site_id>', methods=['PUT'])
@admin_required
def update_site(site_id):
    """更新圣地信息"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM sacred_sites WHERE id = ?", (site_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '圣地不存在'}), 404
    
    try:
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("site_name = ?")
            params.append(data['name'])
        if 'type' in data:
            update_fields.append("site_type = ?")
            params.append(data['type'])
        if 'location' in data:
            update_fields.append("location = ?")
            params.append(data['location'])
        if 'coordinates' in data:
            update_fields.append("coordinates = ?")
            params.append(json.dumps(data['coordinates']))
        if 'description' in data:
            update_fields.append("description = ?")
            params.append(data['description'])
        if 'cultural_significance' in data:
            update_fields.append("cultural_significance = ?")
            params.append(data['cultural_significance'])
        if 'historical_background' in data:
            update_fields.append("historical_background = ?")
            params.append(data['historical_background'])
        if 'images' in data:
            update_fields.append("images = ?")
            params.append(json.dumps(data['images']))
        if 'videos' in data:
            update_fields.append("videos = ?")
            params.append(json.dumps(data['videos']))
        if 'opening_hours' in data:
            update_fields.append("opening_hours = ?")
            params.append(data['opening_hours'])
        if 'admission_fee' in data:
            update_fields.append("admission_fee = ?")
            params.append(data['admission_fee'])
        if 'contact_info' in data:
            update_fields.append("contact_info = ?")
            params.append(data['contact_info'])
        if 'website' in data:
            update_fields.append("website = ?")
            params.append(data['website'])
        if 'status' in data:
            update_fields.append("status = ?")
            params.append(data['status'])
            params.append(data['historical_background'])
        if 'images' in data:
            update_fields.append("images = ?")
            params.append(json.dumps(data['images']))
        if 'videos' in data:
            update_fields.append("videos = ?")
            params.append(json.dumps(data['videos']))
        if 'opening_hours' in data:
            update_fields.append("opening_hours = ?")
            params.append(data['opening_hours'])
        if 'admission_fee' in data:
            update_fields.append("admission_fee = ?")
            params.append(data['admission_fee'])
        if 'contact_info' in data:
            update_fields.append("contact_info = ?")
            params.append(data['contact_info'])
        if 'website' in data:
            update_fields.append("website = ?")
            params.append(data['website'])
        if 'status' in data:
            update_fields.append("status = ?")
            params.append(data['status'])
        
        update_fields.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        params.append(site_id)
        
        query = f"UPDATE sacred_sites SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '圣地更新成功'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@sacred_bp.route('/<int:site_id>', methods=['DELETE'])
@admin_required
def delete_site(site_id):
    """删除圣地"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM sacred_sites WHERE id = ?", (site_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '圣地不存在'}), 404
    
    cursor.execute("DELETE FROM sacred_sites WHERE id = ?", (site_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'message': '圣地删除成功'})

# ==================== 体验管理 ====================

@sacred_bp.route('/<int:site_id>/experiences', methods=['POST'])
@login_required
def create_experience(site_id):
    """创建圣地体验"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM sacred_sites WHERE id = ?", (site_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '圣地不存在'}), 404
    
    try:
        cursor.execute('''
            INSERT INTO site_experiences (
                site_id, experience_name, experience_type, description,
                duration_minutes, max_participants, price,
                schedule, requirements, highlights, images
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            site_id,
            data.get('title'),
            data.get('type'),
            data.get('description'),
            data.get('duration'),
            data.get('max_participants'),
            data.get('price', 0),
            json.dumps(data.get('schedule', [])),
            json.dumps(data.get('requirements', [])),
            json.dumps(data.get('highlights', [])),
            json.dumps(data.get('images', []))
        ))
        
        experience_id = cursor.lastrowid
        conn.commit()
        
        conn.close()
        return jsonify({'message': '体验创建成功', 'id': experience_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@sacred_bp.route('/<int:site_id>/experiences', methods=['GET'])
def get_experiences(site_id):
    """获取圣地的体验列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM site_experiences WHERE site_id = ? ORDER BY created_at DESC", (site_id,))
    experiences = cursor.fetchall()
    
    result = []
    for exp in experiences:
        result.append({
            'id': exp[0],
            'site_id': exp[1],
            'title': exp[2],  # experience_name
            'type': exp[3],  # experience_type
            'description': exp[4],
            'duration': exp[5],  # duration_minutes
            'max_participants': exp[6],
            'price': exp[7],
            'schedule': json.loads(exp[8]) if exp[8] else [],
            'requirements': json.loads(exp[9]) if exp[9] else [],
            'highlights': json.loads(exp[10]) if exp[10] else [],
            'images': json.loads(exp[11]) if exp[11] else [],
            'status': exp[12],
            'created_at': exp[13],
            'updated_at': exp[14]
        })
    
    conn.close()
    return jsonify({'experiences': result})

# ==================== 评分评论 ====================

@sacred_bp.route('/<int:site_id>/reviews', methods=['POST'])
@login_required
def create_review(site_id):
    """创建评论"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM sacred_sites WHERE id = ?", (site_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '圣地不存在'}), 404
    
    # 检查是否已经评论过
    cursor.execute("SELECT id FROM site_reviews WHERE site_id = ? AND user_id = ?", (site_id, request.user_id))
    if cursor.fetchone():
        conn.close()
        return jsonify({'error': '您已经评论过该圣地'}), 400
    
    try:
        cursor.execute('''
            INSERT INTO site_reviews (
                site_id, user_id, rating, title, content,
                images, tags, is_verified, helpful_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            site_id,
            request.user_id,
            data.get('rating'),
            data.get('title'),
            data.get('content'),
            json.dumps(data.get('images', [])),
            json.dumps(data.get('tags', [])),
            1 if data.get('is_verified', False) else 0,
            0
        ))
        
        # 更新圣地的平均评分
        cursor.execute('''
            UPDATE sacred_sites
            SET rating = (
                SELECT AVG(rating) FROM site_reviews WHERE site_id = ?
            ),
            review_count = (
                SELECT COUNT(*) FROM site_reviews WHERE site_id = ?
            ),
            updated_at = ?
            WHERE id = ?
        ''', (site_id, site_id, datetime.now().isoformat(), site_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '评论发布成功'}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@sacred_bp.route('/<int:site_id>/reviews', methods=['GET'])
def get_reviews(site_id):
    """获取圣地评论列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    sort_by = request.args.get('sort', 'latest')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取总数
    cursor.execute("SELECT COUNT(*) FROM site_reviews WHERE site_id = ?", (site_id,))
    total = cursor.fetchone()[0]
    
    # 排序
    order_by = "ORDER BY created_at DESC"
    if sort_by == 'rating':
        order_by = "ORDER BY rating DESC"
    elif sort_by == 'helpful':
        order_by = "ORDER BY helpful_count DESC"
    
    query = f'''
        SELECT r.id, r.site_id, r.user_id, r.rating, r.title, r.content,
               r.images, r.tags, r.is_verified, r.helpful_count, r.created_at, r.updated_at,
               u.username, u.avatar_url, u.role
        FROM site_reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.site_id = ?
        {order_by}
        LIMIT ? OFFSET ?
    '''
    
    cursor.execute(query, (site_id, per_page, (page - 1) * per_page))
    reviews = cursor.fetchall()
    
    result = []
    for review in reviews:
        result.append({
            'id': review[0],
            'site_id': review[1],
            'user_id': review[2],
            'username': review[12],
            'avatar': review[13],
            'user_role': review[14],
            'rating': review[3],
            'title': review[4],
            'content': review[5],
            'images': json.loads(review[6]) if review[6] else [],
            'tags': json.loads(review[7]) if review[7] else [],
            'is_verified': bool(review[8]),
            'helpful_count': review[9],
            'created_at': review[10],
            'updated_at': review[11]
        })
    
    conn.close()
    
    return jsonify({
        'reviews': result,
        'total': total,
        'page': page,
        'per_page': per_page
    })

@sacred_bp.route('/reviews/<int:review_id>/helpful', methods=['POST'])
@login_required
def mark_review_helpful(review_id):
    """标记评论为有用"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM site_reviews WHERE id = ?", (review_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '评论不存在'}), 404
    
    cursor.execute('''
        UPDATE site_reviews
        SET helpful_count = helpful_count + 1
        WHERE id = ?
    ''', (review_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'message': '标记成功'})

# ==================== 浏览记录 ====================

@sacred_bp.route('/<int:site_id>/visit', methods=['POST'])
@login_required
def record_visit(site_id):
    """记录访问"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM sacred_sites WHERE id = ?", (site_id,))
    if not cursor.fetchone():
        conn.close()
        return jsonify({'error': '圣地不存在'}), 404
    
    try:
        cursor.execute('''
            INSERT INTO site_visits (site_id, user_id)
            VALUES (?, ?)
        ''', (site_id, request.user_id))
        
        # 更新访问次数
        cursor.execute('''
            UPDATE sacred_sites
            SET visit_count = visit_count + 1
            WHERE id = ?
        ''', (site_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '访问记录成功'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@sacred_bp.route('/visits', methods=['GET'])
@login_required
def get_user_visits():
    """获取用户的访问记录"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT v.id, v.site_id, v.user_id, v.visited_at,
               s.site_name, s.location, s.images
        FROM site_visits v
        JOIN sacred_sites s ON v.site_id = s.id
        WHERE v.user_id = ?
        ORDER BY v.visited_at DESC
        LIMIT ? OFFSET ?
    ''', (request.user_id, per_page, (page - 1) * per_page))
    
    visits = cursor.fetchall()
    
    result = []
    for visit in visits:
        result.append({
            'id': visit[0],
            'site_id': visit[1],
            'site_name': visit[4],
            'location': visit[5],
            'site_images': json.loads(visit[6]) if visit[6] else [],
            'visited_at': visit[3]
        })
    
    conn.close()
    return jsonify({'visits': result})

import json