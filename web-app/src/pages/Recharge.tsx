import { useState, useEffect } from 'react'
import { useAuth } from '../contexts/AuthContext'
import { Wallet, Gift, Zap, Crown, Diamond, Sparkles, Check, Copy, CheckCircle } from 'lucide-react'

interface RechargeTier {
  id: number
  name: string
  description: string
  price: number
  base_lingzhi: number
  bonus_lingzhi: number
  total_lingzhi: number
  bonus_percentage: number
  partner_level: string
  benefits: string[]
  sort_order: number
}

const Recharge = () => {
  const { user, updateUser } = useAuth()
  const [tiers, setTiers] = useState<RechargeTier[]>([])
  const [selectedTier, setSelectedTier] = useState<RechargeTier | null>(null)
  const [paymentMethod, setPaymentMethod] = useState<'online' | 'bank_transfer'>('online')
  const [loading, setLoading] = useState(true)
  const [orderLoading, setOrderLoading] = useState(false)
  const [orderInfo, setOrderInfo] = useState<any>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    loadRechargeTiers()
  }, [])

  const loadRechargeTiers = async () => {
    try {
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/recharge/tiers`)
      const data = await response.json()
      if (data.success) {
        setTiers(data.data)
      }
    } catch (error) {
      console.error('加载充值档位失败:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateOrder = async () => {
    if (!selectedTier) return

    setOrderLoading(true)
    try {
      const token = localStorage.getItem('token')
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/recharge/create-order`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          tier_id: selectedTier.id,
          payment_method: paymentMethod,
        }),
      })

      const data = await response.json()
      if (data.success) {
        setOrderInfo(data.data)
        // 模拟支付完成（生产环境需要集成真实支付）
        if (paymentMethod === 'online') {
          handleCompletePayment(data.data.order_no)
        }
      } else {
        alert(data.message || '创建订单失败')
      }
    } catch (error) {
      console.error('创建订单失败:', error)
      alert('创建订单失败，请重试')
    } finally {
      setOrderLoading(false)
    }
  }

  const handleCompletePayment = async (orderNo: string) => {
    try {
      const token = localStorage.getItem('token')
      const apiBase = import.meta.env.VITE_API_BASE_URL || '/api'
      const response = await fetch(`${apiBase}/recharge/complete-payment`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          order_no: orderNo,
          transaction_id: `TXN${Date.now()}`,
        }),
      })

      const data = await response.json()
      if (data.success) {
        alert(`充值成功！获得 ${data.data.total_lingzhi} 灵值`)
        // 刷新用户信息
        const userResponse = await fetch(`${apiBase}/user/info`, {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        })
        const userData = await userResponse.json()
        if (userData.success) {
          updateUser(userData.data)
        }
        setOrderInfo(null)
        setSelectedTier(null)
      } else {
        alert(data.message || '充值失败')
      }
    } catch (error) {
      console.error('充值失败:', error)
      alert('充值失败，请重试')
    }
  }

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const getTierIcon = (index: number) => {
    const icons = [Sparkles, Zap, Crown, Diamond, Gift, Wallet, Sparkles]
    return icons[index % icons.length]
  }

  const getTierGradient = (index: number) => {
    const gradients = [
      'from-green-500 to-emerald-600',
      'from-blue-500 to-indigo-600',
      'from-purple-500 to-pink-600',
      'from-orange-500 to-red-600',
      'from-pink-500 to-rose-600',
      'from-cyan-500 to-blue-600',
      'from-amber-500 to-yellow-600',
    ]
    return gradients[index % gradients.length]
  }

  return (
    <div className="space-y-6 animate-fade-in pb-20">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">购买灵值</h1>
        <p className="text-gray-600 mt-2">选择合适的充值档位，快速获取灵值，开启生态之旅</p>
      </div>

      {/* 灵值余额展示 */}
      <div className="bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl p-6 text-white">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
              <Wallet className="w-8 h-8" />
            </div>
            <div>
              <div className="text-sm opacity-80">当前灵值</div>
              <div className="text-3xl font-bold">{user?.total_lingzhi || 0}</div>
              <div className="text-sm opacity-80">等值：¥{((user?.total_lingzhi || 0) * 0.1).toFixed(2)}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm opacity-80">购买提示</div>
            <div className="text-sm">灵值可在生态内流通消费</div>
          </div>
        </div>
      </div>

      {/* 充值档位列表 */}
      <div>
        <h2 className="text-xl font-bold mb-4">充值档位</h2>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tiers.map((tier, index) => {
              const Icon = getTierIcon(index)
              const gradient = getTierGradient(index)
              return (
                <div
                  key={tier.id}
                  className={`relative bg-white rounded-xl shadow-lg overflow-hidden transition-all cursor-pointer hover:shadow-2xl border-2 ${
                    selectedTier?.id === tier.id ? 'border-primary-500 ring-2 ring-primary-500' : 'border-transparent'
                  }`}
                  onClick={() => setSelectedTier(tier)}
                >
                  {tier.bonus_lingzhi > 0 && (
                    <div className={`absolute top-0 right-0 bg-gradient-to-r ${gradient} text-white text-xs font-bold px-3 py-1 rounded-bl-lg`}>
                      赠送 {tier.bonus_lingzhi}
                    </div>
                  )}

                  <div className={`absolute top-0 left-0 right-0 h-1 bg-gradient-to-r ${gradient}`}></div>

                  <div className="p-6">
                    <div className="flex items-center space-x-3 mb-4">
                      <div className={`w-12 h-12 bg-gradient-to-r ${gradient} rounded-lg flex items-center justify-center text-white`}>
                        <Icon className="w-6 h-6" />
                      </div>
                      <div>
                        <div className="text-xl font-bold">{tier.name}</div>
                        <div className="text-sm text-gray-500">{tier.description}</div>
                      </div>
                    </div>

                    <div className="text-center my-4">
                      <div className="text-sm text-gray-500 mb-1">价格</div>
                      <div className="text-3xl font-bold text-primary-600">¥{tier.price}</div>
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600">基础灵值</span>
                        <span className="font-semibold">{tier.base_lingzhi}</span>
                      </div>
                      {tier.bonus_lingzhi > 0 && (
                        <div className="flex justify-between text-sm">
                          <span className="text-green-600">赠送灵值</span>
                          <span className="font-semibold text-green-600">+{tier.bonus_lingzhi}</span>
                        </div>
                      )}
                      <div className="border-t pt-2 flex justify-between">
                        <span className="text-gray-600 font-semibold">总计</span>
                        <span className="text-xl font-bold text-primary-600">{tier.total_lingzhi} 灵值</span>
                      </div>
                    </div>

                    {tier.bonus_percentage > 0 && (
                      <div className={`text-center text-xs font-semibold text-white py-1 rounded bg-gradient-to-r ${gradient}`}>
                        额外赠送 {tier.bonus_percentage}%
                      </div>
                    )}
                  </div>
                </div>
              )
            })}
          </div>
        )}
      </div>

      {/* 支付方式选择 */}
      {selectedTier && !orderInfo && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">选择支付方式</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <button
              className={`p-4 rounded-lg border-2 transition-all ${
                paymentMethod === 'online'
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setPaymentMethod('online')}
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <CheckCircle className="w-5 h-5 text-green-600" />
                </div>
                <div className="text-left">
                  <div className="font-semibold">在线支付</div>
                  <div className="text-sm text-gray-500">微信/支付宝</div>
                </div>
                {paymentMethod === 'online' && <Check className="w-5 h-5 text-primary-600 ml-auto" />}
              </div>
            </button>

            <button
              className={`p-4 rounded-lg border-2 transition-all ${
                paymentMethod === 'bank_transfer'
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
              onClick={() => setPaymentMethod('bank_transfer')}
            >
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Wallet className="w-5 h-5 text-blue-600" />
                </div>
                <div className="text-left">
                  <div className="font-semibold">公司公户转账</div>
                  <div className="text-sm text-gray-500">银行转账</div>
                </div>
                {paymentMethod === 'bank_transfer' && <Check className="w-5 h-5 text-primary-600 ml-auto" />}
              </div>
            </button>
          </div>

          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-600">充值档位</span>
              <span className="font-semibold">{selectedTier.name}</span>
            </div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-600">支付金额</span>
              <span className="font-bold text-xl text-primary-600">¥{selectedTier.price}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">获得灵值</span>
              <span className="font-bold text-xl text-green-600">{selectedTier.total_lingzhi}</span>
            </div>
          </div>

          <button
            onClick={handleCreateOrder}
            disabled={orderLoading}
            className="w-full mt-6 bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-3 rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {orderLoading ? '创建订单中...' : '确认充值'}
          </button>
        </div>
      )}

      {/* 订单确认 */}
      {orderInfo && paymentMethod === 'bank_transfer' && (
        <div className="bg-white rounded-xl shadow-lg p-6">
          <h3 className="text-lg font-bold mb-4">转账信息</h3>
          <div className="space-y-4">
            <div className="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
              <div className="font-semibold text-yellow-800 mb-2">重要提示</div>
              <div className="text-sm text-yellow-700">
                转账时请务必填写备注：<span className="font-bold">{orderInfo.transfer_remark}</span>
              </div>
            </div>

            <div className="space-y-3">
              <div className="text-sm text-gray-600">请转账到以下公司账户：</div>
              {orderInfo.company_accounts?.map((account: any, index: number) => (
                <div key={index} className="p-4 bg-gray-50 rounded-lg space-y-2">
                  <div className="flex justify-between">
                    <span className="text-gray-600">公司名称</span>
                    <span className="font-semibold">{account.company_name}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">账户名称</span>
                    <span className="font-semibold">{account.account_name}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">银行账户</span>
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold">{account.account_number}</span>
                      <button
                        onClick={() => handleCopy(account.account_number)}
                        className="text-primary-600 hover:text-primary-700"
                      >
                        {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">开户银行</span>
                    <span className="font-semibold">{account.bank_name}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">开户网点</span>
                    <span className="font-semibold">{account.bank_branch}</span>
                  </div>
                </div>
              ))}
            </div>

            <div className="text-sm text-gray-600">
              转账金额：<span className="font-bold">¥{orderInfo.amount}</span>
            </div>
          </div>

          <button
            onClick={() => {
              setOrderInfo(null)
              setSelectedTier(null)
            }}
            className="w-full mt-6 bg-gray-200 text-gray-700 py-3 rounded-lg font-semibold hover:bg-gray-300 transition-colors"
          >
            返回
          </button>
        </div>
      )}
    </div>
  )
}

export default Recharge
