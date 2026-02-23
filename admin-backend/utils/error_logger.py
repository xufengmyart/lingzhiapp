"""
错误日志收集模块
统一收集前后端错误日志
"""

import traceback
import json
from datetime import datetime, timedelta
from flask import request, g
from database import get_db


class ErrorLogger:
    def __init__(self):
        pass
    
    def log_error(self, error_type, message, stack_trace=None, context=None):
        """记录错误日志"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # 确保表存在
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS error_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    error_type VARCHAR(100) NOT NULL,
                    message TEXT NOT NULL,
                    stack_trace TEXT,
                    context TEXT,
                    user_id INTEGER,
                    ip_address VARCHAR(50),
                    user_agent TEXT,
                    request_url TEXT,
                    request_method VARCHAR(10),
                    severity VARCHAR(20) DEFAULT 'error',
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 获取请求上下文
            ip_address = request.remote_addr if request else None
            user_agent = request.headers.get('User-Agent') if request else None
            request_url = request.url if request else None
            request_method = request.method if request else None
            user_id = getattr(g, 'user_id', None)
            
            # 确定严重性
            severity = self._determine_severity(error_type, message)
            
            cursor.execute("""
                INSERT INTO error_logs 
                (error_type, message, stack_trace, context, user_id, ip_address, user_agent, 
                 request_url, request_method, severity)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                error_type,
                message,
                stack_trace,
                json.dumps(context) if context else None,
                user_id,
                ip_address,
                user_agent,
                request_url,
                request_method,
                severity
            ))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"记录错误日志失败: {str(e)}")
    
    def _determine_severity(self, error_type, message):
        """确定错误严重性"""
        critical_keywords = ['database', 'security', 'authentication', 'authorization']
        warning_keywords = ['timeout', 'connection', 'network']
        
        message_lower = message.lower()
        
        for keyword in critical_keywords:
            if keyword in message_lower or keyword in error_type.lower():
                return 'critical'
        
        for keyword in warning_keywords:
            if keyword in message_lower or keyword in error_type.lower():
                return 'warning'
        
        return 'error'
    
    def get_recent_errors(self, limit=50, hours=24):
        """获取最近的错误日志"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            start_time = datetime.now() - timedelta(hours=hours) if hours else datetime.min
            
            cursor.execute("""
                SELECT * FROM error_logs
                WHERE created_at >= ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (start_time, limit))
            
            errors = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'id': row[0],
                    'error_type': row[1],
                    'message': row[2],
                    'stack_trace': row[3],
                    'context': json.loads(row[4]) if row[4] else None,
                    'user_id': row[5],
                    'ip_address': row[6],
                    'user_agent': row[7],
                    'request_url': row[8],
                    'request_method': row[9],
                    'severity': row[10],
                    'resolved': row[11],
                    'created_at': row[12]
                }
                for row in errors
            ]
        except Exception as e:
            print(f"获取错误日志失败: {str(e)}")
            return []
    
    def mark_resolved(self, error_id):
        """标记错误为已解决"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE error_logs
                SET resolved = TRUE
                WHERE id = ?
            """, (error_id,))
            
            conn.commit()
            conn.close()
            
            return True
        except Exception as e:
            print(f"标记错误已解决失败: {str(e)}")
            return False


# 创建全局错误日志实例
error_logger = ErrorLogger()


def log_exception(exception):
    """记录异常"""
    error_type = type(exception).__name__
    message = str(exception)
    stack_trace = traceback.format_exc()
    
    error_logger.log_error(
        error_type=error_type,
        message=message,
        stack_trace=stack_trace
    )


def log_error_message(error_type, message, context=None):
    """记录错误消息"""
    error_logger.log_error(
        error_type=error_type,
        message=message,
        context=context
    )
