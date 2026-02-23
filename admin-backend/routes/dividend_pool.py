"""
分红池管理路由蓝图
包含分红记录、分配和统计功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
from datetime import datetime, timedelta

dividend_pool_bp = Blueprint('dividend_pool', __name__)

# 导入配置
from config import config
DATABASE = config.DATABASE_PATH

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# ============ 获取分红统计 ============

@dividend_pool_bp.route('/admin/dividends/stats', methods=['GET'])
def get_dividend_stats():
    """获取分红统计"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 总分红池
        cursor.execute("SELECT SUM(amount) as total FROM dividend_pool WHERE status = 'active'")
        total_pool = cursor.fetchone()['total'] or 0

        # 已分配分红
        cursor.execute("SELECT SUM(amount) as distributed FROM dividend_records WHERE status = 'distributed'")
        distributed = cursor.fetchone()['distributed'] or 0

        # 待分配分红
        pending = total_pool - distributed

        # 本月分配
        this_month = datetime.now().strftime('%Y-%m')
        cursor.execute("""
            SELECT SUM(amount) as month_amount
            FROM dividend_records
            WHERE strftime('%Y-%m', distributed_at) = ?
            AND status = 'distributed'
        """, (this_month,))
        month_amount = cursor.fetchone()['month_amount'] or 0

        # 分配人数
        cursor.execute("""
            SELECT COUNT(DISTINCT user_id) as user_count
            FROM dividend_records
            WHERE status = 'distributed'
        """)
        user_count = cursor.fetchone()['user_count'] or 0

        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'totalPool': total_pool,
                'distributed': distributed,
                'pending': pending,
                'monthAmount': month_amount,
                'userCount': user_count
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分红统计失败: {str(e)}'
        }), 500

# ============ 获取分红记录 ============

@dividend_pool_bp.route('/admin/dividends', methods=['GET'])
def get_dividends():
    """获取分红记录"""
    try:
        # 获取分页参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
        user_id = request.args.get('userId', '')
        status = request.args.get('status', '')
        start_date = request.args.get('startDate', '')
        end_date = request.args.get('endDate', '')

        offset = (page - 1) * page_size

        conn = get_db()
        cursor = conn.cursor()

        # 构建查询条件
        where_conditions = []
        params = []

        if user_id:
            where_conditions.append("dr.user_id = ?")
            params.append(user_id)

        if status:
            where_conditions.append("dr.status = ?")
            params.append(status)

        if start_date:
            where_conditions.append("dr.distributed_at >= ?")
            params.append(start_date)

        if end_date:
            where_conditions.append("dr.distributed_at <= ?")
            params.append(end_date)

        where_clause = ""
        if where_conditions:
            where_clause = "WHERE " + " AND ".join(where_conditions)

        # 查询总数
        count_sql = f"SELECT COUNT(*) as total FROM dividend_records dr {where_clause}"
        cursor.execute(count_sql, params)
        total = cursor.fetchone()['total']

        # 查询分红记录
        sql = f"""
            SELECT dr.*, u.username, u.phone
            FROM dividend_records dr
            LEFT JOIN users u ON dr.user_id = u.id
            {where_clause}
            ORDER BY dr.distributed_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(sql, params + [page_size, offset])
        dividends = cursor.fetchall()

        result = [dict(dividend) for dividend in dividends]

        conn.close()

        return jsonify({
            'success': True,
            'data': result,
            'pagination': {
                'page': page,
                'pageSize': page_size,
                'total': total,
                'totalPages': (total + page_size - 1) // page_size
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分红记录失败: {str(e)}'
        }), 500

# ============ 分配分红 ============

@dividend_pool_bp.route('/admin/dividends/distribute', methods=['POST'])
def distribute_dividends():
    """分配分红"""
    try:
        data = request.json

        user_id = data.get('userId')
        amount = data.get('amount')
        reason = data.get('reason', '')
        pool_id = data.get('poolId', 1)

        if not user_id or not amount:
            return jsonify({
                'success': False,
                'message': '用户ID和分红金额不能为空'
            }), 400

        if amount <= 0:
            return jsonify({
                'success': False,
                'message': '分红金额必须大于0'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查用户是否存在
        cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            conn.close()
            return jsonify({
                'success': False,
                'message': '用户不存在'
            }), 404

        # 检查分红池是否有足够余额
        cursor.execute("""
            SELECT amount FROM dividend_pool WHERE id = ? AND status = 'active'
        """, (pool_id,))
        pool = cursor.fetchone()
        if not pool:
            conn.close()
            return jsonify({
                'success': False,
                'message': '分红池不存在或已关闭'
            }), 404

        if pool['amount'] < amount:
            conn.close()
            return jsonify({
                'success': False,
                'message': f'分红池余额不足，当前余额: {pool["amount"]}'
            }), 400

        # 创建分红记录
        cursor.execute("""
            INSERT INTO dividend_records (
                user_id, pool_id, amount, reason, status,
                distributed_at, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'distributed', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (user_id, pool_id, amount, reason))

        # 更新分红池余额
        cursor.execute("""
            UPDATE dividend_pool SET
                amount = amount - ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (amount, pool_id))

        # 增加用户灵值
        cursor.execute("""
            UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?
        """, (amount, user_id))

        # 记录灵值消费记录
        cursor.execute("""
            INSERT INTO lingzhi_consumption_records (
                user_id, consumption_type, consumption_item, lingzhi_amount, description
            ) VALUES (?, 'dividend', 'reward', ?, ?)
        """, (user_id, amount, f'分红奖励: {reason}' if reason else '分红奖励'))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'成功分配 {amount} 灵值给用户 {user["username"]}'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'分配分红失败: {str(e)}'
        }), 500

# ============ 批量分配分红 ============

@dividend_pool_bp.route('/admin/dividends/batch-distribute', methods=['POST'])
def batch_distribute_dividends():
    """批量分配分红"""
    try:
        data = request.json
        allocations = data.get('allocations', [])  # [{userId, amount, reason}, ...]
        pool_id = data.get('poolId', 1)

        if not allocations:
            return jsonify({
                'success': False,
                'message': '请提供分配列表'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 检查分红池是否有足够余额
        cursor.execute("""
            SELECT amount FROM dividend_pool WHERE id = ? AND status = 'active'
        """, (pool_id,))
        pool = cursor.fetchone()
        if not pool:
            conn.close()
            return jsonify({
                'success': False,
                'message': '分红池不存在或已关闭'
            }), 404

        total_amount = sum(alloc['amount'] for alloc in allocations)
        if pool['amount'] < total_amount:
            conn.close()
            return jsonify({
                'success': False,
                'message': f'分红池余额不足，需要: {total_amount}，当前余额: {pool["amount"]}'
            }), 400

        # 批量分配
        success_count = 0
        failed_users = []

        for alloc in allocations:
            try:
                user_id = alloc['userId']
                amount = alloc['amount']
                reason = alloc.get('reason', '')

                # 检查用户是否存在
                cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
                user = cursor.fetchone()
                if not user:
                    failed_users.append({'userId': user_id, 'reason': '用户不存在'})
                    continue

                # 创建分红记录
                cursor.execute("""
                    INSERT INTO dividend_records (
                        user_id, pool_id, amount, reason, status,
                        distributed_at, created_at, updated_at
                    ) VALUES (?, ?, ?, ?, 'distributed', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                """, (user_id, pool_id, amount, reason))

                # 增加用户灵值
                cursor.execute("""
                    UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?
                """, (amount, user_id))

                # 记录灵值消费记录
                cursor.execute("""
                    INSERT INTO lingzhi_consumption_records (
                        user_id, consumption_type, consumption_item, lingzhi_amount, description
                    ) VALUES (?, 'dividend', 'reward', ?, ?)
                """, (user_id, amount, f'分红奖励: {reason}' if reason else '分红奖励'))

                success_count += 1

            except Exception as e:
                failed_users.append({'userId': alloc['userId'], 'reason': str(e)})

        # 更新分红池余额
        cursor.execute("""
            UPDATE dividend_pool SET
                amount = amount - ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (total_amount, pool_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': f'批量分配完成，成功: {success_count}，失败: {len(failed_users)}',
            'data': {
                'successCount': success_count,
                'failedUsers': failed_users
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'批量分配分红失败: {str(e)}'
        }), 500

# ============ 获取分红池列表 ============

@dividend_pool_bp.route('/admin/dividend-pools', methods=['GET'])
def get_dividend_pools():
    """获取分红池列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM dividend_pool ORDER BY created_at DESC")
        pools = cursor.fetchall()

        result = [dict(pool) for pool in pools]

        conn.close()

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取分红池列表失败: {str(e)}'
        }), 500
