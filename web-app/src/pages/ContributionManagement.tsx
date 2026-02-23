import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  TrendingUp,
  TrendingDown,
  Users,
  Award,
  Settings,
  Plus,
  Edit2,
  Trash2,
  Search,
  Filter,
  Download,
  ArrowUp,
  ArrowDown,
  CheckCircle,
  XCircle,
  BarChart3,
  PieChart,
  Activity,
  ArrowLeft
} from 'lucide-react'

interface ContributionRule {
  id: number
  rule_type: string
  rule_name: string
  rule_code: string
  description: string
  target_role: string
  contribution_value: number
  lingzhi_value: number
  max_daily_times: number | null
  max_total_times: number | null
  status: string
  priority: number
  created_at: string
}

interface Transaction {
  id: number
  user_id: number
  username?: string
  real_name?: string
  rule_code: string
  rule_name: string
  transaction_type: string
  contribution_change: number
  balance_before: number
  balance_after: number
  lingzhi_change: number
  description: string
  status: string
  created_at: string
}

interface ContributionStats {
  total_earned: number
  total_consumed: number
  total_balance: number
  total_transactions: number
  active_users: number
  today_earned: number
  today_consumed: number
}

interface LeaderboardUser {
  id: number
  username: string
  real_name?: string
  total_contribution: number
  cumulative_contribution: number
  total_lingzhi: number
}

const ContributionManagement = () => {
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState<'overview' | 'rules' | 'transactions' | 'adjust'>('overview')
  const [loading, setLoading] = useState(true)
  const [stats, setStats] = useState<ContributionStats | null>(null)
  const [rules, setRules] = useState<ContributionRule[]>([])
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [leaderboard, setLeaderboard] = useState<LeaderboardUser[]>([])
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  // 规则筛选
  const [ruleFilter, setRuleFilter] = useState({
    rule_type: '',
    target_role: '',
    status: ''
  })

  // 交易筛选
  const [transactionFilter, setTransactionFilter] = useState({
    user_id: '',
    transaction_type: '',
    rule_code: '',
    start_date: '',
    end_date: ''
  })

  // 分页
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)

  useEffect(() => {
    loadStats()
  }, [])

  useEffect(() => {
    if (activeTab === 'overview') {
      loadStats()
    } else if (activeTab === 'rules') {
      loadRules()
    } else if (activeTab === 'transactions') {
      loadTransactions()
    }
  }, [activeTab, currentPage])

  const loadStats = async () => {
    try {
      const token = localStorage.getItem('token')
      const response = await fetch(`${import.meta.env.VITE_API_URL}/admin/contribution/stats`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })

      if (!response.ok) throw new Error('获取统计失败')

      const result = await response.json()
      setStats(result.stats)
      setLeaderboard(result.leaderboard)
    } catch (error) {
      console.error('加载统计失败:', error)
      setMessage({ type: 'error', text: '加载统计失败' })
    } finally {
      setLoading(false)
    }
  }

  const loadRules = async () => {
    try {
      const token = localStorage.getItem('token')
      const params = new URLSearchParams({
        ...ruleFilter,
        page: currentPage.toString(),
        page_size: '20'
      })

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/admin/contribution/rules?${params}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      )

      if (!response.ok) throw new Error('获取规则失败')

      const result = await response.json()
      setRules(result.rules)
      setTotalPages(Math.ceil(result.total / 20))
    } catch (error) {
      console.error('加载规则失败:', error)
      setMessage({ type: 'error', text: '加载规则失败' })
    }
  }

  const loadTransactions = async () => {
    try {
      const token = localStorage.getItem('token')
      const params = new URLSearchParams({
        ...transactionFilter,
        page: currentPage.toString(),
        page_size: '20'
      })

      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/admin/contribution/transactions?${params}`,
        { headers: { 'Authorization': `Bearer ${token}` } }
      )

      if (!response.ok) throw new Error('获取交易记录失败')

      const result = await response.json()
      setTransactions(result.transactions)
      setTotalPages(Math.ceil(result.total / 20))
    } catch (error) {
      console.error('加载交易记录失败:', error)
      setMessage({ type: 'error', text: '加载交易记录失败' })
    }
  }

  const handleDeleteRule = async (ruleId: number) => {
    if (!window.confirm('确定要删除这个规则吗？')) return

    try {
      const token = localStorage.getItem('token')
      const response = await fetch(
        `${import.meta.env.VITE_API_URL}/admin/contribution/rules/${ruleId}`,
        {
          method: 'DELETE',
          headers: { 'Authorization': `Bearer ${token}` }
        }
      )

      if (!response.ok) throw new Error('删除失败')

      setMessage({ type: 'success', text: '规则删除成功' })
      loadRules()
    } catch (error) {
      console.error('删除规则失败:', error)
      setMessage({ type: 'error', text: '删除规则失败' })
    }
  }

  const StatCard = ({ title, value, icon: Icon, change, changeType }: any) => (
    <div className="bg-white rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600 mb-1">{title}</p>
          <p className="text-2xl font-bold text-gray-900">{value.toLocaleString()}</p>
          {change && (
            <p className={`text-sm mt-1 ${changeType === 'positive' ? 'text-green-600' : 'text-red-600'}`}>
              {changeType === 'positive' ? <ArrowUp className="w-4 h-4 inline" /> : <ArrowDown className="w-4 h-4 inline" />}
              {change}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${
          changeType === 'positive' ? 'bg-green-100 text-green-600' : 'bg-blue-100 text-blue-600'
        }`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  )

  if (loading && !stats) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* 顶部导航 */}
      <div className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate('/admin')}
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600" />
              </button>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">贡献值管理</h1>
                <p className="text-sm text-gray-600 mt-1">管理贡献值规则、交易记录和统计</p>
              </div>
            </div>
            {activeTab === 'adjust' && (
              <button
                onClick={() => navigate('/admin/users')}
                className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                返回用户管理
              </button>
            )}
          </div>
        </div>
      </div>

      {/* 消息提示 */}
      {message && (
        <div className="max-w-7xl mx-auto px-4 mt-4">
          <div className={`p-4 rounded-lg flex items-center ${
            message.type === 'success' ? 'bg-green-50 text-green-800' : 'bg-red-50 text-red-800'
          }`}>
            {message.type === 'success' ? <CheckCircle className="w-5 h-5 mr-2" /> : <XCircle className="w-5 h-5 mr-2" />}
            {message.text}
          </div>
        </div>
      )}

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* 标签导航 */}
        <div className="bg-white rounded-lg shadow-sm mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'overview'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <BarChart3 className="w-4 h-4 inline mr-2" />
                概览统计
              </button>
              <button
                onClick={() => setActiveTab('rules')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'rules'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Settings className="w-4 h-4 inline mr-2" />
                规则管理
              </button>
              <button
                onClick={() => setActiveTab('transactions')}
                className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors ${
                  activeTab === 'transactions'
                    ? 'border-indigo-500 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                <Activity className="w-4 h-4 inline mr-2" />
                交易记录
              </button>
            </nav>
          </div>
        </div>

        {/* 概览统计 */}
        {activeTab === 'overview' && stats && (
          <div className="space-y-6">
            {/* 统计卡片 */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <StatCard
                title="总发放贡献值"
                value={stats.total_earned}
                icon={TrendingUp}
                changeType="positive"
              />
              <StatCard
                title="总消耗贡献值"
                value={stats.total_consumed}
                icon={TrendingDown}
                changeType="negative"
              />
              <StatCard
                title="当前流通余额"
                value={stats.total_balance}
                icon={Award}
                changeType="positive"
              />
              <StatCard
                title="活跃用户数（30天）"
                value={stats.active_users}
                icon={Users}
                changeType="positive"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <StatCard
                title="今日发放"
                value={stats.today_earned}
                icon={TrendingUp}
                changeType="positive"
              />
              <StatCard
                title="今日消耗"
                value={stats.today_consumed}
                icon={TrendingDown}
                changeType="negative"
              />
            </div>

            {/* 贡献值排行榜 */}
            <div className="bg-white rounded-lg shadow-sm p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">贡献值排行榜 TOP 10</h2>
              <div className="space-y-4">
                {leaderboard.map((user, index) => (
                  <div key={user.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                        index === 0 ? 'bg-yellow-400 text-white' :
                        index === 1 ? 'bg-gray-400 text-white' :
                        index === 2 ? 'bg-orange-400 text-white' :
                        'bg-gray-200 text-gray-700'
                      }`}>
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{user.real_name || user.username}</p>
                        <p className="text-sm text-gray-600">ID: {user.id}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="font-bold text-indigo-600">{user.total_contribution.toLocaleString()}</p>
                      <p className="text-sm text-gray-600">贡献值</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* 规则管理 */}
        {activeTab === 'rules' && (
          <div className="space-y-6">
            {/* 筛选工具栏 */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="flex items-center space-x-4">
                <select
                  value={ruleFilter.rule_type}
                  onChange={(e) => setRuleFilter({ ...ruleFilter, rule_type: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">全部类型</option>
                  <option value="earn">赚取规则</option>
                  <option value="consume">消耗规则</option>
                </select>
                <select
                  value={ruleFilter.target_role}
                  onChange={(e) => setRuleFilter({ ...ruleFilter, target_role: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">全部角色</option>
                  <option value="all">所有用户</option>
                  <option value="merchant">商家</option>
                  <option value="expert">专家</option>
                  <option value="user">普通用户</option>
                </select>
                <select
                  value={ruleFilter.status}
                  onChange={(e) => setRuleFilter({ ...ruleFilter, status: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">全部状态</option>
                  <option value="active">启用</option>
                  <option value="inactive">禁用</option>
                </select>
                <button
                  onClick={() => { setRuleFilter({ rule_type: '', target_role: '', status: '' }); loadRules() }}
                  className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
                >
                  重置筛选
                </button>
              </div>
            </div>

            {/* 规则列表 */}
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">规则名称</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">角色</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">贡献值</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {rules.map((rule) => (
                    <tr key={rule.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div>
                          <p className="font-medium text-gray-900">{rule.rule_name}</p>
                          <p className="text-sm text-gray-500">{rule.rule_code}</p>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded ${
                          rule.rule_type === 'earn' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                        }`}>
                          {rule.rule_type === 'earn' ? '赚取' : '消耗'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {rule.target_role === 'all' ? '所有用户' : rule.target_role}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <p className={`font-semibold ${rule.contribution_value > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {rule.contribution_value > 0 ? '+' : ''}{rule.contribution_value}
                        </p>
                        {rule.lingzhi_value !== 0 && (
                          <p className={`text-sm ${rule.lingzhi_value > 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                            灵值: {rule.lingzhi_value > 0 ? '+' : ''}{rule.lingzhi_value}
                          </p>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded ${
                          rule.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {rule.status === 'active' ? '启用' : '禁用'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <div className="flex items-center space-x-2">
                          <button className="p-2 rounded hover:bg-blue-100 text-blue-600">
                            <Edit2 className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteRule(rule.id)}
                            className="p-2 rounded hover:bg-red-100 text-red-600"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* 分页 */}
              {totalPages > 1 && (
                <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
                  <div className="text-sm text-gray-700">第 {currentPage} / {totalPages} 页</div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="p-2 rounded hover:bg-gray-200 disabled:opacity-50"
                    >
                      ←
                    </button>
                    <button
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="p-2 rounded hover:bg-gray-200 disabled:opacity-50"
                    >
                      →
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* 交易记录 */}
        {activeTab === 'transactions' && (
          <div className="space-y-6">
            {/* 筛选工具栏 */}
            <div className="bg-white rounded-lg shadow-sm p-4">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <input
                  type="text"
                  placeholder="用户ID"
                  value={transactionFilter.user_id}
                  onChange={(e) => setTransactionFilter({ ...transactionFilter, user_id: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                />
                <select
                  value={transactionFilter.transaction_type}
                  onChange={(e) => setTransactionFilter({ ...transactionFilter, transaction_type: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                >
                  <option value="">全部类型</option>
                  <option value="earn">赚取</option>
                  <option value="consume">消耗</option>
                  <option value="adjust">调整</option>
                  <option value="transfer">转移</option>
                </select>
                <div className="flex items-center space-x-2">
                  <input
                    type="date"
                    value={transactionFilter.start_date}
                    onChange={(e) => setTransactionFilter({ ...transactionFilter, start_date: e.target.value })}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                  <span className="text-gray-500">至</span>
                  <input
                    type="date"
                    value={transactionFilter.end_date}
                    onChange={(e) => setTransactionFilter({ ...transactionFilter, end_date: e.target.value })}
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  />
                </div>
              </div>
            </div>

            {/* 交易列表 */}
            <div className="bg-white rounded-lg shadow-sm overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">时间</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">用户</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">规则</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">类型</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">贡献值变化</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">余额</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">描述</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {transactions.map((tx) => (
                    <tr key={tx.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {new Date(tx.created_at).toLocaleString('zh-CN')}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <p className="font-medium text-gray-900">{tx.real_name || tx.username || `用户#${tx.user_id}`}</p>
                        <p className="text-sm text-gray-500">ID: {tx.user_id}</p>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {tx.rule_name}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`px-2 py-1 text-xs rounded ${
                          tx.transaction_type === 'earn' ? 'bg-green-100 text-green-800' :
                          tx.transaction_type === 'consume' ? 'bg-red-100 text-red-800' :
                          'bg-blue-100 text-blue-800'
                        }`}>
                          {tx.transaction_type === 'earn' ? '赚取' :
                           tx.transaction_type === 'consume' ? '消耗' :
                           tx.transaction_type === 'adjust' ? '调整' : '转移'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <p className={`font-semibold ${tx.contribution_change > 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {tx.contribution_change > 0 ? '+' : ''}{tx.contribution_change}
                        </p>
                        {tx.lingzhi_change !== 0 && (
                          <p className={`text-sm ${tx.lingzhi_change > 0 ? 'text-blue-600' : 'text-orange-600'}`}>
                            灵值: {tx.lingzhi_change > 0 ? '+' : ''}{tx.lingzhi_change}
                          </p>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {tx.balance_after}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500 max-w-xs truncate">
                        {tx.description}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {/* 分页 */}
              {totalPages > 1 && (
                <div className="bg-gray-50 px-6 py-4 flex items-center justify-between">
                  <div className="text-sm text-gray-700">第 {currentPage} / {totalPages} 页</div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setCurrentPage(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="p-2 rounded hover:bg-gray-200 disabled:opacity-50"
                    >
                      ←
                    </button>
                    <button
                      onClick={() => setCurrentPage(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="p-2 rounded hover:bg-gray-200 disabled:opacity-50"
                    >
                      →
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ContributionManagement
