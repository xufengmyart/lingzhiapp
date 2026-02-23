"""
数字资产系统API
实现通证（Token）和SBT（Soulbound Token）管理
"""

from flask import Blueprint, request, jsonify
from functools import wraps
from datetime import datetime
import json
import os
import sys
import sqlite3

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config

assets_bp = Blueprint('digital_assets', __name__, url_prefix='/api/assets')

DB_PATH = config.DATABASE_PATH

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': '未登录'}), 401
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = request.headers.get('X-User-ID')
        if not user_id:
            return jsonify({'error': '未登录'}), 401
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        if not result or result[0] != 'admin':
            return jsonify({'error': '需要管理员权限'}), 403
        request.user_id = user_id
        return f(*args, **kwargs)
    return decorated_function

# ==================== 通证管理 ====================

@assets_bp.route('/tokens', methods=['POST'])
@admin_required
def create_token():
    """创建通证"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO digital_tokens (
                name, symbol, description, token_type,
                total_supply, circulating_supply, decimals,
                contract_address, created_by, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('symbol'),
            data.get('description'),
            data.get('token_type', 'erc20'),
            data.get('total_supply', 0),
            0,  # circulating_supply
            data.get('decimals', 18),
            data.get('contract_address'),
            request.user_id,
            'active'
        ))
        
        token_id = cursor.lastrowid
        conn.commit()
        
        conn.close()
        return jsonify({'message': '通证创建成功', 'id': token_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@assets_bp.route('/tokens', methods=['GET'])
def get_tokens():
    """获取通证列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取总数
    cursor.execute("SELECT COUNT(*) FROM digital_tokens")
    total = cursor.fetchone()[0]
    
    # 分页查询
    cursor.execute('''
        SELECT * FROM digital_tokens
        ORDER BY created_at DESC
        LIMIT ? OFFSET ?
    ''', (per_page, (page - 1) * per_page))
    
    tokens = cursor.fetchall()
    
    result = []
    for token in tokens:
        result.append({
            'id': token[0],
            'name': token[1],
            'symbol': token[2],
            'description': token[3],
            'token_type': token[4],
            'total_supply': token[5],
            'circulating_supply': token[6],
            'decimals': token[7],
            'contract_address': token[8],
            'status': token[9],
            'created_at': token[10],
            'created_by': token[11]
        })
    
    conn.close()
    
    return jsonify({
        'tokens': result,
        'total': total,
        'page': page,
        'per_page': per_page
    })

# ==================== 用户通证余额 ====================

@assets_bp.route('/tokens/<int:token_id>/balance', methods=['GET'])
@login_required
def get_token_balance(token_id):
    """获取用户通证余额"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT balance FROM user_token_balances
        WHERE user_id = ? AND token_id = ?
    ''', (request.user_id, token_id))
    
    result = cursor.fetchone()
    
    if result:
        balance = result[0]
    else:
        balance = 0
    
    conn.close()
    return jsonify({'balance': balance})

@assets_bp.route('/tokens/<int:token_id>/transfer', methods=['POST'])
@login_required
def transfer_token(token_id):
    """转账通证"""
    data = request.json
    to_user_id = data.get('to_user_id')
    amount = data.get('amount', 0)
    
    if not to_user_id or amount <= 0:
        return jsonify({'error': '参数错误'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查余额
        cursor.execute('''
            SELECT balance FROM user_token_balances
            WHERE user_id = ? AND token_id = ?
        ''', (request.user_id, token_id))
        
        result = cursor.fetchone()
        if not result or result[0] < amount:
            conn.close()
            return jsonify({'error': '余额不足'}), 400
        
        # 扣除发送方余额
        cursor.execute('''
            UPDATE user_token_balances
            SET balance = balance - ?
            WHERE user_id = ? AND token_id = ?
        ''', (amount, request.user_id, token_id))
        
        # 增加接收方余额
        cursor.execute('''
            INSERT OR REPLACE INTO user_token_balances
            (user_id, token_id, balance, updated_at)
            VALUES (?, ?, ?, ?)
        ''', (to_user_id, token_id, amount, datetime.now().isoformat()))
        
        # 创建交易记录
        cursor.execute('''
            INSERT INTO token_transactions (
                from_user_id, to_user_id, token_id, amount,
                transaction_type, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.user_id,
            to_user_id,
            token_id,
            amount,
            'transfer',
            'completed',
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': '转账成功'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

# ==================== SBT管理 ====================

@assets_bp.route('/sbt', methods=['POST'])
@admin_required
def create_sbt_template():
    """创建SBT模板"""
    data = request.json
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO sbt_templates (
                name, description, category, attributes_schema,
                rarity, max_mint_count, created_by, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data.get('name'),
            data.get('description'),
            data.get('category'),
            json.dumps(data.get('attributes_schema', {})),
            data.get('rarity', 'common'),
            data.get('max_mint_count'),
            request.user_id,
            'active'
        ))
        
        template_id = cursor.lastrowid
        conn.commit()
        
        conn.close()
        return jsonify({'message': 'SBT模板创建成功', 'id': template_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@assets_bp.route('/sbt', methods=['GET'])
def get_sbt_templates():
    """获取SBT模板列表"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    category = request.args.get('category')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    query = "SELECT * FROM sbt_templates WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    # 获取总数
    count_query = query.replace('*', 'COUNT(*)')
    cursor.execute(count_query, params)
    total = cursor.fetchone()[0]
    
    # 分页查询
    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([per_page, (page - 1) * per_page])
    
    cursor.execute(query, params)
    templates = cursor.fetchall()
    
    result = []
    for template in templates:
        result.append({
            'id': template[0],
            'name': template[1],
            'description': template[2],
            'category': template[3],
            'attributes_schema': json.loads(template[4]) if template[4] else {},
            'rarity': template[5],
            'max_mint_count': template[6],
            'minted_count': template[7],
            'status': template[8],
            'created_at': template[9],
            'created_by': template[10]
        })
    
    conn.close()
    
    return jsonify({
        'templates': result,
        'total': total,
        'page': page,
        'per_page': per_page
    })

@assets_bp.route('/sbt/<int:template_id>/mint', methods=['POST'])
@login_required
def mint_sbt(template_id):
    """铸造SBT"""
    data = request.json
    attributes = data.get('attributes', {})
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 检查模板
        cursor.execute("SELECT * FROM sbt_templates WHERE id = ?", (template_id,))
        template = cursor.fetchone()
        
        if not template:
            conn.close()
            return jsonify({'error': '模板不存在'}), 404
        
        # 检查限制
        max_mint = template[6]
        minted = template[7]
        
        if max_mint and minted >= max_mint:
            conn.close()
            return jsonify({'error': '已达到最大铸造数量'}), 400
        
        # 检查是否已拥有（SBT不可转移）
        cursor.execute('''
            SELECT id FROM user_sbt
            WHERE user_id = ? AND template_id = ?
        ''', (request.user_id, template_id))
        
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': '您已拥有该SBT'}), 400
        
        # 铸造SBT
        cursor.execute('''
            INSERT INTO user_sbt (
                user_id, template_id, token_id,
                attributes, minted_at
            ) VALUES (?, ?, ?, ?, ?)
        ''', (
            request.user_id,
            template_id,
            f"SBT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{request.user_id}",
            json.dumps(attributes),
            datetime.now().isoformat()
        ))
        
        # 更新模板铸造数量
        cursor.execute('''
            UPDATE sbt_templates
            SET minted_count = minted_count + 1
            WHERE id = ?
        ''', (template_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'message': 'SBT铸造成功'})
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

@assets_bp.route('/sbt/my-sbt', methods=['GET'])
@login_required
def get_user_sbt():
    """获取用户的SBT列表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT s.*, t.name, t.description, t.category, t.rarity
        FROM user_sbt s
        JOIN sbt_templates t ON s.template_id = t.id
        WHERE s.user_id = ?
        ORDER BY s.minted_at DESC
    ''', (request.user_id,))
    
    sbts = cursor.fetchall()
    
    result = []
    for sbt in sbts:
        result.append({
            'id': sbt[0],
            'template_id': sbt[1],
            'token_id': sbt[2],
            'attributes': json.loads(sbt[3]) if sbt[3] else {},
            'minted_at': sbt[4],
            'name': sbt[5],
            'description': sbt[6],
            'category': sbt[7],
            'rarity': sbt[8]
        })
    
    conn.close()
    return jsonify({'sbts': result})

# ==================== 资产统计 ====================

@assets_bp.route('/stats', methods=['GET'])
@login_required
def get_asset_stats():
    """获取用户资产统计"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取通证余额
    cursor.execute('''
        SELECT t.symbol, SUM(b.balance) as total
        FROM user_token_balances b
        JOIN digital_tokens t ON b.token_id = t.id
        WHERE b.user_id = ? AND b.balance > 0
        GROUP BY t.id
    ''', (request.user_id,))
    
    tokens = cursor.fetchall()
    token_balances = []
    for token in tokens:
        token_balances.append({
            'symbol': token[0],
            'balance': token[1]
        })
    
    # 获取SBT数量
    cursor.execute('''
        SELECT COUNT(*) FROM user_sbt WHERE user_id = ?
    ''', (request.user_id,))
    
    sbt_count = cursor.fetchone()[0]
    
    # 获取灵值余额
    cursor.execute('''
        SELECT spirit_tokens FROM user_balances WHERE user_id = ?
    ''', (request.user_id,))
    
    spirit_result = cursor.fetchone()
    spirit_balance = spirit_result[0] if spirit_result else 0
    
    conn.close()
    
    return jsonify({
        'token_balances': token_balances,
        'sbt_count': sbt_count,
        'spirit_balance': spirit_balance
    })
