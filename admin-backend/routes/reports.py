"""
报表系统 API
功能：
1. 项目统计报表
2. 资源统计报表
3. 分润统计报表
4. 综合数据分析
"""

import json
import sqlite3
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, g

# 导入JWT认证中间件
from middleware.jwt_auth import require_auth

reports_bp = Blueprint('reports', __name__)


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


# ==================== 项目统计报表 ====================

@reports_bp.route('/api/reports/projects/summary', methods=['GET'])
@require_auth
def get_project_summary_report():
    """
    获取项目综合统计报表
    查询参数：startDate, endDate
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        # 基础统计
        base_query = '''
            SELECT 
                COUNT(*) as total_projects,
                SUM(CASE WHEN status = 'recruiting' THEN 1 ELSE 0 END) as recruiting,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END) as closed,
                SUM(budget) as total_budget,
                AVG(budget) as avg_budget
            FROM company_projects
            WHERE 1=1
        '''
        
        params = []
        if start_date:
            base_query += ' AND created_at >= ?'
            params.append(start_date)
        if end_date:
            base_query += ' AND created_at <= ?'
            params.append(end_date)
        
        base_stats = conn.execute(base_query, params).fetchone()
        
        # 参与统计
        participation_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_participations,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active_participations,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_participations,
                SUM(payment_amount) as total_invested
            FROM project_participations
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        # 项目收益统计
        profit_stats = conn.execute('''
            SELECT 
                SUM(total_profit) as total_revenue,
                SUM(user_share) as user_earnings,
                COUNT(*) as profit_records
            FROM profit_sharing ps
            JOIN project_participations pp ON ps.participation_id = pp.id
            WHERE pp.user_id = ?
        ''', (user_id,)).fetchone()
        
        # 按月份统计项目创建趋势
        monthly_trend = conn.execute('''
            SELECT 
                substr(created_at, 1, 7) as month,
                COUNT(*) as count
            FROM company_projects
            WHERE created_at >= date('now', '-12 months')
            GROUP BY substr(created_at, 1, 7)
            ORDER BY month DESC
            LIMIT 12
        ''').fetchall()
        
        # 按类型统计项目分布
        type_distribution = conn.execute('''
            SELECT 
                status,
                COUNT(*) as count,
                SUM(budget) as total_budget
            FROM company_projects
            GROUP BY status
            ORDER BY count DESC
        ''').fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取项目统计报表成功',
            'data': {
                'baseStats': {
                    'totalProjects': base_stats['total_projects'] or 0,
                    'recruiting': base_stats['recruiting'] or 0,
                    'active': base_stats['active'] or 0,
                    'completed': base_stats['completed'] or 0,
                    'closed': base_stats['closed'] or 0,
                    'totalBudget': base_stats['total_budget'] or 0,
                    'avgBudget': base_stats['avg_budget'] or 0
                },
                'participationStats': {
                    'totalParticipations': participation_stats['total_participations'] or 0,
                    'activeParticipations': participation_stats['active_participations'] or 0,
                    'completedParticipations': participation_stats['completed_participations'] or 0,
                    'totalInvested': participation_stats['total_invested'] or 0
                },
                'profitStats': {
                    'totalRevenue': profit_stats['total_revenue'] or 0,
                    'userEarnings': profit_stats['user_earnings'] or 0,
                    'profitRecords': profit_stats['profit_records'] or 0
                },
                'monthlyTrend': [
                    {'month': row['month'], 'count': row['count']}
                    for row in monthly_trend
                ],
                'typeDistribution': [
                    {'status': row['status'], 'count': row['count'], 'budget': row['total_budget']}
                    for row in type_distribution
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 资源统计报表 ====================

@reports_bp.route('/api/reports/resources/summary', methods=['GET'])
@require_auth
def get_resource_summary_report():
    """
    获取资源综合统计报表
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 基础统计
        base_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_resources,
                SUM(CASE WHEN authorization_status = 'authorized' THEN 1 ELSE 0 END) as authorized,
                SUM(CASE WHEN verification_status = 'verified' THEN 1 ELSE 0 END) as verified,
                SUM(CASE WHEN visibility = 'matchable' THEN 1 ELSE 0 END) as matchable
            FROM private_resources
            WHERE user_id = ? AND deleted_at IS NULL
        ''', (user_id,)).fetchone()
        
        # 按类型统计
        type_stats = conn.execute('''
            SELECT 
                resource_type,
                COUNT(*) as count
            FROM private_resources
            WHERE user_id = ? AND deleted_at IS NULL
            GROUP BY resource_type
        ''', (user_id,)).fetchall()
        
        # 匹配统计
        match_stats = conn.execute('''
            SELECT 
                COUNT(*) as total_matches,
                SUM(CASE WHEN status = 'approved' THEN 1 ELSE 0 END) as approved_matches,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) as pending_matches,
                AVG(match_score) as avg_match_score
            FROM resource_matches rm
            JOIN private_resources pr ON rm.resource_id = pr.id
            WHERE pr.user_id = ?
        ''', (user_id,)).fetchone()
        
        # 资源使用率
        usage_stats = conn.execute('''
            SELECT 
                pr.id,
                pr.resource_name,
                COUNT(rm.id) as match_count,
                SUM(CASE WHEN rm.status = 'approved' THEN 1 ELSE 0 END) as approved_count
            FROM private_resources pr
            LEFT JOIN resource_matches rm ON pr.id = rm.resource_id
            WHERE pr.user_id = ? AND pr.deleted_at IS NULL
            GROUP BY pr.id
            ORDER BY match_count DESC
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取资源统计报表成功',
            'data': {
                'baseStats': {
                    'totalResources': base_stats['total_resources'] or 0,
                    'authorized': base_stats['authorized'] or 0,
                    'verified': base_stats['verified'] or 0,
                    'matchable': base_stats['matchable'] or 0
                },
                'typeStats': [
                    {'type': row['resource_type'], 'count': row['count']}
                    for row in type_stats
                ],
                'matchStats': {
                    'totalMatches': match_stats['total_matches'] or 0,
                    'approvedMatches': match_stats['approved_matches'] or 0,
                    'pendingMatches': match_stats['pending_matches'] or 0,
                    'avgMatchScore': match_stats['avg_match_score'] or 0
                },
                'topUsedResources': [
                    {
                        'resourceName': row['resource_name'],
                        'matchCount': row['match_count'],
                        'approvedCount': row['approved_count']
                    }
                    for row in usage_stats
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 分润统计报表 ====================

@reports_bp.route('/api/reports/profits/summary', methods=['GET'])
@require_auth
def get_profit_summary_report():
    """
    获取分润综合统计报表
    查询参数：startDate, endDate
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        start_date = request.args.get('startDate')
        end_date = request.args.get('endDate')
        
        # 基础统计
        query = '''
            SELECT 
                COUNT(*) as total_records,
                SUM(total_profit) as total_profit,
                SUM(user_share) as total_user_share,
                AVG(share_percentage) as avg_share_percentage,
                SUM(CASE WHEN ps.status = 'distributed' THEN 1 ELSE 0 END) as distributed_count,
                SUM(CASE WHEN ps.status = 'distributed' THEN ps.user_share ELSE 0 END) as distributed_amount,
                SUM(CASE WHEN ps.status = 'pending' THEN ps.user_share ELSE 0 END) as pending_amount
            FROM profit_sharing ps
            JOIN project_participations pp ON ps.participation_id = pp.id
            WHERE pp.user_id = ?
        '''
        params = [user_id]
        
        if start_date:
            query += ' AND ps.created_at >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND ps.created_at <= ?'
            params.append(end_date)
        
        base_stats = conn.execute(query, params).fetchone()
        
        # 按月份统计分润趋势
        monthly_trend = conn.execute('''
            SELECT 
                substr(ps.created_at, 1, 7) as month,
                COUNT(*) as count,
                SUM(ps.user_share) as total_share,
                SUM(CASE WHEN ps.status = 'distributed' THEN ps.user_share ELSE 0 END) as distributed
            FROM profit_sharing ps
            JOIN project_participations pp ON ps.participation_id = pp.id
            WHERE pp.user_id = ? 
              AND ps.created_at >= date('now', '-12 months')
            GROUP BY substr(ps.created_at, 1, 7)
            ORDER BY month DESC
            LIMIT 12
        ''', (user_id,)).fetchall()
        
        # 按项目统计
        project_profits = conn.execute('''
            SELECT 
                p.name as project_name,
                COUNT(ps.id) as record_count,
                SUM(ps.user_share) as total_share,
                SUM(CASE WHEN ps.status = 'distributed' THEN ps.user_share ELSE 0 END) as distributed
            FROM profit_sharing ps
            JOIN project_participations pp ON ps.participation_id = pp.id
            JOIN company_projects p ON pp.project_id = p.id
            WHERE pp.user_id = ?
            GROUP BY p.id
            ORDER BY total_share DESC
            LIMIT 10
        ''', (user_id,)).fetchall()
        
        # 结算周期分布
        settlement_distribution = conn.execute('''
            SELECT 
                settlement_period,
                COUNT(*) as count,
                SUM(user_share) as total_amount
            FROM profit_sharing ps
            JOIN project_participations pp ON ps.participation_id = pp.id
            WHERE pp.user_id = ?
            GROUP BY settlement_period
        ''', (user_id,)).fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取分润统计报表成功',
            'data': {
                'baseStats': {
                    'totalRecords': base_stats['total_records'] or 0,
                    'totalProfit': base_stats['total_profit'] or 0,
                    'totalUserShare': base_stats['total_user_share'] or 0,
                    'avgSharePercentage': base_stats['avg_share_percentage'] or 0,
                    'distributedCount': base_stats['distributed_count'] or 0,
                    'distributedAmount': base_stats['distributed_amount'] or 0,
                    'pendingAmount': base_stats['pending_amount'] or 0
                },
                'monthlyTrend': [
                    {
                        'month': row['month'],
                        'count': row['count'],
                        'totalShare': row['total_share'],
                        'distributed': row['distributed']
                    }
                    for row in monthly_trend
                ],
                'projectProfits': [
                    {
                        'projectName': row['project_name'],
                        'recordCount': row['record_count'],
                        'totalShare': row['total_share'],
                        'distributed': row['distributed']
                    }
                    for row in project_profits
                ],
                'settlementDistribution': [
                    {
                        'period': row['settlement_period'],
                        'count': row['count'],
                        'amount': row['total_amount']
                    }
                    for row in settlement_distribution
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 综合仪表盘 ====================

@reports_bp.route('/api/reports/dashboard', methods=['GET'])
@require_auth
def get_dashboard_report():
    """
    获取综合仪表盘数据
    """
    try:
        conn = get_db_connection()
        user_id = g.current_user_id
        
        # 资源统计
        resource_stats = conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN authorization_status = 'authorized' THEN 1 ELSE 0 END) as authorized,
                SUM(CASE WHEN visibility = 'matchable' THEN 1 ELSE 0 END) as matchable
            FROM private_resources
            WHERE user_id = ? AND deleted_at IS NULL
        ''', (user_id,)).fetchone()
        
        # 匹配统计
        match_stats = conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN rm.status = 'approved' THEN 1 ELSE 0 END) as approved,
                SUM(CASE WHEN rm.status = 'pending' THEN 1 ELSE 0 END) as pending
            FROM resource_matches rm
            JOIN private_resources pr ON rm.resource_id = pr.id
            WHERE pr.user_id = ?
        ''', (user_id,)).fetchone()
        
        # 参与统计
        participation_stats = conn.execute('''
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN status = 'active' THEN 1 ELSE 0 END) as active,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                SUM(payment_amount) as total_invested
            FROM project_participations
            WHERE user_id = ?
        ''', (user_id,)).fetchone()
        
        # 分润统计
        profit_stats = conn.execute('''
            SELECT 
                SUM(user_share) as total,
                SUM(CASE WHEN ps.status = 'distributed' THEN user_share ELSE 0 END) as distributed,
                SUM(CASE WHEN ps.status = 'pending' THEN user_share ELSE 0 END) as pending
            FROM profit_sharing ps
            JOIN project_participations pp ON ps.participation_id = pp.id
            WHERE pp.user_id = ?
        ''', (user_id,)).fetchone()
        
        # 最近活动
        recent_activities = conn.execute('''
            SELECT 
                'participation' as type,
                '申请参与项目' as title,
                created_at
            FROM project_participations
            WHERE user_id = ?
            
            UNION ALL
            
            SELECT 
                'match' as type,
                '资源匹配成功' as title,
                rm.created_at
            FROM resource_matches rm
            JOIN private_resources pr ON rm.resource_id = pr.id
            WHERE pr.user_id = ? AND rm.status = 'approved'
            
            UNION ALL
            
            SELECT 
                'profit' as type,
                '分润到账' as title,
                distribution_time as created_at
            FROM profit_sharing ps
            JOIN project_participations pp ON ps.participation_id = pp.id
            WHERE pp.user_id = ? AND ps.status = 'distributed'
            
            ORDER BY created_at DESC
            LIMIT 10
        ''', (user_id, user_id, user_id)).fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取仪表盘数据成功',
            'data': {
                'resources': {
                    'total': resource_stats['total'] or 0,
                    'authorized': resource_stats['authorized'] or 0,
                    'matchable': resource_stats['matchable'] or 0
                },
                'matches': {
                    'total': match_stats['total'] or 0,
                    'approved': match_stats['approved'] or 0,
                    'pending': match_stats['pending'] or 0
                },
                'participations': {
                    'total': participation_stats['total'] or 0,
                    'active': participation_stats['active'] or 0,
                    'completed': participation_stats['completed'] or 0,
                    'totalInvested': participation_stats['total_invested'] or 0
                },
                'profits': {
                    'total': profit_stats['total'] or 0,
                    'distributed': profit_stats['distributed'] or 0,
                    'pending': profit_stats['pending'] or 0
                },
                'recentActivities': [
                    {
                        'type': row['type'],
                        'title': row['title'],
                        'createdAt': row['created_at']
                    }
                    for row in recent_activities
                ]
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ==================== 导出报表 ====================

@reports_bp.route('/api/reports/export', methods=['GET'])
@require_auth
def export_report():
    """
    导出报表
    查询参数：reportType (projects, resources, profits), format (json, csv)
    """
    try:
        report_type = request.args.get('reportType')
        format_type = request.args.get('format', 'json')
        
        if not report_type:
            return jsonify({'success': False, 'message': '缺少报表类型'}), 400
        
        # 获取数据
        if report_type == 'projects':
            response = get_project_summary_report()
        elif report_type == 'resources':
            response = get_resource_summary_report()
        elif report_type == 'profits':
            response = get_profit_summary_report()
        else:
            return jsonify({'success': False, 'message': '无效的报表类型'}), 400
        
        # 解析响应
        import json as json_module
        if isinstance(response, str):
            response_data = json_module.loads(response)
        else:
            response_data = json_module.loads(response[0].response[0])
        
        if not response_data.get('success'):
            return jsonify({'success': False, 'message': response_data.get('message')}), 500
        
        if format_type == 'csv':
            # 转换为CSV格式
            data = response_data['data']
            csv_content = 'type,value\n'
            
            for key, value in data.items():
                if isinstance(value, dict):
                    for sub_key, sub_value in value.items():
                        csv_content += f'{key}.{sub_key},{sub_value}\n'
                elif isinstance(value, list):
                    csv_content += f'{key}.count,{len(value)}\n'
                else:
                    csv_content += f'{key},{value}\n'
            
            from flask import Response
            return Response(
                csv_content,
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename={report_type}_report.csv'}
            )
        
        return response
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
