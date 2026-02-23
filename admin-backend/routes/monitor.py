"""
API性能监控路由
"""

from flask import Blueprint, jsonify, request
from datetime import datetime, timedelta
from utils.api_monitor import api_monitor
from database import get_db

# 尝试导入，如果失败则使用本地实现
try:
    from utils.api_monitor import get_monitor_stats
except ImportError:
    # 本地实现
    def get_monitor_stats(start_time):
        """获取监控统计数据（本地实现）"""
        try:
            conn = get_db()
            cursor = conn.cursor()
            
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
            """, (start_time,))
            
            rows = cursor.fetchall()
            
            endpoint_metrics = []
            for row in rows:
                endpoint_metrics.append({
                    'endpoint': row[0],
                    'method': row[1],
                    'totalRequests': row[2],
                    'avgResponseTime': round(row[3], 2) if row[3] else 0,
                    'p95ResponseTime': 0,
                    'p99ResponseTime': 0,
                    'successRate': round(row[6] / row[2] * 100, 2) if row[2] > 0 else 0,
                    'errorRate': round(row[7] / row[2] * 100, 2) if row[2] > 0 else 0,
                    'successCount': row[6],
                    'errorCount': row[7]
                })
            
            total_requests = sum(m['totalRequests'] for m in endpoint_metrics)
            avg_response_time = sum(m['avgResponseTime'] for m in endpoint_metrics) / len(endpoint_metrics) if endpoint_metrics else 0
            total_success = sum(m['successCount'] for m in endpoint_metrics)
            total_errors = sum(m['errorCount'] for m in endpoint_metrics)
            success_rate = round(total_success / total_requests * 100, 2) if total_requests > 0 else 0
            
            conn.close()
            
            return {
                'endpoint_metrics': endpoint_metrics,
                'summary': {
                    'totalRequests': total_requests,
                    'avgResponseTime': round(avg_response_time, 2),
                    'successRate': success_rate,
                    'totalErrors': total_errors
                }
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

monitor_bp = Blueprint('monitor', __name__)


@monitor_bp.route('/admin/api-monitor', methods=['GET'])
def get_api_monitor_data():
    """获取API监控数据"""
    try:
        time_range = request.args.get('timeRange', '24h')
        
        # 计算时间范围
        if time_range == '1h':
            start_time = datetime.now() - timedelta(hours=1)
        elif time_range == '24h':
            start_time = datetime.now() - timedelta(hours=24)
        elif time_range == '7d':
            start_time = datetime.now() - timedelta(days=7)
        elif time_range == '30d':
            start_time = datetime.now() - timedelta(days=30)
        else:
            start_time = datetime.now() - timedelta(hours=24)
        
        # 获取监控统计
        stats = get_monitor_stats(start_time)
        
        # 生成图表数据
        chart_data = []
        metric_history = api_monitor.get_metric_history(start_time)
        
        for metric in metric_history:
            chart_data.append({
                'time': metric['timestamp'].strftime('%Y-%m-%d %H:%M'),
                'avgResponseTime': metric['avgResponseTime'],
                'p95ResponseTime': metric['p95ResponseTime'],
                'p99ResponseTime': metric['p99ResponseTime'],
                'successRate': metric['successRate'],
                'errorRate': metric['errorRate']
            })
        
        return jsonify({
            'success': True,
            'message': '获取监控数据成功',
            'data': {
                'metrics': stats['endpoint_metrics'],
                'chartData': chart_data,
                'summary': stats['summary']
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取监控数据失败: {str(e)}',
            'data': None
        }), 500


@monitor_bp.route('/admin/api-monitor/alerts', methods=['GET'])
def get_alert_rules():
    """获取告警规则"""
    try:
        alerts = api_monitor.get_alert_rules()
        
        return jsonify({
            'success': True,
            'message': '获取告警规则成功',
            'data': alerts
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取告警规则失败: {str(e)}',
            'data': []
        }), 500


@monitor_bp.route('/admin/api-monitor/alerts/<int:rule_id>', methods=['PUT'])
def update_alert_rule(rule_id):
    """更新告警规则"""
    try:
        data = request.json
        enabled = data.get('enabled', True)
        
        api_monitor.update_alert_rule(rule_id, enabled)
        
        return jsonify({
            'success': True,
            'message': '更新告警规则成功',
            'data': None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'更新告警规则失败: {str(e)}',
            'data': None
        }), 500


@monitor_bp.route('/admin/error-logs', methods=['GET'])
def get_error_logs():
    """获取错误日志"""
    try:
        from utils.error_logger import error_logger
        
        severity = request.args.get('severity')
        resolved = request.args.get('resolved')
        keyword = request.args.get('keyword')
        
        # 获取最近24小时的错误日志
        logs = error_logger.get_recent_errors(limit=100, hours=24)
        
        # 过滤
        if severity:
            logs = [log for log in logs if log['severity'] == severity]
        if resolved is not None:
            resolved_bool = resolved.lower() == 'true'
            logs = [log for log in logs if log['resolved'] == resolved_bool]
        if keyword:
            logs = [log for log in logs if keyword.lower() in log['message'].lower() or keyword.lower() in log['errorType'].lower()]
        
        return jsonify({
            'success': True,
            'message': '获取错误日志成功',
            'data': logs
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取错误日志失败: {str(e)}',
            'data': []
        }), 500


@monitor_bp.route('/admin/error-logs/<int:log_id>/resolve', methods=['PUT'])
def resolve_error_log(log_id):
    """标记错误日志已解决"""
    try:
        from utils.error_logger import error_logger
        
        success = error_logger.mark_resolved(log_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': '标记已解决成功',
                'data': None
            })
        else:
            return jsonify({
                'success': False,
                'message': '标记已解决失败',
                'data': None
            }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'标记已解决失败: {str(e)}',
            'data': None
        }), 500


@monitor_bp.route('/admin/error-logs/<int:log_id>', methods=['DELETE'])
def delete_error_log(log_id):
    """删除错误日志"""
    try:
        # TODO: 实现删除逻辑
        return jsonify({
            'success': True,
            'message': '删除成功',
            'data': None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'删除失败: {str(e)}',
            'data': None
        }), 500
