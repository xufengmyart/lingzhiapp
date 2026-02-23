"""
充值系统路由蓝图
包含充值档位、订单创建、支付完成、转账凭证等功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
import random
from datetime import datetime

recharge_bp = Blueprint('recharge', __name__)

# 导入配置
from config import config
DATABASE = config.DATABASE_PATH

# 辅助函数
def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_order_no():
    """生成订单号"""
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    random_str = ''.join(random.choices('0123456789', k=6))
    return f"RE{timestamp}{random_str}"

# ============ 充值档位 ============

@recharge_bp.route('/recharge/tiers', methods=['GET'])
def get_recharge_tiers():
    """获取充值档位列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                name,
                description,
                price,
                base_lingzhi,
                bonus_lingzhi,
                bonus_percentage,
                partner_level,
                benefits,
                sort_order
            FROM recharge_tiers
            WHERE status = 'active'
            ORDER BY sort_order ASC, price ASC
            """
        )
        tiers = []
        for row in cursor.fetchall():
            tier = dict(row)
            tier['total_lingzhi'] = tier['base_lingzhi'] + tier['bonus_lingzhi']
            tiers.append(tier)

        conn.close()

        return jsonify({
            'success': True,
            'data': tiers
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取充值档位失败: {str(e)}'
        }), 500

# ============ 充值订单 ============

@recharge_bp.route('/recharge/create-order', methods=['POST'])
def create_recharge_order():
    """创建充值订单"""
    try:
        # TODO: 验证JWT令牌
        data = request.json
        user_id = data.get('user_id')
        tier_id = data.get('tier_id')
        payment_method = data.get('payment_method', 'online')

        if not user_id or not tier_id:
            return jsonify({
                'success': False,
                'message': '用户ID和充值档位ID不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询充值档位
        cursor.execute(
            """
            SELECT
                id,
                name,
                price,
                base_lingzhi,
                bonus_lingzhi
            FROM recharge_tiers
            WHERE id = ? AND status = 'active'
            """,
            (tier_id,)
        )
        tier = cursor.fetchone()

        if not tier:
            conn.close()
            return jsonify({
                'success': False,
                'message': '充值档位不存在'
            }), 404

        # 计算总灵值
        total_lingzhi = tier['base_lingzhi'] + tier['bonus_lingzhi']

        # 创建订单
        order_no = generate_order_no()
        cursor.execute(
            """
            INSERT INTO recharge_records (
                user_id,
                tier_id,
                order_no,
                amount,
                base_lingzhi,
                bonus_lingzhi,
                total_lingzhi,
                payment_method,
                payment_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
            """,
            (
                user_id,
                tier_id,
                order_no,
                tier['price'],
                tier['base_lingzhi'],
                tier['bonus_lingzhi'],
                total_lingzhi,
                payment_method
            )
        )
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'data': {
                'order_no': order_no,
                'record_id': record_id,
                'amount': tier['price'],
                'total_lingzhi': total_lingzhi
            }
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建订单失败: {str(e)}'
        }), 500

# ============ 完成支付 ============

@recharge_bp.route('/recharge/complete-payment', methods=['POST'])
def complete_recharge_payment():
    """完成充值支付"""
    try:
        data = request.json
        order_no = data.get('order_no')
        payment_status = data.get('payment_status', 'success')
        transaction_id = data.get('transaction_id')

        if not order_no:
            return jsonify({
                'success': False,
                'message': '订单号不能为空'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询订单
        cursor.execute(
            """
            SELECT
                id,
                user_id,
                total_lingzhi,
                payment_status
            FROM recharge_records
            WHERE order_no = ?
            """,
            (order_no,)
        )
        record = cursor.fetchone()

        if not record:
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单不存在'
            }), 404

        # 检查订单状态
        if record['payment_status'] == 'success':
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单已完成支付'
            }), 400

        # 更新订单状态
        cursor.execute(
            """
            UPDATE recharge_records
            SET payment_status = ?,
                payment_time = CURRENT_TIMESTAMP,
                transaction_id = ?
            WHERE order_no = ?
            """,
            (payment_status, transaction_id, order_no)
        )

        # 如果支付成功，增加用户灵值
        if payment_status == 'success':
            cursor.execute(
                "UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?",
                (record['total_lingzhi'], record['user_id'])
            )

            # 记录灵值消费（反向记录）
            cursor.execute(
                """
                INSERT INTO lingzhi_consumption_records
                (user_id, consumption_type, consumption_item, lingzhi_amount, description)
                VALUES (?, 'recharge', ?, ?, ?)
                """,
                (record['user_id'], record['id'], record['total_lingzhi'], f'充值订单: {order_no}')
            )

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '支付完成'
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'完成支付失败: {str(e)}'
        }), 500

# ============ 公司收款账户 ============

@recharge_bp.route('/company/accounts', methods=['GET'])
def get_company_accounts():
    """获取公司收款账户"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                id,
                account_name,
                account_number,
                bank_name,
                bank_branch,
                company_name,
                company_credit_code,
                account_type
            FROM company_accounts
            WHERE is_active = 1
            ORDER BY sort_order ASC
            """
        )
        accounts = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return jsonify({
            'success': True,
            'data': accounts
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取收款账户失败: {str(e)}'
        }), 500

# ============ 转账凭证 ============

@recharge_bp.route('/recharge/upload-voucher', methods=['POST'])
def upload_transfer_voucher():
    """上传转账凭证"""
    try:
        # TODO: 验证JWT令牌
        data = request.json
        user_id = data.get('user_id')
        recharge_record_id = data.get('recharge_record_id')
        image_url = data.get('image_url')
        transfer_amount = data.get('transfer_amount')
        transfer_time = data.get('transfer_time')
        transfer_account = data.get('transfer_account')
        remark = data.get('remark', '')

        if not all([user_id, recharge_record_id, image_url, transfer_amount]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400

        conn = get_db()
        cursor = conn.cursor()

        # 查询订单
        cursor.execute(
            """
            SELECT id, user_id, amount, payment_status
            FROM recharge_records
            WHERE id = ?
            """,
            (recharge_record_id,)
        )
        record = cursor.fetchone()

        if not record:
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单不存在'
            }), 404

        if record['payment_status'] != 'pending':
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单状态不正确'
            }), 400

        # 创建转账凭证
        cursor.execute(
            """
            INSERT INTO transfer_vouchers (
                recharge_record_id,
                user_id,
                image_url,
                transfer_amount,
                transfer_time,
                transfer_account,
                remark,
                audit_status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
            """,
            (
                recharge_record_id,
                user_id,
                image_url,
                transfer_amount,
                transfer_time,
                transfer_account,
                remark
            )
        )
        voucher_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'message': '转账凭证上传成功',
            'data': {'voucher_id': voucher_id}
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'上传凭证失败: {str(e)}'
        }), 500

@recharge_bp.route('/recharge/voucher/<int:voucher_id>', methods=['GET'])
def get_voucher_detail(voucher_id):
    """获取转账凭证详情"""
    try:
        # TODO: 验证JWT令牌
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                tv.*,
                rr.order_no,
                rr.amount as order_amount
            FROM transfer_vouchers tv
            LEFT JOIN recharge_records rr ON tv.recharge_record_id = rr.id
            WHERE tv.id = ?
            """,
            (voucher_id,)
        )
        voucher = cursor.fetchone()

        if not voucher:
            conn.close()
            return jsonify({
                'success': False,
                'message': '凭证不存在'
            }), 404

        conn.close()

        return jsonify({
            'success': True,
            'data': dict(voucher)
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取凭证详情失败: {str(e)}'
        }), 500
