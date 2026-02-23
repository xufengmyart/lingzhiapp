# -*- coding: utf-8 -*-
"""
平台信息增强功能API
包括：推送、阅读状态、订阅、评论、分享功能
"""

from flask import Blueprint, jsonify, request
import sys
import os
from datetime import datetime
import random
import string

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
import jwt
from config import config

platform_info_enhanced_bp = Blueprint('platform_info_enhanced', __name__)

JWT_SECRET = config.JWT_SECRET_KEY

def get_user_id_from_token():
    """从token中获取用户ID"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return None
    
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload.get('user_id')
    except:
        return None

# ============ 1. 推送功能 ============

@platform_info_enhanced_bp.route('/v9/platform-info/<int:info_id>/push', methods=['POST'])
def push_platform_info(info_id):
    """推送平台信息"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        # 检查用户是否是管理员
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if not user or user['username'] != 'admin':
            conn.close()
            return jsonify({'success': False, 'message': '需要管理员权限'}), 403
        
        data = request.get_json()
        push_type = data.get('push_type', 'all')  # all, subscribed, important
        target_type = data.get('target_type', 'all')  # all, users, specific
        target_ids = data.get('target_ids', '')
        
        # 获取平台信息
        cursor.execute('SELECT title, summary, importance_level FROM news_articles WHERE id = ?', (info_id,))
        info = cursor.fetchone()
        
        if not info:
            conn.close()
            return jsonify({'success': False, 'message': '平台信息不存在'}), 404
        
        # 创建推送记录
        cursor.execute('''
            INSERT INTO platform_info_pushes (
                platform_info_id, push_type, target_type, target_ids,
                title, content, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, 'pending', CURRENT_TIMESTAMP)
        ''', (info_id, push_type, target_type, target_ids, info['title'], info['summary']))
        
        push_id = cursor.lastrowid
        
        # 模拟推送（实际项目中应接入推送服务）
        # 这里只是记录推送任务
        cursor.execute('''
            UPDATE platform_info_pushes
            SET status = 'sent', sent_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (push_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '推送任务已创建',
            'data': {
                'push_id': push_id,
                'push_type': push_type,
                'target_type': target_type
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ 2. 阅读状态功能 ============

@platform_info_enhanced_bp.route('/v9/platform-info/<int:info_id>/read', methods=['POST'])
def mark_as_read(info_id):
    """标记为已读"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否已读
        cursor.execute('''
            SELECT id FROM platform_info_reads
            WHERE user_id = ? AND platform_info_id = ?
        ''', (user_id, info_id))
        
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': True, 'message': '已经标记为已读'})
        
        # 标记为已读
        cursor.execute('''
            INSERT INTO platform_info_reads (user_id, platform_info_id, read_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, info_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '已标记为已读'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@platform_info_enhanced_bp.route('/v9/platform-info/read-status', methods=['GET'])
def get_read_status():
    """获取阅读状态"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        info_ids = request.args.get('info_ids', '')
        if not info_ids:
            return jsonify({'success': False, 'message': '请提供信息ID列表'}), 400
        
        info_id_list = [int(x) for x in info_ids.split(',')]
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 构建占位符
        placeholders = ','.join('?' * len(info_id_list))
        
        cursor.execute(f'''
            SELECT platform_info_id
            FROM platform_info_reads
            WHERE user_id = ? AND platform_info_id IN ({placeholders})
        ''', [user_id] + info_id_list)
        
        read_ids = [row['platform_info_id'] for row in cursor.fetchall()]
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'read_ids': read_ids,
                'total_read': len(read_ids),
                'total': len(info_id_list)
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@platform_info_enhanced_bp.route('/v9/platform-info/unread-count', methods=['GET'])
def get_unread_count():
    """获取未读数量"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取平台信息分类ID
        cursor.execute("SELECT id FROM news_categories WHERE slug = 'platform-info'")
        platform_cat = cursor.fetchone()
        
        if not platform_cat:
            conn.close()
            return jsonify({'success': False, 'message': '平台信息分类不存在'}), 404
        
        category_id = platform_cat['id']
        
        # 获取未读数量
        cursor.execute(f'''
            SELECT COUNT(*) as total
            FROM news_articles n
            WHERE n.category_id = ? AND n.status = 'published'
                AND n.id NOT IN (
                    SELECT platform_info_id
                    FROM platform_info_reads
                    WHERE user_id = ?
                )
        ''', (category_id, user_id))
        
        result = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'unread_count': result['total'] if result else 0
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ 3. 订阅功能 ============

@platform_info_enhanced_bp.route('/v9/platform-info/subscribe', methods=['POST'])
def subscribe_platform_info():
    """订阅平台信息"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        data = request.get_json()
        info_type = data.get('info_type')
        importance_level = data.get('importance_level')
        
        if not info_type:
            return jsonify({'success': False, 'message': '请提供信息类型'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否已订阅
        cursor.execute('''
            SELECT id FROM platform_info_subscriptions
            WHERE user_id = ? AND info_type = ? AND is_active = 1
        ''', (user_id, info_type))
        
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': False, 'message': '已经订阅该类型'}), 400
        
        # 创建订阅
        cursor.execute('''
            INSERT INTO platform_info_subscriptions
            (user_id, info_type, importance_level, subscribed_at, is_active)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, 1)
        ''', (user_id, info_type, importance_level))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '订阅成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@platform_info_enhanced_bp.route('/v9/platform-info/unsubscribe', methods=['POST'])
def unsubscribe_platform_info():
    """取消订阅"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        data = request.get_json()
        info_type = data.get('info_type')
        
        if not info_type:
            return jsonify({'success': False, 'message': '请提供信息类型'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 取消订阅
        cursor.execute('''
            UPDATE platform_info_subscriptions
            SET is_active = 0
            WHERE user_id = ? AND info_type = ?
        ''', (user_id, info_type))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '取消订阅成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@platform_info_enhanced_bp.route('/v9/platform-info/subscriptions', methods=['GET'])
def get_subscriptions():
    """获取订阅列表"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, info_type, importance_level, subscribed_at, is_active
            FROM platform_info_subscriptions
            WHERE user_id = ? AND is_active = 1
            ORDER BY subscribed_at DESC
        ''', (user_id,))
        
        subscriptions = []
        for row in cursor.fetchall():
            subscriptions.append({
                'id': row['id'],
                'infoType': row['info_type'],
                'importanceLevel': row['importance_level'],
                'subscribedAt': row['subscribed_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': subscriptions
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ 4. 评论功能 ============

@platform_info_enhanced_bp.route('/v9/platform-info/<int:info_id>/comments', methods=['GET'])
def get_comments(info_id):
    """获取评论列表"""
    try:
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 20, type=int)
        offset = (page - 1) * page_size
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取总数
        cursor.execute('''
            SELECT COUNT(*) as total FROM platform_info_comments
            WHERE platform_info_id = ? AND is_deleted = 0
        ''', (info_id,))
        total = cursor.fetchone()['total']
        
        # 获取评论列表
        cursor.execute('''
            SELECT 
                c.id, c.user_id, c.content, c.parent_id,
                c.like_count, c.reply_count, c.created_at,
                u.username, u.nickname
            FROM platform_info_comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.platform_info_id = ? AND c.is_deleted = 0
                AND c.parent_id IS NULL
            ORDER BY c.created_at DESC
            LIMIT ? OFFSET ?
        ''', (info_id, page_size, offset))
        
        comments = []
        for row in cursor.fetchall():
            # 获取回复
            cursor.execute('''
                SELECT 
                    c.id, c.user_id, c.content,
                    c.like_count, c.created_at,
                    u.username, u.nickname
                FROM platform_info_comments c
                JOIN users u ON c.user_id = u.id
                WHERE c.parent_id = ? AND c.is_deleted = 0
                ORDER BY c.created_at ASC
                LIMIT 5
            ''', (row['id'],))
            
            replies = []
            for reply_row in cursor.fetchall():
                replies.append({
                    'id': reply_row['id'],
                    'userId': reply_row['user_id'],
                    'username': reply_row['username'],
                    'nickname': reply_row['nickname'],
                    'content': reply_row['content'],
                    'likeCount': reply_row['like_count'],
                    'createdAt': reply_row['created_at']
                })
            
            comments.append({
                'id': row['id'],
                'userId': row['user_id'],
                'username': row['username'],
                'nickname': row['nickname'],
                'content': row['content'],
                'likeCount': row['like_count'],
                'replyCount': row['reply_count'],
                'replies': replies,
                'createdAt': row['created_at']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': comments,
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'total': total
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@platform_info_enhanced_bp.route('/v9/platform-info/<int:info_id>/comments', methods=['POST'])
def create_comment(info_id):
    """创建评论"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        data = request.get_json()
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        
        if not content:
            return jsonify({'success': False, 'message': '评论内容不能为空'}), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 创建评论
        cursor.execute('''
            INSERT INTO platform_info_comments
            (platform_info_id, user_id, content, parent_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        ''', (info_id, user_id, content, parent_id))
        
        comment_id = cursor.lastrowid
        
        # 如果是回复，更新父评论的回复数
        if parent_id:
            cursor.execute('''
                UPDATE platform_info_comments
                SET reply_count = reply_count + 1
                WHERE id = ?
            ''', (parent_id,))
        
        # 更新文章的评论数
        cursor.execute('''
            UPDATE news_articles
            SET comment_count = comment_count + 1
            WHERE id = ?
        ''', (info_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '评论成功',
            'data': {'comment_id': comment_id}
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@platform_info_enhanced_bp.route('/v9/platform-info/comments/<int:comment_id>/like', methods=['POST'])
def like_comment(comment_id):
    """点赞评论"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否已点赞
        # 简化实现：直接增加点赞数
        cursor.execute('''
            UPDATE platform_info_comments
            SET like_count = like_count + 1
            WHERE id = ?
        ''', (comment_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '点赞成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ 5. 点赞功能 ============

@platform_info_enhanced_bp.route('/v9/platform-info/<int:info_id>/like', methods=['POST'])
def like_platform_info(info_id):
    """点赞平台信息"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 检查是否已点赞
        cursor.execute('''
            SELECT id FROM platform_info_likes
            WHERE user_id = ? AND platform_info_id = ?
        ''', (user_id, info_id))
        
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({'success': False, 'message': '已经点赞'}), 400
        
        # 创建点赞记录
        cursor.execute('''
            INSERT INTO platform_info_likes (user_id, platform_info_id, liked_at)
            VALUES (?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, info_id))
        
        # 更新文章点赞数
        cursor.execute('''
            UPDATE news_articles
            SET like_count = like_count + 1
            WHERE id = ?
        ''', (info_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '点赞成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@platform_info_enhanced_bp.route('/v9/platform-info/<int:info_id>/unlike', methods=['POST'])
def unlike_platform_info(info_id):
    """取消点赞"""
    try:
        user_id = get_user_id_from_token()
        if not user_id:
            return jsonify({'success': False, 'message': '未授权'}), 401
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 删除点赞记录
        cursor.execute('''
            DELETE FROM platform_info_likes
            WHERE user_id = ? AND platform_info_id = ?
        ''', (user_id, info_id))
        
        # 更新文章点赞数
        if cursor.rowcount > 0:
            cursor.execute('''
                UPDATE news_articles
                SET like_count = like_count - 1
                WHERE id = ?
            ''', (info_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '取消点赞成功'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ============ 6. 分享功能 ============

@platform_info_enhanced_bp.route('/v9/platform-info/<int:info_id>/share', methods=['POST'])
def share_platform_info(info_id):
    """生成分享链接"""
    try:
        user_id = get_user_id_from_token()
        data = request.get_json()
        platform = data.get('platform', 'link')  # link, wechat, weibo, qq
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取平台信息
        cursor.execute('SELECT title, slug FROM news_articles WHERE id = ?', (info_id,))
        info = cursor.fetchone()
        
        if not info:
            conn.close()
            return jsonify({'success': False, 'message': '平台信息不存在'}), 404
        
        # 生成推荐码
        referral_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        
        # 生成分享链接
        share_url = f"https://meiyueart.com/platform-info/{info['slug']}?ref={referral_code}"
        
        # 记录分享
        cursor.execute('''
            INSERT INTO platform_info_shares
            (user_id, platform_info_id, platform, share_url, referral_code, created_at)
            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (user_id, info_id, platform, share_url, referral_code))
        
        # 更新文章分享数（需要在news_articles表添加share_count字段）
        # 这里简化处理
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '分享链接生成成功',
            'data': {
                'shareUrl': share_url,
                'referralCode': referral_code,
                'platform': platform
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@platform_info_enhanced_bp.route('/v9/platform-info/<int:info_id>/share-stats', methods=['GET'])
def get_share_stats(info_id):
    """获取分享统计"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_shares,
                COUNT(DISTINCT platform) as unique_platforms
            FROM platform_info_shares
            WHERE platform_info_id = ?
        ''', (info_id,))
        
        stats = cursor.fetchone()
        
        # 按平台统计
        cursor.execute('''
            SELECT platform, COUNT(*) as count
            FROM platform_info_shares
            WHERE platform_info_id = ?
            GROUP BY platform
        ''', (info_id,))
        
        by_platform = {}
        for row in cursor.fetchall():
            by_platform[row['platform']] = row['count']
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': {
                'totalShares': stats['total_shares'] if stats else 0,
                'uniquePlatforms': stats['unique_platforms'] if stats else 0,
                'byPlatform': by_platform
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
