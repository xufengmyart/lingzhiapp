import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowLeft, TrendingUp, Users, Wallet, ArrowDown, ArrowUp, RefreshCw, Search, Calendar } from 'lucide-react'
import api from '../services/api'

interface EconomyStats {
  totalLingzhi: number
  totalUsers: number
  activeUsers: number
  dailyReward: number
  monthlyReward: number
  dividendPool: number
  digitalAssets: number
}

interface Transaction {
  id: number
  userId: number
  userName: string
  type: string
  amount: number
  balance: number
  description: string
  createdAt: string
}

const EconomyManagement = () => {
  const navigate = useNavigate()
  const [stats, setStats] = useState<EconomyStats | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [searchTerm, setSearchTerm] = useState('')

  useEffect(() => {
    fetchEconomyData()
  }, [])

  const fetchEconomyData = async () => {
    try {
      setLoading(true)
      const [statsRes, transactionsRes] = await Promise.all([
        api.get('/admin/economy/stats'),
        api.get('/admin/economy/transactions')
      ])
      
      if (statsRes.data.success) {
        setStats(statsRes.data.data)
      }
      if (transactionsRes.data.success) {
        setTransactions(transactionsRes.data.data || [])
      }
    } catch (err) {
      setError('获取经济数据失败')
    } finally {
      setLoading(false)
    }
  }

  const filteredTransactions = transactions.filter(tx => {
    const matchesSearch = tx.userName.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         tx.description.toLowerCase().includes(searchTerm.toLowerCase())
    return matchesSearch
  })

  const getTransactionIcon = (type: string) => {
    switch (type) {
      case 'reward':
        return <ArrowDown className="w-5 h-5 text-green-600" />
      case 'consumption':
        return <ArrowUp className="w-5 h-5 text-red-600" />
      case 'transfer':
        return <RefreshCw className="w-5 h-5 text-blue-600" />
      case 'dividend':
        return <TrendingUp className="w-5 h-5 text-purple-600" />
      default:
        return <Wallet className="w-5 h-5 text-gray-600" />
    }
  }

  const getTransactionColor = (type: string) => {
    switch (type) {
      case 'reward':
        return 'text-green-600'
      case 'consumption':
        return 'text-red-600'
      case 'transfer':
        return 'text-blue-600'
      case 'dividend':
        return 'text-purple-600'
      default:
        return 'text-gray-600'
    }
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat('zh-CN').format(num)
  }

  const formatAmount = (amount: number, type: string) => {
    const isIncome = type === 'reward' || type === 'dividend'
    return `${isIncome ? '+' : '-'}${formatNumber(amount)}`
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/admin/modules')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">经济系统管理</h1>
                <p className="text-sm text-gray-600">管理灵值系统和分红池</p>
              </div>
            </div>
            <button
              onClick={fetchEconomyData}
              className="flex items-center px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
            >
              <RefreshCw className="w-4 h-4 mr-2" />
              刷新数据
            </button>
          </div>
        </div>
      </div>

      {/* 消息提示 */}
      {error && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className="bg-red-50 text-red-800 px-4 py-3 rounded-lg">
            {error}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* 统计卡片 */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">总灵值</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {formatNumber(stats.totalLingzhi)}
                  </p>
                </div>
                <div className="p-3 bg-indigo-100 rounded-lg">
                  <Wallet className="w-6 h-6 text-indigo-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">总用户数</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {formatNumber(stats.totalUsers)}
                  </p>
                </div>
                <div className="p-3 bg-green-100 rounded-lg">
                  <Users className="w-6 h-6 text-green-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">分红池</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {formatNumber(stats.dividendPool)}
                  </p>
                </div>
                <div className="p-3 bg-purple-100 rounded-lg">
                  <TrendingUp className="w-6 h-6 text-purple-600" />
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">数字资产</p>
                  <p className="text-2xl font-bold text-gray-900 mt-1">
                    {formatNumber(stats.digitalAssets)}
                  </p>
                </div>
                <div className="p-3 bg-yellow-100 rounded-lg">
                  <ArrowUp className="w-6 h-6 text-yellow-600" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 详细统计 */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">活跃用户统计</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">活跃用户</span>
                  <span className="text-lg font-bold text-green-600">
                    {formatNumber(stats.activeUsers)}
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-600 h-2 rounded-full"
                    style={{ width: `${(stats.activeUsers / stats.totalUsers) * 100}%` }}
                  ></div>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">活跃率</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {((stats.activeUsers / stats.totalUsers) * 100).toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">奖励统计</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">每日奖励</span>
                  <span className="text-lg font-bold text-blue-600">
                    {formatNumber(stats.dailyReward)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">每月奖励</span>
                  <span className="text-lg font-bold text-purple-600">
                    {formatNumber(stats.monthlyReward)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">人均月奖励</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {stats.activeUsers > 0
                      ? formatNumber(Math.floor(stats.monthlyReward / stats.activeUsers))
                      : 0}
                  </span>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg shadow-sm p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">系统概况</h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">总灵值流通</span>
                  <span className="text-lg font-bold text-indigo-600">
                    {formatNumber(stats.totalLingzhi)}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">分红池占比</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {((stats.dividendPool / stats.totalLingzhi) * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-600">人均灵值</span>
                  <span className="text-sm font-semibold text-gray-900">
                    {stats.totalUsers > 0
                      ? formatNumber(Math.floor(stats.totalLingzhi / stats.totalUsers))
                      : 0}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* 交易记录 */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="p-4 border-b border-gray-200">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900">最近交易记录</h2>
              <div className="relative">
                <Search className="w-5 h-5 text-gray-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                <input
                  type="text"
                  placeholder="搜索交易..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    用户
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    类型
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    金额
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    余额
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    描述
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    时间
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {loading ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-4 text-center text-gray-500">
                      加载中...
                    </td>
                  </tr>
                ) : filteredTransactions.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                      暂无交易记录
                    </td>
                  </tr>
                ) : (
                  filteredTransactions.slice(0, 50).map((tx) => (
                    <tr key={tx.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="flex-shrink-0 h-10 w-10 bg-indigo-100 rounded-full flex items-center justify-center">
                            <Users className="h-5 w-5 text-indigo-600" />
                          </div>
                          <div className="ml-4">
                            <div className="text-sm font-medium text-gray-900">
                              {tx.userName}
                            </div>
                            <div className="text-xs text-gray-500">
                              ID: {tx.userId}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          {getTransactionIcon(tx.type)}
                          <span className="ml-2 text-sm text-gray-900 capitalize">
                            {tx.type}
                          </span>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`text-sm font-semibold ${getTransactionColor(tx.type)}`}>
                          {formatAmount(tx.amount, tx.type)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm font-medium text-gray-900">
                          {formatNumber(tx.balance)}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className="text-sm text-gray-900">
                          {tx.description}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center text-sm text-gray-500">
                          <Calendar className="w-4 h-4 mr-1" />
                          {new Date(tx.createdAt).toLocaleString('zh-CN')}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EconomyManagement
