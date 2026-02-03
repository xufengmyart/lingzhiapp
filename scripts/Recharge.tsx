import { useState, useEffect } from 'react'
import { CreditCard, Gift, Star, Crown, Diamond, CheckCircle, Clock, TrendingUp } from 'lucide-react'
import { useAuth } from '../contexts/AuthContext'

interface RechargeTier {
  id: number
  name: string
  description: string
  price: number
  base_lingzhi: number
  bonus_lingzhi: number
  total_lingzhi: number
  bonus_percentage: number
  partner_level: number
  benefits: string[]
  sort_order: number
}

export default function Recharge() {
  const [tiers, setTiers] = useState<RechargeTier[]>([])
  const [loading, setLoading] = useState(true)
  const [selectedTier, setSelectedTier] = useState<RechargeTier | null>(null)
  const [showOrderModal, setShowOrderModal] = useState(false)
  const { user } = useAuth()

  useEffect(() => {
    loadRechargeTiers()
  }, [])

  const loadRechargeTiers = async () => {
    try {
      const response = await fetch('/api/recharge/tiers')
      const result = await response.json()
      if (result.success) {
        setTiers(result.data)
      }
    } catch (error) {
      console.error('加载充值档位失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleSelectTier = (tier: RechargeTier) => {
    setSelectedTier(tier)
    setShowOrderModal(true)
  }

  const getIcon = (tier: RechargeTier) => {
    if (tier.name.includes('合伙人')) {
      return <Crown className="w-8 h-8" />
    } else if (tier.price >= 999) {
      return <Diamond className="w-8 h-8" />
    } else if (tier.price >= 499) {
      return <Star className="w-8 h-8" />
    } else {
      return <Gift className="w-8 h-8" />
    }
  }

  const getGradient = (tier: RechargeTier) => {
    if (tier.name.includes('合伙人')) {
      return 'from-purple-600 to-pink-500'
    } else if (tier.price >= 999) {
      return 'from-blue-600 to-cyan-500'
    } else if (tier.price >= 499) {
      return 'from-emerald-600 to-teal-500'
    } else if (tier.price >= 199) {
      return 'from-orange-500 to-amber-500'
    } else {
      return 'from-gray-600 to-gray-700'
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-50 via-pink-50 to-blue-50 p-6">
      <div className="max-w-6xl mx-auto">
        {/* 头部 */}
        <div className="text-center mb-12">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-purple-500 to-pink-500 rounded-3xl mb-6 shadow-2xl">
            <CreditCard className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent mb-3">
            灵值充值中心
          </h1>
          <p className="text-gray-600 text-lg">
            选择适合您的充值方案，获得更多灵值，开启精彩旅程
          </p>
        </div>

        {/* 用户当前灵值 */}
        {user && (
          <div className="bg-white rounded-2xl shadow-xl p-6 mb-8 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="bg-gradient-to-br from-purple-500 to-pink-500 p-3 rounded-xl">
                <CreditCard className="w-6 h-6 text-white" />
              </div>
              <div>
                <div className="text-sm text-gray-500">当前灵值</div>
                <div className="text-3xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                  {user.totalLingzhi || 0}
                </div>
              </div>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 text-sm text-gray-500">
                <TrendingUp className="w-4 h-4" />
                <span>充值后立即到账</span>
              </div>
            </div>
          </div>
        )}

        {/* 充值档位列表 */}
        {loading ? (
          <div className="text-center py-20">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-500 mx-auto mb-4"></div>
            <p className="text-gray-500">加载中...</p>
          </div>
        ) : (
          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
            {tiers.map((tier) => (
              <div
                key={tier.id}
                className={`relative bg-white rounded-3xl shadow-xl overflow-hidden transform transition-all duration-300 hover:scale-105 hover:shadow-2xl cursor-pointer ${
                  tier.bonus_percentage >= 25 ? 'ring-4 ring-purple-400' : ''
                }`}
                onClick={() => handleSelectTier(tier)}
              >
                {/* 热门标签 */}
                {tier.bonus_percentage >= 25 && (
                  <div className="absolute top-0 right-0 bg-gradient-to-r from-red-500 to-pink-500 text-white text-xs font-bold px-4 py-1 rounded-bl-2xl">
                    🔥 热门推荐
                  </div>
                )}

                {/* 顶部图标 */}
                <div className={`bg-gradient-to-r ${getGradient(tier)} p-8 flex items-center justify-center`}>
                  <div className="text-white">
                    {getIcon(tier)}
                  </div>
                </div>

                {/* 内容 */}
                <div className="p-6">
                  {/* 档位名称 */}
                  <h3 className="text-2xl font-bold text-gray-800 mb-2">
                    {tier.name}
                  </h3>

                  {/* 描述 */}
                  <p className="text-gray-600 text-sm mb-4 h-10">
                    {tier.description}
                  </p>

                  {/* 价格 */}
                  <div className="flex items-baseline gap-2 mb-4">
                    <span className="text-4xl font-bold text-purple-600">
                      ¥{tier.price}
                    </span>
                    <span className="text-gray-400 line-through text-sm">
                      ¥{Math.round(tier.price / (1 + tier.bonus_percentage / 100))}
                    </span>
                  </div>

                  {/* 灵值数量 */}
                  <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-xl p-4 mb-4">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-gray-600 text-sm">基础灵值</span>
                      <span className="font-semibold text-gray-800">
                        {tier.base_lingzhi.toLocaleString()}
                      </span>
                    </div>
                    {tier.bonus_lingzhi > 0 && (
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-gray-600 text-sm">赠送灵值</span>
                        <span className="font-semibold text-green-600">
                          +{tier.bonus_lingzhi.toLocaleString()}
                        </span>
                      </div>
                    )}
                    <div className="border-t border-purple-200 pt-2 mt-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-gray-700">总计灵值</span>
                        <span className="text-xl font-bold bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">
                          {tier.total_lingzhi.toLocaleString()}
                        </span>
                      </div>
                    </div>
                  </div>

                  {/* 赠送比例 */}
                  {tier.bonus_percentage > 0 && (
                    <div className="inline-flex items-center gap-1 bg-green-100 text-green-700 text-sm font-semibold px-3 py-1 rounded-full mb-4">
                      <Gift className="w-4 h-4" />
                      <span>赠送 {tier.bonus_percentage}%</span>
                    </div>
                  )}

                  {/* 权益列表 */}
                  {tier.benefits && tier.benefits.length > 0 && (
                    <div className="space-y-2 mb-4">
                      {tier.benefits.slice(0, 3).map((benefit, index) => (
                        <div key={index} className="flex items-start gap-2 text-sm text-gray-600">
                          <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                          <span>{benefit}</span>
                        </div>
                      ))}
                      {tier.benefits.length > 3 && (
                        <div className="text-sm text-purple-600 font-medium">
                          +{tier.benefits.length - 3} 项更多权益
                        </div>
                      )}
                    </div>
                  )}

                  {/* 按钮 */}
                  <button className={`w-full py-3 rounded-xl font-semibold text-white bg-gradient-to-r ${getGradient(tier)} hover:shadow-lg transform hover:scale-[1.02] transition-all`}>
                    立即充值
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 温馨提示 */}
        <div className="mt-12 bg-blue-50 border border-blue-200 rounded-2xl p-6">
          <div className="flex items-start gap-4">
            <div className="bg-blue-100 p-2 rounded-lg">
              <Clock className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <h4 className="font-semibold text-blue-900 mb-2">温馨提示</h4>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• 充值成功后，灵值将立即到账</li>
                <li>• 获得合伙人资格后，将享受专属权益和收益</li>
                <li>• 如遇充值问题，请联系客服</li>
                <li>• 灵值可用于签到、参与活动、购买服务等</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* 订单确认弹窗 */}
      {showOrderModal && selectedTier && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-3xl shadow-2xl max-w-md w-full p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">确认充值订单</h2>

            {/* 充值信息 */}
            <div className="bg-gradient-to-r from-purple-50 to-pink-50 rounded-2xl p-6 mb-6">
              <div className="flex items-center justify-between mb-4">
                <span className="text-gray-600">充值档位</span>
                <span className="font-semibold text-gray-800">{selectedTier.name}</span>
              </div>
              <div className="flex items-center justify-between mb-4">
                <span className="text-gray-600">充值金额</span>
                <span className="font-bold text-2xl text-purple-600">¥{selectedTier.price}</span>
              </div>
              <div className="flex items-center justify-between border-t border-purple-200 pt-4">
                <span className="text-gray-600 font-medium">获得灵值</span>
                <span className="font-bold text-xl text-green-600">
                  {selectedTier.total_lingzhi.toLocaleString()}
                </span>
              </div>
            </div>

            {/* 支付方式 */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">选择支付方式</label>
              <div className="space-y-3">
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl cursor-pointer hover:border-purple-400 transition-all">
                  <input type="radio" name="payment" value="wechat" className="mr-3" defaultChecked />
                  <span className="font-medium text-gray-800">微信支付</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl cursor-pointer hover:border-purple-400 transition-all">
                  <input type="radio" name="payment" value="alipay" className="mr-3" />
                  <span className="font-medium text-gray-800">支付宝</span>
                </label>
                <label className="flex items-center p-4 border-2 border-gray-200 rounded-xl cursor-pointer hover:border-purple-400 transition-all">
                  <input type="radio" name="payment" value="bank" className="mr-3" />
                  <span className="font-medium text-gray-800">银行转账</span>
                </label>
              </div>
            </div>

            {/* 按钮 */}
            <div className="flex gap-4">
              <button
                onClick={() => setShowOrderModal(false)}
                className="flex-1 py-3 border-2 border-gray-200 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition-all"
              >
                取消
              </button>
              <button
                className="flex-1 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-xl font-semibold hover:shadow-lg transform hover:scale-[1.02] transition-all"
              >
                确认充值
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
