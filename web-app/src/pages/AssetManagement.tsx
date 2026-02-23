import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

interface TokenBalance {
  token_type_id: number;
  token_name: string;
  token_symbol: string;
  balance: number;
  frozen_balance: number;
}

interface Transaction {
  id: number;
  from_user_id: number | null;
  to_user_id: number;
  token_type_id: number;
  amount: number;
  transaction_type: 'issue' | 'transfer' | 'reward' | 'stake';
  description: string;
  created_at: string;
}

interface SBT {
  id: number;
  sbt_type_id: number;
  sbt_name: string;
  category: 'achievement' | 'badge' | 'identity' | 'certification';
  rarity: 'common' | 'rare' | 'epic' | 'legendary';
  metadata: any;
  issued_at: string;
}

const AssetManagement: React.FC = () => {
  const [tokens, setTokens] = useState<TokenBalance[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [sbts, setSbts] = useState<SBT[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'tokens' | 'transactions' | 'sbts'>('tokens');
  const [showTransferModal, setShowTransferModal] = useState(false);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      fetchData(storedToken);
    }
  }, []);

  const fetchData = async (authToken: string) => {
    try {
      const [tokensRes, sbtsRes] = await Promise.all([
        fetch('/api/user/tokens', {
          headers: { 'Authorization': `Bearer ${authToken}` },
        }),
        fetch('/api/user/sbts', {
          headers: { 'Authorization': `Bearer ${authToken}` },
        }),
      ]);

      const tokensData = await tokensRes.json();
      const sbtsData = await sbtsRes.json();

      if (tokensData.success) {
        setTokens(tokensData.data);
      }

      if (sbtsData.success) {
        setSbts(sbtsData.data);
      }

      setLoading(false);
    } catch (error) {
      console.error('获取资产数据失败:', error);
      setLoading(false);
    }
  };

  const fetchTransactions = async () => {
    try {
      const response = await fetch('/api/tokens/transactions?page=1&limit=20', {
        headers: { 'Authorization': `Bearer ${token}` },
      });
      const data = await response.json();
      if (data.success) {
        setTransactions(data.data.transactions);
      }
    } catch (error) {
      console.error('获取交易记录失败:', error);
    }
  };

  const getRarityColor = (rarity: string) => {
    switch (rarity) {
      case 'common': return 'bg-gray-100 text-gray-800';
      case 'rare': return 'bg-blue-100 text-blue-800';
      case 'epic': return 'bg-purple-100 text-purple-800';
      case 'legendary': return 'bg-yellow-100 text-yellow-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getRarityText = (rarity: string) => {
    switch (rarity) {
      case 'common': return '普通';
      case 'rare': return '稀有';
      case 'epic': return '史诗';
      case 'legendary': return '传说';
      default: return '未知';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'achievement': return '🏆';
      case 'badge': return '🎖️';
      case 'identity': return '👤';
      case 'certification': return '🎓';
      default: return '📜';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-gray-50 min-h-screen">
      {/* 头部 */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">资产管理</h1>
        <p className="text-gray-600">管理您的数字资产和徽章</p>
      </div>

      {/* 总资产概览 */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg p-6 mb-8 text-white">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div>
            <div className="text-sm opacity-80 mb-1">总资产价值</div>
            <div className="text-3xl font-bold">¥{(tokens.reduce((sum, t) => sum + t.balance, 0) * 1).toLocaleString()}</div>
          </div>
          <div>
            <div className="text-sm opacity-80 mb-1">可用余额</div>
            <div className="text-3xl font-bold">{tokens.reduce((sum, t) => sum + t.balance, 0).toLocaleString()}</div>
          </div>
          <div>
            <div className="text-sm opacity-80 mb-1">冻结余额</div>
            <div className="text-3xl font-bold">{tokens.reduce((sum, t) => sum + t.frozen_balance, 0).toLocaleString()}</div>
          </div>
        </div>
      </div>

      {/* 标签切换 */}
      <div className="bg-white rounded-xl shadow-sm mb-6">
        <div className="flex">
          <button
            onClick={() => setActiveTab('tokens')}
            className={`flex-1 py-4 text-center font-medium transition-colors ${
              activeTab === 'tokens'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            通证
          </button>
          <button
            onClick={() => {
              setActiveTab('transactions');
              fetchTransactions();
            }}
            className={`flex-1 py-4 text-center font-medium transition-colors ${
              activeTab === 'transactions'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            交易记录
          </button>
          <button
            onClick={() => setActiveTab('sbts')}
            className={`flex-1 py-4 text-center font-medium transition-colors ${
              activeTab === 'sbts'
                ? 'text-blue-600 border-b-2 border-blue-600'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            徽章
          </button>
        </div>
      </div>

      {/* 通证列表 */}
      {activeTab === 'tokens' && (
        <div className="space-y-4">
          {tokens.map((token, index) => (
            <motion.div
              key={token.token_type_id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6"
            >
              <div className="flex justify-between items-center">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full flex items-center justify-center text-white font-bold">
                    {token.token_symbol[0]}
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{token.token_name}</h3>
                    <p className="text-sm text-gray-500">{token.token_symbol}</p>
                  </div>
                </div>
                <div className="text-right">
                  <div className="text-2xl font-bold text-gray-900">{token.balance.toLocaleString()}</div>
                  <div className="text-sm text-gray-500">可用</div>
                </div>
              </div>

              {token.frozen_balance > 0 && (
                <div className="mt-4 pt-4 border-t">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-600">冻结余额</span>
                    <span className="font-semibold text-orange-600">{token.frozen_balance.toLocaleString()}</span>
                  </div>
                </div>
              )}

              <div className="mt-4 flex gap-3">
                <button className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                  转账
                </button>
                <button className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                  充值
                </button>
              </div>
            </motion.div>
          ))}
        </div>
      )}

      {/* 交易记录 */}
      {activeTab === 'transactions' && (
        <div className="bg-white rounded-xl shadow-sm overflow-hidden">
          {transactions.length > 0 ? (
            <div className="divide-y">
              {transactions.map((transaction, index) => (
                <motion.div
                  key={transaction.id}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="p-6 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className={`font-semibold ${transaction.to_user_id === parseInt(localStorage.getItem('userId') || '0') ? 'text-green-600' : 'text-red-600'}`}>
                        {transaction.to_user_id === parseInt(localStorage.getItem('userId') || '0') ? '+' : '-'}
                        {transaction.amount}
                      </div>
                      <div className="text-sm text-gray-500">{transaction.description}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-medium text-gray-900">
                        {transaction.transaction_type === 'transfer' ? '转账' :
                         transaction.transaction_type === 'reward' ? '奖励' :
                         transaction.transaction_type === 'issue' ? '发行' : '质押'}
                      </div>
                      <div className="text-xs text-gray-500">
                        {new Date(transaction.created_at).toLocaleString('zh-CN')}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
              <p className="text-gray-600">暂无交易记录</p>
            </div>
          )}
        </div>
      )}

      {/* SBT 徽章 */}
      {activeTab === 'sbts' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {sbts.map((sbt, index) => (
            <motion.div
              key={sbt.id}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.1 }}
              className="bg-white rounded-xl shadow-sm hover:shadow-md transition-shadow p-6"
            >
              <div className="text-center">
                <div className="text-6xl mb-4">{getCategoryIcon(sbt.category)}</div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">{sbt.sbt_name}</h3>
                <div className="space-y-2">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${getRarityColor(sbt.rarity)}`}>
                    {getRarityText(sbt.rarity)}
                  </span>
                </div>
                <div className="mt-4 text-sm text-gray-500">
                  获得时间：{new Date(sbt.issued_at).toLocaleDateString('zh-CN')}
                </div>
              </div>
            </motion.div>
          ))}

          {sbts.length === 0 && (
            <div className="col-span-full text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                </svg>
              </div>
              <p className="text-gray-600">暂无徽章</p>
              <p className="text-sm text-gray-500 mt-2">完成成就即可获得徽章</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AssetManagement;
