import { useState } from 'react'
import { economyApi } from '../services/api'
import { Wallet, TrendingUp, Lock, Calculator } from 'lucide-react'

const Economy = () => {
  const [activeTab, setActiveTab] = useState<'income' | 'calculator' | 'exchange'>('income')
  const [contribution, setContribution] = useState<number>(100)
  const [lockPeriod, setLockPeriod] = useState<string | undefined>(undefined)
  const [result, setResult] = useState<any>(null)
  const [loading, setLoading] = useState(false)

  const handleCalculate = async () => {
    setLoading(true)
    try {
      const res = await economyApi.calculateLingzhiValue(contribution, lockPeriod)
      setResult(res.data)
    } catch (error) {
      console.error('计算失败:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">经济模型</h1>
        <p className="text-gray-600 mt-2">了解灵值的价值体系，规划您的财富增长</p>
      </div>

      {/* 标签页 */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden">
        <div className="flex border-b">
          {[
            { id: 'income', icon: TrendingUp, label: '收入预测' },
            { id: 'calculator', icon: Calculator, label: '价值计算器' },
            { id: 'exchange', icon: Wallet, label: '兑换规则' },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center space-x-2 py-4 font-semibold transition-colors ${
                activeTab === tab.id
                  ? 'text-primary-600 bg-primary-50 border-b-2 border-primary-500'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <tab.icon className="w-5 h-5" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === 'income' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {[
                  { level: '轻度参与', daily: 30, monthly: 90, yearly: 1080 },
                  { level: '中度参与', daily: 300, monthly: 900, yearly: 10800 },
                  { level: '深度参与', daily: 1000, monthly: 3000, yearly: 36000 },
                ].map((item) => (
                  <div key={item.level} className="border rounded-xl p-6 hover:shadow-lg transition-shadow">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">{item.level}</h3>
                    <div className="space-y-3">
                      <div className="flex justify-between">
                        <span className="text-gray-600">日均</span>
                        <span className="font-semibold text-primary-600">+{item.daily} 灵值</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">月收入</span>
                        <span className="font-semibold text-secondary-600">+{item.monthly} 元</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">年收入</span>
                        <span className="font-semibold text-teal-600">+{item.yearly} 元</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {activeTab === 'calculator' && (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    贡献值数量
                  </label>
                  <input
                    type="number"
                    value={contribution}
                    onChange={(e) => setContribution(Number(e.target.value))}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                    placeholder="输入贡献值数量"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    锁定期限（可选）
                  </label>
                  <select
                    value={lockPeriod || ''}
                    onChange={(e) => setLockPeriod(e.target.value || undefined)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                  >
                    <option value="">不锁定</option>
                    <option value="1年">1年 (+20%)</option>
                    <option value="2年">2年 (+50%)</option>
                    <option value="3年">3年 (+100%)</option>
                  </select>
                </div>
              </div>

              <button
                onClick={handleCalculate}
                disabled={loading}
                className="w-full bg-gradient-to-r from-primary-500 to-secondary-500 text-white py-3 rounded-lg font-semibold hover:from-primary-600 hover:to-secondary-600 transition-all disabled:opacity-50"
              >
                {loading ? '计算中...' : '开始计算'}
              </button>

              {result && (
                <div className="bg-gradient-to-br from-pink-50 to-teal-50 rounded-xl p-6 border border-pink-200">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">计算结果</h3>
                  <pre className="whitespace-pre-wrap text-sm text-gray-700">
                    {result}
                  </pre>
                </div>
              )}
            </div>
          )}

          {activeTab === 'exchange' && (
            <div className="space-y-6">
              <div className="bg-gradient-to-r from-primary-500 to-secondary-500 text-white rounded-xl p-6">
                <div className="flex items-center space-x-4 mb-4">
                  <Wallet className="w-12 h-12" />
                  <div>
                    <h3 className="text-2xl font-bold">1 灵值 = 0.1 元</h3>
                    <p className="opacity-90">100% 确定，随时可兑换</p>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="border rounded-xl p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <Lock className="w-5 h-5 text-green-600" />
                    </div>
                    <h3 className="font-semibold">锁定增值</h3>
                  </div>
                  <ul className="space-y-3">
                    <li className="flex justify-between">
                      <span>锁定1年</span>
                      <span className="text-green-600 font-semibold">+20%</span>
                    </li>
                    <li className="flex justify-between">
                      <span>锁定2年</span>
                      <span className="text-green-600 font-semibold">+50%</span>
                    </li>
                    <li className="flex justify-between">
                      <span>锁定3年</span>
                      <span className="text-green-600 font-semibold">+100%</span>
                    </li>
                  </ul>
                </div>

                <div className="border rounded-xl p-6">
                  <div className="flex items-center space-x-3 mb-4">
                    <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                      <Wallet className="w-5 h-5 text-blue-600" />
                    </div>
                    <h3 className="font-semibold">兑换规则</h3>
                  </div>
                  <ul className="space-y-3 text-sm text-gray-600">
                    <li>• 最低兑换：10灵值（1元）</li>
                    <li>• 到账时间：T+1（工作日）</li>
                    <li>• 手续费：0%（平台承担）</li>
                    <li>• 兑换频率：不限次数</li>
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Economy
