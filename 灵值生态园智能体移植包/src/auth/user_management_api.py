"""
灵值生态园 - 用户管理系统统一API接口
整合用户、推荐、项目、分红等所有管理模块

版本: v1.0
更新日期: 2026年1月25日
"""

import os
import sys
from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict, Any
from flask import Flask, request, jsonify
from functools import wraps

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入管理模块
from src.auth.my_user import MyUser, TransactionType
from src.auth.referral_manager import ReferralManager
from src.auth.project_manager import ProjectManager
from src.auth.dividend_manager import DividendManager

# 创建Flask应用
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True


# ==================== 错误处理 ====================

def handle_error(f):
    """统一错误处理装饰器"""
    @wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    return wrapper


def success_response(data: Any = None, message: str = "操作成功") -> Dict:
    """成功响应格式"""
    return {
        "success": True,
        "data": data,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }


def error_response(message: str, code: int = 400) -> tuple:
    """错误响应格式"""
    return jsonify({
        "success": False,
        "error": message,
        "timestamp": datetime.now().isoformat()
    }), code


# ==================== 用户管理API ====================

@app.route('/api/user', methods=['POST'])
@handle_error
def create_user():
    """创建用户"""
    data = request.json
    
    with MyUser() as user_mgr:
        user = user_mgr.create_user(
            name=data.get('name'),
            email=data.get('email'),
            password_hash=data.get('password_hash'),
            phone=data.get('phone'),
            wechat=data.get('wechat'),
            department=data.get('department'),
            position=data.get('position'),
            created_by=data.get('created_by')
        )
        
        if user:
            return jsonify(success_response({
                "user_id": user.id,
                "name": user.name,
                "email": user.email
            }, "用户创建成功"))
        else:
            return error_response("用户创建失败", 400)


@app.route('/api/user/<int:user_id>', methods=['GET'])
@handle_error
def get_user(user_id: int):
    """获取用户信息"""
    with MyUser() as user_mgr:
        user = user_mgr.get_user(user_id)
        
        if user:
            return jsonify(success_response({
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "phone": user.phone,
                "wechat": user.wechat,
                "department": user.department,
                "position": user.position,
                "status": user.status,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }))
        else:
            return error_response("用户不存在", 404)


@app.route('/api/user/<int:user_id>', methods=['PUT'])
@handle_error
def update_user(user_id: int):
    """更新用户信息"""
    data = request.json
    
    with MyUser() as user_mgr:
        success = user_mgr.update_user(
            user_id=user_id,
            name=data.get('name'),
            phone=data.get('phone'),
            wechat=data.get('wechat'),
            department=data.get('department'),
            position=data.get('position'),
            status=data.get('status')
        )
        
        if success:
            return jsonify(success_response(message="用户信息更新成功"))
        else:
            return error_response("用户信息更新失败", 400)


@app.route('/api/user/<int:user_id>', methods=['DELETE'])
@handle_error
def delete_user(user_id: int):
    """删除用户"""
    with MyUser() as user_mgr:
        success = user_mgr.delete_user(user_id)
        
        if success:
            return jsonify(success_response(message="用户删除成功"))
        else:
            return error_response("用户删除失败", 400)


@app.route('/api/users', methods=['GET'])
@handle_error
def list_users():
    """列出用户"""
    status = request.args.get('status')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    with MyUser() as user_mgr:
        users = user_mgr.list_users(status=status, limit=limit, offset=offset)
        
        user_list = [{
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "phone": u.phone,
            "department": u.department,
            "position": u.position,
            "status": u.status,
            "created_at": u.created_at.isoformat() if u.created_at else None
        } for u in users]
        
        return jsonify(success_response({
            "users": user_list,
            "count": len(user_list)
        }))


@app.route('/api/user/<int:user_id>/contribution', methods=['GET'])
@handle_error
def get_contribution(user_id: int):
    """获取用户贡献值"""
    with MyUser() as user_mgr:
        contribution = user_mgr.get_contribution_value(user_id)
        
        return jsonify(success_response({
            "user_id": user_id,
            "contribution_value": contribution
        }))


@app.route('/api/user/<int:user_id>/contribution/add', methods=['POST'])
@handle_error
def add_contribution(user_id: int):
    """增加用户贡献值"""
    data = request.json
    
    with MyUser() as user_mgr:
        success = user_mgr.add_contribution(
            user_id=user_id,
            amount=float(data.get('amount', 0)),
            transaction_type=TransactionType(data.get('transaction_type', 'task_reward')),
            description=data.get('description')
        )
        
        if success:
            return jsonify(success_response(message="贡献值增加成功"))
        else:
            return error_response("贡献值增加失败", 400)


@app.route('/api/user/<int:user_id>/contribution/consume', methods=['POST'])
@handle_error
def consume_contribution(user_id: int):
    """消耗用户贡献值"""
    data = request.json
    
    with MyUser() as user_mgr:
        success = user_mgr.consume_contribution(
            user_id=user_id,
            amount=float(data.get('amount', 0)),
            transaction_type=TransactionType(data.get('transaction_type', 'contribution_consume')),
            description=data.get('description')
        )
        
        if success:
            return jsonify(success_response(message="贡献值消耗成功"))
        else:
            return error_response("贡献值消耗失败", 400)


@app.route('/api/user/<int:user_id>/level', methods=['GET'])
@handle_error
def get_member_level(user_id: int):
    """获取用户会员级别"""
    with MyUser() as user_mgr:
        user_level = user_mgr.get_member_level(user_id)
        
        if user_level:
            return jsonify(success_response({
                "user_id": user_id,
                "level_id": user_level.level_id,
                "contribution_value": user_level.contribution_value,
                "team_member_count": user_level.team_member_count,
                "total_earned": float(user_level.total_earned),
                "total_dividend_earned": float(user_level.total_dividend_earned),
                "equity_percentage": user_level.equity_percentage,
                "level_since": user_level.level_since.isoformat() if user_level.level_since else None
            }))
        else:
            return error_response("会员级别不存在", 404)


# ==================== 推荐管理API ====================

@app.route('/api/referral', methods=['POST'])
@handle_error
def create_referral():
    """创建推荐关系"""
    data = request.json
    
    with ReferralManager() as ref_mgr:
        success = ref_mgr.create_referral_relationship(
            referrer_id=data.get('referrer_id'),
            referee_id=data.get('referee_id'),
            project_id=data.get('project_id')
        )
        
        if success:
            return jsonify(success_response(message="推荐关系创建成功"))
        else:
            return error_response("推荐关系创建失败", 400)


@app.route('/api/referral/code/<referral_code>', methods=['GET'])
@handle_error
def get_referral_by_code(referral_code: str):
    """通过推荐码获取推荐关系"""
    with ReferralManager() as ref_mgr:
        referral = ref_mgr.get_referral_by_code(referral_code)
        
        if referral:
            return jsonify(success_response({
                "id": referral.id,
                "referral_code": referral.referral_code,
                "referrer_id": referral.referrer_id,
                "referee_id": referral.referee_id,
                "relationship_type": referral.relationship_type,
                "status": referral.status
            }))
        else:
            return error_response("推荐关系不存在", 404)


@app.route('/api/user/<int:user_id>/referrals', methods=['GET'])
@handle_error
def get_user_referrals(user_id: int):
    """获取用户的推荐记录"""
    with ReferralManager() as ref_mgr:
        referrals = ref_mgr.get_referrals_by_user(user_id)
        
        referral_list = [{
            "id": r.id,
            "referral_code": r.referral_code,
            "referee_id": r.referee_id,
            "relationship_type": r.relationship_type,
            "status": r.status,
            "created_at": r.created_at.isoformat() if r.created_at else None
        } for r in referrals]
        
        return jsonify(success_response({
            "referrals": referral_list,
            "count": len(referral_list)
        }))


@app.route('/api/user/<int:user_id>/referral/stats', methods=['GET'])
@handle_error
def get_referral_stats(user_id: int):
    """获取用户推荐统计"""
    with ReferralManager() as ref_mgr:
        stats = ref_mgr.get_referral_stats(user_id)
        
        return jsonify(success_response({
            "user_id": user_id,
            **stats
        }))


# ==================== 项目管理API ====================

@app.route('/api/project', methods=['POST'])
@handle_error
def create_project():
    """创建项目"""
    data = request.json
    
    with ProjectManager() as proj_mgr:
        project = proj_mgr.create_project(
            project_name=data.get('project_name'),
            project_code=data.get('project_code'),
            description=data.get('description'),
            project_type=data.get('project_type'),
            total_investment=Decimal(str(data.get('total_investment', 0))),
            profit_distribution_rate=float(data.get('profit_distribution_rate', 1.0)),
            min_participation_amount=Decimal(str(data.get('min_participation_amount'))) if data.get('min_participation_amount') else None,
            max_participants=data.get('max_participants'),
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            end_date=datetime.fromisoformat(data['end_date']) if data.get('end_date') else None,
            created_by=data.get('created_by')
        )
        
        if project:
            return jsonify(success_response({
                "project_id": project.id,
                "project_name": project.project_name,
                "project_code": project.project_code
            }, "项目创建成功"))
        else:
            return error_response("项目创建失败", 400)


@app.route('/api/projects', methods=['GET'])
@handle_error
def list_projects():
    """列出项目"""
    status = request.args.get('status')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    
    with ProjectManager() as proj_mgr:
        projects = proj_mgr.list_projects(status=status, limit=limit, offset=offset)
        
        project_list = [{
            "id": p.id,
            "project_name": p.project_name,
            "project_code": p.project_code,
            "description": p.description,
            "project_type": p.project_type,
            "total_investment": float(p.total_investment),
            "total_revenue": float(p.total_revenue),
            "total_profit": float(p.total_profit),
            "status": p.status,
            "current_participants": p.current_participants or 0,
            "created_at": p.created_at.isoformat() if p.created_at else None
        } for p in projects]
        
        return jsonify(success_response({
            "projects": project_list,
            "count": len(project_list)
        }))


@app.route('/api/project/<int:project_id>/participate', methods=['POST'])
@handle_error
def participate_project(project_id: int):
    """参与项目"""
    data = request.json
    
    with ProjectManager() as proj_mgr:
        success = proj_mgr.participate_project(
            user_id=data.get('user_id'),
            project_id=project_id,
            participation_amount=Decimal(str(data.get('participation_amount', 0))),
            participant_id=data.get('participant_id')
        )
        
        if success:
            return jsonify(success_response(message="项目参与成功"))
        else:
            return error_response("项目参与失败", 400)


@app.route('/api/user/<int:user_id>/participations', methods=['GET'])
@handle_error
def get_user_participations(user_id: int):
    """获取用户的项目参与记录"""
    with ProjectManager() as proj_mgr:
        participations = proj_mgr.get_user_participations(user_id)
        
        participation_list = [{
            "id": p.id,
            "project_id": p.project_id,
            "participation_amount": float(p.participation_amount),
            "share_percentage": p.share_percentage,
            "profit_share": float(p.profit_share),
            "profit_paid": float(p.profit_paid),
            "participation_date": p.participation_date.isoformat() if p.participation_date else None,
            "status": p.status
        } for p in participations]
        
        return jsonify(success_response({
            "participations": participation_list,
            "count": len(participation_list)
        }))


@app.route('/api/project/<int:project_id>/stats', methods=['GET'])
@handle_error
def get_project_stats(project_id: int):
    """获取项目统计"""
    with ProjectManager() as proj_mgr:
        stats = proj_mgr.get_project_stats(project_id)
        
        return jsonify(success_response({
            "project_id": project_id,
            **stats
        }))


# ==================== 分红管理API ====================

@app.route('/api/dividend-pool', methods=['POST'])
@handle_error
def create_dividend_pool():
    """创建分红池"""
    data = request.json
    
    with DividendManager() as div_mgr:
        pool = div_mgr.create_dividend_pool(
            pool_name=data.get('pool_name'),
            pool_type=data.get('pool_type', 'expert'),
            initial_amount=Decimal(str(data.get('initial_amount'))) if data.get('initial_amount') else None
        )
        
        if pool:
            return jsonify(success_response({
                "pool_id": pool.id,
                "pool_name": pool.pool_name
            }, "分红池创建成功"))
        else:
            return error_response("分红池创建失败", 400)


@app.route('/api/dividend-pool/<int:pool_id>/stats', methods=['GET'])
@handle_error
def get_dividend_stats(pool_id: int):
    """获取分红池统计"""
    with DividendManager() as div_mgr:
        stats = div_mgr.get_dividend_stats(pool_id)
        
        return jsonify(success_response({
            "pool_id": pool_id,
            **stats
        }))


@app.route('/api/dividend-pool/<int:pool_id>/distribute', methods=['POST'])
@handle_error
def distribute_dividends(pool_id: int):
    """分配分红"""
    data = request.json
    
    with DividendManager() as div_mgr:
        success = div_mgr.distribute_dividends(
            pool_id=pool_id,
            distribution_amount=Decimal(str(data.get('distribution_amount'))) if data.get('distribution_amount') else None
        )
        
        if success:
            return jsonify(success_response(message="分红分配成功"))
        else:
            return error_response("分红分配失败", 400)


@app.route('/api/user/<int:user_id>/equities', methods=['GET'])
@handle_error
def get_user_equities(user_id: int):
    """获取用户的股权持有记录"""
    with DividendManager() as div_mgr:
        equities = div_mgr.get_user_equities(user_id)
        
        equity_list = [{
            "id": e.id,
            "pool_id": e.pool_id,
            "equity_percentage": e.equity_percentage,
            "granted_date": e.granted_date.isoformat() if e.granted_date else None,
            "expires_date": e.expires_date.isoformat() if e.expires_date else None,
            "status": e.status
        } for e in equities]
        
        return jsonify(success_response({
            "equities": equity_list,
            "count": len(equity_list)
        }))


@app.route('/api/user/<int:user_id>/dividends', methods=['GET'])
@handle_error
def get_user_dividends(user_id: int):
    """获取用户的分红记录"""
    with DividendManager() as div_mgr:
        dividends = div_mgr.get_user_dividends(user_id)
        
        dividend_list = [{
            "id": d.id,
            "pool_id": d.pool_id,
            "distribution_round": d.distribution_round,
            "total_pool_amount": float(d.total_pool_amount) if d.total_pool_amount else 0,
            "user_equity_percentage": d.user_equity_percentage,
            "dividend_amount": float(d.dividend_amount) if d.dividend_amount else 0,
            "status": d.status,
            "paid_at": d.paid_at.isoformat() if d.paid_at else None,
            "created_at": d.created_at.isoformat() if d.created_at else None
        } for d in dividends]
        
        return jsonify(success_response({
            "dividends": dividend_list,
            "count": len(dividend_list)
        }))


# ==================== 系统API ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify(success_response({
        "status": "healthy",
        "version": "1.0.0"
    }, "系统运行正常"))


@app.route('/api/info', methods=['GET'])
def system_info():
    """系统信息"""
    return jsonify(success_response({
        "name": "灵值生态园用户管理系统",
        "version": "1.0.0",
        "description": "基于合伙人模式的用户核心管理模块",
        "features": [
            "用户管理",
            "贡献值管理",
            "会员级别系统",
            "推荐和佣金系统",
            "项目参与和奖励系统",
            "分红股权系统"
        ]
    }))


# ==================== 主程序 ====================

if __name__ == '__main__':
    print("=" * 80)
    print("灵值生态园用户管理系统 - API服务")
    print("版本: v1.0.0")
    print("启动时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 80)
    print()
    print("API接口:")
    print("  用户管理: http://localhost:5000/api/user")
    print("  推荐管理: http://localhost:5000/api/referral")
    print("  项目管理: http://localhost:5000/api/project")
    print("  分红管理: http://localhost:5000/api/dividend-pool")
    print()
    print("健康检查: http://localhost:5000/api/health")
    print("系统信息: http://localhost:5000/api/info")
    print()
    print("=" * 80)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
