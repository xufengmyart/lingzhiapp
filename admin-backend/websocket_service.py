"""
WebSocket实时推送服务
用于推送用户活动、通知等实时信息
"""

from flask_socketio import SocketIO, emit, join_room, leave_room
from flask import request
import logging

logger = logging.getLogger(__name__)

# 创建SocketIO实例
socketio = SocketIO(cors_allowed_origins="*", async_mode='threading')

# 全局变量
_connected_clients = {}

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    from database import get_db
    import jwt
    from config import config

    try:
        # 获取token
        token = request.args.get('token')

        if token:
            # 验证token
            try:
                payload = jwt.decode(token, config.JWT_SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                username = payload.get('username')

                if user_id:
                    # 加入用户房间
                    join_room(f'user_{user_id}')
                    _connected_clients[request.sid] = {
                        'user_id': user_id,
                        'username': username
                    }

                    logger.info(f"用户 {username} (ID: {user_id}) 已连接")
                    emit('connected', {'message': '连接成功', 'user_id': user_id})
                else:
                    emit('error', {'message': 'Token无效'})
            except Exception as e:
                logger.error(f"Token验证失败: {e}")
                emit('error', {'message': 'Token验证失败'})
        else:
            # 匿名连接，只能接收公共通知
            join_room('public')
            logger.info(f"匿名客户端已连接")
            emit('connected', {'message': '连接成功（只读模式）'})

    except Exception as e:
        logger.error(f"连接处理失败: {e}")
        emit('error', {'message': '连接失败'})

@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    if request.sid in _connected_clients:
        client = _connected_clients[request.sid]
        user_id = client['user_id']
        username = client['username']

        leave_room(f'user_{user_id}')
        del _connected_clients[request.sid]

        logger.info(f"用户 {username} (ID: {user_id}) 已断开连接")

@socketio.on('subscribe_activities')
def handle_subscribe_activities(data):
    """订阅用户活动更新"""
    user_id = data.get('user_id')

    if user_id:
        join_room(f'activities_{user_id}')
        emit('subscribed', {'room': f'activities_{user_id}'})
        logger.info(f"客户端订阅用户 {user_id} 的活动更新")

@socketio.on('unsubscribe_activities')
def handle_unsubscribe_activities(data):
    """取消订阅用户活动更新"""
    user_id = data.get('user_id')

    if user_id:
        leave_room(f'activities_{user_id}')
        emit('unsubscribed', {'room': f'activities_{user_id}'})
        logger.info(f"客户端取消订阅用户 {user_id} 的活动更新")

# ==================== 推送函数 ====================

def push_user_activity(activity_data):
    """
    推送用户活动
    activity_data: {
        'id': int,
        'username': str,
        'action': str,
        'description': str,
        'type': str,
        'createdAt': str,
        'lingzhi': int
    }
    """
    try:
        # 推送到公共房间（所有连接的客户端）
        socketio.emit('new_activity', activity_data, room='public')
        logger.info(f"推送新活动: {activity_data.get('action')} - {activity_data.get('username')}")
    except Exception as e:
        logger.error(f"推送用户活动失败: {e}")

def push_notification(user_id, notification_data):
    """
    推送用户通知
    notification_data: {
        'title': str,
        'message': str,
        'type': str,
        'createdAt': str
    }
    """
    try:
        # 推送到特定用户的房间
        socketio.emit('new_notification', notification_data, room=f'user_{user_id}')
        logger.info(f"推送通知给用户 {user_id}")
    except Exception as e:
        logger.error(f"推送通知失败: {e}")

def push_global_message(message_data):
    """
    推送全局消息
    message_data: {
        'title': str,
        'message': str,
        'priority': str,
        'createdAt': str
    }
    """
    try:
        # 推送到所有连接的客户端
        socketio.emit('global_message', message_data)
        logger.info(f"推送全局消息: {message_data.get('title')}")
    except Exception as e:
        logger.error(f"推送全局消息失败: {e}")

def get_connected_users():
    """获取在线用户列表"""
    return list(_connected_clients.values())

def get_online_count():
    """获取在线人数"""
    return len(_connected_clients)
