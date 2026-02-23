#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
区块链集成服务
连接到以太坊测试网（Goerli）
"""

import os
import json
from datetime import datetime
from typing import Optional, Dict, Any

try:
    from web3 import Web3
    from web3.middleware import geth_poa_middleware
    from eth_account import Account
    HAS_WEB3 = True
except ImportError:
    HAS_WEB3 = False
    print("⚠️  web3.py未安装，区块链功能将使用模拟模式")

# 配置
GOERLI_RPC_URL = os.getenv(
    'GOERLI_RPC_URL',
    'https://goerli.infura.io/v3/YOUR_INFURA_PROJECT_ID'
)

PRIVATE_KEY = os.getenv('BLOCKCHAIN_PRIVATE_KEY', '')

# 如果没有配置，使用公共节点
PUBLIC_NODES = [
    'https://rpc.ankr.com/eth_goerli',
    'https://goerli.infura.io/v3/9aa3d95b3bc440fa88ea12eaa4456161',
]

# 智能合约ABI（示例）
NFT_CONTRACT_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "tokenId", "type": "uint256"}],
        "name": "tokenURI",
        "outputs": [{"name": "", "type": "string"}],
        "type": "function"
    },
    {
        "constant": False,
        "inputs": [
            {"name": "to", "type": "address"},
            {"name": "tokenId", "type": "uint256"}
        ],
        "name": "mint",
        "outputs": [],
        "type": "function"
    }
]


class BlockchainService:
    """区块链服务类"""

    def __init__(self):
        self.w3 = None
        self.connected = False
        self.network_name = "Goerli Testnet"
        self.chain_id = 5  # Goerli chain ID
        self.account = None

        if HAS_WEB3:
            self._connect()

    def _connect(self) -> bool:
        """连接到区块链网络"""
        try:
            # 尝试所有公共节点
            for node_url in PUBLIC_NODES:
                try:
                    self.w3 = Web3(Web3.HTTPProvider(node_url))

                    # 对于Goerli，需要添加POA中间件
                    self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

                    if self.w3.is_connected():
                        self.connected = True
                        print(f"✅ 成功连接到区块链节点: {node_url}")
                        break

                except Exception as e:
                    print(f"❌ 连接失败 {node_url}: {str(e)}")
                    continue

            if not self.connected:
                print("⚠️  所有节点连接失败，使用模拟模式")
                return False

            # 设置账户
            if PRIVATE_KEY:
                self.account = Account.from_key(PRIVATE_KEY)
                print(f"✅ 区块链账户已配置: {self.account.address}")
            else:
                print("⚠️  未配置私钥，只能进行只读操作")

            return True

        except Exception as e:
            print(f"❌ 区块链连接失败: {str(e)}")
            return False

    def get_network_status(self) -> Dict[str, Any]:
        """获取网络状态"""
        if not self.connected:
            return {
                'connected': False,
                'network': self.network_name,
                'blockNumber': 0,
                'gasPrice': 0,
                'accounts': []
            }

        try:
            block_number = self.w3.eth.block_number
            gas_price = self.w3.eth.gas_price

            accounts = []
            if self.account:
                balance = self.w3.eth.get_balance(self.account.address)
                accounts.append({
                    'address': self.account.address,
                    'balance': self.w3.from_wei(balance, 'ether')
                })

            return {
                'connected': True,
                'network': self.network_name,
                'chainId': self.chain_id,
                'blockNumber': block_number,
                'gasPrice': str(gas_price),
                'accounts': accounts
            }
        except Exception as e:
            print(f"获取网络状态失败: {str(e)}")
            return {
                'connected': False,
                'error': str(e)
            }

    def deploy_contract(self, bytecode: str, abi: list) -> Dict[str, Any]:
        """部署智能合约"""
        if not self.connected or not self.account:
            return {
                'success': False,
                'error': '未连接到区块链或未配置账户'
            }

        try:
            contract = self.w3.eth.contract(abi=abi, bytecode=bytecode)

            # 构建交易
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            transaction = contract.constructor().build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 2000000,
                'gasPrice': self.w3.eth.gas_price
            })

            # 签名交易
            signed_txn = self.w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

            # 发送交易
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return {
                'success': True,
                'contractAddress': tx_receipt.contractAddress,
                'transactionHash': tx_hash.hex(),
                'blockNumber': tx_receipt.blockNumber
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def mint_nft(self, contract_address: str, to_address: str, token_id: int, metadata_url: str) -> Dict[str, Any]:
        """铸造NFT"""
        if not self.connected or not self.account:
            return {
                'success': False,
                'error': '未连接到区块链或未配置账户'
            }

        try:
            # 创建合约实例
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=NFT_CONTRACT_ABI
            )

            # 构建交易
            nonce = self.w3.eth.get_transaction_count(self.account.address)
            transaction = contract.functions.mint(to_address, token_id).build_transaction({
                'from': self.account.address,
                'nonce': nonce,
                'gas': 300000,
                'gasPrice': self.w3.eth.gas_price
            })

            # 签名交易
            signed_txn = self.w3.eth.account.sign_transaction(transaction, PRIVATE_KEY)

            # 发送交易
            tx_hash = self.w3.eth.send_raw_transaction(signed_txn.rawTransaction)
            tx_receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

            return {
                'success': True,
                'tokenId': token_id,
                'metadataUrl': metadata_url,
                'transactionHash': tx_hash.hex(),
                'blockNumber': tx_receipt.blockNumber,
                'contractAddress': contract_address
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_token_balance(self, contract_address: str, account_address: str) -> Dict[str, Any]:
        """获取代币余额"""
        if not self.connected:
            return {
                'success': False,
                'error': '未连接到区块链'
            }

        try:
            contract = self.w3.eth.contract(
                address=contract_address,
                abi=NFT_CONTRACT_ABI
            )

            balance = contract.functions.balanceOf(account_address).call()

            return {
                'success': True,
                'balance': balance,
                'accountAddress': account_address,
                'contractAddress': contract_address
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    def get_transaction(self, tx_hash: str) -> Dict[str, Any]:
        """获取交易详情"""
        if not self.connected:
            return {
                'success': False,
                'error': '未连接到区块链'
            }

        try:
            receipt = self.w3.eth.get_transaction_receipt(tx_hash)

            return {
                'success': True,
                'transactionHash': tx_hash,
                'blockNumber': receipt.blockNumber,
                'gasUsed': receipt.gasUsed,
                'status': receipt.status
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# 全局实例
blockchain_service = BlockchainService()


def get_blockchain_service() -> BlockchainService:
    """获取区块链服务实例"""
    return blockchain_service
