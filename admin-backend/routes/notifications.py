"""
通知系统 API
功能：
1. 通知的增删改查
2. 通知标记已读/未读
3. 通知偏好设置
4. 通知模板管理
5. 发送通知
"""

import json
import sqlite3
from datetime import datetime
from flask import Blueprint, request, jsonify, g

# 导入JWT认证中间件
from middleware.jwt_auth import require_auth

notifications_bp = Blueprint('notifications', __name__)


def get_db_connection():
    """获取数据库连接"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('/app/meiyueart-backend/data/lingzhi_ecosystem.db')
        db.row_factory = sqlite3.Row
    return db


def get_current_user_id():
    """获取当前用户ID"""
    return getattr(g, 'current_user_id', None)


# ==================== 通知管理 ====================

@notifications_bp.route('/v9/user/notifications', methods=['GET'])
@require_auth
def get_user_notifications_v9():
    """
    获取当前用户的通知列表（v9 版本）
    查询参数：is_read, category, type, page, page_size, sort
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id

        is_read = request.args.get('is_read')
        category = request.args.get('category')
        notification_type = request.args.get('type')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        sort = request.args.get('sort', '-created_at')

        offset = (page - 1) * page_size

        # 构建查询条件
        where_conditions = ["user_id = ?"]
        params = [user_id]

        if is_read is not None and is_read != 'all':
            where_conditions.append("is_read = ?")
            params.append(is_read == 'true')

        if category:
            where_conditions.append("type LIKE ?")
            params.append(f"%{category}%")

        if notification_type:
            where_conditions.append("type = ?")
            params.append(notification_type)

        where_clause = " AND ".join(where_conditions)

        # 构建排序
        if sort == '-created_at':
            order_clause = "ORDER BY created_at DESC"
        elif sort == 'created_at':
            order_clause = "ORDER BY created_at ASC"
        elif sort == 'priority':
            order_clause = "ORDER BY priority DESC, created_at DESC"
        else:
            order_clause = "ORDER BY created_at DESC"

        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM user_notifications WHERE {where_clause}"
        total_result = conn.execute(count_query, params).fetchone()
        total = total_result['total'] if total_result else 0

        # 获取通知列表
        query = f'''
            SELECT * FROM user_notifications
            WHERE {where_clause}
            {order_clause}
            LIMIT ? OFFSET ?
        '''
        params.extend([page_size, offset])

        notifications = conn.execute(query, params).fetchall()

        # 获取未读数量
        unread_count = conn.execute(
            'SELECT COUNT(*) as count FROM user_notifications WHERE user_id = ? AND is_read = 0',
            (user_id,)
        ).fetchone()['count']

        notification_list = []
        for n in notifications:
            notification_list.append({
                'id': n['id'],
                'userId': n['user_id'],
                'type': n['type'],
                'title': n['title'],
                'content': n['content'],
                'isRead': bool(n['is_read']),
                'link': n['link'],
                'data': json.loads(n['data']) if n['data'] else {},
                'createdAt': n['created_at'],
                'readAt': n['read_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取通知成功',
            'data': notification_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            },
            'unreadCount': unread_count
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/v9/notifications', methods=['GET'])
@require_auth
def get_notifications_v9():
    """
    获取当前用户的通知列表（v9 版本 - 路径简化）
    查询参数：page, page_size, sort, is_read, type
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id

        is_read = request.args.get('is_read')
        notification_type = request.args.get('type')
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 10))
        sort = request.args.get('sort', '-created_at')

        offset = (page - 1) * page_size

        # 构建查询条件
        where_conditions = ["user_id = ?"]
        params = [user_id]

        if is_read is not None and is_read != 'all':
            where_conditions.append("is_read = ?")
            params.append(is_read == 'true')

        if notification_type:
            where_conditions.append("type = ?")
            params.append(notification_type)

        where_clause = " AND ".join(where_conditions)

        # 构建排序
        if sort == '-created_at':
            order_clause = "ORDER BY created_at DESC"
        elif sort == 'created_at':
            order_clause = "ORDER BY created_at ASC"
        else:
            order_clause = "ORDER BY created_at DESC"

        # 获取总数
        count_query = f"SELECT COUNT(*) as total FROM user_notifications WHERE {where_clause}"
        total_result = conn.execute(count_query, params).fetchone()
        total = total_result['total'] if total_result else 0

        # 获取通知列表
        query = f'''
            SELECT * FROM user_notifications
            WHERE {where_clause}
            {order_clause}
            LIMIT ? OFFSET ?
        '''
        params.extend([page_size, offset])

        notifications = conn.execute(query, params).fetchall()

        # 获取未读数量
        unread_count = conn.execute(
            'SELECT COUNT(*) as count FROM user_notifications WHERE user_id = ? AND is_read = 0',
            (user_id,)
        ).fetchone()['count']

        notification_list = []
        for n in notifications:
            notification_list.append({
                'id': n['id'],
                'userId': n['user_id'],
                'type': n['type'],
                'title': n['title'],
                'content': n['content'],
                'isRead': bool(n['is_read']),
                'link': n['link'],
                'data': json.loads(n['data']) if n['data'] else {},
                'createdAt': n['created_at'],
                'readAt': n['read_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'message': '获取通知成功',
            'data': notification_list,
            'pagination': {
                'page': page,
                'page_size': page_size,
                'total': total,
                'total_pages': (total + page_size - 1) // page_size
            },
            'unreadCount': unread_count
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/v9/notifications/unread/count', methods=['GET'])
@require_auth
def get_unread_count_v9():
    """获取未读通知数量（v9 版本）"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id

        count = conn.execute(
            'SELECT COUNT(*) as count FROM user_notifications WHERE user_id = ? AND is_read = 0',
            (user_id,)
        ).fetchone()['count']

        conn.close()

        return jsonify({
            'success': True,
            'data': {'count': count}
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/v9/notifications/latest', methods=['GET'])
@require_auth
def get_latest_notifications_v9():
    """获取最新通知（v9 版本）"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id

        since = request.args.get('since')

        query = '''
            SELECT * FROM user_notifications
            WHERE user_id = ?
        '''
        params = [user_id]

        if since:
            query += ' AND created_at > ?'
            params.append(since)

        query += ' ORDER BY created_at DESC LIMIT 10'

        notifications = conn.execute(query, params).fetchall()

        notification_list = []
        for n in notifications:
            notification_list.append({
                'id': n['id'],
                'userId': n['user_id'],
                'type': n['type'],
                'title': n['title'],
                'content': n['content'],
                'isRead': bool(n['is_read']),
                'link': n['link'],
                'data': json.loads(n['data']) if n['data'] else {},
                'createdAt': n['created_at'],
                'readAt': n['read_at']
            })

        conn.close()

        return jsonify({
            'success': True,
            'data': notification_list
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/api/notifications', methods=['GET'])
@require_auth
def get_notifications():
    """
    获取当前用户的通知列表
    查询参数：is_read, type, limit, offset
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        is_read = request.args.get('is_read')
        notification_type = request.args.get('type')
        limit = int(request.args.get('limit', 20))
        offset = int(request.args.get('offset', 0))
        
        query = '''
            SELECT * FROM user_notifications
            WHERE user_id = ?
        '''
        params = [user_id]
        
        if is_read is not None:
            query += ' AND is_read = ?'
            params.append(is_read == 'true')
        
        if notification_type:
            query += ' AND notification_type = ?'
            params.append(notification_type)
        
        query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])
        
        notifications = conn.execute(query, params).fetchall()
        
        # 获取未读数量
        unread_count = conn.execute(
            'SELECT COUNT(*) as count FROM user_notifications WHERE user_id = ? AND is_read = 0',
            (user_id,)
        ).fetchone()['count']
        
        notification_list = []
        for n in notifications:
            notification_list.append({
                'id': n['id'],
                'notificationType': n['notification_type'],
                'title': n['title'],
                'content': n['content'],
                'relatedType': n['related_type'],
                'relatedId': n['related_id'],
                'priority': n['priority'],
                'isRead': bool(n['is_read']),
                'readAt': n['read_at'],
                'createdAt': n['created_at'],
                'metadata': json.loads(n['metadata']) if n['metadata'] else {}
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取通知成功',
            'data': {
                'notifications': notification_list,
                'unreadCount': unread_count,
                'total': len(notification_list)
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/api/notifications/<int:notification_id>/read', methods=['POST'])
@require_auth
def mark_notification_read(notification_id):
    """标记通知为已读"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 检查通知是否属于当前用户
        notification = conn.execute(
            'SELECT * FROM user_notifications WHERE id = ? AND user_id = ?',
            (notification_id, user_id)
        ).fetchone()
        
        if not notification:
            return jsonify({'success': False, 'message': '通知不存在'}), 404
        
        # 标记为已读
        conn.execute(
            'UPDATE user_notifications SET is_read = 1, read_at = ? WHERE id = ?',
            (datetime.now().isoformat(), notification_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '标记成功'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/api/notifications/read-all', methods=['POST'])
@require_auth
def mark_all_notifications_read():
    """标记所有通知为已读"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        conn.execute(
            'UPDATE user_notifications SET is_read = 1, read_at = ? WHERE user_id = ? AND is_read = 0',
            (datetime.now().isoformat(), user_id)
        )
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '全部标记为已读'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
@require_auth
def delete_notification(notification_id):
    """删除通知"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 检查通知是否属于当前用户
        notification = conn.execute(
            'SELECT * FROM user_notifications WHERE id = ? AND user_id = ?',
            (notification_id, user_id)
        ).fetchone()
        
        if not notification:
            return jsonify({'success': False, 'message': '通知不存在'}), 404
        
        conn.execute('DELETE FROM user_notifications WHERE id = ?', (notification_id,))
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '删除成功'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 通知偏好设置 ====================

@notifications_bp.route('/api/notification-preferences', methods=['GET'])
@require_auth
def get_notification_preferences():
    """获取当前用户的通知偏好设置"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        preferences = conn.execute(
            'SELECT * FROM notification_preferences WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if not preferences:
            # 创建默认偏好设置
            conn.execute(
                '''INSERT INTO notification_preferences (user_id) VALUES (?)''',
                (user_id,)
            )
            conn.commit()
            
            preferences = conn.execute(
                'SELECT * FROM notification_preferences WHERE user_id = ?',
                (user_id,)
            ).fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取偏好设置成功',
            'data': {
                'emailNotifications': bool(preferences['email_notifications']),
                'pushNotifications': bool(preferences['push_notifications']),
                'smsNotifications': bool(preferences['sms_notifications']),
                'resourceMatchNotifications': bool(preferences['resource_match_notifications']),
                'projectUpdates': bool(preferences['project_updates']),
                'profitNotifications': bool(preferences['profit_notifications']),
                'systemNotifications': bool(preferences['system_notifications'])
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@notifications_bp.route('/api/notification-preferences', methods=['PUT'])
@require_auth
def update_notification_preferences():
    """更新通知偏好设置"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        data = request.get_json()
        
        # 确保偏好设置存在
        preferences = conn.execute(
            'SELECT * FROM notification_preferences WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        if not preferences:
            conn.execute(
                '''INSERT INTO notification_preferences (user_id) VALUES (?)''',
                (user_id,)
            )
        
        # 构建更新SQL
        update_fields = []
        update_values = []
        
        field_mapping = {
            'emailNotifications': 'email_notifications',
            'pushNotifications': 'push_notifications',
            'smsNotifications': 'sms_notifications',
            'resourceMatchNotifications': 'resource_match_notifications',
            'projectUpdates': 'project_updates',
            'profitNotifications': 'profit_notifications',
            'systemNotifications': 'system_notifications'
        }
        
        for key, db_field in field_mapping.items():
            if key in data:
                update_fields.append(f'{db_field} = ?')
                update_values.append(1 if data[key] else 0)
        
        if update_fields:
            update_values.append(user_id)
            conn.execute(
                f'UPDATE notification_preferences SET {", ".join(update_fields)} WHERE user_id = ?',
                update_values
            )
            conn.commit()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '偏好设置更新成功'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 发送通知 ====================

def send_notification(
    user_id: int,
    notification_type: str,
    title: str,
    content: str = None,
    related_type: str = None,
    related_id: int = None,
    priority: str = 'normal',
    metadata: dict = None
):
    """
    发送通知的内部函数
    
    参数:
        user_id: 接收通知的用户ID
        notification_type: 通知类型
        title: 通知标题
        content: 通知内容
        related_type: 关联类型
        related_id: 关联ID
        priority: 优先级
        metadata: 元数据
    """
    try:
        conn = get_db_connection()
        
        # 检查用户是否关闭了该类型的通知
        preferences = conn.execute(
            'SELECT * FROM notification_preferences WHERE user_id = ?',
            (user_id,)
        ).fetchone()
        
        should_send = True
        if preferences:
            if notification_type == 'resource_match' and not preferences['resource_match_notifications']:
                should_send = False
            elif notification_type == 'project_application' and not preferences['project_updates']:
                should_send = False
            elif notification_type == 'profit_distribution' and not preferences['profit_notifications']:
                should_send = False
            elif notification_type == 'system' and not preferences['system_notifications']:
                should_send = False
        
        if should_send:
            conn.execute(
                '''INSERT INTO user_notifications
                (user_id, notification_type, title, content, related_type, related_id, priority, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                (
                    user_id,
                    notification_type,
                    title,
                    content,
                    related_type,
                    related_id,
                    priority,
                    json.dumps(metadata) if metadata else None
                )
            )
            conn.commit()
        
        conn.close()
        return True
    except Exception as e:
        print(f"发送通知失败: {e}")
        return False


@notifications_bp.route('/api/notifications/send', methods=['POST'])
def send_notification_api():
    """
    发送通知API（内部调用）
    """
    try:
        data = request.get_json()
        
        required_fields = ['userId', 'notificationType', 'title']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'message': f'缺少必填字段: {field}'}), 400
        
        success = send_notification(
            user_id=data.get('userId'),
            notification_type=data.get('notificationType'),
            title=data.get('title'),
            content=data.get('content'),
            related_type=data.get('relatedType'),
            related_id=data.get('relatedId'),
            priority=data.get('priority', 'normal'),
            metadata=data.get('metadata')
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': '通知发送成功'
            })
        else:
            return jsonify({
                'success': False,
                'message': '通知发送失败'
            }), 500
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 通知统计 ====================

@notifications_bp.route('/api/notifications/statistics', methods=['GET'])
@require_auth
def get_notification_statistics():
    """获取通知统计"""
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 按类型统计
        type_stats = conn.execute('''
            SELECT 
                notification_type,
                COUNT(*) as total,
                SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread
            FROM user_notifications
            WHERE user_id = ?
            GROUP BY notification_type
        ''', (user_id,)).fetchall()
        
        # 按优先级统计
        priority_stats = conn.execute('''
            SELECT 
                priority,
                COUNT(*) as total,
                SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread
            FROM user_notifications
            WHERE user_id = ?
            GROUP BY priority
        ''', (user_id,)).fetchall()
        
        # 总体统计
        total_stats = conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN is_read = 0 THEN 1 ELSE 0 END) as unread,
                SUM(CASE WHEN priority = 'urgent' AND is_read = 0 THEN 1 ELSE 0 END) as urgent_unread
            FROM user_notifications
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取统计成功',
            'data': {
                'byType': [
                    {
                        'type': stat['notification_type'],
                        'total': stat['total'],
                        'unread': stat['unread']
                    }
                    for stat in type_stats
                ],
                'byPriority': [
                    {
                        'priority': stat['priority'],
                        'total': stat['total'],
                        'unread': stat['unread']
                    }
                    for stat in priority_stats
                ],
                'total': total_stats['total'],
                'unread': total_stats['unread'],
                'urgentUnread': total_stats['urgent_unread']
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
