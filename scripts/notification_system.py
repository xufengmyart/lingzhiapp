#!/usr/bin/env python3
"""
通知系统
支持邮件通知、短信通知、站内通知、推送通知
"""

from flask import request, jsonify
from functools import wraps
import sqlite3
import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from enum import Enum
import threading
import queue

# 配置
DATABASE = 'lingzhi_ecosystem.db'

# 通知类型
class NotificationType(str, Enum):
    SYSTEM = "system"
    ACTIVITY = "activity"
    ASSET = "asset"
    CONTRIBUTION = "contribution"
    PROJECT = "project"
    REMINDER = "reminder"

# 通知渠道
class NotificationChannel(str, Enum):
    EMAIL = "email"
    SMS = "sms"
    IN_APP = "in_app"
    PUSH = "push"

# 通知优先级
class NotificationPriority(str, Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ==================== 通知队列 ====================

class NotificationQueue:
    """通知队列"""

    def __init__(self):
        self.queue = queue.Queue()
        self.workers = []
        self.running = False

    def start(self, num_workers=3):
        """启动工作线程"""
        self.running = True
        for i in range(num_workers):
            worker = threading.Thread(target=self._worker, args=(i,))
            worker.daemon = True
            worker.start()
            self.workers.append(worker)
        print(f"✅ 通知队列已启动，{num_workers} 个工作线程")

    def stop(self):
        """停止工作线程"""
        self.running = False
        for worker in self.workers:
            worker.join()
        print("✅ 通知队列已停止")

    def _worker(self, worker_id):
        """工作线程"""
        while self.running:
            try:
                task = self.queue.get(timeout=1)
                self._process_task(task, worker_id)
                self.queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"工作线程 {worker_id} 处理任务失败: {e}")

    def _process_task(self, task: Dict, worker_id: int):
        """处理通知任务"""
        try:
            notification_id = task.get('notification_id')
            channels = task.get('channels', [])
            user_id = task.get('user_id')
            title = task.get('title')
            content = task.get('content')

            print(f"工作线程 {worker_id} 处理通知 {notification_id}")

            # 根据渠道发送通知
            for channel in channels:
                if channel == NotificationChannel.EMAIL:
                    self._send_email(user_id, title, content)
                elif channel == NotificationChannel.SMS:
                    self._send_sms(user_id, title, content)
                elif channel == NotificationChannel.PUSH:
                    self._send_push(user_id, title, content)

            # 标记为已发送
            self._mark_as_sent(notification_id)

        except Exception as e:
            print(f"处理通知任务失败: {e}")
            self._mark_as_failed(task.get('notification_id'))

    def _send_email(self, user_id: int, title: str, content: str):
        """发送邮件通知"""
        # 这里集成邮件服务
        print(f"发送邮件到用户 {user_id}: {title}")

    def _send_sms(self, user_id: int, title: str, content: str):
        """发送短信通知"""
        # 这里集成短信服务
        print(f"发送短信到用户 {user_id}: {title}")

    def _send_push(self, user_id: int, title: str, content: str):
        """发送推送通知"""
        # 这里集成推送服务
        print(f"发送推送到用户 {user_id}: {title}")

    def _mark_as_sent(self, notification_id: int):
        """标记为已发送"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications
                SET status = 'sent', sent_at = ?
                WHERE id = ?
            ''', (datetime.now(), notification_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"标记通知发送状态失败: {e}")

    def _mark_as_failed(self, notification_id: int):
        """标记为发送失败"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications
                SET status = 'failed'
                WHERE id = ?
            ''', (notification_id,))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"标记通知失败状态失败: {e}")

    def enqueue(self, notification_id: int, channels: List[str], user_id: int, title: str, content: str):
        """入队"""
        task = {
            'notification_id': notification_id,
            'channels': channels,
            'user_id': user_id,
            'title': title,
            'content': content
        }
        self.queue.put(task)

# 全局通知队列
notification_queue = NotificationQueue()

# ==================== 通知管理器 ====================

class NotificationManager:
    """通知管理器"""

    def __init__(self):
        pass

    def create_notification(
        self,
        user_id: int,
        title: str,
        content: str,
        notification_type: str,
        channels: List[str],
        priority: str = "normal",
        related_id: int = None,
        metadata: dict = None
    ) -> int:
        """创建通知"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO notifications
                (user_id, title, content, type, channels, priority, related_id, metadata, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id,
                title,
                content,
                notification_type,
                json.dumps(channels),
                priority,
                related_id,
                json.dumps(metadata or {}),
                'pending',
                datetime.now()
            ))

            notification_id = cursor.lastrowid
            conn.commit()
            conn.close()

            # 如果有外部渠道，加入队列
            external_channels = [c for c in channels if c != NotificationChannel.IN_APP]
            if external_channels:
                notification_queue.enqueue(notification_id, external_channels, user_id, title, content)

            return notification_id

        except Exception as e:
            print(f"创建通知失败: {e}")
            return 0

    def get_user_notifications(
        self,
        user_id: int,
        limit: int = 20,
        offset: int = 0,
        unread_only: bool = False
    ) -> List[Dict]:
        """获取用户通知"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            query = '''
                SELECT * FROM notifications
                WHERE user_id = ?
            '''
            params = [user_id]

            if unread_only:
                query += ' AND is_read = 0'

            query += ' ORDER BY created_at DESC LIMIT ? OFFSET ?'
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()

            return [dict(row) for row in rows]

        except Exception as e:
            print(f"获取用户通知失败: {e}")
            return []

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """标记为已读"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE notifications
                SET is_read = 1, read_at = ?
                WHERE id = ? AND user_id = ?
            ''', (datetime.now(), notification_id, user_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"标记为已读失败: {e}")
            return False

    def mark_all_as_read(self, user_id: int) -> int:
        """标记所有为已读"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE notifications
                SET is_read = 1, read_at = ?
                WHERE user_id = ? AND is_read = 0
            ''', (datetime.now(), user_id))

            count = cursor.rowcount
            conn.commit()
            conn.close()
            return count

        except Exception as e:
            print(f"标记所有为已读失败: {e}")
            return 0

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """删除通知"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                DELETE FROM notifications
                WHERE id = ? AND user_id = ?
            ''', (notification_id, user_id))

            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"删除通知失败: {e}")
            return False

    def get_unread_count(self, user_id: int) -> int:
        """获取未读数量"""
        try:
            conn = get_db()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(*) as count
                FROM notifications
                WHERE user_id = ? AND is_read = 0
            ''', (user_id,))

            count = cursor.fetchone()['count']
            conn.close()
            return count

        except Exception as e:
            print(f"获取未读数量失败: {e}")
            return 0

# 全局通知管理器
notification_manager = NotificationManager()

# ==================== 模板管理器 ====================

class NotificationTemplateManager:
    """通知模板管理器"""

    def __init__(self):
        self.templates = {
            'activity_reminder': {
                'title': '活动提醒',
                'content': '您报名的活动 "{activity_name}" 即将开始！\n时间：{start_time}\n地点：{location}'
            },
            'contribution_approved': {
                'title': '贡献审核通过',
                'content': '您的贡献 "{contribution_title}" 已通过审核，获得 {reward} 灵值奖励！'
            },
            'token_received': {
                'title': '收到转账',
                'content': '您收到 {amount} {token_symbol}，来源：{from_user}'
            },
            'system_announcement': {
                'title': '系统公告',
                'content': '{content}'
            }
        }

    def render_template(self, template_name: str, variables: dict) -> tuple:
        """渲染模板"""
        template = self.templates.get(template_name)
        if not template:
            return "通知", "通知内容"

        title = template['title'].format(**variables)
        content = template['content'].format(**variables)
        return title, content

template_manager = NotificationTemplateManager()

# ==================== 注册 API ====================

def register_notification_apis(app):
    """注册通知系统 API"""

    # 获取通知列表
    @app.route('/api/notifications', methods=['GET'])
    def get_notifications():
        """获取用户通知列表"""
        try:
            user_id = request.args.get('user_id', type=int)
            limit = request.args.get('limit', 20, type=int)
            offset = request.args.get('offset', 0, type=int)
            unread_only = request.args.get('unread_only', 'false').lower() == 'true'

            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '缺少用户ID',
                    'error_code': 'MISSING_USER_ID'
                }), 400

            notifications = notification_manager.get_user_notifications(
                user_id, limit, offset, unread_only
            )

            # 获取未读数量
            unread_count = notification_manager.get_unread_count(user_id)

            return jsonify({
                'success': True,
                'data': {
                    'notifications': notifications,
                    'unread_count': unread_count
                }
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'获取通知列表失败: {str(e)}',
                'error_code': 'GET_NOTIFICATIONS_ERROR'
            }), 500

    # 标记为已读
    @app.route('/api/notifications/<int:notification_id>/read', methods=['PUT'])
    def mark_notification_as_read(notification_id):
        """标记通知为已读"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')

            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '缺少用户ID',
                    'error_code': 'MISSING_USER_ID'
                }), 400

            success = notification_manager.mark_as_read(notification_id, user_id)

            if success:
                return jsonify({
                    'success': True,
                    'message': '已标记为已读'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '标记失败',
                    'error_code': 'MARK_READ_FAILED'
                }), 500

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'标记为已读失败: {str(e)}',
                'error_code': 'MARK_READ_ERROR'
            }), 500

    # 标记所有为已读
    @app.route('/api/notifications/read-all', methods=['PUT'])
    def mark_all_notifications_as_read():
        """标记所有通知为已读"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')

            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '缺少用户ID',
                    'error_code': 'MISSING_USER_ID'
                }), 400

            count = notification_manager.mark_all_as_read(user_id)

            return jsonify({
                'success': True,
                'message': f'已标记 {count} 条通知为已读',
                'data': {'count': count}
            })

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'标记所有为已读失败: {str(e)}',
                'error_code': 'MARK_ALL_READ_ERROR'
            }), 500

    # 创建通知（管理员）
    @app.route('/api/notifications', methods=['POST'])
    def create_notification():
        """创建通知"""
        try:
            data = request.get_json()

            required_fields = ['user_id', 'title', 'content', 'type', 'channels']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'success': False,
                        'message': f'缺少必填字段: {field}',
                        'error_code': 'MISSING_FIELD'
                    }), 400

            notification_id = notification_manager.create_notification(
                user_id=data['user_id'],
                title=data['title'],
                content=data['content'],
                notification_type=data['type'],
                channels=data['channels'],
                priority=data.get('priority', 'normal'),
                related_id=data.get('related_id'),
                metadata=data.get('metadata')
            )

            if notification_id > 0:
                return jsonify({
                    'success': True,
                    'message': '通知创建成功',
                    'data': {'notification_id': notification_id}
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '通知创建失败',
                    'error_code': 'CREATE_NOTIFICATION_FAILED'
                }), 500

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'创建通知失败: {str(e)}',
                'error_code': 'CREATE_NOTIFICATION_ERROR'
            }), 500

    # 删除通知
    @app.route('/api/notifications/<int:notification_id>', methods=['DELETE'])
    def delete_notification(notification_id):
        """删除通知"""
        try:
            data = request.get_json()
            user_id = data.get('user_id')

            if not user_id:
                return jsonify({
                    'success': False,
                    'message': '缺少用户ID',
                    'error_code': 'MISSING_USER_ID'
                }), 400

            success = notification_manager.delete_notification(notification_id, user_id)

            if success:
                return jsonify({
                    'success': True,
                    'message': '通知已删除'
                })
            else:
                return jsonify({
                    'success': False,
                    'message': '删除失败',
                    'error_code': 'DELETE_NOTIFICATION_FAILED'
                }), 500

        except Exception as e:
            return jsonify({
                'success': False,
                'message': f'删除通知失败: {str(e)}',
                'error_code': 'DELETE_NOTIFICATION_ERROR'
            }), 500

    print("✅ 通知系统 API 已注册")
