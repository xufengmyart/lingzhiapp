"""
动态资讯路由蓝图
提供文章、分类、推荐、通知等功能
"""

from flask import Blueprint, jsonify, request
import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db

news_bp = Blueprint('news', __name__)

# ============ 文章列表 ============

@news_bp.route('/v9/news/articles', methods=['GET'])
def get_articles():
    """获取文章列表"""
    try:
        # 获取查询参数
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 10, type=int)
        category_id = request.args.get('category_id', type=int)
        status = request.args.get('status', 'published')
        keyword = request.args.get('keyword', '')

        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 构建查询条件
        where_conditions = ["status = ?"]
        params = [status]

        if category_id:
            where_conditions.append("category_id = ?")
            params.append(category_id)

        if keyword:
            where_conditions.append("(title LIKE ? OR content LIKE ?)")
            params.extend([f"%{keyword}%", f"%{keyword}%"])

        where_clause = " AND ".join(where_conditions)

        # 获取总数
        cursor.execute(f"SELECT COUNT(*) as total FROM news_articles WHERE {where_clause}", params)
        total = cursor.fetchone()['total']

        # 获取文章列表
        cursor.execute(f"""
            SELECT
                id, title, slug, summary, category_id,
                cover_image, is_featured, is_pinned,
                view_count, like_count, comment_count,
                published_at, created_at
            FROM news_articles
            WHERE {where_clause}
            ORDER BY is_pinned DESC, published_at DESC
            LIMIT ? OFFSET ?
        """, params + [page_size, offset])

        articles = []
        for row in cursor.fetchall():
            # 获取分类信息
            category_name = None
            if row['category_id']:
                cursor.execute(
                    "SELECT name FROM news_categories WHERE id = ?",
                    (row['category_id'],)
                )
                cat = cursor.fetchone()
                if cat:
                    category_name = cat['name']

            articles.append({
                'id': row['id'],
                'title': row['title'],
                'slug': row['slug'],
                'summary': row['summary'],
                'categoryId': row['category_id'],
                'categoryName': category_name,
                'coverImage': row['cover_image'],
                'isFeatured': bool(row['is_featured']),
                'isPinned': bool(row['is_pinned']),
                'viewCount': row['view_count'],
                'likeCount': row['like_count'],
                'commentCount': row['comment_count'],
                'publishedAt': row['published_at'],
                'createdAt': row['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取文章列表成功',
            'data': articles,
            'total': total,
            'page': page,
            'page_size': page_size
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取文章列表失败: {str(e)}',
            'data': [],
            'total': 0
        }), 500


# ============ 文章详情 ============

@news_bp.route('/v9/news/articles/<slug>', methods=['GET'])
def get_article_detail(slug):
    """获取文章详情"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 获取文章
        cursor.execute("""
            SELECT * FROM news_articles WHERE slug = ? AND status = 'published'
        """, (slug,))

        article = cursor.fetchone()

        if not article:
            conn.close()
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        # 增加阅读次数
        cursor.execute(
            "UPDATE news_articles SET view_count = view_count + 1 WHERE id = ?",
            (article['id'],)
        )

        # 获取分类信息
        category_name = None
        if article['category_id']:
            cursor.execute(
                "SELECT name, slug FROM news_categories WHERE id = ?",
                (article['category_id'],)
            )
            cat = cursor.fetchone()
            if cat:
                category_name = cat['name']

        article_data = {
            'id': article['id'],
            'title': article['title'],
            'slug': article['slug'],
            'content': article['content'],
            'summary': article['summary'],
            'categoryId': article['category_id'],
            'categoryName': category_name,
            'coverImage': article['cover_image'],
            'authorName': article['user_name'],
            'isFeatured': bool(article['is_featured']),
            'isPinned': bool(article['is_pinned']),
            'viewCount': article['view_count'],
            'likeCount': article['like_count'],
            'commentCount': article['comment_count'],
            'tags': article['tags'].split(',') if article['tags'] else [],
            'publishedAt': article['published_at'],
            'createdAt': article['created_at']
        }

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '获取文章详情成功',
            'data': article_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取文章详情失败: {str(e)}'
        }), 500


# ============ 文章分类 ============

@news_bp.route('/v9/news/categories', methods=['GET'])
def get_categories():
    """获取文章分类"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT
                id, name, slug, description, icon, sort_order
            FROM news_categories
            WHERE is_active = 1
            ORDER BY sort_order ASC
        """)

        categories = []
        for row in cursor.fetchall():
            # 获取该分类下的文章数量
            cursor.execute(
                "SELECT COUNT(*) as count FROM news_articles WHERE category_id = ? AND status = 'published'",
                (row['id'],)
            )
            count_row = cursor.fetchone()
            article_count = count_row['count'] if count_row else 0

            categories.append({
                'id': row['id'],
                'name': row['name'],
                'slug': row['slug'],
                'description': row['description'],
                'icon': row['icon'],
                'sortOrder': row['sort_order'],
                'articleCount': article_count
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取分类成功',
            'data': categories
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分类失败: {str(e)}',
            'data': []
        }), 500


# ============ 推荐文章 ============

@news_bp.route('/v9/news/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    """获取推荐文章"""
    try:
        limit = request.args.get('limit', 5, type=int)

        conn = get_db()
        cursor = conn.cursor()

        # 获取精选文章和最新文章
        cursor.execute("""
            SELECT
                id, title, slug, summary, cover_image,
                view_count, published_at
            FROM news_articles
            WHERE status = 'published' AND (is_featured = 1 OR is_pinned = 1)
            ORDER BY is_pinned DESC, published_at DESC
            LIMIT ?
        """, (limit * 2,))

        articles = []
        for row in cursor.fetchall():
            articles.append({
                'id': row['id'],
                'title': row['title'],
                'slug': row['slug'],
                'summary': row['summary'],
                'coverImage': row['cover_image'],
                'viewCount': row['view_count'],
                'publishedAt': row['published_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取推荐文章成功',
            'data': articles[:limit],
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取推荐文章失败: {str(e)}',
            'data': [],
            'user_id': user_id
        }), 500


# ============ 用户通知 ============

@news_bp.route('/v9/news/notifications', methods=['GET'])
def get_notifications():
    """获取用户通知"""
    try:
        # 获取用户ID（从JWT或查询参数）
        user_id = request.args.get('user_id', 1, type=int)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)

        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 获取总数（未读数量）
        cursor.execute(
            "SELECT COUNT(*) as total, SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread FROM user_notifications WHERE user_id = ?",
            (user_id,)
        )
        count_row = cursor.fetchone()
        total = count_row['total']
        unread_count = count_row['unread'] if count_row['unread'] else 0

        # 获取通知列表
        cursor.execute("""
            SELECT
                id, title, content, type, is_read, link,
                created_at, read_at
            FROM user_notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (user_id, page_size, offset))

        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row['id'],
                'title': row['title'],
                'content': row['content'],
                'type': row['type'],
                'isRead': bool(row['is_read']),
                'link': row['link'],
                'createdAt': row['created_at'],
                'readAt': row['read_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取通知成功',
            'data': notifications,
            'unreadCount': unread_count,
            'total': total,
            'page': page,
            'page_size': page_size,
            'user_id': user_id
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取通知失败: {str(e)}',
            'data': [],
            'unreadCount': 0,
            'user_id': user_id
        }), 500


# ============ 标记通知为已读 ============

@news_bp.route('/v9/news/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_read(notification_id):
    """标记通知为已读"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_notifications
            SET is_read = 1, read_at = ?
            WHERE id = ?
        """, (datetime.now(), notification_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '标记为已读成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'标记失败: {str(e)}'
        }), 500


# ============ 批量标记通知为已读 ============

@news_bp.route('/v9/news/notifications/read-all', methods=['PUT'])
def mark_all_notifications_read():
    """批量标记通知为已读"""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 1)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_notifications
            SET is_read = 1, read_at = ?
            WHERE user_id = ? AND is_read = 0
        """, (datetime.now(), user_id))

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'成功标记 {affected_rows} 条通知为已读'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'批量标记失败: {str(e)}'
        }), 500


# ============ 管理员：创建文章 ============

@news_bp.route('/admin/news/articles', methods=['POST'])
def create_article():
    """管理员创建文章"""
    try:
        data = request.get_json()

        required_fields = ['title', 'content']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'success': False,
                    'message': f'缺少必填字段: {field}'
                }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 生成slug
        import re
        slug = re.sub(r'[^\w\-]', '-', data['title'].lower()).strip('-')

        cursor.execute("""
            INSERT INTO news_articles (
                title, slug, content, summary,
                category_id, author_name, cover_image,
                is_featured, is_pinned, status,
                tags, published_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['title'],
            slug,
            data['content'],
            data.get('summary', ''),
            data.get('category_id'),
            data.get('author_name', '管理员'),
            data.get('cover_image'),
            1 if data.get('is_featured') else 0,
            1 if data.get('is_pinned') else 0,
            data.get('status', 'published'),
            ','.join(data.get('tags', [])),
            datetime.now() if data.get('status') == 'published' else None
        ))

        article_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '文章创建成功',
            'data': {'id': article_id, 'slug': slug}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建文章失败: {str(e)}'
        }), 500


# ============ 管理员：删除文章 ============

# ============ 管理员编辑文章 ============

@news_bp.route('/admin/news/articles/<int:article_id>', methods=['PUT'])
def update_article(article_id):
    """管理员编辑文章"""
    try:
        data = request.get_json()

        conn = get_db()
        cursor = conn.cursor()

        # 检查文章是否存在
        cursor.execute("SELECT id, slug FROM news_articles WHERE id = ?", (article_id,))
        article = cursor.fetchone()
        if not article:
            conn.close()
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        # 生成slug
        import re
        slug = re.sub(r'[^\w\-]', '-', data['title'].lower()).strip('-')

        # 构建更新字段
        update_fields = []
        params = []

        if 'title' in data:
            update_fields.append('title = ?')
            params.append(data['title'])

        if 'slug' in data:
            update_fields.append('slug = ?')
            params.append(data['slug'])
        else:
            update_fields.append('slug = ?')
            params.append(slug)

        if 'content' in data:
            update_fields.append('content = ?')
            params.append(data['content'])

        if 'summary' in data:
            update_fields.append('summary = ?')
            params.append(data['summary'])

        if 'category_id' in data:
            update_fields.append('category_id = ?')
            params.append(data['category_id'])

        if 'cover_image' in data:
            update_fields.append('cover_image = ?')
            params.append(data['cover_image'])

        if 'is_featured' in data:
            update_fields.append('is_featured = ?')
            params.append(1 if data['is_featured'] else 0)

        if 'is_pinned' in data:
            update_fields.append('is_pinned = ?')
            params.append(1 if data['is_pinned'] else 0)

        if 'status' in data:
            update_fields.append('status = ?')
            params.append(data['status'])
            
            # 如果状态改为 published，设置发布时间
            if data['status'] == 'published':
                update_fields.append('published_at = ?')
                params.append(datetime.now())

        if 'tags' in data:
            update_fields.append('tags = ?')
            params.append(','.join(data['tags']) if isinstance(data['tags'], list) else data['tags'])

        update_fields.append('updated_at = ?')
        params.append(datetime.now())

        params.append(article_id)

        query = f"UPDATE news_articles SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, params)

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '文章更新成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新文章失败: {str(e)}'
        }), 500


# ============ 管理员审核文章 ============

@news_bp.route('/admin/news/articles/<int:article_id>/approve', methods=['PUT'])
def approve_article(article_id):
    """管理员审核文章（通过）"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查文章是否存在
        cursor.execute("SELECT id, status, author_id, title FROM news_articles WHERE id = ?", (article_id,))
        article = cursor.fetchone()
        if not article:
            conn.close()
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        # 更新文章状态为 published
        cursor.execute("""
            UPDATE news_articles
            SET status = 'published', published_at = ?, updated_at = ?
            WHERE id = ?
        """, (datetime.now(), datetime.now(), article_id))

        # 发送通知给作者
        cursor.execute("""
            INSERT INTO user_notifications
            (user_id, title, content, type, link, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (
            article['author_id'],
            '您的文章已通过审核',
            f'您的文章《{article["title"]}》已通过审核并发布',
            'article_approved',
            f'/article/{article_id}',
            datetime.now()
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '文章已通过审核'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'审核文章失败: {str(e)}'
        }), 500


@news_bp.route('/admin/news/articles/<int:article_id>/reject', methods=['PUT'])
def reject_article(article_id):
    """管理员审核文章（拒绝）"""
    try:
        data = request.get_json()
        reason = data.get('reason', '审核未通过')

        conn = get_db()
        cursor = conn.cursor()

        # 检查文章是否存在
        cursor.execute("SELECT id, status, author_id, title FROM news_articles WHERE id = ?", (article_id,))
        article = cursor.fetchone()
        if not article:
            conn.close()
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        # 更新文章状态为 rejected
        cursor.execute("""
            UPDATE news_articles
            SET status = 'rejected', updated_at = ?
            WHERE id = ?
        """, (datetime.now(), article_id))

        # 发送通知给作者
        cursor.execute("""
            INSERT INTO user_notifications
            (user_id, title, content, type, link, is_read, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (
            article['author_id'],
            '您的文章未通过审核',
            f'您的文章《{article["title"]}》未通过审核。原因：{reason}',
            'article_rejected',
            f'/article/{article_id}',
            datetime.now()
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'文章已拒绝: {reason}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'拒绝文章失败: {str(e)}'
        }), 500


# ============ 管理员删除文章 ============

@news_bp.route('/admin/news/articles/<int:article_id>', methods=['DELETE'])
def delete_article(article_id):
    """管理员删除文章"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM news_articles WHERE id = ?", (article_id,))
        affected_rows = cursor.rowcount

        conn.commit()
        conn.close()

        if affected_rows == 0:
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        return jsonify({
            'success': True,
            'message': '文章删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除文章失败: {str(e)}'
        }), 500


# ============ 文章评论 API ============

@news_bp.route('/v9/news/articles/<int:article_id>/comments', methods=['GET'])
def get_news_comments(article_id):
    """获取文章评论列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 获取总数
        cursor.execute(
            "SELECT COUNT(*) as total FROM news_comments WHERE article_id = ?",
            (article_id,)
        )
        total = cursor.fetchone()['total']

        # 获取评论列表
        cursor.execute("""
            SELECT
                id, article_id, content, user_id, user_name,
                like_count, created_at
            FROM news_comments
            WHERE article_id = ?
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (article_id, page_size, offset))

        comments = []
        for row in cursor.fetchall():
            comments.append({
                'id': row['id'],
                'articleId': row['article_id'],
                'content': row['content'],
                'author': row['user_name'],
                'authorId': row['user_id'],
                'likeCount': row['like_count'],
                'createdAt': row['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取评论列表成功',
            'data': comments,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取评论列表失败: {str(e)}',
            'data': []
        }), 500


@news_bp.route('/v9/news/articles/<int:article_id>/comments', methods=['POST'])
def create_article_comment(article_id):
    """创建文章评论"""
    try:
        data = request.get_json()
        content = data.get('content', '').strip()
        user_id = data.get('user_id', 1)  # 默认为管理员，实际应从JWT获取
        user_name = data.get('user_name', '匿名用户')

        if not content:
            return jsonify({
                'success': False,
                'message': '评论内容不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查文章是否存在
        cursor.execute("SELECT id FROM news_articles WHERE id = ?", (article_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        # 创建评论
        cursor.execute("""
            INSERT INTO news_comments (
                article_id, user_id, user_name, content
            ) VALUES (?, ?, ?, ?)
        """, (article_id, user_id, user_name, content))

        comment_id = cursor.lastrowid

        # 更新文章评论数
        cursor.execute("""
            UPDATE news_articles
            SET comment_count = comment_count + 1
            WHERE id = ?
        """, (article_id,))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '评论发布成功',
            'data': {'id': comment_id, 'articleId': article_id}
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'评论发布失败: {str(e)}'
        }), 500


@news_bp.route('/v9/news/articles/<int:article_id>/comments/<int:comment_id>/like', methods=['POST'])
def like_article_comment(article_id, comment_id):
    """点赞评论"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE news_comments
            SET like_count = like_count + 1
            WHERE id = ? AND article_id = ?
        """, (comment_id, article_id))

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        if affected_rows == 0:
            return jsonify({
                'success': False,
                'message': '评论不存在'
            }), 404

        return jsonify({
            'success': True,
            'message': '点赞成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'点赞失败: {str(e)}'
        }), 500


# ============ 通知增强 API ============

@news_bp.route('/v9/notifications/unread/count', methods=['GET'])
def get_unread_notifications_count():
    """获取未读通知数量"""
    try:
        # 从查询参数获取用户ID
        user_id = request.args.get('user_id', 1, type=int)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) as count FROM user_notifications WHERE user_id = ? AND is_read = 0",
            (user_id,)
        )
        result = cursor.fetchone()

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取未读数量成功',
            'data': {
                'count': result['count'] if result else 0,
                'user_id': user_id
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取未读数量失败: {str(e)}',
            'data': {'count': 0}
        }), 500


@news_bp.route('/v9/notifications/latest', methods=['GET'])
def get_latest_notifications():
    """获取最新通知（用于实时通知）"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        since = request.args.get('since')  # ISO格式的时间戳

        conn = get_db()
        cursor = conn.cursor()

        if since:
            # 获取指定时间之后的新通知
            cursor.execute("""
                SELECT
                    id, user_id, type, title, content, is_read,
                    priority, category, created_at
                FROM user_notifications
                WHERE user_id = ? AND created_at > ?
                ORDER BY created_at DESC
                LIMIT 10
            """, (user_id, since))
        else:
            # 获取最新的5条通知
            cursor.execute("""
                SELECT
                    id, user_id, type, title, content, is_read,
                    priority, category, created_at
                FROM user_notifications
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT 5
            """, (user_id,))

        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row['id'],
                'userId': row['user_id'],
                'type': row['type'],
                'title': row['title'],
                'content': row['content'],
                'isRead': bool(row['is_read']),
                'priority': row['priority'] or 'medium',
                'category': row['category'] or 'system',
                'createdAt': row['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取最新通知成功',
            'data': notifications
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取最新通知失败: {str(e)}',
            'data': []
        }), 500


@news_bp.route('/v9/notifications', methods=['GET'])
def get_all_notifications():
    """获取通知列表（增强版，支持筛选和排序）"""
    try:
        user_id = request.args.get('user_id', 1, type=int)
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        category = request.args.get('category')
        is_read = request.args.get('is_read')
        sort = request.args.get('sort', '-created_at')

        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 构建查询条件
        where_conditions = ["user_id = ?"]
        params = [user_id]

        if category:
            where_conditions.append("category = ?")
            params.append(category)

        if is_read is not None:
            where_conditions.append("is_read = ?")
            params.append(1 if is_read.lower() in ['true', '1'] else 0)

        where_clause = " AND ".join(where_conditions)

        # 构建排序
        if sort.startswith('-'):
            sort_field = sort[1:]
            sort_order = "DESC"
        else:
            sort_field = sort
            sort_order = "ASC"

        # 映射优先级到数字用于排序
        if sort_field == 'priority':
            order_clause = "CASE priority WHEN 'high' THEN 3 WHEN 'medium' THEN 2 WHEN 'low' THEN 1 ELSE 0 END DESC, created_at DESC"
        else:
            order_clause = f"{sort_field} {sort_order}"

        # 获取总数
        cursor.execute(f"SELECT COUNT(*) as total FROM user_notifications WHERE {where_clause}", params)
        total = cursor.fetchone()['total']

        # 获取通知列表
        cursor.execute(f"""
            SELECT
                id, user_id, type, title, content, is_read,
                priority, category, link, related_id, related_type,
                created_at, read_at, metadata
            FROM user_notifications
            WHERE {where_clause}
            ORDER BY {order_clause}
            LIMIT ? OFFSET ?
        """, params + [page_size, offset])

        notifications = []
        for row in cursor.fetchall():
            notifications.append({
                'id': row['id'],
                'userId': row['user_id'],
                'type': row['type'],
                'title': row['title'],
                'content': row['content'],
                'isRead': bool(row['is_read']),
                'priority': row['priority'] or 'medium',
                'category': row['category'] or 'system',
                'link': row['link'],
                'relatedId': row['related_id'],
                'relatedType': row['related_type'],
                'createdAt': row['created_at'],
                'readAt': row['read_at'],
                'metadata': row['metadata']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取通知成功',
            'data': notifications,
            'pagination': {
                'total': total,
                'page': page,
                'page_size': page_size
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取通知失败: {str(e)}',
            'data': []
        }), 500


@news_bp.route('/v9/notifications/<int:notification_id>/read', methods=['PUT'])
def mark_notification_as_read(notification_id):
    """标记通知为已读"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_notifications
            SET is_read = 1, read_at = ?
            WHERE id = ?
        """, (datetime.now(), notification_id))

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        if affected_rows == 0:
            return jsonify({
                'success': False,
                'message': '通知不存在'
            }), 404

        return jsonify({
            'success': True,
            'message': '标记为已读成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'标记失败: {str(e)}'
        }), 500


@news_bp.route('/v9/notifications/read-all', methods=['PUT'])
def mark_all_notifications_as_read():
    """批量标记通知为已读"""
    try:
        data = request.get_json() or {}
        user_id = data.get('user_id', 1)

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_notifications
            SET is_read = 1, read_at = ?
            WHERE user_id = ? AND is_read = 0
        """, (datetime.now(), user_id))

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'成功标记 {affected_rows} 条通知为已读'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'批量标记失败: {str(e)}'
        }), 500


@news_bp.route('/v9/notifications/<int:notification_id>', methods=['DELETE'])
def delete_notification(notification_id):
    """删除通知"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM user_notifications WHERE id = ?", (notification_id,))
        affected_rows = cursor.rowcount

        conn.commit()
        conn.close()

        if affected_rows == 0:
            return jsonify({
                'success': False,
                'message': '通知不存在'
            }), 404

        return jsonify({
            'success': True,
            'message': '删除通知成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除通知失败: {str(e)}'
        }), 500



@news_bp.route('/v9/news/articles/<int:article_id>/comments/<int:comment_id>', methods=['DELETE'])
def delete_article_comment(article_id, comment_id):
    """删除评论"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 删除评论
        cursor.execute("""
            DELETE FROM news_comments
            WHERE id = ? AND article_id = ?
        """, (comment_id, article_id))

        affected_rows = cursor.rowcount

        if affected_rows > 0:
            # 更新文章评论数
            cursor.execute("""
                UPDATE news_articles
                SET comment_count = comment_count - 1
                WHERE id = ?
            """, (article_id,))

        conn.commit()
        conn.close()

        if affected_rows == 0:
            return jsonify({
                'success': False,
                'message': '评论不存在'
            }), 404

        return jsonify({
            'success': True,
            'message': '评论删除成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除评论失败: {str(e)}'
        }), 500


@news_bp.route('/v9/news/articles/<int:article_id>/like', methods=['POST'])
def like_article(article_id):
    """点赞文章"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 更新文章点赞数
        cursor.execute("""
            UPDATE news_articles
            SET like_count = like_count + 1
            WHERE id = ?
        """, (article_id,))

        affected_rows = cursor.rowcount
        conn.commit()
        conn.close()

        if affected_rows == 0:
            return jsonify({
                'success': False,
                'message': '文章不存在'
            }), 404

        return jsonify({
            'success': True,
            'message': '点赞成功'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'点赞失败: {str(e)}'
        }), 500

