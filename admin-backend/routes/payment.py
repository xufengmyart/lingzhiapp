"""
支付集成 API
提供支付宝、微信支付等功能
"""

from flask import Blueprint, request, jsonify
import sqlite3
import hashlib
import json
import random
import time
from datetime import datetime

# 导入配置
from config import config

payment_bp = Blueprint('payment', __name__)

DATABASE = config.DATABASE_PATH

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def generate_payment_params(order_no, amount, payment_method):
    """生成支付参数（模拟真实支付接口）"""
    timestamp = int(time.time())
    nonce_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))
    
    # 模拟签名（真实环境中需要使用支付宝/微信的签名算法）
    sign_str = f"amount={amount}&nonce_str={nonce_str}&order_no={order_no}&timestamp={timestamp}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()
    
    return {
        'order_no': order_no,
        'amount': amount,
        'timestamp': timestamp,
        'nonce_str': nonce_str,
        'sign': sign,
        'payment_method': payment_method
    }

# ============ 支付宝支付 ============

@payment_bp.route('/payment/alipay/create', methods=['POST'])
def create_alipay_order():
    """创建支付宝支付订单"""
    try:
        data = request.get_json()
        order_no = data.get('order_no')
        
        if not order_no:
            return jsonify({
                'success': False,
                'message': '订单号不能为空'
            }), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询订单
        cursor.execute(
            "SELECT id, order_no, amount, user_id, payment_status FROM recharge_records WHERE order_no = ?",
            (order_no,)
        )
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单不存在'
            }), 404
        
        if order['payment_status'] == 'success':
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单已完成支付'
            }), 400
        
        # 生成支付参数
        payment_params = generate_payment_params(order_no, order['amount'], 'alipay')
        
        # 模拟支付宝支付URL
        payment_url = f"https://openapi.alipay.com/gateway.do?method=alipay.trade.page.pay&out_trade_no={order_no}&total_amount={order['amount']}"
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '支付订单创建成功',
            'data': {
                'order_no': order_no,
                'amount': order['amount'],
                'payment_url': payment_url,
                'payment_params': payment_params,
                'qr_code': f"https://qr.alipay.com/{order_no}",  # 模拟二维码
                'expire_time': 900  # 15分钟过期
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建支付订单失败: {str(e)}'
        }), 500

@payment_bp.route('/payment/alipay/callback', methods=['POST'])
def alipay_callback():
    """支付宝支付回调"""
    try:
        # 获取回调数据
        out_trade_no = request.form.get('out_trade_no')
        trade_status = request.form.get('trade_status')
        trade_no = request.form.get('trade_no')
        
        if not out_trade_no or trade_status != 'TRADE_SUCCESS':
            return 'fail'
        
        # 更新订单状态
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE recharge_records
            SET payment_status = 'success',
                payment_time = CURRENT_TIMESTAMP,
                transaction_id = ?
            WHERE order_no = ? AND payment_status = 'pending'
            """,
            (trade_no, out_trade_no)
        )
        
        # 增加用户灵值
        cursor.execute(
            """
            UPDATE users SET total_lingzhi = total_lingzhi + 
            (SELECT total_lingzhi FROM recharge_records WHERE order_no = ?)
            WHERE id = (SELECT user_id FROM recharge_records WHERE order_no = ?)
            """,
            (out_trade_no, out_trade_no)
        )
        
        conn.commit()
        conn.close()
        
        return 'success'
        
    except Exception as e:
        print(f"支付宝回调处理失败: {e}")
        return 'fail'

# ============ 微信支付 ============

@payment_bp.route('/payment/wechat/create', methods=['POST'])
def create_wechat_order():
    """创建微信支付订单"""
    try:
        data = request.get_json()
        order_no = data.get('order_no')
        
        if not order_no:
            return jsonify({
                'success': False,
                'message': '订单号不能为空'
            }), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询订单
        cursor.execute(
            "SELECT id, order_no, amount, user_id, payment_status FROM recharge_records WHERE order_no = ?",
            (order_no,)
        )
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单不存在'
            }), 404
        
        if order['payment_status'] == 'success':
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单已完成支付'
            }), 400
        
        # 生成支付参数
        payment_params = generate_payment_params(order_no, order['amount'], 'wechat')
        
        # 模拟微信支付二维码
        qr_code = f"weixin://wxpay/bizpayurl?pr={order_no}"
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '支付订单创建成功',
            'data': {
                'order_no': order_no,
                'amount': order['amount'],
                'qr_code': qr_code,
                'payment_params': payment_params,
                'code_url': qr_code,
                'expire_time': 900  # 15分钟过期
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建支付订单失败: {str(e)}'
        }), 500

@payment_bp.route('/payment/wechat/callback', methods=['POST'])
def wechat_callback():
    """微信支付回调"""
    try:
        # 获取回调数据（XML格式）
        # 真实环境中需要解析XML
        data = request.get_data(as_text=True)
        
        # 模拟解析
        out_trade_no = request.form.get('out_trade_no', '')
        return_code = request.form.get('return_code', 'FAIL')
        transaction_id = request.form.get('transaction_id', '')
        
        if return_code != 'SUCCESS':
            return '<xml><return_code><![CDATA[FAIL]]></return_code></xml>'
        
        # 更新订单状态
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            UPDATE recharge_records
            SET payment_status = 'success',
                payment_time = CURRENT_TIMESTAMP,
                transaction_id = ?
            WHERE order_no = ? AND payment_status = 'pending'
            """,
            (transaction_id, out_trade_no)
        )
        
        # 增加用户灵值
        cursor.execute(
            """
            UPDATE users SET total_lingzhi = total_lingzhi + 
            (SELECT total_lingzhi FROM recharge_records WHERE order_no = ?)
            WHERE id = (SELECT user_id FROM recharge_records WHERE order_no = ?)
            """,
            (out_trade_no, out_trade_no)
        )
        
        conn.commit()
        conn.close()
        
        return '<xml><return_code><![CDATA[SUCCESS]]></return_code><return_msg><![CDATA[OK]]></return_msg></xml>'
        
    except Exception as e:
        print(f"微信回调处理失败: {e}")
        return '<xml><return_code><![CDATA[FAIL]]></return_code></xml>'

# ============ 查询支付状态 ============

@payment_bp.route('/payment/status/<order_no>', methods=['GET'])
def query_payment_status(order_no):
    """查询支付状态"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT order_no, payment_status, payment_time, transaction_id
            FROM recharge_records
            WHERE order_no = ?
            """,
            (order_no,)
        )
        order = cursor.fetchone()
        
        conn.close()
        
        if not order:
            return jsonify({
                'success': False,
                'message': '订单不存在'
            }), 404
        
        return jsonify({
            'success': True,
            'data': {
                'order_no': order['order_no'],
                'payment_status': order['payment_status'],
                'payment_time': order['payment_time'],
                'transaction_id': order['transaction_id']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'查询支付状态失败: {str(e)}'
        }), 500

# ============ 模拟支付（测试用） ============

@payment_bp.route('/payment/simulate/<order_no>', methods=['POST'])
def simulate_payment(order_no):
    """模拟支付（仅用于测试）"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # 查询订单
        cursor.execute(
            """
            SELECT id, order_no, amount, user_id, payment_status, total_lingzhi
            FROM recharge_records
            WHERE order_no = ?
            """,
            (order_no,)
        )
        order = cursor.fetchone()
        
        if not order:
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单不存在'
            }), 404
        
        if order['payment_status'] == 'success':
            conn.close()
            return jsonify({
                'success': False,
                'message': '订单已完成支付'
            }), 400
        
        # 生成模拟交易ID
        transaction_id = f"SIM{int(time.time())}{random.randint(1000, 9999)}"
        
        # 更新订单状态
        cursor.execute(
            """
            UPDATE recharge_records
            SET payment_status = 'success',
                payment_time = CURRENT_TIMESTAMP,
                transaction_id = ?
            WHERE order_no = ?
            """,
            (transaction_id, order_no)
        )
        
        # 增加用户灵值
        cursor.execute(
            "UPDATE users SET total_lingzhi = total_lingzhi + ? WHERE id = ?",
            (order['total_lingzhi'], order['user_id'])
        )
        
        # 记录灵值消费
        cursor.execute(
            """
            INSERT INTO lingzhi_consumption_records
            (user_id, consumption_type, consumption_item, lingzhi_amount, description)
            VALUES (?, 'recharge', ?, ?, ?)
            """,
            (order['user_id'], order['id'], order['total_lingzhi'], f'模拟充值订单: {order_no}')
        )
        
        conn.commit()
        
        # 查询更新后的用户灵值
        cursor.execute("SELECT total_lingzhi FROM users WHERE id = ?", (order['user_id'],))
        user = cursor.fetchone()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '模拟支付成功',
            'data': {
                'order_no': order_no,
                'transaction_id': transaction_id,
                'amount': order['amount'],
                'total_lingzhi': order['total_lingzhi'],
                'new_balance': user['total_lingzhi']
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'模拟支付失败: {str(e)}'
        }), 500
