"""
资产交易市场对接API
模拟交易市场功能
"""

from flask import Blueprint, jsonify, request
from database import get_db
from datetime import datetime
import random

market_bp = Blueprint('market', __name__)

# 模拟市场数据
MARKET_DATA = {
    'total_volume': 1250000.00,
    '24h_volume': 45000.00,
    'active_traders': 156,
    'listed_assets': 23,
}

# 模拟价格历史数据
def generate_price_history(base_price, days=30):
    """生成模拟价格历史"""
    history = []
    price = base_price
    
    for i in range(days):
        # 随机波动 -5% 到 +5%
        change = random.uniform(-0.05, 0.05)
        price = price * (1 + change)
        volume = random.uniform(1000, 10000)
        
        history.append({
            'date': datetime.now().date().isoformat(),
            'price': round(price, 2),
            'volume': round(volume, 2),
            'change': round(change * 100, 2)
        })
    
    return history


@market_bp.route('/market/stats', methods=['GET'])
def get_market_stats():
    """获取市场统计数据"""
    try:
        return jsonify({
            'success': True,
            'message': '获取市场统计成功',
            'data': MARKET_DATA
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取市场统计失败: {str(e)}',
            'data': None
        }), 500


@market_bp.route('/market/assets', methods=['GET'])
def get_market_assets():
    """获取市场挂牌资产列表"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, project_id as projectId,
                asset_name as assetName, asset_type as assetType,
                estimated_value as estimatedValue,
                token_address as tokenAddress, token_symbol as tokenSymbol,
                total_supply as totalSupply,
                current_price as currentPrice,
                status
            FROM data_assets
            WHERE status = 'listed' OR status = 'tokenized'
        """)
        
        assets = []
        for row in cursor.fetchall():
            price = row[9] or random.uniform(10, 1000)
            change_24h = random.uniform(-10, 10)
            
            assets.append({
                'id': row[0],
                'projectId': row[1],
                'assetName': row[2],
                'assetType': row[3],
                'estimatedValue': row[4],
                'tokenAddress': row[5],
                'tokenSymbol': row[6],
                'totalSupply': row[7],
                'currentPrice': round(price, 2),
                'change24h': round(change_24h, 2),
                'volume24h': round(random.uniform(1000, 50000), 2),
                'status': row[10]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取市场资产成功',
            'data': assets
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取市场资产失败: {str(e)}',
            'data': []
        }), 500


@market_bp.route('/market/assets/<int:asset_id>/price-history', methods=['GET'])
def get_asset_price_history(asset_id):
    """获取资产价格历史"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT current_price FROM data_assets WHERE id = ?
        """, (asset_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return jsonify({
                'success': False,
                'message': '资产不存在',
                'data': None
            }), 404
        
        base_price = result[0] or random.uniform(10, 1000)
        history = generate_price_history(base_price)
        
        return jsonify({
            'success': True,
            'message': '获取价格历史成功',
            'data': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取价格历史失败: {str(e)}',
            'data': []
        }), 500


@market_bp.route('/market/assets/<int:asset_id>/list', methods=['POST'])
def list_asset(asset_id):
    """挂牌资产到市场"""
    try:
        data = request.json
        price = data.get('price', 0)
        min_order = data.get('min_order', 1)
        
        if price <= 0:
            return jsonify({
                'success': False,
                'message': '挂牌价格必须大于0',
                'data': None
            }), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 更新资产状态和价格
        cursor.execute("""
            UPDATE data_assets
            SET status = 'listed',
                current_price = ?,
                updated_at = ?
            WHERE id = ?
        """, (price, datetime.now(), asset_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '资产挂牌成功',
            'data': {
                'assetId': asset_id,
                'price': price,
                'minOrder': min_order
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'资产挂牌失败: {str(e)}',
            'data': None
        }), 500


@market_bp.route('/market/orders', methods=['POST'])
def create_order():
    """创建交易订单"""
    try:
        data = request.json
        asset_id = data.get('assetId')
        order_type = data.get('orderType')  # buy, sell
        amount = data.get('amount', 0)
        price = data.get('price', 0)
        user_id = data.get('userId')
        
        if not asset_id or not order_type or amount <= 0:
            return jsonify({
                'success': False,
                'message': '参数不完整',
                'data': None
            }), 400
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 创建订单记录
        order_id = cursor.execute("""
            INSERT INTO market_orders
            (asset_id, order_type, amount, price, user_id, status, created_at)
            VALUES (?, ?, ?, ?, ?, 'pending', ?)
        """, (asset_id, order_type, amount, price, user_id, datetime.now()))
        
        conn.commit()
        conn.close()
        
        # 模拟订单成交（实际应该在匹配引擎中处理）
        order_status = 'filled' if random.random() > 0.3 else 'pending'
        
        return jsonify({
            'success': True,
            'message': '订单创建成功',
            'data': {
                'orderId': cursor.lastrowid,
                'assetId': asset_id,
                'orderType': order_type,
                'amount': amount,
                'price': price,
                'totalValue': round(amount * price, 2),
                'status': order_status,
                'timestamp': datetime.now().isoformat()
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建订单失败: {str(e)}',
            'data': None
        }), 500


@market_bp.route('/market/orders', methods=['GET'])
def get_orders():
    """获取订单列表"""
    try:
        asset_id = request.args.get('assetId')
        user_id = request.args.get('userId')
        status = request.args.get('status')
        
        conn = get_db()
        cursor = conn.cursor()
        
        # 确保表存在
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id INTEGER NOT NULL,
                order_type VARCHAR(10) NOT NULL,
                amount DECIMAL(20, 2) NOT NULL,
                price DECIMAL(20, 2) NOT NULL,
                user_id INTEGER,
                status VARCHAR(20) DEFAULT 'pending',
                filled_amount DECIMAL(20, 2) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        query = "SELECT * FROM market_orders WHERE 1=1"
        params = []
        
        if asset_id:
            query += " AND asset_id = ?"
            params.append(asset_id)
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        if status:
            query += " AND status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT 100"
        
        cursor.execute(query, params)
        orders = cursor.fetchall()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': '获取订单成功',
            'data': [
                {
                    'id': row[0],
                    'assetId': row[1],
                    'orderType': row[2],
                    'amount': row[3],
                    'price': row[4],
                    'userId': row[5],
                    'status': row[6],
                    'filledAmount': row[7],
                    'createdAt': row[8],
                    'updatedAt': row[9]
                }
                for row in orders
            ]
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取订单失败: {str(e)}',
            'data': []
        }), 500
