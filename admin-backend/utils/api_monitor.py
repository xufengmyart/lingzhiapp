"""
API性能监控模块
跟踪API请求时间、成功率等指标
"""

import time
import json
from datetime import datetime, timedelta
from functools import wraps
from flask import request, g
from database import get_db

class APIMonitor:
    def __init__(self):
        self.metrics = {}
    
    def record_request(self, endpoint, method, status_code, response_time):
        """记录API请求指标"""
        key = f"{method}:{endpoint}"
        
        if key not in self.metrics:
            self.metrics[key] = {
                'endpoint': endpoint,
                'method': method,
                'count': 0,
                'success_count': 0,
                'error_count': 0,
                'total_response_time': 0,
                'min_response_time': float('inf'),
                'max_response_time': 0,
                'last_error': None,
                'errors': []
            }
        
        metric = self.metrics[key]
        metric['count'] += 1
        metric['total_response_time'] += response_time
        metric['min_response_time'] = min(metric['min_response_time'], response_time)
        metric['max_response_time'] = max(metric['max_response_time'], response_time)
        
        if status_code < 400:
            metric['success_count'] += 1
        else:
            metric['error_count'] += 1
            metric['last_error'] = {
                'status_code': status_code,
                'timestamp': datetime.now().isoformat()
            }
        
        # 保存到数据库
        self.save_to_database(endpoint, method, status_code, response_time)
    
    def save_to_database(self, endpoint, method, status_code, response_time):
        """保存指标到数据库"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # 确保表存在
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    endpoint VARCHAR(255) NOT NULL,
                    method VARCHAR(10) NOT NULL,
                    status_code INTEGER NOT NULL,
                    response_time FLOAT NOT NULL,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            cursor.execute("""
                INSERT INTO api_metrics (endpoint, method, status_code, response_time)
                VALUES (?, ?, ?, ?)
            """, (endpoint, method, status_code, response_time))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"保存API指标失败: {str(e)}")
    
    def get_metric_history(self, start_time):
        """获取指标历史数据"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    strftime('%Y-%m-%d %H:00:00', timestamp) as hour,
                    AVG(response_time) as avg_response_time,
                    SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as success_count,
                    SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
                FROM api_metrics
                WHERE timestamp >= ?
                GROUP BY hour
                ORDER BY hour
                LIMIT 24
            """, (start_time,))
            
            rows = cursor.fetchall()
            
            history = []
            for row in rows:
                total = row[2] + row[3]
                history.append({
                    'timestamp': datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'),
                    'avgResponseTime': round(row[1], 2) if row[1] else 0,
                    'p95ResponseTime': 0,
                    'p99ResponseTime': 0,
                    'successRate': round(row[2] / total * 100, 2) if total > 0 else 0,
                    'errorRate': round(row[3] / total * 100, 2) if total > 0 else 0
                })
            
            conn.close()
            return history
        except Exception as e:
            print(f"获取指标历史失败: {str(e)}")
            return []
    
    def get_stats(self, endpoint=None, hours=24):
        """获取API统计信息"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
            # 计算时间范围
            start_time = datetime.now() - timedelta(hours=hours)
            
            if endpoint:
                cursor.execute("""
                    SELECT 
                        endpoint,
                        method,
                        COUNT(*) as count,
                        AVG(response_time) as avg_response_time,
                        MIN(response_time) as min_response_time,
                        MAX(response_time) as max_response_time,
                        SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as success_count,
                        SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
                    FROM api_metrics
                    WHERE endpoint = ? AND timestamp >= ?
                    GROUP BY endpoint, method
                """, (endpoint, start_time))
            else:
                cursor.execute("""
                    SELECT 
                        endpoint,
                        method,
                        COUNT(*) as count,
                        AVG(response_time) as avg_response_time,
                        MIN(response_time) as min_response_time,
                        MAX(response_time) as max_response_time,
                        SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as success_count,
                        SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
                    FROM api_metrics
                    WHERE timestamp >= ?
                    GROUP BY endpoint, method
                    ORDER BY count DESC
                    LIMIT 50
                """, (start_time,))
            
            stats = cursor.fetchall()
            conn.close()
            
            return [
                {
                    'endpoint': row[0],
                    'method': row[1],
                    'count': row[2],
                    'avg_response_time': round(row[3], 2),
                    'min_response_time': round(row[4], 2),
                    'max_response_time': round(row[5], 2),
                    'success_count': row[6],
                    'error_count': row[7],
                    'success_rate': round(row[6] / row[2] * 100, 2) if row[2] > 0 else 0
                }
                for row in stats
            ]
        except Exception as e:
            print(f"获取API统计失败: {str(e)}")
            return []
    
    def get_alert_rules(self):
        """获取告警规则"""
        return [
            {
                'id': 1,
                'name': '高响应时间告警',
                'metricType': 'response_time',
                'threshold': 1000,
                'condition': '>',
                'enabled': True
            },
            {
                'id': 2,
                'name': '高错误率告警',
                'metricType': 'error_rate',
                'threshold': 5,
                'condition': '>',
                'enabled': True
            },
            {
                'id': 3,
                'name': '低成功率告警',
                'metricType': 'success_rate',
                'threshold': 95,
                'condition': '<',
                'enabled': True
            }
        ]
    
    def update_alert_rule(self, rule_id, enabled):
        """更新告警规则状态"""
        print(f"更新告警规则 {rule_id} 为 {'启用' if enabled else '禁用'}")
        return True


# 创建全局监控实例
api_monitor = APIMonitor()


def monitor_api(f):
    """API监控装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 记录开始时间
        start_time = time.time()
        
        try:
            # 执行原始函数
            response = f(*args, **kwargs)
            
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000  # 转换为毫秒
            
            # 获取状态码
            status_code = getattr(response, 'status_code', 200)
            
            # 获取endpoint和method
            endpoint = request.endpoint or request.path
            method = request.method
            
            # 记录指标
            api_monitor.record_request(endpoint, method, status_code, response_time)
            
            return response
        except Exception as e:
            # 计算响应时间
            response_time = (time.time() - start_time) * 1000
            
            # 记录错误指标
            endpoint = request.endpoint or request.path
            method = request.method
            api_monitor.record_request(endpoint, method, 500, response_time)
            
            raise
    return decorated_function


# 自动告警配置
ALERT_THRESHOLDS = {
    'high_response_time': 5000,  # 5秒
    'high_error_rate': 10,       # 10%错误率
    'low_success_rate': 90       # 90%成功率
}

def check_alerts():
    """检查是否需要发送告警"""
    stats = api_monitor.get_stats(hours=1)
    
    alerts = []
    
    for stat in stats:
        # 检查响应时间
        if stat['avg_response_time'] > ALERT_THRESHOLDS['high_response_time']:
            alerts.append({
                'type': 'high_response_time',
                'endpoint': stat['endpoint'],
                'method': stat['method'],
                'avg_response_time': stat['avg_response_time'],
                'threshold': ALERT_THRESHOLDS['high_response_time'],
                'severity': 'warning'
            })
        
        # 检查错误率
        if stat['error_count'] > 0 and (stat['error_count'] / stat['count'] * 100) > ALERT_THRESHOLDS['high_error_rate']:
            alerts.append({
                'type': 'high_error_rate',
                'endpoint': stat['endpoint'],
                'method': stat['method'],
                'error_rate': round(stat['error_count'] / stat['count'] * 100, 2),
                'threshold': ALERT_THRESHOLDS['high_error_rate'],
                'severity': 'critical'
            })
        
        # 检查成功率
        if stat['success_rate'] < ALERT_THRESHOLDS['low_success_rate']:
            alerts.append({
                'type': 'low_success_rate',
                'endpoint': stat['endpoint'],
                'method': stat['method'],
                'success_rate': stat['success_rate'],
                'threshold': ALERT_THRESHOLDS['low_success_rate'],
                'severity': 'critical'
            })
    
    return alerts


def save_alert(alert):
    """保存告警到数据库"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS api_alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                alert_type VARCHAR(50) NOT NULL,
                endpoint VARCHAR(255),
                method VARCHAR(10),
                message TEXT,
                severity VARCHAR(20),
                resolved BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO api_alerts (alert_type, endpoint, method, message, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (alert['type'], alert.get('endpoint'), alert.get('method'), json.dumps(alert), alert['severity']))
        
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"保存告警失败: {str(e)}")


def get_monitor_stats(start_time):
    """获取监控统计数据"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 获取端点级别统计
        cursor.execute("""
            SELECT 
                endpoint,
                method,
                COUNT(*) as count,
                AVG(response_time) as avg_response_time,
                PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY response_time) OVER () as p95_response_time,
                PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY response_time) OVER () as p99_response_time,
                SUM(CASE WHEN status_code < 400 THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN status_code >= 400 THEN 1 ELSE 0 END) as error_count
            FROM api_metrics
            WHERE timestamp >= ?
            GROUP BY endpoint, method
        """, (start_time,))
        
        rows = cursor.fetchall()
        
        # 转换结果
        endpoint_metrics = []
        for row in rows:
            endpoint_metrics.append({
                'endpoint': row[0],
                'method': row[1],
                'totalRequests': row[2],
                'avgResponseTime': round(row[3], 2) if row[3] else 0,
                'p95ResponseTime': round(row[4], 2) if row[4] else 0,
                'p99ResponseTime': round(row[5], 2) if row[5] else 0,
                'successRate': round(row[6] / row[2] * 100, 2) if row[2] > 0 else 0,
                'errorRate': round(row[7] / row[2] * 100, 2) if row[2] > 0 else 0,
                'successCount': row[6],
                'errorCount': row[7]
            })
        
        # 获取汇总统计
        total_requests = sum(m['totalRequests'] for m in endpoint_metrics)
        avg_response_time = sum(m['avgResponseTime'] for m in endpoint_metrics) / len(endpoint_metrics) if endpoint_metrics else 0
        total_success = sum(m['successCount'] for m in endpoint_metrics)
        total_errors = sum(m['errorCount'] for m in endpoint_metrics)
        success_rate = round(total_success / total_requests * 100, 2) if total_requests > 0 else 0
        
        summary = {
            'totalRequests': total_requests,
            'avgResponseTime': round(avg_response_time, 2),
            'successRate': success_rate,
            'totalErrors': total_errors
        }
        
        conn.close()
        
        return {
            'endpoint_metrics': endpoint_metrics,
            'summary': summary
        }
    except Exception as e:
        print(f"获取监控统计失败: {str(e)}")
        return {
            'endpoint_metrics': [],
            'summary': {
                'totalRequests': 0,
                'avgResponseTime': 0,
                'successRate': 0,
                'totalErrors': 0
            }
        }
