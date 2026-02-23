"""
项目详情API - 支持项目具体化详情和数据资产工作流
SQLite兼容版本
"""

from flask import Blueprint, jsonify, request
from database import get_db

project_details_bp = Blueprint('project_details', __name__)

# ============ 辅助函数 ============

def fetch_all_as_dict(cursor):
    """将cursor结果转换为字典列表"""
    if not cursor.description:
        return []
    columns = [column[0] for column in cursor.description]
    results = []
    for row in cursor.fetchall():
        results.append(dict(zip(columns, row)))
    return results

def fetch_one_as_dict(cursor):
    """将cursor结果转换为单个字典"""
    if not cursor.description:
        return None
    columns = [column[0] for column in cursor.description]
    row = cursor.fetchone()
    if row:
        return dict(zip(columns, row))
    return None

# ============ 项目详情（完整版） ============

@project_details_bp.route('/v9/projects/<int:project_id>/details', methods=['GET'])
def get_project_details(project_id):
    """
    获取项目完整详情，包含：
    - 基本信息
    - 数据化要素
    - 资源对应关系
    - 数据资产信息
    - 确权记录
    - 通证化状态
    - 交易记录
    - 收入统计
    """
    try:
        conn = get_db()
        cursor = conn.cursor()

        # 1. 获取项目基本信息
        cursor.execute("""
            SELECT 
                id, name, description, category, status, 
                budget, progress, priority, 
                start_date as startDate, end_date as endDate,
                NULL as userId, NULL as userName,
                created_at as createdAt, updated_at as updatedAt
            FROM company_projects
            WHERE id = ?
        """, (project_id,))
        project = fetch_one_as_dict(cursor)

        if not project:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': '项目不存在',
                'data': None
            }), 404

        # 2. 获取数据化要素
        cursor.execute("""
            SELECT 
                id, project_id as projectId,
                element_name as elementName, element_type as elementType,
                description, data_source as dataSource,
                processing_method as processingMethod,
                status, created_at as createdAt
            FROM data_elements
            WHERE project_id = ?
            ORDER BY created_at DESC
        """, (project_id,))
        dataElements = fetch_all_as_dict(cursor)

        # 3. 获取资源对应关系
        cursor.execute("""
            SELECT 
                id, project_id as projectId,
                element_id as elementId,
                resource_name as resourceName, resource_type as resourceType,
                resource_url as resourceUrl, file_size as fileSize,
                metadata, status, created_at as createdAt
            FROM data_resources
            WHERE project_id = ?
            ORDER BY created_at DESC
        """, (project_id,))
        resources = fetch_all_as_dict(cursor)

        # 4. 获取数据资产信息
        cursor.execute("""
            SELECT 
                id, project_id as projectId,
                asset_name as assetName, asset_type as assetType,
                data_value as dataValue, estimated_value as estimatedValue,
                token_address as tokenAddress, token_symbol as tokenSymbol,
                total_supply as totalSupply, circulating_supply as circulatingSupply,
                current_price as currentPrice, market_cap as marketCap,
                status, created_at as createdAt, updated_at as updatedAt
            FROM data_assets
            WHERE project_id = ?
        """, (project_id,))
        dataAssets = fetch_all_as_dict(cursor)

        # 5. 获取确权记录
        cursor.execute("""
            SELECT 
                id, project_id as projectId,
                asset_id as assetId,
                rights_type as rightsType, rights_holder as rightsHolder,
                rights_value as rightsValue, certificate_no as certificateNo,
                certificate_url as certificateUrl, expiry_date as expiryDate,
                status, created_at as createdAt
            FROM asset_rights
            WHERE project_id = ?
            ORDER BY created_at DESC
        """, (project_id,))
        rightsRecords = fetch_all_as_dict(cursor)

        # 6. 获取通证化记录
        cursor.execute("""
            SELECT 
                id, project_id as projectId,
                asset_id as assetId,
                token_address as tokenAddress, token_symbol as tokenSymbol,
                total_supply as totalSupply, decimals,
                mint_date as mintDate, mint_tx as mintTx,
                contract_type as contractType, status, created_at as createdAt
            FROM asset_tokens
            WHERE project_id = ?
            ORDER BY created_at DESC
        """, (project_id,))
        tokenRecords = fetch_all_as_dict(cursor)

        # 7. 获取交易记录
        cursor.execute("""
            SELECT 
                id, project_id as projectId,
                asset_id as assetId, token_address as tokenAddress,
                transaction_type as transactionType,
                from_address as fromAddress, to_address as toAddress,
                amount, price, total_value as totalValue,
                tx_hash as txHash, block_number as blockNumber,
                created_at as createdAt
            FROM asset_transactions
            WHERE project_id = ?
            ORDER BY created_at DESC
            LIMIT 50
        """, (project_id,))
        transactions = fetch_all_as_dict(cursor)

        # 8. 获取收入统计
        cursor.execute("""
            SELECT 
                project_id as projectId,
                total_revenue as totalRevenue,
                total_transactions as totalTransactions,
                avg_transaction_value as avgTransactionValue,
                last_transaction_date as lastTransactionDate,
                period, updated_at as updatedAt
            FROM project_revenue
            WHERE project_id = ?
            ORDER BY updated_at DESC
            LIMIT 1
        """, (project_id,))
        revenue = fetch_one_as_dict(cursor)

        cursor.close()
        conn.close()

        # 组装完整的项目详情
        projectDetails = {
            'basicInfo': project,
            'dataElements': dataElements or [],
            'resources': resources or [],
            'dataAssets': dataAssets or [],
            'rightsRecords': rightsRecords or [],
            'tokenRecords': tokenRecords or [],
            'transactions': transactions or [],
            'revenue': revenue or None
        }

        return jsonify({
            'success': True,
            'message': '获取项目详情成功',
            'data': projectDetails
        })

    except Exception as e:
        print(f"获取项目详情失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取项目详情失败: {str(e)}',
            'data': None
        }), 500


# ============ 数据化要素管理 ============

@project_details_bp.route('/v9/projects/<int:project_id>/elements', methods=['GET', 'POST'])
def manage_data_elements(project_id):
    """管理数据化要素（列表/创建）"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        if request.method == 'GET':
            # 获取数据化要素列表
            cursor.execute("""
                SELECT 
                    id, project_id as projectId,
                    element_name as elementName, element_type as elementType,
                    description, data_source as dataSource,
                    processing_method as processingMethod,
                    status, created_at as createdAt
                FROM data_elements
                WHERE project_id = ?
                ORDER BY created_at DESC
            """, (project_id,))
            elements = fetch_all_as_dict(cursor)
            cursor.close()
            conn.close()

            return jsonify({
                'success': True,
                'message': '获取数据化要素成功',
                'data': elements
            })

        elif request.method == 'POST':
            # 创建新的数据化要素
            data = request.json
            element_name = data.get('elementName')
            element_type = data.get('elementType')
            description = data.get('description', '')
            data_source = data.get('dataSource', '')
            processing_method = data.get('processingMethod', '')
            status = data.get('status', 'pending')

            if not element_name or not element_type:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '要素名称和类型不能为空',
                    'data': None
                }), 400

            cursor.execute("""
                INSERT INTO data_elements 
                (project_id, element_name, element_type, description, data_source, processing_method, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (project_id, element_name, element_type, description, data_source, processing_method, status))

            conn.commit()
            element_id = cursor.lastrowid
            cursor.close()
            conn.close()

            return jsonify({
                'success': True,
                'message': '创建数据化要素成功',
                'data': {'id': element_id, 'elementName': element_name}
            })

    except Exception as e:
        print(f"管理数据化要素失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'管理数据化要素失败: {str(e)}',
            'data': None
        }), 500


# ============ 资源管理 ============

@project_details_bp.route('/v9/projects/<int:project_id>/resources', methods=['GET', 'POST'])
def manage_resources(project_id):
    """管理资源（列表/创建）"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        if request.method == 'GET':
            cursor.execute("""
                SELECT 
                    id, project_id as projectId,
                    element_id as elementId,
                    resource_name as resourceName, resource_type as resourceType,
                    resource_url as resourceUrl, file_size as fileSize,
                    metadata, status, created_at as createdAt
                FROM data_resources
                WHERE project_id = ?
                ORDER BY created_at DESC
            """, (project_id,))
            resources = fetch_all_as_dict(cursor)
            cursor.close()
            conn.close()

            return jsonify({
                'success': True,
                'message': '获取资源列表成功',
                'data': resources
            })

        elif request.method == 'POST':
            data = request.json
            element_id = data.get('elementId')
            resource_name = data.get('resourceName')
            resource_type = data.get('resourceType')
            resource_url = data.get('resourceUrl', '')
            file_size = data.get('fileSize', 0)
            metadata = data.get('metadata', {})
            status = data.get('status', 'pending')

            if not element_id or not resource_name or not resource_type:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '关联要素、资源名称和类型不能为空',
                    'data': None
                }), 400

            cursor.execute("""
                INSERT INTO data_resources
                (project_id, element_id, resource_name, resource_type, resource_url, file_size, metadata, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, element_id, resource_name, resource_type, resource_url, file_size, 
                  str(metadata), status))

            conn.commit()
            resource_id = cursor.lastrowid
            cursor.close()
            conn.close()

            return jsonify({
                'success': True,
                'message': '创建资源成功',
                'data': {'id': resource_id, 'resourceName': resource_name}
            })

    except Exception as e:
        print(f"管理资源失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'管理资源失败: {str(e)}',
            'data': None
        }), 500


# ============ 数据资产确权 ============

@project_details_bp.route('/v9/projects/<int:project_id>/assets/<int:asset_id>/rights', methods=['POST'])
def create_asset_rights(project_id, asset_id):
    """创建数据资产确权"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        data = request.json
        rights_type = data.get('rightsType')
        rights_holder = data.get('rightsHolder')
        rights_value = data.get('rightsValue', 0)
        expiry_date = data.get('expiryDate')
        status = data.get('status', 'active')

        if not rights_type or not rights_holder:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': '权利类型和权利人不能为空',
                'data': None
            }), 400

        # 生成证书编号
        from datetime import datetime
        certificate_no = f"CERT-{project_id}-{asset_id}-{int(datetime.now().timestamp())}"

        cursor.execute("""
            INSERT INTO asset_rights
            (project_id, asset_id, rights_type, rights_holder, rights_value, certificate_no, expiry_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, asset_id, rights_type, rights_holder, rights_value, certificate_no, 
              expiry_date, status))

        conn.commit()
        rights_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': '确权成功',
            'data': {'id': rights_id, 'certificateNo': certificate_no}
        })

    except Exception as e:
        print(f"创建确权失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'创建确权失败: {str(e)}',
            'data': None
        }), 500


# ============ 通证化 ============

@project_details_bp.route('/v9/projects/<int:project_id>/assets/<int:asset_id>/tokenize', methods=['POST'])
def tokenize_asset(project_id, asset_id):
    """将数据资产通证化"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        data = request.json
        token_symbol = data.get('tokenSymbol')
        total_supply = data.get('totalSupply', 1000000)
        decimals = data.get('decimals', 18)
        contract_type = data.get('contractType', 'ERC721')

        if not token_symbol:
            cursor.close()
            conn.close()
            return jsonify({
                'success': False,
                'message': '通证符号不能为空',
                'data': None
            }), 400

        # 模拟通证地址生成
        from datetime import datetime
        token_address = f"0x{''.join([format(ord(c), '02x') for c in token_symbol + str(int(datetime.now().timestamp()))])}"

        cursor.execute("""
            INSERT INTO asset_tokens
            (project_id, asset_id, token_address, token_symbol, total_supply, decimals, contract_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (project_id, asset_id, token_address, token_symbol, total_supply, decimals, contract_type, 'minted'))

        conn.commit()
        token_id = cursor.lastrowid

        # 更新数据资产的通证信息
        cursor.execute("""
            UPDATE data_assets
            SET token_address = ?, token_symbol = ?, status = 'tokenized'
            WHERE id = ? AND project_id = ?
        """, (token_address, token_symbol, asset_id, project_id))
        
        conn.commit()
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': '通证化成功',
            'data': {
                'id': token_id,
                'tokenAddress': token_address,
                'tokenSymbol': token_symbol,
                'totalSupply': total_supply
            }
        })

    except Exception as e:
        print(f"通证化失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'通证化失败: {str(e)}',
            'data': None
        }), 500


# ============ 交易记录 ============

@project_details_bp.route('/v9/projects/<int:project_id>/transactions', methods=['GET', 'POST'])
def manage_transactions(project_id):
    """管理交易记录（列表/创建）"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        if request.method == 'GET':
            cursor.execute("""
                SELECT 
                    id, project_id as projectId,
                    asset_id as assetId, token_address as tokenAddress,
                    transaction_type as transactionType,
                    from_address as fromAddress, to_address as toAddress,
                    amount, price, total_value as totalValue,
                    tx_hash as txHash, block_number as blockNumber,
                    created_at as createdAt
                FROM asset_transactions
                WHERE project_id = ?
                ORDER BY created_at DESC
                LIMIT 100
            """, (project_id,))
            transactions = fetch_all_as_dict(cursor)
            cursor.close()
            conn.close()

            return jsonify({
                'success': True,
                'message': '获取交易记录成功',
                'data': transactions
            })

        elif request.method == 'POST':
            data = request.json
            asset_id = data.get('assetId')
            token_address = data.get('tokenAddress')
            transaction_type = data.get('transactionType')
            from_address = data.get('fromAddress')
            to_address = data.get('toAddress')
            amount = data.get('amount', 0)
            price = data.get('price', 0)
            total_value = amount * price
            tx_hash = data.get('txHash', '')

            if not asset_id or not transaction_type or not to_address:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': False,
                    'message': '资产ID、交易类型和接收地址不能为空',
                    'data': None
                }), 400

            cursor.execute("""
                INSERT INTO asset_transactions
                (project_id, asset_id, token_address, transaction_type, from_address, to_address, 
                 amount, price, total_value, tx_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (project_id, asset_id, token_address, transaction_type, from_address, to_address,
                  amount, price, total_value, tx_hash))

            conn.commit()
            tx_id = cursor.lastrowid

            # 更新项目收入统计
            if transaction_type == 'sell':
                cursor.execute("""
                    INSERT INTO project_revenue 
                    (project_id, total_revenue, total_transactions, avg_transaction_value)
                    VALUES (?, ?, 1, ?)
                """, (project_id, total_value, total_value))
                
                conn.commit()
            
            cursor.close()
            conn.close()

            return jsonify({
                'success': True,
                'message': '交易记录创建成功',
                'data': {'id': tx_id, 'totalValue': total_value}
            })

    except Exception as e:
        print(f"管理交易记录失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'管理交易记录失败: {str(e)}',
            'data': None
        }), 500


# ============ 项目收入统计 ============

@project_details_bp.route('/v9/projects/<int:project_id>/revenue', methods=['GET'])
def get_project_revenue(project_id):
    """获取项目收入统计"""
    try:
        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                project_id as projectId,
                total_revenue as totalRevenue,
                total_transactions as totalTransactions,
                avg_transaction_value as avgTransactionValue,
                last_transaction_date as lastTransactionDate,
                period, updated_at as updatedAt
            FROM project_revenue
            WHERE project_id = ?
            ORDER BY updated_at DESC
        """, (project_id,))
        revenue = fetch_all_as_dict(cursor)
        
        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'message': '获取收入统计成功',
            'data': revenue or []
        })

    except Exception as e:
        print(f"获取收入统计失败: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'获取收入统计失败: {str(e)}',
            'data': []
        }), 500
