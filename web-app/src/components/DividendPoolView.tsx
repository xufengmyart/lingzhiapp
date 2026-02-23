import { useEffect, useState } from 'react'
import {
  DollarSign,
  TrendingUp,
  Users,
  PieChart,
  Calendar,
  ArrowUp,
  CheckCircle,
  AlertCircle,
  Building2,
  UserCheck,
  Target,
  Wallet
} from 'lucide-react'

interface DividendPoolData {
  pool: {
    total_amount: number
    available_amount: number
    distributed_amount: number
    participants_count: number
  }
  sources: Array<{
    source_type: string
    count: number
    total_profit: number
    total_contribution: number
  }>
  trend: Array<{
    date: string
    daily_contribution: number
  }>
}

interface UserEligibility {
  success: boolean
  user_id: number
  is_eligible: boolean
  referral_count: number
  eligibility_type: string
}

// 模拟分红池数据
const MOCK_POOL_DATA: DividendPoolData = {
  pool: {
    total_amount: 1500000,
    available_amount: 850000,
    distributed_amount: 650000,
    participants_count: 1250
  },
  sources: [
    {
      source_type: '圣地贡献',
      count: 320,
      total_profit: 180000,
      total_contribution: 150000
    },
    {
      source_type: '项目分成',
      count: 85,
      total_profit: 220000,
      total_contribution: 180000
    },
    {
      source_type: '通证质押',
      count: 560,
      total_profit: 120000,
      total_contribution: 100000
    },
    {
      source_type: '会员订阅',
      count: 285,
      total_profit: 80000,
      total_contribution: 65000
    }
  ],
  trend: [
    { date: '2024-01-15', daily_contribution: 32000 },
    { date: '2024-01-16', daily_contribution: 28000 },
    { date: '2024-01-17', daily_contribution: 35000 },
    { date: '2024-01-18', daily_contribution: 42000 },
    { date: '2024-01-19', daily_contribution: 38000 },
    { date: '2024-01-20', daily_contribution: 45000 },
    { date: '2024-01-21', daily_contribution: 51000 }
  ]
}

const MOCK_USER_ELIGIBILITY: UserEligibility = {
  success: true,
  user_id: 1,
  is_eligible: true,
  referral_count: 5,
  eligibility_type: 'referrer'
}

const DividendPoolView = () => {
  const [poolData, setPoolData] = useState<DividendPoolData | null>(MOCK_POOL_DATA)
  const [userEligibility, setUserEligibility] = useState<UserEligibility | null>(MOCK_USER_ELIGIBILITY)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDividendPoolData()
  }, [])

  const fetchDividendPoolData = async () => {
    try {
      setLoading(true)

      // 获取分红池汇总信息
      const poolResponse = await fetch('http://123.56.142.143:5000/api/dividend-pool/summary')
      const poolResult = await poolResponse.json()
      if (poolResult.success) {
        setPoolData(poolResult)
      } else {
        setPoolData(MOCK_POOL_DATA)
      }

      // 获取用户分红资格
      const userId = localStorage.getItem('user_id')
      if (userId) {
        const eligibilityResponse = await fetch(
          `http://123.56.142.143:5000/api/dividend-pool/eligibility?user_id=${userId}`
        )
        const eligibilityResult = await eligibilityResponse.json()
        if (eligibilityResult.success) {
          setUserEligibility(eligibilityResult)
        } else {
          setUserEligibility(MOCK_USER_ELIGIBILITY)
        }
      } else {
        setUserEligibility(MOCK_USER_ELIGIBILITY)
      }
    } catch (error) {
      console.error('获取分红池数据失败:', error)
      setPoolData(MOCK_POOL_DATA)
      setUserEligibility(MOCK_USER_ELIGIBILITY)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('zh-CN', {
      style: 'currency',
      currency: 'CNY',
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    }).format(amount)
  }

  const getSourceLabel = (type: string) => {
    const labels: { [key: string]: { label: string; icon: any; color: string } } = {
      project: { label: '项目收益', icon: Building2, color: 'blue' },
      partner: { label: '合伙人收益', icon: UserCheck, color: 'purple' },
      bounty_hunter: { label: '赏金猎人', icon: Target, color: 'orange' },
      investor: { label: '投资人收益', icon: Wallet, color: 'green' }
    }
    return labels[type] || { label: type, icon: DollarSign, color: 'gray' }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* 用户资格提示 */}
      {userEligibility && (
        <div
          className={`rounded-xl p-6 ${
            userEligibility.is_eligible
              ? 'bg-green-50 border border-green-200'
              : 'bg-yellow-50 border border-yellow-200'
          }`}
        >
          <div className="flex items-center space-x-3">
            {userEligibility.is_eligible ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <AlertCircle className="w-6 h-6 text-yellow-600" />
            )}
            <div>
              <h3 className="font-semibold text-gray-900">
                {userEligibility.is_eligible ? '您有分红资格！' : '暂无分红资格'}
              </h3>
              <p className="text-sm text-gray-600">
                {userEligibility.is_eligible
                  ? `您已推荐 ${userEligibility.referral_count} 位用户，可参与分红池分配`
                  : '参与推荐即可获得分红资格'}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* 分红池总览卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-gradient-to-br from-blue-500 to-blue-600 text-white rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <DollarSign className="w-10 h-10 opacity-80" />
            <span className="text-sm font-medium opacity-80">分红池总额</span>
          </div>
          <div className="text-3xl font-bold mb-2">
            {poolData ? formatCurrency(poolData.pool.total_amount) : '¥0.00'}
          </div>
          <div className="text-sm opacity-80">
            累计收益贡献
          </div>
        </div>

        <div className="bg-gradient-to-br from-green-500 to-green-600 text-white rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <Wallet className="w-10 h-10 opacity-80" />
            <span className="text-sm font-medium opacity-80">可用分红</span>
          </div>
          <div className="text-3xl font-bold mb-2">
            {poolData ? formatCurrency(poolData.pool.available_amount) : '¥0.00'}
          </div>
          <div className="text-sm opacity-80">
            待分配金额
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-purple-600 text-white rounded-xl p-6 shadow-lg">
          <div className="flex items-center justify-between mb-4">
            <Users className="w-10 h-10 opacity-80" />
            <span className="text-sm font-medium opacity-80">参与人数</span>
          </div>
          <div className="text-3xl font-bold mb-2">
            {poolData ? poolData.pool.participants_count.toLocaleString() : '0'}
          </div>
          <div className="text-sm opacity-80">
            有分红资格的用户
          </div>
        </div>
      </div>

      {/* 资金来源分布 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <PieChart className="w-6 h-6 mr-2 text-primary-500" />
          资金来源分布
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {poolData?.sources.map((source) => {
            const { label, icon: Icon, color } = getSourceLabel(source.source_type)
            const contribution = poolData.pool.total_amount
            const percentage =
              contribution > 0 ? (source.total_contribution / contribution) * 100 : 0

            return (
              <div
                key={source.source_type}
                className="border rounded-xl p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between mb-3">
                  <div className={`w-10 h-10 bg-${color}-100 rounded-lg flex items-center justify-center`}>
                    <Icon className="w-5 h-5 text-${color}-600" />
                  </div>
                  <span className="text-sm font-medium text-gray-600">{percentage.toFixed(1)}%</span>
                </div>
                <h4 className="font-semibold text-gray-900 mb-2">{label}</h4>
                <div className="space-y-1 text-sm">
                  <div className="flex justify-between text-gray-600">
                    <span>贡献次数</span>
                    <span className="font-medium">{source.count}</span>
                  </div>
                  <div className="flex justify-between text-gray-600">
                    <span>总收益</span>
                    <span className="font-medium">{formatCurrency(source.total_profit)}</span>
                  </div>
                  <div className="flex justify-between text-primary-600 font-semibold">
                    <span>贡献金额</span>
                    <span>{formatCurrency(source.total_contribution)}</span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* 分红池机制说明 */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
          <Calendar className="w-6 h-6 mr-2 text-primary-500" />
          分红机制说明
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-blue-600 font-bold text-sm">1</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">资金来源</h4>
                <p className="text-sm text-gray-600">
                  项目收益、合伙人收益、赏金猎人收益、投资人收益的 1% 自动汇入分红池
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-green-600 font-bold text-sm">2</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">参与资格</h4>
                <p className="text-sm text-gray-600">
                  所有参与推荐的用户（推荐至少1人）自动获得分红资格
                </p>
              </div>
            </div>
          </div>
          <div className="space-y-4">
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-purple-600 font-bold text-sm">3</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">分配方式</h4>
                <p className="text-sm text-gray-600">
                  根据推荐人数和贡献度按比例分配，每月定期发放
                </p>
              </div>
            </div>
            <div className="flex items-start space-x-3">
              <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center flex-shrink-0">
                <span className="text-orange-600 font-bold text-sm">4</span>
              </div>
              <div>
                <h4 className="font-semibold text-gray-900 mb-1">持续增长</h4>
                <p className="text-sm text-gray-600">
                  随着生态发展，分红池持续积累，长期持有价值越高
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* 趋势图表（简化版） */}
      {poolData?.trend && poolData.trend.length > 0 && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
            <TrendingUp className="w-6 h-6 mr-2 text-primary-500" />
            近30日贡献趋势
          </h3>
          <div className="h-64 flex items-end space-x-2">
            {poolData.trend.slice(0, 30).reverse().map((item, index) => {
              const maxContribution = Math.max(...poolData.trend.map((t) => t.daily_contribution))
              const height = maxContribution > 0 ? (item.daily_contribution / maxContribution) * 100 : 0

              return (
                <div key={index} className="flex-1 flex flex-col items-center">
                  <div
                    className="w-full bg-gradient-to-t from-primary-500 to-primary-300 rounded-t transition-all hover:from-primary-600 hover:to-primary-400"
                    style={{ height: `${Math.max(height, 5)}%` }}
                    title={`${item.date}: ${formatCurrency(item.daily_contribution)}`}
                  ></div>
                  <span className="text-xs text-gray-500 mt-2">
                    {new Date(item.date).toLocaleDateString('zh-CN', { day: '2-digit', month: '2-digit' })}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}

export default DividendPoolView
