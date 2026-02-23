"""
区块链集成路由
提供区块链网络连接、智能合约部署、NFT铸造等功能
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import os

try:
    from blockchain_service import get_blockchain_service
    HAS_BLOCKCHAIN = True
except ImportError:
    HAS_BLOCKCHAIN = False

blockchain_bp = Blueprint('blockchain', __name__)


# ============ 获取网络状态 ============

@blockchain_bp.route('/v9/blockchain/network-status', methods=['GET'])
def get_network_status():
    """获取区块链网络状态"""
    try:
        if not HAS_BLOCKCHAIN:
            return jsonify({
                'success': False,
                'message': '区块链服务未安装',
                'data': {
                    'connected': False,
                    'network': 'Not Available',
                    'mode': 'simulation'
                }
            }), 500

        service = get_blockchain_service()
        status = service.get_network_status()

        return jsonify({
            'success': status['connected'],
            'message': '网络状态获取成功' if status['connected'] else '网络未连接',
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取网络状态失败: {str(e)}',
            'data': None
        }), 500


# ============ 部署智能合约 ============

@blockchain_bp.route('/v9/blockchain/deploy-contract', methods=['POST'])
def deploy_contract():
    """部署智能合约"""
    try:
        if not HAS_BLOCKCHAIN:
            return jsonify({
                'success': False,
                'message': '区块链服务未安装'
            }), 500

        data = request.get_json()
        bytecode = data.get('bytecode', '')
        abi = data.get('abi', [])

        if not bytecode:
            return jsonify({
                'success': False,
                'message': '合约字节码不能为空'
            }), 400

        service = get_blockchain_service()
        result = service.deploy_contract(bytecode, abi)

        return jsonify({
            'success': result['success'],
            'message': '合约部署成功' if result['success'] else '合约部署失败',
            'data': result if result['success'] else None,
            'error': result.get('error')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'部署合约失败: {str(e)}'
        }), 500


# ============ 铸造NFT ============

@blockchain_bp.route('/v9/blockchain/mint-nft', methods=['POST'])
def mint_nft():
    """铸造NFT"""
    try:
        if not HAS_BLOCKCHAIN:
            return jsonify({
                'success': False,
                'message': '区块链服务未安装'
            }), 500

        data = request.get_json()
        contract_address = data.get('contractAddress')
        to_address = data.get('toAddress')
        token_id = data.get('tokenId')
        metadata_url = data.get('metadataUrl')

        if not all([contract_address, to_address, token_id]):
            return jsonify({
                'success': False,
                'message': '缺少必要参数'
            }), 400

        service = get_blockchain_service()
        result = service.mint_nft(contract_address, to_address, token_id, metadata_url)

        return jsonify({
            'success': result['success'],
            'message': 'NFT铸造成功' if result['success'] else 'NFT铸造失败',
            'data': result if result['success'] else None,
            'error': result.get('error')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'铸造NFT失败: {str(e)}'
        }), 500


# ============ 获取余额 ============

@blockchain_bp.route('/v9/blockchain/balance/<address>', methods=['GET'])
def get_balance(address):
    """获取代币余额"""
    try:
        if not HAS_BLOCKCHAIN:
            return jsonify({
                'success': False,
                'message': '区块链服务未安装'
            }), 500

        contract_address = request.args.get('contractAddress')

        if not contract_address:
            return jsonify({
                'success': False,
                'message': '缺少合约地址参数'
            }), 400

        service = get_blockchain_service()
        result = service.get_token_balance(contract_address, address)

        return jsonify({
            'success': result['success'],
            'message': '获取余额成功' if result['success'] else '获取余额失败',
            'data': result if result['success'] else None,
            'error': result.get('error')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取余额失败: {str(e)}'
        }), 500


# ============ 获取交易详情 ============

@blockchain_bp.route('/v9/blockchain/transaction/<tx_hash>', methods=['GET'])
def get_transaction(tx_hash):
    """获取交易详情"""
    try:
        if not HAS_BLOCKCHAIN:
            return jsonify({
                'success': False,
                'message': '区块链服务未安装'
            }), 500

        service = get_blockchain_service()
        result = service.get_transaction(tx_hash)

        return jsonify({
            'success': result['success'],
            'message': '获取交易成功' if result['success'] else '获取交易失败',
            'data': result if result['success'] else None,
            'error': result.get('error')
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取交易失败: {str(e)}'
        }), 500


# ============ 健康检查 ============

@blockchain_bp.route('/v9/blockchain/health', methods=['GET'])
def health_check():
    """健康检查"""
    try:
        status = {
            'service': 'running',
            'hasWeb3': HAS_BLOCKCHAIN,
            'timestamp': datetime.now().isoformat()
        }

        if HAS_BLOCKCHAIN:
            service = get_blockchain_service()
            network_status = service.get_network_status()
            status['connected'] = network_status.get('connected', False)
            status['network'] = network_status.get('network', 'Unknown')
            status['mode'] = 'production' if network_status.get('connected') else 'simulation'
        else:
            status['connected'] = False
            status['network'] = 'Not Available'
            status['mode'] = 'simulation'

        return jsonify({
            'success': True,
            'message': '区块链服务运行正常',
            'data': status
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'健康检查失败: {str(e)}'
        }), 500
