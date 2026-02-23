"""
文章评论路由蓝图
提供文章评论的增删改查功能
"""

from flask import Blueprint, jsonify, request, g
import sys
import os
import json
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from middleware.jwt_auth import require_auth

comments_bp = Blueprint('comments', __name__)

# ==================== 评论列表 ====================

@comments_bp.route('/v9/news/articles/<int:article_id>/comments', methods=['GET'])
def get_comments(article_id):
    """获取文章评论列表"""
    try:
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

        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        offset = (page - 1) * page_size

        # 获取评论总数
        cursor.execute("SELECT COUNT(*) as total FROM news_comments WHERE article_id = ?", (article_id,))
        total_result = cursor.fetchone()
        total = total_result['total'] if total_result else 0

        # 获取评论列表
        cursor.execute('''
            SELECT * FROM news_comments
            WHERE article_id = ? AND status = 'approved'
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        ''', (article_id, page_size, offset))

        comments = []
        for row in cursor.fetchall():
            comments.append({
                'id': row['id'],
                'articleId': row['article_id'],
                'userId': row['user_id'],
                'userName': row['user_name'],
                'userAvatar': row['user_avatar'],
                'content': row['content'],
                'parentId': row['parent_id'],
                'likeCount': row['like_count'],
                'status': row['status'],
                'createdAt': row['created_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取评论成功',
            'data': comments,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            }
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'获取评论失败: {str(e)}',
            'data': []
        }), 500


# ==================== 创建评论 ====================

@comments_bp.route('/v9/news/articles/<int:article_id>/comments', methods=['POST'])
@require_auth
def create_comment(article_id):
    """创建文章评论"""
    try:
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

        data = request.get_json()
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')

        if not content:
            conn.close()
            return jsonify({
                'success': False,
                'message': '评论内容不能为空'
            }), 400

        # 获取用户信息
        cursor.execute("SELECT id, username, avatar_url FROM users WHERE id = ?", (g.current_user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 创建评论
        cursor.execute('''
            INSERT INTO news_comments (article_id, user_id, user_name, user_avatar, content, parent_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, 'approved', ?)
        ''', (
            article_id,
            g.current_user_id,
            user['username'],
            user['avatar_url'] or '/uploads/avatars/default.png',
            content,
            parent_id,
            datetime.now()
        ))

        # 更新文章评论数
        cursor.execute(
            'UPDATE news_articles SET comment_count = comment_count + 1 WHERE id = ?',
            (article_id,)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '评论成功'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'评论失败: {str(e)}'
        }), 500


# ==================== 删除评论 ====================

@comments_bp.route('/v9/news/comments/<int:comment_id>', methods=['DELETE'])
@require_auth
def delete_comment(comment_id):
    """删除评论"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查评论是否存在
        cursor.execute("SELECT id, article_id, user_id FROM news_comments WHERE id = ?", (comment_id,))
        comment = cursor.fetchone()
        if not comment:
            conn.close()
            return jsonify({
                'success': False,
                'message': '评论不存在'
            }), 404

        # 检查权限（只能删除自己的评论）
        if comment['user_id'] != g.current_user_id:
            conn.close()
            return jsonify({
                'success': False,
                'message': '无权限删除此评论'
            }), 403

        # 删除评论
        cursor.execute('DELETE FROM news_comments WHERE id = ?', (comment_id,))

        # 更新文章评论数
        cursor.execute(
            'UPDATE news_articles SET comment_count = comment_count - 1 WHERE id = ?',
            (comment['article_id'],)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '删除成功'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}'
        }), 500


# ==================== 点赞评论 ====================

@comments_bp.route('/v9/news/comments/<int:comment_id>/like', methods=['POST'])
@require_auth
def like_comment(comment_id):
    """点赞评论"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 检查评论是否存在
        cursor.execute("SELECT id FROM news_comments WHERE id = ?", (comment_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({
                'success': False,
                'message': '评论不存在'
            }), 404

        # 更新点赞数
        cursor.execute(
            'UPDATE news_comments SET like_count = like_count + 1 WHERE id = ?',
            (comment_id,)
        )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '点赞成功'
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'点赞失败: {str(e)}'
        }), 500
