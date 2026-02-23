# -*- coding: utf-8 -*-
"""
平台信息API
统一的平台信息管理接口，替代之前的系统新闻和平台公告
"""

from flask import Blueprint, jsonify, request
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db

platform_info_bp = Blueprint('platform_info', __name__)

# ============ 获取平台信息列表 ============

@platform_info_bp.route('/v9/platform-info', methods=['GET'])
def get_platform_info_list():
    """获取平台信息列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        info_type = request.args.get('info_type')
        keyword = request.args.get('keyword', '')
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM news_categories WHERE slug = 'platform-info'")
        platform_cat = cursor.fetchone()
        
        if not platform_cat:
            conn.close()
            return jsonify({'success': False, 'message': '平台信息分类不存在'}), 404
        
        category_id = platform_cat['id']

        where_conditions = ["category_id = ?", "status = 'published'"]
        params = [category_id]

        if info_type:
            where_conditions.append("info_type = ?")
            params.append(info_type)

        if keyword:
            where_conditions.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        where_clause = " AND ".join(where_conditions)

        cursor.execute(f"SELECT COUNT(*) as total FROM news_articles WHERE {where_clause}", params)
        total = cursor.fetchone()['total']

        cursor.execute(f"""
            SELECT id, title, slug, summary, cover_image,
                   info_type, importance_level, effective_date, expiry_date,
                   view_count, like_count, comment_count,
                   published_at, is_pinned, is_featured,
                   created_at, updated_at
            FROM news_articles
            WHERE {where_clause}
            ORDER BY is_pinned DESC, published_at DESC
            LIMIT ? OFFSET ?
        """, params + [page_size, offset])

        articles = []
        for row in cursor.fetchall():
            is_expired = False
            if row['expiry_date']:
                try:
                    expiry_date = datetime.strptime(row['expiry_date'], '%Y-%m-%d %H:%M:%S')
                    is_expired = expiry_date < datetime.now()
                except:
                    pass

            articles.append({
                'id': row['id'],
                'title': row['title'],
                'slug': row['slug'],
                'summary': row['summary'],
                'coverImage': row['cover_image'],
                'infoType': row['info_type'] or 'general',
                'importanceLevel': row['importance_level'] or 1,
                'effectiveDate': row['effective_date'],
                'expiryDate': row['expiry_date'],
                'isExpired': is_expired,
                'viewCount': row['view_count'],
                'likeCount': row['like_count'],
                'commentCount': row['comment_count'],
                'publishedAt': row['published_at'],
                'isPinned': bool(row['is_pinned']),
                'isFeatured': bool(row['is_featured']),
                'createdAt': row['created_at'],
                'updatedAt': row['updated_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': articles,
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'total': total
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ 获取重要通知 ============

@platform_info_bp.route('/v9/platform-info/important', methods=['GET'])
def get_important_notices():
    """获取重要通知"""
    try:
        limit = request.args.get('limit', 10, type=int)
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM news_categories WHERE slug = 'platform-info'")
        platform_cat = cursor.fetchone()
        
        if not platform_cat:
            conn.close()
            return jsonify({'success': False, 'message': '平台信息分类不存在'}), 404

        category_id = platform_cat['id']

        cursor.execute('''
            SELECT id, title, slug, summary, cover_image,
                   info_type, importance_level, published_at
            FROM news_articles
            WHERE category_id = ? AND status = 'published'
                AND (is_pinned = 1 OR importance_level >= 2)
            ORDER BY importance_level DESC, published_at DESC
            LIMIT ?
        ''', (category_id, limit))

        notices = []
        for row in cursor.fetchall():
            notices.append({
                'id': row['id'],
                'title': row['title'],
                'slug': row['slug'],
                'summary': row['summary'],
                'coverImage': row['cover_image'],
                'infoType': row['info_type'] or 'general',
                'importanceLevel': row['importance_level'] or 1,
                'publishedAt': row['published_at']
            })

        conn.close()

        return jsonify({'success': True, 'data': notices})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ 获取统计 ============

@platform_info_bp.route('/v9/platform-info/stats', methods=['GET'])
def get_platform_info_stats():
    """获取平台信息统计"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM news_categories WHERE slug = 'platform-info'")
        platform_cat = cursor.fetchone()
        
        if not platform_cat:
            conn.close()
            return jsonify({'success': False, 'message': '平台信息分类不存在'}), 404

        category_id = platform_cat['id']

        cursor.execute('''
            SELECT COUNT(*) as count FROM news_articles
            WHERE category_id = ? AND status = 'published'
        ''', (category_id,))
        total = cursor.fetchone()['count']

        conn.close()

        return jsonify({'success': True, 'data': {'total': total}})

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
